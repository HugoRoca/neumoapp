import { useState, useEffect } from 'react'
import { useNavigate, useSearchParams } from 'react-router-dom'
import MainLayout from '@/components/Layout/MainLayout'
import Card from '@/components/UI/Card'
import Select from '@/components/UI/Select'
import Input from '@/components/UI/Input'
import Button from '@/components/UI/Button'
import LoadingSpinner from '@/components/UI/LoadingSpinner'
import ConfirmDialog from '@/components/UI/ConfirmDialog'
import CalendarPicker from '@/components/Appointment/CalendarPicker'
import TimeSlotPicker from '@/components/Appointment/TimeSlotPicker'
import { Building2, Stethoscope, DoorOpen, Calendar, Clock, CheckCircle, AlertCircle, RefreshCw } from 'lucide-react'
import { toast } from 'sonner'
import hospitalService from '@/services/hospital.service'
import consultationRoomService from '@/services/consultationRoom.service'
import slotService from '@/services/slot.service'
import appointmentService from '@/services/appointment.service'
import { formatDateForAPI, formatDate, formatTime } from '@/utils/dateUtils'

/**
 * Book Appointment Page
 * Multi-step form for booking medical appointments
 * Supports rescheduling existing appointments
 */
const BookAppointment = () => {
  const navigate = useNavigate()
  const [searchParams] = useSearchParams()
  const rescheduleAppointmentId = searchParams.get('reschedule')
  
  // Form data
  const [selectedHospital, setSelectedHospital] = useState('')
  const [selectedSpecialty, setSelectedSpecialty] = useState('')
  const [selectedRoom, setSelectedRoom] = useState('')
  const [selectedShift, setSelectedShift] = useState('')
  const [selectedDate, setSelectedDate] = useState(null)
  const [selectedSlot, setSelectedSlot] = useState(null)
  const [reason, setReason] = useState('')
  
  // Data lists
  const [hospitals, setHospitals] = useState([])
  const [specialties, setSpecialties] = useState([])
  const [rooms, setRooms] = useState([])
  const [slots, setSlots] = useState([])
  
  // Reschedule state
  const [originalAppointment, setOriginalAppointment] = useState(null)
  const [loadingOriginalAppointment, setLoadingOriginalAppointment] = useState(false)
  
  // Confirmation dialog state
  const [showConfirmDialog, setShowConfirmDialog] = useState(false)
  
  // Loading states
  const [loadingHospitals, setLoadingHospitals] = useState(true)
  const [loadingSpecialties, setLoadingSpecialties] = useState(false)
  const [loadingRooms, setLoadingRooms] = useState(false)
  const [loadingSlots, setLoadingSlots] = useState(false)
  const [submitting, setSubmitting] = useState(false)

  // Load original appointment if rescheduling
  useEffect(() => {
    if (rescheduleAppointmentId) {
      const fetchOriginalAppointment = async () => {
        try {
          setLoadingOriginalAppointment(true)
          const appointment = await appointmentService.getAppointmentById(rescheduleAppointmentId)
          setOriginalAppointment(appointment)
          
          // Pre-fill form with original appointment data
          if (appointment.consultation_room?.hospital_id) {
            setSelectedHospital(appointment.consultation_room.hospital_id.toString())
          }
          if (appointment.specialty_id) {
            setSelectedSpecialty(appointment.specialty_id.toString())
          }
          if (appointment.reason) {
            setReason(appointment.reason)
          }
        } catch (error) {
          toast.error('Error al cargar la cita original')
          navigate('/dashboard')
        } finally {
          setLoadingOriginalAppointment(false)
        }
      }
      fetchOriginalAppointment()
    }
  }, [rescheduleAppointmentId, navigate])

  // Load hospitals on mount
  useEffect(() => {
    const fetchHospitals = async () => {
      try {
        setLoadingHospitals(true)
        const data = await hospitalService.getHospitals(0, 10)
        setHospitals(data)
      } catch (error) {
        toast.error('Error al cargar hospitales')
      } finally {
        setLoadingHospitals(false)
      }
    }
    fetchHospitals()
  }, [])

  // Load specialties when hospital changes
  useEffect(() => {
    if (selectedHospital) {
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
        } catch (error) {
          toast.error('Error al cargar especialidades')
        } finally {
          setLoadingSpecialties(false)
        }
      }
      fetchSpecialties()
    } else {
      setSpecialties([])
    }
  }, [selectedHospital])

  // Load rooms when hospital and specialty are selected
  useEffect(() => {
    if (selectedHospital && selectedSpecialty) {
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
        } catch (error) {
          toast.error('Error al cargar consultorios')
        } finally {
          setLoadingRooms(false)
        }
      }
      fetchRooms()
    } else {
      setRooms([])
    }
  }, [selectedHospital, selectedSpecialty])

  // Load slots when date and shift are selected
  useEffect(() => {
    if (selectedHospital && selectedSpecialty && selectedRoom && selectedDate && selectedShift) {
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
        } catch (error) {
          toast.error('Error al cargar horarios disponibles')
          setSlots([])
        } finally {
          setLoadingSlots(false)
        }
      }
      fetchSlots()
    } else {
      setSlots([])
    }
  }, [selectedHospital, selectedSpecialty, selectedRoom, selectedDate, selectedShift])

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

    // Show confirmation dialog
    setShowConfirmDialog(true)
  }

  const handleConfirmSubmit = async () => {
    setShowConfirmDialog(false)
    
    try {
      setSubmitting(true)
      
      // Create new appointment
      const newAppointment = await appointmentService.createAppointment({
        specialty_id: parseInt(selectedSpecialty),
        consultation_room_id: selectedSlot.consultation_room.id,
        appointment_date: formatDateForAPI(selectedDate),
        start_time: selectedSlot.start_time,
        shift: selectedShift,
        reason: reason.trim(),
      })
      
      // If rescheduling, update new appointment status and delete original
      if (rescheduleAppointmentId && originalAppointment) {
        try {
          // Update NEW appointment status to "rescheduled"
          await appointmentService.updateAppointment(newAppointment.id, {
            status: 'rescheduled',
            observations: `Cita reprogramada. Cita original ID: ${rescheduleAppointmentId} fue eliminada.`
          })
          
          // Delete the original appointment
          await appointmentService.cancelAppointment(rescheduleAppointmentId)
          
          toast.success('¡Cita reprogramada exitosamente!')
        } catch (updateError) {
          // Even if update/delete fails, the new appointment was created
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

  const isStepComplete = (step) => {
    switch(step) {
      case 1: return !!selectedHospital
      case 2: return !!selectedSpecialty
      case 3: return !!selectedRoom
      case 4: return !!selectedShift
      case 5: return !!selectedDate
      case 6: return !!selectedSlot
      default: return false
    }
  }

  return (
    <MainLayout>
      <div className="px-4 sm:px-6 lg:px-8 py-6 sm:py-8">
        <div className="mb-6 sm:mb-8">
          <div className="flex items-center space-x-3 mb-2">
            {rescheduleAppointmentId && (
              <RefreshCw className="w-6 h-6 text-primary-600" />
            )}
            <h1 className="text-2xl sm:text-3xl font-bold text-gray-900">
              {rescheduleAppointmentId ? 'Reagendar Cita' : 'Agendar Cita'}
            </h1>
          </div>
          <p className="text-gray-600 mt-2 text-sm sm:text-base">
            {rescheduleAppointmentId 
              ? 'Selecciona la nueva fecha y horario para tu cita'
              : 'Completa los siguientes pasos para agendar tu cita médica'
            }
          </p>
        </div>

        {/* Original Appointment Info (Reschedule Mode) */}
        {rescheduleAppointmentId && (
          <>
            {loadingOriginalAppointment ? (
              <Card className="max-w-4xl mx-auto mb-6">
                <LoadingSpinner size="sm" message="Cargando información de la cita original..." />
              </Card>
            ) : originalAppointment ? (
              <Card className="max-w-4xl mx-auto mb-6 border-2 border-yellow-200 bg-yellow-50">
                <div className="flex items-start space-x-3">
                  <AlertCircle className="w-5 h-5 text-yellow-600 mt-0.5 flex-shrink-0" />
                  <div className="flex-1">
                    <h3 className="text-sm font-semibold text-yellow-900 mb-2">
                      Estás reprogramando una cita existente
                    </h3>
                    <div className="bg-white rounded-lg p-3 space-y-2 text-sm">
                      <div className="grid grid-cols-1 sm:grid-cols-2 gap-2">
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
                          <span className="font-medium">
                            {originalAppointment.consultation_room?.name || 'N/A'}
                          </span>
                        </div>
                      </div>
                      <p className="text-xs text-gray-600 pt-2 border-t border-gray-100">
                        La cita original será cancelada y marcada como reprogramada una vez que confirmes la nueva cita.
                      </p>
                    </div>
                  </div>
                </div>
              </Card>
            ) : null}
          </>
        )}

        {loadingHospitals ? (
          <LoadingSpinner message="Cargando..." />
        ) : (
          <form onSubmit={handleSubmit} className="max-w-4xl mx-auto space-y-6">
            {/* Step 1: Hospital */}
            <Card className="relative">
              <div className="flex items-start space-x-4">
                <div className={`flex-shrink-0 w-10 h-10 rounded-full flex items-center justify-center ${isStepComplete(1) ? 'bg-green-100' : 'bg-primary-100'}`}>
                  {isStepComplete(1) ? (
                    <CheckCircle className="w-6 h-6 text-green-600" />
                  ) : (
                    <Building2 className="w-6 h-6 text-primary-600" />
                  )}
                </div>
                <div className="flex-1">
                  <h3 className="text-lg font-semibold text-gray-900 mb-3">
                    1. Selecciona el Hospital
                  </h3>
                  <Select
                    name="hospital"
                    value={selectedHospital}
                    onChange={(e) => setSelectedHospital(e.target.value)}
                    options={hospitals.map(h => ({ value: h.id, label: h.name }))}
                    placeholder="Selecciona un hospital"
                    required
                  />
                </div>
              </div>
            </Card>

            {/* Step 2: Specialty */}
            {selectedHospital && (
              <Card className="relative">
                <div className="flex items-start space-x-4">
                  <div className={`flex-shrink-0 w-10 h-10 rounded-full flex items-center justify-center ${isStepComplete(2) ? 'bg-green-100' : 'bg-primary-100'}`}>
                    {isStepComplete(2) ? (
                      <CheckCircle className="w-6 h-6 text-green-600" />
                    ) : (
                      <Stethoscope className="w-6 h-6 text-primary-600" />
                    )}
                  </div>
                  <div className="flex-1">
                    <h3 className="text-lg font-semibold text-gray-900 mb-3">
                      2. Selecciona la Especialidad
                    </h3>
                    {loadingSpecialties ? (
                      <LoadingSpinner size="sm" message="Cargando especialidades..." />
                    ) : (
                      <Select
                        name="specialty"
                        value={selectedSpecialty}
                        onChange={(e) => setSelectedSpecialty(e.target.value)}
                        options={specialties.map(s => ({ value: s.id, label: `${s.name} (${s.available_rooms} consultorios)` }))}
                        placeholder="Selecciona una especialidad"
                        required
                      />
                    )}
                  </div>
                </div>
              </Card>
            )}

            {/* Step 3: Room */}
            {selectedSpecialty && (
              <Card className="relative">
                <div className="flex items-start space-x-4">
                  <div className={`flex-shrink-0 w-10 h-10 rounded-full flex items-center justify-center ${isStepComplete(3) ? 'bg-green-100' : 'bg-primary-100'}`}>
                    {isStepComplete(3) ? (
                      <CheckCircle className="w-6 h-6 text-green-600" />
                    ) : (
                      <DoorOpen className="w-6 h-6 text-primary-600" />
                    )}
                  </div>
                  <div className="flex-1">
                    <h3 className="text-lg font-semibold text-gray-900 mb-3">
                      3. Selecciona el Consultorio
                    </h3>
                    {loadingRooms ? (
                      <LoadingSpinner size="sm" message="Cargando consultorios..." />
                    ) : (
                      <Select
                        name="room"
                        value={selectedRoom}
                        onChange={(e) => setSelectedRoom(e.target.value)}
                        options={rooms.map(r => ({ value: r.id, label: `${r.name} - ${r.room_number}` }))}
                        placeholder="Selecciona un consultorio"
                        required
                      />
                    )}
                  </div>
                </div>
              </Card>
            )}

            {/* Step 4: Shift */}
            {selectedRoom && (
              <Card className="relative">
                <div className="flex items-start space-x-4">
                  <div className={`flex-shrink-0 w-10 h-10 rounded-full flex items-center justify-center ${isStepComplete(4) ? 'bg-green-100' : 'bg-primary-100'}`}>
                    {isStepComplete(4) ? (
                      <CheckCircle className="w-6 h-6 text-green-600" />
                    ) : (
                      <Clock className="w-6 h-6 text-primary-600" />
                    )}
                  </div>
                  <div className="flex-1">
                    <h3 className="text-lg font-semibold text-gray-900 mb-3">
                      4. Selecciona el Turno
                    </h3>
                    <Select
                      name="shift"
                      value={selectedShift}
                      onChange={(e) => setSelectedShift(e.target.value)}
                      options={[
                        { value: 'morning', label: 'Mañana (8:00 - 13:00)' },
                        { value: 'afternoon', label: 'Tarde (14:00 - 18:00)' },
                      ]}
                      placeholder="Selecciona un turno"
                      required
                    />
                  </div>
                </div>
              </Card>
            )}

            {/* Step 5: Date */}
            {selectedShift && (
              <Card className="relative">
                <div className="flex items-start space-x-4">
                  <div className={`flex-shrink-0 w-10 h-10 rounded-full flex items-center justify-center ${isStepComplete(5) ? 'bg-green-100' : 'bg-primary-100'}`}>
                    {isStepComplete(5) ? (
                      <CheckCircle className="w-6 h-6 text-green-600" />
                    ) : (
                      <Calendar className="w-6 h-6 text-primary-600" />
                    )}
                  </div>
                  <div className="flex-1">
                    <h3 className="text-lg font-semibold text-gray-900 mb-3">
                      5. Selecciona la Fecha
                    </h3>
                    <CalendarPicker
                      selectedDate={selectedDate}
                      onSelectDate={setSelectedDate}
                    />
                    {selectedDate && (
                      <div className="mt-3 space-y-1">
                        <p className="text-sm text-gray-600">
                          Fecha seleccionada: <span className="font-semibold">{formatDate(selectedDate)}</span>
                        </p>
                      </div>
                    )}
                  </div>
                </div>
              </Card>
            )}

            {/* Step 6: Time Slot */}
            {selectedDate && (
              <Card className="relative">
                <div className="flex items-start space-x-4">
                  <div className={`flex-shrink-0 w-10 h-10 rounded-full flex items-center justify-center ${isStepComplete(6) ? 'bg-green-100' : 'bg-primary-100'}`}>
                    {isStepComplete(6) ? (
                      <CheckCircle className="w-6 h-6 text-green-600" />
                    ) : (
                      <Clock className="w-6 h-6 text-primary-600" />
                    )}
                  </div>
                  <div className="flex-1">
                    <h3 className="text-lg font-semibold text-gray-900 mb-3">
                      6. Selecciona el Horario
                    </h3>
                    <TimeSlotPicker
                      slots={slots}
                      selectedSlot={selectedSlot}
                      onSelectSlot={setSelectedSlot}
                      loading={loadingSlots}
                    />
                  </div>
                </div>
              </Card>
            )}

            {/* Step 7: Reason */}
            {selectedSlot && (
              <Card className="relative">
                <div className="flex items-start space-x-4">
                  <div className="flex-shrink-0 w-10 h-10 rounded-full flex items-center justify-center bg-primary-100">
                    <span className="text-primary-600 font-semibold">7</span>
                  </div>
                  <div className="flex-1">
                    <h3 className="text-lg font-semibold text-gray-900 mb-3">
                      7. Motivo de la Consulta
                    </h3>
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
            )}

            {/* Submit Button */}
            {selectedSlot && (
              <div className="flex justify-end space-x-4">
                <Button
                  type="button"
                  variant="outline"
                  onClick={() => navigate('/dashboard')}
                >
                  Cancelar
                </Button>
                <Button
                  type="submit"
                  variant="primary"
                  loading={submitting}
                  disabled={submitting}
                >
                  {rescheduleAppointmentId ? 'Confirmar Reagendamiento' : 'Confirmar Cita'}
                </Button>
              </div>
            )}
          </form>
        )}

        {/* Confirmation Dialog */}
        <ConfirmDialog
          isOpen={showConfirmDialog}
          onClose={() => setShowConfirmDialog(false)}
          onConfirm={handleConfirmSubmit}
          title={rescheduleAppointmentId ? 'Confirmar Reagendamiento' : 'Confirmar Cita'}
          message={
            rescheduleAppointmentId
              ? `¿Estás seguro de que deseas reagendar tu cita?\n\nLa cita original será eliminada y se creará una nueva cita con la fecha y horario seleccionados.`
              : `¿Estás seguro de que deseas agendar esta cita?\n\nFecha: ${selectedDate ? formatDate(selectedDate) : ''}\nHora: ${selectedSlot ? `${formatTime(selectedSlot.start_time)} - ${formatTime(selectedSlot.end_time)}` : ''}\nEspecialidad: ${specialties.find(s => s.id === parseInt(selectedSpecialty))?.name || ''}`
          }
          confirmText={rescheduleAppointmentId ? 'Sí, Reagendar' : 'Sí, Confirmar'}
          cancelText="Cancelar"
          variant="primary"
        />
      </div>
    </MainLayout>
  )
}

export default BookAppointment

