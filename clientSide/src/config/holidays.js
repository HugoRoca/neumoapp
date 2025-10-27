/**
 * Holidays Configuration
 * Lista de días festivos en Perú
 */

/**
 * Feriados en Perú para 2025
 * Fuente: https://www.gob.pe/feriados
 */
export const HOLIDAYS_2025 = [
  { date: '2025-01-01', name: 'Año Nuevo' },
  { date: '2025-04-17', name: 'Jueves Santo' },
  { date: '2025-04-18', name: 'Viernes Santo' },
  { date: '2025-05-01', name: 'Día del Trabajo' },
  { date: '2025-06-29', name: 'San Pedro y San Pablo' },
  { date: '2025-07-28', name: 'Día de la Independencia' },
  { date: '2025-07-29', name: 'Fiestas Patrias' },
  { date: '2025-08-30', name: 'Santa Rosa de Lima' },
  { date: '2025-10-08', name: 'Combate de Angamos' },
  { date: '2025-11-01', name: 'Día de Todos los Santos' },
  { date: '2025-12-08', name: 'Inmaculada Concepción' },
  { date: '2025-12-09', name: 'Batalla de Ayacucho' },
  { date: '2025-12-25', name: 'Navidad' },
]

/**
 * Feriados para 2024 (por si hay citas hacia atrás en el tiempo)
 */
export const HOLIDAYS_2024 = [
  { date: '2024-01-01', name: 'Año Nuevo' },
  { date: '2024-03-28', name: 'Jueves Santo' },
  { date: '2024-03-29', name: 'Viernes Santo' },
  { date: '2024-05-01', name: 'Día del Trabajo' },
  { date: '2024-06-29', name: 'San Pedro y San Pablo' },
  { date: '2024-07-28', name: 'Día de la Independencia' },
  { date: '2024-07-29', name: 'Fiestas Patrias' },
  { date: '2024-08-30', name: 'Santa Rosa de Lima' },
  { date: '2024-10-08', name: 'Combate de Angamos' },
  { date: '2024-11-01', name: 'Día de Todos los Santos' },
  { date: '2024-12-08', name: 'Inmaculada Concepción' },
  { date: '2024-12-09', name: 'Batalla de Ayacucho' },
  { date: '2024-12-25', name: 'Navidad' },
]

/**
 * Obtiene todos los feriados configurados
 * @returns {Array} Lista de feriados con fecha y nombre
 */
export const getAllHolidays = () => {
  return HOLIDAYS_2025
}

/**
 * Obtiene los feriados de un año específico
 * @param {number} year - Año
 * @returns {Array} Lista de feriados del año
 */
export const getHolidaysByYear = () => {
  // Por ahora solo devolvemos 2025
  // Puedes descomentar el switch cuando agregues más años
  /*switch (year) {
    case 2024:
      return HOLIDAYS_2024
    case 2025:
      return HOLIDAYS_2025
    default:
      return []
  }*/

  return HOLIDAYS_2025
}

/**
 * Verifica si una fecha es feriado
 * @param {Date|string} date - Fecha a verificar
 * @returns {Object|null} Objeto con info del feriado o null si no es feriado
 */
export const isHoliday = (date) => {
  if (!date) return null
  
  let dateStr
  if (date instanceof Date) {
    // Formatear fecha local sin conversión de zona horaria
    const year = date.getFullYear()
    const month = String(date.getMonth() + 1).padStart(2, '0')
    const day = String(date.getDate()).padStart(2, '0')
    dateStr = `${year}-${month}-${day}`
  } else {
    dateStr = date.split('T')[0]
  }
  
  const allHolidays = getAllHolidays()
  return allHolidays.find(holiday => holiday.date === dateStr) || null
}

/**
 * Obtiene el nombre del feriado si existe
 * @param {Date|string} date - Fecha a verificar
 * @returns {string|null} Nombre del feriado o null
 */
export const getHolidayName = (date) => {
  const holiday = isHoliday(date)
  return holiday ? holiday.name : null
}

export default {
  HOLIDAYS_2024,
  HOLIDAYS_2025,
  getAllHolidays,
  getHolidaysByYear,
  isHoliday,
  getHolidayName,
}

