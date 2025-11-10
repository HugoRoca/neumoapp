import { useQuery } from '@tanstack/react-query'
import appointmentService from '@/services/appointment.service'

/**
 * Custom hook to fetch upcoming appointments using React Query
 * @param {number} limit - Number of appointments to fetch (default: 5)
 * @returns {Object} { appointments, loading, error, refetch }
 */
export const useUpcomingAppointments = (limit = 5) => {
  const {
    data: appointments = [],
    isLoading: loading,
    isError: hasError,
    error,
    refetch,
  } = useQuery({
    queryKey: ['upcomingAppointments', limit],
    queryFn: () => appointmentService.getUpcomingAppointments(0, limit),
  })

  return {
    appointments,
    loading,
    error: hasError ? error.response?.data?.detail || error.message : null,
    refetch,
  }
}

export default useUpcomingAppointments
