from typing import List, Dict, Any, Optional, Annotated
from pydantic import BaseModel, Field
import operator
from app.schemas.itinerary import StructuredItineraryPlan


class AgentState(BaseModel):
    """LangGraph Agent State schema tracked across workflow nodes."""

    # User Input & Context
    user_id: str
    user_prompt: str
    conversation_history: List[Dict[str, Any]] = Field(default_factory=list)
    user_preferences: Dict[str, Any] = Field(default_factory=dict)
    existing_trip_id: Optional[str] = None
    existing_itinerary: Optional[Dict[str, Any]] = None

    # Extracted Parameters
    intent: str = "plan_trip"  # plan_trip, modify_trip, ask_question, explore_places
    destination: Optional[str] = None
    duration_days: Optional[int] = None
    budget: Optional[float] = None
    currency: str = "BDT"
    travel_style: Optional[str] = None
    travelers_count: int = 1
    interests: List[str] = Field(default_factory=list)

    # Missing Information Check
    is_missing_critical_info: bool = False
    clarification_question: Optional[str] = None

    # Retrieved Context & Tool Results
    destination_knowledge: List[Dict[str, Any]] = Field(default_factory=list)
    discovered_places: List[Dict[str, Any]] = Field(default_factory=list)
    discovered_hotels: List[Dict[str, Any]] = Field(default_factory=list)
    discovered_restaurants: List[Dict[str, Any]] = Field(default_factory=list)
    weather_data: Optional[Dict[str, Any]] = None
    budget_allocations: Optional[Dict[str, Any]] = None

    # Generated Artifacts
    generated_itinerary: Optional[StructuredItineraryPlan] = None
    is_valid_itinerary: bool = False
    validation_notes: List[str] = Field(default_factory=list)

    # Final Conversational Output
    final_response_text: str = ""
    message_type: str = "text"  # text, itinerary_card, place_card, weather_card, budget_card
    structured_card_data: Optional[Dict[str, Any]] = None
