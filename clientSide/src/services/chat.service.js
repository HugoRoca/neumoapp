import apiClient from './api.service'
import { API_CONFIG } from '@/config/api.config'

/**
 * Asistente IA — conversación con historial.
 * El backend exige JWT; el cliente ya adjunta Authorization.
 */
export const chatService = {
  /**
   * @param {string} message - último mensaje del usuario
   * @param {Array<{ role: 'user'|'assistant', content: string }>} history - mensajes previos (sin el actual)
   * @param {Record<string, unknown> | null} [wizardState] - estado del flujo guiado (Hospital→…→hora); lo devuelve el backend.
   * @param {Record<string, unknown> | null} [wizardSelection] - selección estructurada al pulsar un botón (no visible como comando).
   * @returns {Promise<{ response: string, hospitals?: Array<{ id: number, name: string }>, compose_context?: string, wizard_state?: object, quick_replies?: { step: string, prompt: string, options: Array<{ label: string, payload: object }> } }>}
   */
  sendMessage: async (message, history = [], wizardState = null, wizardSelection = null) => {
    const body = { message, history }
    if (wizardState != null && typeof wizardState === 'object') {
      body.wizard_state = wizardState
    }
    if (wizardSelection != null && typeof wizardSelection === 'object') {
      body.wizard_selection = wizardSelection
    }
    // Ollama/local puede tardar en el primer turno; evita falsos errores por timeout
    const response = await apiClient.post(API_CONFIG.ENDPOINTS.CHAT.BASE, body, { timeout: 120000 })
    return response.data
  },
}

export default chatService

/*
  Ejemplo de llamada directa (fetch) equivalente:

  const token = localStorage.getItem('neumoapp_token')
  const res = await fetch(`${import.meta.env.VITE_API_BASE_URL || 'http://localhost:3000'}/chat/`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      Authorization: `Bearer ${token}`,
    },
    body: JSON.stringify({
      message: '¿Qué citas tengo mañana?',
      history: [
        { role: 'user', content: 'Hola' },
        { role: 'assistant', content: '¡Hola! ¿En qué te ayudo con tus citas?' },
      ],
    }),
  })
  const data = await res.json()
  // data.response -> texto del asistente
*/
