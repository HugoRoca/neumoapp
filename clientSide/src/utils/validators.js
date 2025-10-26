/**
 * Validation utilities
 */

/**
 * Validate Peruvian DNI (8 digits)
 * @param {string} dni - DNI to validate
 * @returns {boolean} True if valid
 */
export const validateDNI = (dni) => {
  if (!dni) return false
  const dniRegex = /^\d{8}$/
  return dniRegex.test(dni)
}

/**
 * Validate email format
 * @param {string} email - Email to validate
 * @returns {boolean} True if valid
 */
export const validateEmail = (email) => {
  if (!email) return false
  const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/
  return emailRegex.test(email)
}

/**
 * Validate phone number (9 digits, starts with 9)
 * @param {string} phone - Phone to validate
 * @returns {boolean} True if valid
 */
export const validatePhone = (phone) => {
  if (!phone) return false
  const phoneRegex = /^9\d{8}$/
  return phoneRegex.test(phone)
}

/**
 * Validate password strength
 * @param {string} password - Password to validate
 * @returns {Object} { valid: boolean, message: string }
 */
export const validatePassword = (password) => {
  if (!password) {
    return { valid: false, message: 'La contraseña es requerida' }
  }
  
  if (password.length < 8) {
    return { valid: false, message: 'La contraseña debe tener al menos 8 caracteres' }
  }
  
  return { valid: true, message: '' }
}

/**
 * Validate required field
 * @param {any} value - Value to validate
 * @param {string} fieldName - Field name for error message
 * @returns {Object} { valid: boolean, message: string }
 */
export const validateRequired = (value, fieldName = 'Campo') => {
  if (!value || (typeof value === 'string' && value.trim() === '')) {
    return { valid: false, message: `${fieldName} es requerido` }
  }
  return { valid: true, message: '' }
}

export default {
  validateDNI,
  validateEmail,
  validatePhone,
  validatePassword,
  validateRequired,
}

