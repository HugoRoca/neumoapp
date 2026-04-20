"""
Reglas de calendario compartidas: citas solo lun–vie, 'mañana' hábil, etc.
Usado por el asistente IA y por el flujo guiado de agendamiento.
"""

from __future__ import annotations

import re
from datetime import date, datetime, timedelta
from typing import Literal, Optional, Tuple
from zoneinfo import ZoneInfo

from app.core.config import settings


def first_weekday_on_or_after(d: date) -> date:
    """Primer lunes–viernes en o después de d (d inclusive)."""
    one = timedelta(days=1)
    while d.weekday() >= 5:
        d += one
    return d


def calendar_tomorrow(today: date) -> date:
    return today + timedelta(days=1)


def date_for_manana_cita(today: date) -> date:
    """
    Si el usuario dice 'mañana' para una cita: el día calendario siguiente,
    o el primer hábil si ese día es sábado/domingo.
    """
    tmr = calendar_tomorrow(today)
    if tmr.weekday() < 5:
        return tmr
    return first_weekday_on_or_after(tmr)


def ensure_weekday_booking(d: date) -> date:
    """Si cae en fin de semana, avanza al siguiente día hábil."""
    return first_weekday_on_or_after(d)


def next_business_day_after(d: date) -> date:
    """Primer día hábil estrictamente después de d."""
    nxt = d + timedelta(days=1)
    return first_weekday_on_or_after(nxt)


def date_for_pasado_manana(today: date) -> date:
    return ensure_weekday_booking(today + timedelta(days=2))


def app_today_now() -> Tuple[date, datetime]:
    tz = ZoneInfo(settings.APP_TIMEZONE or "America/Lima")
    now = datetime.now(tz)
    return now.date(), now


def suggest_date_when_today_has_no_slots(today: date) -> date:
    """Si 'hoy' ya no tiene cupos, la siguiente opción es 'mañana' hábil."""
    return date_for_manana_cita(today)


ShiftHint = Optional[Literal["morning", "afternoon", "any"]]


def parse_booking_intent(message: str, today: date) -> Tuple[Optional[date], ShiftHint]:
    """
    Extrae fecha deseada (si se menciona) y preferencia de turno desde lenguaje natural.
    No es exhaustivo; el wizard puede refinar después.
    """
    m = message.lower()
    shift: ShiftHint = "any"
    if re.search(r"\b(por la tarde|en la tarde|esta tarde|hoy en la tarde)\b", m):
        shift = "afternoon"
    elif re.search(r"\b(por la mañana|en la mañana|esta mañana|hoy en la mañana|mañana por la mañana)\b", m):
        shift = "morning"

    anchor: Optional[date] = None
    if re.search(r"\bhoy\b", m):
        anchor = today
    elif re.search(r"\bpasado\s+mañana\b", m):
        anchor = date_for_pasado_manana(today)
    elif re.search(r"\bmañana\b", m):
        anchor = date_for_manana_cita(today)

    return anchor, shift
