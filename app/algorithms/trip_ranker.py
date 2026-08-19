from typing import List, Dict, Any


class TripRanker:
    """Rank complete trip itineraries."""

    @staticmethod
    def rank(
        trips: List[Dict[str, Any]],
        budget: float,
    ) -> List[Dict[str, Any]]:

        for trip in trips:

            total_cost = trip["total_cost"]

            if total_cost <= budget:
                budget_score = 1.0
            else:
                budget_score = 0.0

            # Reward trips that stay under budget.
            savings = max(0, budget - total_cost)

            trip["savings"] = savings
            trip["budget_score"] = budget_score

            # Initial simple score.
            #
            # Later this can incorporate:
            # - transportation time
            # - hotel rating
            # - city preferences
            # - destination quality
            # - weather
            # - savings
            trip["score"] = (
                budget_score * 100
                + savings * 0.01
            )

        return sorted(
            trips,
            key=lambda trip: trip["score"],
            reverse=True,
        )