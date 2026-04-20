import { useState, useEffect, useRef } from 'react'
import { useNavigate, useSearchParams } from 'react-router-dom'
import Card from '@/components/UI/Card'
import Input from '@/components/UI/Input'
import Button from '@/components/UI/Button'
import LoadingSpinner from '@/components/UI/LoadingSpinner'
import ConfirmDialog from '@/components/UI/ConfirmDialog'
import TimeSlotPicker from '@/components/Appointment/TimeSlotPicker'
import BookingDateField from '@/components/Appointment/BookingDateField'
import RoomSelectionCarousel from '@/components/Appointment/RoomSelectionCarousel'
import ShiftToggleGroup from '@/components/Appointment/ShiftToggleGroup'
import { DoorOpen, Calendar, Clock, CheckCircle, AlertCircle, RefreshCw } from 'lucide-react'
import { toast } from 'sonner'
import hospitalService from '@/services/hospital.service'
import consultationRoomService from '@/services/consultationRoom.service'
import slotService from '@/services/slot.service'
import appointmentService from '@/services/appointment.service'
import { formatDateForAPI, formatDate, formatTime } from '@/utils/dateUtils'

/** Pasos visibles: consultorio → turno → fecha/hora → motivo (hospital y especialidad son fijos por API) */
const STEP = { room: 1, shift: 2, datetime: 3, reason: 4 }


/**
 * Flujo de agendamiento: centro y especialidad implícitos (primer resultado de la API).
 */
const BookAppointment = () => {
  const navigate = useNavigate()
  const [searchParams] = useSearchParams()
  const rescheduleAppointmentId = searchParams.get('reschedule')

  const [selectedHospital, setSelectedHospital] = useState('')
  const [selectedSpecialty, setSelectedSpecialty] = useState('')
  const [selectedRoom, setSelectedRoom] = useState('')
  const [selectedShift, setSelectedShift] = useState('')
  const [selectedDate, setSelectedDate] = useState(null)
  const [selectedSlot, setSelectedSlot] = useState(null)
  const [reason, setReason] = useState('')

  const [specialties, setSpecialties] = useState([])
  const [rooms, setRooms] = useState([])
  const [slots, setSlots] = useState([])

  const [originalAppointment, setOriginalAppointment] = useState(null)
  const [loadingOriginalAppointment, setLoadingOriginalAppointment] = useState(false)

  const [showConfirmDialog, setShowConfirmDialog] = useState(false)

  const [loadingHospitals, setLoadingHospitals] = useState(true)
  const [loadingSpecialties, setLoadingSpecialties] = useState(false)
  const [loadingRooms, setLoadingRooms] = useState(false)
  const [loadingSlots, setLoadingSlots] = useState(false)
  const [submitting, setSubmitting] = useState(false)

  const sectionShiftRef = useRef(null)
  const sectionDatetimeRef = useRef(null)
  const sectionTimeSlotsRef = useRef(null)
  const sectionReasonRef = useRef(null)

  useEffect(() => {
    if (!rescheduleAppointmentId) return
    const fetchOriginalAppointment = async () => {
      try {
        setLoadingOriginalAppointment(true)
        const appointment = await appointmentService.getAppointmentById(rescheduleAppointmentId)
        setOriginalAppointment(appointment)
        if (appointment.consultation_room?.hospital_id) {
          setSelectedHospital(appointment.consultation_room.hospital_id.toString())
        }
        if (appointment.specialty_id) {
          setSelectedSpecialty(appointment.specialty_id.toString())
        }
        if (appointment.reason) {
          setReason(appointment.reason)
        }
      } catch {
        toast.error('Error al cargar la cita original')
        navigate('/dashboard')
      } finally {
        setLoadingOriginalAppointment(false)
      }
    }
    fetchOriginalAppointment()
  }, [rescheduleAppointmentId, navigate])

  useEffect(() => {
    const fetchHospitals = async () => {
      try {
        setLoadingHospitals(true)
        const data = await hospitalService.getHospitals(0, 10)
        if (!Array.isArray(data) || data.length === 0) {
          toast.error('No hay centro médico disponible')
          return
        }
        if (!rescheduleAppointmentId) {
          setSelectedHospital(String(data[0].id))
        }
      } catch {
        toast.error('Error al cargar hospitales')
      } finally {
        setLoadingHospitals(false)
      }
    }
    fetchHospitals()
  }, [rescheduleAppointmentId])

  useEffect(() => {
    if (!selectedHospital) {
      setSpecialties([])
      return
    }
    const fetchSpecialties = async () => {
      try {
        setLoadingSpecialties(true)
        setSelectedSpecialty('')
        setSelectedRoom('')
        setSelectedShift('')
        setSelectedDate(null)
        setSelectedSlot(null)
        setSpecialties([])
        setRooms([])
        setSlots([])

        const data = await hospitalService.getHospitalSpecialties(selectedHospital)
        setSpecialties(data)
        if (Array.isArray(data) && data.length > 0) {
          setSelectedSpecialty(String(data[0].id))
        }
      } catch {
        toast.error('Error al cargar especialidades')
      } finally {
        setLoadingSpecialties(false)
      }
    }
    fetchSpecialties()
  }, [selectedHospital])

  useEffect(() => {
    if (!selectedHospital || !selectedSpecialty) {
      setRooms([])
      return
    }
    const fetchRooms = async () => {
      try {
        setLoadingRooms(true)
        setSelectedRoom('')
        setSelectedShift('')
        setSelectedDate(null)
        setSelectedSlot(null)
        setRooms([])
        setSlots([])

        const data = await consultationRoomService.getRoomsByHospitalAndSpecialty(
          selectedHospital,
          selectedSpecialty
        )
        setRooms(data)
      } catch {
        toast.error('Error al cargar consultorios')
      } finally {
        setLoadingRooms(false)
      }
    }
    fetchRooms()
  }, [selectedHospital, selectedSpecialty])

  useEffect(() => {
    if (!selectedHospital || !selectedSpecialty || !selectedRoom || !selectedDate || !selectedShift) {
      setSlots([])
      return
    }
    const fetchSlots = async () => {
      try {
        setLoadingSlots(true)
        setSelectedSlot(null)

        const data = await slotService.getAvailableSlots({
          hospital_id: selectedHospital,
          specialty_id: selectedSpecialty,
          date: formatDateForAPI(selectedDate),
          shift: selectedShift,
          room_id: selectedRoom,
        })

        setSlots(data.slots || [])
      } catch {
        toast.error('Error al cargar horarios disponibles')
        setSlots([])
      } finally {
        setLoadingSlots(false)
      }
    }
    fetchSlots()
  }, [selectedHospital, selectedSpecialty, selectedRoom, selectedDate, selectedShift])

  useEffect(() => {
    if (!selectedRoom) return
    let cancelled = false
    requestAnimationFrame(() => {
      requestAnimationFrame(() => {
        if (!cancelled) {
          sectionShiftRef.current?.scrollIntoView({ behavior: 'smooth', block: 'nearest', inline: 'nearest' })
        }
      })
    })
    return () => {
      cancelled = true
    }
  }, [selectedRoom])

  useEffect(() => {
    if (!selectedShift) return
    let cancelled = false
    requestAnimationFrame(() => {
      requestAnimationFrame(() => {
        if (!cancelled) {
          sectionDatetimeRef.current?.scrollIntoView({ behavior: 'smooth', block: 'nearest', inline: 'nearest' })
        }
      })
    })
    return () => {
      cancelled = true
    }
  }, [selectedShift])

  useEffect(() => {
    if (!selectedDate) return
    let cancelled = false
    requestAnimationFrame(() => {
      requestAnimationFrame(() => {
        if (!cancelled) {
          sectionTimeSlotsRef.current?.scrollIntoView({ behavior: 'smooth', block: 'nearest', inline: 'nearest' })
        }
      })
    })
    return () => {
      cancelled = true
    }
  }, [selectedDate])

  useEffect(() => {
    if (!selectedSlot) return
    let cancelled = false
    requestAnimationFrame(() => {
      requestAnimationFrame(() => {
        if (!cancelled) {
          sectionReasonRef.current?.scrollIntoView({ behavior: 'smooth', block: 'nearest', inline: 'nearest' })
        }
      })
    })
    return () => {
      cancelled = true
    }
  }, [selectedSlot])

  const handleSubmit = async (e) => {
    e.preventDefault()

    if (!selectedHospital || !selectedSpecialty || !selectedRoom || !selectedDate || !selectedShift || !selectedSlot) {
      toast.error('Por favor completa todos los campos')
      return
    }

    if (!reason.trim()) {
      toast.error('Por favor indica el motivo de la consulta')
      return
    }

    setShowConfirmDialog(true)
  }

  const handleConfirmSubmit = async () => {
    setShowConfirmDialog(false)

    try {
      setSubmitting(true)

      const newAppointment = await appointmentService.createAppointment({
        specialty_id: parseInt(selectedSpecialty, 10),
        consultation_room_id: selectedSlot.consultation_room.id,
        appointment_date: formatDateForAPI(selectedDate),
        start_time: selectedSlot.start_time,
        shift: selectedShift,
        reason: reason.trim(),
      })

      if (rescheduleAppointmentId && originalAppointment) {
        try {
          await appointmentService.updateAppointment(newAppointment.id, {
            status: 'rescheduled',
            observations: `Cita reprogramada. Cita original ID: ${rescheduleAppointmentId} fue eliminada.`,
          })
          await appointmentService.cancelAppointment(rescheduleAppointmentId)
          toast.success('¡Cita reprogramada exitosamente!')
        } catch (updateError) {
          console.error('Error updating/deleting appointments:', updateError)
          toast.warning('¡Nueva cita creada! (Nota: Error al procesar la cita anterior)')
        }
      } else {
        toast.success('¡Cita agendada exitosamente!')
      }

      navigate('/dashboard')
    } catch (error) {
      toast.error(error.response?.data?.detail || 'Error al agendar la cita')
    } finally {
      setSubmitting(false)
    }
  }

  const handleShiftChange = (next) => {
    setSelectedShift(next)
    setSelectedDate(null)
    setSelectedSlot(null)
  }

  const handleDateSelect = (date) => {
    setSelectedDate(date)
    setSelectedSlot(null)
  }

  const shiftTimeLabel =
    selectedShift === 'morning'
      ? 'Turno mañana · 8:00 – 13:00'
      : selectedShift === 'afternoon'
        ? 'Turno tarde · 14:00 – 18:00'
        : ''

  const isStepComplete = (n) => {
    switch (n) {
      case STEP.room:
        return !!selectedRoom
      case STEP.shift:
        return !!selectedShift
      case STEP.datetime:
        return !!selectedSlot
      case STEP.reason:
        return !!reason.trim()
      default:
        return false
    }
  }

  const specialtyName =
    specialties.find((s) => s.id === parseInt(selectedSpecialty, 10))?.name || ''

  const waitingForBookingContext =
    loadingHospitals ||
    (Boolean(rescheduleAppointmentId) && (loadingOriginalAppointment || !selectedHospital))

  return (
    <div className="px-3 py-6 sm:px-6 lg:px-8 sm:py-8">
      <div className="mb-6 sm:mb-8">
        <div className="mb-2 flex items-center space-x-3">
          {rescheduleAppointmentId && <RefreshCw className="h-6 w-6 text-primary-600" />}
          <h1 className="text-2xl font-bold text-gray-900 sm:text-3xl">
            {rescheduleAppointmentId ? 'Reagendar Cita' : 'Agendar Cita'}
          </h1>
        </div>
        <p className="mt-2 text-sm text-gray-600 sm:text-base">
          {rescheduleAppointmentId
            ? 'Selecciona la nueva fecha y horario para tu cita'
            : 'Consultorio → turno → fecha y hora. El centro y la especialidad están definidos para tu atención.'}
        </p>
      </div>

      {rescheduleAppointmentId && (
        <>
          {loadingOriginalAppointment ? (
            <Card className="mx-auto mb-6 max-w-4xl">
              <LoadingSpinner size="sm" message="Cargando información de la cita original..." />
            </Card>
          ) : originalAppointment ? (
            <Card className="mx-auto mb-6 max-w-4xl border-2 border-yellow-200 bg-yellow-50">
              <div className="flex items-start space-x-3">
                <AlertCircle className="mt-0.5 h-5 w-5 flex-shrink-0 text-yellow-600" />
                <div className="flex-1">
                  <h3 className="mb-2 text-sm font-semibold text-yellow-900">Estás reprogramando una cita existente</h3>
                  <div className="space-y-2 rounded-lg bg-white p-3 text-sm">
                    <div className="grid grid-cols-1 gap-2 sm:grid-cols-2">
                      <div>
                        <span className="text-gray-500">Especialidad:</span>{' '}
                        <span className="font-medium">{originalAppointment.specialty?.name || 'N/A'}</span>
                      </div>
                      <div>
                        <span className="text-gray-500">Fecha actual:</span>{' '}
                        <span className="font-medium">{formatDate(originalAppointment.appointment_date)}</span>
                      </div>
                      <div>
                        <span className="text-gray-500">Hora actual:</span>{' '}
                        <span className="font-medium">
                          {formatTime(originalAppointment.start_time)} - {formatTime(originalAppointment.end_time)}
                        </span>
                      </div>
                      <div>
                        <span className="text-gray-500">Consultorio:</span>{' '}
                        <span className="font-medium">{originalAppointment.consultation_room?.name || 'N/A'}</span>
                      </div>
                    </div>
                    <p className="border-t border-gray-100 pt-2 text-xs text-gray-600">
                      La cita original será cancelada y marcada como reprogramada una vez que confirmes la nueva cita.
                    </p>
                  </div>
                </div>
              </div>
            </Card>
          ) : null}
        </>
      )}

      {waitingForBookingContext ? (
        <LoadingSpinner
          message={rescheduleAppointmentId ? 'Cargando tu cita…' : 'Cargando...'}
        />
      ) : (
        <form onSubmit={handleSubmit} className="mx-auto max-w-4xl space-y-6">
          {selectedHospital && !selectedSpecialty && loadingSpecialties && (
            <Card>
              <LoadingSpinner size="sm" message="Preparando datos de tu cita..." />
            </Card>
          )}

          {selectedSpecialty && (
            <Card className="relative min-w-0" bodyClassName="px-3 py-4 sm:px-6 sm:py-4">
              <div className="grid grid-cols-[auto_1fr] gap-x-2.5 sm:grid-cols-[2.5rem_1fr] sm:gap-x-4">
                <div
                  className={`flex h-9 w-9 shrink-0 items-center justify-center rounded-full sm:h-10 sm:w-10 ${
                    isStepComplete(STEP.room) ? 'bg-green-100' : 'bg-primary-100'
                  }`}
                >
                  {isStepComplete(STEP.room) ? (
                    <CheckCircle className="h-5 w-5 text-green-600 sm:h-6 sm:w-6" />
                  ) : (
                    <DoorOpen className="h-5 w-5 text-primary-600 sm:h-6 sm:w-6" />
                  )}
                </div>
                <div className="min-w-0">
                  <h3 className="mb-3 text-lg font-semibold text-gray-900">
                    {STEP.room}. Elige el Consultorio
                  </h3>
                </div>
                <div className="col-span-2 min-w-0 sm:col-span-1 sm:col-start-2">
                  {loadingRooms ? (
                    <LoadingSpinner size="sm" message="Cargando consultorios..." />
                  ) : (
                    <RoomSelectionCarousel
                      rooms={rooms}
                      selectedRoom={selectedRoom}
                      onSelectRoom={setSelectedRoom}
                    />
                  )}
                </div>
              </div>
            </Card>
          )}

          {selectedRoom && (
            <section
              ref={sectionShiftRef}
              className="scroll-mt-4"
              aria-label="Paso: turno de atención"
            >
            <Card className="relative min-w-0" bodyClassName="px-3 py-4 sm:px-6 sm:py-4">
              <div className="grid grid-cols-[auto_1fr] gap-x-2.5 sm:grid-cols-[2.5rem_1fr] sm:gap-x-4">
                <div
                  className={`flex h-9 w-9 shrink-0 items-center justify-center rounded-full sm:h-10 sm:w-10 ${
                    isStepComplete(STEP.shift) ? 'bg-green-100' : 'bg-primary-100'
                  }`}
                >
                  {isStepComplete(STEP.shift) ? (
                    <CheckCircle className="h-5 w-5 text-green-600 sm:h-6 sm:w-6" />
                  ) : (
                    <Clock className="h-5 w-5 text-primary-600 sm:h-6 sm:w-6" />
                  )}
                </div>
                <div className="min-w-0">
                  <h3 className="mb-1 text-lg font-semibold text-gray-900">
                    {STEP.shift}. Elige el turno de atención
                  </h3>
                  <p className="mb-4 text-sm text-gray-500">
                    Elige mañana o tarde; después podrás indicar el día y la hora.
                  </p>
                </div>
                <div className="col-span-2 min-w-0 sm:col-span-1 sm:col-start-2">
                  <ShiftToggleGroup value={selectedShift} onChange={handleShiftChange} />
                </div>
              </div>
            </Card>
            </section>
          )}

          {selectedShift && (
            <section
              ref={sectionDatetimeRef}
              className="scroll-mt-4"
              aria-label="Paso: fecha y horario"
            >
            <Card className="relative min-w-0 !overflow-visible" bodyClassName="px-3 py-4 sm:px-6 sm:py-4">
              <div className="grid grid-cols-[auto_1fr] gap-x-2.5 sm:grid-cols-[2.5rem_1fr] sm:gap-x-4">
                <div
                  className={`flex h-9 w-9 shrink-0 items-center justify-center rounded-full sm:h-10 sm:w-10 ${
                    isStepComplete(STEP.datetime) ? 'bg-green-100' : 'bg-primary-100'
                  }`}
                >
                  {isStepComplete(STEP.datetime) ? (
                    <CheckCircle className="h-5 w-5 text-green-600 sm:h-6 sm:w-6" />
                  ) : (
                    <Calendar className="h-5 w-5 text-primary-600 sm:h-6 sm:w-6" />
                  )}
                </div>
                <div className="min-w-0">
                  <h3 className="text-lg font-semibold text-gray-900">{STEP.datetime}. Fecha y horario</h3>
                  <p className="mt-1 text-sm text-gray-500">
                    Elige la fecha; los horarios aparecen al confirmar el día.
                  </p>
                </div>
                <div className="col-span-2 min-w-0 space-y-5 sm:col-span-1 sm:col-start-2">
                  <BookingDateField
                    selectedDate={selectedDate}
                    onSelectDate={handleDateSelect}
                    id="booking-appointment-date"
                  />

                  {selectedDate && (
                    <div
                      ref={sectionTimeSlotsRef}
                      className="scroll-mt-3 border-t border-gray-100 pt-5"
                    >
                      <TimeSlotPicker
                        variant="chips"
                        shiftLabel={shiftTimeLabel}
                        slots={slots}
                        selectedSlot={selectedSlot}
                        onSelectSlot={setSelectedSlot}
                        loading={loadingSlots}
                      />
                    </div>
                  )}
                </div>
              </div>
            </Card>
            </section>
          )}

          {selectedSlot && (
            <section
              ref={sectionReasonRef}
              className="scroll-mt-4"
              aria-label="Paso: motivo de consulta"
            >
            <Card className="relative" bodyClassName="px-3 py-4 sm:px-6 sm:py-4">
              <div className="grid grid-cols-[auto_1fr] gap-x-2.5 sm:grid-cols-[2.5rem_1fr] sm:gap-x-4">
                <div
                  className={`flex h-9 w-9 shrink-0 items-center justify-center rounded-full sm:h-10 sm:w-10 ${
                    isStepComplete(STEP.reason) ? 'bg-green-100' : 'bg-primary-100'
                  }`}
                >
                  {isStepComplete(STEP.reason) ? (
                    <CheckCircle className="h-5 w-5 text-green-600 sm:h-6 sm:w-6" />
                  ) : (
                    <span className="text-sm font-semibold text-primary-600 sm:text-base">{STEP.reason}</span>
                  )}
                </div>
                <div className="min-w-0">
                  <h3 className="mb-3 text-lg font-semibold text-gray-900">
                    {STEP.reason}. Motivo de la Consulta
                  </h3>
                </div>
                <div className="col-span-2 min-w-0 sm:col-span-1 sm:col-start-2">
                  <Input
                    label="Describe brevemente el motivo de tu consulta"
                    name="reason"
                    value={reason}
                    onChange={(e) => setReason(e.target.value)}
                    placeholder="Ej: Dolor de cabeza persistente"
                    required
                  />
                </div>
              </div>
            </Card>
            </section>
          )}

          {selectedSlot && (
            <div className="flex justify-end space-x-4">
              <Button type="button" variant="outline" onClick={() => navigate('/dashboard')}>
                Cancelar
              </Button>
              <Button type="submit" variant="primary" loading={submitting} disabled={submitting}>
                {rescheduleAppointmentId ? 'Confirmar Reagendamiento' : 'Confirmar Cita'}
              </Button>
            </div>
          )}
        </form>
      )}

      <ConfirmDialog
        isOpen={showConfirmDialog}
        onClose={() => setShowConfirmDialog(false)}
        onConfirm={handleConfirmSubmit}
        title={rescheduleAppointmentId ? 'Confirmar Reagendamiento' : 'Confirmar Cita'}
        message={
          rescheduleAppointmentId
            ? `¿Estás seguro de que deseas reagendar tu cita?\n\nLa cita original será eliminada y se creará una nueva cita con la fecha y horario seleccionados.`
            : `¿Estás seguro de que deseas agendar esta cita?\n\nFecha: ${selectedDate ? formatDate(selectedDate) : ''}\nHora: ${selectedSlot ? `${formatTime(selectedSlot.start_time)} - ${formatTime(selectedSlot.end_time)}` : ''}\nEspecialidad: ${specialtyName}`
        }
        confirmText={rescheduleAppointmentId ? 'Sí, Reagendar' : 'Sí, Confirmar'}
        cancelText="Cancelar"
        variant="primary"
      />
    </div>
  )
}

export default BookAppointment
