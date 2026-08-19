from crewai import Crew, Process, Task

from app.agents.hotel_agent import create_hotel_agent


def run_hotel_test():
    hotel_agent = create_hotel_agent()

    task = Task(
        description=(
            "Find the best available hotel in Tokyo.\n\n"

            "You MUST use the hotel search tool to retrieve "
            "the available hotels.\n\n"

            "The tool returns hotels ranked by price, rating, "
            "and access to public transportation. Treat rank 1 "
            "as the primary recommendation. Do not recalculate "
            "the ranking.\n\n"

            "Briefly explain the relevant tradeoffs using the "
            "returned hotel data.\n\n"

            "Provide a concise recommendation."
        ),

        expected_output=(
            "A concise hotel recommendation containing:\n"
            "- Recommended hotel\n"
            "- Price per night\n"
            "- Rating\n"
            "- Area\n"
            "- Public transportation access\n"
            "- Brief explanation of why it is recommended\n"
            "- Important tradeoff if applicable"
        ),

        agent=hotel_agent,
    )

    crew = Crew(
        agents=[hotel_agent],
        tasks=[task],
        process=Process.sequential,
        verbose=True,
    )

    return crew.kickoff()


if __name__ == "__main__":
    result = run_hotel_test()

    print("\n" + "=" * 60)
    print("FINAL HOTEL RECOMMENDATION")
    print("=" * 60)
    print(result)