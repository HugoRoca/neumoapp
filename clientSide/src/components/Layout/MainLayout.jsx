import { useState, useEffect } from 'react'
import { Link, useLocation, useNavigate, Outlet } from 'react-router-dom'
import { useAuth } from '@/context/AuthContext'
import {
  Home,
  List,
  Calendar,
  MessageCircle,
  LogOut,
  User,
  Menu,
  X,
  Sparkles,
} from 'lucide-react'
import UserProfileModal from '@/components/Layout/UserProfileModal'

/**
 * Shell principal: sidebar (desktop) + barra móvil + contenido.
 * Estilo tipo portal clínico: sidebar claro, CTA “Agendar cita”.
 */
const MainLayout = () => {
  const { logout } = useAuth()
  const location = useLocation()
  const navigate = useNavigate()
  /** El chat necesita altura fija al viewport; otras rutas siguen pudiendo hacer scroll en el documento. */
  const assistantViewportLock = location.pathname === '/asistente'
  const [mobileOpen, setMobileOpen] = useState(false)
  const [profileOpen, setProfileOpen] = useState(false)

  useEffect(() => {
    setMobileOpen(false)
  }, [location.pathname])

  const handleLogout = () => {
    logout()
    navigate('/login')
  }

  const mainLinks = [
    { path: '/dashboard', icon: Home, label: 'Inicio' },
    { path: '/mis-citas', icon: List, label: 'Mis citas' },
    { path: '/asistente', icon: MessageCircle, label: 'Asistente', assistant: true },
  ]

  const linkClass = (path, { assistant } = {}) => {
    const active = location.pathname === path
    if (assistant) {
      return [
        'flex items-center gap-3 rounded-2xl px-3 py-2.5 text-sm font-semibold transition-all',
        active
          ? 'bg-gradient-to-r from-primary-600 to-sky-600 text-white shadow-md ring-1 ring-primary-400/30'
          : 'bg-gradient-to-r from-sky-500 to-primary-600 text-white shadow-sm hover:brightness-105',
      ].join(' ')
    }
    return [
      'flex items-center gap-3 rounded-2xl px-3 py-2.5 text-sm font-medium transition-colors',
      active
        ? 'bg-white text-primary-900 shadow-sm ring-1 ring-slate-200/80'
        : 'text-slate-600 hover:bg-white/60 hover:text-slate-900',
    ].join(' ')
  }

  const SidebarContent = ({ onNavigate } = {}) => (
    <div className="flex min-h-0 flex-1 flex-col">
      <div className="px-4 pb-4 pt-6 lg:pt-8">
        <Link
          to="/dashboard"
          onClick={() => onNavigate?.()}
          className="block font-bold tracking-tight text-primary-700"
        >
          <span className="text-xl">Neumoapp</span>
        </Link>
        <p className="mt-1 text-xs font-medium text-slate-500">Portal del paciente</p>
        <Link
          to="/agendar-cita"
          onClick={() => onNavigate?.()}
          className="mt-4 flex w-full items-center justify-center gap-2 rounded-full bg-primary-600 px-4 py-3 text-sm font-semibold text-white shadow-md shadow-primary-600/25 transition hover:bg-primary-700"
        >
          <Calendar className="h-4 w-4 shrink-0" aria-hidden />
          Agendar cita
        </Link>
      </div>

      <nav className="flex flex-col gap-1 px-3 pb-4" aria-label="Principal">
        {mainLinks.map(({ path, icon: Icon, label, assistant }) => (
          <Link
            key={path}
            to={path}
            onClick={() => onNavigate?.()}
            className={linkClass(path, { assistant })}
          >
            {assistant ? (
              <Sparkles className="h-4 w-4 shrink-0 opacity-90" aria-hidden />
            ) : (
              <Icon className="h-5 w-5 shrink-0 opacity-90" aria-hidden />
            )}
            {label}
          </Link>
        ))}
      </nav>

      <div className="mt-auto border-t border-slate-200/80 px-4 py-5">
        <button
          type="button"
          onClick={() => {
            onNavigate?.()
            handleLogout()
          }}
          className="flex w-full items-center justify-center gap-2 rounded-2xl border border-slate-200/90 bg-white/80 py-2.5 text-sm font-medium text-slate-600 transition hover:bg-white hover:text-slate-900"
        >
          <LogOut className="h-4 w-4" aria-hidden />
          Cerrar sesión
        </button>
      </div>
    </div>
  )

  return (
    <div
      className={
        assistantViewportLock
          ? 'flex h-[100dvh] max-h-[100dvh] min-h-0 w-full overflow-hidden bg-slate-100'
          : 'flex min-h-[100dvh] bg-slate-100'
      }
    >
      {/* Desktop sidebar */}
      <aside
        className="fixed inset-y-0 left-0 z-30 hidden w-64 flex-col border-r border-slate-200/90 bg-gradient-to-b from-indigo-50/90 via-slate-50 to-slate-100/95 shadow-sm lg:flex"
        aria-label="Navegación"
      >
        <SidebarContent />
      </aside>

      {/* Mobile overlay */}
      {mobileOpen ? (
        <button
          type="button"
          className="fixed inset-0 z-40 bg-slate-900/40 backdrop-blur-[2px] lg:hidden"
          aria-label="Cerrar menú"
          onClick={() => setMobileOpen(false)}
        />
      ) : null}

      {/* Mobile drawer: scroll interno para ver “Cerrar sesión” */}
      <aside
        className={`fixed inset-y-0 left-0 z-50 flex w-[min(18rem,88vw)] max-w-[100vw] flex-col border-r border-slate-200/90 bg-gradient-to-b from-indigo-50/95 via-slate-50 to-slate-100 shadow-2xl transition-transform duration-200 ease-out lg:hidden ${
          mobileOpen ? 'translate-x-0' : '-translate-x-full'
        }`}
        aria-hidden={!mobileOpen}
      >
        <div className="flex h-14 shrink-0 items-center justify-end border-b border-slate-200/80 px-3">
          <button
            type="button"
            className="rounded-xl p-2 text-slate-600 hover:bg-white/80"
            onClick={() => setMobileOpen(false)}
            aria-label="Cerrar"
          >
            <X className="h-6 w-6" />
          </button>
        </div>
        <div className="min-h-0 flex-1 overflow-y-auto overscroll-contain">
          <SidebarContent onNavigate={() => setMobileOpen(false)} />
        </div>
      </aside>

      <div
        className={`flex min-h-0 min-w-0 flex-1 flex-col lg:pl-64 ${
          assistantViewportLock ? 'overflow-hidden' : ''
        }`}
      >
        {/* Mobile top bar */}
        <header className="sticky top-0 z-20 flex items-center justify-between gap-3 border-b border-slate-200/80 bg-white/95 px-4 py-3 backdrop-blur-sm lg:hidden">
          <button
            type="button"
            className="rounded-xl p-2 text-slate-700 hover:bg-slate-100"
            onClick={() => setMobileOpen(true)}
            aria-expanded={mobileOpen}
            aria-label="Abrir menú"
          >
            <Menu className="h-6 w-6" />
          </button>
          <Link to="/dashboard" className="min-w-0 flex-1 text-center">
            <span className="text-lg font-bold text-primary-700">Neumoapp</span>
          </Link>
          <button
            type="button"
            onClick={() => setProfileOpen(true)}
            className="flex h-9 w-9 shrink-0 items-center justify-center rounded-full bg-primary-100 text-primary-700 transition hover:bg-primary-200"
            aria-label="Mi cuenta"
          >
            <User className="h-4 w-4" aria-hidden />
          </button>
        </header>

        <main
          className={`flex min-h-0 min-w-0 flex-1 flex-col bg-slate-100 ${
            assistantViewportLock ? 'overflow-hidden' : ''
          }`}
        >
          <Outlet context={{ openUserProfile: () => setProfileOpen(true) }} />
        </main>
      </div>

      <UserProfileModal open={profileOpen} onClose={() => setProfileOpen(false)} onLogout={handleLogout} />
    </div>
  )
}

export default MainLayout
