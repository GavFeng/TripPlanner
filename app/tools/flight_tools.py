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
    Rank flights by price, duration, and number of stops.
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
    Return relevant airport information.
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

        origin_airport = airport_lookup.get(
            origin_code
        )

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


def _top_flights_per_destination(
    flights: List[Dict[str, Any]],
    limit: int = 2
) -> List[Dict[str, Any]]:
    """
    Return the top flights for each destination airport.

    Example:

        SEA -> HND
        SEA -> NRT
        SEA -> KIX

    Each destination airport can contribute up to
    `limit` flights.
    """

    grouped: Dict[str, List[Dict[str, Any]]] = {}

    for flight in flights:

        destination = flight.get(
            "destination",
            ""
        ).upper()

        grouped.setdefault(
            destination,
            []
        ).append(flight)

    result: List[Dict[str, Any]] = []

    for destination_flights in grouped.values():

        ranked = _rank_flights(
            destination_flights
        )

        result.extend(
            ranked[:limit]
        )

    return result


def _top_flights_per_origin(
    flights: List[Dict[str, Any]],
    limit: int = 2
) -> List[Dict[str, Any]]:
    """
    Return the top flights for each origin airport.

    Example:

        HND -> SEA
        NRT -> SEA
        KIX -> SEA

    Each origin airport can contribute up to
    `limit` flights.
    """

    grouped: Dict[str, List[Dict[str, Any]]] = {}

    for flight in flights:

        origin = flight.get(
            "origin",
            ""
        ).upper()

        grouped.setdefault(
            origin,
            []
        ).append(flight)

    result: List[Dict[str, Any]] = []

    for origin_flights in grouped.values():

        ranked = _rank_flights(
            origin_flights
        )

        result.extend(
            ranked[:limit]
        )

    return result


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

    The route planner can use these results to determine
    the cheapest combination of Japan entry and exit cities.

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

    origin_airport = _resolve_origin_airport(
        origin
    )

    if not origin_airport:
        return json.dumps({
            "success": False,
            "message": (
                f"Origin airport '{origin}' was not found."
            ),
            "outbound": {
                "count": 0,
                "flights": []
            },
            "return": {
                "count": 0,
                "flights": []
            }
        })

    origin_code = origin_airport["code"].upper()

    # --------------------------------------------------
    # 2. Get all supported Japan airports
    # --------------------------------------------------

    japan_airports = _get_japan_airports()

    if not japan_airports:
        return json.dumps({
            "success": False,
            "origin": origin_code,
            "message": (
                "No supported Japan airports were found."
            ),
            "outbound": {
                "count": 0,
                "flights": []
            },
            "return": {
                "count": 0,
                "flights": []
            }
        })

    japan_codes = {
        airport["code"].upper()
        for airport in japan_airports
    }

    origin_codes = {
        origin_code
    }

    # --------------------------------------------------
    # 3. Retrieve flights
    # --------------------------------------------------

    flights = MockDataService.get_flights()

    # --------------------------------------------------
    # 4. Find outbound flights
    #
    # SEA -> ANY Japan airport
    # --------------------------------------------------

    outbound_flights = _find_flights(
        flights=flights,
        origin_codes=origin_codes,
        destination_codes=japan_codes
    )

    # --------------------------------------------------
    # 5. Find return flights
    #
    # ANY Japan airport -> SEA
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
    # 7. Keep only top flights per Japan airport
    # --------------------------------------------------

    top_outbound = _top_flights_per_destination(
        flights=outbound_flights,
        limit=2
    )

    top_return = _top_flights_per_origin(
        flights=return_flights,
        limit=2
    )

    # --------------------------------------------------
    # 8. Return compact flight data
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
            "count": len(top_outbound),
            "flights": top_outbound
        },

        "return": {
            "count": len(top_return),
            "flights": top_return
        }
    })

