import crewai.llms.cache as crewai_cache

# Workaround needed for CrewAI to work with Groq
crewai_cache.mark_cache_breakpoint = lambda msg: msg

from crewai import Agent, LLM

from app.tools.flight_tools import search_japan_flights


def create_flight_agent() -> Agent:
    """Create the Japan Flight Agent."""

    llm = LLM(
        model="groq/openai/gpt-oss-20b",
        temperature=0.2,
    )

    return Agent(
        role="Japan Flight Researcher",

        goal=(
            "Find and recommend the most suitable flight based on "
            "the user's origin, destination, price, duration, and "
            "number of stops."
        ),

        backstory=(
            "You are a travel research specialist focused on flights "
            "to Japan. You use the flight search tool to retrieve "
            "available flight options and resolve airport codes to "
            "their corresponding airports and cities. "

            "The tool returns flights ranked by the RankingService "
            "using price, duration, and number of stops. Treat rank 1 "
            "as the default recommendation. "

            "Do not recalculate the ranking yourself. Instead, "
            "interpret the ranked results and explain important "
            "tradeoffs between price, duration, stops, and convenience. "

            "Use the airport and city information returned by the tool "
            "when explaining where the flight departs and arrives."
        ),

        tools=[search_japan_flights],

        llm=llm,

        verbose=True,
    )