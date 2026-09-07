from fastapi import APIRouter
from app.api.v1.endpoints import (
    auth,
    users,
    trips,
    itinerary,
    destinations,
    weather,
    budget,
    maps,
    knowledge,
    chat,
    voice,
)

api_router = APIRouter()

api_router.include_router(auth.router, prefix="/auth", tags=["Authentication"])
api_router.include_router(users.router, prefix="/users", tags=["Users & Preferences"])
api_router.include_router(trips.router, prefix="/trips", tags=["Trips"])
api_router.include_router(itinerary.router, prefix="/itinerary", tags=["Itinerary"])
api_router.include_router(destinations.router, prefix="/destinations", tags=["Destinations & Places"])
api_router.include_router(weather.router, prefix="/weather", tags=["Weather"])
api_router.include_router(budget.router, prefix="/budget", tags=["Budget & Expenses"])
api_router.include_router(maps.router, prefix="/maps", tags=["Maps & Routing"])
api_router.include_router(knowledge.router, prefix="/knowledge", tags=["RAG Knowledge"])
api_router.include_router(chat.router, prefix="/chat", tags=["AI Copilot Chat"])
api_router.include_router(voice.router, prefix="/voice", tags=["Voice AI"])
