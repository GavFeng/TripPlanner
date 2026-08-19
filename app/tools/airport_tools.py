import json

from crewai.tools import tool

from app.services.airport_service import AirportService


@tool("Find Airport")
def find_airport(airport_code: str) -> str:
    """
    Find airport information by IATA airport code.

    Args:
        airport_code: Three-letter IATA airport code, e.g. SEA or HND.

    Returns:
        JSON string containing airport information.
    """

    airport = AirportService.find_by_code(airport_code)

    if not airport:
        return json.dumps({
            "success": False,
            "airport_code": airport_code.upper(),
            "message": (
                f"Airport '{airport_code.upper()}' was not found."
            )
        })

    return json.dumps({
        "success": True,
        "airport": airport
    })