import json

from crewai.tools import tool

from app.services.weather_service import WeatherService


weather_service = WeatherService()


# ============================================================
# Weather interpretation helpers
# ============================================================

def weather_code_to_condition(code: int) -> str:
    """
    Convert WMO weather codes into human-readable conditions.
    """

    if code == 0:
        return "Clear"

    if code in [1, 2, 3]:
        return "Partly cloudy"

    if code in [45, 48]:
        return "Foggy"

    if code in [51, 53, 55]:
        return "Drizzle"

    if code in [56, 57]:
        return "Freezing drizzle"

    if code in [61, 63, 65]:
        return "Rain"

    if code in [66, 67]:
        return "Freezing rain"

    if code in [71, 73, 75, 77]:
        return "Snow"

    if code in [80, 81, 82]:
        return "Rain showers"

    if code in [85, 86]:
        return "Snow showers"

    if code in [95, 96, 99]:
        return "Thunderstorm"

    return "Unknown"


def determine_outdoor_suitability(
    high_temperature: float,
    rain_probability: int,
    precipitation: float,
    condition: str,
) -> str:
    """
    Give the Destination Agent a simple indication of
    how suitable the day is for outdoor activities.
    """

    # Extreme heat
    if high_temperature >= 35:
        return "poor"

    # Thunderstorms
    if "Thunderstorm" in condition:
        return "poor"

    # Very high chance of rain
    if rain_probability >= 80:
        return "poor"

    # Significant rain
    if precipitation >= 5:
        return "poor"

    # Moderate weather concerns
    if high_temperature >= 33:
        return "moderate"

    if rain_probability >= 60:
        return "moderate"

    if precipitation >= 2:
        return "moderate"

    return "good"


def get_weather_recommendations(
    high_temperature: float,
    rain_probability: int,
    precipitation: float,
    condition: str,
    outdoor_suitability: str,
) -> list[str]:
    """
    Generate simple recommendations that the Destination Agent
    can use when selecting activities.
    """

    recommendations = []

    if outdoor_suitability == "poor":
        recommendations.append("Prefer indoor activities")

    elif outdoor_suitability == "moderate":
        recommendations.append(
            "Mix indoor and outdoor activities"
        )

    else:
        recommendations.append(
            "Good day for outdoor sightseeing"
        )

    if high_temperature >= 35:
        recommendations.append(
            "Avoid prolonged outdoor activities during peak heat"
        )

    elif high_temperature >= 33:
        recommendations.append(
            "Schedule outdoor activities during cooler hours"
        )

    if rain_probability >= 80:
        recommendations.append(
            "Have an indoor backup plan"
        )

    elif rain_probability >= 60:
        recommendations.append(
            "Consider flexible outdoor activities"
        )

    if precipitation >= 5:
        recommendations.append(
            "Avoid activities that depend on dry weather"
        )

    if "Thunderstorm" in condition:
        recommendations.append(
            "Avoid outdoor activities"
        )

    return recommendations


# ============================================================
# Weather Tool
# ============================================================

@tool("Get Weather")
def get_weather(
    itinerary: list[dict],
) -> str:
    """
    Get weather forecasts for each city in the planned trip.

    The weather is returned in a simplified format designed
    for the Destination Agent.

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
    # 2. Get and simplify weather for each city
    # ==================================================

    results = []

    for stop in itinerary:

        if not isinstance(stop, dict):
            continue

        city = stop.get("city")
        days = stop.get("days")

        # ----------------------------------------------
        # Validate city
        # ----------------------------------------------

        if not isinstance(city, str) or not city.strip():
            continue

        city = city.strip()

        # ----------------------------------------------
        # Validate days
        # ----------------------------------------------

        if isinstance(days, str):
            try:
                days = int(days)
            except ValueError:
                continue

        if not isinstance(days, int) or days <= 0:
            continue

        # ----------------------------------------------
        # Get forecast
        # ----------------------------------------------

        try:
            weather = weather_service.get_forecast(
                city=city,
                days=days,
            )

            forecast = weather.get("forecast", {})

            times = forecast.get("time", [])
            max_temperatures = forecast.get(
                "temperature_2m_max",
                [],
            )
            min_temperatures = forecast.get(
                "temperature_2m_min",
                [],
            )
            precipitation = forecast.get(
                "precipitation_sum",
                [],
            )
            rain_probability = forecast.get(
                "precipitation_probability_max",
                [],
            )
            weather_codes = forecast.get(
                "weather_code",
                [],
            )

            daily_forecast = []

            # ------------------------------------------
            # Convert parallel arrays into daily objects
            # ------------------------------------------

            for i, date in enumerate(times):

                high = max_temperatures[i]
                low = min_temperatures[i]
                rain_mm = precipitation[i]
                rain_chance = rain_probability[i]
                weather_code = weather_codes[i]

                condition = weather_code_to_condition(
                    weather_code
                )

                outdoor_suitability = (
                    determine_outdoor_suitability(
                        high_temperature=high,
                        rain_probability=rain_chance,
                        precipitation=rain_mm,
                        condition=condition,
                    )
                )

                recommendations = (
                    get_weather_recommendations(
                        high_temperature=high,
                        rain_probability=rain_chance,
                        precipitation=rain_mm,
                        condition=condition,
                        outdoor_suitability=outdoor_suitability,
                    )
                )

                daily_forecast.append({
                    "date": date,
                    "temperature": {
                        "high": high,
                        "low": low,
                    },
                    "rain": {
                        "probability": rain_chance,
                        "amount_mm": rain_mm,
                    },
                    "condition": condition,
                    "outdoor_suitability": (
                        outdoor_suitability
                    ),
                    "recommendations": recommendations,
                })

            results.append({
                "city": city,
                "days": daily_forecast,
            })

        except Exception as e:

            results.append({
                "city": city,
                "error": str(e),
            })

    # ==================================================
    # 3. Validate results
    # ==================================================

    successful_results = [
        result
        for result in results
        if "days" in result
    ]

    if not successful_results:
        return json.dumps({
            "success": False,
            "message": (
                "No weather forecasts could be retrieved."
            )
        })

    # ==================================================
    # 4. Return simplified weather
    # ==================================================

    return json.dumps({
        "success": True,
        "weather": results,
    })