import requests
import urllib.parse
import pytz
from datetime import datetime, timedelta
import os
from dotenv import load_dotenv
load_dotenv()
WEATHER_API_KEY = os.getenv("GOOGLE_API_KEY")

def get_maps_places(location, search_text="Most Popular places in "):
    search_query = search_text + location
    search_url = (
        "https://maps.googleapis.com/maps/api/place/textsearch/json?query="
        + urllib.parse.quote(search_query)
        + f"&radius=20000&key={WEATHER_API_KEY}"
    )

    response = requests.get(search_url)
    if response.status_code != 200:
        raise Exception(f"Failed to fetch place info: {response.status_code}")

    data = response.json()
    if "results" not in data or not data["results"]:
        raise Exception("No places found for the location.")
    return data["results"][0]["geometry"]["location"]


def get_weather(destination):
    loc = get_maps_places(destination)
    url = (
        f"https://weather.googleapis.com/v1/forecast/days:lookup?"
        f"key={WEATHER_API_KEY}&location.latitude={loc['lat']}&location.longitude={loc['lng']}&days=10"
    )
    response = requests.get(url)
    if response.status_code != 200:
        raise Exception(f"Weather API failed: {response.status_code}")
    return response.json()


def parse_weather_data(destination, start_date, end_date):
    data = get_weather(destination)
    forecast_days = data.get("forecastDays", [])
    tz_info = pytz.timezone(data["timeZone"]["id"])

    start = datetime.strptime(start_date, "%Y-%m-%d").date()
    end = datetime.strptime(end_date, "%Y-%m-%d").date()

    forecast_map = {
        datetime(
            year=day["displayDate"]["year"],
            month=day["displayDate"]["month"],
            day=day["displayDate"]["day"],
        ).date(): day
        for day in forecast_days
    }

    result = {}
    day_counter = 1
    current = start

    while current <= end:
        key = f"Day {day_counter}"
        if current in forecast_map:
            day = forecast_map[current]
            df, nf, sun = day["daytimeForecast"], day["nighttimeForecast"], day["sunEvents"]
            result[key] = {
                "condition_day": df["weatherCondition"]["description"]["text"],
                "condition_night": nf["weatherCondition"]["description"]["text"],
                "max_temp": day["maxTemperature"]["degrees"],
                "min_temp": day["minTemperature"]["degrees"],
                "humidity_day": df["relativeHumidity"],
                "humidity_night": nf["relativeHumidity"],
                "rain_chance": df["precipitation"]["probability"]["percent"],
                "sunrise": datetime.fromisoformat(sun["sunriseTime"].replace("Z", "+00:00"))
                .astimezone(tz_info)
                .strftime("%I:%M %p"),
                "sunset": datetime.fromisoformat(sun["sunsetTime"].replace("Z", "+00:00"))
                .astimezone(tz_info)
                .strftime("%I:%M %p"),
            }
        else:
            result[key] = "Weather data not available for this day"

        current += timedelta(days=1)
        day_counter += 1

    return result

# if __name__ == "__main__":
#     print("=== WEATHER API TEST STARTED ===")
#
#     # Change this city and dates for testing
#     test_city = "Varanasi"
#     start_date = (datetime.now().date() + timedelta(days=1)).strftime("%Y-%m-%d")
#     end_date = (datetime.now().date() + timedelta(days=3)).strftime("%Y-%m-%d")
#
#     try:
#         print(f"\nTesting for city: {test_city}")
#         print(f"Date range: {start_date} to {end_date}\n")
#
#         weather_data = parse_weather_data(test_city, start_date, end_date)
#
#         print("✅ API WORKING SUCCESSFULLY\n")
#         print("Parsed Weather Output:\n")
#         for day, info in weather_data.items():
#             print(day, "->", info)
#
#     except Exception as e:
#         print("\n❌ API TEST FAILED")
#         print("Error:", e)
#
#     print("\n=== WEATHER API TEST FINISHED ===")
#
