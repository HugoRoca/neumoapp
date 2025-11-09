import { format, isValid, isBefore, startOfDay, addDays } from 'date-fns'
import { es } from 'date-fns/locale'

/**
 * Parse a date string from API (YYYY-MM-DD) to Date object in local timezone
 * Avoids timezone conversion issues
 * @param {string} dateStr - Date string in format YYYY-MM-DD
 * @returns {Date} Date object in local timezone
 */
export const parseDateFromAPI = (dateStr) => {
  if (!dateStr) return null
  
  try {
    // If it's already a Date object, return it
    if (dateStr instanceof Date) {
      return startOfDay(dateStr)
    }
    
    // Parse YYYY-MM-DD format without timezone conversion
    const parts = dateStr.split('T')[0].split('-')
    if (parts.length !== 3) {
      // Try parsing as regular date string
      const date = new Date(dateStr)
      return isValid(date) ? startOfDay(date) : null
    }
    
    const year = parseInt(parts[0], 10)
    const month = parseInt(parts[1], 10) - 1 // Month is 0-indexed
    const day = parseInt(parts[2], 10)
    
    // Create date in local timezone (not UTC)
    const date = new Date(year, month, day, 0, 0, 0, 0)
    return isValid(date) ? date : null
  } catch (error) {
    console.error('Error parsing date from API:', error)
    return null
  }
}

/**
 * Format a date to display format
 * @param {Date|string} date - Date to format
 * @param {string} formatStr - Format string (default: 'dd/MM/yyyy')
 * @returns {string} Formatted date
 */
export const formatDate = (date, formatStr = 'dd/MM/yyyy') => {
  if (!date) return ''
  
  try {
    let dateObj
    if (typeof date === 'string') {
      // Use parseDateFromAPI for date strings to avoid timezone issues
      dateObj = parseDateFromAPI(date)
      if (!dateObj) return ''
    } else {
      dateObj = date
    }
    
    if (!isValid(dateObj)) return ''
    
    // Normalize to start of day in local timezone to ensure consistent formatting
    const normalizedDate = startOfDay(dateObj)
    
    return format(normalizedDate, formatStr, { locale: es })
  } catch (error) {
    console.error('Error formatting date:', error)
    return ''
  }
}

/**
 * Format a time string to display format
 * @param {string} time - Time string (HH:mm:ss or HH:mm)
 * @returns {string} Formatted time (HH:mm)
 */
export const formatTime = (time) => {
  if (!time) return ''
  
  try {
    // Remove seconds if present
    return time.substring(0, 5)
  } catch (error) {
    console.error('Error formatting time:', error)
    return ''
  }
}

/**
 * Format date to API format (YYYY-MM-DD)
 * Uses local timezone to avoid day shift issues
 * @param {Date} date - Date object
 * @returns {string} Formatted date
 */
export const formatDateForAPI = (date) => {
  if (!date) return ''
  
  try {
    if (!isValid(date)) return ''
    
    // Normalize to start of day in local timezone to avoid timezone issues
    const normalizedDate = startOfDay(date)
    
    // Format using local date components to avoid UTC conversion
    const year = normalizedDate.getFullYear()
    const month = String(normalizedDate.getMonth() + 1).padStart(2, '0')
    const day = String(normalizedDate.getDate()).padStart(2, '0')
    
    return `${year}-${month}-${day}`
  } catch (error) {
    console.error('Error formatting date for API:', error)
    return ''
  }
}

/**
 * Check if a date is in the past
 * @param {Date|string} date - Date to check
 * @returns {boolean} True if date is in the past
 */
export const isPastDate = (date) => {
  if (!date) return false
  
  try {
    const dateObj = typeof date === 'string' ? new Date(date) : date
    if (!isValid(dateObj)) return false
    
    return isBefore(startOfDay(dateObj), startOfDay(new Date()))
  } catch (error) {
    console.error('Error checking if date is in past:', error)
    return false
  }
}

/**
 * Check if a date is a weekend (Saturday or Sunday)
 * @param {Date} date - Date to check
 * @returns {boolean} True if date is weekend
 */
export const isWeekend = (date) => {
  if (!date || !isValid(date)) return false
  const day = date.getDay()
  return day === 0 || day === 6 // Sunday = 0, Saturday = 6
}

/**
 * Get the minimum bookable date (tomorrow if today is Friday, otherwise today)
 * @returns {Date} Minimum bookable date
 */
export const getMinBookableDate = () => {
  const today = new Date()
  const tomorrow = addDays(today, 1)
  
  // If today is Friday (5), Saturday (6) or Sunday (0), return next Monday
  const dayOfWeek = today.getDay()
  if (dayOfWeek === 5) return addDays(today, 3) // Friday -> Monday
  if (dayOfWeek === 6) return addDays(today, 2) // Saturday -> Monday
  if (dayOfWeek === 0) return addDays(today, 1) // Sunday -> Monday
  
  // Otherwise return tomorrow
  return tomorrow
}

/**
 * Format date to Spanish long format
 * @param {Date|string} date - Date to format
 * @returns {string} Formatted date (e.g., "Lunes, 30 de Octubre de 2024")
 */
export const formatDateLong = (date) => {
  if (!date) return ''
  
  try {
    const dateObj = typeof date === 'string' ? new Date(date) : date
    if (!isValid(dateObj)) return ''
    
    return format(dateObj, "EEEE, d 'de' MMMM 'de' yyyy", { locale: es })
  } catch (error) {
    console.error('Error formatting date:', error)
    return ''
  }
}

export default {
  formatDate,
  formatTime,
  formatDateForAPI,
  isPastDate,
  isWeekend,
  getMinBookableDate,
  formatDateLong,
}

