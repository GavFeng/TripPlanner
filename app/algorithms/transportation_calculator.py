from typing import List, Dict, Any


class TransportationCalculator:
    """Calculate transportation costs for city routes."""

    @staticmethod
    def calculate_route(
        route: List[str],
        transportation_service,
    ) -> Dict[str, Any]:
        """
        Calculate transportation cost and duration
        for every leg of a route.

        The transportation service is expected to provide
        the available options between two cities.
        """

        total_cost = 0
        total_duration = 0
        legs = []

        for index in range(len(route) - 1):
            origin = route[index]
            destination = route[index + 1]

            options = transportation_service.find_route(
                origin,
                destination,
            )

            if not options:
                return {
                    "valid": False,
                    "route": route,
                    "reason": (
                        f"No transportation found from "
                        f"{origin} to {destination}."
                    ),
                }

            # For now, choose cheapest option.
            best_option = min(
                options,
                key=lambda option: option["cost"]
            )

            total_cost += best_option["cost"]
            total_duration += best_option["durationHours"]

            legs.append({
                "from": origin,
                "to": destination,
                "option": best_option,
            })

        return {
            "valid": True,
            "route": route,
            "transport_cost": total_cost,
            "transport_hours": total_duration,
            "legs": legs,
        }