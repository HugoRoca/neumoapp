import { useState, useEffect, useCallback } from 'react'
import appointmentService from '@/services/appointment.service'

/**
 * Custom hook to fetch upcoming appointments
 * @param {number} limit - Number of appointments to fetch (default: 5)
 * @returns {Object} { appointments, loading, error, refetch }
 */
export const useUpcomingAppointments = (limit = 5) => {
  const [appointments, setAppointments] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)

  const fetchAppointments = useCallback(async () => {
    try {
      setLoading(true)
      setError(null)
      const data = await appointmentService.getUpcomingAppointments(0, limit)
      setAppointments(data)
    } catch (err) {
      setError(err.response?.data?.detail || 'Error al cargar las citas')
    } finally {
      setLoading(false)
    }
  }, [limit])

  useEffect(() => {
    fetchAppointments()
  }, [fetchAppointments])

  return {
    appointments,
    loading,
    error,
    refetch: fetchAppointments,
  }
}

export default useUpcomingAppointments

