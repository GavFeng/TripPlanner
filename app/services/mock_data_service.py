import json
import os
from typing import Dict, List, Any, Optional


class MockDataService:

    @staticmethod
    def _load_json(filename: str) -> Any:
        """Safely load a JSON file from the app/data directory."""
        base_path = os.path.join(os.path.dirname(__file__), "..", "data")
        file_path = os.path.abspath(os.path.join(base_path, filename))

        if not os.path.exists(file_path):
            print(f"⚠️ Warning: Mock data file not found at {file_path}")
            return {}

        try:
            with open(file_path, "r", encoding="utf-8") as f:
                return json.load(f)

        except json.JSONDecodeError as e:
            print(f"❌ Invalid JSON in {filename}: {e}")
            return {}

        except OSError as e:
            print(f"❌ Error reading {filename}: {e}")
            return {}

    # -------------------------
    # Airports
    # -------------------------

    @classmethod
    def get_airports(cls) -> List[Dict[str, Any]]:
        data = cls._load_json("airports.json")
        return data.get("airports", [])

    # -------------------------
    # Cities
    # -------------------------

    @classmethod
    def get_city_info(
        cls,
        city_name: str
    ) -> Optional[Dict[str, Any]]:

        data = cls._load_json("cities.json")

        return data.get(city_name)

    @classmethod
    def get_all_cities(cls) -> Dict[str, Any]:
        return cls._load_json("cities.json")

    # -------------------------
    # Destinations
    # -------------------------

    @classmethod
    def get_destinations_by_city(
        cls,
        city_name: str
    ) -> List[Dict[str, Any]]:

        data = cls._load_json("destinations.json")

        return data.get(city_name, [])

    # -------------------------
    # Flights
    # -------------------------

    @classmethod
    def get_flights(cls) -> List[Dict[str, Any]]:
        """
        Retrieve all mock flights.
        """
        data = cls._load_json("flights.json")

        return data.get("flights", [])

    # -------------------------
    # Hotels
    # -------------------------

    @classmethod
    def get_hotels_by_city(
        cls,
        city_name: str
    ) -> List[Dict[str, Any]]:

        data = cls._load_json("hotels.json")

        return data.get(city_name, [])
    
    @classmethod
    def get_all_hotels(cls) -> Dict[str, Any]:
        """Retrieve all hotels grouped by city."""
        return cls._load_json("hotels.json")

    # -------------------------
    # Restaurants
    # -------------------------

    @classmethod
    def get_restaurants_by_city(
        cls,
        city_name: str
    ) -> List[Dict[str, Any]]:

        data = cls._load_json("restaurants.json")

        return data.get(city_name, [])
    
    # -------------------------
    # Transportation
    # -------------------------

    @classmethod
    def get_transportation_routes(
        cls
    ) -> List[Dict[str, Any]]:
        data = cls._load_json("transportation.json")
        return data.get("routes", [])

    @classmethod
    def find_route(cls, origin: str, destination: str) -> List[Dict[str, Any]]:
        """
        Finds transportation options between an origin and destination city.
        """
        routes = cls.get_transportation_routes()
        print(f"DEBUG: Loaded {len(routes)} routes from JSON. Searching {origin} -> {destination}")
        for route in routes:
            if (
                route.get("from", "").strip().lower() == origin.strip().lower() and
                route.get("to", "").strip().lower() == destination.strip().lower()
            ):
                return route.get("options", [])
        return []