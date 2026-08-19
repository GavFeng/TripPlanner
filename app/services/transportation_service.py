from typing import Dict, List, Any, Optional

from app.services.mock_data_service import MockDataService


class TransportationService:

    @staticmethod
    def find_route(
        origin: str,
        destination: str
    ) -> Optional[Dict[str, Any]]:
        """
        Find transportation options between two cities.
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
                return route

        return None

    @staticmethod
    def get_options(
        origin: str,
        destination: str
    ) -> List[Dict[str, Any]]:
        route = TransportationService.find_route(
            origin,
            destination
        )

        if not route:
            return []

        return route.get("options", [])