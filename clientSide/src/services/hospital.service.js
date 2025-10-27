import apiClient from './api.service'
import { API_CONFIG } from '@/config/api.config'

/**
 * Hospital Service
 * Handles all hospital-related API calls
 */

export const hospitalService = {
  /**
   * Get all hospitals with pagination
   * @param {number} skip - Number of hospitals to skip (default: 0)
   * @param {number} limit - Number of hospitals to fetch (default: 10)
   * @returns {Promise} API response with hospitals list
   */
  getHospitals: async (skip = 0, limit = 10) => {
    const response = await apiClient.get(API_CONFIG.ENDPOINTS.HOSPITALS.BASE, {
      params: { skip, limit }
    })
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

  /**
   * Get specialties available in a hospital
   * @param {number} hospitalId - Hospital ID
   * @returns {Promise} API response with specialties list
   */
  getHospitalSpecialties: async (hospitalId) => {
    const response = await apiClient.get(`/hospitals/${hospitalId}/specialties`)
    return response.data
  },
}

export default hospitalService

