import { useState, useRef, useEffect, useCallback } from 'react'
import Button from '@/components/UI/Button'
import {
  MessageCircle,
  Send,
  Loader2,
  User,
  Sparkles,
  Trash2,
  Stethoscope,
  Calendar,
  ListTodo,
} from 'lucide-react'
import { useAuth } from '@/context/AuthContext'
import chatService from '@/services/chat.service'
import { API_CONFIG } from '@/config/api.config'
import { toast } from 'sonner'
import AssistantRobot from '@/components/chat/AssistantRobot'
import HelpTipBalloon from '@/components/chat/HelpTipBalloon'

function newId() {
  return globalThis.crypto?.randomUUID?.() ?? `${Date.now()}-${Math.random().toString(36).slice(2)}`
}

function getChatErrorMessage(err) {
  const detail = err.response?.data?.detail
  if (detail != null) {
    if (typeof detail === 'string') return detail
    if (Array.isArray(detail)) {
      return detail.map((d) => (typeof d === 'object' ? d.msg || JSON.stringify(d) : String(d))).join(', ')
    }
    return String(detail)
  }
  if (err.code === 'ECONNABORTED' || err.message?.toLowerCase().includes('timeout')) {
    return (
      'Tiempo de espera agotado. Si usas Ollama, el primer mensaje puede tardar mucho; ' +
      'inténtalo de nuevo. Si persiste, revisa que el modelo esté cargado (ollama run …).'
    )
  }
  if (!err.response) {
    return (
      `No hay conexión con la API (${API_CONFIG.BASE_URL}). ` +
      '¿Está el backend en marcha? (p. ej. ./start-backend.sh)'
    )
  }
  return err.message || 'Error al contactar el asistente'
}

const SUGGESTIONS = [
  { label: 'Ver mis citas', text: '¿Qué citas tengo programadas?', icon: ListTodo },
  { label: 'Agendar mañana', text: 'Quiero agendar una cita mañana por la mañana', icon: Calendar },
  { label: 'Cancelar una cita', text: 'Quiero cancelar una cita, ¿cómo lo hago?', icon: Stethoscope },
]

/**
 * Ocupa todo el alto disponible bajo la navbar; solo la lista de mensajes hace scroll.
 */
const ChatAssistant = () => {
  const { user } = useAuth()
  const firstName = user?.firstname?.trim() || ''
  const [messages, setMessages] = useState([])
  const [input, setInput] = useState('')
  const [sending, setSending] = useState(false)
  /** Estado del wizard devuelto por el backend; se reenvía en cada POST hasta salir del flujo. */
  const [wizardState, setWizardState] = useState(null)
  const bottomRef = useRef(null)
  const textareaRef = useRef(null)

  const scrollToBottom = useCallback(() => {
    bottomRef.current?.scrollIntoView({ behavior: 'smooth', block: 'end' })
  }, [])

  useEffect(() => {
    scrollToBottom()
  }, [messages, sending, scrollToBottom])

  useEffect(() => {
    const el = textareaRef.current
    if (!el) return
    el.style.height = 'auto'
    el.style.height = `${Math.min(el.scrollHeight, 200)}px`
  }, [input])

  /**
   * Envía un mensaje. `overrideText`: texto del usuario (visible en el chat).
   * `options.wizardSelection`: payload estructurado al pulsar un botón (no se muestra como comando).
   */
  const submitMessage = async (overrideText, options = {}) => {
    const { wizardSelection = null } = options
    const raw = overrideText !== undefined ? overrideText : input
    const text = typeof raw === 'string' ? raw.trim() : ''
    if (!text || sending) return

    const historyForApi = messages.map(({ role, content }) => ({ role, content }))
    const userMsg = { id: newId(), role: 'user', content: text }
    setMessages((prev) => [...prev, userMsg])
    setInput('')
    setSending(true)
    textareaRef.current?.focus()

    try {
      const data = await chatService.sendMessage(text, historyForApi, wizardState, wizardSelection)
      const responseText = typeof data?.response === 'string' ? data.response : String(data ?? '')
      const hospitalQuickReplies =
        Array.isArray(data?.hospitals) && data.hospitals.length > 0 ? data.hospitals : undefined
      const quickReplies =
        data?.quick_replies &&
        Array.isArray(data.quick_replies.options) &&
        data.quick_replies.options.length > 0
          ? data.quick_replies
          : undefined
      setWizardState(data?.wizard_state ?? null)
      setMessages((prev) => [
        ...prev,
        {
          id: newId(),
          role: 'assistant',
          content: responseText,
          variant: 'default',
          hospitalQuickReplies,
          quickReplies,
          userIntentForQuickReply: text,
        },
      ])
    } catch (err) {
      const msg = getChatErrorMessage(err)
      toast.error(msg)
      setMessages((prev) => [
        ...prev,
        {
          id: newId(),
          role: 'assistant',
          variant: 'error',
          content:
            `${msg}\n\n(Si el fallo es de configuración: en service/.env usa OPENAI_API_KEY para OpenAI, o OPENAI_BASE_URL + OPENAI_CHAT_MODEL para Ollama local.)`,
        },
      ])
    } finally {
      setSending(false)
    }
  }

  const handleSend = (e) => {
    e?.preventDefault?.()
    void submitMessage()
  }

  const handleKeyDown = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      void submitMessage()
    }
  }

  const clearChat = () => {
    if (messages.length === 0) return
    if (!window.confirm('¿Borrar toda la conversación?')) return
    setMessages([])
    setWizardState(null)
    toast.success('Conversación vaciada')
    textareaRef.current?.focus()
  }

  const sendSuggestion = (text) => {
    void submitMessage(text)
  }

  return (
    <div className="relative flex min-h-0 flex-1 flex-col overflow-hidden px-3 py-2 sm:px-5 sm:py-4 lg:px-8">
      {/* Fondo decorativo */}
      <div className="pointer-events-none absolute inset-0 -z-10 overflow-hidden">
        <div className="absolute -right-24 top-0 h-80 w-80 rounded-full bg-gradient-to-br from-primary-400/35 to-cyan-300/20 blur-3xl" />
        <div className="absolute -left-20 bottom-10 h-72 w-72 rounded-full bg-gradient-to-tr from-sky-400/25 to-primary-300/20 blur-3xl" />
        <div className="absolute left-1/2 top-1/3 h-px w-[min(90%,48rem)] -translate-x-1/2 bg-gradient-to-r from-transparent via-primary-200/50 to-transparent" />
      </div>

      <div className="mx-auto flex min-h-0 w-full max-w-6xl flex-1 flex-col overflow-hidden lg:max-w-[88rem]">
        {/* Panel principal */}
        <div className="relative flex min-h-0 min-h-[70vh] flex-1 flex-col overflow-hidden rounded-3xl border border-primary-100/80 bg-white/85 shadow-xl shadow-primary-900/[0.06] ring-1 ring-white backdrop-blur-md sm:min-h-[76vh] lg:min-h-[78vh]">
          {/* Cabecera */}
          <header className="relative flex shrink-0 items-center justify-between gap-3 overflow-hidden border-b border-primary-100/60 bg-gradient-to-r from-primary-50/90 via-white to-cyan-50/80 px-3 py-3 sm:px-5 sm:py-4">
            <div className="absolute inset-0 bg-[radial-gradient(ellipse_80%_60%_at_100%_0%,rgba(14,165,233,0.12),transparent)]" aria-hidden />
            <div className="relative flex min-w-0 items-center gap-3">
              <div className="relative flex h-11 w-11 shrink-0 items-center justify-center sm:h-12 sm:w-12">
                <span className="absolute inset-0 rounded-2xl bg-gradient-to-br from-primary-500 via-sky-500 to-cyan-600 opacity-90 shadow-lg shadow-primary-500/30" />
                <span className="absolute inset-0 animate-chat-float rounded-2xl bg-gradient-to-br from-white/25 to-transparent" />
                <MessageCircle className="relative h-5 w-5 text-white drop-shadow sm:h-6 sm:w-6" strokeWidth={2.2} />
              </div>
              <div className="min-w-0">
                <div className="flex flex-wrap items-center gap-2">
                  <h1 className="truncate bg-gradient-to-r from-primary-800 via-primary-700 to-cyan-700 bg-clip-text text-lg font-bold tracking-tight text-transparent sm:text-xl">
                    Tu asistente de citas
                  </h1>
                  <span className="hidden shrink-0 rounded-full bg-gradient-to-r from-amber-400 to-orange-400 px-2 py-0.5 text-[10px] font-bold uppercase tracking-wide text-white shadow-sm sm:inline">
                    En vivo
                  </span>
                </div>
                <p className="truncate text-xs text-primary-900/70 sm:text-sm">
                  Habla natural: agenda, consulta o cancela sin formularios complicados
                </p>
              </div>
            </div>
            <Button
              type="button"
              variant="outline"
              size="sm"
              onClick={clearChat}
              disabled={messages.length === 0 || sending}
              className="relative shrink-0 border-primary-200/80 bg-white/80 hover:bg-primary-50"
            >
              <Trash2 className="h-4 w-4 sm:mr-1.5" />
              <span className="hidden sm:inline">Limpiar</span>
            </Button>
          </header>

          {/* Lista de mensajes; mascota pulmón integrada al cargar y decorativa cuando hay hilo */}
          <div className="custom-scrollbar relative min-h-0 flex-1 overflow-y-auto overscroll-contain bg-gradient-to-b from-slate-50/80 to-white/50">
            <div
              className={`mx-auto max-w-5xl space-y-4 px-3 py-4 sm:px-6 sm:py-5 lg:px-8 ${
                messages.length > 0 && !sending ? 'pb-16 sm:pb-20' : 'pb-6 sm:pb-8'
              }`}
            >
              {messages.length === 0 && !sending && (
                <div className="flex flex-col items-center px-2 pb-4 pt-2 text-center sm:pb-8 sm:pt-4">
                  <div className="mb-6 flex w-full max-w-4xl flex-col items-center gap-8 sm:mb-8 sm:flex-row sm:items-end sm:justify-center sm:gap-10">
                    <HelpTipBalloon
                      title="¿Por dónde empiezo?"
                      subtitle="Elige una tarjeta abajo o escribe lo que necesitas. Las opciones de clínica aparecen en el chat cuando correspondan."
                    />
                    <div className="relative shrink-0">
                      <div className="absolute -inset-6 rounded-full bg-primary-400/15 blur-2xl" aria-hidden />
                      <AssistantRobot size="lg" className="relative z-[1]" />
                    </div>
                  </div>
                  {firstName ? (
                    <p className="text-sm font-medium text-primary-800/90">Hola, {firstName}</p>
                  ) : null}
                  <h2 className="mt-2 max-w-md text-balance text-xl font-bold tracking-tight text-gray-900 sm:text-2xl">
                    ¿Qué necesitas{' '}
                    <span className="bg-gradient-to-r from-primary-600 to-cyan-600 bg-clip-text text-transparent">
                      hoy
                    </span>
                    ?
                  </h2>
                  <p className="mt-2 max-w-md text-pretty text-sm leading-relaxed text-gray-600 sm:text-base">
                    Toca una idea rápida o escribe abajo.
                  </p>
                  <div className="mt-8 grid w-full max-w-4xl gap-3 sm:grid-cols-3">
                    {SUGGESTIONS.map((s) => {
                      const Icon = s.icon
                      return (
                        <button
                          key={s.label}
                          type="button"
                          disabled={sending}
                          onClick={() => sendSuggestion(s.text)}
                          className="group relative flex w-full flex-col items-start gap-2 overflow-hidden rounded-2xl border border-gray-200/90 bg-white p-3.5 text-left shadow-md shadow-gray-200/50 transition-all hover:-translate-y-0.5 hover:border-primary-300 hover:shadow-lg hover:shadow-primary-500/10 enabled:cursor-pointer disabled:cursor-not-allowed disabled:opacity-50 sm:min-h-[5.5rem]"
                        >
                          <span className="flex h-9 w-9 items-center justify-center rounded-xl bg-gradient-to-br from-primary-100 to-cyan-100 text-primary-700 transition-transform group-hover:scale-105">
                            <Icon className="h-4 w-4 shrink-0" strokeWidth={2} />
                          </span>
                          <span className="text-sm font-semibold text-gray-800">{s.label}</span>
                          <span className="pointer-events-none absolute -right-6 -top-6 h-20 w-20 rounded-full bg-gradient-to-br from-primary-400/10 to-transparent opacity-0 transition-opacity group-hover:opacity-100" />
                        </button>
                      )
                    })}
                  </div>
                </div>
              )}

            {messages.map((m) => {
              const isUser = m.role === 'user'
              const isErr = m.variant === 'error'
              return (
                <div key={m.id} className={`flex gap-3 ${isUser ? 'flex-row-reverse' : 'flex-row'}`}>
                  <div
                    className={`flex h-8 w-8 shrink-0 items-center justify-center rounded-full shadow-sm ring-2 ring-white sm:h-9 sm:w-9 ${
                      isUser
                        ? 'bg-gradient-to-br from-primary-600 to-primary-800 text-white shadow-primary-500/20'
                        : isErr
                          ? 'bg-red-100 text-red-600 ring-red-50'
                          : 'border border-primary-100/80 bg-gradient-to-br from-white to-primary-50/50 text-primary-600 shadow-md'
                    }`}
                  >
                    {isUser ? <User className="h-3.5 w-3.5 sm:h-4 sm:w-4" /> : <Sparkles className="h-3.5 w-3.5 sm:h-4 sm:w-4" />}
                  </div>
                  <div className="flex min-w-0 max-w-[min(100%,42rem)] flex-1 flex-col gap-2">
                    <div
                      className={`rounded-2xl px-3.5 py-2.5 text-[15px] leading-relaxed shadow-md sm:px-4 sm:py-3 sm:text-base ${
                        isUser
                          ? 'rounded-tr-md bg-gradient-to-br from-primary-600 to-primary-700 text-white shadow-primary-600/15'
                          : isErr
                            ? 'rounded-tl-md border border-red-200/80 bg-red-50 text-red-900'
                            : 'rounded-tl-md border border-primary-100/60 bg-white text-gray-800 shadow-gray-200/50'
                      }`}
                    >
                      {!isUser && (
                        <span className={`mb-1 block text-xs font-medium ${isErr ? 'text-red-600' : 'text-primary-600'}`}>
                          {isErr ? 'Error' : 'Asistente'}
                        </span>
                      )}
                      {isUser && <span className="mb-1 block text-xs font-medium text-primary-100">Tú</span>}
                      <p className="whitespace-pre-wrap break-words">{m.content}</p>
                    </div>
                    {!isUser && !isErr && m.quickReplies?.options?.length > 0 ? (
                      <div className="flex flex-col gap-1.5">
                        {m.quickReplies.prompt?.trim() ? (
                          <span className="text-[11px] font-semibold uppercase tracking-wide text-primary-700">
                            {m.quickReplies.prompt}
                          </span>
                        ) : null}
                        <div className="flex flex-wrap gap-2">
                          {m.quickReplies.options.map((opt, idx) => (
                            <button
                              key={`${m.id}-qr-${idx}-${opt.label}`}
                              type="button"
                              disabled={sending}
                              onClick={() =>
                                void submitMessage(opt.label, { wizardSelection: opt.payload })
                              }
                              className="max-w-full rounded-full border border-primary-300 bg-gradient-to-r from-primary-50 to-white px-3 py-2 text-left text-xs font-semibold text-primary-900 shadow-sm transition hover:border-primary-500 hover:bg-primary-100/80 disabled:opacity-50 sm:text-sm"
                            >
                              {opt.label}
                            </button>
                          ))}
                        </div>
                      </div>
                    ) : null}
                    {!isUser && !isErr && !m.quickReplies && m.hospitalQuickReplies?.length > 0 ? (
                      <div className="flex flex-col gap-1.5">
                        <span className="text-[11px] font-semibold uppercase tracking-wide text-primary-700">
                          Elige clínica
                        </span>
                        <div className="flex flex-wrap gap-2">
                          {m.hospitalQuickReplies.map((h) => (
                            <button
                              key={`${m.id}-h-${h.id}`}
                              type="button"
                              disabled={sending}
                              onClick={() => {
                                const base = (m.userIntentForQuickReply || '').trim()
                                const composed = base
                                  ? `${base} en la clínica ${h.name}`
                                  : `Quiero agendar una cita en la clínica ${h.name}`
                                void submitMessage(composed)
                              }}
                              className="max-w-full rounded-full border border-primary-300 bg-gradient-to-r from-primary-50 to-white px-3 py-2 text-left text-xs font-semibold text-primary-900 shadow-sm transition hover:border-primary-500 hover:bg-primary-100/80 disabled:opacity-50 sm:text-sm"
                            >
                              {h.name}
                            </button>
                          ))}
                        </div>
                      </div>
                    ) : null}
                  </div>
                </div>
              )
            })}

            {sending ? (
              <div
                className="flex items-end gap-3 sm:gap-4"
                aria-live="polite"
                aria-busy="true"
                role="status"
              >
                <div className="relative shrink-0">
                  <div
                    className="pointer-events-none absolute -inset-3 rounded-full bg-gradient-to-br from-rose-200/40 to-primary-200/30 blur-lg"
                    aria-hidden
                  />
                  <AssistantRobot thinking size="md" className="relative drop-shadow-md" />
                </div>
                <div className="flex min-w-0 max-w-[min(100%,42rem)] flex-1 flex-col gap-1 pb-0.5">
                  <span className="text-xs font-medium text-primary-600">Asistente</span>
                  <div className="inline-flex max-w-full flex-wrap items-center gap-3 rounded-2xl rounded-tl-md border border-primary-100/80 bg-white px-4 py-3 text-left shadow-md shadow-gray-200/50">
                    <Loader2
                      className="h-5 w-5 shrink-0 animate-spin text-primary-600"
                      aria-hidden
                    />
                    <div className="flex min-w-0 flex-col gap-0.5">
                      <span className="text-sm font-medium text-gray-800">Preparando respuesta…</span>
                      <span className="text-xs text-gray-500">Un momento, por favor</span>
                    </div>
                  </div>
                </div>
              </div>
            ) : null}
            {messages.length > 0 && !sending ? (
              <div
                className="pointer-events-none absolute bottom-2 right-3 z-10 sm:bottom-3 sm:right-5"
                aria-hidden
              >
                <div className="relative">
                  <div className="absolute -inset-3 rounded-full bg-rose-200/20 blur-xl" />
                  <AssistantRobot size="sm" className="relative opacity-95 drop-shadow-lg" />
                </div>
              </div>
            ) : null}
            <div ref={bottomRef} className="h-px w-full shrink-0" aria-hidden />
          </div>
        </div>

        {/* Composer */}
        <div className="shrink-0 border-t border-primary-100/60 bg-gradient-to-b from-white to-primary-50/30 p-3 sm:p-4">
          <form onSubmit={handleSend} className="mx-auto max-w-5xl lg:max-w-[88rem]">
            <div className="flex items-end gap-2 rounded-2xl border border-primary-200/40 bg-white p-2 shadow-lg shadow-primary-900/[0.04] ring-1 ring-primary-100/50 focus-within:border-primary-400 focus-within:ring-2 focus-within:ring-primary-200/80">
              <label htmlFor="chat-input" className="sr-only">
                Mensaje para el asistente
              </label>
              <textarea
                id="chat-input"
                ref={textareaRef}
                rows={1}
                value={input}
                onChange={(e) => setInput(e.target.value)}
                onKeyDown={handleKeyDown}
                placeholder="Pregunta lo que quieras sobre tus citas…"
                disabled={sending}
                autoComplete="off"
                className="min-h-[48px] max-h-[200px] flex-1 resize-none bg-transparent px-2 py-2.5 text-sm text-gray-900 placeholder:text-gray-400 focus:outline-none disabled:opacity-60 sm:text-base"
              />
              <Button
                type="submit"
                disabled={sending || !input.trim()}
                size="md"
                className="!rounded-xl !bg-gradient-to-r !from-primary-600 !to-sky-600 !px-3 !shadow-md hover:!brightness-105 sm:!px-4"
                aria-label="Enviar mensaje"
              >
                {sending ? (
                  <Loader2 className="mx-auto h-5 w-5 animate-spin" />
                ) : (
                  <>
                    <Send className="h-4 w-4 sm:mr-2" />
                    <span className="hidden sm:inline">Enviar</span>
                  </>
                )}
              </Button>
            </div>
          </form>
        </div>
      </div>
      </div>
    </div>
  )
}

export default ChatAssistant
