from typing import Dict, Any


class BudgetValidator:
    """Determine whether an itinerary fits within a budget."""

    @staticmethod
    def validate(
        total_cost: float,
        budget: float,
    ) -> Dict[str, Any]:

        remaining = budget - total_cost

        return {
            "budget": budget,
            "total_cost": total_cost,
            "remaining": remaining,
            "within_budget": remaining >= 0,
            "over_budget": max(0, -remaining),
        }