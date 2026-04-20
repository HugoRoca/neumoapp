import apiClient from './api.service'
import { API_CONFIG } from '@/config/api.config'

/**
 * Appointment Service
 * Handles all appointment-related API calls
 */

export const appointmentService = {
  /**
   * Listado paginado de mis citas (filtros opcionales).
   * @param {Object} [params]
   * @param {number} [params.skip]
   * @param {number} [params.limit]
   * @param {string} [params.status]
   * @param {string} [params.date_from] - YYYY-MM-DD
   * @param {string} [params.date_to] - YYYY-MM-DD
   * @param {string} [params.search]
   * @returns {Promise<{ items, total, skip, limit }>}
   */
  getMyAppointments: async (params = {}) => {
    const clean = Object.fromEntries(
      Object.entries(params).filter(([, v]) => v !== undefined && v !== null && v !== '')
    )
    const response = await apiClient.get(API_CONFIG.ENDPOINTS.APPOINTMENTS.MY_APPOINTMENTS, {
      params: clean,
    })
    return response.data
  },

  /**
   * Get upcoming appointments
   * @param {number} skip - Number of appointments to skip (default: 0)
   * @param {number} limit - Number of appointments to fetch (default: 5)
   * @returns {Promise} API response with upcoming appointments
   */
  getUpcomingAppointments: async (skip = 0, limit = 5) => {
    const response = await apiClient.get(API_CONFIG.ENDPOINTS.APPOINTMENTS.UPCOMING, {
      params: { skip, limit }
    })
    return response.data
  },

  /**
   * Get appointment by ID
   * @param {number} id - Appointment ID
   * @returns {Promise} API response with appointment details
   */
  getAppointmentById: async (id) => {
    const response = await apiClient.get(API_CONFIG.ENDPOINTS.APPOINTMENTS.BY_ID(id))
    return response.data
  },

  /**
   * Create a new appointment
   * @param {Object} appointmentData - Appointment data
   * @returns {Promise} API response with created appointment
   */
  createAppointment: async (appointmentData) => {
    const response = await apiClient.post(API_CONFIG.ENDPOINTS.APPOINTMENTS.BASE, appointmentData)
    return response.data
  },

  /**
   * Update an appointment
   * @param {number} id - Appointment ID
   * @param {Object} updateData - Data to update
   * @returns {Promise} API response with updated appointment
   */
  updateAppointment: async (id, updateData) => {
    const response = await apiClient.patch(API_CONFIG.ENDPOINTS.APPOINTMENTS.BY_ID(id), updateData)
    return response.data
  },

  /**
   * Cancel an appointment
   * @param {number} id - Appointment ID
   * @returns {Promise} API response
   */
  cancelAppointment: async (id) => {
    const response = await apiClient.delete(API_CONFIG.ENDPOINTS.APPOINTMENTS.BY_ID(id))
    return response.data
  },
}

export default appointmentService

