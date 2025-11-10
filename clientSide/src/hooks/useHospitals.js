import { useQuery } from '@tanstack/react-query'
import hospitalService from '@/services/hospital.service'

/**
 * Custom hook to fetch hospitals using React Query
 * @param {number} skip - Number of hospitals to skip (default: 0)
 * @param {number} limit - Number of hospitals to fetch (default: 10)
 * @returns {Object} { hospitals, loading, error, refetch }
 */
export const useHospitals = (skip = 0, limit = 10) => {
  const {
    data: hospitals = [],
    isLoading: loading,
    isError: hasError,
    error,
    refetch,
  } = useQuery({
    queryKey: ['hospitals', skip, limit],
    queryFn: () => hospitalService.getHospitals(skip, limit),
  })

  return {
    hospitals,
    loading,
    error: hasError ? error.response?.data?.detail || error.message : null,
    refetch,
  }
}

export default useHospitals
