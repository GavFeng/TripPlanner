import crewai.llms.cache as crewai_cache

# Workaround needed for CrewAI + Groq
crewai_cache.mark_cache_breakpoint = lambda msg: msg

from crewai import Agent, LLM

from app.tools.hotel_tools import search_japan_hotels


def create_hotel_agent() -> Agent:
    """Create the Japan Hotel Agent."""

    llm = LLM(
        model="groq/openai/gpt-oss-20b",
        temperature=0.2,
    )

    return Agent(
        role="Japan Hotel Researcher",

        goal=(
            "Find and recommend the most suitable hotel in the requested "
            "Japanese city based on price, rating, location, and access "
            "to public transportation."
        ),

        backstory=(
            "You are a Japan travel accommodation specialist. "
            "You use the hotel search tool to retrieve available hotels. "
            "The tool returns hotels ranked by price, rating, and proximity "
            "to public transportation. Treat rank 1 as the default "
            "recommendation. Do not recalculate the ranking yourself. "
            "Your responsibility is to interpret the ranked results, "
            "explain important tradeoffs, and communicate the recommendation "
            "clearly."
        ),

        tools=[search_japan_hotels],

        llm=llm,

        verbose=True,
    )