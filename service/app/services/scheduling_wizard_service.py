"""
Flujo guiado (wizard) para agendar citas vía chat.

Alineado con la pantalla web /agendar-cita: primer hospital activo + primera especialidad de ese
hospital (misma idea que getHospitals + getHospitalSpecialties). Si existe ese par, el usuario
empieza en **consultorio** → fecha → hora → confirmar. Si faltan datos en BD, se vuelve al flujo
completo Hospital → Especialidad → …
"""

from __future__ import annotations

import re
from datetime import date, datetime, time, timedelta
from typing import Any, Dict, List, Optional, Tuple

from sqlalchemy.orm import Session

from app.models.patient import Patient
from app.models.specialty import Specialty
from app.models.hospital import Hospital
from app.schemas.chat import WizardSelectionPayload
from app.repositories.consultation_room_repository import ConsultationRoomRepository
from app.repositories.hospital_repository import HospitalRepository
from app.repositories.specialty_repository import SpecialtyRepository
from app.services.chat_tool_executor import ChatToolExecutor, parse_iso_date, parse_time_string
from app.services.scheduling_dates import (
    app_today_now,
    ensure_weekday_booking,
    parse_booking_intent,
    parse_calendar_preferences_from_message,
    suggest_date_when_today_has_no_slots,
)
from app.services.slot_service import SlotService


def _label_date_es(d: date) -> str:
    dias = ("lun", "mar", "mié", "jue", "vie", "sáb", "dom")
    return f"{dias[d.weekday()]} {d.day:02d}/{d.month:02d}/{d.year}"


def _looks_like_booking_start(message: str) -> bool:
    m = message.strip().lower()
    if m.startswith("__pick__:"):
        return False
    if re.search(r"(cancelar|anular|borrar).{0,24}cita", m):
        return False
    if re.search(r"(ver|listar|mostrar).{0,12}(mis\s+)?citas", m) or re.match(
        r"^¿?(qué|cu[aá]les|cu[aá]ntas)\s+citas", m
    ):
        return False
    return bool(
        re.search(
            r"(^|\s)(agendar|reservar|nueva\s+cita|pedir\s+cita|sacar\s+cita|quiero\s+(una\s+)?cita)(\s|$)",
            m,
            re.IGNORECASE,
        )
    )


def _wants_exit_wizard(message: str) -> bool:
    m = message.strip().lower()
    return bool(
        re.match(
            r"^(salir|cancelar(\s+el)?\s+flujo|volver|reset|reiniciar|empezar\s+de\s+nuevo)\b",
            m,
        )
    )


def parse_pick(message: str) -> Optional[Tuple[str, str]]:
    s = message.strip()
    m = re.match(r"^__pick__:([a-z_]+):(.+)$", s, re.IGNORECASE)
    if not m:
        return None
    return m.group(1).lower(), m.group(2).strip()


def effective_wizard_selection(
    message: str,
    state_in: Optional[Dict[str, Any]],
    explicit: Optional[WizardSelectionPayload],
) -> Optional[WizardSelectionPayload]:
    """
    Con flujo activo, prioriza `wizard_selection` del cliente.
    En `idle`, solo acepta legado `__pick__` en el texto (no payloads sueltos que bloqueen el LLM).
    """
    st = _merge_state(state_in)
    legacy = coerce_legacy_pick_to_selection(message)
    if st.get("phase") in (None, "", "idle"):
        return legacy
    if explicit is not None:
        return explicit
    return legacy


def coerce_legacy_pick_to_selection(message: str) -> Optional[WizardSelectionPayload]:
    """Compatibilidad con clientes antiguos que enviaban __pick__ en el texto del mensaje."""
    p = parse_pick(message)
    if not p:
        return None
    kind, val = p
    if kind == "hospital":
        try:
            return WizardSelectionPayload(step="hospital", hospital_id=int(val))
        except ValueError:
            return None
    if kind == "specialty":
        try:
            return WizardSelectionPayload(step="specialty", specialty_id=int(val))
        except ValueError:
            return None
    if kind == "room":
        try:
            return WizardSelectionPayload(step="room", consultation_room_id=int(val))
        except ValueError:
            return None
    if kind == "date":
        return WizardSelectionPayload(step="date", date_iso=val.strip())
    if kind == "time":
        return WizardSelectionPayload(step="time", time_hhmm=val.strip())
    if kind == "confirm":
        v = val.lower()
        if v in ("yes", "si", "sí"):
            return WizardSelectionPayload(step="confirm", confirm=True)
        if v == "no":
            return WizardSelectionPayload(step="confirm", confirm=False)
    return None


_WIZARD_KEYS = frozenset(
    {
        "phase",
        "hospital_id",
        "hospital_name",
        "specialty_id",
        "specialty_name",
        "consultation_room_id",
        "consultation_room_name",
        "appointment_date_iso",
        "appointment_time_hhmm",
        "anchor_date_iso",
        "shift_hint",
        "bumped_from_today",
        "user_requested_date_iso",
        "user_requested_time_hhmm",
    }
)


def _empty_state() -> Dict[str, Any]:
    return {
        "phase": "idle",
        "hospital_id": None,
        "hospital_name": None,
        "specialty_id": None,
        "specialty_name": None,
        "consultation_room_id": None,
        "consultation_room_name": None,
        "appointment_date_iso": None,
        "appointment_time_hhmm": None,
        "anchor_date_iso": None,
        "shift_hint": "any",
        "bumped_from_today": False,
        "user_requested_date_iso": None,
        "user_requested_time_hhmm": None,
    }


def _merge_state(base: Optional[Dict[str, Any]]) -> Dict[str, Any]:
    out = _empty_state()
    if not base:
        return out
    for k, v in base.items():
        if k in _WIZARD_KEYS:
            out[k] = v
    return out


def _soft_opening_for_message(message: str) -> str:
    """Saludo breve si el usuario escribe hola / buenos días, etc.; si no, cadena vacía."""
    m = message.strip().lower()
    if re.match(r"^(hola|hey|hi|buenas)\b", m):
        return "¡Hola! "
    if re.match(r"^buen(os|as)\s+(d[ií]as|tardes|noches)\b", m):
        return "¡Buen día! "
    if re.match(r"^gracias\b", m):
        return "Con gusto. "
    return ""


class SchedulingWizardService:
    def __init__(self, db: Session, patient: Patient):
        self.db = db
        self.patient = patient
        self.hospital_repo = HospitalRepository(db)
        self.specialty_repo = SpecialtyRepository(db)
        self.room_repo = ConsultationRoomRepository(db)
        self.slot_service = SlotService(db)
        self.executor = ChatToolExecutor(db, patient)

    def _default_hospital_and_specialty(self) -> Optional[Tuple[Hospital, Specialty]]:
        """Igual que la web /agendar-cita: primer centro activo y primera especialidad de ese centro."""
        hospitals = self.hospital_repo.get_all(skip=0, limit=10, active_only=True)
        if not hospitals:
            return None
        h = hospitals[0]
        specs = self.hospital_repo.get_specialties(h.id, active_only=True)
        if not specs:
            return None
        return (h, specs[0])

    def process(
        self,
        message: str,
        state_in: Optional[Dict[str, Any]],
        wizard_selection: Optional[WizardSelectionPayload] = None,
    ) -> Tuple[str, Dict[str, Any], Optional[Dict[str, Any]]]:
        """
        Devuelve (texto_asistente, nuevo_estado, quick_replies o None).
        Las opciones usan `payload` (WizardSelectionPayload); no se exponen comandos al usuario.
        """
        today, now = app_today_now()
        state = _merge_state(state_in)

        if wizard_selection is not None:
            if state.get("phase") in (None, "", "idle"):
                return (
                    "Para reservar por aquí, escribe algo como **quiero agendar una cita** "
                    "o toca la sugerencia «Agendar mañana».",
                    state,
                    None,
                )
            return self._apply_selection(wizard_selection, state, today, now)

        if state.get("phase") not in ("idle", None, "") and re.search(
            r"\b(ver\s+mis\s+citas|mis\s+citas|qué\s+citas|listar\s+citas)\b",
            message.lower(),
        ):
            st = _empty_state()
            return (
                "Dejamos la reserva de lado un momento. Cuando quieras, pregúntame otra vez por tus citas y las vemos.",
                st,
                None,
            )

        if state.get("phase") == "idle" and _looks_like_booking_start(message):
            anchor, shift = parse_booking_intent(message, today)
            explicit_d, explicit_t = parse_calendar_preferences_from_message(message, today)
            state["shift_hint"] = shift or "any"
            if explicit_d:
                ed = ensure_weekday_booking(explicit_d)
                state["user_requested_date_iso"] = ed.isoformat()
                state["anchor_date_iso"] = ed.isoformat()
            elif anchor:
                state["anchor_date_iso"] = ensure_weekday_booking(anchor).isoformat()
            if explicit_t:
                state["user_requested_time_hhmm"] = explicit_t.strip()
            default_pair = self._default_hospital_and_specialty()
            if default_pair:
                h, spec = default_pair
                state["hospital_id"] = h.id
                state["hospital_name"] = h.name
                state["specialty_id"] = spec.id
                state["specialty_name"] = spec.name
                state["phase"] = "room"
                lead = (
                    f"Perfecto. En **{h.name}** la consulta sería de **{spec.name}** "
                    "(es lo habitual en la app; no tienes que elegirlo a mano)."
                )
                if explicit_d and explicit_t:
                    lead += (
                        f" Tomo nota de la fecha **{_label_date_es(ensure_weekday_booking(explicit_d))}** "
                        f"y la hora **{explicit_t}**; las usaré al reservar si hay cupo."
                    )
                elif explicit_d:
                    lead += (
                        f" Tomo nota de la fecha **{_label_date_es(ensure_weekday_booking(explicit_d))}**; "
                        "la usaré al reservar si hay cupo."
                    )
                elif explicit_t:
                    lead += f" Tomo nota de la hora **{explicit_t}**; la usaré al reservar si hay cupo."
                return self._step_room(state, today, now, lead_paragraph=lead)
            state["phase"] = "hospital"
            return self._step_hospital(state, today, now)

        if state.get("phase") not in (None, "idle") and _wants_exit_wizard(message):
            st = _empty_state()
            return (
                "Listo, cerramos la reserva guiada. ¿Seguimos con otra cosa?",
                st,
                None,
            )

        # NL fallback en pasos (número o nombre)
        phase = state.get("phase")
        if phase == "hospital":
            return self._match_hospital_nl(message, state, today, now)
        if phase == "specialty":
            return self._match_specialty_nl(message, state, today, now)
        if phase == "room":
            return self._match_room_nl(message, state, today, now)

        # Fecha, hora o confirmación: texto libre sin selección — tono humano y volver a mostrar botones
        if phase == "date":
            t, st, qr = self._step_date(state, today, now)
            pre = _soft_opening_for_message(message)
            hint = f"{pre}Elige el día que te venga bien abajo (son días con hueco libre).\n\n"
            return hint + t, st, qr
        if phase == "time":
            t, st, qr = self._step_time(state, today, now)
            pre = _soft_opening_for_message(message)
            hint = f"{pre}Toca la hora que prefieras.\n\n"
            return hint + t, st, qr
        if phase == "confirm":
            t, st, qr = self._step_confirm(state, today, now)
            pre = _soft_opening_for_message(message)
            hint = f"{pre}Échale un vistazo al resumen: si va bien, confirma; si no, puedes cambiar solo la hora.\n\n"
            return hint + t, st, qr

        return (
            "Para seguir con la reserva, usa los botones del mensaje de arriba. "
            "Si ya no quieres reservar, escribe **salir** y hablamos de otra cosa.",
            state,
            None,
        )

    def _apply_selection(
        self,
        payload: WizardSelectionPayload,
        state: Dict[str, Any],
        today: date,
        now: datetime,
    ) -> Tuple[str, Dict[str, Any], Optional[Dict[str, Any]]]:
        phase = state.get("phase")
        if payload.step != phase:
            return (
                "Esa opción ya no encaja con el paso actual. Mira el último mensaje o escribe **salir** para empezar de nuevo.",
                state,
                None,
            )

        if payload.step == "hospital" and payload.hospital_id is not None:
            h = self.hospital_repo.get_by_id(payload.hospital_id)
            if not h or not h.active:
                return "Ese centro no está disponible.", state, None
            state["hospital_id"] = h.id
            state["hospital_name"] = h.name
            state["phase"] = "specialty"
            return self._step_specialty(state, today, now)

        if payload.step == "specialty" and payload.specialty_id is not None:
            spec = self.specialty_repo.get_by_id(payload.specialty_id)
            if not spec or not spec.active:
                return "Esa especialidad no está disponible.", state, None
            hid = state.get("hospital_id")
            if hid and not self.hospital_repo.has_specialty(int(hid), payload.specialty_id):
                return "Esa especialidad no está en el hospital elegido.", state, None
            state["specialty_id"] = spec.id
            state["specialty_name"] = spec.name
            state["phase"] = "room"
            return self._step_room(state, today, now)

        if payload.step == "room" and payload.consultation_room_id is not None:
            hid = state.get("hospital_id")
            sid = state.get("specialty_id")
            rooms = self.room_repo.get_by_hospital_and_specialty(int(hid), int(sid))
            match = next((r for r in rooms if r.id == payload.consultation_room_id), None)
            if not match:
                return "Ese consultorio no aplica aquí.", state, None
            state["consultation_room_id"] = match.id
            state["consultation_room_name"] = match.name
            return self._after_room_selection(state, today, now)

        if payload.step == "date" and payload.date_iso:
            try:
                d = parse_iso_date(payload.date_iso)
            except ValueError:
                return "Fecha no válida.", state, None
            if d < today:
                return "Esa fecha ya pasó. Elige otra.", state, None
            state["appointment_date_iso"] = d.isoformat()
            state["phase"] = "time"
            return self._step_time(state, today, now)

        if payload.step == "time" and payload.time_hhmm:
            try:
                parse_time_string(payload.time_hhmm)
            except ValueError:
                return "Hora no válida (ej. 10:00 o 3pm).", state, None
            state["appointment_time_hhmm"] = payload.time_hhmm.strip()
            state["phase"] = "confirm"
            return self._step_confirm(state, today, now)

        if payload.step == "confirm" and payload.confirm is True:
            return self._do_create(state)

        if payload.step == "confirm" and payload.confirm is False:
            state["phase"] = "time"
            return self._step_time(state, today, now)

        return "No pude aplicar esa opción. Intenta de nuevo.", state, None

    def _match_hospital_nl(
        self, message: str, state: Dict[str, Any], today: date, now: datetime
    ):
        rows = self.hospital_repo.get_all(skip=0, limit=100, active_only=True)
        m = message.strip()
        if re.match(r"^\d+$", m):
            idx = int(m) - 1
            if 0 <= idx < len(rows):
                return self._apply_selection(
                    WizardSelectionPayload(step="hospital", hospital_id=rows[idx].id),
                    state,
                    today,
                    now,
                )
        low = m.lower()
        for h in rows:
            if h.name.lower() in low or low in h.name.lower():
                return self._apply_selection(
                    WizardSelectionPayload(step="hospital", hospital_id=h.id),
                    state,
                    today,
                    now,
                )
        t, st, qr = self._step_hospital(state, today, now)
        pre = _soft_opening_for_message(message)
        hint = f"{pre}Elige el centro con un toque o con el número de la lista.\n\n"
        return hint + t, st, qr

    def _match_specialty_nl(self, message: str, state: Dict[str, Any], today: date, now: datetime):
        rows = self.specialty_repo.get_active(skip=0, limit=200)
        hid = state.get("hospital_id")
        if hid:
            rows = [s for s in rows if self.hospital_repo.has_specialty(int(hid), s.id)]
        m = message.strip()
        if re.match(r"^\d+$", m):
            idx = int(m) - 1
            if 0 <= idx < len(rows):
                return self._apply_selection(
                    WizardSelectionPayload(step="specialty", specialty_id=rows[idx].id),
                    state,
                    today,
                    now,
                )
        low = m.lower()
        for s in rows:
            if s.name.lower() in low or low in s.name.lower():
                return self._apply_selection(
                    WizardSelectionPayload(step="specialty", specialty_id=s.id),
                    state,
                    today,
                    now,
                )
        t, st, qr = self._step_specialty(state, today, now)
        pre = _soft_opening_for_message(message)
        hint = f"{pre}Elige la especialidad con un toque o con el número de la lista.\n\n"
        return hint + t, st, qr

    def _match_room_nl(self, message: str, state: Dict[str, Any], today: date, now: datetime):
        hid = int(state["hospital_id"])
        sid = int(state["specialty_id"])
        rooms = self.room_repo.get_by_hospital_and_specialty(hid, sid)
        m = message.strip()
        if re.match(r"^\d+$", m):
            idx = int(m) - 1
            if 0 <= idx < len(rooms):
                return self._apply_selection(
                    WizardSelectionPayload(step="room", consultation_room_id=rooms[idx].id),
                    state,
                    today,
                    now,
                )
        low = m.lower()
        for r in rooms:
            if r.name.lower() in low or (r.room_number and r.room_number.lower() in low):
                return self._apply_selection(
                    WizardSelectionPayload(step="room", consultation_room_id=r.id),
                    state,
                    today,
                    now,
                )
        t, st, qr = self._step_room(state, today, now)
        pre = _soft_opening_for_message(message)
        hint = f"{pre}Elige consultorio con un toque o con el número o nombre de la lista.\n\n"
        return hint + t, st, qr

    def _step_hospital(self, state: Dict[str, Any], today: date, now: datetime):
        rows = self.hospital_repo.get_all(skip=0, limit=100, active_only=True)
        intro = "¿En qué centro te gustaría la visita? Elige abajo o dime el número de la lista."
        if state.get("anchor_date_iso"):
            intro += " (Más adelante afinamos la fecha si hace falta.)"
        opts = [
            {
                "label": h.name,
                "payload": WizardSelectionPayload(step="hospital", hospital_id=h.id).model_dump(
                    exclude_none=True
                ),
            }
            for h in rows
        ]
        qr = {"step": "hospital", "prompt": "", "options": opts}
        return intro, state, qr

    def _step_specialty(self, state: Dict[str, Any], today: date, now: datetime):
        rows = self.specialty_repo.get_active(skip=0, limit=200)
        hid = state.get("hospital_id")
        if hid:
            rows = [s for s in rows if self.hospital_repo.has_specialty(int(hid), s.id)]
        if not rows:
            state["phase"] = "hospital"
            state["hospital_id"] = None
            state["hospital_name"] = None
            return self._step_hospital(state, today, now)
        text = "¿Qué tipo de consulta necesitas? Elige la especialidad."
        opts = [
            {
                "label": s.name,
                "payload": WizardSelectionPayload(step="specialty", specialty_id=s.id).model_dump(exclude_none=True),
            }
            for s in rows
        ]
        qr = {"step": "specialty", "prompt": "", "options": opts}
        return text, state, qr

    def _step_room(
        self,
        state: Dict[str, Any],
        today: date,
        now: datetime,
        *,
        lead_paragraph: Optional[str] = None,
    ):
        hid = int(state["hospital_id"])
        sid = int(state["specialty_id"])
        rooms = self.room_repo.get_by_hospital_and_specialty(hid, sid)
        if not rooms:
            state["phase"] = "specialty"
            return (
                "Con esa especialidad no hay consultorio disponible; prueba con otra opción.",
                state,
                None,
            )
        ask = "¿Con qué consultorio te quedas? Puedes tocar una opción o escribir el nombre o el número."
        if lead_paragraph:
            text = f"{lead_paragraph}\n\n{ask}"
        else:
            text = ask
        opts = [
            {
                "label": f"{r.name}" + (f" — consultorio {r.room_number}" if r.room_number else ""),
                "payload": WizardSelectionPayload(
                    step="room", consultation_room_id=r.id
                ).model_dump(exclude_none=True),
            }
            for r in rooms
        ]
        qr = {"step": "room", "prompt": "", "options": opts}
        return text, state, qr

    def _first_available_dates_for_room(
        self, state: Dict[str, Any], today: date, now: datetime
    ) -> Tuple[List[date], str]:
        """Lista de fechas con hueco + nota (p. ej. bump si hoy ya no sirve). Puede mutar `anchor_date_iso`."""
        hid = int(state["hospital_id"])
        sid = int(state["specialty_id"])
        rid = int(state["consultation_room_id"])
        shift = state.get("shift_hint") or "any"

        start_from = today
        anchor_note = ""
        if state.get("anchor_date_iso"):
            ad = date.fromisoformat(state["anchor_date_iso"])
            ad = ensure_weekday_booking(ad)
            start_from = max(today, ad)

        if state.get("anchor_date_iso"):
            ad0 = date.fromisoformat(state["anchor_date_iso"])
            if ad0 == today:
                times_today = self.slot_service.collect_available_times_for_room(
                    hid, sid, rid, today, shift_hint=shift if shift != "any" else None
                )
                if not times_today:
                    nxt = suggest_date_when_today_has_no_slots(today)
                    state["anchor_date_iso"] = nxt.isoformat()
                    state["bumped_from_today"] = True
                    start_from = nxt
                    anchor_note = (
                        f"\n\nPara hoy ya no quedan huecos; seguimos a partir del **{_label_date_es(nxt)}**."
                    )

        dates = self.slot_service.first_available_dates_for_room(
            hid,
            sid,
            rid,
            start_from,
            shift_hint=shift if shift != "any" else None,
        )
        return dates, anchor_note

    def _after_room_selection(
        self, state: Dict[str, Any], today: date, now: datetime
    ) -> Tuple[str, Dict[str, Any], Optional[Dict[str, Any]]]:
        """
        Tras elegir consultorio: si el primer mensaje ya traía fecha/hora y hay hueco real,
        salta pasos redundantes (fecha y/o confirmación).
        """
        dates, anchor_note = self._first_available_dates_for_room(state, today, now)
        if not dates:
            return (
                "En los próximos días no vi huecos libres para ese consultorio. "
                "Prueba otro consultorio o especialidad, o escribe **salir** si prefieres parar.",
                state,
                None,
            )

        req_date_iso = state.get("user_requested_date_iso")
        req_time_raw = (state.get("user_requested_time_hhmm") or "").strip()

        chosen: Optional[date] = None
        if req_date_iso:
            try:
                cand = ensure_weekday_booking(date.fromisoformat(req_date_iso))
                if cand in dates:
                    chosen = cand
            except (ValueError, TypeError):
                chosen = None

        if chosen is not None:
            state["appointment_date_iso"] = chosen.isoformat()
            hid = int(state["hospital_id"])
            sid = int(state["specialty_id"])
            rid = int(state["consultation_room_id"])
            shift = state.get("shift_hint") or "any"
            times = self.slot_service.collect_available_times_for_room(
                hid, sid, rid, chosen, shift_hint=shift if shift != "any" else None
            )
            if not times:
                state["appointment_date_iso"] = None
                lead = (
                    f"El **{_label_date_es(chosen)}** que comentaste sigue en agenda, "
                    "pero ya no tiene huecos libres; elige otra fecha.\n\n"
                )
                state["phase"] = "date"
                return self._step_date(state, today, now, lead_prefix=lead)

            def fmt_tm(t: time) -> str:
                return t.strftime("%H:%M")

            labels = [fmt_tm(t) for t in times]
            matched_time: Optional[str] = None
            if req_time_raw:
                if req_time_raw in labels:
                    matched_time = req_time_raw
                else:
                    try:
                        rt = parse_time_string(req_time_raw)
                        for t, lbl in zip(times, labels):
                            if t.hour == rt.hour and t.minute == rt.minute:
                                matched_time = lbl
                                break
                    except ValueError:
                        matched_time = None

            if matched_time:
                state["appointment_time_hhmm"] = matched_time
                state["phase"] = "confirm"
                head = (
                    f"Vale: **{_label_date_es(chosen)}** a las **{matched_time}** encajan con lo que pediste "
                    "y hay hueco libre — solo falta confirmar.\n\n"
                )
                body, st, qr = self._step_confirm(state, today, now)
                return head + body, st, qr

            state["phase"] = "time"
            if req_time_raw:
                head = (
                    f"Dejé lista la fecha **{_label_date_es(chosen)}** que mencionaste. "
                    f"La hora **{req_time_raw}** no coincide con un inicio libre; elige otra de la lista.\n\n"
                )
            else:
                head = f"Dejé lista la fecha **{_label_date_es(chosen)}** que mencionaste. Elige hora:\n\n"
            t_part, st, qr = self._step_time(state, today, now)
            return head + t_part, st, qr

        lead_miss = ""
        if req_date_iso:
            try:
                missed = ensure_weekday_booking(date.fromisoformat(req_date_iso))
                if missed not in dates:
                    lead_miss = (
                        f"No vi cupo el **{_label_date_es(missed)}** entre las próximas fechas con hueco; "
                        "elige una de abajo.\n\n"
                    )
            except (ValueError, TypeError):
                lead_miss = ""

        state["phase"] = "date"
        return self._step_date(state, today, now, lead_prefix=lead_miss)

    def _step_date(
        self,
        state: Dict[str, Any],
        today: date,
        now: datetime,
        *,
        lead_prefix: str = "",
    ):
        dates, anchor_note = self._first_available_dates_for_room(state, today, now)
        if not dates:
            return (
                "En los próximos días no vi huecos libres para ese consultorio. "
                "Prueba otro consultorio o especialidad, o escribe **salir** si prefieres parar.",
                state,
                None,
            )

        text = lead_prefix + "Estos días tienen hueco libre; elige el que te encaje mejor." + anchor_note
        opts = [
            {
                "label": _label_date_es(d),
                "payload": WizardSelectionPayload(step="date", date_iso=d.isoformat()).model_dump(exclude_none=True),
            }
            for d in dates
        ]
        qr = {"step": "date", "prompt": "", "options": opts}
        return text, state, qr

    def _step_time(self, state: Dict[str, Any], today: date, now: datetime):
        hid = int(state["hospital_id"])
        sid = int(state["specialty_id"])
        rid = int(state["consultation_room_id"])
        ad = date.fromisoformat(state["appointment_date_iso"])
        shift = state.get("shift_hint") or "any"

        times = self.slot_service.collect_available_times_for_room(
            hid, sid, rid, ad, shift_hint=shift if shift != "any" else None
        )
        if not times:
            state["phase"] = "date"
            state["appointment_date_iso"] = None
            return self._step_date(
                state,
                today,
                now,
                lead_prefix="Ese día se llenó para ese consultorio. Elige otra fecha:\n\n",
            )

        def fmt(t) -> str:
            return t.strftime("%H:%M")

        text = "¿A qué hora te viene bien? (Son horarios de inicio de la cita.)"
        opts = [
            {
                "label": fmt(t),
                "payload": WizardSelectionPayload(step="time", time_hhmm=fmt(t)).model_dump(exclude_none=True),
            }
            for t in times
        ]
        qr = {"step": "time", "prompt": "", "options": opts}
        return text, state, qr

    def _step_confirm(self, state: Dict[str, Any], today: date, now: datetime):
        d = date.fromisoformat(state["appointment_date_iso"])
        t = state["appointment_time_hhmm"]
        text = (
            f"Quedaría así: **{state.get('hospital_name')}**, **{state.get('specialty_name')}**, "
            f"consultorio **{state.get('consultation_room_name')}**, el **{_label_date_es(d)}** "
            f"a las **{t}**. ¿Lo confirmamos?"
        )
        qr = {
            "step": "confirm",
            "prompt": "",
            "options": [
                {
                    "label": "Sí, confirmar",
                    "payload": WizardSelectionPayload(step="confirm", confirm=True).model_dump(exclude_none=True),
                },
                {
                    "label": "Prefiero otra hora",
                    "payload": WizardSelectionPayload(step="confirm", confirm=False).model_dump(exclude_none=True),
                },
            ],
        }
        return text, state, qr

    def _do_create(self, state: Dict[str, Any]) -> Tuple[str, Dict[str, Any], Optional[Dict[str, Any]]]:
        # create_appointment devuelve dict (no JSON string como dispatch() del LLM)
        data = self.executor.create_appointment(
            {
                "user_id": str(self.patient.id),
                "hospital_id": state["hospital_id"],
                "specialty_id": state["specialty_id"],
                "consultation_room_id": state["consultation_room_id"],
                "date": state["appointment_date_iso"],
                "time": state["appointment_time_hhmm"],
                "reason": "Cita vía asistente guiado",
            }
        )

        if data.get("ok"):
            st = _empty_state()
            apt = data.get("appointment") or {}
            when = apt.get("appointment_date") or state["appointment_date_iso"]
            tm = apt.get("start_time") or state["appointment_time_hhmm"]
            return (
                f"Listo: te dejé la cita el **{when}** a las **{str(tm)[:5]}**. "
                "Si quieres, seguimos con otra cosa.",
                st,
                None,
            )

        err = data.get("error") or "No se pudo guardar la cita."
        return f"No pude cerrar la reserva: {err}", state, None


def should_run_wizard(
    message: str,
    state_in: Optional[Dict[str, Any]],
    wizard_selection: Optional[WizardSelectionPayload] = None,
) -> bool:
    st = _merge_state(state_in)
    if wizard_selection is not None:
        return True
    if st.get("phase") not in (None, "", "idle"):
        return True
    return _looks_like_booking_start(message)
