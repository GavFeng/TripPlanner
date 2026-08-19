from typing import List, Dict, Any


class RouteSelector:
    """Select the best X candidate routes."""

    @staticmethod
    def select_top_x(
        routes: List[Dict[str, Any]],
        top_x: int = 5,
        sort_by: str = "transport_cost",
    ) -> List[Dict[str, Any]]:
        """
        Return the top X routes based on a metric.

        Expected route format:

        {
            "path": ["Tokyo", "Kyoto", "Osaka", "Tokyo"],
            "transport_cost": 190,
            "transport_hours": 3.5
        }
        """

        if top_x <= 0:
            return []

        sorted_routes = sorted(
            routes,
            key=lambda route: route.get(sort_by, float("inf"))
        )

        selected = sorted_routes[:top_x]

        for index, route in enumerate(selected, start=1):
            route["rank"] = index

        return selected