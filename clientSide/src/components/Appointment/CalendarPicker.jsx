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
const CalendarPicker = ({ selectedDate, onSelectDate, minDate = new Date() }) => {
  const [currentMonth, setCurrentMonth] = useState(new Date())

  const monthStart = startOfMonth(currentMonth)
  const monthEnd = endOfMonth(currentMonth)
  const calendarStart = startOfWeek(monthStart, { locale: es })
  const calendarEnd = endOfWeek(monthEnd, { locale: es })

  // Normalize all days to start of day in local timezone
  const days = eachDayOfInterval({ start: calendarStart, end: calendarEnd }).map(day => startOfDay(day))

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
      // Normalize date to start of day in local timezone to avoid timezone issues
      const normalizedDate = startOfDay(date)
      onSelectDate(normalizedDate)
    }
  }

  return (
    <div className="bg-white rounded-lg border border-gray-200 p-3 max-w-md mx-auto">
      {/* Header */}
      <div className="flex items-center justify-between mb-3">
        <button
          type="button"
          onClick={goToPreviousMonth}
          className="p-1.5 hover:bg-gray-100 rounded-lg transition-colors"
        >
          <ChevronLeft className="w-4 h-4" />
        </button>
        
        <h3 className="text-base font-semibold capitalize">
          {format(currentMonth, 'MMMM yyyy', { locale: es })}
        </h3>
        
        <button
          type="button"
          onClick={goToNextMonth}
          className="p-1.5 hover:bg-gray-100 rounded-lg transition-colors"
        >
          <ChevronRight className="w-4 h-4" />
        </button>
      </div>

      {/* Weekday headers */}
      <div className="grid grid-cols-7 gap-0.5 mb-1.5">
        {['Lun', 'Mar', 'Mié', 'Jue', 'Vie', 'Sáb', 'Dom'].map((day) => (
          <div
            key={day}
            className="text-center text-xs font-medium text-gray-500 py-1"
          >
            {day}
          </div>
        ))}
      </div>

      {/* Calendar days */}
      <div className="grid grid-cols-7 gap-0.5">
        {days.map((day, index) => {
          const normalizedDay = startOfDay(day)
          const normalizedSelectedDate = selectedDate ? startOfDay(selectedDate) : null
          const normalizedToday = startOfDay(new Date())
          
          const isCurrentMonth = isSameMonth(day, currentMonth)
          const isSelected = normalizedSelectedDate && isSameDay(normalizedDay, normalizedSelectedDate)
          const isDisabled = isDateDisabled(day) || isWeekend(day) || isDateHoliday(day)
          const isToday = isSameDay(normalizedDay, normalizedToday)
          const holidayInfo = isDateHoliday(day) ? isHoliday(day) : null

          return (
            <button
              key={index}
              type="button"
              onClick={() => handleDateClick(day)}
              disabled={isDisabled || !isCurrentMonth}
              title={holidayInfo ? holidayInfo.name : ''}
              className={`
                aspect-square p-1 text-xs rounded-md transition-colors relative
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
                <div className="absolute bottom-0.5 left-1/2 transform -translate-x-1/2 w-1 h-1 bg-red-500 rounded-full"></div>
              )}
            </button>
          )
        })}
      </div>

      {/* Legend */}
      <div className="mt-3 pt-3 border-t border-gray-200 text-xs text-gray-500 space-y-0.5">
        <p>• Fines de semana deshabilitados</p>
        <p>• Solo fechas futuras disponibles</p>
        <p>• <span className="text-red-400">●</span> Días festivos bloqueados (hover para ver nombre)</p>
      </div>
    </div>
  )
}

export default CalendarPicker

