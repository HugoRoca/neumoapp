import { useState, useEffect, useRef, useCallback } from 'react'
import { Link } from 'react-router-dom'
import { ChevronLeft, ChevronRight, ArrowRight } from 'lucide-react'

const SLIDES = [
  {
    id: 'agenda',
    badge: 'Neumología',
    badgeClass: 'bg-rose-100 text-rose-700 ring-rose-200/80',
    title: 'Agenda tu valoración en consulta externa',
    subtitle: 'Elige consultorio, turno y horario en pocos pasos.',
    to: '/agendar-cita',
    cta: 'Agendar ahora',
    panelClass: 'from-primary-100/90 via-cyan-50/80 to-white bg-gradient-to-br',
    art: (
      <div
        className="pointer-events-none absolute -right-8 -top-10 h-48 w-48 rounded-full bg-primary-400/20 blur-3xl"
        aria-hidden
      />
    ),
  },
  {
    id: 'assistant',
    badge: 'Nuevo',
    badgeClass: 'bg-amber-100 text-amber-800 ring-amber-200/80',
    title: 'Habla con el asistente y agenda sin complicaciones',
    subtitle: 'Pregunta por horarios y opciones como si hablaras con recepción.',
    to: '/asistente',
    cta: 'Abrir asistente',
    panelClass: 'from-indigo-50 via-white to-primary-50 bg-gradient-to-br',
    art: (
      <div
        className="pointer-events-none absolute -bottom-6 left-1/2 h-40 w-40 -translate-x-1/2 rounded-full bg-primary-300/25 blur-2xl"
        aria-hidden
      />
    ),
  },
]

const AUTOPLAY_MS = 6000
const SWIPE_THRESHOLD_PX = 48

/**
 * Carrusel “Te puede interesar”: autoplay, pausa en hover, swipe en táctil, bucle infinito.
 * Sin dependencias externas; respeta prefers-reduced-motion.
 */
export default function FeaturedCarousel() {
  const n = SLIDES.length
  const [index, setIndex] = useState(0)
  const [hoverPaused, setHoverPaused] = useState(false)
  const [tabHidden, setTabHidden] = useState(typeof document !== 'undefined' ? document.hidden : false)
  const [reduceMotion, setReduceMotion] = useState(false)

  const touchStartX = useRef(null)
  const suppressClickRef = useRef(false)

  useEffect(() => {
    if (typeof window === 'undefined' || !window.matchMedia) return
    const mq = window.matchMedia('(prefers-reduced-motion: reduce)')
    const apply = () => setReduceMotion(mq.matches)
    apply()
    mq.addEventListener('change', apply)
    return () => mq.removeEventListener('change', apply)
  }, [])

  useEffect(() => {
    const onVis = () => setTabHidden(document.hidden)
    document.addEventListener('visibilitychange', onVis)
    return () => document.removeEventListener('visibilitychange', onVis)
  }, [])

  const next = useCallback(() => {
    setIndex((i) => (i + 1) % n)
  }, [n])

  const prev = useCallback(() => {
    setIndex((i) => (i - 1 + n) % n)
  }, [n])

  const autoplayBlocked = reduceMotion || n <= 1 || hoverPaused || tabHidden

  useEffect(() => {
    if (autoplayBlocked) return
    const id = window.setInterval(next, AUTOPLAY_MS)
    return () => window.clearInterval(id)
  }, [autoplayBlocked, next, index])

  const onTouchStart = (e) => {
    touchStartX.current = e.touches[0].clientX
  }

  const onTouchEnd = (e) => {
    if (touchStartX.current == null) return
    const endX = e.changedTouches[0].clientX
    const dx = endX - touchStartX.current
    touchStartX.current = null
    if (Math.abs(dx) < SWIPE_THRESHOLD_PX) return
    suppressClickRef.current = true
    window.setTimeout(() => {
      suppressClickRef.current = false
    }, 400)
    if (dx > 0) prev()
    else next()
  }

  const onSlideClick = (e) => {
    if (suppressClickRef.current) {
      e.preventDefault()
    }
  }

  const transitionClass = reduceMotion
    ? 'transition-none'
    : 'transition-transform duration-500 ease-out motion-reduce:transition-none'

  return (
    <section className="min-w-0" aria-labelledby="featured-heading" aria-roledescription="carrusel">
      <div className="mb-3 flex items-end justify-between gap-3">
        <h2 id="featured-heading" className="text-lg font-semibold tracking-tight text-slate-900 sm:text-xl">
          Te puede interesar
        </h2>
        <div className="flex gap-1">
          <button
            type="button"
            onClick={prev}
            className="rounded-full border border-slate-200 bg-white p-2 text-slate-600 shadow-sm transition hover:bg-slate-50"
            aria-label="Diapositiva anterior"
          >
            <ChevronLeft className="h-4 w-4" />
          </button>
          <button
            type="button"
            onClick={next}
            className="rounded-full border border-slate-200 bg-white p-2 text-slate-600 shadow-sm transition hover:bg-slate-50"
            aria-label="Diapositiva siguiente"
          >
            <ChevronRight className="h-4 w-4" />
          </button>
        </div>
      </div>

      <div
        className="relative overflow-hidden rounded-3xl border border-slate-200/90 bg-white shadow-md shadow-slate-900/5 ring-1 ring-slate-100 touch-pan-y"
        onMouseEnter={() => setHoverPaused(true)}
        onMouseLeave={() => setHoverPaused(false)}
        onTouchStart={onTouchStart}
        onTouchEnd={onTouchEnd}
        role="region"
        aria-label="Promociones destacadas"
      >
        <div
          className={`flex ${transitionClass}`}
          style={{
            transform: `translate3d(-${(index * 100) / n}%, 0, 0)`,
            width: `${n * 100}%`,
          }}
        >
          {SLIDES.map((slide, i) => (
            <div
              key={slide.id}
              className="min-w-0 shrink-0"
              style={{ width: `${100 / n}%` }}
              aria-hidden={i !== index}
            >
              <Link
                to={slide.to}
                onClick={onSlideClick}
                className={`relative flex min-h-[150px] flex-col justify-end p-4 sm:min-h-[168px] sm:p-5 ${slide.panelClass}`}
              >
                {slide.art}
                <div className="relative max-w-lg">
                  <span
                    className={`inline-flex items-center rounded-full px-2.5 py-0.5 text-[11px] font-semibold ring-1 sm:px-3 sm:py-1 sm:text-xs ${slide.badgeClass}`}
                  >
                    {slide.badge}
                  </span>
                  <h3 className="mt-2 text-lg font-bold leading-snug text-slate-900 sm:text-xl">{slide.title}</h3>
                  <p className="mt-1.5 text-sm leading-relaxed text-slate-600">{slide.subtitle}</p>
                  <span className="mt-3 inline-flex items-center gap-2 rounded-full border-2 border-slate-900/15 bg-white/90 px-3 py-1.5 text-sm font-semibold text-slate-900 shadow-sm transition group-hover:bg-white sm:mt-4 sm:px-4 sm:py-2">
                    {slide.cta}
                    <ArrowRight className="h-4 w-4" aria-hidden />
                  </span>
                </div>
              </Link>
            </div>
          ))}
        </div>

        <div className="flex justify-center gap-2 pb-3 pt-0.5" role="tablist" aria-label="Seleccionar promoción">
          {SLIDES.map((s, i) => (
            <button
              key={s.id}
              type="button"
              role="tab"
              aria-selected={i === index}
              aria-label={`Promoción ${i + 1} de ${n}`}
              className={`h-2 rounded-full transition-all ${i === index ? 'w-8 bg-primary-600' : 'w-2 bg-slate-300 hover:bg-slate-400'}`}
              onClick={() => setIndex(i)}
            />
          ))}
        </div>
      </div>
    </section>
  )
}
