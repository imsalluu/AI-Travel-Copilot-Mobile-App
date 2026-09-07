import math
from typing import List, Dict, Any, Optional, Tuple


class MapService:
    """Map service abstraction providing geocoding, distance matrix, and route polylines."""

    @staticmethod
    def calculate_haversine_distance_km(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
        """Calculate Great Circle distance between two points in km."""
        r = 6371.0  # Earth radius in kilometers
        d_lat = math.radians(lat2 - lat1)
        d_lon = math.radians(lon2 - lon1)
        a = (
            math.sin(d_lat / 2) ** 2
            + math.cos(math.radians(lat1))
            * math.cos(math.radians(lat2))
            * math.sin(d_lon / 2) ** 2
        )
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
        return round(r * c, 2)

    @classmethod
    def estimate_travel_time_minutes(
        cls,
        lat1: float,
        lon1: float,
        lat2: float,
        lon2: float,
        mode: str = "drive"
    ) -> int:
        """Estimate travel duration between two coordinates based on travel mode."""
        dist_km = cls.calculate_haversine_distance_km(lat1, lon1, lat2, lon2)
        if dist_km == 0:
            return 0

        # Speeds in km/h including traffic/stops heuristics
        speeds = {
            "walk": 4.5,
            "drive": 30.0,
            "transit": 22.0,
            "boat": 18.0,
            "flight": 450.0,
        }
        speed = speeds.get(mode.lower(), 30.0)
        hours = dist_km / speed
        minutes = int(math.ceil(hours * 60.0))
        # Add 5 minutes buffer for parking/transitions if driving/transit
        if mode in ["drive", "transit"] and minutes > 5:
            minutes += 5
        return minutes

    @classmethod
    def generate_route_coordinates(
        cls,
        points: List[Tuple[float, float]],
        num_interpolations: int = 5
    ) -> List[Dict[str, float]]:
        """Generate smooth route polyline coordinate list connecting itinerary waypoints."""
        if not points:
            return []
        if len(points) == 1:
            return [{"latitude": points[0][0], "longitude": points[0][1]}]

        route = []
        for i in range(len(points) - 1):
            p1 = points[i]
            p2 = points[i + 1]
            route.append({"latitude": p1[0], "longitude": p1[1]})
            # Interpolate sub-points for smooth visual lines
            for step in range(1, num_interpolations):
                fraction = step / float(num_interpolations)
                lat = p1[0] + (p2[0] - p1[0]) * fraction
                lon = p1[1] + (p2[1] - p1[1]) * fraction
                route.append({"latitude": round(lat, 6), "longitude": round(lon, 6)})
        route.append({"latitude": points[-1][0], "longitude": points[-1][1]})
        return route


map_service = MapService()
