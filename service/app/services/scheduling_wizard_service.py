"""
Flujo guiado (wizard) para agendar citas: Hospital → Especialidad → Consultorio → Fecha → Hora → Confirmar.
La lógica de negocio y disponibilidad vive aquí; el frontend solo muestra botones y reenvía estado.
"""

from __future__ import annotations

import re
from datetime import date, datetime, timedelta
from typing import Any, Dict, List, Optional, Tuple

from sqlalchemy.orm import Session

from app.models.patient import Patient
from app.schemas.chat import WizardSelectionPayload
from app.repositories.consultation_room_repository import ConsultationRoomRepository
from app.repositories.hospital_repository import HospitalRepository
from app.repositories.specialty_repository import SpecialtyRepository
from app.services.chat_tool_executor import ChatToolExecutor, parse_iso_date, parse_time_string
from app.services.scheduling_dates import (
    app_today_now,
    ensure_weekday_booking,
    parse_booking_intent,
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
                    "Para empezar, escribe que quieres **agendar una cita** o usa la sugerencia «Agendar mañana».",
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
                "Salimos del agendamiento guiado. Vuelve a preguntar por tus citas y te ayudo con el listado.",
                st,
                None,
            )

        if state.get("phase") == "idle" and _looks_like_booking_start(message):
            anchor, shift = parse_booking_intent(message, today)
            state["phase"] = "hospital"
            state["shift_hint"] = shift or "any"
            if anchor:
                state["anchor_date_iso"] = ensure_weekday_booking(anchor).isoformat()
            return self._step_hospital(state, today, now)

        if state.get("phase") not in (None, "idle") and _wants_exit_wizard(message):
            st = _empty_state()
            return (
                "Listo, salimos del agendamiento guiado. ¿En qué más te ayudo?",
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
            hint = (
                f"{pre}Cuando quieras, elige el día tocando una de las fechas de abajo.\n\n"
            )
            return hint + t, st, qr
        if phase == "time":
            t, st, qr = self._step_time(state, today, now)
            pre = _soft_opening_for_message(message)
            hint = f"{pre}Elige la hora con los botones de abajo.\n\n"
            return hint + t, st, qr
        if phase == "confirm":
            t, st, qr = self._step_confirm(state, today, now)
            pre = _soft_opening_for_message(message)
            hint = (
                f"{pre}Revisa el resumen y confirma abajo, o elige cambiar la hora si lo prefieres.\n\n"
            )
            return hint + t, st, qr

        return (
            "Si querés seguir con la reserva, elegí una opción con los botones del mensaje anterior. "
            "Si preferís hablar de otra cosa, escribí **salir** y seguimos por ahí.",
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
                "Este paso ya no coincide. Mira el último mensaje del asistente o escribe **salir** para reiniciar.",
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
            state["phase"] = "date"
            return self._step_date(state, today, now)

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
        hint = f"{pre}Para elegir el centro, toca un botón o responde con el número de la lista.\n\n"
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
        hint = f"{pre}Elige la especialidad con un botón o con el número de la lista.\n\n"
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
        hint = f"{pre}Elige el consultorio con un botón o con el número de la lista.\n\n"
        return hint + t, st, qr

    def _step_hospital(self, state: Dict[str, Any], today: date, now: datetime):
        rows = self.hospital_repo.get_all(skip=0, limit=100, active_only=True)
        intro = "**Paso 1 — Hospital**\n\nSelecciona el centro donde deseas atenderte."
        if state.get("anchor_date_iso"):
            intro += "\n\n(Tomaremos en cuenta tu preferencia de fecha más adelante.)"
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
        text = "**Paso 2 — Especialidad**\n\n¿En qué especialidad necesitas la consulta?"
        opts = [
            {
                "label": s.name,
                "payload": WizardSelectionPayload(step="specialty", specialty_id=s.id).model_dump(exclude_none=True),
            }
            for s in rows
        ]
        qr = {"step": "specialty", "prompt": "", "options": opts}
        return text, state, qr

    def _step_room(self, state: Dict[str, Any], today: date, now: datetime):
        hid = int(state["hospital_id"])
        sid = int(state["specialty_id"])
        rooms = self.room_repo.get_by_hospital_and_specialty(hid, sid)
        if not rooms:
            state["phase"] = "specialty"
            return (
                "No hay consultorios para esa combinación; elige otra especialidad.",
                state,
                None,
            )
        text = "**Paso 3 — Consultorio / médico**\n\nElige el consultorio donde te atenderán."
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

    def _step_date(self, state: Dict[str, Any], today: date, now: datetime):
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
                        f"\n\nPara **hoy** ya no hay horarios disponibles; "
                        f"te propongo seguir con fechas desde **{_label_date_es(nxt)}**."
                    )

        dates = self.slot_service.first_available_dates_for_room(
            hid,
            sid,
            rid,
            start_from,
            shift_hint=shift if shift != "any" else None,
        )
        if not dates:
            return (
                "No encontré fechas libres en los próximos días para este consultorio. "
                "Prueba otro consultorio o especialidad (escribe **salir** para salir del flujo).",
                state,
                None,
            )

        text = "**Paso 4 — Fecha**\n\nElige un día con disponibilidad." + anchor_note
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
            return (
                "Ese día ya no tiene huecos para ese consultorio. Elige otra fecha.",
                state,
                None,
            )

        def fmt(t) -> str:
            return t.strftime("%H:%M")

        text = "**Paso 5 — Hora**\n\nElige la hora de inicio de tu cita."
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
            "**Resumen**\n"
            f"- **Hospital:** {state.get('hospital_name')}\n"
            f"- **Especialidad:** {state.get('specialty_name')}\n"
            f"- **Consultorio:** {state.get('consultation_room_name')}\n"
            f"- **Fecha:** {_label_date_es(d)}\n"
            f"- **Hora:** {t}\n\n"
            "¿Deseas confirmar la cita?"
        )
        qr = {
            "step": "confirm",
            "prompt": "",
            "options": [
                {
                    "label": "Confirmar",
                    "payload": WizardSelectionPayload(step="confirm", confirm=True).model_dump(exclude_none=True),
                },
                {
                    "label": "Cambiar hora",
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
                f"Listo, tu cita quedó registrada para el **{when}** a las **{str(tm)[:5]}**. "
                "¿Necesitas algo más?",
                st,
                None,
            )

        err = data.get("error") or "No se pudo crear la cita."
        return f"No pude confirmar: {err}", state, None


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
