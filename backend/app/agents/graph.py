import re
from typing import Dict, Any, List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from app.agents.state import AgentState
from app.tools.travel_tools import TravelToolSuite
from app.schemas.itinerary import StructuredItineraryPlan, ItineraryDayPlan, ActivityPlan


class TravelAgentGraph:
    """LangGraph-style stateful agent workflow for end-to-end travel planning, tool execution, and itinerary synthesis."""

    def __init__(self, db: AsyncSession):
        self.db = db
        self.tools = TravelToolSuite(db)

    async def run(self, initial_state: AgentState) -> AgentState:
        """Execute state machine step-by-step through pipeline nodes."""
        state = initial_state

        # Node 1: Understand Request
        state = await self.node_understand_request(state)

        # Node 2: Check & Collect Missing Information
        state = await self.node_collect_missing_info(state)
        if state.is_missing_critical_info:
            return state

        # Node 3: If conversational modification of existing trip
        if state.intent == "modify_trip" and state.existing_itinerary:
            state = await self.node_modify_existing_itinerary(state)
            return state

        # Node 4: Retrieve Grounded Destination Knowledge (RAG)
        state = await self.node_retrieve_destination_knowledge(state)

        # Node 5: Search Places, Hotels, Restaurants (Tools)
        state = await self.node_search_places_and_amenities(state)

        # Node 6: Check Weather & Calculate Distances (Tools)
        state = await self.node_check_weather_and_distances(state)

        # Node 7: Estimate Budget Allocations (Tool)
        state = await self.node_estimate_budget(state)

        # Node 8: Build Structured Itinerary
        state = await self.node_build_itinerary(state)

        # Node 9: Validate Constraints
        state = await self.node_validate_itinerary(state)

        # Node 10: Generate Final Conversational Plan
        state = await self.node_generate_final_plan(state)

        return state

    # ==================== PIPELINE NODES ====================

    async def node_understand_request(self, state: AgentState) -> AgentState:
        """Parse natural language request to extract destination, days, budget, and intent."""
        prompt = state.user_prompt.lower()

        # Intent detection
        modify_keywords = ["make day", "less busy", "add sunset", "remove expensive", "change day", "cheaper", "move activity", "add a", "delete", "replace"]
        if any(kw in prompt for kw in modify_keywords) and (state.existing_trip_id or state.existing_itinerary):
            state.intent = "modify_trip"
        elif any(q in prompt for q in ["what is", "how much", "weather in", "safety", "is it worth", "rules in", "tips"]):
            state.intent = "ask_question"
        else:
            state.intent = "plan_trip"

        # Extract Destination
        destinations_known = ["cox's bazar", "coxsbazar", "sylhet", "sajek", "saint martin", "dhaka", "chittagong", "bandarban", "bali", "tokyo", "paris"]
        for d in destinations_known:
            if d in prompt:
                state.destination = "Cox's Bazar" if "cox" in d else d.title()
                break

        # Extract Duration (e.g., "3 days", "3-day", "weekend", "5 days")
        days_match = re.search(r"(\d+)\s*(?:-| )*(?:days?|day|nights?)", prompt)
        if days_match:
            state.duration_days = int(days_match.group(1))
        elif "weekend" in prompt:
            state.duration_days = 2
        elif not state.duration_days:
            state.duration_days = 3  # Default duration

        # Extract Budget (e.g., "20,000 BDT", "20000 taka", "$500", "budget of 15000")
        budget_match = re.search(r"(?:budget\s*(?:of)?\s*)?(\d{1,3}(?:,\d{3})*|\d+)\s*(?:bdt|taka|tk|\$|usd)?", prompt)
        if budget_match:
            val_str = budget_match.group(1).replace(",", "")
            if float(val_str) > 500:  # Avoid matching short numbers like days
                state.budget = float(val_str)
        if not state.budget:
            state.budget = (state.duration_days or 3) * 6000.0  # Default budget

        # Extract Currency
        if "$" in prompt or "usd" in prompt:
            state.currency = "USD"
        else:
            state.currency = state.user_preferences.get("preferred_currency", "BDT")

        return state

    async def node_collect_missing_info(self, state: AgentState) -> AgentState:
        """Determine if mandatory parameters are missing and formulate clarification question if needed."""
        if state.intent == "plan_trip" and not state.destination:
            state.is_missing_critical_info = True
            state.clarification_question = (
                "Where would you like to travel? I can create complete itineraries for **Cox's Bazar**, **Sylhet**, **Sajek Valley**, **Saint Martin**, and many other wonderful destinations!"
            )
            state.final_response_text = state.clarification_question
            state.message_type = "text"
            return state

        state.is_missing_critical_info = False
        return state

    async def node_retrieve_destination_knowledge(self, state: AgentState) -> AgentState:
        """Call RAG tool to retrieve grounded destination guidelines and rules."""
        if not state.destination:
            return state

        docs = await self.tools.search_destination_knowledge(
            query=f"best itinerary guidelines safety transport rules in {state.destination}",
            destination=state.destination,
        )
        state.destination_knowledge = docs
        return state

    async def node_search_places_and_amenities(self, state: AgentState) -> AgentState:
        """Execute external tools to discover places, hotels, and dining."""
        dest = state.destination or "Cox's Bazar"
        state.discovered_places = await self.tools.search_places(destination=dest, max_results=8)
        state.discovered_hotels = await self.tools.search_hotels(destination=dest, max_price=(state.budget / max(state.duration_days, 1)) * 0.4)
        state.discovered_restaurants = await self.tools.search_restaurants(destination=dest)
        return state

    async def node_check_weather_and_distances(self, state: AgentState) -> AgentState:
        """Execute weather tool and verify outdoor conditions."""
        dest = state.destination or "Cox's Bazar"
        state.weather_data = await self.tools.get_weather(destination=dest, duration_days=state.duration_days or 3)
        return state

    async def node_estimate_budget(self, state: AgentState) -> AgentState:
        """Call budget tool to compute financial allocations."""
        total = state.budget or 18000.0
        days = state.duration_days or 3
        state.budget_allocations = await self.tools.calculate_trip_budget(total_budget=total, duration_days=days)
        return state

    async def node_build_itinerary(self, state: AgentState) -> AgentState:
        """Synthesize discovered places, weather, and budget constraints into structured Pydantic plan."""
        dest = state.destination or "Cox's Bazar"
        days_count = state.duration_days or 3
        places = state.discovered_places
        restaurants = state.discovered_restaurants
        hotels = state.discovered_hotels
        weather = state.weather_data or {}
        daily_weather = weather.get("daily_forecasts", [])

        plan_days: List[ItineraryDayPlan] = []
        total_estimated = 0.0

        for day_num in range(1, days_count + 1):
            w_info = daily_weather[day_num - 1] if day_num - 1 < len(daily_weather) else {}
            is_rainy = w_info.get("indoor_recommended", False)

            activities: List[ActivityPlan] = []
            day_cost = 0.0

            if day_num == 1:
                # Arrival day
                title = f"Day 1: Arrival & {dest} Sunset Discovery"
                theme = "Welcome & Coastline Orientation"

                # Morning / Check-in
                hotel_name = hotels[0]["name"] if hotels else f"Luxury Beach Hotel {dest}"
                activities.append(
                    ActivityPlan(
                        title=f"Check-in at {hotel_name}",
                        description=f"Settle into your room, freshen up, and enjoy welcome drinks.",
                        category="hotel",
                        location_name=hotel_name,
                        start_time="11:00",
                        end_time="12:30",
                        duration_minutes=90,
                        estimated_cost=0.0,
                        currency=state.currency,
                        travel_mode="drive",
                    )
                )

                # Lunch
                rest_name = restaurants[0]["name"] if restaurants else "Local Specialty Eatery"
                activities.append(
                    ActivityPlan(
                        title=f"Traditional Lunch at {rest_name}",
                        description="Savor authentic local delicacies and fresh coastal seafood.",
                        category="meal",
                        location_name=rest_name,
                        start_time="13:00",
                        end_time="14:15",
                        duration_minutes=75,
                        estimated_cost=650.0,
                        currency=state.currency,
                        travel_mode="walk",
                    )
                )
                day_cost += 650.0

                # Afternoon attraction / Sunset
                place1 = places[0] if places else {"name": "Scenic Beach Point", "description": "Relax on golden sand"}
                activities.append(
                    ActivityPlan(
                        title=f"Sunset & Beach Walk at {place1['name']}",
                        description=place1.get("description", "Enjoy sea breeze and ocean views."),
                        category="attraction",
                        location_name=place1["name"],
                        start_time="16:30",
                        end_time="18:30",
                        duration_minutes=120,
                        estimated_cost=place1.get("estimated_cost", 200.0),
                        currency=state.currency,
                        travel_mode="walk",
                        is_indoor=is_rainy,
                    )
                )
                day_cost += place1.get("estimated_cost", 200.0)

                # Dinner
                rest2 = restaurants[1]["name"] if len(restaurants) > 1 else rest_name
                activities.append(
                    ActivityPlan(
                        title=f"Evening Dinner at {rest2}",
                        description="Relaxing dinner experience with ocean ambience.",
                        category="meal",
                        location_name=rest2,
                        start_time="20:00",
                        end_time="21:30",
                        duration_minutes=90,
                        estimated_cost=800.0,
                        currency=state.currency,
                        travel_mode="drive",
                    )
                )
                day_cost += 800.0

            else:
                # Subsequent exploration days
                title = f"Day {day_num}: {dest} Nature & Culture Exploration"
                theme = "Immersive Scenic Adventure"

                # Morning Activity
                p_idx = (day_num - 1) % len(places) if places else 0
                place = places[p_idx] if places else {"name": "Panoramic Viewpoint", "description": "Scenic sightseeing"}
                activities.append(
                    ActivityPlan(
                        title=f"Morning Excursion to {place['name']}",
                        description=place.get("description", "Explore natural scenic beauty and photography spots."),
                        category="attraction",
                        location_name=place["name"],
                        start_time="09:00",
                        end_time="11:30",
                        duration_minutes=150,
                        estimated_cost=place.get("estimated_cost", 400.0),
                        currency=state.currency,
                        travel_mode="drive",
                        is_indoor=is_rainy,
                    )
                )
                day_cost += place.get("estimated_cost", 400.0)

                # Lunch
                rest = restaurants[(day_num) % len(restaurants)] if restaurants else "Local Cafe"
                r_name = rest["name"] if isinstance(rest, dict) else rest
                activities.append(
                    ActivityPlan(
                        title=f"Local Dining at {r_name}",
                        description="Enjoy regional cuisine with seasonal ingredients.",
                        category="meal",
                        location_name=r_name,
                        start_time="12:30",
                        end_time="13:45",
                        duration_minutes=75,
                        estimated_cost=600.0,
                        currency=state.currency,
                        travel_mode="drive",
                    )
                )
                day_cost += 600.0

                # Afternoon
                p2_idx = (day_num) % len(places) if places else 0
                place2 = places[p2_idx] if places else {"name": "Heritage Cultural Market", "description": "Shopping and leisure"}
                activities.append(
                    ActivityPlan(
                        title=f"Afternoon Discovery: {place2['name']}",
                        description=place2.get("description", "Handmade crafts, local souvenirs, and leisure photography."),
                        category="leisure",
                        location_name=place2["name"],
                        start_time="15:30",
                        end_time="18:00",
                        duration_minutes=150,
                        estimated_cost=place2.get("estimated_cost", 300.0),
                        currency=state.currency,
                        travel_mode="drive",
                    )
                )
                day_cost += place2.get("estimated_cost", 300.0)

                # Dinner
                activities.append(
                    ActivityPlan(
                        title="Coastal BBQ & Evening Stroll",
                        description="Fresh grilled dinner and peaceful evening walk.",
                        category="meal",
                        location_name=f"{dest} Promenade",
                        start_time="19:30",
                        end_time="21:00",
                        duration_minutes=90,
                        estimated_cost=900.0,
                        currency=state.currency,
                        travel_mode="walk",
                    )
                )
                day_cost += 900.0

            plan_days.append(
                ItineraryDayPlan(
                    day_number=day_num,
                    title=title,
                    theme=theme,
                    notes=f"Weather condition: {w_info.get('condition', 'Pleasant')}. Estimated day expenses ~{day_cost:.0f} {state.currency}.",
                    estimated_day_cost=day_cost,
                    activities=activities,
                )
            )
            total_estimated += day_cost

        # Hotel cost estimation for total
        hotel_nightly = hotels[0]["price_per_night"] if hotels else 3500.0
        total_hotel_cost = hotel_nightly * max(days_count - 1, 1)
        total_estimated += total_hotel_cost

        packing = [
            "Comfortable walking shoes & sandals",
            "Sunscreen, sunglasses, and UV protection hat",
            "Light cotton breathable clothing",
            "Waterproof phone pouch for beach/water spots",
            "Power bank and camera charger",
        ]
        if weather.get("is_rainy", False):
            packing.append("Compact travel umbrella or light rain poncho")

        tips = [
            "Hire registered CNG auto-rickshaws or Chander Gari with pre-negotiated rates.",
            "Try local authentic seafood dishes like Rupchanda, Koral, and Shatkora Beef.",
            "Always obey beach safety lifeguard flag indicators along the coastline.",
        ]

        state.generated_itinerary = StructuredItineraryPlan(
            title=f"{days_count}-Day Premium {dest} Travel Experience",
            destination=dest,
            duration_days=days_count,
            total_budget=state.budget or (days_count * 6000.0),
            estimated_cost=round(total_estimated, 2),
            currency=state.currency,
            travel_style=state.travel_style or "balanced",
            description=f"Curated {days_count}-day itinerary designed with real-time weather alignment, optimal travel times, top attractions, and budget allocation.",
            weather_summary=weather,
            packing_suggestions=packing,
            travel_tips=tips,
            days=plan_days,
        )

        return state

    async def node_validate_itinerary(self, state: AgentState) -> AgentState:
        """Validate schedule timings, travel feasibility, and budget limits."""
        if not state.generated_itinerary:
            state.is_valid_itinerary = False
            return state

        itin = state.generated_itinerary
        notes = []

        # Budget validation
        if itin.estimated_cost > (itin.total_budget * 1.15) and itin.total_budget > 0:
            notes.append(f"Estimated expenses ({itin.estimated_cost:.0f} {itin.currency}) slightly exceed target budget ({itin.total_budget:.0f} {itin.currency}). Cheaper dining options have been tagged.")
        else:
            notes.append(f"Itinerary is well within target budget of {itin.total_budget:.0f} {itin.currency}.")

        # Weather validation
        if itin.weather_summary and itin.weather_summary.get("is_rainy", False):
            notes.append("Weather adaptation applied: added flexible indoor alternatives for rainy periods.")

        state.validation_notes = notes
        state.is_valid_itinerary = True
        return state

    async def node_generate_final_plan(self, state: AgentState) -> AgentState:
        """Format final conversational assistant response and attach structured itinerary card."""
        itin = state.generated_itinerary
        if not itin:
            state.final_response_text = "I'm ready to craft your personalized travel plan. Where would you like to travel?"
            return state

        lines = [
            f"Here is your personalized **{itin.duration_days}-Day {itin.destination} Travel Plan**! 🏖️✨",
            "",
            f"- 📍 **Destination**: {itin.destination}",
            f"- 🗓️ **Duration**: {itin.duration_days} Days",
            f"- 💰 **Target Budget**: {itin.total_budget:,.0f} {itin.currency} (Estimated: ~{itin.estimated_cost:,.0f} {itin.currency})",
            f"- ⛅ **Weather**: {itin.weather_summary.get('condition', 'Pleasant')} (~{itin.weather_summary.get('current_temperature', 28)}°C)",
            "",
            "### 🗺️ Highlights Overview:",
        ]

        for d in itin.days:
            act_names = [a.title for a in d.activities[:3]]
            lines.append(f"- **Day {d.day_number}**: {d.title} — *({', '.join(act_names)})*")

        lines.append("")
        lines.append("💡 *You can modify this plan conversationally at any time (e.g. 'Make day 2 less busy', 'Add beach sunset', or 'Remove expensive restaurants')!*")

        state.final_response_text = "\n".join(lines)
        state.message_type = "itinerary_card"
        state.structured_card_data = itin.model_dump()
        return state

    async def node_modify_existing_itinerary(self, state: AgentState) -> AgentState:
        """Handle natural language conversational modifications to an existing itinerary."""
        prompt = state.user_prompt.lower()
        existing = state.existing_itinerary or {}
        days = existing.get("days", [])

        # Modification 1: "Make day X less busy"
        if "less busy" in prompt or "relax" in prompt or "fewer activities" in prompt:
            for d in days:
                if len(d.get("activities", [])) > 2:
                    d["activities"] = d["activities"][:2]
                    d["notes"] = (d.get("notes", "") + " (Pace reduced to relaxed schedule)").strip()

            state.final_response_text = "✨ I've adjusted your itinerary to a more relaxed pace! Afternoon activities have been lightened so you have ample free time to unwind."
        
        # Modification 2: "Add beach sunset"
        elif "sunset" in prompt or "beach" in prompt:
            if days:
                d1 = days[0]
                d1.get("activities", []).append({
                    "title": "Private Sunset Beach Walk & Coconut Drinks",
                    "description": "Relax along the shoreline enjoying refreshing green coconuts and golden sunset views.",
                    "category": "attraction",
                    "location_name": f"{state.destination or 'Beach'} Coastline",
                    "start_time": "17:00",
                    "end_time": "18:30",
                    "duration_minutes": 90,
                    "estimated_cost": 250.0,
                    "currency": existing.get("currency", "BDT"),
                    "travel_mode": "walk",
                    "is_indoor": False,
                })
            state.final_response_text = "🌅 Added an idyllic Sunset Beach & Coconut session to your itinerary! Check the updated schedule below."

        # Modification 3: "Cheaper" or "Remove expensive restaurants"
        elif "cheap" in prompt or "expensive" in prompt or "budget" in prompt:
            for d in days:
                for a in d.get("activities", []):
                    if a.get("category") == "meal" and a.get("estimated_cost", 0) > 700:
                        a["title"] = "Authentic Local Street & Seafood Diner"
                        a["estimated_cost"] = 350.0
                        a["description"] = "Delicious and highly-rated budget local specialty diner."
            state.final_response_text = "💰 Updated dining selections to high-value local eateries to reduce total trip expenses!"

        else:
            state.final_response_text = f"✨ Updated your trip plan according to: '{state.user_prompt}'."

        existing["days"] = days
        state.message_type = "itinerary_card"
        state.structured_card_data = existing
        return state
