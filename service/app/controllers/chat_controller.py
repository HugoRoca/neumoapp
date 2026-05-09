"""Endpoint POST /chat — asistente con OpenAI y herramientas de citas."""

from fastapi import APIRouter, Depends, HTTPException, status

from app.database.base import get_db
from app.schemas.chat import ChatRequest, ChatResponse, HospitalQuickReply, QuickReplyGroup
from app.core.config import settings
from app.core.dependencies import get_current_patient
from app.models.patient import Patient
from app.services.openai_chat_service import run_chat
from app.services.scheduling_wizard_service import (
    SchedulingWizardService,
    effective_wizard_selection,
    should_run_wizard,
)
from sqlalchemy.orm import Session

router = APIRouter(prefix="/chat", tags=["Chat"])


def _chat_llm_configured() -> bool:
    """
    - OpenAI en la nube: solo OPENAI_API_KEY (sin OPENAI_BASE_URL).
    - Ollama / local: OPENAI_BASE_URL apuntando a localhost (clave opcional).
    - Gemini (OpenAI-compat): OPENAI_BASE_URL de Google + OPENAI_API_KEY (clave de AI Studio).
    """
    if settings.OPENAI_BASE_URL:
        base = (settings.OPENAI_BASE_URL or "").lower()
        local = "localhost" in base or "127.0.0.1" in base
        if local:
            return True
        return bool(settings.OPENAI_API_KEY)
    return bool(settings.OPENAI_API_KEY)


@router.post(
    "/",
    response_model=ChatResponse,
    summary="Asistente IA para gestionar citas",
)
def chat(
    body: ChatRequest,
    db: Session = Depends(get_db),
    current_patient: Patient = Depends(get_current_patient),
):
    selection = effective_wizard_selection(
        body.message, body.wizard_state, body.wizard_selection
    )

    if should_run_wizard(body.message, body.wizard_state, selection):
        try:
            wiz = SchedulingWizardService(db, current_patient)
            text, state_out, qr = wiz.process(body.message, body.wizard_state, selection)
            qr_out = QuickReplyGroup.model_validate(qr) if qr else None
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error en el flujo de agendamiento: {e!s}",
            ) from e
        return ChatResponse(
            response=text,
            hospitals=None,
            compose_context=body.message,
            wizard_state=state_out,
            quick_replies=qr_out,
        )

    if not _chat_llm_configured():
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=(
                "Asistente no configurado: OpenAI en la nube → OPENAI_API_KEY; "
                "Ollama → OPENAI_BASE_URL (localhost); Gemini → OPENAI_BASE_URL de Google + OPENAI_API_KEY. "
                "Ajusta también OPENAI_CHAT_MODEL."
            ),
        )
    try:
        history_payload = [m.model_dump() for m in body.history]
        text, hospitals_payload = run_chat(
            db=db,
            patient=current_patient,
            user_message=body.message,
            history=history_payload,
        )
        hospitals_out = None
        if hospitals_payload:
            hospitals_out = [
                HospitalQuickReply(id=int(h["id"]), name=str(h.get("name") or ""))
                for h in hospitals_payload
                if h.get("id") is not None
            ]
            if not hospitals_out:
                hospitals_out = None
    except RuntimeError as e:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=str(e),
        ) from e
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=f"Error al contactar el modelo: {e!s}",
        ) from e

    return ChatResponse(
        response=text,
        hospitals=hospitals_out,
        compose_context=body.message,
        wizard_state=None,
        quick_replies=None,
    )
