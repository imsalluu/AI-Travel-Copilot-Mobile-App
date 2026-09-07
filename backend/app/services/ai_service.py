import time
from typing import Dict, Any, Optional, List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.core.config import settings
from app.models.user import UserPreference
from app.models.trip import Trip
from app.models.chat import Conversation, Message, AIRequest, AIAction
from app.agents.state import AgentState
from app.agents.graph import TravelAgentGraph
from app.schemas.itinerary import StructuredItineraryPlan
from app.services.trip_service import trip_service
import logging

logger = logging.getLogger(__name__)


class AIService:
    """Core AI Service orchestrating LLMs, multi-step LangGraph agents, memory, and structured outputs."""

    @classmethod
    async def process_chat_message(
        cls,
        user_id: str,
        message_text: str,
        conversation_id: Optional[str] = None,
        trip_id: Optional[str] = None,
        client_context: Optional[Dict[str, Any]] = None,
        db: AsyncSession = None,
    ) -> Message:
        """Process user chat prompt through LangGraph workflow with conversation memory and save interaction."""
        start_time = time.time()

        # 1. Retrieve or initialize Conversation
        if conversation_id:
            c_stmt = select(Conversation).where(Conversation.id == conversation_id, Conversation.user_id == user_id)
            c_res = await db.execute(c_stmt)
            conversation = c_res.scalar_one_or_none()
        else:
            conversation = None

        if not conversation:
            conversation = Conversation(
                user_id=user_id,
                trip_id=trip_id,
                title=f"Trip Planning - {message_text[:30]}..." if len(message_text) > 30 else message_text,
                context=client_context or {},
            )
            db.add(conversation)
            await db.flush()

        # 2. Save User Message
        user_msg = Message(
            conversation_id=conversation.id,
            role="user",
            content=message_text,
            message_type="text",
        )
        db.add(user_msg)
        await db.flush()

        # 3. Fetch User Long-term Preferences
        pref_stmt = select(UserPreference).where(UserPreference.user_id == user_id)
        pref_res = await db.execute(pref_stmt)
        pref = pref_res.scalar_one_or_none()
        user_pref_dict = {}
        if pref:
            user_pref_dict = {
                "preferred_budget_level": pref.preferred_budget_level,
                "travel_style": pref.travel_style,
                "dietary_restrictions": pref.dietary_restrictions,
                "preferred_transport": pref.preferred_transport,
                "preferred_currency": pref.preferred_currency,
                "interests": pref.interests,
            }

        # 4. Fetch Existing Trip Itinerary if modifying
        existing_itin_dict = None
        if trip_id or conversation.trip_id:
            active_trip_id = trip_id or conversation.trip_id
            existing_trip = await trip_service.get_trip_by_id(active_trip_id, user_id, db)
            if existing_trip:
                existing_itin_dict = {
                    "title": existing_trip.title,
                    "destination": existing_trip.destination,
                    "total_budget": existing_trip.total_budget,
                    "currency": existing_trip.currency,
                    "duration_days": existing_trip.duration_days,
                    "days": [
                        {
                            "day_number": d.day_number,
                            "title": d.title,
                            "theme": d.theme,
                            "notes": d.notes,
                            "activities": [
                                {
                                    "id": a.id,
                                    "title": a.title,
                                    "category": a.category,
                                    "location_name": a.location_name,
                                    "start_time": a.start_time,
                                    "end_time": a.end_time,
                                    "estimated_cost": a.estimated_cost,
                                    "currency": a.currency,
                                }
                                for a in d.activities
                            ]
                        }
                        for d in existing_trip.days
                    ]
                }

        # 5. Build Agent State & Execute LangGraph Workflow
        agent_state = AgentState(
            user_id=user_id,
            user_prompt=message_text,
            user_preferences=user_pref_dict,
            existing_trip_id=trip_id or conversation.trip_id,
            existing_itinerary=existing_itin_dict,
        )

        graph = TravelAgentGraph(db=db)
        final_state = await graph.run(agent_state)

        # 6. If Itinerary Plan Generated, Auto-Persist Trip into Database
        if final_state.generated_itinerary:
            try:
                saved_trip = await trip_service.save_structured_itinerary(
                    user_id=user_id,
                    itinerary=final_state.generated_itinerary,
                    db=db,
                    existing_trip_id=trip_id or conversation.trip_id,
                )
                conversation.trip_id = saved_trip.id
                if final_state.structured_card_data:
                    final_state.structured_card_data["trip_id"] = saved_trip.id
            except Exception as e:
                logger.error(f"Error auto-saving itinerary: {e}")

        # 7. Save Assistant Message
        assistant_msg = Message(
            conversation_id=conversation.id,
            role="assistant",
            content=final_state.final_response_text,
            message_type=final_state.message_type,
            structured_data=final_state.structured_card_data,
        )
        db.add(assistant_msg)

        # 8. Record AI Request Audit
        latency = (time.time() - start_time) * 1000.0
        ai_req = AIRequest(
            user_id=user_id,
            conversation_id=conversation.id,
            prompt=message_text,
            intent=final_state.intent,
            provider=settings.AI_PROVIDER,
            model=settings.OPENAI_MODEL,
            latency_ms=round(latency, 2),
            success=True,
        )
        db.add(ai_req)

        await db.commit()
        await db.refresh(assistant_msg)
        return assistant_msg


ai_service = AIService()
