import json

from crewai.tools import tool

from app.services.weather_service import WeatherService


weather_service = WeatherService()


@tool("Get Weather")
def get_weather(
    itinerary: list[dict],
) -> str:
    """
    Get weather forecasts for each city in the planned trip.

    The itinerary must contain cities in travel order and
    the number of days spent in each city.

    Example:
    [
        {"city": "Tokyo", "days": 2},
        {"city": "Hiroshima", "days": 2},
        {"city": "Kyoto", "days": 2},
        {"city": "Osaka", "days": 4}
    ]
    """

    # ==================================================
    # 1. Sanitize itinerary
    # ==================================================

    if isinstance(itinerary, str):
        try:
            itinerary = json.loads(itinerary)
        except json.JSONDecodeError:
            return json.dumps({
                "success": False,
                "message": "itinerary must be a valid JSON list."
            })

    if not isinstance(itinerary, list):
        return json.dumps({
            "success": False,
            "message": (
                f"itinerary must be a list, "
                f"got {type(itinerary).__name__}"
            )
        })

    if not itinerary:
        return json.dumps({
            "success": False,
            "message": "Itinerary cannot be empty."
        })

    # ==================================================
    # 2. Get weather for each destination
    # ==================================================

    results = []

    for stop in itinerary:

        if not isinstance(stop, dict):
            continue

        city = stop.get("city")
        days = stop.get("days")

        if not isinstance(city, str) or not city.strip():
            continue

        if isinstance(days, str):
            try:
                days = int(days)
            except ValueError:
                continue

        if not isinstance(days, int) or days <= 0:
            continue
        city = city.strip()
        try:
            weather = weather_service.get_forecast(
                city=city,
                days=days,
            )

            results.append({
                "city": city,
                "days": days,
                "weather": weather,
            })

        except Exception as e:

            results.append({
                "city": city,
                "days": days,
                "error": str(e),
            })

    # ==================================================
    # 3. Validate results
    # ==================================================

    if not results:
        return json.dumps({
            "success": False,
            "message": "No weather forecasts could be retrieved."
        })

    return json.dumps({
        "success": True,
        "weather": results,
    })