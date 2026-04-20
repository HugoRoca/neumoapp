import { addDays } from 'date-fns'
import apiClient from '@/services/api.service'
import { API_CONFIG } from '@/config/api.config'

/** Misma zona que el backend (`APP_TIMEZONE`). Configura `VITE_APP_TIMEZONE` en el cliente si difiere. */
export const APP_TIMEZONE = import.meta.env.VITE_APP_TIMEZONE || 'America/Lima'

/** A partir de esta hora (inclusive) ya no se ofrece el día actual como primera opción (alineado con backend). */
export const BOOKING_DAY_END_HOUR = 18

export function formatDateInTz(date, tz = APP_TIMEZONE) {
  return new Intl.DateTimeFormat('en-CA', {
    timeZone: tz,
    year: 'numeric',
    month: '2-digit',
    day: '2-digit',
  }).format(date)
}

export function getHourMinuteInTz(date, tz = APP_TIMEZONE) {
  const parts = new Intl.DateTimeFormat('en-GB', {
    timeZone: tz,
    hour: '2-digit',
    minute: '2-digit',
    hour12: false,
  }).formatToParts(date)
  const pick = (type) => Number(parts.find((p) => p.type === type)?.value ?? 0)
  return { hour: pick('hour'), minute: pick('minute') }
}

export function isWeekdayInTz(date, tz = APP_TIMEZONE) {
  const w = new Intl.DateTimeFormat('en-US', { timeZone: tz, weekday: 'short' }).format(date)
  return w !== 'Sat' && w !== 'Sun'
}

/**
 * Próximos días hábiles (lun–vie) como YYYY-MM-DD.
 * Si ya pasó la hora de cierre del día (≥ 18:00 en la zona), **no incluye hoy**.
 */
export function upcomingWeekdayDateStrings(count = 8, tz = APP_TIMEZONE) {
  const out = []
  const now = new Date()
  const todayIsoInTz = formatDateInTz(now, tz)
  const { hour, minute } = getHourMinuteInTz(now, tz)
  const todayIsWeekday = isWeekdayInTz(now, tz)
  const afterBookingDay =
    todayIsWeekday &&
    (hour > BOOKING_DAY_END_HOUR || (hour === BOOKING_DAY_END_HOUR && minute >= 0))

  const start = new Date()
  start.setHours(12, 0, 0, 0)

  for (let i = 0; i < 90 && out.length < count; i++) {
    const cur = addDays(start, i)
    if (!isWeekdayInTz(cur, tz)) continue
    const iso = formatDateInTz(cur, tz)
    if (iso === todayIsoInTz && afterBookingDay) continue
    out.push(iso)
  }
  return out
}

function formatTimeLabel(isoTime) {
  if (!isoTime) return ''
  const part = String(isoTime).slice(0, 5)
  const [h, m] = part.split(':').map(Number)
  const dt = new Date()
  dt.setHours(h, m, 0, 0)
  return dt.toLocaleTimeString('es-PE', { hour: '2-digit', minute: '2-digit' })
}

export function formatDayLabel(dateIso) {
  const d = new Date(`${dateIso}T12:00:00`)
  return d.toLocaleDateString('es-PE', { weekday: 'short', day: 'numeric', month: 'short' })
}

const SHIFT_LABELS = {
  morning: 'mañana (8:00–13:00)',
  afternoon: 'tarde (14:00–18:00)',
}

/**
 * Slots libres para un consultorio y turno concretos (misma API que agendar cita).
 */
export async function fetchAvailableSlotTimes(hospitalId, specialtyId, roomId, shift, dateIso) {
  const { data } = await apiClient.get(API_CONFIG.ENDPOINTS.SLOTS.AVAILABLE, {
    params: {
      hospital_id: hospitalId,
      specialty_id: specialtyId,
      date: dateIso,
      shift,
      room_id: roomId,
    },
  })
  const raw = data?.slots ?? []
  const items = []
  const seen = new Set()
  for (const s of raw) {
    if (!s.available) continue
    const key = String(s.start_time).slice(0, 5)
    if (seen.has(key)) continue
    seen.add(key)
    items.push({
      startTime: String(s.start_time),
      label: formatTimeLabel(s.start_time),
      key,
    })
  }
  items.sort((a, b) => a.startTime.localeCompare(b.startTime))
  return items
}

export function buildBookingSuggestionPhrase({
  hospitalName,
  specialtyName,
  roomName,
  shift,
  dateIso,
  timeKey,
}) {
  const day = formatDayLabel(dateIso)
  const [hh, mm] = timeKey.split(':')
  const t = new Date()
  t.setHours(Number(hh), Number(mm), 0, 0)
  const timeStr = t.toLocaleTimeString('es-PE', { hour: '2-digit', minute: '2-digit' })
  const shiftStr = SHIFT_LABELS[shift] || shift
  return (
    `Quiero agendar una cita en ${hospitalName || 'el hospital'}, ` +
    `especialidad ${specialtyName || '—'}, ` +
    `consultorio ${roomName || '—'}, ` +
    `turno ${shiftStr}, ` +
    `el ${day} (${dateIso}) a las ${timeStr}`
  )
}
