import { useQuery } from '@tanstack/react-query'
import appointmentService from '@/services/appointment.service'

/**
 * Normalizes the appointment data structure
 * @param {Array} data - The raw appointment data from the API
 * @returns {Array} The normalized appointment data
 */
const normalizeAppointments = (data) => {
  if (!Array.isArray(data)) {
    return []
  }
  return data.map(appointment => ({
    ...appointment,
    specialty_name: appointment.specialty?.name || appointment.specialty_name || 'N/A',
    consultation_room_name: appointment.consultation_room?.name || appointment.consultation_room_name || 'N/A',
    consultation_room_number: appointment.consultation_room?.room_number || appointment.consultation_room_number || 'N/A',
  }))
}

/**
 * Custom hook to fetch appointments using React Query
 * @returns {Object} { appointments, loading, error, refetch }
 */
export const useAppointments = () => {
  const { 
    data: appointments = [], 
    isLoading: loading, 
    isError: hasError,
    error, 
    refetch 
  } = useQuery({
    queryKey: ['appointments'],
    queryFn: () => appointmentService.getMyAppointments(),
    select: normalizeAppointments,
  })

  return {
    appointments,
    loading,
    error: hasError ? error.response?.data?.detail || error.message : null,
    refetch,
  }
}

export default useAppointments
