from typing import Dict, Any, Optional

from app.services.mock_data_service import MockDataService


class CityService:

    @staticmethod
    def find_by_name(
        city_name: str
    ) -> Optional[Dict[str, Any]]:
        """
        Find a city by name.
        """

        cities = MockDataService.get_all_cities()

        for name, city in cities.items():
            if name.lower() == city_name.strip().lower():
                return {
                    "name": name,
                    **city
                }

        return None