import json

from crewai import Crew, Process, Task

from app.agents.orchestrator_agent import create_orchestrator_agent


def run_orchestrator_test():
    orchestrator = create_orchestrator_agent()

    trip = {
        "origin": "SEA",
        "cities": [
            "Tokyo",
            "Osaka"
        ],
        "days": 7,
        "budget": 3000,
        "returnToOrigin": True
    }

    task = Task(
        description=(
            "Plan the following trip using the available tools.\n\n"

            f"Trip requirements:\n"
            f"{json.dumps(trip, indent=2)}\n\n"

            "First, use search_japan_flights with the origin airport "
            "code to retrieve all available flights between the origin "
            "and supported airports in Japan, in both directions.\n\n"

            "Then use plan_trip with the requested cities and the "
            "available flight information to generate and evaluate "
            "the possible Japan routes.\n\n"

            "The itinerary must:\n"
            "- Start from SEA.\n"
            "- Visit Tokyo and Osaka.\n"
            "- Last 7 days.\n"
            "- Return to SEA.\n"
            "- Stay within the $3,000 budget if possible.\n\n"

            "Let the planning tool determine the best route and "
            "international entry and departure airports. Do not "
            "manually calculate flight, transportation, hotel, or "
            "total trip costs.\n\n"

            "Provide a concise summary of the best itinerary and "
            "the important cost and route tradeoffs."
        ),

        expected_output=(
            "A concise trip recommendation containing:\n"
            "- Origin airport and city\n"
            "- Cities visited\n"
            "- Route order\n"
            "- International entry airport and flight\n"
            "- International departure airport and flight\n"
            "- Hotel selections and assigned days\n"
            "- Transportation cost\n"
            "- Hotel cost\n"
            "- Total trip cost\n"
            "- Remaining budget\n"
            "- Whether the trip is within budget\n"
            "- Brief explanation of the route and cost tradeoffs"
        ),

        agent=orchestrator,
    )

    crew = Crew(
        agents=[orchestrator],
        tasks=[task],
        process=Process.sequential,
        verbose=True,
    )

    return crew.kickoff()


if __name__ == "__main__":
    result = run_orchestrator_test()

    print("\n" + "=" * 70)
    print("FINAL ORCHESTRATOR RESULT")
    print("=" * 70)
    print(result)