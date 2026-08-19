from typing import List, Dict, Any


class RankingService:

    @staticmethod
    def _normalize(
        value: float,
        minimum: float,
        maximum: float,
        lower_is_better: bool = True
    ) -> float:
        if maximum == minimum:
            return 100.0

        if lower_is_better:
            return 100.0 * (maximum - value) / (maximum - minimum)

        return 100.0 * (value - minimum) / (maximum - minimum)

    @classmethod
    def rank(
        cls,
        items: List[Dict[str, Any]],
        weights: Dict[str, float],
        lower_is_better: Dict[str, bool]
    ) -> List[Dict[str, Any]]:
        if not items:
            return []
        if not weights:
            raise ValueError("Weights cannot be empty.")

        if any(weight < 0 for weight in weights.values()):
            raise ValueError("Weights cannot be negative.")

        
        # Normalize weights so they sum to 1.0 to prevent scaling distortion
        total_weight = sum(weights.values())

        if total_weight <= 0:
            raise ValueError("Sum of weights must be greater than zero.")

        normalized_weights = {
            criterion: weight / total_weight
            for criterion, weight in weights.items()
        }

        # Calculate min/max ranges for criteria present in items
        ranges = {}
        for criterion in weights:
            values = [
                item[criterion]
                for item in items
                if criterion in item and isinstance(item[criterion], (int, float))
            ]
            if values:
                ranges[criterion] = {
                    "min": min(values),
                    "max": max(values)
                }

        ranked_items = []

        for item in items:
            total_score = 0.0
            criterion_scores = {}
            active_weight_sum = 0.0

            # First pass: calculate scores for criteria present in both item and ranges
            for criterion, weight in normalized_weights.items():
                if criterion not in item or criterion not in ranges:
                    continue

                value = item[criterion]
                minimum = ranges[criterion]["min"]
                maximum = ranges[criterion]["max"]

                score = cls._normalize(
                    value,
                    minimum,
                    maximum,
                    lower_is_better.get(criterion, True)
                )

                criterion_scores[criterion] = round(score, 2)
                total_score += score * weight
                active_weight_sum += weight

            # Adjust score if some criteria were missing from this specific item
            if active_weight_sum > 0 and active_weight_sum < 1.0:
                total_score = total_score / active_weight_sum

            ranked_item = {
                **item,
                "score": round(total_score, 2),
                "criterionScores": criterion_scores
            }
            ranked_items.append(ranked_item)

        # Sort highest score first
        ranked_items.sort(key=lambda x: x["score"], reverse=True)

        # Assign positions
        for index, item in enumerate(ranked_items, start=1):
            item["rank"] = index

        return ranked_items