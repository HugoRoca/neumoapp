import apiClient from './api.service'
import { API_CONFIG } from '@/config/api.config'

/**
 * Authentication Service
 * Handles all authentication-related API calls
 */

export const authService = {
  /**
   * Register a new patient
   * @param {Object} userData - User registration data
   * @returns {Promise} API response
   */
  register: async (userData) => {
    const response = await apiClient.post(API_CONFIG.ENDPOINTS.AUTH.REGISTER, userData)
    return response.data
  },

  /**
   * Login with document number and password
   * @param {string} document_number - Patient document number
   * @param {string} password - Patient password
   * @returns {Promise} API response with token
   */
  login: async (document_number, password) => {
    const response = await apiClient.post(API_CONFIG.ENDPOINTS.AUTH.LOGIN, {
      document_number,
      password,
    })
    return response.data
  },

  /**
   * Get current authenticated user profile
   * @returns {Promise} API response with user data
   */
  getProfile: async () => {
    const response = await apiClient.get(API_CONFIG.ENDPOINTS.AUTH.ME)
    return response.data
  },
}

export default authService

