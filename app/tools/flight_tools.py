import json
from typing import Any, Dict, List, Optional

from crewai.tools import tool

from app.services.airport_service import AirportService
from app.services.mock_data_service import MockDataService
from app.services.ranking_service import RankingService


def _resolve_origin_airport(
    value: str
) -> Optional[Dict[str, Any]]:
    """
    Resolve the traveler's origin to an airport.

    The origin should normally be an airport code,
    such as SEA.
    """

    value = value.strip()

    if not value:
        return None

    return AirportService.find_by_code(value)


def _get_japan_airports() -> List[Dict[str, Any]]:
    """
    Get all supported airports in Japan.

    These airports are used as possible international
    entry and exit points for the Japan trip.
    """

    airports = MockDataService.get_airports()

    return [
        airport
        for airport in airports
        if airport.get("country", "").strip().lower() == "japan"
    ]


def _find_flights(
    flights: List[Dict[str, Any]],
    origin_codes: set[str],
    destination_codes: set[str]
) -> List[Dict[str, Any]]:
    """
    Find flights between sets of airports.
    """

    return [
        flight
        for flight in flights
        if (
            flight.get("origin", "").upper() in origin_codes
            and
            flight.get("destination", "").upper()
            in destination_codes
        )
    ]


def _rank_flights(
    flights: List[Dict[str, Any]]
) -> List[Dict[str, Any]]:
    """
    Rank flights by price, duration, and stops.
    """

    weights = {
        "price": 0.40,
        "durationHours": 0.35,
        "stops": 0.25
    }

    lower_is_better = {
        "price": True,
        "durationHours": True,
        "stops": True
    }

    return RankingService.rank(
        items=flights,
        weights=weights,
        lower_is_better=lower_is_better
    )


def _airport_summary(
    airport: Dict[str, Any]
) -> Dict[str, Any]:
    """
    Return the relevant airport information.
    """

    return {
        "airportCode": airport["code"],
        "airportName": airport["name"],
        "city": airport["city"],
        "country": airport["country"]
    }


def _add_airport_information(
    flights: List[Dict[str, Any]],
    airports: List[Dict[str, Any]]
) -> List[Dict[str, Any]]:
    """
    Add airport information to each flight.
    """

    airport_lookup = {
        airport["code"].upper(): airport
        for airport in airports
    }

    for flight in flights:
        origin_code = flight.get(
            "origin",
            ""
        ).upper()

        destination_code = flight.get(
            "destination",
            ""
        ).upper()

        origin_airport = airport_lookup.get(origin_code)
        destination_airport = airport_lookup.get(
            destination_code
        )

        if origin_airport:
            flight["originAirport"] = _airport_summary(
                origin_airport
            )

        if destination_airport:
            flight["destinationAirport"] = _airport_summary(
                destination_airport
            )

    return flights


@tool("Search and Rank Japan Flights")
def search_japan_flights(
    origin: str
) -> str:
    """
    Search and rank international flights between the
    traveler's origin and all supported airports in Japan.

    The tool does NOT select a Japan destination city.

    It searches both directions:

        Origin -> every Japan airport
        Every Japan airport -> Origin

    The route planner can then determine whether the
    cheapest itinerary should enter Japan through one city
    and leave through another.

    Example:

        SEA -> HND
        SEA -> NRT
        SEA -> KIX

        HND -> SEA
        NRT -> SEA
        KIX -> SEA
    """

    # --------------------------------------------------
    # 1. Resolve origin airport
    # --------------------------------------------------

    origin_airport = _resolve_origin_airport(origin)

    if not origin_airport:
        return json.dumps({
            "success": False,
            "message": (
                f"Origin airport '{origin}' was not found."
            ),
            "outboundFlights": [],
            "returnFlights": []
        })

    origin_code = origin_airport["code"].upper()

    # --------------------------------------------------
    # 2. Find all supported Japan airports
    # --------------------------------------------------

    japan_airports = _get_japan_airports()

    if not japan_airports:
        return json.dumps({
            "success": False,
            "origin": origin_code,
            "message": (
                "No supported Japan airports were found."
            ),
            "outboundFlights": [],
            "returnFlights": []
        })

    japan_codes = {
        airport["code"].upper()
        for airport in japan_airports
    }

    origin_codes = {origin_code}

    # --------------------------------------------------
    # 3. Retrieve flights
    # --------------------------------------------------

    flights = MockDataService.get_flights()

    # --------------------------------------------------
    # 4. Find outbound flights
    #
    # Origin -> Any Japan airport
    # --------------------------------------------------

    outbound_flights = _find_flights(
        flights=flights,
        origin_codes=origin_codes,
        destination_codes=japan_codes
    )

    # --------------------------------------------------
    # 5. Find return flights
    #
    # Any Japan airport -> Origin
    # --------------------------------------------------

    return_flights = _find_flights(
        flights=flights,
        origin_codes=japan_codes,
        destination_codes=origin_codes
    )

    # --------------------------------------------------
    # 6. Add airport information
    # --------------------------------------------------

    all_relevant_airports = (
        [origin_airport] +
        japan_airports
    )

    outbound_flights = _add_airport_information(
        flights=outbound_flights,
        airports=all_relevant_airports
    )

    return_flights = _add_airport_information(
        flights=return_flights,
        airports=all_relevant_airports
    )

    # --------------------------------------------------
    # 7. Rank outbound flights
    # --------------------------------------------------

    ranked_outbound = _rank_flights(
        outbound_flights
    ) if outbound_flights else []

    # --------------------------------------------------
    # 8. Rank return flights
    # --------------------------------------------------

    ranked_return = _rank_flights(
        return_flights
    ) if return_flights else []

    # --------------------------------------------------
    # 9. Return flight data
    # --------------------------------------------------

    return json.dumps({
        "success": True,

        "origin": _airport_summary(
            origin_airport
        ),

        "japanAirports": [
            _airport_summary(airport)
            for airport in japan_airports
        ],

        "outbound": {
            "count": len(ranked_outbound),
            "flights": ranked_outbound
        },

        "return": {
            "count": len(ranked_return),
            "flights": ranked_return
        }
    })