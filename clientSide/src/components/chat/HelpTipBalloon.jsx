/**
 * Globo tipo cómic para mensajes de ayuda en el estado inicial del chat.
 */
export default function HelpTipBalloon({ title = '¿Necesitas ayuda?', subtitle, children, className = '' }) {
  return (
    <div className={`relative max-w-md ${className}`}>
      <div className="relative rounded-2xl border-2 border-primary-200/90 bg-gradient-to-br from-white via-primary-50/90 to-cyan-50/80 px-5 py-4 shadow-xl shadow-primary-600/10 ring-1 ring-white/70">
        <p className="text-[11px] font-bold uppercase tracking-wider text-primary-600">Ayuda</p>
        <p className="mt-1 text-lg font-bold tracking-tight text-gray-900">{title}</p>
        {subtitle ? (
          <p className="mt-2 text-sm leading-relaxed text-gray-600">{subtitle}</p>
        ) : null}
        {children}
      </div>
      {/* Cola del globo (apunta hacia el robot en desktop) */}
      <div className="absolute -bottom-2 left-1/2 z-0 -translate-x-1/2 sm:left-[42%]" aria-hidden>
        <div className="h-4 w-4 rotate-45 border-b-2 border-r-2 border-primary-200/90 bg-gradient-to-br from-primary-50 to-cyan-50 shadow-sm" />
      </div>
    </div>
  )
}
