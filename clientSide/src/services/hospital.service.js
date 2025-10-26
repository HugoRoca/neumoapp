import apiClient from './api.service'
import { API_CONFIG } from '@/config/api.config'

/**
 * Hospital Service
 * Handles all hospital-related API calls
 */

export const hospitalService = {
  /**
   * Get all hospitals
   * @returns {Promise} API response with hospitals list
   */
  getHospitals: async () => {
    const response = await apiClient.get(API_CONFIG.ENDPOINTS.HOSPITALS.BASE)
    return response.data
  },

  /**
   * Get hospital by ID
   * @param {number} id - Hospital ID
   * @returns {Promise} API response with hospital details
   */
  getHospitalById: async (id) => {
    const response = await apiClient.get(API_CONFIG.ENDPOINTS.HOSPITALS.BY_ID(id))
    return response.data
  },
}

export default hospitalService

