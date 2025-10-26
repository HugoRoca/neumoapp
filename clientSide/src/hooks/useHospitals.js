import { useState, useEffect, useCallback } from 'react'
import hospitalService from '@/services/hospital.service'

/**
 * Custom hook to fetch hospitals
 * @returns {Object} { hospitals, loading, error, refetch }
 */
export const useHospitals = () => {
  const [hospitals, setHospitals] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)

  const fetchHospitals = useCallback(async () => {
    try {
      setLoading(true)
      setError(null)
      const data = await hospitalService.getHospitals()
      setHospitals(data)
    } catch (err) {
      setError(err.response?.data?.detail || 'Error al cargar los hospitales')
    } finally {
      setLoading(false)
    }
  }, [])

  useEffect(() => {
    fetchHospitals()
  }, [fetchHospitals])

  return {
    hospitals,
    loading,
    error,
    refetch: fetchHospitals,
  }
}

export default useHospitals

