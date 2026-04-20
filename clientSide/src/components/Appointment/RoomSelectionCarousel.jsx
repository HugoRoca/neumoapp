import { useRef, useEffect } from 'react'
import { ChevronLeft, ChevronRight, DoorOpen, MapPin } from 'lucide-react'

function scrollContainer(el, delta) {
  if (!el) return
  el.scrollBy({ left: delta, behavior: 'smooth' })
}

/**
 * Carrusel horizontal para elegir consultorio.
 * Touch: deslizamiento horizontal suave; flechas debajo en móvil para no recortar tarjetas.
 */
export default function RoomSelectionCarousel({
  rooms = [],
  selectedRoom,
  onSelectRoom,
  disabled = false,
}) {
  const scrollRef = useRef(null)

  useEffect(() => {
    if (!selectedRoom || !scrollRef.current) return
    const el = scrollRef.current.querySelector(`[data-room-id="${CSS.escape(String(selectedRoom))}"]`)
    el?.scrollIntoView({ behavior: 'smooth', inline: 'center', block: 'nearest' })
  }, [selectedRoom, rooms])

  if (!rooms.length) {
    return (
      <p className="rounded-lg border border-amber-100 bg-amber-50/80 px-3 py-2.5 text-sm text-amber-900">
        No hay consultorios disponibles para esta combinación hospital / especialidad.
      </p>
    )
  }

  return (
    <div className="w-full min-w-0 space-y-3">
      <div
        ref={scrollRef}
        role="radiogroup"
        aria-label="Seleccionar consultorio"
        className={[
          'flex snap-x snap-mandatory gap-3 overflow-x-auto scroll-smooth',
          'px-1 py-1 -mx-1 sm:mx-0 sm:px-0',
          'touch-pan-x overscroll-x-contain pb-1',
          '[-ms-overflow-style:none] [scrollbar-width:none] [&::-webkit-scrollbar]:hidden',
        ].join(' ')}
        style={{ WebkitOverflowScrolling: 'touch' }}
      >
        {rooms.map((room) => {
          const idStr = String(room.id)
          const selected = idStr === String(selectedRoom)
          const locationBits = [room.building, room.floor].filter(Boolean).join(' · ')

          return (
            <button
              key={room.id}
              type="button"
              role="radio"
              data-room-id={idStr}
              aria-checked={selected}
              disabled={disabled}
              onClick={() => onSelectRoom(idStr)}
              className={[
                'flex min-h-[132px] w-[min(100%,280px)] shrink-0 snap-start flex-col rounded-xl border-2 px-3 py-3 text-left transition-colors',
                'focus:outline-none focus-visible:ring-2 focus-visible:ring-primary-500 focus-visible:ring-offset-2',
                'disabled:opacity-50',
                selected
                  ? 'border-primary-500 bg-primary-50 shadow-md ring-1 ring-primary-200'
                  : 'border-gray-200 bg-white hover:border-primary-200 hover:bg-gray-50/80',
              ].join(' ')}
            >
              <div className="mb-2 flex items-start justify-between gap-2">
                <span className="flex min-w-0 items-center gap-1.5 font-semibold text-gray-900">
                  <DoorOpen className="h-4 w-4 shrink-0 text-primary-600" aria-hidden />
                  <span className="truncate" title={room.name}>
                    {room.name || 'Consultorio'}
                  </span>
                </span>
                {room.room_number != null && room.room_number !== '' && (
                  <span className="shrink-0 rounded-md bg-gray-100 px-2 py-0.5 text-xs font-medium text-gray-700">
                    N.º {room.room_number}
                  </span>
                )}
              </div>

              {locationBits ? (
                <p className="mb-1 flex items-start gap-1 text-xs text-gray-600">
                  <MapPin className="mt-0.5 h-3.5 w-3.5 shrink-0 text-gray-400" aria-hidden />
                  <span>{locationBits}</span>
                </p>
              ) : null}

              {room.description ? (
                <p className="line-clamp-2 text-xs leading-relaxed text-gray-500" title={room.description}>
                  {room.description}
                </p>
              ) : (
                <p className="text-xs text-gray-400">Consultorio médico</p>
              )}
            </button>
          )
        })}
      </div>

      <div className="flex flex-col items-stretch gap-2 sm:flex-row sm:items-center sm:justify-between">
        <span className="order-2 text-center text-[11px] font-medium uppercase tracking-wide text-gray-500 sm:order-1 sm:text-left">
          Desliza horizontalmente o usa las flechas
        </span>
        <div className="order-1 flex justify-center gap-4 sm:order-2 sm:justify-end">
          <button
            type="button"
            aria-label="Consultorios anteriores"
            className="rounded-xl border border-gray-200 bg-white p-2.5 text-gray-700 shadow-sm transition-colors hover:border-primary-300 hover:bg-primary-50 hover:text-primary-800 focus:outline-none focus-visible:ring-2 focus-visible:ring-primary-500 active:scale-95"
            onClick={() => scrollContainer(scrollRef.current, -Math.min(300, typeof window !== 'undefined' ? window.innerWidth * 0.85 : 280))}
          >
            <ChevronLeft className="h-5 w-5" aria-hidden />
          </button>
          <button
            type="button"
            aria-label="Siguientes consultorios"
            className="rounded-xl border border-gray-200 bg-white p-2.5 text-gray-700 shadow-sm transition-colors hover:border-primary-300 hover:bg-primary-50 hover:text-primary-800 focus:outline-none focus-visible:ring-2 focus-visible:ring-primary-500 active:scale-95"
            onClick={() => scrollContainer(scrollRef.current, Math.min(300, typeof window !== 'undefined' ? window.innerWidth * 0.85 : 280))}
          >
            <ChevronRight className="h-5 w-5" aria-hidden />
          </button>
        </div>
      </div>
    </div>
  )
}
