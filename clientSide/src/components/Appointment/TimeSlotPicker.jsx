import { Clock, CheckCircle2 } from 'lucide-react'
import { formatTime } from '@/utils/dateUtils'

/**
 * @param {'default' | 'chips'} variant - chips: botones compactos estilo píldora
 */
const TimeSlotPicker = ({
  slots,
  selectedSlot,
  onSelectSlot,
  loading,
  variant = 'default',
  /** Para etiquetar el bloque cuando el API devuelve un solo turno */
  shiftLabel = '',
}) => {
  if (loading) {
    return (
      <div className="py-6 text-center">
        <div className="mx-auto h-8 w-8 animate-spin rounded-full border-b-2 border-primary-600" />
        <p className="mt-2 text-sm text-gray-600">Cargando horarios...</p>
      </div>
    )
  }

  if (!slots || slots.length === 0) {
    return (
      <div className="py-6 text-center">
        <Clock className="mx-auto mb-2 h-10 w-10 text-gray-300" />
        <p className="text-sm text-gray-600">No hay horarios disponibles</p>
      </div>
    )
  }

  const availableSlots = slots.filter((slot) => slot.available)

  if (availableSlots.length === 0) {
    return (
      <div className="py-6 text-center">
        <Clock className="mx-auto mb-2 h-10 w-10 text-gray-300" />
        <p className="text-sm text-gray-600">No hay horarios libres para esta fecha</p>
        <p className="mt-1 text-xs text-gray-500">Prueba con otro día</p>
      </div>
    )
  }

  if (variant === 'chips') {
    return (
      <div>
        <div className="mb-3 flex flex-wrap items-end justify-between gap-2">
          <div>
            <h4 className="text-sm font-semibold text-gray-900">Horarios disponibles</h4>
            {shiftLabel ? <p className="text-xs text-gray-500">{shiftLabel}</p> : null}
          </div>
          <span className="rounded-full bg-primary-50 px-2 py-0.5 text-xs font-medium text-primary-700 ring-1 ring-primary-100">
            {availableSlots.length} opciones
          </span>
        </div>
        <div
          className="grid grid-cols-2 gap-2 sm:grid-cols-3 md:grid-cols-4"
          role="listbox"
          aria-label="Horarios disponibles"
        >
          {availableSlots.map((slot, index) => {
            const isSelected =
              selectedSlot &&
              selectedSlot.start_time === slot.start_time &&
              selectedSlot.consultation_room.id === slot.consultation_room.id

            return (
              <button
                key={`${slot.start_time}-${slot.consultation_room?.id ?? index}`}
                type="button"
                role="option"
                aria-selected={isSelected}
                onClick={() => onSelectSlot(slot)}
                className={[
                  'flex h-12 w-full min-w-0 items-center justify-center gap-1.5 rounded-xl border-2 text-sm font-semibold transition-all',
                  'focus:outline-none focus-visible:ring-2 focus-visible:ring-primary-500 focus-visible:ring-offset-2',
                  isSelected
                    ? 'border-primary-500 bg-primary-500 text-white shadow-md ring-1 ring-primary-300'
                    : 'border-gray-200 bg-white text-gray-900 hover:border-primary-300 hover:bg-primary-50',
                ].join(' ')}
              >
                <Clock className={`h-4 w-4 shrink-0 ${isSelected ? 'text-white' : 'text-primary-600'}`} aria-hidden />
                <span className="tabular-nums">{formatTime(slot.start_time)}</span>
                {isSelected ? <CheckCircle2 className="h-4 w-4 shrink-0 text-white" aria-hidden /> : null}
              </button>
            )
          })}
        </div>
      </div>
    )
  }

  return (
    <div>
      <div className="mb-3 flex items-center justify-between">
        <h4 className="text-sm font-medium text-gray-700">
          Horarios disponibles ({availableSlots.length})
        </h4>
      </div>

      <div className="custom-scrollbar grid max-h-96 grid-cols-2 gap-2 overflow-y-auto sm:grid-cols-3 lg:grid-cols-4">
        {slots.map((slot, index) => {
          const isSelected =
            selectedSlot &&
            selectedSlot.start_time === slot.start_time &&
            selectedSlot.consultation_room.id === slot.consultation_room.id

          return (
            <button
              key={index}
              type="button"
              onClick={() => slot.available && onSelectSlot(slot)}
              disabled={!slot.available}
              className={`
                relative rounded-lg border-2 p-3 text-left transition-all
                ${!slot.available ? 'cursor-not-allowed border-gray-200 bg-gray-50 opacity-50' : ''}
                ${slot.available && !isSelected ? 'cursor-pointer border-gray-200 hover:border-primary-300 hover:bg-primary-50' : ''}
                ${isSelected ? 'border-primary-500 bg-primary-50' : ''}
              `}
            >
              <div className="flex items-start justify-between">
                <div className="flex-1">
                  <div className="mb-1 flex items-center space-x-1">
                    <Clock className="h-3 w-3 text-gray-500" />
                    <span className="text-sm font-semibold text-gray-900">{formatTime(slot.start_time)}</span>
                  </div>
                  <p className="text-xs text-gray-500">
                    {formatTime(slot.start_time)} - {formatTime(slot.end_time)}
                  </p>
                </div>
                {isSelected && <CheckCircle2 className="h-5 w-5 flex-shrink-0 text-primary-600" />}
              </div>

              {!slot.available && (
                <div className="mt-2">
                  <span className="text-xs font-medium text-red-600">No disponible</span>
                </div>
              )}
            </button>
          )
        })}
      </div>
    </div>
  )
}

export default TimeSlotPicker
