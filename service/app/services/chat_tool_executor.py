"""
Ejecuta las herramientas que el modelo LLM solicita, delegando en AppointmentService
y repositorios existentes. Todas las operaciones quedan acotadas al paciente autenticado.
"""

from __future__ import annotations

import json
import re
from datetime import date, datetime, time, timedelta
from typing import Any, Dict, List, Optional
from zoneinfo import ZoneInfo

from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.core.config import settings
from app.models.appointment import Appointment
from app.models.patient import Patient
from app.schemas.appointment import AppointmentCreate
from app.repositories.consultation_room_repository import ConsultationRoomRepository
from app.repositories.hospital_repository import HospitalRepository
from app.repositories.specialty_repository import SpecialtyRepository
from app.services.appointment_service import AppointmentService
from app.services.slot_service import SlotService


def _appointment_to_dict(apt: Appointment) -> Dict[str, Any]:
    """Serializa una cita a JSON-friendly (sin inventar datos)."""
    spec = getattr(apt, "specialty", None)
    room = getattr(apt, "consultation_room", None)
    return {
        "id": apt.id,
        "patient_id": apt.patient_id,
        "specialty_id": apt.specialty_id,
        "specialty_name": spec.name if spec else None,
        "consultation_room_id": apt.consultation_room_id,
        "consultation_room_name": room.name if room else None,
        "room_number": room.room_number if room else None,
        "appointment_date": apt.appointment_date.isoformat(),
        "start_time": apt.start_time.strftime("%H:%M:%S"),
        "end_time": apt.end_time.strftime("%H:%M:%S"),
        "shift": apt.shift,
        "status": apt.status if isinstance(apt.status, str) else getattr(apt.status, "value", str(apt.status)),
        "reason": apt.reason,
    }


def parse_iso_date(s: str) -> date:
    s = s.strip()
    try:
        return date.fromisoformat(s)
    except ValueError as e:
        raise ValueError(f"Fecha inválida (usa YYYY-MM-DD): {s}") from e


def parse_time_string(s: str) -> time:
    """
    Interpreta horas como 15:00, 15:00:00, 3pm, 3:30pm, 6.30pm (punto como separador).
    """
    raw = s.strip().lower()
    compact = re.sub(r"\s+", "", raw)
    m_dot = re.match(r"^(\d{1,2})\.(\d{2})(am|pm)$", compact)
    if m_dot:
        raw = f"{m_dot.group(1)}:{m_dot.group(2)} {m_dot.group(3)}"
    for fmt in ("%H:%M:%S", "%H:%M"):
        try:
            return datetime.strptime(raw, fmt).time()
        except ValueError:
            continue
    m = re.match(r"^(\d{1,2})(?::(\d{2}))?\s*(am|pm)$", raw.replace(" ", ""))
    if m:
        h = int(m.group(1))
        mn = int(m.group(2) or 0)
        ap = m.group(3)
        if ap == "pm" and h != 12:
            h += 12
        if ap == "am" and h == 12:
            h = 0
        return time(h, mn)
    raise ValueError(f"Hora inválida: {s}")


class ChatToolExecutor:
    def __init__(self, db: Session, patient: Patient):
        self.db = db
        self.patient = patient
        self.appointment_service = AppointmentService(db)
        self.hospital_repo = HospitalRepository(db)
        self.specialty_repo = SpecialtyRepository(db)
        self.room_repo = ConsultationRoomRepository(db)
        self.slot_service = SlotService(db)

    def _ensure_user(self, user_id: str) -> None:
        if str(self.patient.id) != str(user_id).strip():
            raise ValueError("user_id no coincide con el paciente autenticado")

    def list_hospitals(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """Lista centros activos (id y nombre) para alinear con lo que el usuario dijo."""
        rows = self.hospital_repo.get_all(skip=0, limit=100, active_only=True)
        return {
            "ok": True,
            "hospitals": [{"id": h.id, "name": h.name} for h in rows],
        }

    def list_specialties(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """
        Lista especialidades activas. Si hospital_id está presente, solo las que atiende ese hospital.
        """
        rows = self.specialty_repo.get_active(skip=0, limit=200)
        hid = args.get("hospital_id")
        if hid is not None and str(hid).strip() != "":
            hospital_id = int(str(hid).strip())
            rows = [s for s in rows if self.hospital_repo.has_specialty(hospital_id, s.id)]
        return {
            "ok": True,
            "specialties": [{"id": s.id, "name": s.name} for s in rows],
        }

    def list_consultation_rooms(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """Consultorios para un hospital y especialidad concretos."""
        hid = args.get("hospital_id")
        sid = args.get("specialty_id")
        if hid is None or str(hid).strip() == "" or sid is None or str(sid).strip() == "":
            return {
                "ok": False,
                "error": "Indica hospital_id y specialty_id para listar consultorios.",
            }
        hospital_id = int(str(hid).strip())
        specialty_id = int(str(sid).strip())
        rooms = self.room_repo.get_by_hospital_and_specialty(hospital_id, specialty_id)
        return {
            "ok": True,
            "consultation_rooms": [
                {"id": r.id, "name": r.name, "room_number": r.room_number} for r in rooms
            ],
        }

    def get_scheduling_rules(self) -> Dict[str, Any]:
        """
        Datos estáticos para el LLM: no confundir con get_appointments (citas ya reservadas).
        """
        tz = ZoneInfo(settings.APP_TIMEZONE or "America/Lima")
        now = datetime.now(tz)
        dias = ("lunes", "martes", "miércoles", "jueves", "viernes", "sábado", "domingo")
        today_local = now.date()
        tomorrow_local = today_local + timedelta(days=1)
        first_booking_day = tomorrow_local
        while first_booking_day.weekday() >= 5:
            first_booking_day += timedelta(days=1)
        return {
            "ok": True,
            "hora_referencia": now.strftime("%Y-%m-%dT%H:%M:%S"),
            "zona_horaria": settings.APP_TIMEZONE,
            "dia_semana_hoy": dias[now.weekday()],
            "fecha_hoy": today_local.isoformat(),
            "maniana_dia_calendario": tomorrow_local.isoformat(),
            "primera_fecha_habil_si_pidieran_manana": first_booking_day.isoformat(),
            "nota_maniana_fin_de_semana": (
                "Si hoy es sábado, 'mañana' en calendario es domingo: sin citas. "
                "La primera fecha de cita posible suele ser el lunes (ver primera_fecha_habil_si_pidieran_manana)."
            ),
            "dias_habiles": "Solo lunes a viernes. No se agendan citas sábado ni domingo.",
            "duracion_cita_minutos": 20,
            "turno_manana": "Mañana: inicios entre 08:00 y 12:59 (hasta ~13:00; slots cada 20 min).",
            "turno_tarde": "Tarde: inicios entre 14:00 y 17:59 (hasta ~18:00; slots cada 20 min).",
            "despues_de_18h": "Si la hora local ya es 18:00 o más en un día hábil, prioriza ofrecer el siguiente día hábil para nuevas citas, no insistir en 'hoy'.",
            "hueco_mediodia": "No hay citas entre 13:00 y 13:59 (ej. 1:30 pm no es válido). Usa 12:40 o 14:00.",
            "regla_hoy": "Para la fecha de hoy solo tienen sentido horas posteriores a hora_referencia; no ofrezcas mañanas del mismo día si ya pasaron.",
            "no_fechas_pasadas": "No se agendan citas en ayer ni fechas anteriores a hoy. No pidas hora para esos días.",
            "ultimo_inicio_turno_tarde": "17:40 (slots cada 20 min desde 14:00; el último inicio antes del cierre de tarde).",
            "hora_18_no_valida": "Las 18:00 (6:00 pm) NO son hora de inicio: la tarde va de 14:00 a antes de 18:00. Pedir 6 pm es fuera de franja, no es 'ayer'.",
            "no_turnos_nocturnos": "No hay citas nocturnas: 9pm, 8pm, 7pm ni 6:30pm como inicio no existen en este sistema. No ofrezcas 18:40, 19:20 ni 'más tarde esta noche' como alternativas: no son slots válidos (último inicio tarde típico 17:40).",
            "error_kind_ayuda": "Si create_appointment devuelve error_kind 'out_of_schedule', el problema es reglamento de horario, NO que la hora 'haya pasado'. Solo 'past_time_today' significa que hoy esa hora ya quedó atrás.",
            "nota_get_appointments": "get_appointments lista las citas que el usuario YA tiene reservadas, no muestra horas libres del hospital.",
        }

    def create_appointment(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """create_appointment(date, time, user_id, specialty_id, hospital_id, consultation_room_id, reason?)"""
        self._ensure_user(str(args.get("user_id", "")))

        missing = []
        for key in ("specialty_id", "hospital_id", "consultation_room_id"):
            v = args.get(key)
            if v is None or (isinstance(v, str) and not str(v).strip()):
                missing.append(key)
        if missing:
            return {
                "ok": False,
                "error_kind": "missing_fields",
                "error": (
                    "Faltan datos obligatorios para crear la cita: "
                    + ", ".join(missing)
                    + ". Usa list_hospitals, list_specialties y list_consultation_rooms para obtener ids "
                    "tras acordar con el usuario hospital, especialidad y consultorio."
                ),
            }

        try:
            spec_id = int(str(args["specialty_id"]).strip())
            hospital_id = int(str(args["hospital_id"]).strip())
            room_id = int(str(args["consultation_room_id"]).strip())
        except (TypeError, ValueError):
            return {
                "ok": False,
                "error_kind": "invalid_ids",
                "error": "hospital_id, specialty_id y consultation_room_id deben ser números enteros válidos.",
            }

        appt_date = parse_iso_date(str(args["date"]))
        start_t = parse_time_string(str(args["time"]))

        tz = ZoneInfo(settings.APP_TIMEZONE or "America/Lima")
        today_local = datetime.now(tz).date()

        if appt_date < today_local:
            return {
                "ok": False,
                "error_kind": "past_date",
                "error": (
                    "No se pueden agendar citas en fechas pasadas (ayer o antes). "
                    "Solo desde hoy en adelante, en días hábiles."
                ),
            }

        if appt_date.weekday() >= 5:
            return {
                "ok": False,
                "error_kind": "weekend",
                "error": "Las citas solo son de lunes a viernes. No se puede agendar sábado ni domingo; elige un día hábil.",
            }

        now_local = datetime.now(tz)
        if appt_date == today_local and start_t <= now_local.time():
            return {
                "ok": False,
                "error_kind": "past_time_today",
                "error": (
                    "Esa hora de hoy ya pasó o es ahora mismo. "
                    "Elige una hora más tarde hoy u otra fecha."
                ),
            }

        if time(8, 0) <= start_t < time(13, 0):
            shift_str = "morning"
        elif time(14, 0) <= start_t < time(18, 0):
            shift_str = "afternoon"
        else:
            return {
                "ok": False,
                "error_kind": "out_of_schedule",
                "error": (
                    "Hora fuera de franja (no es que haya 'pasado': esta hora no se atiende). "
                    "Mañana: inicios 08:00–12:59; tarde: 14:00–17:59 cada 20 min (último inicio tarde 17:40). "
                    "Las 18:00 (6 pm), 6:30 pm, 9 pm no son inicios válidos. "
                    "Entre 13:00 y 13:59 no hay turno. Ej.: 10:00, 14:00, 16:20, 17:40."
                ),
            }

        hospital = self.hospital_repo.get_by_id(hospital_id)
        if not hospital or not hospital.active:
            return {
                "ok": False,
                "error_kind": "invalid_hospital",
                "error": "El hospital indicado no existe o no está activo.",
            }

        spec = self.specialty_repo.get_by_id(spec_id)
        if not spec or not spec.active:
            return {
                "ok": False,
                "error_kind": "invalid_specialty",
                "error": "La especialidad indicada no existe o no está activa.",
            }

        if not self.hospital_repo.has_specialty(hospital_id, spec_id):
            return {
                "ok": False,
                "error_kind": "specialty_not_at_hospital",
                "error": "Esa especialidad no está disponible en el hospital elegido.",
            }

        rooms_here = self.room_repo.get_by_hospital_and_specialty(hospital_id, spec_id)
        if not any(r.id == room_id for r in rooms_here):
            return {
                "ok": False,
                "error_kind": "invalid_room",
                "error": "El consultorio no corresponde a ese hospital y especialidad, o no está activo.",
            }

        try:
            slots_resp = self.slot_service.get_available_slots(
                hospital_id=hospital_id,
                specialty_id=spec_id,
                check_date=appt_date,
                shift=shift_str,
                room_id=room_id,
            )
        except HTTPException as e:
            return {
                "ok": False,
                "error_kind": "slots_lookup_failed",
                "error": _http_detail(e),
            }

        slot_ok = any(
            slot.start_time == start_t and slot.available for slot in slots_resp.slots
        )
        if not slot_ok:
            return {
                "ok": False,
                "error_kind": "no_room_available",
                "error": "Ese horario no está disponible en el consultorio elegido (ocupado o fuera de reglas).",
            }

        reason = args.get("reason") or "Consulta solicitada vía asistente"
        create = AppointmentCreate(
            specialty_id=spec_id,
            consultation_room_id=room_id,
            appointment_date=appt_date,
            start_time=start_t,
            shift=shift_str,
            reason=str(reason)[:500],
        )
        try:
            apt = self.appointment_service.book_appointment(create, self.patient)
        except HTTPException as e:
            return {
                "ok": False,
                "error_kind": "booking_failed",
                "error": _http_detail(e),
            }
        self.db.refresh(apt)
        return {"ok": True, "appointment": _appointment_to_dict(apt)}

    def get_appointments(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """get_appointments(user_id, date?)"""
        self._ensure_user(str(args.get("user_id", "")))
        filter_date: Optional[date] = None
        if args.get("date"):
            filter_date = parse_iso_date(str(args["date"]))
        try:
            rows, _ = self.appointment_service.get_my_appointments(self.patient, skip=0, limit=100)
        except HTTPException as e:
            return {"ok": False, "error": _http_detail(e)}
        out: List[Dict[str, Any]] = []
        for apt in rows:
            if filter_date and apt.appointment_date != filter_date:
                continue
            out.append(_appointment_to_dict(apt))
        return {"ok": True, "appointments": out, "count": len(out)}

    def update_appointment(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """update_appointment(id, user_id, date?, time?) — reprograma fecha/hora real."""
        self._ensure_user(str(args.get("user_id", "")))
        aid = int(str(args["id"]).strip())

        apt = self.appointment_service.get_appointment_by_id(aid, self.patient)
        new_date = apt.appointment_date
        new_time = apt.start_time

        if args.get("date"):
            new_date = parse_iso_date(str(args["date"]))
        if args.get("time"):
            new_time = parse_time_string(str(args["time"]))

        if not args.get("date") and not args.get("time"):
            return {
                "ok": False,
                "error": "Indica al menos una nueva fecha o una nueva hora para reprogramar.",
            }

        try:
            updated = self.appointment_service.reschedule_appointment_datetime(
                appointment_id=aid,
                new_date=new_date,
                new_start_time=new_time,
                current_patient=self.patient,
            )
        except HTTPException as e:
            return {"ok": False, "error": _http_detail(e)}
        self.db.refresh(updated)
        return {"ok": True, "appointment": _appointment_to_dict(updated)}

    def delete_appointment(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """delete_appointment(id, user_id) — cancela la cita (libera el slot)."""
        self._ensure_user(str(args.get("user_id", "")))
        aid = int(str(args["id"]).strip())
        try:
            msg = self.appointment_service.cancel_appointment(aid, self.patient)
        except HTTPException as e:
            return {"ok": False, "error": _http_detail(e)}
        return {"ok": True, "appointment_id": aid, "message": msg.get("message", "Cancelled")}

    def dispatch(self, name: str, arguments_json: str) -> str:
        """Punto único de entrada desde OpenAI tool_calls."""
        try:
            args = json.loads(arguments_json or "{}")
        except json.JSONDecodeError:
            return json.dumps({"ok": False, "error": "Argumentos JSON inválidos"})

        try:
            if name == "get_scheduling_rules":
                return json.dumps(self.get_scheduling_rules(), ensure_ascii=False)
            if name == "list_hospitals":
                return json.dumps(self.list_hospitals(args), ensure_ascii=False)
            if name == "list_specialties":
                return json.dumps(self.list_specialties(args), ensure_ascii=False)
            if name == "list_consultation_rooms":
                return json.dumps(self.list_consultation_rooms(args), ensure_ascii=False)
            if name == "create_appointment":
                return json.dumps(self.create_appointment(args), ensure_ascii=False)
            if name == "get_appointments":
                return json.dumps(self.get_appointments(args), ensure_ascii=False)
            if name == "update_appointment":
                return json.dumps(self.update_appointment(args), ensure_ascii=False)
            if name == "delete_appointment":
                return json.dumps(self.delete_appointment(args), ensure_ascii=False)
            return json.dumps({"ok": False, "error": f"Herramienta desconocida: {name}"})
        except ValueError as e:
            err = str(e)
            kind = "invalid_argument"
            if err.startswith("Hora inválida"):
                kind = "invalid_time_format"
            elif err.startswith("Fecha inválida"):
                kind = "invalid_date_format"
            return json.dumps(
                {"ok": False, "error": err, "error_kind": kind},
                ensure_ascii=False,
            )
        except HTTPException as e:
            return json.dumps({"ok": False, "error": _http_detail(e)}, ensure_ascii=False)


def _http_detail(e: HTTPException) -> str:
    d = e.detail
    if isinstance(d, list):
        return "; ".join(str(x) for x in d)
    return str(d)


# Definición de herramientas en formato OpenAI Chat Completions
OPENAI_CHAT_TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "get_scheduling_rules",
            "description": (
                "Devuelve reglas fijas: días hábiles (lun–vie), franjas mañana/tarde, hueco de mediodía, duración, "
                "qué horas NO existen (noche, 9pm, etc.), y fechas de referencia (maniana_dia_calendario vs primera fecha hábil). "
                "En una **nueva reserva**, llámala **antes** de list_hospitals cuando el usuario diga 'mañana', un día de la semana o una fecha: "
                "valida si ese día puede tener citas. "
                "También si preguntan por horarios, sábado/domingo, 9pm. "
                "NO lista citas del usuario (para eso es get_appointments)."
            ),
            "parameters": {"type": "object", "properties": {}},
        },
    },
    {
        "type": "function",
        "function": {
            "name": "list_hospitals",
            "description": (
                "Lista hospitales/centros activos con id y nombre. "
                "Llámala **después** de get_scheduling_rules cuando ya esté claro **qué día** es posible (o la primera fecha hábil). "
                "Antes de list_specialties. Presenta nombres numerados (1, 2, 3)."
            ),
            "parameters": {"type": "object", "properties": {}},
        },
    },
    {
        "type": "function",
        "function": {
            "name": "list_specialties",
            "description": (
                "Lista especialidades médicas activas con id y nombre. "
                "Si el usuario ya eligió hospital, pasa hospital_id para ver solo especialidades disponibles en ese centro."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "hospital_id": {
                        "type": "integer",
                        "description": "Opcional. Filtra especialidades atendidas en ese hospital.",
                    },
                },
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "list_consultation_rooms",
            "description": (
                "Lista consultorios (id, nombre, número) para un hospital y especialidad dados. "
                "Llámala después de tener hospital_id y specialty_id acordados con el usuario."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "hospital_id": {"type": "integer", "description": "Id del hospital"},
                    "specialty_id": {"type": "integer", "description": "Id de la especialidad"},
                },
                "required": ["hospital_id", "specialty_id"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "create_appointment",
            "description": (
                "Crea una cita en el sistema. Requiere fecha YYYY-MM-DD, hora (HH:MM o 3pm), "
                "y los ids numéricos hospital_id, specialty_id, consultation_room_id obtenidos con las herramientas de listado. "
                "Orden en diálogo: hospital → especialidad → consultorio → turno coherente → día hábil → hora concreta. "
                "NO llames sin esos tres ids: primero lista y alinea con lo que dijo el usuario. "
                "NO confirmes al usuario que la cita quedó hecha si no ejecutaste esta función y devolvió ok:true. "
                "NO uses como hora solo 'tarde' o 'mañana' sin reloj. "
                "Si ok:false, usa error y error_kind; con out_of_schedule no digas que la hora 'ya pasó'."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "date": {"type": "string", "description": "Fecha en YYYY-MM-DD"},
                    "time": {
                        "type": "string",
                        "description": "Hora: HH:MM 24h o formato como 3pm",
                    },
                    "user_id": {
                        "type": "string",
                        "description": (
                            "ID interno del paciente en sesión; no se pide al usuario. "
                            "Debe coincidir con el paciente autenticado."
                        ),
                    },
                    "hospital_id": {
                        "type": "integer",
                        "description": "Id del hospital acordado (list_hospitals).",
                    },
                    "specialty_id": {
                        "type": "integer",
                        "description": (
                            "Id de la especialidad acordada (list_specialties). No inventes: debe coincidir con la elección del usuario."
                        ),
                    },
                    "consultation_room_id": {
                        "type": "integer",
                        "description": "Id del consultorio acordado (list_consultation_rooms).",
                    },
                    "reason": {"type": "string", "description": "Motivo de la consulta (opcional)"},
                },
                "required": [
                    "date",
                    "time",
                    "user_id",
                    "hospital_id",
                    "specialty_id",
                    "consultation_room_id",
                ],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_appointments",
            "description": (
                "Lista las citas que este paciente YA TIENE agendadas (reservas propias). "
                "El usuario ya está autenticado en la app: NO pidas nombre, DNI ni datos para identificarlo. "
                "Incluye id, especialidad, fecha, hora. NO es el horario libre del consultorio ni disponibilidad general. "
                "Úsala para ver/cancelar/reprogramar citas existentes cuando falte el id. "
                "Para preguntas como 'qué horarios existen' o 'sábado hay?' usa get_scheduling_rules. "
                "Filtro opcional date YYYY-MM-DD."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "user_id": {
                        "type": "string",
                        "description": (
                            "ID interno del paciente en sesión (el backend ya lo conoce; "
                            "no se obtiene preguntando al usuario). Debe coincidir con el paciente autenticado."
                        ),
                    },
                    "date": {
                        "type": "string",
                        "description": "Opcional. Filtrar citas de este día (YYYY-MM-DD)",
                    },
                },
                "required": ["user_id"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "update_appointment",
            "description": (
                "Reprograma una cita (nueva fecha y/o hora). "
                "No pidas DNI ni nombre: el paciente ya está autenticado. "
                "El id debe venir de get_appointments. Si el usuario no dijo qué cita, lista antes con get_appointments."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "id": {
                        "type": "string",
                        "description": "ID de la cita según get_appointments",
                    },
                    "user_id": {
                        "type": "string",
                        "description": (
                            "ID interno del paciente en sesión; no se pide al usuario. "
                            "Debe coincidir con el paciente autenticado."
                        ),
                    },
                    "date": {"type": "string", "description": "Nueva fecha YYYY-MM-DD (opcional)"},
                    "time": {"type": "string", "description": "Nueva hora HH:MM o 3pm (opcional)"},
                },
                "required": ["id", "user_id"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "delete_appointment",
            "description": (
                "Cancela una cita por su id numérico (libera el horario). "
                "No pidas DNI ni nombre: el paciente ya está autenticado. "
                "El id debe ser el que devolvió get_appointments en el campo id. "
                "No inventes ids: si el usuario no especifica cuál cita, llama antes get_appointments."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "id": {
                        "type": "string",
                        "description": "ID numérico de la cita (string), tal como en get_appointments",
                    },
                    "user_id": {
                        "type": "string",
                        "description": (
                            "ID interno del paciente en sesión; no se pide al usuario. "
                            "Debe coincidir con el paciente autenticado."
                        ),
                    },
                },
                "required": ["id", "user_id"],
            },
        },
    },
]
