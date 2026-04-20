import { useEffect, useState } from 'react'
import { useAuth } from '@/context/AuthContext'
import { format } from 'date-fns'
import { es } from 'date-fns/locale'
import { User, Mail, Phone, MapPin, Hash, Calendar, LogOut, X, Activity, Users } from 'lucide-react'
import { formatDate } from '@/utils/dateUtils'

function Row({ icon: Icon, label, value, children }) {
  return (
    <div className="flex gap-3 border-b border-slate-100 py-3 last:border-0">
      <span className="mt-0.5 flex h-9 w-9 shrink-0 items-center justify-center rounded-xl bg-slate-100 text-slate-600">
        <Icon className="h-4 w-4" aria-hidden />
      </span>
      <div className="min-w-0 flex-1">
        <p className="text-xs font-medium uppercase tracking-wide text-slate-500">{label}</p>
        <div className="mt-0.5 text-sm font-medium text-slate-900">{children ?? value ?? '—'}</div>
      </div>
    </div>
  )
}

/**
 * Modal con datos del paciente desde GET /auth/me (refresh al abrir).
 */
export default function UserProfileModal({ open, onClose, onLogout }) {
  const { user, refreshProfile } = useAuth()
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)

  useEffect(() => {
    if (!open) {
      setError(null)
      return
    }
    let cancelled = false
    setLoading(true)
    setError(null)
    refreshProfile()
      .then(() => {
        if (!cancelled) setLoading(false)
      })
      .catch((e) => {
        if (!cancelled) {
          setError(e.response?.data?.detail || e.message || 'No se pudo cargar tu perfil')
          setLoading(false)
        }
      })
    return () => {
      cancelled = true
    }
  }, [open, refreshProfile])

  if (!open) return null

  const genderLabel =
    user?.gender === 'M' ? 'Masculino' : user?.gender === 'F' ? 'Femenino' : user?.gender ?? '—'

  let createdLabel = '—'
  if (user?.created_at) {
    try {
      createdLabel = format(new Date(user.created_at), "d MMM yyyy, HH:mm", { locale: es })
    } catch {
      createdLabel = String(user.created_at)
    }
  }

  return (
    <div className="fixed inset-0 z-[100] flex items-end justify-center sm:items-center sm:p-4" role="dialog" aria-modal="true" aria-labelledby="profile-modal-title">
      <button type="button" className="absolute inset-0 bg-slate-900/50 backdrop-blur-[1px]" aria-label="Cerrar" onClick={onClose} />

      <div className="relative flex max-h-[min(92dvh,720px)] w-full max-w-lg flex-col overflow-hidden rounded-t-3xl bg-white shadow-2xl ring-1 ring-slate-200/80 sm:rounded-3xl">
        <div className="flex shrink-0 items-center justify-between border-b border-slate-100 px-5 py-4">
          <div className="flex items-center gap-3">
            <span className="flex h-11 w-11 items-center justify-center rounded-2xl bg-primary-100 text-primary-700">
              <User className="h-6 w-6" aria-hidden />
            </span>
            <div>
              <h2 id="profile-modal-title" className="text-lg font-semibold text-slate-900">
                Mi cuenta
              </h2>
              <p className="text-xs text-slate-500">Datos según el registro en el sistema</p>
            </div>
          </div>
          <button
            type="button"
            onClick={onClose}
            className="rounded-xl p-2 text-slate-500 hover:bg-slate-100 hover:text-slate-800"
            aria-label="Cerrar ventana"
          >
            <X className="h-5 w-5" />
          </button>
        </div>

        <div className="min-h-0 flex-1 overflow-y-auto px-5 pb-4">
          {loading && (
            <div className="flex flex-col items-center justify-center py-12 text-slate-500">
              <div className="h-9 w-9 animate-spin rounded-full border-2 border-primary-600 border-t-transparent" />
              <p className="mt-3 text-sm">Actualizando tu información…</p>
            </div>
          )}

          {!loading && error && (
            <div className="rounded-2xl border border-red-200 bg-red-50 px-4 py-3 text-sm text-red-800">{error}</div>
          )}

          {!loading && !error && user && (
            <div className="pt-2">
              <Row icon={User} label="Nombre completo">
                {[user.first_name ?? user.firstname, user.last_name ?? user.lastname].filter(Boolean).join(' ') ||
                  '—'}
              </Row>
              <Row icon={Hash} label="Documento" value={user.document_number} />
              <Row icon={Mail} label="Correo electrónico" value={user.email} />
              <Row icon={Phone} label="Teléfono" value={user.phone || '—'} />
              <Row icon={MapPin} label="Dirección" value={user.address || '—'} />
              <Row icon={Calendar} label="Fecha de nacimiento">
                {user.birth_date ? formatDate(user.birth_date) : '—'}
              </Row>
              <Row icon={Users} label="Género">
                {genderLabel}
              </Row>
              <Row icon={Activity} label="Estado de la cuenta">
                {user.active !== false ? 'Activo' : 'Inactivo'}
              </Row>
              <Row icon={Calendar} label="Registro">
                {createdLabel}
              </Row>
            </div>
          )}
        </div>

        <div className="shrink-0 space-y-2 border-t border-slate-100 bg-slate-50/80 px-5 py-4">
          <button
            type="button"
            onClick={() => {
              onClose()
              onLogout()
            }}
            className="flex w-full items-center justify-center gap-2 rounded-full border border-red-200 bg-white py-3 text-sm font-semibold text-red-700 shadow-sm transition hover:bg-red-50"
          >
            <LogOut className="h-4 w-4" aria-hidden />
            Cerrar sesión
          </button>
          <button
            type="button"
            onClick={onClose}
            className="w-full rounded-full py-2.5 text-sm font-medium text-slate-600 hover:bg-white"
          >
            Volver
          </button>
        </div>
      </div>
    </div>
  )
}
