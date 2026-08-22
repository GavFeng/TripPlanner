import json

from app.tools.weather_tools import get_weather


def test_get_weather_full_trip():

    itinerary = [
        {"city": "Tokyo", "days": 2},
        {"city": "Hiroshima", "days": 2},
        {"city": "Kyoto", "days": 2},
        {"city": "Osaka", "days": 4},
    ]

    result = get_weather.run(
        itinerary=itinerary
    )

    data = json.loads(result)

    print("\n===== FULL JAPAN WEATHER =====")
    print(json.dumps(data, indent=2))

    # ==================================================
    # Basic validation
    # ==================================================

    assert data["success"] is True
    assert len(data["weather"]) == 4

    # ==================================================
    # City validation
    # ==================================================

    assert data["weather"][0]["city"] == "Tokyo"
    assert data["weather"][1]["city"] == "Hiroshima"
    assert data["weather"][2]["city"] == "Kyoto"
    assert data["weather"][3]["city"] == "Osaka"

    # ==================================================
    # Number of forecast days
    # ==================================================

    assert len(data["weather"][0]["days"]) == 2
    assert len(data["weather"][1]["days"]) == 2
    assert len(data["weather"][2]["days"]) == 2
    assert len(data["weather"][3]["days"]) == 4

    # ==================================================
    # Check daily forecast structure
    # ==================================================

    tokyo_day = data["weather"][0]["days"][0]

    assert "date" in tokyo_day
    assert "temperature" in tokyo_day
    assert "rain" in tokyo_day
    assert "condition" in tokyo_day
    assert "outdoor_suitability" in tokyo_day
    assert "recommendations" in tokyo_day

    # ==================================================
    # Check temperature structure
    # ==================================================

    assert "high" in tokyo_day["temperature"]
    assert "low" in tokyo_day["temperature"]

    # ==================================================
    # Check rain structure
    # ==================================================

    assert "probability" in tokyo_day["rain"]
    assert "amount_mm" in tokyo_day["rain"]

    # ==================================================
    # Check outdoor suitability
    # ==================================================

    assert tokyo_day["outdoor_suitability"] in [
        "good",
        "moderate",
        "poor",
    ]

    # ==================================================
    # Check recommendations
    # ==================================================

    assert isinstance(
        tokyo_day["recommendations"],
        list
    )