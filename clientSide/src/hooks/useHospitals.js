import { useState, useEffect, useCallback } from 'react'
import hospitalService from '@/services/hospital.service'

/**
 * Custom hook to fetch hospitals
 * @param {number} skip - Number of hospitals to skip (default: 0)
 * @param {number} limit - Number of hospitals to fetch (default: 10)
 * @returns {Object} { hospitals, loading, error, refetch }
 */
export const useHospitals = (skip = 0, limit = 10) => {
  const [hospitals, setHospitals] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)

  const fetchHospitals = useCallback(async () => {
    try {
      setLoading(true)
      setError(null)
      const data = await hospitalService.getHospitals(skip, limit)
      setHospitals(data)
    } catch (err) {
      setError(err.response?.data?.detail || 'Error al cargar los hospitales')
    } finally {
      setLoading(false)
    }
  }, [skip, limit])

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

