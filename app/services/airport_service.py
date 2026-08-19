from typing import Dict, Any, List, Optional

from app.services.mock_data_service import MockDataService


class AirportService:

    @classmethod
    def find_by_code(
        cls,
        airport_code: str
    ) -> Optional[Dict[str, Any]]:
        """
        Find an airport by its IATA airport code.

        Example:
            HND -> Tokyo Haneda Airport
            SEA -> Seattle-Tacoma International Airport
        """

        code = airport_code.strip().upper()

        if not code:
            return None

        airports = MockDataService.get_airports()

        for airport in airports:
            if airport.get("code", "").upper() == code:
                return airport

        return None

    @classmethod
    def find_by_city(
        cls,
        city_name: str
    ) -> List[Dict[str, Any]]:
        """
        Find all airports serving a city.

        Example:
            Tokyo -> [HND, NRT]
            Osaka -> [KIX]
        """

        city = city_name.strip().lower()

        if not city:
            return []

        airports = MockDataService.get_airports()

        return [
            airport
            for airport in airports
            if airport.get("city", "").strip().lower() == city
        ]