from typing import Dict, List, Any, Optional

from app.services.mock_data_service import MockDataService


class TransportationService:

    @staticmethod
    def find_route(
        origin: str,
        destination: str
    ) -> List[Dict[str, Any]]:
        """
        Find transportation options between two cities.
        Returns a list of option dictionaries.
        """
        routes = MockDataService.get_transportation_routes()

        origin = origin.strip().lower()
        destination = destination.strip().lower()

        for route in routes:
            if (
                route.get("from", "").strip().lower() == origin
                and
                route.get("to", "").strip().lower() == destination
            ):
                # ✅ Return the options list so the calculator can iterate through it
                return route.get("options", [])

        return []