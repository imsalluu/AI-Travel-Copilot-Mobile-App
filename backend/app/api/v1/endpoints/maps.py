from typing import List, Dict, Any
from fastapi import APIRouter, Query, Body
from pydantic import BaseModel
from app.services.map_service import map_service

router = APIRouter()


class Waypoint(BaseModel):
    latitude: float
    longitude: float
    name: str = ""


class RouteRequest(BaseModel):
    waypoints: List[Waypoint]
    travel_mode: str = "drive"


class RouteResponse(BaseModel):
    total_distance_km: float
    total_duration_minutes: int
    travel_mode: str
    route_polyline: List[Dict[str, float]]
    segments: List[Dict[str, Any]]


@router.post("/calculate-route", response_model=RouteResponse)
async def calculate_trip_route(payload: RouteRequest):
    """Calculate distance, travel times, and interpolated map polyline coordinates for waypoints."""
    if not payload.waypoints:
        return RouteResponse(
            total_distance_km=0.0,
            total_duration_minutes=0,
            travel_mode=payload.travel_mode,
            route_polyline=[],
            segments=[],
        )

    points = [(w.latitude, w.longitude) for w in payload.waypoints]
    polyline = map_service.generate_route_coordinates(points)

    total_dist = 0.0
    total_time = 0
    segments = []

    for i in range(len(payload.waypoints) - 1):
        w1 = payload.waypoints[i]
        w2 = payload.waypoints[i + 1]
        dist = map_service.calculate_haversine_distance_km(w1.latitude, w1.longitude, w2.latitude, w2.longitude)
        dur = map_service.estimate_travel_time_minutes(w1.latitude, w1.longitude, w2.latitude, w2.longitude, payload.travel_mode)
        total_dist += dist
        total_time += dur
        segments.append({
            "from_name": w1.name,
            "to_name": w2.name,
            "distance_km": dist,
            "duration_minutes": dur,
        })

    return RouteResponse(
        total_distance_km=round(total_dist, 2),
        total_duration_minutes=total_time,
        travel_mode=payload.travel_mode,
        route_polyline=polyline,
        segments=segments,
    )
