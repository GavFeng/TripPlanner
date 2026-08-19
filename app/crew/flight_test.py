from crewai import Crew, Process, Task

from app.agents.flight_agent import create_flight_agent


def run_flight_test():
    flight_agent = create_flight_agent()

    task = Task(
        description=(
            "Find the best available flight from Seattle-Tacoma "
            "International Airport (SEA) to Tokyo Haneda Airport (HND).\n\n"

            "You MUST use the flight search tool to retrieve the "
            "available flights.\n\n"

            "The tool will also provide information about the origin "
            "and destination airports, including their corresponding "
            "cities.\n\n"

            "The tool returns flights ranked by price, duration, "
            "and number of stops. Treat rank 1 as the primary "
            "recommendation. Do not recalculate the ranking.\n\n"

            "Briefly explain the relevant tradeoffs using the returned "
            "flight data.\n\n"

            "Provide a concise recommendation."
        ),

        expected_output=(
            "A concise flight recommendation containing:\n"
            "- Recommended airline\n"
            "- Origin airport and city\n"
            "- Destination airport and city\n"
            "- Price\n"
            "- Number of stops\n"
            "- Duration\n"
            "- Brief explanation of why it is recommended\n"
            "- Mention of an important tradeoff if applicable"
        ),

        agent=flight_agent,
    )

    crew = Crew(
        agents=[flight_agent],
        tasks=[task],
        process=Process.sequential,
        verbose=True,
    )

    return crew.kickoff()


if __name__ == "__main__":
    result = run_flight_test()

    print("\n" + "=" * 60)
    print("FINAL FLIGHT RECOMMENDATION")
    print("=" * 60)
    print(result)