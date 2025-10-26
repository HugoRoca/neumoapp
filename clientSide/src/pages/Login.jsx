import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { useAuth } from '@/context/AuthContext'
import { toast } from 'sonner'
import Input from '@/components/UI/Input'
import Button from '@/components/UI/Button'

/**
 * Login Page
 */
const Login = () => {
  const navigate = useNavigate()
  const { login, isAuthenticated } = useAuth()
  const [formData, setFormData] = useState({
    document_number: '',
    password: '',
  })
  const [loading, setLoading] = useState(false)

  // Redirect if already authenticated
  if (isAuthenticated) {
    navigate('/dashboard')
    return null
  }

  const handleChange = (e) => {
    setFormData({
      ...formData,
      [e.target.name]: e.target.value,
    })
  }

  const handleSubmit = async (e) => {
    e.preventDefault()
    setLoading(true)

    try {
      const result = await login(formData.document_number, formData.password)
      
      if (result.success) {
        toast.success('Inicio de sesión exitoso')
        navigate('/dashboard')
      } else {
        toast.error(result.error || 'Error al iniciar sesión')
      }
    } catch (error) {
      toast.error('Error al iniciar sesión')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-primary-50 to-primary-100 py-8 sm:py-12 px-4 sm:px-6 lg:px-8">
      <div className="max-w-md w-full space-y-6 sm:space-y-8">
        <div>
          <h2 className="mt-4 sm:mt-6 text-center text-3xl sm:text-4xl font-extrabold text-gray-900">
            Neumoapp
          </h2>
          <p className="mt-2 text-center text-xs sm:text-sm text-gray-600">
            Sistema de Reserva de Citas Médicas
          </p>
        </div>
        
        <div className="bg-white rounded-lg shadow-xl p-6 sm:p-8">
          <form className="space-y-5 sm:space-y-6" onSubmit={handleSubmit}>
            <Input
              label="Número de Documento (DNI)"
              type="text"
              name="document_number"
              value={formData.document_number}
              onChange={handleChange}
              placeholder="12345678"
              required
              maxLength={8}
            />
            
            <Input
              label="Contraseña"
              type="password"
              name="password"
              value={formData.password}
              onChange={handleChange}
              placeholder="••••••••"
              required
            />

            <Button
              type="submit"
              variant="primary"
              className="w-full"
              loading={loading}
              disabled={loading}
            >
              Iniciar Sesión
            </Button>
          </form>

          <div className="mt-6 text-center">
            <p className="text-xs sm:text-sm text-gray-600">
              Credenciales de prueba: <br className="sm:hidden" />
              <span className="font-mono font-semibold text-xs sm:text-sm">DNI: 12345678</span>
              <span className="hidden sm:inline"> | </span>
              <br className="sm:hidden" />
              <span className="font-mono font-semibold text-xs sm:text-sm">Password: password123</span>
            </p>
          </div>
        </div>
      </div>
    </div>
  )
}

export default Login

