import { Link } from 'react-router-dom'
import { MessageCircle, Sparkles, ArrowRight } from 'lucide-react'

/**
 * Globo promocional en el home hacia el asistente de citas.
 */
export default function AssistantPromoBanner() {
  return (
    <div className="mb-8 max-w-5xl mx-auto">
      <Link
        to="/asistente"
        className="group relative flex flex-col gap-3 overflow-visible rounded-2xl border-2 border-primary-200/80 bg-gradient-to-br from-white via-primary-50/80 to-cyan-50/60 p-5 shadow-lg shadow-primary-600/10 ring-1 ring-white/80 transition-all hover:border-primary-400 hover:shadow-xl hover:shadow-primary-500/15 sm:flex-row sm:items-center sm:gap-6 sm:p-6"
      >
        <div className="absolute -right-1 -top-2 flex rotate-6 items-center gap-1 rounded-full bg-gradient-to-r from-amber-400 to-orange-500 px-3 py-1 text-[10px] font-bold uppercase tracking-wide text-white shadow-md sm:right-4 sm:top-3">
          <Sparkles className="h-3 w-3" aria-hidden />
          Nuevo
        </div>

        <div className="relative shrink-0 sm:pl-1">
          <div className="flex h-14 w-14 items-center justify-center rounded-2xl bg-gradient-to-br from-primary-500 to-cyan-600 text-white shadow-lg shadow-primary-500/30 sm:h-16 sm:w-16">
            <MessageCircle className="h-7 w-7 sm:h-8 sm:w-8" strokeWidth={2} />
          </div>
          {/* Cola del globo hacia el icono */}
          <div
            className="absolute -bottom-2 left-6 hidden h-4 w-4 rotate-45 border-b-2 border-r-2 border-primary-200/80 bg-gradient-to-br from-primary-50 to-white sm:block"
            aria-hidden
          />
        </div>

        <div className="min-w-0 flex-1">
          <p className="text-xs font-bold uppercase tracking-wider text-primary-600">Tu copiloto de salud pulmonar</p>
          <h2 className="mt-1 text-lg font-bold text-gray-900 sm:text-xl">
            Habla con el asistente y agenda citas sin complicaciones
          </h2>
          <p className="mt-2 text-sm leading-relaxed text-gray-600 sm:text-base">
            Pregunta por horarios, cancela o reserva en lenguaje natural — como chatear con recepción.
          </p>
        </div>

        <span className="inline-flex shrink-0 items-center justify-center gap-2 self-start rounded-xl bg-gradient-to-r from-primary-600 to-sky-600 px-4 py-3 text-sm font-semibold text-white shadow-md transition group-hover:brightness-105 sm:self-center">
          Probar asistente
          <ArrowRight className="h-4 w-4 transition group-hover:translate-x-0.5" aria-hidden />
        </span>
      </Link>
    </div>
  )
}
