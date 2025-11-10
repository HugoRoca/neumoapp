import { useEffect } from 'react'
import { BrowserRouter as Router, Routes, Route, Navigate, useNavigate, Outlet } from 'react-router-dom'
import { Toaster } from 'sonner'
import { AuthProvider, useAuth } from './context/AuthContext'
import ProtectedRoute from './components/ProtectedRoute'
import MainLayout from './components/Layout/MainLayout'

// Pages
import Login from './pages/Login'
import Dashboard from './pages/Dashboard'
import BookAppointment from './pages/BookAppointment'
import MyAppointments from './pages/MyAppointments'

const AppContent = () => {
  const { logout } = useAuth()
  const navigate = useNavigate()

  useEffect(() => {
    const handleLogout = () => {
      logout()
      navigate('/login')
    }

    window.addEventListener('logout', handleLogout)

    return () => {
      window.removeEventListener('logout', handleLogout)
    }
  }, [logout, navigate])

  return (
    <div className="min-h-screen bg-gray-50">
      <Routes>
        {/* Public Route */}
        <Route path="/login" element={<Login />} />
        
        {/* Protected Routes */}
        <Route 
          element={
            <ProtectedRoute>
              <MainLayout>
                <Outlet />
              </MainLayout>
            </ProtectedRoute>
          }
        >
          <Route path="/dashboard" element={<Dashboard />} />
          <Route path="/agendar-cita" element={<BookAppointment />} />
          <Route path="/mis-citas" element={<MyAppointments />} />
          <Route path="/" element={<Navigate to="/dashboard" replace />} />
        </Route>
        
        {/* 404 - Redirect to dashboard */}
        <Route path="*" element={<Navigate to="/dashboard" replace />} />
      </Routes>
      
      {/* Toast notifications */}
      <Toaster position="top-right" richColors />
    </div>
  )
}

function App() {
  return (
    <AuthProvider>
      <Router>
        <AppContent />
      </Router>
    </AuthProvider>
  )
}

export default App

