from typing import Dict, Any


class HotelCalculator:
    """Calculate hotel costs for a city itinerary."""

    @staticmethod
    def calculate_city_cost(
        hotel: Dict[str, Any],
        days: int,
    ) -> Dict[str, Any]:

        if days <= 0:
            raise ValueError("Days must be greater than zero.")

        nightly_price = hotel["pricePerNight"]

        total_cost = nightly_price * days

        return {
            "hotel_id": hotel["id"],
            "hotel_name": hotel["name"],
            "city": hotel.get("city"),
            "days": days,
            "price_per_night": nightly_price,
            "total_cost": total_cost,
        }

    @staticmethod
    def calculate_total(
        hotels_by_city: Dict[str, Dict[str, Any]],
        days_by_city: Dict[str, int],
    ) -> Dict[str, Any]:

        hotels = []
        total_cost = 0

        for city, days in days_by_city.items():

            hotel = hotels_by_city.get(city)

            if not hotel:
                continue

            result = HotelCalculator.calculate_city_cost(
                hotel,
                days,
            )

            hotels.append(result)
            total_cost += result["total_cost"]

        return {
            "hotels": hotels,
            "hotel_cost": total_cost,
        }