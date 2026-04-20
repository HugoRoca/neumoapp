import { useState, useEffect } from 'react'
import { Link, useNavigate, useOutletContext } from 'react-router-dom'
import { useAuth } from '@/context/AuthContext'
import { useUpcomingAppointments } from '@/hooks/useUpcomingAppointments'
import Card from '@/components/UI/Card'
import LoadingSpinner from '@/components/UI/LoadingSpinner'
import Button from '@/components/UI/Button'
import {
  Calendar,
  Clock,
  User,
  MapPin,
  AlertCircle,
  X,
  RefreshCw,
  Building2,
  List,
  MessageCircle,
  Sparkles,
  FileText,
} from 'lucide-react'
import { formatDate, formatTime } from '@/utils/dateUtils'
import { APPOINTMENT_STATUS_LABELS, APPOINTMENT_STATUS_COLORS } from '@/config/constants'
import appointmentService from '@/services/appointment.service'
import { toast } from 'sonner'
import hospitalService from '@/services/hospital.service'
import FeaturedCarousel from '@/components/Dashboard/FeaturedCarousel'

function QuickAccess() {
  const items = [
    {
      to: '/agendar-cita',
      icon: Calendar,
      title: 'Agendar cita',
      description: 'Consultorio, turno y horario',
    },
    {
      to: '/mis-citas',
      icon: List,
      title: 'Mis citas',
      description: 'Lista y gestión',
    },
    {
      to: '/asistente',
      icon: MessageCircle,
      title: 'Asistente',
      description: 'Ayuda para reservar',
      highlight: true,
    },
    {
      soon: true,
      icon: FileText,
      title: 'Documentos',
      description: 'Informes y resultados',
    },
  ]

  return (
    <section aria-labelledby="quick-heading">
      <h2 id="quick-heading" className="mb-4 text-lg font-semibold tracking-tight text-slate-900 sm:text-xl">
        Accesos rápidos
      </h2>
      <div className="grid grid-cols-2 gap-3 sm:gap-4 lg:grid-cols-4">
        {items.map((item) => {
          const Icon = item.icon
          if (item.soon) {
            return (
              <div
                key={item.title}
                role="group"
                aria-disabled="true"
                aria-label={`${item.title}: no disponible aún`}
                className="flex cursor-not-allowed flex-col items-start rounded-2xl border border-slate-200/90 bg-white p-4 opacity-50 shadow-sm grayscale sm:p-5"
              >
                <span className="flex h-10 w-10 items-center justify-center rounded-xl bg-slate-100 text-slate-600">
                  <Icon className="h-5 w-5" aria-hidden />
                </span>
                <span className="mt-3 text-sm font-semibold text-slate-900">{item.title}</span>
                <span className="mt-1 text-xs text-slate-500">{item.description}</span>
                <span className="mt-2 rounded-full bg-slate-100 px-2 py-0.5 text-[10px] font-semibold uppercase tracking-wide text-slate-500">
                  Próximamente
                </span>
              </div>
            )
          }
          return (
            <Link
              key={item.to}
              to={item.to}
              className={`group flex flex-col items-start rounded-2xl border border-slate-200/90 bg-white p-4 shadow-sm transition-shadow duration-200 hover:border-primary-200 hover:shadow-md sm:p-5 ${
                item.highlight ? 'ring-1 ring-primary-100' : ''
              }`}
            >
              <span
                className={`flex h-10 w-10 items-center justify-center rounded-xl ${
                  item.highlight
                    ? 'bg-gradient-to-br from-primary-500 to-sky-600 text-white shadow-md shadow-primary-500/25'
                    : 'bg-primary-50 text-primary-700'
                }`}
              >
                {item.highlight ? (
                  <Sparkles className="h-5 w-5" aria-hidden />
                ) : (
                  <Icon className="h-5 w-5" aria-hidden />
                )}
              </span>
              <span className="mt-3 text-sm font-semibold text-slate-900">{item.title}</span>
              <span className="mt-1 text-xs text-slate-500">{item.description}</span>
            </Link>
          )
        })}
      </div>
    </section>
  )
}

/**
 * Dashboard / Inicio — carrusel, accesos rápidos y lista de próximas citas.
 */
const Dashboard = () => {
  const navigate = useNavigate()
  const { openUserProfile } = useOutletContext() || {}
  const { user } = useAuth()
  const { appointments, loading, error, refetch } = useUpcomingAppointments(5)
  const [cancellingId, setCancellingId] = useState(null)
  const [contextHospitalName, setContextHospitalName] = useState(null)

  const firstName = user?.firstname || user?.first_name || 'Usuario'
  const displayName = [user?.firstname || user?.first_name, user?.lastname || user?.last_name]
    .filter(Boolean)
    .join(' ')

  useEffect(() => {
    let cancelled = false
    hospitalService
      .getHospitals(0, 5)
      .then((data) => {
        if (cancelled || !Array.isArray(data) || data.length === 0) return
        setContextHospitalName(data[0]?.name ?? null)
      })
      .catch(() => {
        setContextHospitalName(null)
      })
    return () => {
      cancelled = true
    }
  }, [])

  const handleCancel = async (appointmentId) => {
    if (!window.confirm('¿Estás seguro de que deseas cancelar esta cita?')) {
      return
    }

    try {
      setCancellingId(appointmentId)
      await appointmentService.cancelAppointment(appointmentId)
      toast.success('Cita cancelada exitosamente')
      refetch()
    } catch (err) {
      toast.error(err.response?.data?.detail || 'Error al cancelar la cita')
    } finally {
      setCancellingId(null)
    }
  }

  const handleReschedule = (appointment) => {
    navigate(`/agendar-cita?reschedule=${appointment.id}`)
  }

  return (
    <div className="mx-auto min-h-full w-full max-w-6xl px-4 py-8 sm:px-6 lg:px-8 lg:py-10">
      <header className="mb-8 flex flex-col gap-4 sm:flex-row sm:items-start sm:justify-between">
        <div>
          <h1 className="text-3xl font-bold tracking-tight text-slate-900 sm:text-4xl">¡Hola, {firstName}!</h1>
          <p className="mt-1 text-slate-600">Aquí tienes un resumen de tu actividad y tus próximas citas.</p>
        </div>
        <button
          type="button"
          onClick={() => openUserProfile?.()}
          className="hidden items-center gap-2.5 self-start rounded-full border-2 border-slate-900/10 bg-white px-4 py-2.5 text-left shadow-sm ring-1 ring-slate-100 transition hover:border-primary-200 hover:ring-primary-100 lg:inline-flex"
          aria-label="Ver mi cuenta"
        >
          <span className="flex h-9 w-9 items-center justify-center rounded-full bg-slate-100 text-slate-600">
            <User className="h-4 w-4" aria-hidden />
          </span>
          <span className="max-w-[12rem] truncate text-sm font-semibold text-slate-800 lg:max-w-xs">
            {displayName || firstName}
          </span>
        </button>
      </header>

      {contextHospitalName && (
        <div className="mb-8 flex items-start gap-3 rounded-2xl border border-primary-100 bg-gradient-to-r from-primary-50/95 to-cyan-50/50 px-4 py-3 text-sm text-primary-950 shadow-sm">
          <Building2 className="mt-0.5 h-5 w-5 shrink-0 text-primary-600" aria-hidden />
          <div>
            <p className="text-xs font-semibold uppercase tracking-wide text-primary-700/90">Centro asignado</p>
            <p className="font-semibold text-slate-900">{contextHospitalName}</p>
          </div>
        </div>
      )}

      <div className="space-y-8 lg:space-y-10">
        <FeaturedCarousel />
        <QuickAccess />

        {loading && (
          <div className="rounded-2xl border border-slate-200/90 bg-white p-8 shadow-sm">
            <LoadingSpinner message="Cargando tus citas…" />
          </div>
        )}

        {error && (
          <Card className="border-red-100 bg-red-50/50">
            <div className="flex items-start gap-3 text-red-700">
              <AlertCircle className="mt-0.5 h-6 w-6 shrink-0" aria-hidden />
              <div>
                <p className="font-semibold">Error al cargar las citas</p>
                <p className="text-sm text-red-600/90">{error}</p>
              </div>
            </div>
          </Card>
        )}

        {!loading && !error && appointments.length === 0 && (
          <section aria-labelledby="empty-appointments-heading">
            <h2 id="empty-appointments-heading" className="sr-only">
              Sin citas próximas
            </h2>
            <Card className="overflow-hidden rounded-2xl border-slate-200/90 shadow-sm">
              <div className="flex flex-col items-center px-6 py-10 text-center sm:py-12">
                <div className="mb-4 flex h-16 w-16 items-center justify-center rounded-2xl bg-primary-50 ring-1 ring-primary-100 sm:h-20 sm:w-20">
                  <Calendar className="h-8 w-8 text-primary-500 sm:h-10 sm:w-10" aria-hidden />
                </div>
                <p className="text-base font-semibold text-slate-900">No cuentas con citas por el momento</p>
                <p className="mt-2 max-w-md text-sm text-slate-600">
                  Agenda una visita cuando la necesites; elige consultorio y horario en pocos pasos.
                </p>
                <Link
                  to="/agendar-cita"
                  className="mt-6 inline-flex items-center justify-center rounded-full bg-primary-600 px-6 py-3 text-sm font-semibold text-white shadow-md shadow-primary-600/20 transition hover:bg-primary-700"
                >
                  Agendar cita
                </Link>
              </div>
            </Card>
          </section>
        )}

        {!loading && !error && appointments.length > 0 && (
        <section className="border-t border-slate-200/80 pt-8 lg:pt-10">
          <h2 className="mb-6 text-xl font-semibold text-slate-900">
            Próximas citas
            <span className="ml-2 text-base font-normal text-slate-500">
              ({appointments.length})
            </span>
          </h2>
          <div className="space-y-5">
            {appointments.map((appointment, index) => (
              <Card
                key={appointment.id}
                className={`overflow-hidden rounded-2xl border-slate-200/90 shadow-sm transition-shadow hover:shadow-md ${
                  index === 0 ? 'border-2 border-primary-200 ring-1 ring-primary-100' : ''
                }`}
              >
                {index === 0 && (
                  <div className="border-b border-slate-100 bg-primary-50/50 px-5 py-2">
                    <span className="text-xs font-semibold uppercase tracking-wide text-primary-800">
                      Más próxima
                    </span>
                  </div>
                )}

                <div className="p-5 sm:p-6">
                  <div className="grid grid-cols-1 gap-6 sm:grid-cols-2">
                    <div className="space-y-4">
                      <div className="flex items-start gap-3">
                        <User className="mt-0.5 h-5 w-5 shrink-0 text-primary-600" />
                        <div className="min-w-0">
                          <p className="text-xs text-slate-500">Especialidad</p>
                          <p className="font-semibold text-slate-900">{appointment.specialty?.name || 'N/A'}</p>
                          {appointment.specialty?.description && (
                            <p className="mt-1 text-xs text-slate-500">{appointment.specialty.description}</p>
                          )}
                        </div>
                      </div>
                      <div className="flex items-start gap-3">
                        <Calendar className="mt-0.5 h-5 w-5 shrink-0 text-primary-600" />
                        <div>
                          <p className="text-xs text-slate-500">Fecha</p>
                          <p className="font-semibold text-slate-900">{formatDate(appointment.appointment_date)}</p>
                        </div>
                      </div>
                      <div className="flex items-start gap-3">
                        <Clock className="mt-0.5 h-5 w-5 shrink-0 text-primary-600" />
                        <div>
                          <p className="text-xs text-slate-500">Hora</p>
                          <p className="font-semibold text-slate-900">
                            {formatTime(appointment.start_time)} - {formatTime(appointment.end_time)}
                          </p>
                          <p className="text-xs capitalize text-slate-500">
                            Turno: {appointment.shift === 'morning' ? 'Mañana' : 'Tarde'}
                          </p>
                        </div>
                      </div>
                    </div>

                    <div className="space-y-4 sm:border-l sm:border-slate-100 sm:pl-6">
                      <div className="flex items-start gap-3">
                        <MapPin className="mt-0.5 h-5 w-5 shrink-0 text-primary-600" />
                        <div>
                          <p className="text-xs text-slate-500">Consultorio</p>
                          <p className="font-semibold text-slate-900">{appointment.consultation_room?.name || 'N/A'}</p>
                          <p className="text-xs text-slate-500">{appointment.consultation_room?.room_number || ''}</p>
                        </div>
                      </div>
                      <div>
                        <p className="text-xs text-slate-500">Estado</p>
                        <span
                          className={`mt-1 inline-block rounded-full px-3 py-1 text-xs font-medium ${APPOINTMENT_STATUS_COLORS[appointment.status]}`}
                        >
                          {APPOINTMENT_STATUS_LABELS[appointment.status] || appointment.status}
                        </span>
                      </div>
                      {appointment.reason && (
                        <div>
                          <p className="text-xs text-slate-500">Motivo</p>
                          <p className="line-clamp-2 text-sm text-slate-800">{appointment.reason}</p>
                        </div>
                      )}
                    </div>
                  </div>

                  {appointment.observations && (
                    <div className="mt-5 border-t border-slate-100 pt-4">
                      <p className="text-xs text-slate-500">Observaciones</p>
                      <p className="text-sm text-slate-700">{appointment.observations}</p>
                    </div>
                  )}

                  <div className="mt-5 flex flex-col gap-2 border-t border-slate-100 pt-5 sm:flex-row sm:gap-3">
                    <Button
                      type="button"
                      variant="outline"
                      size="sm"
                      className="flex-1 rounded-full sm:flex-none"
                      onClick={() => handleReschedule(appointment)}
                    >
                      <RefreshCw className="mr-2 h-4 w-4" />
                      Reagendar
                    </Button>
                    <Button
                      type="button"
                      variant="danger"
                      size="sm"
                      className="flex-1 rounded-full sm:flex-none"
                      onClick={() => handleCancel(appointment.id)}
                      loading={cancellingId === appointment.id}
                      disabled={cancellingId === appointment.id || appointment.status === 'cancelled'}
                    >
                      <X className="mr-2 h-4 w-4" />
                      Anular
                    </Button>
                  </div>
                </div>
              </Card>
            ))}
          </div>
        </section>
        )}
      </div>
    </div>
  )
}

export default Dashboard
