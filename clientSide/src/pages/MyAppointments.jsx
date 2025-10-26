import MainLayout from '@/components/Layout/MainLayout'
import Card from '@/components/UI/Card'
import LoadingSpinner from '@/components/UI/LoadingSpinner'
import { useAppointments } from '@/hooks/useAppointments'
import { formatDate, formatTime } from '@/utils/dateUtils'
import { APPOINTMENT_STATUS_LABELS, APPOINTMENT_STATUS_COLORS } from '@/config/constants'
import { Calendar, Clock, MapPin, FileText } from 'lucide-react'

/**
 * My Appointments Page
 * Shows all user's appointments
 */
const MyAppointments = () => {
  const { appointments, loading } = useAppointments()

  return (
    <MainLayout>
      <div className="px-4 sm:px-6 lg:px-8 py-6 sm:py-8">
        <div className="mb-6 sm:mb-8">
          <h1 className="text-2xl sm:text-3xl font-bold text-gray-900">Mis Citas</h1>
          <p className="text-gray-600 mt-2 text-sm sm:text-base">
            Historial completo de tus citas médicas
          </p>
        </div>

        {loading ? (
          <LoadingSpinner message="Cargando tus citas..." />
        ) : appointments.length === 0 ? (
          <Card>
            <div className="text-center py-8 sm:py-12">
              <Calendar className="w-12 h-12 sm:w-16 sm:h-16 text-gray-400 mx-auto mb-4" />
              <h3 className="text-base sm:text-lg font-semibold text-gray-900 mb-2">
                No tienes citas registradas
              </h3>
              <p className="text-sm sm:text-base text-gray-600">
                Agenda tu primera cita desde el menú
              </p>
            </div>
          </Card>
        ) : (
          <div className="grid gap-4 sm:gap-5 md:grid-cols-2 xl:grid-cols-3">
            {appointments.map((appointment) => (
              <Card key={appointment.id} className="hover:shadow-lg transition-shadow">
                <div className="space-y-3">
                  <div className="flex justify-between items-start gap-2">
                    <h3 className="font-semibold text-base sm:text-lg text-gray-900 leading-tight">
                      {appointment.specialty?.name || appointment.specialty_name || 'N/A'}
                    </h3>
                    <span className={`px-2 py-1 rounded-full text-xs font-medium whitespace-nowrap flex-shrink-0 ${APPOINTMENT_STATUS_COLORS[appointment.status]}`}>
                      {APPOINTMENT_STATUS_LABELS[appointment.status] || appointment.status}
                    </span>
                  </div>

                  <div className="flex items-center text-xs sm:text-sm text-gray-600">
                    <Calendar className="w-4 h-4 mr-2 flex-shrink-0" />
                    <span>{formatDate(appointment.appointment_date)}</span>
                  </div>

                  <div className="flex items-center text-xs sm:text-sm text-gray-600">
                    <Clock className="w-4 h-4 mr-2 flex-shrink-0" />
                    <span>{formatTime(appointment.start_time)} - {formatTime(appointment.end_time)}</span>
                  </div>

                  <div className="flex items-start text-xs sm:text-sm text-gray-600">
                    <MapPin className="w-4 h-4 mr-2 mt-0.5 flex-shrink-0" />
                    <div className="min-w-0 flex-1">
                      <p className="font-medium truncate">
                        {appointment.consultation_room?.name || appointment.consultation_room_name || 'N/A'}
                      </p>
                      <p className="text-xs text-gray-500">
                        {appointment.consultation_room?.room_number || appointment.consultation_room_number || 'N/A'}
                      </p>
                    </div>
                  </div>

                  {appointment.reason && (
                    <div className="flex items-start text-xs sm:text-sm text-gray-600 pt-2 border-t border-gray-100">
                      <FileText className="w-4 h-4 mr-2 mt-0.5 flex-shrink-0" />
                      <p className="text-xs line-clamp-2">{appointment.reason}</p>
                    </div>
                  )}
                </div>
              </Card>
            ))}
          </div>
        )}
      </div>
    </MainLayout>
  )
}

export default MyAppointments

