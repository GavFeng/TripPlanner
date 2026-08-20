from app.services.weather_service import WeatherService

def test_weather_service_tokyo():

    print("\n===== WEATHER SERVICE TEST =====")

    service = WeatherService()

    result = service.get_forecast(
        city="Tokyo",
        days=2,
    )

    print("Weather result:")
    print(result)

    assert result is not None
    assert result["city"] == "Tokyo"
    assert "forecast" in result
    assert "time" in result["forecast"]