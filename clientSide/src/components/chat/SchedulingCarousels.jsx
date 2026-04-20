import { useCallback, useEffect, useMemo, useRef, useState } from 'react'
import {
  ChevronLeft,
  ChevronRight,
  Building2,
  Stethoscope,
  DoorOpen,
  Sun,
  CalendarDays,
  Clock,
  Check,
} from 'lucide-react'
import hospitalService from '@/services/hospital.service'
import consultationRoomService from '@/services/consultationRoom.service'
import {
  upcomingWeekdayDateStrings,
  fetchAvailableSlotTimes,
  buildBookingSuggestionPhrase,
  formatDayLabel,
} from '@/services/slotsSuggestions.service'

const TOTAL_STEPS = 6

function scrollContainer(el, delta) {
  if (!el) return
  el.scrollBy({ left: delta, behavior: 'smooth' })
}

function CarouselRow({ title, icon: Icon, children, scrollRef }) {
  return (
    <div>
      <div className="mb-1 flex items-center justify-between gap-2">
        <span className="inline-flex items-center gap-1 text-[11px] font-medium uppercase tracking-wide text-gray-500">
          {Icon ? <Icon className="h-3.5 w-3.5" aria-hidden /> : null}
          {title}
        </span>
        <div className="flex gap-0.5">
          <button
            type="button"
            aria-label="Anterior"
            className="rounded p-1 text-gray-500 hover:bg-gray-200/80"
            onClick={() => scrollContainer(scrollRef?.current, -180)}
          >
            <ChevronLeft className="h-4 w-4" />
          </button>
          <button
            type="button"
            aria-label="Siguiente"
            className="rounded p-1 text-gray-500 hover:bg-gray-200/80"
            onClick={() => scrollContainer(scrollRef?.current, 180)}
          >
            <ChevronRight className="h-4 w-4" />
          </button>
        </div>
      </div>
      <div
        ref={scrollRef}
        className="flex snap-x snap-mandatory gap-2 overflow-x-auto pb-1 [-ms-overflow-style:none] [scrollbar-width:none] [&::-webkit-scrollbar]:hidden"
      >
        {children}
      </div>
    </div>
  )
}

function StepSummary({ label, value, onEdit }) {
  return (
    <div className="flex items-start gap-2 rounded-lg border border-gray-200/90 bg-white px-3 py-2 text-sm shadow-sm">
      <span className="mt-0.5 flex h-5 w-5 shrink-0 items-center justify-center rounded-full bg-primary-100 text-primary-700">
        <Check className="h-3 w-3" strokeWidth={2.5} aria-hidden />
      </span>
      <div className="min-w-0 flex-1">
        <span className="block text-[10px] font-semibold uppercase tracking-wide text-gray-500">{label}</span>
        <p className="truncate font-medium text-gray-900" title={value}>
          {value}
        </p>
      </div>
      <button
        type="button"
        className="shrink-0 rounded-md px-2 py-1 text-xs font-medium text-primary-600 hover:bg-primary-50"
        onClick={onEdit}
      >
        Cambiar
      </button>
    </div>
  )
}

const STEP_TITLES = ['Hospital', 'Especialidad', 'Consultorio', 'Turno', 'Día', 'Horario']

/**
 * Asistente por pasos: solo se muestra un carrusel activo; lo anterior queda resumido.
 */
export default function SchedulingCarousels({ onSuggestionPick, disabled }) {
  const [hospitals, setHospitals] = useState([])
  const [specialties, setSpecialties] = useState([])
  const [rooms, setRooms] = useState([])
  const [loadingH, setLoadingH] = useState(true)
  const [loadingS, setLoadingS] = useState(false)
  const [loadingR, setLoadingR] = useState(false)

  const [hospitalId, setHospitalId] = useState('')
  const [specialtyId, setSpecialtyId] = useState('')
  const [roomId, setRoomId] = useState('')
  const [shift, setShift] = useState('')

  const dateOptions = useMemo(() => upcomingWeekdayDateStrings(8), [])
  const [selectedDate, setSelectedDate] = useState(() => dateOptions[0] ?? '')
  const [times, setTimes] = useState([])
  const [loadingTimes, setLoadingTimes] = useState(false)
  /** Hora elegida en el paso 6 (misma marca visual que hospital, día, etc.). */
  const [selectedTimeKey, setSelectedTimeKey] = useState('')

  /** Paso visible (1–6). */
  const [step, setStep] = useState(1)

  const refH = useRef(null)
  const refS = useRef(null)
  const refR = useRef(null)
  const refSh = useRef(null)
  const refD = useRef(null)
  const refT = useRef(null)

  const goToEdit = useCallback((fromStep) => {
    setSelectedTimeKey('')
    if (fromStep === 1) {
      setHospitalId('')
      setStep(1)
      return
    }
    if (fromStep === 2) {
      setSpecialtyId('')
      setRoomId('')
      setShift('')
      setStep(2)
      return
    }
    if (fromStep === 3) {
      setRoomId('')
      setShift('')
      setStep(3)
      return
    }
    if (fromStep === 4) {
      setShift('')
      setStep(4)
      return
    }
    if (fromStep === 5) {
      setStep(5)
      return
    }
  }, [])

  useEffect(() => {
    let c = true
    ;(async () => {
      try {
        setLoadingH(true)
        const data = await hospitalService.getHospitals(0, 50)
        const list = Array.isArray(data) ? data : []
        if (c) {
          setHospitals(list)
          if (list.length === 1) {
            setHospitalId(String(list[0].id))
            setStep(2)
          }
        }
      } catch {
        if (c) setHospitals([])
      } finally {
        if (c) setLoadingH(false)
      }
    })()
    return () => {
      c = false
    }
  }, [])

  useEffect(() => {
    if (!hospitalId) {
      setSpecialties([])
      setSpecialtyId('')
      return
    }
    let c = true
    ;(async () => {
      try {
        setLoadingS(true)
        const data = await hospitalService.getHospitalSpecialties(hospitalId)
        const list = Array.isArray(data) ? data : []
        if (c) {
          setSpecialties(list)
          setSpecialtyId('')
          setRooms([])
          setRoomId('')
          setShift('')
          setTimes([])
          if (list.length === 1) {
            setSpecialtyId(String(list[0].id))
            setStep(3)
          }
        }
      } catch {
        if (c) setSpecialties([])
      } finally {
        if (c) setLoadingS(false)
      }
    })()
    return () => {
      c = false
    }
  }, [hospitalId])

  useEffect(() => {
    if (!hospitalId || !specialtyId) {
      setRooms([])
      setRoomId('')
      return
    }
    let c = true
    ;(async () => {
      try {
        setLoadingR(true)
        const data = await consultationRoomService.getRoomsByHospitalAndSpecialty(hospitalId, specialtyId)
        if (c) {
          setRooms(Array.isArray(data) ? data : [])
          setRoomId('')
          setShift('')
          setTimes([])
        }
      } catch {
        if (c) setRooms([])
      } finally {
        if (c) setLoadingR(false)
      }
    })()
    return () => {
      c = false
    }
  }, [hospitalId, specialtyId])

  const selectedHospital = hospitals.find((h) => String(h.id) === String(hospitalId))
  const selectedSpecialty = specialties.find((s) => String(s.id) === String(specialtyId))
  const selectedRoom = rooms.find((r) => String(r.id) === String(roomId))

  const shiftLabel =
    shift === 'morning' ? 'Mañana (8:00–13:00)' : shift === 'afternoon' ? 'Tarde (14:00–18:00)' : ''

  useEffect(() => {
    setSelectedTimeKey('')
  }, [selectedDate, shift, roomId, specialtyId, hospitalId])

  useEffect(() => {
    if (!hospitalId || !specialtyId || !roomId || !shift || !selectedDate) {
      setTimes([])
      return
    }
    let c = true
    setLoadingTimes(true)
    ;(async () => {
      try {
        const list = await fetchAvailableSlotTimes(
          Number(hospitalId),
          Number(specialtyId),
          Number(roomId),
          shift,
          selectedDate
        )
        if (c) setTimes(list)
      } catch {
        if (c) setTimes([])
      } finally {
        if (c) setLoadingTimes(false)
      }
    })()
    return () => {
      c = false
    }
  }, [hospitalId, specialtyId, roomId, shift, selectedDate])

  useEffect(() => {
    if (selectedDate && !dateOptions.includes(selectedDate)) {
      setSelectedDate(dateOptions[0] ?? '')
    }
  }, [dateOptions, selectedDate])

  const selectedTimeLabel = useMemo(
    () => times.find((x) => x.key === selectedTimeKey)?.label || '',
    [times, selectedTimeKey]
  )

  const handlePickTime = useCallback(
    (timeKey) => {
      setSelectedTimeKey(timeKey)
      const phrase = buildBookingSuggestionPhrase({
        hospitalName: selectedHospital?.name,
        specialtyName: selectedSpecialty?.name,
        roomName: selectedRoom?.name || selectedRoom?.room_number,
        shift,
        dateIso: selectedDate,
        timeKey,
      })
      onSuggestionPick?.(phrase)
    },
    [selectedHospital, selectedSpecialty, selectedRoom, shift, selectedDate, onSuggestionPick]
  )

  if (loadingH && hospitals.length === 0) {
    return (
      <div className="border-t border-primary-100/50 bg-gradient-to-r from-slate-50/95 to-primary-50/20 px-3 py-3 text-center text-xs font-medium text-primary-700/80">
        Cargando hospitales…
      </div>
    )
  }

  if (!loadingH && hospitals.length === 0) {
    return null
  }

  const roomLabel = selectedRoom
    ? selectedRoom.name
      ? `${selectedRoom.name} (${selectedRoom.room_number})`
      : selectedRoom.room_number
    : ''

  return (
    <div className="border-t border-primary-100/60 bg-gradient-to-br from-slate-50/90 via-white to-cyan-50/30 px-2 py-3 sm:px-3">
      <div className="mx-auto max-w-5xl space-y-3 lg:max-w-[88rem] lg:px-2">
        <div className="flex items-center justify-between gap-2 rounded-xl border border-primary-100/50 bg-white/60 px-3 py-2.5 shadow-sm">
          <div>
            <p className="text-[11px] font-bold uppercase tracking-wider text-primary-600/90">Reserva guiada</p>
            <p className="text-sm text-gray-800">
              Paso {step} de {TOTAL_STEPS}:{' '}
              <span className="font-semibold text-primary-800">{STEP_TITLES[step - 1]}</span>
            </p>
          </div>
          <div className="h-2 w-28 overflow-hidden rounded-full bg-gray-200/90 shadow-inner">
            <div
              className="h-full rounded-full bg-gradient-to-r from-primary-500 to-cyan-500 transition-all duration-300"
              style={{ width: `${(step / TOTAL_STEPS) * 100}%` }}
            />
          </div>
        </div>

        {/* Resúmenes de pasos ya completados (solo lectura) */}
        <div className="space-y-1.5">
          {step >= 2 && hospitalId && selectedHospital && (
            <StepSummary label="Hospital" value={selectedHospital.name} onEdit={() => goToEdit(1)} />
          )}
          {step >= 3 && specialtyId && selectedSpecialty && (
            <StepSummary label="Especialidad" value={selectedSpecialty.name} onEdit={() => goToEdit(2)} />
          )}
          {step >= 4 && roomId && roomLabel && (
            <StepSummary label="Consultorio" value={roomLabel} onEdit={() => goToEdit(3)} />
          )}
          {step >= 5 && shift && (
            <StepSummary label="Turno" value={shiftLabel} onEdit={() => goToEdit(4)} />
          )}
          {step >= 6 && selectedDate && (
            <StepSummary
              label="Día"
              value={`${formatDayLabel(selectedDate)} (${selectedDate})`}
              onEdit={() => goToEdit(5)}
            />
          )}
          {step >= 6 && selectedTimeKey && selectedTimeLabel && (
            <StepSummary
              label="Hora"
              value={selectedTimeLabel}
              onEdit={() => {
                setSelectedTimeKey('')
                setStep(6)
              }}
            />
          )}
        </div>

        {/* Un solo carrusel activo */}
        {step === 1 && (
          <CarouselRow title="Elige hospital" icon={Building2} scrollRef={refH}>
            {hospitals.map((h) => {
              const active = String(h.id) === String(hospitalId)
              return (
                <button
                  key={h.id}
                  type="button"
                  disabled={disabled}
                  onClick={() => {
                    setHospitalId(String(h.id))
                    setStep(2)
                  }}
                  className={`shrink-0 snap-start rounded-full border px-3 py-1.5 text-left text-sm font-medium transition-colors ${
                    active
                      ? 'border-primary-500 bg-primary-50 text-primary-800'
                      : 'border-gray-200 bg-white text-gray-700 hover:border-primary-200'
                  } disabled:opacity-50`}
                >
                  {h.name}
                </button>
              )
            })}
          </CarouselRow>
        )}

        {step === 2 && (
          <CarouselRow title="Elige especialidad" icon={Stethoscope} scrollRef={refS}>
            {loadingS ? (
              <span className="py-2 text-xs text-gray-400">Cargando…</span>
            ) : (
              specialties.map((s) => {
                const active = String(s.id) === String(specialtyId)
                return (
                  <button
                    key={s.id}
                    type="button"
                    disabled={disabled || !hospitalId}
                    onClick={() => {
                      setSpecialtyId(String(s.id))
                      setStep(3)
                    }}
                    className={`max-w-[14rem] shrink-0 snap-start rounded-full border px-3 py-1.5 text-left text-sm font-medium transition-colors ${
                      active
                        ? 'border-primary-500 bg-primary-50 text-primary-800'
                        : 'border-gray-200 bg-white text-gray-700 hover:border-primary-200'
                    } disabled:opacity-50`}
                  >
                    {s.name}
                  </button>
                )
              })
            )}
          </CarouselRow>
        )}

        {step === 3 && (
          <CarouselRow title="Elige consultorio" icon={DoorOpen} scrollRef={refR}>
            {loadingR ? (
              <span className="py-2 text-xs text-gray-400">Cargando…</span>
            ) : rooms.length === 0 ? (
              <span className="py-2 text-xs text-amber-700">No hay consultorios para esta especialidad.</span>
            ) : (
              rooms.map((r) => {
                const active = String(r.id) === String(roomId)
                const label = r.name ? `${r.name} (${r.room_number})` : r.room_number
                return (
                  <button
                    key={r.id}
                    type="button"
                    disabled={disabled || !specialtyId}
                    onClick={() => {
                      setRoomId(String(r.id))
                      setStep(4)
                    }}
                    className={`max-w-[16rem] shrink-0 snap-start rounded-full border px-3 py-1.5 text-left text-sm font-medium transition-colors ${
                      active
                        ? 'border-primary-500 bg-primary-50 text-primary-800'
                        : 'border-gray-200 bg-white text-gray-700 hover:border-primary-200'
                    } disabled:opacity-50`}
                  >
                    {label}
                  </button>
                )
              })
            )}
          </CarouselRow>
        )}

        {step === 4 && (
          <CarouselRow title="Elige turno" icon={Sun} scrollRef={refSh}>
            {['morning', 'afternoon'].map((sh) => {
              const active = shift === sh
              const label = sh === 'morning' ? 'Mañana 8–13 h' : 'Tarde 14–18 h'
              return (
                <button
                  key={sh}
                  type="button"
                  disabled={disabled || !roomId}
                  onClick={() => {
                    setShift(sh)
                    setStep(5)
                  }}
                  className={`shrink-0 snap-start rounded-full border px-3 py-1.5 text-sm font-medium transition-colors ${
                    active
                      ? 'border-primary-500 bg-primary-50 text-primary-800'
                      : 'border-gray-200 bg-white text-gray-700 hover:border-primary-200'
                  } disabled:opacity-50`}
                >
                  {label}
                </button>
              )
            })}
          </CarouselRow>
        )}

        {step === 5 && (
          <CarouselRow title="Elige día" icon={CalendarDays} scrollRef={refD}>
            {dateOptions.map((iso) => {
              const active = iso === selectedDate
              return (
                <button
                  key={iso}
                  type="button"
                  disabled={disabled || !shift}
                  onClick={() => {
                    setSelectedDate(iso)
                    setStep(6)
                  }}
                  className={`shrink-0 snap-start rounded-full border px-3 py-1.5 text-left text-sm font-medium capitalize transition-colors ${
                    active
                      ? 'border-primary-500 bg-primary-50 text-primary-800'
                      : 'border-gray-200 bg-white text-gray-700 hover:border-primary-200'
                  } disabled:opacity-50`}
                >
                  {formatDayLabel(iso)}
                </button>
              )
            })}
          </CarouselRow>
        )}

        {step === 6 && (
          <CarouselRow title="Elige hora" icon={Clock} scrollRef={refT}>
            {loadingTimes ? (
              <span className="px-1 py-2 text-xs text-gray-400">Cargando horarios…</span>
            ) : times.length === 0 ? (
              <span className="px-1 py-2 text-xs text-gray-600">
                No hay horarios libres. Prueba otro día o pulsa &quot;Cambiar&quot; en el paso anterior.
              </span>
            ) : (
              times.map((t) => {
                const active = selectedTimeKey === t.key
                return (
                  <button
                    key={t.key}
                    type="button"
                    disabled={disabled}
                    onClick={() => handlePickTime(t.key)}
                    className={`shrink-0 snap-start rounded-lg border px-3 py-1.5 text-sm font-medium shadow-sm transition-colors disabled:opacity-50 ${
                      active
                        ? 'border-primary-500 bg-primary-50 text-primary-900 ring-1 ring-primary-200'
                        : 'border-gray-200 bg-white text-gray-800 hover:border-primary-300 hover:bg-primary-50/60'
                    }`}
                  >
                    {t.label}
                  </button>
                )
              })
            )}
          </CarouselRow>
        )}
      </div>
    </div>
  )
}
