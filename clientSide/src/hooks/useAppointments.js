import { useState, useEffect, useCallback } from 'react'
import appointmentService from '@/services/appointment.service'

/**
 * Custom hook to fetch appointments
 * @returns {Object} { appointments, loading, error, refetch }
 */
export const useAppointments = () => {
  const [appointments, setAppointments] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)

  const fetchAppointments = useCallback(async () => {
    try {
      setLoading(true)
      setError(null)
      const data = await appointmentService.getMyAppointments()
      setAppointments(data)
    } catch (err) {
      setError(err.response?.data?.detail || 'Error al cargar las citas')
    } finally {
      setLoading(false)
    }
  }, [])

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

export default useAppointments

