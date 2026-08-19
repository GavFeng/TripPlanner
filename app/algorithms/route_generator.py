from itertools import permutations
from typing import List, Dict, Any


class RouteGenerator:
    """
    Generates possible multi-city travel routes.

    This service is responsible only for generating valid city
    combinations/orders. It does not calculate transportation
    costs or rank routes.
    """

    @staticmethod
    def generate_routes(
        cities: List[str],
        start_city: str | None = None,
        end_city: str | None = None,
        return_to_start: bool = False,
    ) -> List[Dict[str, Any]]:
        """
        Generate possible routes from a list of cities.

        Args:
            cities:
                Cities that may be included in the trip.

            start_city:
                Optional required starting city.

            end_city:
                Optional required ending city.

            return_to_start:
                If True, the route returns to its starting city.

        Returns:
            List of route dictionaries.
        """

        if not cities:
            return []

        # Remove duplicates while preserving order.
        cities = list(dict.fromkeys(cities))

        # Validate start city.
        if start_city and start_city not in cities:
            return []

        # Validate end city.
        if end_city and end_city not in cities:
            return []

        routes = []

        # --------------------------------------------------
        # Case 1:
        # Fixed start + fixed end
        # --------------------------------------------------

        if start_city and end_city and start_city != end_city:

            middle_cities = [
                city
                for city in cities
                if city != start_city and city != end_city
            ]

            for permutation in permutations(middle_cities):
                route = [
                    start_city,
                    *permutation,
                    end_city,
                ]

                routes.append(
                    RouteGenerator._create_route(route)
                )

            return routes

        # --------------------------------------------------
        # Case 2:
        # Fixed starting city
        # Any ending city
        # --------------------------------------------------

        if start_city:

            remaining_cities = [
                city
                for city in cities
                if city != start_city
            ]

            for permutation in permutations(remaining_cities):

                route = [
                    start_city,
                    *permutation,
                ]

                if return_to_start:
                    route.append(start_city)

                routes.append(
                    RouteGenerator._create_route(route)
                )

            return routes

        # --------------------------------------------------
        # Case 3:
        # Fixed ending city
        # Any starting city
        # --------------------------------------------------

        if end_city:

            remaining_cities = [
                city
                for city in cities
                if city != end_city
            ]

            for permutation in permutations(remaining_cities):

                route = [
                    *permutation,
                    end_city,
                ]

                routes.append(
                    RouteGenerator._create_route(route)
                )

            return routes

        # --------------------------------------------------
        # Case 4:
        # No fixed start/end
        #
        # Generate every possible ordering.
        # --------------------------------------------------

        for permutation in permutations(cities):

            route = list(permutation)

            if return_to_start:
                route.append(route[0])

            routes.append(
                RouteGenerator._create_route(route)
            )

        return routes

    # ------------------------------------------------------
    # Route formatting
    # ------------------------------------------------------

    @staticmethod
    def _create_route(route: List[str]) -> Dict[str, Any]:
        """
        Convert a city list into a standard route object.
        """

        # Prevent duplicate cities except for the final return
        # to the starting city.
        unique_cities = set(route)

        if len(route) != len(unique_cities):
            is_valid_return = (
                len(route) > 1
                and route[0] == route[-1]
                and len(route) - 1 == len(unique_cities)
            )

            if not is_valid_return:
                raise ValueError(
                    f"Invalid route contains duplicate cities: {route}"
                )

        # Prevent consecutive duplicate cities.
        for current, next_city in zip(route, route[1:]):
            if current == next_city:
                raise ValueError(
                    f"Invalid route contains consecutive duplicate cities: {route}"
                )

        return {
            "cities": route,
            "start": route[0],
            "end": route[-1],
            "stops": max(len(route) - 2, 0),
            "returnToStart": (
                len(route) > 1
                and route[0] == route[-1]
            ),
        }