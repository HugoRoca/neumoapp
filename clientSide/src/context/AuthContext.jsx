import { createContext, useState, useEffect, useContext, useCallback } from 'react'
import { TOKEN_KEY, REFRESH_TOKEN_KEY, USER_KEY } from '@/config/constants'
import authService from '@/services/auth.service'

const AuthContext = createContext(null)

export const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(null)
  const [token, setToken] = useState(null)
  const [loading, setLoading] = useState(true)

  // Logout function - memoized to prevent recreating
  const logout = useCallback(() => {
    setUser(null)
    setToken(null)
    localStorage.removeItem(TOKEN_KEY)
    localStorage.removeItem(REFRESH_TOKEN_KEY)
    localStorage.removeItem(USER_KEY)
  }, [])

  // Initialize auth state from localStorage
  useEffect(() => {
    const initAuth = async () => {
      const storedToken = localStorage.getItem(TOKEN_KEY)
      const storedUser = localStorage.getItem(USER_KEY)

      if (storedToken && storedUser) {
        setToken(storedToken)
        setUser(JSON.parse(storedUser))
        
        // Verify token is still valid
        try {
          const profile = await authService.getProfile()
          setUser(profile)
          localStorage.setItem(USER_KEY, JSON.stringify(profile))
        } catch (error) {
          // Token is invalid, clear auth
          logout()
        }
      }
      
      setLoading(false)
    }

    initAuth()
  }, [logout])

  const login = async (document_number, password) => {
    try {
      const response = await authService.login(document_number, password)
      const { access_token, refresh_token } = response
      
      // Store tokens
      setToken(access_token)
      localStorage.setItem(TOKEN_KEY, access_token)
      localStorage.setItem(REFRESH_TOKEN_KEY, refresh_token)
      
      // Get and store user profile
      const profile = await authService.getProfile()
      setUser(profile)
      localStorage.setItem(USER_KEY, JSON.stringify(profile))
      
      return { success: true }
    } catch (error) {
      return {
        success: false,
        error: error.response?.data?.detail || 'Error al iniciar sesión',
      }
    }
  }

  const register = async (userData) => {
    try {
      await authService.register(userData)
      return { success: true }
    } catch (error) {
      return {
        success: false,
        error: error.response?.data?.detail || 'Error al registrar usuario',
      }
    }
  }

  const value = {
    user,
    token,
    loading,
    login,
    logout,
    register,
    isAuthenticated: !!token,
  }

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>
}

// eslint-disable-next-line react-refresh/only-export-components
export const useAuth = () => {
  const context = useContext(AuthContext)
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider')
  }
  return context
}

export default AuthContext

