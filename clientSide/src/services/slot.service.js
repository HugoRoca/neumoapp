import apiClient from './api.service'
import { API_CONFIG } from '@/config/api.config'

/**
 * Slot Service
 * Handles all time slot-related API calls
 */

export const slotService = {
  /**
   * Get available time slots
   * @param {Object} params - Query parameters
   * @param {number} params.hospital_id - Hospital ID
   * @param {number} params.specialty_id - Specialty ID
   * @param {string} params.date - Date in YYYY-MM-DD format
   * @param {string} params.shift - Shift type (morning/afternoon)
   * @returns {Promise} API response with available slots
   */
  getAvailableSlots: async ({ hospital_id, specialty_id, date, shift }) => {
    const response = await apiClient.get(API_CONFIG.ENDPOINTS.SLOTS.AVAILABLE, {
      params: {
        hospital_id,
        specialty_id,
        date,
        shift,
      },
    })
    return response.data
  },
}

export default slotService

