import { useState } from 'react'
import { ChevronLeft, ChevronRight } from 'lucide-react'
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
  startOfDay
} from 'date-fns'
import { es } from 'date-fns/locale'
import { isHoliday } from '@/config/holidays'

/**
 * Calendar Picker Component
 * Allows selecting a date from a calendar view
 * Blocks weekends, past dates, and holidays
 * 
 * @param {Date} selectedDate - Currently selected date
 * @param {Function} onSelectDate - Callback when date is selected
 * @param {Date} minDate - Minimum selectable date
 */
// eslint-disable-next-line react/prop-types
const CalendarPicker = ({ selectedDate, onSelectDate, minDate = new Date() }) => {
  const [currentMonth, setCurrentMonth] = useState(new Date())

  const monthStart = startOfMonth(currentMonth)
  const monthEnd = endOfMonth(currentMonth)
  const calendarStart = startOfWeek(monthStart, { locale: es })
  const calendarEnd = endOfWeek(monthEnd, { locale: es })

  const days = eachDayOfInterval({ start: calendarStart, end: calendarEnd })

  const goToPreviousMonth = () => {
    setCurrentMonth(subMonths(currentMonth, 1))
  }

  const goToNextMonth = () => {
    setCurrentMonth(addMonths(currentMonth, 1))
  }

  const isDateDisabled = (date) => {
    // Disable dates before minDate
    return isBefore(startOfDay(date), startOfDay(minDate))
  }

  const isWeekend = (date) => {
    const day = date.getDay()
    return day === 0 || day === 6 // Sunday = 0, Saturday = 6
  }

  const isDateHoliday = (date) => {
    return isHoliday(date) !== null
  }

  const handleDateClick = (date) => {
    if (!isDateDisabled(date) && !isWeekend(date) && !isDateHoliday(date) && isSameMonth(date, currentMonth)) {
      onSelectDate(date)
    }
  }

  return (
    <div className="bg-white rounded-lg border border-gray-200 p-4">
      {/* Header */}
      <div className="flex items-center justify-between mb-4">
        <button
          type="button"
          onClick={goToPreviousMonth}
          className="p-2 hover:bg-gray-100 rounded-lg transition-colors"
        >
          <ChevronLeft className="w-5 h-5" />
        </button>
        
        <h3 className="text-lg font-semibold capitalize">
          {format(currentMonth, 'MMMM yyyy', { locale: es })}
        </h3>
        
        <button
          type="button"
          onClick={goToNextMonth}
          className="p-2 hover:bg-gray-100 rounded-lg transition-colors"
        >
          <ChevronRight className="w-5 h-5" />
        </button>
      </div>

      {/* Weekday headers */}
      <div className="grid grid-cols-7 gap-1 mb-2">
        {['Lun', 'Mar', 'Mié', 'Jue', 'Vie', 'Sáb', 'Dom'].map((day) => (
          <div
            key={day}
            className="text-center text-xs font-medium text-gray-500 py-2"
          >
            {day}
          </div>
        ))}
      </div>

      {/* Calendar days */}
      <div className="grid grid-cols-7 gap-1">
        {days.map((day, index) => {
          const isCurrentMonth = isSameMonth(day, currentMonth)
          const isSelected = selectedDate && isSameDay(day, selectedDate)
          const isDisabled = isDateDisabled(day) || isWeekend(day) || isDateHoliday(day)
          const isToday = isSameDay(day, new Date())
          const holidayInfo = isDateHoliday(day) ? isHoliday(day) : null

          return (
            <button
              key={index}
              type="button"
              onClick={() => handleDateClick(day)}
              disabled={isDisabled || !isCurrentMonth}
              title={holidayInfo ? holidayInfo.name : ''}
              className={`
                aspect-square p-2 text-sm rounded-lg transition-colors relative
                ${!isCurrentMonth ? 'text-gray-300' : ''}
                ${isSelected ? 'bg-primary-600 text-white font-semibold hover:bg-primary-700' : ''}
                ${!isSelected && isToday && isCurrentMonth ? 'bg-primary-50 text-primary-600 font-semibold' : ''}
                ${!isSelected && !isToday && !isDisabled && isCurrentMonth ? 'hover:bg-gray-100 text-gray-900' : ''}
                ${isDisabled && isCurrentMonth ? 'text-gray-300 cursor-not-allowed' : ''}
                ${!isDisabled && isCurrentMonth ? 'cursor-pointer' : ''}
                ${holidayInfo && isCurrentMonth ? 'bg-red-50 text-red-400' : ''}
              `}
            >
              {format(day, 'd')}
              {holidayInfo && isCurrentMonth && (
                <div className="absolute bottom-0 left-1/2 transform -translate-x-1/2 w-1 h-1 bg-red-500 rounded-full"></div>
              )}
            </button>
          )
        })}
      </div>

      {/* Legend */}
      <div className="mt-4 pt-4 border-t border-gray-200 text-xs text-gray-500 space-y-1">
        <p>• Fines de semana deshabilitados</p>
        <p>• Solo fechas futuras disponibles</p>
        <p>• <span className="text-red-400">●</span> Días festivos bloqueados (hover para ver nombre)</p>
      </div>
    </div>
  )
}

export default CalendarPicker

