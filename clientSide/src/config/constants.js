/**
 * Application Constants
 */

export const APP_NAME = import.meta.env.VITE_APP_NAME || 'Neumoapp'
export const APP_VERSION = import.meta.env.VITE_APP_VERSION || '1.0.0'

export const TOKEN_KEY = 'neumoapp_token'
export const USER_KEY = 'neumoapp_user'

export const APPOINTMENT_STATUS = {
  PENDING: 'pending',
  CONFIRMED: 'confirmed',
  COMPLETED: 'completed',
  CANCELLED: 'cancelled',
}

export const APPOINTMENT_STATUS_LABELS = {
  [APPOINTMENT_STATUS.PENDING]: 'Pendiente',
  [APPOINTMENT_STATUS.CONFIRMED]: 'Confirmada',
  [APPOINTMENT_STATUS.COMPLETED]: 'Completada',
  [APPOINTMENT_STATUS.CANCELLED]: 'Cancelada',
}

export const APPOINTMENT_STATUS_COLORS = {
  [APPOINTMENT_STATUS.PENDING]: 'bg-yellow-100 text-yellow-800',
  [APPOINTMENT_STATUS.CONFIRMED]: 'bg-green-100 text-green-800',
  [APPOINTMENT_STATUS.COMPLETED]: 'bg-blue-100 text-blue-800',
  [APPOINTMENT_STATUS.CANCELLED]: 'bg-red-100 text-red-800',
}

export const SHIFT_TYPES = {
  MORNING: 'morning',
  AFTERNOON: 'afternoon',
}

export const SHIFT_LABELS = {
  [SHIFT_TYPES.MORNING]: 'Mañana (8:00 - 13:00)',
  [SHIFT_TYPES.AFTERNOON]: 'Tarde (14:00 - 18:00)',
}

export const GENDERS = {
  MALE: 'Masculino',
  FEMALE: 'Femenino',
  OTHER: 'Otro',
}

export const CIVIL_STATUS = {
  SINGLE: 'Soltero/a',
  MARRIED: 'Casado/a',
  DIVORCED: 'Divorciado/a',
  WIDOWED: 'Viudo/a',
}

export const DATE_FORMAT = 'dd/MM/yyyy'
export const TIME_FORMAT = 'HH:mm'
export const DATETIME_FORMAT = 'dd/MM/yyyy HH:mm'

