import crewai.llms.cache as crewai_cache

# Workaround needed for CrewAI + Groq
crewai_cache.mark_cache_breakpoint = lambda msg: msg

from crewai import Agent, LLM

# from app.tools.flight_tools import search_japan_flights
# from app.tools.airport_tools import find_airport
# from app.tools.city_tools import find_city
# from app.tools.hotel_tools import search_japan_hotels
# from app.tools.transportation_tools import search_transportation
# from app.tools.trip_tools import plan_trip

from app.tools.flight_tools import search_japan_flights
from app.tools.trip_tools import plan_trip

def create_orchestrator_agent() -> Agent:
    """Create the Trip Planning Orchestrator Agent."""

    llm = LLM(
        model="groq/openai/gpt-oss-20b",
        temperature=0.2,
    )

    return Agent(
        role="Trip Planning Orchestrator",

        goal=(
            "Coordinate the trip planning process by understanding "
            "the user's trip requirements, resolving the starting "
            "airport and city, and using the trip planning tool to "
            "generate and evaluate suitable multi-city itineraries."
        ),

        backstory=(
            "You are the central coordinator for an AI travel planning system. "
            "You receive structured trip requirements including origin, requested "
            "Japan destination cities, duration, budget, and return preference.\n\n"

            "CORE RULES:\n"
            "Coordinate tools rather than manually calculating costs or inventing "
            "airports, flights, hotels, transportation, or routes.\n\n"

            "WORKFLOW:\n"
            "1. FLIGHT SEARCH:\n"
            "Call search_japan_flights using the user's origin airport code. "
            "The flight tool resolves the origin and searches all supported Japan "
            "airports in both directions. Do not select a Japan destination airport "
            "yourself.\n\n"

            "2. ROUTE PLANNING:\n"
            "Pass the user's requested Japan cities, trip requirements, and the "
            "flight results to plan_trip. The route planner determines the best "
            "Japan route and which available Japan airport should be used for "
            "entry and departure.\n\n"

            "3. COST AND RANKING:\n"
            "Use the calculations returned by plan_trip. Do not manually "
            "recalculate flight, transportation, hotel, or total trip costs.\n\n"

            "The Japan route must visit the cities requested by the user. "
            "The international flight origin is separate from the Japan route. "
            "When returnToOrigin is true, the itinerary must return to the "
            "original airport/city.\n\n"

            "If required data is unavailable, report the missing information. "
            "Never guess or fabricate data."
        ),

        tools=[
            search_japan_flights,
            plan_trip,
        ],

        llm=llm,

        verbose=True,
    )