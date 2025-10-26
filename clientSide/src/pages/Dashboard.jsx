import { useAuth } from '@/context/AuthContext'
import { useUpcomingAppointments } from '@/hooks/useUpcomingAppointments'
import MainLayout from '@/components/Layout/MainLayout'
import Card from '@/components/UI/Card'
import LoadingSpinner from '@/components/UI/LoadingSpinner'
import { Calendar, Clock, User, MapPin, AlertCircle } from 'lucide-react'
import { formatDate, formatTime } from '@/utils/dateUtils'
import { APPOINTMENT_STATUS_LABELS, APPOINTMENT_STATUS_COLORS } from '@/config/constants'

/**
 * Dashboard Page
 * Shows user's upcoming appointments
 */
const Dashboard = () => {
  const { user } = useAuth()
  const { appointments, loading, error } = useUpcomingAppointments(5)

  return (
    <MainLayout>
      <div className="px-4 sm:px-6 lg:px-8 py-6 sm:py-8">
        {/* Header */}
        <div className="mb-6 sm:mb-8">
          <h1 className="text-2xl sm:text-3xl font-bold text-gray-900">
            Bienvenido, {user?.firstname}
          </h1>
          <p className="text-gray-600 mt-2 text-sm sm:text-base">
            Tus próximas citas médicas agendadas
          </p>
        </div>

        {/* Loading State */}
        {loading && <LoadingSpinner message="Cargando tus citas..." />}

        {/* Error State */}
        {error && (
          <Card className="max-w-2xl mx-auto">
            <div className="flex items-center space-x-3 text-red-600">
              <AlertCircle className="w-6 h-6 flex-shrink-0" />
              <div>
                <p className="font-semibold">Error al cargar las citas</p>
                <p className="text-sm text-gray-600">{error}</p>
              </div>
            </div>
          </Card>
        )}

        {/* Empty State */}
        {!loading && !error && appointments.length === 0 && (
          <Card className="max-w-2xl mx-auto">
            <div className="text-center py-8 sm:py-12">
              <Calendar className="w-12 h-12 sm:w-16 sm:h-16 text-gray-400 mx-auto mb-4" />
              <h3 className="text-base sm:text-lg font-semibold text-gray-900 mb-2">
                No tienes citas próximas
              </h3>
              <p className="text-sm sm:text-base text-gray-600">
                Agenda tu próxima cita médica desde el menú
              </p>
            </div>
          </Card>
        )}

        {/* Appointments List */}
        {!loading && !error && appointments.length > 0 && (
          <div className="space-y-4 sm:space-y-5 max-w-4xl mx-auto">
            <div className="flex items-center justify-between mb-4">
              <h2 className="text-lg sm:text-xl font-semibold text-gray-900">
                Próximas {appointments.length} cita{appointments.length !== 1 ? 's' : ''}
              </h2>
            </div>

            {appointments.map((appointment, index) => (
              <Card 
                key={appointment.id} 
                className={`hover:shadow-lg transition-shadow ${index === 0 ? 'border-2 border-primary-200' : ''}`}
              >
                {index === 0 && (
                  <div className="mb-3 sm:mb-4">
                    <span className="inline-block px-3 py-1 bg-primary-100 text-primary-800 text-xs font-semibold rounded-full">
                      Próxima Cita
                    </span>
                  </div>
                )}
                
                <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                  {/* Left Column */}
                  <div className="space-y-3">
                    {/* Specialty */}
                    <div className="flex items-start space-x-3">
                      <User className="w-5 h-5 text-primary-600 mt-1 flex-shrink-0" />
                      <div className="min-w-0 flex-1">
                        <p className="text-xs text-gray-500">Especialidad</p>
                        <p className="font-semibold text-sm sm:text-base text-gray-900">
                          {appointment.specialty?.name || 'N/A'}
                        </p>
                        {appointment.specialty?.description && (
                          <p className="text-xs text-gray-500 mt-1">
                            {appointment.specialty.description}
                          </p>
                        )}
                      </div>
                    </div>

                    {/* Date */}
                    <div className="flex items-start space-x-3">
                      <Calendar className="w-5 h-5 text-primary-600 mt-1 flex-shrink-0" />
                      <div className="min-w-0 flex-1">
                        <p className="text-xs text-gray-500">Fecha</p>
                        <p className="font-semibold text-sm sm:text-base">
                          {formatDate(appointment.appointment_date)}
                        </p>
                      </div>
                    </div>

                    {/* Time */}
                    <div className="flex items-start space-x-3">
                      <Clock className="w-5 h-5 text-primary-600 mt-1 flex-shrink-0" />
                      <div className="min-w-0 flex-1">
                        <p className="text-xs text-gray-500">Hora</p>
                        <p className="font-semibold text-sm sm:text-base">
                          {formatTime(appointment.start_time)} - {formatTime(appointment.end_time)}
                        </p>
                        <p className="text-xs text-gray-500 capitalize">
                          Turno: {appointment.shift === 'morning' ? 'Mañana' : 'Tarde'}
                        </p>
                      </div>
                    </div>
                  </div>

                  {/* Right Column */}
                  <div className="space-y-3 sm:border-l sm:pl-4">
                    {/* Consultation Room */}
                    <div className="flex items-start space-x-3">
                      <MapPin className="w-5 h-5 text-primary-600 mt-1 flex-shrink-0" />
                      <div className="min-w-0 flex-1">
                        <p className="text-xs text-gray-500">Consultorio</p>
                        <p className="font-semibold text-sm sm:text-base">
                          {appointment.consultation_room?.name || 'N/A'}
                        </p>
                        <p className="text-xs text-gray-500">
                          {appointment.consultation_room?.room_number || 'N/A'}
                        </p>
                      </div>
                    </div>

                    {/* Status */}
                    <div className="flex items-start space-x-3">
                      <div className="w-5 h-5 mt-1 flex-shrink-0" />
                      <div className="min-w-0 flex-1">
                        <p className="text-xs text-gray-500">Estado</p>
                        <span className={`inline-block px-2 sm:px-3 py-1 rounded-full text-xs sm:text-sm font-medium ${APPOINTMENT_STATUS_COLORS[appointment.status]}`}>
                          {APPOINTMENT_STATUS_LABELS[appointment.status] || appointment.status}
                        </span>
                      </div>
                    </div>

                    {/* Reason */}
                    {appointment.reason && (
                      <div className="flex items-start space-x-3">
                        <div className="w-5 h-5 mt-1 flex-shrink-0" />
                        <div className="min-w-0 flex-1">
                          <p className="text-xs text-gray-500">Motivo</p>
                          <p className="text-sm text-gray-800 line-clamp-2">
                            {appointment.reason}
                          </p>
                        </div>
                      </div>
                    )}
                  </div>
                </div>

                {/* Observations */}
                {appointment.observations && (
                  <div className="mt-4 pt-4 border-t border-gray-100">
                    <p className="text-xs text-gray-500 mb-1">Observaciones</p>
                    <p className="text-sm text-gray-700">{appointment.observations}</p>
                  </div>
                )}
              </Card>
            ))}
          </div>
        )}
      </div>
    </MainLayout>
  )
}

export default Dashboard

