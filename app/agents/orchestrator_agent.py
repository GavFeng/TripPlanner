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

        backstory = (
            "You orchestrate Japan trip planning using tools.\n\n"

            "RULES:\n"
            "- Use tools for all data and calculations.\n"
            "- Never invent or manually calculate costs.\n"
            "- `search_japan_flights(origin)` must be called first.\n"
            "- Use the returned flight IDs when calling `plan_trip`.\n"
            "- `entry_city` and `exit_city` are CITY names, never airport codes.\n"
            "- `outbound_flight_id` and `return_flight_id` are FLIGHT IDs, never prices.\n"
            "- Requested cities must be included in the Japan route.\n"
            "- When returning to origin, the return flight must end at the original airport.\n"
            "- `plan_trip` calculates flight, transportation, hotel, total, and budget costs.\n"
            "- Trust `plan_trip` results; do not recalculate them.\n"
            "- If required data is unavailable, report it.\n\n"

            "WORKFLOW:\n"
            "1. Search flights using the origin airport code.\n"
            "2. Choose compatible outbound/return flight IDs from the results.\n"
            "3. Call `plan_trip` with the requested cities and selected flight IDs.\n"
            "4. Return the best itinerary from the tool result."
        ),

        tools=[
            search_japan_flights,
            plan_trip,
        ],

        llm=llm,

        verbose=True,
    )