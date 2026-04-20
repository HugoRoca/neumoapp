import { useState, useEffect, useMemo } from 'react'
import Card from '@/components/UI/Card'
import LoadingSpinner from '@/components/UI/LoadingSpinner'
import BookingDateField from '@/components/Appointment/BookingDateField'
import { useAppointments } from '@/hooks/useAppointments'
import { formatDate, formatTime, parseDateFromAPI, formatDateForAPI } from '@/utils/dateUtils'
import { APPOINTMENT_STATUS, APPOINTMENT_STATUS_LABELS, APPOINTMENT_STATUS_COLORS } from '@/config/constants'
import {
  Calendar,
  Clock,
  MapPin,
  FileText,
  AlertCircle,
  Search,
  ChevronLeft,
  ChevronRight,
  Filter,
  ChevronDown,
} from 'lucide-react'

const PAGE_SIZE = 12

const STATUS_OPTIONS = [
  { value: '', label: 'Todos los estados' },
  { value: APPOINTMENT_STATUS.PENDING, label: APPOINTMENT_STATUS_LABELS[APPOINTMENT_STATUS.PENDING] },
  { value: APPOINTMENT_STATUS.CONFIRMED, label: APPOINTMENT_STATUS_LABELS[APPOINTMENT_STATUS.CONFIRMED] },
  { value: APPOINTMENT_STATUS.RESCHEDULED, label: APPOINTMENT_STATUS_LABELS[APPOINTMENT_STATUS.RESCHEDULED] },
  { value: APPOINTMENT_STATUS.COMPLETED, label: APPOINTMENT_STATUS_LABELS[APPOINTMENT_STATUS.COMPLETED] },
  { value: APPOINTMENT_STATUS.CANCELLED, label: APPOINTMENT_STATUS_LABELS[APPOINTMENT_STATUS.CANCELLED] },
]

/**
 * Mis citas: filtros (estado, fechas, búsqueda) y paginación.
 */
const MyAppointments = () => {
  const [page, setPage] = useState(0)
  const [statusFilter, setStatusFilter] = useState('')
  const [dateFrom, setDateFrom] = useState('')
  const [dateTo, setDateTo] = useState('')
  const [searchInput, setSearchInput] = useState('')
  const [debouncedSearch, setDebouncedSearch] = useState('')

  useEffect(() => {
    const t = window.setTimeout(() => setDebouncedSearch(searchInput.trim()), 400)
    return () => window.clearTimeout(t)
  }, [searchInput])

  useEffect(() => {
    setPage(0)
  }, [statusFilter, dateFrom, dateTo, debouncedSearch])

  useEffect(() => {
    if (dateFrom && dateTo && dateTo < dateFrom) {
      setDateTo('')
    }
  }, [dateFrom, dateTo])

  const queryParams = useMemo(
    () => ({
      skip: page * PAGE_SIZE,
      limit: PAGE_SIZE,
      status: statusFilter || undefined,
      date_from: dateFrom || undefined,
      date_to: dateTo || undefined,
      search: debouncedSearch || undefined,
    }),
    [page, statusFilter, dateFrom, dateTo, debouncedSearch]
  )

  const { appointments, total, loading, error, fetching } = useAppointments(queryParams)

  const totalPages = Math.max(1, Math.ceil(total / PAGE_SIZE) || 1)
  const rangeFrom = total === 0 ? 0 : page * PAGE_SIZE + 1
  const rangeTo = Math.min((page + 1) * PAGE_SIZE, total)
  const canPrev = page > 0
  const canNext = (page + 1) * PAGE_SIZE < total

  const clearFilters = () => {
    setStatusFilter('')
    setDateFrom('')
    setDateTo('')
    setSearchInput('')
    setDebouncedSearch('')
    setPage(0)
  }

  const hasActiveFilters = Boolean(statusFilter || dateFrom || dateTo || debouncedSearch)

  const renderContent = () => {
    if (loading) {
      return <LoadingSpinner message="Cargando tus citas..." />
    }

    if (error) {
      return (
        <Card>
          <div className="py-8 text-center sm:py-12">
            <AlertCircle className="mx-auto mb-4 h-12 w-12 text-red-500 sm:h-16 sm:w-16" />
            <h3 className="mb-2 text-base font-semibold text-gray-900 sm:text-lg">Error al cargar las citas</h3>
            <p className="text-sm text-gray-600 sm:text-base">{error}</p>
          </div>
        </Card>
      )
    }

    if (!loading && total === 0) {
      return (
        <Card>
          <div className="py-8 text-center sm:py-12">
            <Calendar className="mx-auto mb-4 h-12 w-12 text-gray-400 sm:h-16 sm:w-16" />
            <h3 className="mb-2 text-base font-semibold text-gray-900 sm:text-lg">No hay citas con estos criterios</h3>
            <p className="text-sm text-gray-600 sm:text-base">
              Prueba a cambiar los filtros o busca por otra especialidad o fecha.
            </p>
          </div>
        </Card>
      )
    }

    return (
      <>
        <div className="grid gap-4 sm:gap-5 md:grid-cols-2 xl:grid-cols-3">
          {appointments.map((appointment) => (
            <Card
              key={appointment.id}
              className="transition-shadow duration-200 hover:shadow-md"
            >
              <div className="space-y-3">
                <div className="flex items-start justify-between gap-2">
                  <h3 className="text-base font-semibold leading-tight text-gray-900 sm:text-lg">
                    {appointment.specialty_name}
                  </h3>
                  <span
                    className={`flex-shrink-0 whitespace-nowrap rounded-full px-2 py-1 text-xs font-medium ${APPOINTMENT_STATUS_COLORS[appointment.status]}`}
                  >
                    {APPOINTMENT_STATUS_LABELS[appointment.status] || appointment.status}
                  </span>
                </div>

                <div className="flex items-center text-xs text-gray-600 sm:text-sm">
                  <Calendar className="mr-2 h-4 w-4 flex-shrink-0" />
                  <span>{formatDate(appointment.appointment_date)}</span>
                </div>

                <div className="flex items-center text-xs text-gray-600 sm:text-sm">
                  <Clock className="mr-2 h-4 w-4 flex-shrink-0" />
                  <span>
                    {formatTime(appointment.start_time)} - {formatTime(appointment.end_time)}
                  </span>
                </div>

                <div className="flex items-start text-xs text-gray-600 sm:text-sm">
                  <MapPin className="mr-2 mt-0.5 h-4 w-4 flex-shrink-0" />
                  <div className="min-w-0 flex-1">
                    <p className="truncate font-medium">{appointment.consultation_room_name}</p>
                    <p className="text-xs text-gray-500">{appointment.consultation_room_number}</p>
                  </div>
                </div>

                {appointment.reason && (
                  <div className="flex items-start border-t border-gray-100 pt-2 text-xs text-gray-600 sm:text-sm">
                    <FileText className="mr-2 mt-0.5 h-4 w-4 flex-shrink-0" />
                    <p className="line-clamp-2 text-xs">{appointment.reason}</p>
                  </div>
                )}
              </div>
            </Card>
          ))}
        </div>

        {total > 0 && (
          <div className="mt-8 flex flex-col items-center justify-between gap-4 border-t border-slate-200/90 pt-6 sm:flex-row">
            <p className="text-sm text-slate-600">
              Mostrando{' '}
              <span className="font-medium text-slate-900">
                {rangeFrom}–{rangeTo}
              </span>{' '}
              de <span className="font-medium text-slate-900">{total}</span> citas
            </p>
            <div className="flex items-center gap-2">
              <button
                type="button"
                onClick={() => setPage((p) => Math.max(0, p - 1))}
                disabled={!canPrev}
                className="inline-flex items-center gap-1 rounded-full border border-slate-200 bg-white px-3 py-2 text-sm font-medium text-slate-700 shadow-sm transition hover:bg-slate-50 disabled:cursor-not-allowed disabled:opacity-40"
              >
                <ChevronLeft className="h-4 w-4" aria-hidden />
                Anterior
              </button>
              <span className="min-w-[5rem] text-center text-sm text-slate-600">
                Página {page + 1} / {totalPages}
              </span>
              <button
                type="button"
                onClick={() => setPage((p) => p + 1)}
                disabled={!canNext}
                className="inline-flex items-center gap-1 rounded-full border border-slate-200 bg-white px-3 py-2 text-sm font-medium text-slate-700 shadow-sm transition hover:bg-slate-50 disabled:cursor-not-allowed disabled:opacity-40"
              >
                Siguiente
                <ChevronRight className="h-4 w-4" aria-hidden />
              </button>
            </div>
          </div>
        )}
      </>
    )
  }

  return (
    <div className="px-4 py-6 sm:px-6 lg:px-8 lg:py-8">
      <div className="mb-6 sm:mb-8">
        <h1 className="text-2xl font-bold text-slate-900 sm:text-3xl">Mis Citas</h1>
        <p className="mt-2 text-sm text-slate-600 sm:text-base">Historial de tus citas médicas</p>
      </div>

      <Card className="mb-6 overflow-visible shadow-sm">
        <div className="border-b border-slate-100 px-4 py-3 sm:px-5">
          <div className="flex flex-wrap items-center gap-2">
            <Filter className="h-4 w-4 text-primary-600" aria-hidden />
            <h2 className="text-sm font-semibold text-slate-900">Filtros y búsqueda</h2>
          </div>
        </div>
        <div className="space-y-5 p-4 sm:p-5">
          <div className="relative">
            <Search className="pointer-events-none absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-slate-400" aria-hidden />
            <input
              type="search"
              value={searchInput}
              onChange={(e) => setSearchInput(e.target.value)}
              placeholder="Buscar por especialidad, consultorio o motivo…"
              className="h-11 w-full rounded-xl border border-slate-200 bg-white py-2 pl-10 pr-4 text-sm text-slate-900 shadow-sm placeholder:text-slate-400 focus:border-primary-500 focus:outline-none focus:ring-2 focus:ring-primary-500/20"
              autoComplete="off"
            />
          </div>

          <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-12 lg:items-start lg:gap-x-3 lg:gap-y-0">
            <div className="flex min-w-0 flex-col sm:col-span-2 lg:col-span-4">
              <span className="mb-1.5 block min-h-[1.125rem] text-xs font-semibold uppercase tracking-wide text-slate-500">
                Estado de la cita
              </span>
              <div className="relative">
                <select
                  value={statusFilter}
                  onChange={(e) => setStatusFilter(e.target.value)}
                  aria-label="Filtrar por estado"
                  className="h-[52px] w-full cursor-pointer appearance-none rounded-xl border-2 border-slate-200 bg-gradient-to-b from-white to-slate-50/90 pl-4 pr-11 text-sm font-semibold text-slate-800 shadow-sm ring-1 ring-slate-100 transition hover:border-primary-300 hover:shadow-md focus:border-primary-500 focus:outline-none focus:ring-2 focus:ring-primary-500/25"
                >
                  {STATUS_OPTIONS.map((o) => (
                    <option key={o.value || 'all'} value={o.value}>
                      {o.label}
                    </option>
                  ))}
                </select>
                <ChevronDown
                  className="pointer-events-none absolute right-3 top-1/2 h-5 w-5 -translate-y-1/2 text-primary-600"
                  aria-hidden
                />
              </div>
            </div>

            <div className="min-w-0 lg:col-span-4">
              <BookingDateField
                id="my-appts-date-from"
                label="Desde"
                variant="filter"
                className="max-w-full"
                selectedDate={dateFrom ? parseDateFromAPI(dateFrom) : null}
                onSelectDate={(d) => setDateFrom(formatDateForAPI(d))}
                unrestricted
                helperText={null}
                emptyHint="Cualquier día"
              />
            </div>

            <div className="min-w-0 lg:col-span-3">
              <BookingDateField
                id="my-appts-date-to"
                label="Hasta"
                variant="filter"
                className="max-w-full"
                selectedDate={dateTo ? parseDateFromAPI(dateTo) : null}
                onSelectDate={(d) => setDateTo(formatDateForAPI(d))}
                unrestricted
                helperText={null}
                emptyHint="Cualquier día"
                minSelectableDate={dateFrom ? parseDateFromAPI(dateFrom) : undefined}
              />
            </div>

            <div className="flex min-w-0 flex-col sm:col-span-2 lg:col-span-1">
              <span className="mb-1.5 block min-h-[1.125rem] w-full select-none text-[0] leading-none opacity-0" aria-hidden>
                &nbsp;
              </span>
              <button
                type="button"
                onClick={clearFilters}
                disabled={!hasActiveFilters}
                className="flex h-[52px] w-full items-center justify-center rounded-xl border-2 border-primary-200/90 bg-gradient-to-b from-primary-50 to-primary-100/80 px-2 text-sm font-semibold text-primary-900 shadow-sm transition hover:border-primary-400 hover:from-primary-100 hover:to-primary-50 disabled:cursor-not-allowed disabled:opacity-40"
              >
                Limpiar
              </button>
            </div>
          </div>
        </div>
      </Card>

      {fetching && !loading ? (
        <p className="mb-4 text-center text-xs text-slate-500">Actualizando resultados…</p>
      ) : null}

      {renderContent()}
    </div>
  )
}

export default MyAppointments
