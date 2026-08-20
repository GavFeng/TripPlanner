import json

from crewai.tools import tool

from app.algorithms.route_generator import RouteGenerator
from app.algorithms.route_selector import RouteSelector
from app.algorithms.transportation_calculator import TransportationCalculator
from app.algorithms.hotel_calculator import HotelCalculator
from app.algorithms.trip_cost_calculator import TripCostCalculator
from app.algorithms.budget_validator import BudgetValidator
from app.algorithms.trip_ranker import TripRanker

from app.services.transportation_service import TransportationService
from app.services.mock_data_service import MockDataService


@tool("Plan Trip")
def plan_trip(
    cities: list[str],
    days: int,
    budget: float,
    entry_city: str,
    exit_city: str,
    outbound_flight_id: str,
    return_flight_id: str,
) -> str:
    """
    Generate and evaluate a Japan trip using the selected
    international flights.

    The AI selects the outbound and return flight IDs from
    search_japan_flights.

    This tool is responsible for:
    - validating the selected flights
    - resolving flight prices
    - generating Japan routes
    - calculating transportation
    - selecting hotels
    - calculating total cost
    - validating the budget
    - ranking trip options
    """

    # ==================================================
    # 0. Sanitize LLM arguments
    # ==================================================

    if isinstance(cities, str): 
        try:
            parsed = json.loads(cities)
            if isinstance(parsed, list):
                cities = parsed
            else:
                cities = [str(parsed)]
        except json.JSONDecodeError:
            cities = [c.strip() for c in cities.split(",") if c.strip()]

    if not isinstance(cities, list):
        return json.dumps({
            "success": False,
            "message": (
                f"cities must be a list, "
                f"got {type(cities).__name__}"
            )
        })

    if isinstance(days, str):
        try:
            days = int(days)
        except ValueError:
            return json.dumps({
                "success": False,
                "message": "days must be an integer."
            })

    if isinstance(budget, str):
        try:
            budget = float(budget)
        except ValueError:
            return json.dumps({
                "success": False,
                "message": "budget must be a number."
            })

    if not isinstance(outbound_flight_id, str):
        return json.dumps({
            "success": False,
            "message": "outbound_flight_id must be a string."
        })

    if not isinstance(return_flight_id, str):
        return json.dumps({
            "success": False,
            "message": "return_flight_id must be a string."
        })

    # ==================================================
    # 1. Validate basic inputs
    # ==================================================

    if not cities:
        return json.dumps({
            "success": False,
            "message": (
                "At least one destination city is required."
            )
        })

    if days <= 0:
        return json.dumps({
            "success": False,
            "message": "Days must be greater than zero."
        })

    if budget <= 0:
        return json.dumps({
            "success": False,
            "message": "Budget must be greater than zero."
        })

    if not entry_city:
        return json.dumps({
            "success": False,
            "message": "Entry city is required."
        })

    if not exit_city:
        return json.dumps({
            "success": False,
            "message": "Exit city is required."
        })

    entry_city = entry_city.strip()
    exit_city = exit_city.strip()

    outbound_flight_id = outbound_flight_id.strip()
    return_flight_id = return_flight_id.strip()

    # ==================================================
    # 2. Validate cities
    # ==================================================

    city_lookup = {
        city.strip().lower(): city
        for city in cities
    }

    if entry_city.lower() not in city_lookup:
        return json.dumps({
            "success": False,
            "message": (
                f"Entry city '{entry_city}' is not in "
                "the requested cities."
            )
        })

    if exit_city.lower() not in city_lookup:
        return json.dumps({
            "success": False,
            "message": (
                f"Exit city '{exit_city}' is not in "
                "the requested cities."
            )
        })

    # ==================================================
    # 3. Resolve selected flights
    # ==================================================

    flights = MockDataService.get_flights()

    if not isinstance(flights, list):
        return json.dumps({
            "success": False,
            "message": "Flight data is unavailable."
        })

    outbound_flight = next(
        (
            flight
            for flight in flights
            if isinstance(flight, dict)
            and flight.get("id") == outbound_flight_id
        ),
        None
    )

    return_flight = next(
        (
            flight
            for flight in flights
            if isinstance(flight, dict)
            and flight.get("id") == return_flight_id
        ),
        None
    )

    if not outbound_flight:
        return json.dumps({
            "success": False,
            "message": (
                f"Outbound flight "
                f"'{outbound_flight_id}' was not found."
            )
        })

    if not return_flight:
        return json.dumps({
            "success": False,
            "message": (
                f"Return flight "
                f"'{return_flight_id}' was not found."
            )
        })

    # ==================================================
    # 4. Validate flight prices
    # ==================================================

    outbound_price = outbound_flight.get("price")
    return_price = return_flight.get("price")

    if not isinstance(outbound_price, (int, float)):
        return json.dumps({
            "success": False,
            "message": (
                f"Outbound flight '{outbound_flight_id}' "
                "does not have a valid price."
            )
        })

    if not isinstance(return_price, (int, float)):
        return json.dumps({
            "success": False,
            "message": (
                f"Return flight '{return_flight_id}' "
                "does not have a valid price."
            )
        })

    # ==================================================
    # 5. Calculate international flight cost
    # ==================================================

    flight_cost = (
        float(outbound_price) +
        float(return_price)
    )

    # ==================================================
    # 6. Generate Japan routes
    # ==================================================

    routes = RouteGenerator.generate_routes(
        cities=cities,
        start_city=entry_city,
        end_city=exit_city,
        return_to_start=False,
    )

    if not routes:
        return json.dumps({
            "success": False,
            "message": (
                f"No valid route exists from "
                f"{entry_city} to {exit_city}."
            )
        })

    # ==================================================
    # 7. Calculate transportation
    # ==================================================

    transportation_service = TransportationService()

    evaluated_routes = []

    for route_data in routes:
        if isinstance(route_data, str):
            continue

        if isinstance(route_data, dict):
            route = route_data.get("cities", [])

        elif isinstance(route_data, list):
            route = route_data

        else:
            continue

        if not isinstance(route, list) or not route:
            continue

        result = TransportationCalculator.calculate_route(
            route=route,
            transportation_service=transportation_service,
        )

        if not isinstance(result, dict):
            continue

        if result.get("valid"):

            evaluated_routes.append({
                "cities": route,
                **result,
            })

    # ==================================================
    # 8. Validate transportation routes
    # ==================================================

    if not evaluated_routes:
        return json.dumps({
            "success": False,
            "message": (
                "No valid transportation routes were found "
                "between the requested Japanese cities."
            )
        })

    # ==================================================
    # 9. Select top transportation routes
    # ==================================================

    top_routes = RouteSelector.select_top_x(
        routes=evaluated_routes,
        top_x=5,
        sort_by="transport_cost",
    )

    if not isinstance(top_routes, list):
        return json.dumps({
            "success": False,
            "message": "Route selector returned invalid data."
        })

    # ==================================================
    # 10. Retrieve hotels
    # ==================================================

    hotels = MockDataService.get_all_hotels()

    if not isinstance(hotels, dict):
        hotels = {}

    trips = []

    # ==================================================
    # 11. Evaluate each route
    # ==================================================

    for route_data in top_routes:
        if isinstance(route_data, str):
            try:
                route_data = json.loads(route_data)
            except json.JSONDecodeError:
                continue

        if not isinstance(route_data, dict):
            continue

        route = route_data.get("cities", [])

        if not isinstance(route, list) or not route:
            continue

        transport_cost = route_data.get(
            "transport_cost",
            0
        )

        if not isinstance(transport_cost, (int, float)):
            continue

        hotel_results = []
        hotel_cost = 0.0

        # ----------------------------------------------
        # Allocate days
        # ----------------------------------------------

        city_count = len(route)

        city_days = days // city_count
        remaining_days = days % city_count

        # ----------------------------------------------
        # Calculate hotel costs
        # ----------------------------------------------

        for index, city in enumerate(route):

            assigned_days = city_days

            if index == city_count - 1:
                assigned_days += remaining_days

            city_hotels = hotels.get(city, [])

            if isinstance(city_hotels, str):
                city_hotels = []

            if isinstance(city_hotels, dict):
                city_hotels = [city_hotels]

            if not isinstance(city_hotels, list):
                city_hotels = []

            valid_hotels = [
                hotel for hotel in city_hotels
                if isinstance(hotel, dict)
                and isinstance(hotel.get("pricePerNight"), (int, float))
            ]

            if not valid_hotels:
                continue

            selected_hotel = min(
                valid_hotels,
                key=lambda hotel: hotel["pricePerNight"]
            )

            hotel_result = (
                HotelCalculator.calculate_city_cost(
                    selected_hotel,
                    assigned_days,
                )
            )

            if not isinstance(hotel_result, dict):
                continue

            total_hotel_cost = hotel_result.get(
                "total_cost",
                0
            )

            if not isinstance(
                total_hotel_cost,
                (int, float)
            ):
                continue

            hotel_results.append(hotel_result)

            hotel_cost += float(total_hotel_cost)

        # ----------------------------------------------
        # Calculate total trip cost
        # ----------------------------------------------

        cost = TripCostCalculator.calculate(
            flight_cost=flight_cost,
            transportation_cost=float(
                transport_cost
            ),
            hotel_cost=hotel_cost,
        )

        if not isinstance(cost, dict):
            continue

        if "total_cost" not in cost:
            continue

        # ----------------------------------------------
        # Budget validation
        # ----------------------------------------------

        budget_result = BudgetValidator.validate(
            total_cost=cost["total_cost"],
            budget=budget,
        )

        if not isinstance(budget_result, dict):
            budget_result = {}

        # ----------------------------------------------
        # Build trip
        # ----------------------------------------------

        trips.append({
            "entryCity": entry_city,
            "exitCity": exit_city,

            "route": route,

            "outboundFlight": {
                "id": outbound_flight.get("id"),
                "airline": outbound_flight.get("airline"),
                "origin": outbound_flight.get("origin"),
                "destination": outbound_flight.get(
                    "destination"
                ),
                "price": outbound_price,
            },

            "returnFlight": {
                "id": return_flight.get("id"),
                "airline": return_flight.get("airline"),
                "origin": return_flight.get("origin"),
                "destination": return_flight.get(
                    "destination"
                ),
                "price": return_price,
            },

            "flightCost": flight_cost,

            "hotels": hotel_results,

            **cost,
            **budget_result,
        })

    # ==================================================
    # 12. Validate generated trips
    # ==================================================

    if not trips:
        return json.dumps({
            "success": False,
            "message": (
                "No valid trip options could be generated."
            )
        })

    # ==================================================
    # 13. Rank trips
    # ==================================================

    ranked_trips = TripRanker.rank(
        trips=trips,
        budget=budget,
    )

    if not isinstance(ranked_trips, list):
        return json.dumps({
            "success": False,
            "message": "Trip ranker returned invalid data."
        })

    # ==================================================
    # 14. Return result
    # ==================================================

    return json.dumps({
        "success": True,

        "budget": budget,
        "days": days,

        "entryCity": entry_city,
        "exitCity": exit_city,

        "selectedFlights": {
            "outbound": outbound_flight_id,
            "return": return_flight_id,
        },

        "flightCost": flight_cost,

        "count": len(ranked_trips),

        "trips": ranked_trips,
    })