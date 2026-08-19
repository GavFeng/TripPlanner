import json

from crewai.tools import tool

from app.services.transportation_service import TransportationService


@tool("Search Transportation Between Cities")
def search_transportation(
    origin: str,
    destination: str
) -> str:
    """
    Find available transportation options between two cities.

    Returns:
        JSON string containing transportation options.
    """

    route = TransportationService.find_route(
        origin,
        destination
    )

    if not route:
        return json.dumps({
            "success": False,
            "origin": origin,
            "destination": destination,
            "message": (
                f"No transportation route found from "
                f"{origin} to {destination}."
            ),
            "options": []
        })

    return json.dumps({
        "success": True,
        "origin": route["from"],
        "destination": route["to"],
        "options": route.get("options", [])
    })