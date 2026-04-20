"""Schemas for AI chat endpoint."""

from typing import Any, Dict, List, Literal, Optional

from pydantic import BaseModel, Field


class ChatMessageItem(BaseModel):
    role: Literal["user", "assistant"]
    content: str = Field(..., min_length=0, max_length=32000)


class WizardSelectionPayload(BaseModel):
    """
    Selección de una opción del flujo guiado. Solo datos internos en el cuerpo HTTP;
    el usuario ve únicamente la etiqueta (label) en la interfaz.
    """

    step: Literal["hospital", "specialty", "room", "date", "time", "confirm"]
    hospital_id: Optional[int] = None
    specialty_id: Optional[int] = None
    consultation_room_id: Optional[int] = None
    date_iso: Optional[str] = None
    time_hhmm: Optional[str] = None
    confirm: Optional[bool] = None


class ChatRequest(BaseModel):
    message: str = Field(
        ...,
        min_length=1,
        max_length=8000,
        description="Texto visible / natural del usuario (p. ej. nombre del hospital al pulsar un botón).",
    )
    history: List[ChatMessageItem] = Field(default_factory=list)
    wizard_state: Optional[Dict[str, Any]] = Field(
        None,
        description="Estado del flujo guiado de agendamiento (Hospital→…→hora); lo devuelve el servidor y el cliente lo reenvía.",
    )
    wizard_selection: Optional[WizardSelectionPayload] = Field(
        None,
        description="Si el usuario eligió una opción con un botón, el cliente envía el payload estructurado (sin mostrarlo en el chat).",
    )


class HospitalQuickReply(BaseModel):
    """Clínica para botones en el cliente (tras list_hospitals en el mismo turno)."""

    id: int
    name: str


class QuickReplyOption(BaseModel):
    """Opción mostrada como botón; el cliente reenvía `payload` en wizard_selection (no visible para el usuario)."""

    label: str
    payload: WizardSelectionPayload


class QuickReplyGroup(BaseModel):
    step: Literal["hospital", "specialty", "room", "date", "time", "confirm"]
    prompt: str = Field("", description="Subtítulo opcional bajo los botones; puede ir vacío.")
    options: List[QuickReplyOption]


class ChatResponse(BaseModel):
    response: str
    hospitals: Optional[List[HospitalQuickReply]] = Field(
        None,
        description="Si el asistente listó clínicas en este turno, el cliente puede mostrar botones.",
    )
    compose_context: Optional[str] = Field(
        None,
        description="Eco del mensaje del usuario; el cliente puede anteponerlo al elegir clínica.",
    )
    wizard_state: Optional[Dict[str, Any]] = Field(
        None,
        description="Estado actual del agendamiento guiado; el cliente debe reenviarlo en el siguiente POST.",
    )
    quick_replies: Optional[QuickReplyGroup] = Field(
        None,
        description="Botones del wizard (hospital, especialidad, fecha, etc.).",
    )
