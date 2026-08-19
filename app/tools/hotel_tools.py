import json

from crewai.tools import tool

from app.services.mock_data_service import MockDataService
from app.services.ranking_service import RankingService


@tool("Search and Rank Japan Hotels")
def search_japan_hotels(city: str) -> str:
    """
    Search available mock hotels in a Japanese city and rank them
    based on price, rating, and access to public transportation.

    Args:
        city: Japanese city to search for hotels.

    Returns:
        JSON string containing ranked hotel results.
    """

    # 1. Retrieve hotels for the city
    hotels = MockDataService.get_hotels_by_city(city)

    if not hotels:
        return json.dumps({
            "success": False,
            "message": f"No hotels found in {city}.",
            "city": city,
            "count": 0,
            "hotels": []
        })

    # 2. Ranking preferences
    weights = {
        "pricePerNight": 0.40,
        "rating": 0.40,
        "nearTransit": 0.20
    }

    lower_is_better = {
        "pricePerNight": True,
        "rating": False,
        "nearTransit": False
    }

    # 3. Convert nearTransit boolean to a numeric value
    ranking_hotels = []

    for hotel in hotels:
        ranking_hotel = {
            **hotel,
            "nearTransit": 1 if hotel.get("nearTransit", False) else 0
        }

        ranking_hotels.append(ranking_hotel)

    # 4. Rank hotels
    ranked_hotels = RankingService.rank(
        items=ranking_hotels,
        weights=weights,
        lower_is_better=lower_is_better
    )

    # 5. Convert numeric transit value back to boolean
    for hotel in ranked_hotels:
        hotel["nearTransit"] = bool(hotel["nearTransit"])

    # 6. Return structured JSON
    return json.dumps({
        "success": True,
        "city": city,
        "count": len(ranked_hotels),
        "hotels": ranked_hotels
    })