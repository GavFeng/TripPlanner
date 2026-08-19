# import json

# from crewai.tools import tool

# from app.services.city_service import CityService


# @tool("Find City")
# def find_city(city_name: str) -> str:
#     """
#     Find a city by its exact city name.

#     IMPORTANT:
#     Call this tool with only the city_name argument.
#     Example:
#     {"city_name": "Osaka"}

#     Do not include explanations, labels, or other text in the arguments.

#     Args:
#         city_name: The city name, such as "Tokyo" or "Osaka".

#     Returns:
#         JSON string containing the city information, including supported
#         airport information when available.
#     """

#     city = CityService.find_by_name(city_name)

#     if not city:
#         return json.dumps({
#             "success": False,
#             "city": city_name,
#             "message": f"City '{city_name}' was not found."
#         })

#     return json.dumps({
#         "success": True,
#         "city": city
#     })