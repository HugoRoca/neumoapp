/**
 * Mascota del asistente: pulmones estilizados con cara grande y ojos muy visibles.
 * `thinking`: animación más viva + puntos tipo cómic.
 */
export default function AssistantRobot({ thinking = false, className = '', size = 'md' }) {
  const scale = size === 'sm' ? 0.48 : size === 'lg' ? 0.88 : 0.66
  const pairClass = thinking ? 'animate-robot-think' : 'animate-lung-breathe'

  return (
    <div
      className={`relative select-none ${className}`}
      style={{ width: 100 * scale, height: 132 * scale }}
      aria-hidden
    >
      {thinking ? (
        <div className="absolute -top-10 left-1/2 z-10 flex -translate-x-1/2 gap-1 rounded-2xl border border-rose-200/90 bg-white px-2.5 py-1.5 shadow-md">
          <span className="inline-block h-2 w-2 animate-robot-dot rounded-full bg-rose-500 [animation-delay:0ms]" />
          <span className="inline-block h-2 w-2 animate-robot-dot rounded-full bg-rose-400 [animation-delay:200ms]" />
          <span className="inline-block h-2 w-2 animate-robot-dot rounded-full bg-rose-300 [animation-delay:400ms]" />
        </div>
      ) : null}

      <div className={`${pairClass} origin-[50px_62px]`}>
        <svg
          viewBox="0 0 100 132"
          className="h-full w-full drop-shadow-[0_8px_16px_rgba(225,29,72,0.2)]"
          fill="none"
          xmlns="http://www.w3.org/2000/svg"
        >
          <defs>
            <linearGradient id="lungGradL" x1="0" y1="24" x2="46" y2="120" gradientUnits="userSpaceOnUse">
              <stop stopColor="#fda4af" />
              <stop offset="0.5" stopColor="#fb7185" />
              <stop offset="1" stopColor="#e11d48" />
            </linearGradient>
            <linearGradient id="lungGradR" x1="100" y1="24" x2="54" y2="120" gradientUnits="userSpaceOnUse">
              <stop stopColor="#fda4af" />
              <stop offset="0.5" stopColor="#fb7185" />
              <stop offset="1" stopColor="#e11d48" />
            </linearGradient>
            <linearGradient id="faceGrad" x1="18" y1="2" x2="82" y2="40" gradientUnits="userSpaceOnUse">
              <stop stopColor="#ffe4e6" />
              <stop offset="1" stopColor="#fda4af" />
            </linearGradient>
          </defs>

          {/* Cabeza / parte superior: zona clara para ojos grandes (no confundir con lóbulos) */}
          <rect
            x="16"
            y="2"
            width="68"
            height="38"
            rx="18"
            fill="url(#faceGrad)"
            stroke="#be123c"
            strokeWidth="1.1"
          />

          {/* Ojos grandes estilo caricatura */}
          <ellipse cx="36" cy="20" rx="10" ry="11" fill="white" stroke="#881337" strokeWidth="1" />
          <ellipse cx="64" cy="20" rx="10" ry="11" fill="white" stroke="#881337" strokeWidth="1" />
          {/* Brillo en ojos */}
          <ellipse cx="33" cy="17" rx="3" ry="3.5" fill="white" opacity="0.95" />
          <ellipse cx="61" cy="17" rx="3" ry="3.5" fill="white" opacity="0.95" />
          {/* Pupilas grandes */}
          <circle cx="37" cy="21" r="5.5" fill="#881337" className={thinking ? 'animate-pulse' : ''} />
          <circle cx="63" cy="21" r="5.5" fill="#881337" className={thinking ? 'animate-pulse' : ''} />
          <circle cx="38.5" cy="19.5" r="1.8" fill="#fbcfe8" opacity="0.9" />
          <circle cx="64.5" cy="19.5" r="1.8" fill="#fbcfe8" opacity="0.9" />

          {/* Cejas */}
          <path
            d={thinking ? 'M26 9 Q36 4 44 9' : 'M27 10 Q36 7 45 10'}
            stroke="#881337"
            strokeWidth="1.6"
            strokeLinecap="round"
            fill="none"
          />
          <path
            d={thinking ? 'M56 9 Q64 4 74 9' : 'M55 10 Q64 7 73 10'}
            stroke="#881337"
            strokeWidth="1.6"
            strokeLinecap="round"
            fill="none"
          />

          {/* Boca */}
          <path
            d={thinking ? 'M42 32 Q50 37 58 32' : 'M43 32 Q50 35 57 32'}
            stroke="#881337"
            strokeWidth="1.4"
            strokeLinecap="round"
            fill="none"
          />

          {/* Tráquea corta debajo de la cara */}
          <rect x="42" y="38" width="16" height="12" rx="4" fill="#fb7185" stroke="#be123c" strokeWidth="0.9" />

          {/* Bronquios */}
          <path
            d="M46 50 Q32 54 24 62"
            stroke="#be123c"
            strokeWidth="2.4"
            strokeLinecap="round"
            fill="none"
          />
          <path
            d="M54 50 Q68 54 76 62"
            stroke="#be123c"
            strokeWidth="2.4"
            strokeLinecap="round"
            fill="none"
          />

          {/* Pulmón izquierdo: lóbulo ancho, base redondeada, separación clara del derecho */}
          <path
            d="M 42 52
               L 38 52
               C 14 56, 4 72, 6 92
               C 8 110, 22 122, 34 118
               C 42 114, 46 98, 47 80
               C 48 64, 46 56, 42 52 Z"
            fill="url(#lungGradL)"
            stroke="#9f1239"
            strokeWidth="1"
            strokeLinejoin="round"
          />

          {/* Pulmón derecho */}
          <path
            d="M 58 52
               L 62 52
               C 86 56, 96 72, 94 92
               C 92 110, 78 122, 66 118
               C 58 114, 54 98, 53 80
               C 52 64, 54 56, 58 52 Z"
            fill="url(#lungGradR)"
            stroke="#9f1239"
            strokeWidth="1"
            strokeLinejoin="round"
          />

          {/* Líneas de costilla sugeridas (lectura “pulmonar”) */}
          <path
            d="M 22 78 Q 18 88 20 98"
            stroke="#be123c"
            strokeWidth="0.6"
            opacity="0.35"
            fill="none"
          />
          <path
            d="M 78 78 Q 82 88 80 98"
            stroke="#be123c"
            strokeWidth="0.6"
            opacity="0.35"
            fill="none"
          />

          {/* Brillo lóbulos */}
          <ellipse cx="26" cy="88" rx="10" ry="16" fill="white" opacity="0.1" />
          <ellipse cx="74" cy="88" rx="10" ry="16" fill="white" opacity="0.1" />
        </svg>
      </div>
    </div>
  )
}
