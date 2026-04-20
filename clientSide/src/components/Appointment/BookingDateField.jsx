import { useState, useRef, useEffect, useLayoutEffect, useCallback } from 'react'
import { createPortal } from 'react-dom'
import { CalendarDays, ChevronLeft, ChevronRight } from 'lucide-react'
import {
  format,
  startOfMonth,
  endOfMonth,
  eachDayOfInterval,
  isSameMonth,
  isSameDay,
  addMonths,
  subMonths,
  startOfWeek,
  endOfWeek,
  isBefore,
  startOfDay,
} from 'date-fns'
import { es } from 'date-fns/locale'
import { toast } from 'sonner'
import { formatDate, isWeekend } from '@/utils/dateUtils'
import { isHoliday as getHolidayInfo } from '@/config/holidays'

const GAP_PX = 8
const VIEWPORT_MARGIN = 8
/** Altura inicial estimada antes de medir el DOM (evita salto fuerte) */
const ESTIMATED_POPOVER_H = 340

function clamp(n, min, max) {
  return Math.max(min, Math.min(max, n))
}

/**
 * Selector de fecha tipo “card” + calendario en popover (portal + posición fija).
 * Scroll al abrir, flip arriba/abajo según espacio, sin recortes por overflow del padre.
 *
 * @param {boolean} [unrestricted=false] - Sin bloqueo de fines de semana, festivos ni “solo futuro” (p. ej. filtros).
 * @param {Date} [minSelectableDate] - Límite inferior opcional (inclusive).
 * @param {Date} [maxSelectableDate] - Límite superior opcional (inclusive).
 * @param {string} [label]
 * @param {string|null} [helperText] - Texto bajo el campo; `null` lo oculta.
 * @param {string} [emptyHint] - Texto cuando no hay fecha (modo unrestricted).
 * @param {string} [className] - Clases del contenedor (p. ej. `max-w-full`).
 * @param {'default' | 'filter'} [variant] - `filter`: más compacto, una sola línea, altura fija (p. ej. barras de filtro).
 */
export default function BookingDateField({
  selectedDate,
  onSelectDate,
  id = 'booking-date',
  unrestricted = false,
  minSelectableDate,
  maxSelectableDate,
  label = 'Día de la cita',
  helperText,
  emptyHint,
  className = 'max-w-md',
  variant = 'default',
}) {
  const isFilter = variant === 'filter'
  const [open, setOpen] = useState(false)
  const [popoverStyle, setPopoverStyle] = useState(null)
  const [placement, setPlacement] = useState('below')
  const [currentMonth, setCurrentMonth] = useState(() =>
    selectedDate ? startOfMonth(selectedDate) : startOfMonth(new Date())
  )

  const triggerRef = useRef(null)
  const popoverRef = useRef(null)

  const isOutOfOptionalRange = useCallback(
    (d) => {
      const day = startOfDay(d)
      if (minSelectableDate && isBefore(day, startOfDay(minSelectableDate))) return true
      if (maxSelectableDate && isBefore(startOfDay(maxSelectableDate), day)) return true
      return false
    },
    [minSelectableDate, maxSelectableDate]
  )

  const isDateDisabled = useCallback(
    (date) => {
      const d = startOfDay(date)
      if (isOutOfOptionalRange(d)) return true
      if (unrestricted) return false
      return isBefore(d, startOfDay(new Date()))
    },
    [unrestricted, isOutOfOptionalRange]
  )

  const updatePopoverPosition = useCallback(() => {
    const trigger = triggerRef.current
    const pop = popoverRef.current
    if (!trigger || !pop) return

    const rect = trigger.getBoundingClientRect()
    const measured = pop.offsetHeight
    const popH = measured > 80 ? measured : ESTIMATED_POPOVER_H
    const vw = window.innerWidth
    const vh = window.innerHeight

    const width = rect.width
    const left = clamp(rect.left, VIEWPORT_MARGIN, vw - width - VIEWPORT_MARGIN)

    const spaceBelow = vh - rect.bottom - GAP_PX - VIEWPORT_MARGIN
    const spaceAbove = rect.top - GAP_PX - VIEWPORT_MARGIN

    let nextTop
    let nextPlacement = 'below'
    if (spaceBelow >= popH || spaceBelow >= spaceAbove) {
      nextTop = rect.bottom + GAP_PX
      nextPlacement = 'below'
    } else {
      nextTop = rect.top - popH - GAP_PX
      nextPlacement = 'above'
    }

    nextTop = clamp(nextTop, VIEWPORT_MARGIN, vh - popH - VIEWPORT_MARGIN)

    setPlacement(nextPlacement)
    setPopoverStyle({
      position: 'fixed',
      top: nextTop,
      left,
      width,
      maxWidth: 'min(100vw - 16px, 24rem)',
      zIndex: 100,
    })
  }, [])

  useEffect(() => {
    if (open && selectedDate) {
      setCurrentMonth(startOfMonth(selectedDate))
    }
  }, [open, selectedDate])

  useLayoutEffect(() => {
    if (!open) {
      setPopoverStyle(null)
      return
    }

    const trigger = triggerRef.current
    if (trigger) {
      trigger.scrollIntoView({
        block: 'nearest',
        behavior: 'auto',
        inline: 'nearest',
      })
    }

    const raf = requestAnimationFrame(() => {
      requestAnimationFrame(() => {
        updatePopoverPosition()
      })
    })

    const onWin = () => updatePopoverPosition()
    window.addEventListener('resize', onWin)
    window.addEventListener('scroll', onWin, true)

    let resizeObs = null
    const pop = popoverRef.current
    if (pop && typeof ResizeObserver !== 'undefined') {
      resizeObs = new ResizeObserver(() => {
        updatePopoverPosition()
      })
      resizeObs.observe(pop)
    }

    return () => {
      cancelAnimationFrame(raf)
      window.removeEventListener('resize', onWin)
      window.removeEventListener('scroll', onWin, true)
      resizeObs?.disconnect()
    }
  }, [open, updatePopoverPosition, currentMonth])

  useEffect(() => {
    if (!open) return
    const onDoc = (e) => {
      const t = triggerRef.current
      const p = popoverRef.current
      if (t?.contains(e.target) || p?.contains(e.target)) return
      setOpen(false)
    }
    const onKey = (e) => {
      if (e.key === 'Escape') setOpen(false)
    }
    document.addEventListener('mousedown', onDoc)
    document.addEventListener('keydown', onKey)
    return () => {
      document.removeEventListener('mousedown', onDoc)
      document.removeEventListener('keydown', onKey)
    }
  }, [open])

  const monthStart = startOfMonth(currentMonth)
  const monthEnd = endOfMonth(currentMonth)
  const calendarStart = startOfWeek(monthStart, { locale: es })
  const calendarEnd = endOfWeek(monthEnd, { locale: es })
  const days = eachDayOfInterval({ start: calendarStart, end: calendarEnd }).map((d) => startOfDay(d))

  const trySelect = useCallback(
    (date) => {
      const day = startOfDay(date)
      if (isDateDisabled(day)) {
        if (!unrestricted) {
          toast.error('No puedes elegir una fecha pasada')
        }
        return
      }
      if (!unrestricted) {
        if (isWeekend(day)) return
        const hol = getHolidayInfo(day)
        if (hol) {
          toast.error(`Ese día es festivo (${hol.name}). Elige otra fecha.`)
          return
        }
      }
      onSelectDate(day)
      setOpen(false)
    },
    [onSelectDate, unrestricted, isDateDisabled]
  )

  const handleDayClick = (day) => {
    if (!isSameMonth(day, currentMonth)) return
    if (unrestricted) {
      if (isDateDisabled(day)) return
      trySelect(day)
      return
    }
    if (isDateDisabled(day) || isWeekend(day) || getHolidayInfo(day)) return
    trySelect(day)
  }

  const display = selectedDate ? formatDate(selectedDate, 'dd/MM/yyyy') : null

  const popoverContent = open && (
    <div
      ref={popoverRef}
      id={`${id}-popover`}
      role="dialog"
      aria-modal="true"
      aria-label="Elegir fecha"
      style={
        popoverStyle ?? {
          position: 'fixed',
          left: -9999,
          top: 0,
          visibility: 'hidden',
          pointerEvents: 'none',
        }
      }
      className={[
        'overflow-hidden rounded-2xl border border-gray-200/90 bg-white shadow-xl shadow-gray-900/15 ring-1 ring-black/5',
        'max-h-[min(420px,calc(100vh-16px))] overflow-y-auto',
        popoverStyle ? 'pointer-events-auto opacity-100' : 'opacity-0',
      ].join(' ')}
      data-placement={placement}
    >
      <div className="sticky top-0 z-10 border-b border-gray-100 bg-gradient-to-r from-primary-50/90 to-white px-3 py-2.5">
        <div className="flex items-center justify-between gap-2">
          <button
            type="button"
            onClick={() => setCurrentMonth((m) => subMonths(m, 1))}
            className="rounded-lg p-1.5 text-gray-600 transition-colors hover:bg-white hover:text-primary-700"
            aria-label="Mes anterior"
          >
            <ChevronLeft className="h-4 w-4" />
          </button>
          <h3 className="min-w-0 flex-1 text-center text-sm font-bold capitalize text-gray-900">
            {format(currentMonth, 'MMMM yyyy', { locale: es })}
          </h3>
          <button
            type="button"
            onClick={() => setCurrentMonth((m) => addMonths(m, 1))}
            className="rounded-lg p-1.5 text-gray-600 transition-colors hover:bg-white hover:text-primary-700"
            aria-label="Mes siguiente"
          >
            <ChevronRight className="h-4 w-4" />
          </button>
        </div>
      </div>

      <div className="p-3">
        <div className="mb-1.5 grid grid-cols-7 gap-0.5">
          {['Lun', 'Mar', 'Mié', 'Jue', 'Vie', 'Sáb', 'Dom'].map((d) => (
            <div key={d} className="py-1 text-center text-[10px] font-semibold uppercase tracking-wide text-gray-400">
              {d}
            </div>
          ))}
        </div>
        <div className="grid grid-cols-7 gap-1">
          {days.map((day, index) => {
            const inMonth = isSameMonth(day, currentMonth)
            if (!inMonth) {
              return <div key={index} className="aspect-square max-h-9" aria-hidden />
            }

            const normalizedDay = startOfDay(day)
            const normalizedSelected = selectedDate ? startOfDay(selectedDate) : null
            const isSelected = normalizedSelected && isSameDay(normalizedDay, normalizedSelected)
            const disabledPast = isDateDisabled(day)
            const weekend = isWeekend(day)
            const holidayMeta = getHolidayInfo(day)
            const blocked = unrestricted
              ? disabledPast
              : disabledPast || weekend || holidayMeta
            const selectable = !blocked

            let cellClass =
              'aspect-square max-h-9 w-full rounded-lg text-xs font-medium transition-colors flex items-center justify-center '

            if (unrestricted) {
              if (disabledPast) {
                cellClass += 'cursor-not-allowed text-gray-300'
              } else if (isSelected) {
                cellClass +=
                  'bg-primary-600 text-white shadow-md ring-2 ring-primary-300 ring-offset-1 hover:bg-primary-700'
              } else {
                cellClass +=
                  'cursor-pointer bg-white text-gray-900 hover:bg-primary-50 hover:text-primary-900 border border-transparent hover:border-primary-200'
              }
            } else if (weekend) {
              cellClass += 'cursor-not-allowed bg-gray-100 text-gray-400 line-through decoration-gray-300'
            } else if (holidayMeta) {
              cellClass += 'cursor-not-allowed bg-red-50 text-red-400'
            } else if (disabledPast) {
              cellClass += 'cursor-not-allowed text-gray-300'
            } else if (isSelected) {
              cellClass +=
                'bg-primary-600 text-white shadow-md ring-2 ring-primary-300 ring-offset-1 hover:bg-primary-700'
            } else {
              cellClass +=
                'cursor-pointer bg-white text-gray-900 hover:bg-primary-50 hover:text-primary-900 border border-transparent hover:border-primary-200'
            }

            return (
              <button
                key={index}
                type="button"
                disabled={!selectable}
                title={
                  unrestricted
                    ? undefined
                    : holidayMeta
                      ? holidayMeta.name
                      : weekend
                        ? 'Fin de semana'
                        : undefined
                }
                onClick={() => handleDayClick(day)}
                className={cellClass}
              >
                {format(day, 'd')}
              </button>
            )
          })}
        </div>
      </div>
    </div>
  )

  const defaultHelper =
    helperText === undefined
      ? unrestricted
        ? null
        : 'Solo días hábiles disponibles (lun–vie). Festivos bloqueados.'
      : helperText

  const subtitleSelected = unrestricted ? 'Fecha seleccionada' : 'Día hábil seleccionado'
  const emptyLabel = emptyHint ?? (unrestricted ? 'Elegir fecha' : 'Elegir fecha disponible')

  const triggerClasses = isFilter
    ? 'flex h-[52px] w-full items-center justify-between gap-2 rounded-xl border-2 border-slate-200 bg-white px-2.5 text-left shadow-sm transition-all hover:border-primary-300 hover:shadow-md focus:outline-none focus-visible:ring-2 focus-visible:ring-primary-500 focus-visible:ring-offset-2'
    : 'flex min-h-[48px] w-full items-center justify-between gap-3 rounded-2xl border-2 border-gray-200 bg-white px-3 py-2.5 text-left shadow-sm transition-all hover:border-primary-300 hover:shadow-md focus:outline-none focus-visible:ring-2 focus-visible:ring-primary-500 focus-visible:ring-offset-2'

  const iconWrapClasses = isFilter
    ? 'flex h-9 w-9 shrink-0 items-center justify-center rounded-lg bg-gradient-to-br from-primary-100 to-cyan-50 text-primary-700 ring-1 ring-primary-200/60'
    : 'flex h-10 w-10 shrink-0 items-center justify-center rounded-xl bg-gradient-to-br from-primary-100 to-cyan-50 text-primary-700 ring-1 ring-primary-200/60'

  const iconSize = isFilter ? 'h-4 w-4' : 'h-5 w-5'

  return (
    <div className={`relative w-full ${className}`}>
      <label
        htmlFor={`${id}-trigger`}
        className={`mb-1.5 block min-h-[1.125rem] text-xs font-semibold uppercase tracking-wide ${
          isFilter ? 'text-slate-500' : 'text-gray-500'
        }`}
      >
        {label}
      </label>

      <button
        ref={triggerRef}
        id={`${id}-trigger`}
        type="button"
        aria-expanded={open}
        aria-haspopup="dialog"
        aria-controls={`${id}-popover`}
        onClick={() => setOpen((v) => !v)}
        className={triggerClasses}
      >
        <span className={`flex min-w-0 items-center ${isFilter ? 'gap-2' : 'gap-3'}`}>
          <span className={iconWrapClasses}>
            <CalendarDays className={iconSize} aria-hidden />
          </span>
          <span className="min-w-0 flex-1 overflow-hidden text-left">
            {display ? (
              <>
                <span
                  className={`block font-bold tabular-nums tracking-tight text-gray-900 ${
                    isFilter ? 'truncate text-base leading-tight' : 'text-lg'
                  }`}
                >
                  {display}
                </span>
                {!isFilter ? (
                  <span className="block text-xs text-gray-500">{subtitleSelected}</span>
                ) : null}
              </>
            ) : (
              <span
                className={`font-medium text-gray-500 ${isFilter ? 'truncate text-sm leading-tight' : 'text-base'}`}
              >
                {emptyLabel}
              </span>
            )}
          </span>
        </span>
        <span
          className={`shrink-0 rounded-lg bg-primary-50 font-semibold text-primary-800 ring-1 ring-primary-100 ${
            isFilter ? 'px-2 py-1.5 text-[10px] uppercase tracking-wide' : 'px-2.5 py-1.5 text-xs'
          }`}
        >
          {open ? 'Cerrar' : display ? 'Cambiar' : 'Calendario'}
        </span>
      </button>

      {defaultHelper ? (
        <p className="mt-1.5 text-[11px] text-gray-500">{defaultHelper}</p>
      ) : null}

      {typeof document !== 'undefined' && popoverContent && createPortal(popoverContent, document.body)}
    </div>
  )
}
