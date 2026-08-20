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

    assert len(data["weather"]) == 4

    assert data["weather"][0]["city"] == "Tokyo"
    assert data["weather"][1]["city"] == "Hiroshima"
    assert data["weather"][2]["city"] == "Kyoto"
    assert data["weather"][3]["city"] == "Osaka"

    assert data["weather"][0]["days"] == 2
    assert data["weather"][1]["days"] == 2
    assert data["weather"][2]["days"] == 2
    assert data["weather"][3]["days"] == 4