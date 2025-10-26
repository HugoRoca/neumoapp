import { useState, useEffect, useCallback } from 'react'
import specialtyService from '@/services/specialty.service'

/**
 * Custom hook to fetch specialties
 * @returns {Object} { specialties, loading, error, refetch }
 */
export const useSpecialties = () => {
  const [specialties, setSpecialties] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)

  const fetchSpecialties = useCallback(async () => {
    try {
      setLoading(true)
      setError(null)
      const data = await specialtyService.getSpecialties()
      setSpecialties(data)
    } catch (err) {
      setError(err.response?.data?.detail || 'Error al cargar las especialidades')
    } finally {
      setLoading(false)
    }
  }, [])

  useEffect(() => {
    fetchSpecialties()
  }, [fetchSpecialties])

  return {
    specialties,
    loading,
    error,
    refetch: fetchSpecialties,
  }
}

export default useSpecialties

