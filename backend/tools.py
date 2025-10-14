"""
Helper functions that call external APIs: weather, hotels, trains, flights.
Each function returns JSON-friendly data (dictionaries / strings).
Replace placeholder URLs with your chosen providers and keys.
"""

import os
import requests
from dotenv import load_dotenv
load_dotenv()

RAPIDAPI_KEY = os.getenv("RAPIDAPI_KEY")
WEATHER_API_KEY = os.getenv("WEATHER_API_KEY")
IRCTC_API_KEY = os.getenv("IRCTC_API_KEY")
HOTELS_API_KEY = os.getenv("HOTELS_API_KEY")
FLIGHTS_API_KEY = os.getenv("FLIGHTS_API_KEY")

def get_weather(city: str):
    """
    Example using OpenWeatherMap (replace with Google Weather if you have).
    """
    if not WEATHER_API_KEY:
        return {"error": "WEATHER_API_KEY not set"}
    url = "https://api.openweathermap.org/data/2.5/weather"
    params = {"q": city, "appid": WEATHER_API_KEY, "units": "metric"}
    r = requests.get(url, params=params, timeout=10)
    if r.status_code == 200:
        j = r.json()
        return {
            "city": city,
            "desc": j["weather"][0]["description"],
            "temp": j["main"]["temp"],
            "raw": j,
        }
    return {"error": f"weather API failed ({r.status_code})", "detail": r.text}

def fetch_hotels(location: str, checkin: str = None, checkout: str = None):
    """
    Placeholder RapidAPI Booking endpoint example. Replace with actual provider.
    """
    if not RAPIDAPI_KEY:
        return {"error": "RAPIDAPI_KEY not set"}
    # Example RapidAPI header; update host & endpoint per chosen API
    url = "https://booking-com.p.rapidapi.com/v1/hotels/search"  # example
    headers = {
        "X-RapidAPI-Key": RAPIDAPI_KEY,
        "X-RapidAPI-Host": "booking-com.p.rapidapi.com",
    }
    params = {"dest_type": "city", "order_by": "popularity", "locale": "en-gb", "units": "metric", "checkin_date": checkin, "checkout_date": checkout}
    r = requests.get(url, headers=headers, params=params, timeout=10)
    if r.status_code == 200:
        return {"hotels": r.json()}
    return {"error": f"hotels API failed ({r.status_code})", "detail": r.text}

def get_trains(src_code: str, dest_code: str, date: str):
    """
    Example IRCTC via RapidAPI. Update endpoint & parameters as required.
    """
    if not RAPIDAPI_KEY:
        return {"error": "RAPIDAPI_KEY not set"}
    url = "https://irctc1.p.rapidapi.com/api/v1/searchTrain"
    headers = {"X-RapidAPI-Key": RAPIDAPI_KEY, "X-RapidAPI-Host": "irctc1.p.rapidapi.com"}
    params = {"fromStationCode": src_code, "toStationCode": dest_code, "dateOfJourney": date}
    r = requests.get(url, headers=headers, params=params, timeout=10)
    if r.status_code == 200:
        return {"trains": r.json()}
    return {"error": f"trains API failed ({r.status_code})", "detail": r.text}

def get_flights(src: str, dest: str, date: str):
    """
    Placeholder for flights API (RapidAPI or Amadeus). Update accordingly.
    """
    if not FLIGHTS_API_KEY:
        return {"error": "FLIGHTS_API_KEY not set"}
    # Example placeholder; change to your chosen flights endpoint
    url = "https://api.example-flights.com/search"
    headers = {"X-RapidAPI-Key": FLIGHTS_API_KEY}
    params = {"from": src, "to": dest, "date": date}
    r = requests.get(url, headers=headers, params=params, timeout=10)
    if r.status_code == 200:
        return {"flights": r.json()}
    return {"error": f"flights API failed ({r.status_code})", "detail": r.text}
