import json
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from app.tools.trip_tools import plan_trip

def run_test():
    print("=" * 70)
    print("TESTING plan_trip TOOL DIRECTLY")
    print("=" * 70)

    test_args = {
        "cities": ["Tokyo", "Kyoto", "Osaka"],
        "days": 7,
        "budget": 3000.0,
        "entry_city": "Tokyo",
        "exit_city": "Osaka",
        "outbound_flight_id": "FL003", 
        "return_flight_id": "FL008"
    }

    print(f"Input Arguments:\n{json.dumps(test_args, indent=2)}\n")

    try:
        # ✅ FIX: Use .run() to invoke the CrewAI Tool object directly in tests
        result_json_str = plan_trip.run(
            cities=test_args["cities"],
            days=test_args["days"],
            budget=test_args["budget"],
            entry_city=test_args["entry_city"],
            exit_city=test_args["exit_city"],
            outbound_flight_id=test_args["outbound_flight_id"],
            return_flight_id=test_args["return_flight_id"]
        )

        result = json.loads(result_json_str)

        print("-" * 70)
        print(f"Success Status: {result.get('success')}")
        print("-" * 70)

        if result.get("success"):
            print(f"Total Trips Generated & Ranked: {result.get('count')}")
            print(f"Flight Cost: ${result.get('flightCost')}")
            print("\nTop Ranked Trip Details:")
            if result.get("trips"):
                print(json.dumps(result["trips"][0], indent=2))
        else:
            print(f"Tool Error Message: {result.get('message')}")

    except Exception as e:
        print(f"\n❌ Test Failed with Exception: {type(e).__name__}: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    run_test()