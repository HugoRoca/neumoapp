import { useQuery } from '@tanstack/react-query'
import specialtyService from '@/services/specialty.service'

/**
 * Custom hook to fetch specialties using React Query
 * @returns {Object} { specialties, loading, error, refetch }
 */
export const useSpecialties = () => {
  const {
    data: specialties = [],
    isLoading: loading,
    isError: hasError,
    error,
    refetch,
  } = useQuery({
    queryKey: ['specialties'],
    queryFn: () => specialtyService.getSpecialties(),
  })

  return {
    specialties,
    loading,
    error: hasError ? error.response?.data?.detail || error.message : null,
    refetch,
  }
}

export default useSpecialties

