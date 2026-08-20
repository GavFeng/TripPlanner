from typing import List, Dict, Any
import json


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

            # ==========================================
            # Sanitize and validate option items
            # ==========================================
            valid_options = []
            for opt in options:
                if isinstance(opt, str):
                    try:
                        opt = json.loads(opt)
                    except json.JSONDecodeError:
                        continue
                if isinstance(opt, dict) and "cost" in opt:
                    valid_options.append(opt)

            if not valid_options:
                return {
                    "valid": False,
                    "route": route,
                    "reason": (
                        f"No valid transportation options found from "
                        f"{origin} to {destination}."
                    ),
                }

            # Choose cheapest option from valid dictionaries
            best_option = min(
                valid_options,
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