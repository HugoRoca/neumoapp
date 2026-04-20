import { useMemo } from 'react'
import { useQuery } from '@tanstack/react-query'
import appointmentService from '@/services/appointment.service'

const normalizeItem = (appointment) => ({
  ...appointment,
  specialty_name: appointment.specialty?.name || appointment.specialty_name || 'N/A',
  consultation_room_name:
    appointment.consultation_room?.name || appointment.consultation_room_name || 'N/A',
  consultation_room_number:
    appointment.consultation_room?.room_number || appointment.consultation_room_number || 'N/A',
})

/**
 * @param {Object} params - skip, limit, status, date_from, date_to, search
 */
export const useAppointments = (params = {}) => {
  const queryParams = useMemo(
    () => ({
      skip: params.skip ?? 0,
      limit: params.limit ?? 12,
      status: params.status,
      date_from: params.date_from,
      date_to: params.date_to,
      search: params.search,
    }),
    [params.skip, params.limit, params.status, params.date_from, params.date_to, params.search]
  )

  const {
    data,
    isLoading: loading,
    isError: hasError,
    error,
    refetch,
    isFetching,
  } = useQuery({
    queryKey: ['appointments', 'my', queryParams],
    queryFn: () => appointmentService.getMyAppointments(queryParams),
    select: (page) => ({
      items: Array.isArray(page?.items) ? page.items.map(normalizeItem) : [],
      total: typeof page?.total === 'number' ? page.total : 0,
      skip: page?.skip ?? 0,
      limit: page?.limit ?? 12,
    }),
  })

  return {
    appointments: data?.items ?? [],
    total: data?.total ?? 0,
    skip: data?.skip ?? 0,
    limit: data?.limit ?? 12,
    loading,
    fetching: isFetching,
    error: hasError ? error.response?.data?.detail || error.message : null,
    refetch,
  }
}

export default useAppointments
