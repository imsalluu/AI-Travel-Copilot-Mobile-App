from datetime import datetime
from typing import Optional, List, Any, Dict
from pydantic import BaseModel, Field
from app.schemas.itinerary import StructuredItineraryPlan


class ChatMessageRequest(BaseModel):
    message: str = Field(..., description="User prompt or travel request")
    conversation_id: Optional[str] = Field(None, description="Existing conversation ID")
    trip_id: Optional[str] = Field(None, description="Associated trip ID if modifying or asking about a trip")
    voice_enabled: bool = Field(False, description="Whether to return audio TTS response")
    client_context: Optional[Dict[str, Any]] = Field(default_factory=dict, description="Client coordinates, preferences, etc.")


class MessageResponse(BaseModel):
    id: str
    conversation_id: str
    role: str
    content: str
    message_type: str  # text, itinerary_card, place_card, weather_card, budget_card, error
    structured_data: Optional[Dict[str, Any]] = None
    tool_calls: Optional[List[Dict[str, Any]]] = None
    tool_results: Optional[List[Dict[str, Any]]] = None
    audio_url: Optional[str] = None
    created_at: datetime

    model_config = {"from_attributes": True}


class ConversationResponse(BaseModel):
    id: str
    user_id: str
    trip_id: Optional[str] = None
    title: str
    created_at: datetime
    messages: List[MessageResponse] = []

    model_config = {"from_attributes": True}


class ChatStreamChunk(BaseModel):
    event: str  # start, token, tool_start, tool_end, card, finish, error
    data: Optional[str] = None
    structured_data: Optional[Dict[str, Any]] = None
    card_type: Optional[str] = None
