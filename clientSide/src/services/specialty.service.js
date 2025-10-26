import apiClient from './api.service'
import { API_CONFIG } from '@/config/api.config'

/**
 * Specialty Service
 * Handles all specialty-related API calls
 */

export const specialtyService = {
  /**
   * Get all specialties
   * @returns {Promise} API response with specialties list
   */
  getSpecialties: async () => {
    const response = await apiClient.get(API_CONFIG.ENDPOINTS.SPECIALTIES.BASE)
    return response.data
  },

  /**
   * Get specialty by ID
   * @param {number} id - Specialty ID
   * @returns {Promise} API response with specialty details
   */
  getSpecialtyById: async (id) => {
    const response = await apiClient.get(API_CONFIG.ENDPOINTS.SPECIALTIES.BY_ID(id))
    return response.data
  },
}

export default specialtyService

