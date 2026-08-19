import json

from app.tools.flight_tools import search_japan_flights


def main():
    print("=" * 60)
    print("FLIGHT TOOL TEST")
    print("=" * 60)

    result = search_japan_flights.run(
        origin="SEA",
        destination="HND"
    )

    # Convert JSON string into Python object
    data = json.loads(result)

    print("\nSuccess:", data["success"])
    print("Route:", f'{data["origin"]} → {data["destination"]}')
    print("Flights Found:", data["count"])

    print("\nRanked Flights:")

    for flight in data["flights"]:
        print(
            f"\nRank #{flight['rank']}"
            f"\n  Airline: {flight['airline']}"
            f"\n  Price: ${flight['price']}"
            f"\n  Stops: {flight['stops']}"
            f"\n  Duration: {flight['durationHours']} hours"
            f"\n  Score: {flight['score']}"
        )


if __name__ == "__main__":
    main()