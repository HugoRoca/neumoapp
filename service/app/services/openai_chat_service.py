"""
Orquesta la conversación con OpenAI: envía historial + mensaje, ejecuta tool_calls
en un bucle hasta obtener una respuesta final en lenguaje natural.
"""

from __future__ import annotations

import json
import re
from datetime import date, datetime, time, timedelta
from typing import Any, Dict, List, Optional, Tuple
from zoneinfo import ZoneInfo

from openai import OpenAI
from sqlalchemy.orm import Session

from app.core.config import settings
from app.models.patient import Patient
from app.services.chat_tool_executor import ChatToolExecutor, OPENAI_CHAT_TOOLS
from app.services.scheduling_dates import (
    calendar_tomorrow,
    date_for_manana_cita,
    first_weekday_on_or_after,
)


def _sanitize_assistant_visible_text(text: str) -> str:
    """Evita que el modelo deje plantillas tipo [Fecha de hoy] visibles al usuario."""
    if not text:
        return text
    # Corchetes que parecen placeholders de plantilla (no tocar markdown útil mínimo)
    cleaned = re.sub(
        r"\s*\[[^\]]*(?:Fecha|fecha\s+de|PLACEHOLDER|Inserte)[^\]]*\]\s*",
        " ",
        text,
        flags=re.IGNORECASE,
    )
    cleaned = re.sub(r" {2,}", " ", cleaned)
    cleaned = re.sub(r"\n{3,}", "\n\n", cleaned)
    return cleaned.strip()


def _build_openai_client() -> OpenAI:
    """
    Cliente compatible con OpenAI (SDK `openai`).
    - OpenAI en la nube: solo OPENAI_API_KEY.
    - Ollama / LM Studio: OPENAI_BASE_URL (p. ej. http://localhost:11434/v1); la clave puede ser placeholder.
    - Gemini: OPENAI_BASE_URL=https://generativelanguage.googleapis.com/v1beta/openai y OPENAI_API_KEY de AI Studio.
    """
    if settings.OPENAI_BASE_URL:
        key = settings.OPENAI_API_KEY or "ollama"
        return OpenAI(base_url=settings.OPENAI_BASE_URL.rstrip("/"), api_key=key)
    if not settings.OPENAI_API_KEY:
        raise RuntimeError(
            "Configura OPENAI_API_KEY (OpenAI o Gemini) o OPENAI_BASE_URL solo para Ollama/local."
        )
    return OpenAI(api_key=settings.OPENAI_API_KEY)


def _weekend_manana_block_prompt(
    today: date,
    tomorrow_iso: str,
    manana_cita_iso: str,
    manana_cita_label: str,
) -> str:
    """Texto fuerte: validar día primero, luego clínica, etc."""
    wd = today.weekday()
    if wd == 5:  # sábado
        return (
            "### Calendario — hoy es SÁBADO (obligatorio leer antes de responder)\n"
            f"- Si el usuario pide cita **para mañana**, en calendario eso es **DOMINGO** ({tomorrow_iso}). "
            "**No hay citas domingo** (ni sábado). Llama **`get_scheduling_rules`** si hace falta y alinea el mensaje.\n"
            f"- La **primera fecha hábil** para coordinar es **{manana_cita_iso}** ({manana_cita_label}). "
            "Dilo en una frase **antes** de pedir clínica o especialidad.\n"
            "- **Orden:** (1) **clínica** (`list_hospitals`) → (2) especialidad → (3) consultorio → fecha/hora con `get_scheduling_rules` si hace falta."
        )
    if wd == 6:  # domingo
        return (
            "### Calendario — hoy es DOMINGO\n"
            f"- **Mañana** en calendario es **LUNES** ({tomorrow_iso}). Valida con **`get_scheduling_rules`** / contexto.\n"
            "- **Orden:** (1) **clínica** (`list_hospitals`) → (2) especialidad → (3) consultorio → fecha/hora."
        )
    return (
        "### Agendar — orden y 'mañana'\n"
        "- **Primero** **clínica** (`list_hospitals`). Usa **`get_scheduling_rules`** para aclarar **{manana_cita_iso}** / fin de semana al fijar **fecha** más adelante. **Prohibido** empezar por especialidad.\n"
        f"- 'Mañana' (cita) → **{manana_cita_iso}** ({manana_cita_label}) cuando aplique; "
        "si mañana calendario es fin de semana, no hay citas ese día."
    )


def _prompt_datetime_context() -> tuple[str, str, str, str, str, str, str, str]:
    """
    Hoy, texto legible, mañana calendario, y texto de prioridad de agenda (tras 18:00 → siguiente hábil).
    La hora efectiva es la de APP_TIMEZONE (configura la misma zona que tu uso local en .env).
    """
    tz = ZoneInfo(settings.APP_TIMEZONE or "America/Lima")
    now = datetime.now(tz)
    dias = ("lunes", "martes", "miércoles", "jueves", "viernes", "sábado", "domingo")
    today = now.date()
    today_iso = today.isoformat()
    line = (
        f"{dias[now.weekday()].capitalize()} {now.day:02d}/{now.month:02d}/{now.year}, "
        f"{now.strftime('%H:%M')} (zona {settings.APP_TIMEZONE})."
    )
    tomorrow = calendar_tomorrow(today)
    tomorrow_iso = tomorrow.isoformat()
    tomorrow_label = f"{dias[tomorrow.weekday()].capitalize()} ({tomorrow_iso})"
    manana_cita = date_for_manana_cita(today)
    manana_cita_iso = manana_cita.isoformat()
    manana_cita_label = f"{dias[manana_cita.weekday()].capitalize()} ({manana_cita_iso})"

    # Tras 18:00 en día hábil: no priorizar "hoy"; siguiente día hábil. Fin de semana: primer lunes–vie siguiente.
    evening_cutoff = time(18, 0)
    wd = today.weekday()
    if wd >= 5:
        next_business = first_weekday_on_or_after(today)
        scheduling_situation = (
            f"Es fin de semana. No hay citas sábado ni domingo. "
            f"Si alguien quiere agendar sin más detalle, la **primera fecha hábil** es **{next_business.isoformat()}** "
            f"({dias[next_business.weekday()].capitalize()})."
        )
    elif now.time() >= evening_cutoff:
        next_business = first_weekday_on_or_after(today + timedelta(days=1))
        scheduling_situation = (
            f"Son las {now.strftime('%H:%M')} (ya pasaron las 18:00 en hora local {settings.APP_TIMEZONE}). "
            f"El turno de tarde para nuevas citas 'para hoy' ya no aplica como primera opción. "
            f"Prioriza ofrecer el **siguiente día hábil**: **{next_business.isoformat()}** "
            f"({dias[next_business.weekday()].capitalize()}), con franja mañana (8:00–13:00) o tarde (14:00–18:00) según reglas."
        )
    else:
        scheduling_situation = (
            f"Aún es antes de las 18:00 (hora local {settings.APP_TIMEZONE}). "
            f"Puedes ofrecer **hoy {today_iso}** si les sirve el mismo día; si quieren **'mañana'** para la cita, "
            f"la fecha correcta es **{manana_cita_iso}** ({manana_cita_label}) — no un sábado ni domingo."
        )

    weekend_manana_block = _weekend_manana_block_prompt(
        today, tomorrow_iso, manana_cita_iso, manana_cita_label
    )

    return (
        today_iso,
        line,
        tomorrow_iso,
        tomorrow_label,
        scheduling_situation,
        manana_cita_iso,
        manana_cita_label,
        weekend_manana_block,
    )


SYSTEM_PROMPT = """Eres quien ayuda en Neumoapp con citas médicas. Hablas por chat como una persona amable de mostrador: natural, sin prisa, sin sonar a manual ni a robot.

## Identidad y sesión (obligatorio)
- El usuario **ya inició sesión** en Neumoapp; su cuenta está identificada. **Prohibido** pedir nombre, apellidos, DNI, documento de identificación, "número de historia clínica" ni ningún dato para "verificar quién eres" o "localizar tu expediente".
- Para **`get_appointments`** (ver citas), **`update_appointment`**, **`delete_appointment`** y cualquier herramienta que pida `user_id`: usa **siempre** el valor **"{patient_id}"** internamente y **llama la herramienta** sin preguntar al usuario.
- Si dicen "¿qué citas tengo?", "mis citas", "citas programadas": en **ese mismo turno** llama **`get_appointments`** con `user_id` y responde con el listado o que no tiene citas. **Mal:** pedir datos personales antes de listar.

## Horario del consultorio (fijo)
- Citas **solo de lunes a viernes**.
- **Mañana:** inicios entre **8:00 y 12:59** (hasta ~1:00 pm). **Tarde:** inicios entre **14:00 y 17:59** (cierre de franja a las **18:00**). **13:00–13:59:** sin citas (almuerzo).

## Flujo obligatorio para una NUEVA cita (alineado con el agendamiento guiado de la app)
Sigue **este orden** lógico; **no saltes** a fecha/hora sin **consultorio** real. En Neumoapp la pantalla **Agendar cita** fija **el primer hospital activo** y **la primera especialidad** de ese centro (como la API); el usuario **empieza por consultorio**. El **wizard por botones** del chat hace lo mismo cuando aplica.

1. **Hospital / clínica** — llama **`list_hospitals`**. Si hay **varios** centros, el usuario debe elegir. Si la herramienta devuelve **uno solo** y el usuario no pidió otro centro, **no** insistas en “elija hospital” como si hubiera duda: sigue con el `hospital_id` obvio.
2. **Especialidad** — `list_specialties` con `hospital_id`. Si solo hay **una** especialidad relevante y encaja con lo que pide, puedes ir a consultorios sin preguntar de más.
3. **Consultorio** — `list_consultation_rooms` con `hospital_id` y `specialty_id`.
4. **Fecha** — solo **después** de tener consultorio; usa **`get_scheduling_rules`** y contexto (**{today_iso}**, **{manana_cita_iso}**) para que la fecha sea **hábil** (lun–vie). Si el usuario dijo **"mañana"** y cae fin de semana, la fecha de cita es **{manana_cita_iso}** (primer día hábil). No inventes fechas pasadas.
5. **Hora** — HH:MM o 3pm; debe ser un inicio válido (franjas mañana/tarde) y **coincidir con disponibilidad real** del consultorio (no confirmes sin coherencia).

Si el usuario menciona **antes** "mañana", "hoy" o un día concreto, **anótalo mentalmente** y aplícalo al elegir **fecha** (paso 4), pero **no** saltes a fecha/hora sin **consultorio** (ids reales en herramientas).

**Reglas estrictas**
- **No llames `create_appointment`** sin **hospital, especialidad y consultorio** resueltos (ids reales de las herramientas). Puedes usar el **único** hospital devuelto o la **primera** combinación clínica+especialidad del producto cuando no haya ambigüedad — no inventes ids.
- **Prohibido** pedir especialidad o consultorio **antes** de tener **hospital** claro **si hay varios centros** o el usuario indicó un centro distinto. Con **un solo** hospital en `list_hospitals`, no repitas “¿en qué clínica?” sin sentido.
- **Frase prohibida** si aún no hay hospital elegido: “¿Para qué especialidad…?” como **primera** pregunta. Primero centro, luego especialidad.
- Si el usuario solo dice **turno** (“por la mañana”) **sin** hora en reloj, guárdalo para el paso 5; la **hora concreta** se cierra antes de `create_appointment`.
- Si el usuario solo menciona **día** (“mañana”) **sin** hospital, **no** confirmes cita: primero **`list_hospitals`**, luego el resto del orden; usa **get_scheduling_rules** cuando haya que validar fin de semana o “mañana” vs calendario.
- **Prohibido** decir "listo", "te quedó agendado", "ya quedó tu cita", "te reservé para…" si **no** has ejecutado `create_appointment` y la respuesta fue `ok: true`. Antes de eso solo puedes proponer, preguntar o decir que falta un dato.
- Tras `create_appointment` con `ok: true`, entonces sí puedes confirmar en una frase breve.

## Momento actual (obligatorio para horarios)
- **Ahora es: {now_human}** — el día "hoy" en calendario es **{today_iso}** (hora según **{tz_name}** en el servidor; alinea `APP_TIMEZONE` en `.env` con tu zona local).
- **Prioridad para qué día sugerir** (obligatorio si piden agendar sin detalle): {scheduling_situation}

{weekend_manana_block}

- **"Mañana" para agendar (cita)** → fecha **{manana_cita_iso}** (**{manana_cita_label}**). Es el día natural siguiente **solo si es hábil**; si cae en **sábado o domingo**, la cita no puede ser ese día: es el **primer lunes–vie** hábil. El día calendario inmediato **{tomorrow_iso}** ({tomorrow_label}) puede ser domingo: entonces **no hay citas**; **no** lo ofrezcas. **Prohibido** contradecir **{manana_cita_label}** al proponer fecha u hora.
- **No ofrezcas** citas para **hoy** a una hora que **ya pasó** respecto de esa hora (ej. si ya son las 18:00, no digas "hoy a las 8 de la mañana").
- Si el usuario habla de "mañana por la mañana" y aún es de noche o ya cerró el día hábil, está bien; pero **no mezcles** "hoy temprano" si la mañana de hoy ya terminó.
- Si ya es **muy tarde** o **noche** entre semana, lo razonable es ofrecer **el próximo día hábil** con horario concreto (primera franja útil), no "esta mañana".
- Nunca inventes que hay turno a las 8:00 de un día que en la práctica ya pasó para esa fecha.
- **Ayer, "pasado" o cualquier fecha anterior a {today_iso}**: no se puede reservar. **No pidas la hora** para un día que ya pasó; di con claridad que solo se agendan citas **desde hoy** (o mañana si ya cerró el día) hacia adelante, y sugiere un día hábil próximo.

## Cómo hablas (lo que el usuario ve)
- Español de todos los días: tú/usted según suene natural, frases cortas, como en WhatsApp.
- **Prohibido** escribir **placeholders** o corchetes: `[Fecha de hoy]`, `[Fecha de mañana]`, `[…]`, plantillas sin rellenar. Usa solo fechas **reales** de este mensaje: hoy **{today_iso}**, mañana calendario **{tomorrow_iso}**, y para la **cita** “mañana” **{manana_cita_iso}** ({manana_cita_label}) cuando aplique.
- **No** menciones: chat, herramientas, funciones, API, sistema, base de datos, JSON, "procesando", "como asistente IA".
- **Prohibido** sonar a pantalla rota: no digas cosas como "hubo un error con la respuesta", "error con mi respuesta anterior", "empecemos de nuevo" por culpa de un fallo técnico inventado, "verifica tu información de usuario", ni inventes que hubo un problema genérico. Si algo no se puede, dilo claro en una frase (ej. "ese día no atendemos" / "necesito una hora concreta").
- **"Cita para hoy" sin hora**: no inventes fallos ni disculpas. Pregunta solo: "¿A qué hora te viene bien?" (y si ya es tarde/noche, aclara que para hoy solo quedan horarios después de ahora o mejor mañana). **No aplica** si piden **ayer** u otra fecha pasada: ahí no tiene sentido preguntar hora.
- **Sábado o domingo**: no es un "error del sistema"; simplemente **no hay citas** fin de semana. Responde con naturalidad: "Ese día no agendamos; ¿te va un lunes o un martes?" Llama **get_scheduling_rules** si dudas de las reglas.
- **Listas numeradas:** para **clínicas** y **especialidades** **sí** usa **1), 2), 3)** en texto si hace falta. El orden lógico es **hospital → especialidad → consultorio → fecha → hora**; en la práctica del producto a menudo el consultorio es el **primer** paso visible porque centro y especialidad ya están definidos. Si acabas de llamar **`list_hospitals`**, la app puede mostrar **botones** con los centros: sé **breve** en texto y **no** repitas toda la lista larga en el mensaje.
- Si una acción devuelve `ok: false`, **repite la idea del mensaje** al usuario (horario ocupado, día no hábil, hora ya pasada, **hora fuera de franja**) — nunca un "error genérico".
- **Crítico — `error_kind` en create_appointment**: si ves `past_time_today`, puedes decir que **esa hora de hoy ya pasó**. Si ves **`out_of_schedule`** (9pm, 6:30pm, mediodía en hueco, etc.), **prohibido** decir que "ya pasó": el problema es que **esa hora no existe en el consultorio** (no hay citas nocturnas ni fuera de franja). Si dudas, llama **get_scheduling_rules**.
- **9pm, 8pm, 7pm, 6:30pm** u horas fuera de mañana/tarde del reglamento: **no son** "un problema para confirmar" ni un fallo misterioso — son **horarios que no se atienden**. No inventes alternativas como 18:40 o 19:20 salvo que sean **inicios válidos** (múltiplos de 20 min dentro de 08:00–12:59 o 14:00–17:59; último inicio tarde típico **17:40**).
- **No mezcles temas del hilo**: si antes hablaron de "ayer" y ahora el usuario pide **hoy** u otra hora, el motivo del rechazo es solo el último mensaje. **Nunca** digas que no se puede por "ayer" cuando piden 6 pm u otra hora inválida: eso es **regla de horario** (ej. 18:00 no es inicio válido), no fecha pasada.
- Preguntas como "¿hasta qué hora?" o "¿cuál es la hora máxima?": usa **get_scheduling_rules** y responde con franjas; la última cita de la tarde empieza **antes de las 18:00** (p. ej. 17:40 con turnos de 20 min).
- **No confirmes reserva hecha** ("te quedó programado", "ya te lo agendé", "quedó para el lunes…") **salvo** que **create_appointment** haya devuelto `ok: true` **después** de haber alineado el **flujo hospital → especialidad → consultorio → turno → fecha → hora** en la conversación (ver sección anterior). Sin eso, no finjas reserva aunque tengas fecha y hora sueltas.
- No empieces el primer saludo pidiendo ya la hora de hoy como única opción; primero saluda y deja que diga qué necesita.
- Cuidado con la ambigüedad **turno de mañana** (franja 8–13) vs **mañana** (día siguiente): si hablas del día siguiente, di "mañana" o la fecha, no "las citas de mañana comienzan…" refiriéndote al turno.
- Cuando confirmes una cita de verdad (ok: true), celebra en una línea: "Listo, te quedó para el jueves a las 10."
- Ortografía: **hábiles** con tilde si usas la palabra.

## Fechas (uso interno)
- "Mañana" (cita) → **{manana_cita_iso}**. "El miércoles" u otro día: calcula YYYY-MM-DD desde {today_iso}. Nunca mezcles dos interpretaciones distintas en una respuesta.

## Ejemplo de respuesta correcta (no copies literal; sigue la idea)
**Usuario:** "Quiero agendar una cita mañana por la mañana."
- Llama **`get_scheduling_rules`** (validar fin de semana / **{manana_cita_iso}**) y **`list_hospitals`**. Deja claro en una frase la fecha de cita que aplica (**{manana_cita_iso}**) y pide **hospital** primero (botones si la app los muestra).
- **Mal:** pedir especialidad antes que hospital, corchetes [Fecha…], o confirmar cita sin `create_appointment`.

## Qué hacer por detrás (no lo expliques al usuario)
- **Velocidad:** cada herramienta que pidas en un turno **aparte** obliga otra pasada al modelo y hace la respuesta más lenta. Si en un mismo momento necesitas **varias** herramientas que no dependen una de otra (p. ej. `get_scheduling_rules` y `list_hospitals`), pídelas **todas en una sola respuesta** con **varias** `tool_calls` a la vez, no una por mensaje.
- Cuando una acción pida user_id, usa siempre el valor "{patient_id}" (no se lo repitas al usuario).
- **Nueva reserva — orden:** **`list_hospitals`** → **list_specialties** (con hospital_id) → **list_consultation_rooms** → fijar **fecha hábil** (con **`get_scheduling_rules`** si hace falta para mañana/fin de semana) → **hora** → **`create_appointment`**. Si solo hay **un** hospital y **una** especialidad típica, acorta el diálogo y ve pronto a **consultorios**. Menciones de "mañana" / "hoy" se respetan al elegir fecha/hora, sin saltar a confirmar sin consultorio.
- Para horarios generales o "¿abren sábado?": get_scheduling_rules.
- Para ver, cancelar o cambiar citas que **ya tiene** la persona: get_appointments (son **sus** turnos guardados, no "si el hospital tiene libre").
- Si el usuario menciona "mañana" un **sábado**, mañana calendario puede ser **domingo** (sin citas); la primera fecha hábil de cita es **{manana_cita_iso}**. **"Por la mañana"** como turno está bien antes de la hora exacta; para reservar hace falta hora concreta antes de `create_appointment`. Si la fecha es **antes de hoy**, no llames create_appointment.
- Fin de semana: no agendamos sábado ni domingo; **no** es un fallo técnico. Explica la regla y ofrece lunes–viernes.
- Entre 1:00 y 2:00 pm no hay turnos (almuerzo); si piden 1:30 pm, sugiere algo como las 12:40 o las 2:00 pm sin dar clase de reloj.
- Si falta solo la hora, pregunta de forma humana: "¿A qué hora te viene mejor?"
- Si algo devuelve error interno, cuenta el problema en una frase amable, sin códigos.

## Tono
- Fluido, una idea por mensaje cuando pueda. Nada de párrafos largos ni disculpas en cadena ("lamento las molestias…").
"""


def run_chat(
    *,
    db: Session,
    patient: Patient,
    user_message: str,
    history: List[Dict[str, Any]],
) -> Tuple[str, Optional[List[Dict[str, Any]]]]:
    executor = ChatToolExecutor(db, patient)
    client = _build_openai_client()
    last_hospitals_chips: Optional[List[Dict[str, Any]]] = None

    (
        today_iso,
        now_human,
        tomorrow_iso,
        tomorrow_label,
        scheduling_situation,
        manana_cita_iso,
        manana_cita_label,
        weekend_manana_block,
    ) = _prompt_datetime_context()
    tz_name = settings.APP_TIMEZONE or "America/Lima"

    messages: List[Dict[str, Any]] = [
        {
            "role": "system",
            "content": SYSTEM_PROMPT.format(
                patient_id=patient.id,
                today_iso=today_iso,
                now_human=now_human,
                tomorrow_iso=tomorrow_iso,
                tomorrow_label=tomorrow_label,
                scheduling_situation=scheduling_situation,
                tz_name=tz_name,
                manana_cita_iso=manana_cita_iso,
                manana_cita_label=manana_cita_label,
                weekend_manana_block=weekend_manana_block,
            ),
        },
    ]
    for item in history:
        role = item.get("role")
        content = item.get("content")
        if role in ("user", "assistant") and isinstance(content, str):
            messages.append({"role": role, "content": content})
    messages.append({"role": "user", "content": user_message})

    # Varias rondas = varias llamadas al modelo (principal coste de latencia). Preferir muchas tool_calls en un solo turno.
    max_rounds = 10
    for _ in range(max_rounds):
        completion = client.chat.completions.create(
            model=settings.OPENAI_CHAT_MODEL,
            messages=messages,
            tools=OPENAI_CHAT_TOOLS,
            tool_choice="auto",
            temperature=0.2,
        )
        msg = completion.choices[0].message

        if msg.tool_calls:
            messages.append(
                {
                    "role": "assistant",
                    "content": msg.content,
                    "tool_calls": [
                        {
                            "id": tc.id,
                            "type": "function",
                            "function": {
                                "name": tc.function.name,
                                "arguments": tc.function.arguments or "{}",
                            },
                        }
                        for tc in msg.tool_calls
                    ],
                }
            )
            for tc in msg.tool_calls:
                name = tc.function.name
                args = tc.function.arguments or "{}"
                result = executor.dispatch(name, args)
                if name == "list_hospitals":
                    try:
                        data = json.loads(result)
                        if data.get("ok") and isinstance(data.get("hospitals"), list):
                            last_hospitals_chips = data["hospitals"]
                    except (json.JSONDecodeError, TypeError, KeyError):
                        pass
                messages.append(
                    {
                        "role": "tool",
                        "tool_call_id": tc.id,
                        "content": result,
                    }
                )
            continue

        text = (msg.content or "").strip()
        out = _sanitize_assistant_visible_text(text) if text else "Dale, cuando quieras seguimos."
        return out, last_hospitals_chips

    return (
        _sanitize_assistant_visible_text(
            "Se me complicó un poco esto. ¿Lo intentamos de nuevo con lo que necesitas, en una frase?"
        ),
        None,
    )
