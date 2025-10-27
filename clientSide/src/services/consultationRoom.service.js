import apiClient from './api.service'
import { API_CONFIG } from '@/config/api.config'

/**
 * Consultation Room Service
 * Handles all consultation room-related API calls
 */

export const consultationRoomService = {
  /**
   * Get consultation rooms by specialty (deprecated - use getRoomsByHospitalAndSpecialty)
   * @param {number} specialtyId - Specialty ID
   * @returns {Promise} API response with consultation rooms list
   */
  getRoomsBySpecialty: async (specialtyId) => {
    const response = await apiClient.get(API_CONFIG.ENDPOINTS.CONSULTATION_ROOMS.BY_SPECIALTY(specialtyId))
    return response.data
  },

  /**
   * Get consultation rooms filtered by hospital and specialty
   * @param {number} hospitalId - Hospital ID
   * @param {number} specialtyId - Specialty ID
   * @returns {Promise} API response with consultation rooms list
   */
  getRoomsByHospitalAndSpecialty: async (hospitalId, specialtyId) => {
    const response = await apiClient.get('/consultation-rooms/by-hospital-and-specialty', {
      params: {
        hospital_id: hospitalId,
        specialty_id: specialtyId,
      }
    })
    return response.data
  },
}

export default consultationRoomService

