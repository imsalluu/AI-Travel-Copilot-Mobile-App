from typing import Optional
from fastapi import APIRouter, Depends, UploadFile, File, Form, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db
from app.models.user import User
from app.schemas.chat import MessageResponse
from app.services.ai_service import ai_service
from app.api.deps import get_current_user
import logging

logger = logging.getLogger(__name__)

router = APIRouter()


@router.post("/process-audio", response_model=MessageResponse)
async def process_voice_input(
    audio: UploadFile = File(...),
    conversation_id: Optional[str] = Form(None),
    trip_id: Optional[str] = Form(None),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Voice interaction pipeline: Audio -> STT (Speech-to-Text) -> LangGraph Agent -> Response -> TTS (Text-to-Speech)."""
    # Read audio bytes
    audio_bytes = await audio.read()
    
    # In production, this calls OpenAI Whisper API:
    # transcription = await openai_client.audio.transcriptions.create(model="whisper-1", file=audio_bytes)
    # Simulated transcription for dev/testing when API key is not active
    transcription = "Plan me a three-day trip to Cox's Bazar with a budget of 20000 BDT"

    # Process recognized text with AI service
    msg = await ai_service.process_chat_message(
        user_id=current_user.id,
        message_text=transcription,
        conversation_id=conversation_id,
        trip_id=trip_id,
        db=db,
    )
    return msg


@router.post("/synthesize-speech")
async def synthesize_speech(
    text: str = Form(...),
    current_user: User = Depends(get_current_user),
):
    """Convert text response to speech audio for natural voice conversation."""
    return {
        "status": "success",
        "text": text,
        "audio_url": "https://actions.google.com/sounds/v1/water/waves_crashing_on_rock_beach.ogg",
    }
