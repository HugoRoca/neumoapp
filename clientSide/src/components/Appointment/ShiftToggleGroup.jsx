import { Sun, Sunset, Moon } from 'lucide-react'

const OPTIONS = [
  {
    value: 'morning',
    label: 'Mañana',
    hint: '8:00 – 13:00',
    Icon: Sun,
    disabled: false,
  },
  {
    value: 'afternoon',
    label: 'Tarde',
    hint: '14:00 – 18:00',
    Icon: Sunset,
    disabled: false,
  },
  /** El API actual solo admite morning/afternoon; se muestra para expectativa UX */
  {
    value: 'night',
    label: 'Noche',
    hint: 'Próximamente',
    Icon: Moon,
    disabled: true,
  },
]

/**
 * Grupo de botones tipo toggle para elegir un único turno (modalidad horaria).
 * Mañana y tarde son obligatorios para continuar; Noche queda deshabilitada hasta soporte en API.
 * @param {string} value - 'morning' | 'afternoon' | ''
 * @param {(next: string) => void} onChange
 * @param {boolean} [disabled]
 */
export default function ShiftToggleGroup({ value, onChange, disabled = false }) {
  return (
    <div
      className="grid grid-cols-1 gap-3 sm:grid-cols-3 sm:gap-3"
      role="radiogroup"
      aria-label="Turno de atención"
      aria-required="true"
    >
      {OPTIONS.map(({ value: v, label, hint, Icon, disabled: optionDisabled }) => {
        const selected = value === v
        const isDisabled = disabled || optionDisabled
        return (
          <button
            key={v}
            type="button"
            role="radio"
            aria-checked={selected}
            aria-disabled={isDisabled}
            disabled={isDisabled}
            onClick={() => !isDisabled && onChange(v)}
            className={`
              group relative flex flex-col items-start gap-1 rounded-2xl border-2 px-4 py-4 text-left transition-all
              focus:outline-none focus-visible:ring-2 focus-visible:ring-primary-500 focus-visible:ring-offset-2
              ${
                isDisabled
                  ? 'cursor-not-allowed border-dashed border-gray-200 bg-gray-50/80 opacity-75'
                  : ''
              }
              ${
                !isDisabled && selected
                  ? 'border-primary-500 bg-gradient-to-br from-primary-50 to-cyan-50/80 shadow-md ring-1 ring-primary-200'
                  : ''
              }
              ${
                !isDisabled && !selected
                  ? 'border-gray-200 bg-white hover:border-primary-300 hover:bg-primary-50/40 hover:shadow-sm'
                  : ''
              }
            `}
          >
            <span className="flex items-center gap-2">
              <span
                className={`flex h-10 w-10 items-center justify-center rounded-xl ${
                  isDisabled
                    ? 'bg-gray-200 text-gray-400'
                    : selected
                      ? 'bg-primary-500 text-white'
                      : 'bg-gray-100 text-primary-600 group-hover:bg-primary-100'
                }`}
              >
                <Icon className="h-5 w-5" aria-hidden />
              </span>
              <span>
                <span
                  className={`block text-base font-bold ${
                    isDisabled ? 'text-gray-500' : selected ? 'text-primary-900' : 'text-gray-900'
                  }`}
                >
                  {label}
                </span>
                <span className="text-sm text-gray-600">{hint}</span>
              </span>
            </span>
            {selected && !isDisabled && (
              <span className="absolute right-3 top-3 h-2.5 w-2.5 rounded-full bg-primary-500 shadow-sm" aria-hidden />
            )}
          </button>
        )
      })}
    </div>
  )
}
