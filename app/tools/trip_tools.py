import json
from typing import Any, Dict

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
    return_to_origin: bool = True,
    origin_city: str = "",
    flight_cost: float = 0,
) -> str:
    """
    Generate and evaluate possible multi-city trip routes.

    The tool:
    1. Generates valid city routes.
    2. Calculates transportation costs.
    3. Selects the top candidate routes.
    4. Calculates hotel costs.
    5. Calculates total trip costs.
    6. Validates the budget.
    7. Ranks the resulting trips.

    Args:
        cities: Cities the traveler wants to visit.
        days: Total number of days for the trip.
        budget: Maximum trip budget.
        return_to_origin: Whether the trip should return to the origin.
        origin_city: Starting city.
        flight_cost: Flight cost to/from the destination region.

    Returns:
        JSON string containing ranked trip options.
    """

    if not cities:
        return json.dumps({
            "success": False,
            "message": "At least one destination city is required."
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

    # --------------------------------------------------
    # 1. Generate routes
    # --------------------------------------------------

    routes = RouteGenerator.generate_routes(
        cities=cities,
        start_city=origin_city if origin_city else None,
        return_to_start=return_to_origin,
    )

    if not routes:
        return json.dumps({
            "success": False,
            "message": "No valid routes could be generated."
        })
        
    

    # --------------------------------------------------
    # 2. Calculate transportation
    # --------------------------------------------------

    transportation_service = TransportationService()

    evaluated_routes = []

    for route_data in routes:

        route = route_data["cities"]

        result = TransportationCalculator.calculate_route(
            route=route,
            transportation_service=transportation_service,
        )

        if result["valid"]:
            evaluated_routes.append({
                **route_data,
                **result,
            })

    if not evaluated_routes:
        return json.dumps({
            "success": False,
            "message": (
                "No valid transportation routes were found "
                "between the requested cities."
            )
        })

    # --------------------------------------------------
    # 3. Select top transportation routes
    # --------------------------------------------------

    top_routes = RouteSelector.select_top_x(
        routes=evaluated_routes,
        top_x=5,
        sort_by="transport_cost",
    )

    # --------------------------------------------------
    # 4. Calculate hotels
    # --------------------------------------------------

    hotels = MockDataService.get_all_hotels()

    # Temporary/simple hotel handling.
    #
    # This will eventually be replaced with hotel ranking
    # based on city, budget, rating, and preferences.
    trips = []

    for route in top_routes:

        hotel_results = []
        hotel_cost = 0

        # Simple equal-day allocation for now.
        city_days = days // len(cities)

        remaining_days = days - (city_days * len(cities))

        for index, city in enumerate(cities):

            assigned_days = city_days

            if index == len(cities) - 1:
                assigned_days += remaining_days

            city_hotels = hotels.get(city, [])

            if not city_hotels:
                continue

            selected_hotel = min(
                city_hotels,
                key=lambda hotel: hotel["pricePerNight"]
            )

            hotel_result = HotelCalculator.calculate_city_cost(
                selected_hotel,
                assigned_days,
            )

            hotel_results.append(hotel_result)
            hotel_cost += hotel_result["total_cost"]

        # --------------------------------------------------
        # 5. Calculate total trip cost
        # --------------------------------------------------

        cost = TripCostCalculator.calculate(
            flight_cost=flight_cost,
            transportation_cost=route["transport_cost"],
            hotel_cost=hotel_cost,
        )

        # --------------------------------------------------
        # 6. Validate budget
        # --------------------------------------------------

        budget_result = BudgetValidator.validate(
            total_cost=cost["total_cost"],
            budget=budget,
        )

        trips.append({
            "route": route,
            "hotels": hotel_results,
            **cost,
            **budget_result,
        })

    # --------------------------------------------------
    # 7. Rank trips
    # --------------------------------------------------

    ranked_trips = TripRanker.rank(
        trips=trips,
        budget=budget,
    )

    return json.dumps({
        "success": True,
        "budget": budget,
        "days": days,
        "count": len(ranked_trips),
        "trips": ranked_trips,
    })