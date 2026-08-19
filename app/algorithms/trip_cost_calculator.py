from typing import Dict, Any


class TripCostCalculator:
    """Calculate total trip cost."""

    @staticmethod
    def calculate(
        flight_cost: float,
        transportation_cost: float,
        hotel_cost: float,
        other_costs: float = 0,
    ) -> Dict[str, Any]:

        total_cost = (
            flight_cost
            + transportation_cost
            + hotel_cost
            + other_costs
        )

        return {
            "flight_cost": flight_cost,
            "transportation_cost": transportation_cost,
            "hotel_cost": hotel_cost,
            "other_costs": other_costs,
            "total_cost": total_cost,
        }