import { Clock, CheckCircle2 } from 'lucide-react'
import { formatTime } from '@/utils/dateUtils'

/**
 * Time Slot Picker Component
 * Shows available time slots and allows selection
 */
const TimeSlotPicker = ({ slots, selectedSlot, onSelectSlot, loading }) => {
  if (loading) {
    return (
      <div className="text-center py-8">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary-600 mx-auto"></div>
        <p className="text-sm text-gray-600 mt-2">Cargando horarios...</p>
      </div>
    )
  }

  if (!slots || slots.length === 0) {
    return (
      <div className="text-center py-8">
        <Clock className="w-12 h-12 text-gray-300 mx-auto mb-3" />
        <p className="text-sm text-gray-600">No hay horarios disponibles</p>
      </div>
    )
  }

  const availableSlots = slots.filter(slot => slot.available)

  if (availableSlots.length === 0) {
    return (
      <div className="text-center py-8">
        <Clock className="w-12 h-12 text-gray-300 mx-auto mb-3" />
        <p className="text-sm text-gray-600">No hay horarios disponibles para esta fecha</p>
        <p className="text-xs text-gray-500 mt-1">Intenta con otra fecha</p>
      </div>
    )
  }

  return (
    <div>
      <div className="flex items-center justify-between mb-3">
        <h4 className="text-sm font-medium text-gray-700">
          Horarios Disponibles ({availableSlots.length})
        </h4>
      </div>

      <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-4 gap-2 max-h-96 overflow-y-auto custom-scrollbar">
        {slots.map((slot, index) => {
          const isSelected = selectedSlot && 
            selectedSlot.start_time === slot.start_time && 
            selectedSlot.consultation_room.id === slot.consultation_room.id
          
          return (
            <button
              key={index}
              type="button"
              onClick={() => slot.available && onSelectSlot(slot)}
              disabled={!slot.available}
              className={`
                relative p-3 rounded-lg border-2 transition-all text-left
                ${!slot.available ? 'border-gray-200 bg-gray-50 cursor-not-allowed opacity-50' : ''}
                ${slot.available && !isSelected ? 'border-gray-200 hover:border-primary-300 hover:bg-primary-50 cursor-pointer' : ''}
                ${isSelected ? 'border-primary-500 bg-primary-50' : ''}
              `}
            >
              <div className="flex items-start justify-between">
                <div className="flex-1">
                  <div className="flex items-center space-x-1 mb-1">
                    <Clock className="w-3 h-3 text-gray-500" />
                    <span className="text-sm font-semibold text-gray-900">
                      {formatTime(slot.start_time)}
                    </span>
                  </div>
                  <p className="text-xs text-gray-500">
                    {formatTime(slot.start_time)} - {formatTime(slot.end_time)}
                  </p>
                </div>
                {isSelected && (
                  <CheckCircle2 className="w-5 h-5 text-primary-600 flex-shrink-0" />
                )}
              </div>
              
              {!slot.available && (
                <div className="mt-2">
                  <span className="text-xs text-red-600 font-medium">No disponible</span>
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

