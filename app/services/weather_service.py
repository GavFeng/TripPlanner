import requests


class WeatherService:

    BASE_URL = "https://api.open-meteo.com/v1/forecast"
    GEOCODING_URL = "https://geocoding-api.open-meteo.com/v1/search"

    def get_coordinates(self, city: str) -> dict:

        response = requests.get(
            self.GEOCODING_URL,
            params={
                "name": city,
                "count": 1,
                "language": "en",
                "format": "json",
            },
            timeout=10,
        )

        response.raise_for_status()

        data = response.json()

        results = data.get("results", [])

        if not results:
            raise ValueError(
                f"Could not find coordinates for {city}"
            )

        location = results[0]

        return {
            "city": location["name"],
            "latitude": location["latitude"],
            "longitude": location["longitude"],
            "timezone": location.get("timezone"),
        }

    def get_forecast(
        self,
        city: str,
        days: int = 7,
    ) -> dict:

        location = self.get_coordinates(city)

        response = requests.get(
            self.BASE_URL,
            params={
                "latitude": location["latitude"],
                "longitude": location["longitude"],
                "daily": (
                    "temperature_2m_max,"
                    "temperature_2m_min,"
                    "precipitation_sum,"
                    "precipitation_probability_max,"
                    "weather_code"
                ),
                "forecast_days": days,
                "timezone": "auto",
            },
            timeout=10,
        )

        response.raise_for_status()

        return {
            "city": location["city"],
            "latitude": location["latitude"],
            "longitude": location["longitude"],
            "timezone": location["timezone"],
            "forecast": response.json().get("daily", {}),
        }