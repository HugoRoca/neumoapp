/**
 * API Configuration
 * Centralized configuration for API connection
 */

export const API_CONFIG = {
  BASE_URL: import.meta.env.VITE_API_BASE_URL || 'http://localhost:3000',
  TIMEOUT: parseInt(import.meta.env.VITE_API_TIMEOUT) || 30000,
  ENDPOINTS: {
    // Authentication
    AUTH: {
      REGISTER: '/auth/register',
      LOGIN: '/auth/login',
      ME: '/auth/me',
      REFRESH: '/auth/refresh',
    },
    // Patients
    PATIENTS: {
      BASE: '/patients',
      BY_ID: (id) => `/patients/${id}`,
    },
    // Specialties
    SPECIALTIES: {
      BASE: '/specialties',
      BY_ID: (id) => `/specialties/${id}`,
    },
    // Hospitals
    HOSPITALS: {
      BASE: '/hospitals',
      BY_ID: (id) => `/hospitals/${id}`,
    },
    // Consultation Rooms
    CONSULTATION_ROOMS: {
      BASE: '/consultation-rooms',
      BY_ID: (id) => `/consultation-rooms/${id}`,
      BY_SPECIALTY: (specialtyId) => `/consultation-rooms/by-specialty/${specialtyId}`,
      ASSIGN_SPECIALTY: (roomId) => `/consultation-rooms/${roomId}/assign-specialty`,
      REMOVE_SPECIALTY: (roomId) => `/consultation-rooms/${roomId}/remove-specialty`,
    },
    // Available Slots
    SLOTS: {
      AVAILABLE: '/slots/available',
    },
    // Appointments
    APPOINTMENTS: {
      BASE: '/appointments',
      BY_ID: (id) => `/appointments/${id}`,
      MY_APPOINTMENTS: '/appointments/my-appointments',
      UPCOMING: '/appointments/upcoming',
    },
  },
}

export default API_CONFIG

