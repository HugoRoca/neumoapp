import axios from 'axios'
import { API_CONFIG } from '@/config/api.config'
import { TOKEN_KEY, REFRESH_TOKEN_KEY } from '@/config/constants'
import authService from './auth.service'

let isRefreshing = false
let failedQueue = []

const processQueue = (error, token = null) => {
  failedQueue.forEach(prom => {
    if (error) {
      prom.reject(error)
    } else {
      prom.resolve(token)
    }
  })
  failedQueue = []
}

const apiClient = axios.create({
  baseURL: API_CONFIG.BASE_URL,
  timeout: API_CONFIG.TIMEOUT,
  headers: {
    'Content-Type': 'application/json',
  },
})

apiClient.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem(TOKEN_KEY)
    if (token) {
      config.headers.Authorization = `Bearer ${token}`
    }
    return config
  },
  (error) => {
    return Promise.reject(error)
  }
)

apiClient.interceptors.response.use(
  (response) => response,
  async (error) => {
    const originalRequest = error.config
    if (error.response?.status === 401 && !originalRequest._retry) {
      if (isRefreshing) {
        return new Promise((resolve, reject) => {
          failedQueue.push({ resolve, reject })
        })
        .then(token => {
          originalRequest.headers['Authorization'] = 'Bearer ' + token
          return apiClient(originalRequest)
        })
        .catch(err => {
          return Promise.reject(err)
        })
      }

      originalRequest._retry = true
      isRefreshing = true

      const refreshToken = localStorage.getItem(REFRESH_TOKEN_KEY)
      if (!refreshToken) {
        isRefreshing = false
        // Dispatch logout event
        window.dispatchEvent(new Event('logout'))
        return Promise.reject(error)
      }

      try {
        const { access_token: newAccessToken } = await authService.refreshToken(refreshToken)
        localStorage.setItem(TOKEN_KEY, newAccessToken)
        apiClient.defaults.headers.common['Authorization'] = `Bearer ${newAccessToken}`
        originalRequest.headers['Authorization'] = `Bearer ${newAccessToken}`
        processQueue(null, newAccessToken)
        return apiClient(originalRequest)
      } catch (refreshError) {
        processQueue(refreshError, null)
        localStorage.removeItem(TOKEN_KEY)
        localStorage.removeItem(REFRESH_TOKEN_KEY)
        localStorage.removeItem('neumoapp_user')
        // Dispatch logout event
        window.dispatchEvent(new Event('logout'))
        return Promise.reject(refreshError)
      } finally {
        isRefreshing = false
      }
    }
    return Promise.reject(error)
  }
)

export default apiClient

