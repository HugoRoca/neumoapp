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

_MONTH_NAMES_ES: dict[str, int] = {
    "enero": 1,
    "febrero": 2,
    "marzo": 3,
    "abril": 4,
    "mayo": 5,
    "junio": 6,
    "julio": 7,
    "agosto": 8,
    "septiembre": 9,
    "octubre": 10,
    "noviembre": 11,
    "diciembre": 12,
}


def _first_upcoming_calendar_date(month: int, day: int, today: date) -> Optional[date]:
    """Año inferido: hoy o próximos años hasta encontrar fecha válida y >= today."""
    for y in range(today.year, today.year + 5):
        try:
            cand = date(y, month, day)
        except ValueError:
            continue
        if cand >= today:
            return cand
    return None


def parse_explicit_calendar_date(message: str, today: date) -> Optional[date]:
    """
    Detecta fechas concretas en español o numéricas (p. ej. '11 de mayo', '11/05/2026').
    No interpreta 'mañana' (eso va en parse_booking_intent).
    """
    mlow = message.strip().lower()

    m = re.search(
        r"\b(?:el\s+)?(?P<d>\d{1,2})\s+de\s+(?P<mes>enero|febrero|marzo|abril|mayo|junio|julio|agosto|septiembre|octubre|noviembre|diciembre)"
        r"(?:\s+de\s+(?P<y>\d{4}))?\b",
        mlow,
    )
    if m:
        d = int(m.group("d"))
        month = _MONTH_NAMES_ES[m.group("mes")]
        if m.group("y"):
            try:
                cand = date(int(m.group("y")), month, d)
            except ValueError:
                return None
            return cand if cand >= today else None
        return _first_upcoming_calendar_date(month, d, today)

    # dd/mm/yyyy o dd-mm-yyyy (uso habitual en ES/Latam)
    m = re.search(r"\b(\d{1,2})[/-](\d{1,2})[/-](\d{4})\b", mlow)
    if m:
        d, month, y = int(m.group(1)), int(m.group(2)), int(m.group(3))
        try:
            cand = date(y, month, d)
        except ValueError:
            return None
        return cand if cand >= today else None

    # yyyy-mm-dd
    m = re.search(r"\b(\d{4})[/-](\d{1,2})[/-](\d{1,2})\b", mlow)
    if m:
        y, month, d = int(m.group(1)), int(m.group(2)), int(m.group(3))
        try:
            cand = date(y, month, d)
        except ValueError:
            return None
        return cand if cand >= today else None

    return None


def parse_calendar_preferences_from_message(message: str, today: date) -> Tuple[Optional[date], Optional[str]]:
    """
    Fecha explícita + hora en lenguaje natural (p. ej. '8am', '08:00', 'a las 8').
    Devuelve (fecha | None, 'HH:MM' | None).
    """
    from app.services.chat_tool_executor import parse_time_string

    d_part = parse_explicit_calendar_date(message, today)
    mlow = message.strip().lower()
    time_part: Optional[str] = None

    # 8am / 8:30pm (parse_time_string acepta variantes)
    for m in re.finditer(r"\b(\d{1,2}(?::\d{2})?\s*(?:am|pm))\b", mlow):
        try:
            t = parse_time_string(m.group(1))
            time_part = f"{t.hour:02d}:{t.minute:02d}"
            break
        except ValueError:
            continue

    if time_part is None:
        for m in re.finditer(r"\b(\d{1,2}:\d{2})(?::\d{2})?\b", message):
            try:
                t = parse_time_string(m.group(1))
                time_part = f"{t.hour:02d}:{t.minute:02d}"
                break
            except ValueError:
                continue

    if time_part is None:
        m = re.search(r"\ba\s+las\s+(\d{1,2})(?::(\d{2}))?\b", mlow)
        if m:
            h, mn = int(m.group(1)), int(m.group(2) or 0)
            if 0 <= h <= 23 and 0 <= mn <= 59:
                time_part = f"{h:02d}:{mn:02d}"

    return d_part, time_part


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
