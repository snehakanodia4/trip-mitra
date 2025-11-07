import requests
import os
from dotenv import load_dotenv

load_dotenv()
RAPIDAPI_KEY =  os.getenv("Flight_API_KEY")
RAPIDAPI_HOST = "booking-com15.p.rapidapi.com"

from langchain_google_genai import ChatGoogleGenerativeAI

# Initialize Gemini model (you already use it in your agent)
llm = ChatGoogleGenerativeAI(model="gemini-2.5-pro")

def get_airport_code(city_name: str) -> str:
    """
    Uses Gemini to find the primary IATA airport code for a given city.
    Example: 'Mumbai' → 'BOM', 'New Delhi' → 'DEL'
    """
    prompt = f"What is the main IATA airport code for {city_name}? Return only the 3-letter code."
    response = llm.invoke(prompt)
    return response.content.strip().upper()

def fetch_flight_data(from_city: str, to_city: str, date: str, adults: str ):
    """
    Fetch raw flight data from Booking.com Flight Search API.
    """
    url = f"https://{RAPIDAPI_HOST}/api/v1/flights/searchFlights"

    querystring = {
        "fromId": f"{from_city}.AIRPORT",
        "toId": f"{to_city}.AIRPORT",
        "stops": "none",
        "pageNo": "1",
        "adults": adults,
        "children": "0,17",
        "sort": "BEST",
        "cabinClass": "ECONOMY",
        "currency_code": "INR",
        "departDate": date,
    }

    headers = {
        "x-rapidapi-key": RAPIDAPI_KEY,
        "x-rapidapi-host": RAPIDAPI_HOST
    }

    try:
        response = requests.get(url, headers=headers, params=querystring)
        response.raise_for_status()
        data = response.json()
        if not data.get("status", False):
            print(" API returned failure:", data.get("message"))
            return None
        return data
    except Exception as e:
        print(f"Error fetching flight data: {e}")
        return None


def parse_flight_data(data: dict):
    """
    Parse and simplify Booking.com flight data for agent usage.
    """
    if not data or "data" not in data or "aggregation" not in data["data"]:
        return []

    try:
        aggregation = data["data"]["aggregation"]
        airlines = aggregation.get("airlines", [])
        stops = aggregation.get("stops", [])

        results = []
        for airline in airlines:
            price_value = airline["minPrice"]["units"] + airline["minPrice"]["nanos"] / 1e9
            result = {
                "airline": airline["name"],
                "iata": airline["iataCode"],
                "logo": airline["logoUrl"],
                "min_price": f"{airline['minPrice']['currencyCode']} {price_value:.2f}",
                "stops_info": [
                    {
                        "stops": s["numberOfStops"],
                        "min_price": f"{s['minPrice']['currencyCode']} {(s['minPrice']['units'] + s['minPrice']['nanos'] / 1e9):.2f}"
                    }
                    for s in stops
                ]
            }
            results.append(result)

        return results
    except Exception as e:
        print(f"⚠️ Error parsing flight data: {e}")
        return []


def get_flight_data(from_city: str, to_city: str, start_date: str, end_date: str, adults: int):
    """
    Fetch both departure and return flight data between two cities.
    Returns a structured dict containing to_city and from_city flight data.
    """
    from_code = get_airport_code(from_city)
    to_code = get_airport_code(to_city)

    try:
        #  Outgoing flight (from → to)
        raw_data_to = fetch_flight_data(from_code, to_code, start_date,adults)
        flights_to = parse_flight_data(raw_data_to) if raw_data_to else []

        #  Return flight (to → from)
        raw_data_from = fetch_flight_data(to_code, from_code, end_date,adults)
        flights_from = parse_flight_data(raw_data_from) if raw_data_from else []

        return {
            to_city+"to"+from_city: {
                "from": from_city,
                "to": to_city,
                "date": start_date,
                "flights": flights_to
            },
            from_city+"to"+to_city: {
                "from": to_city,
                "to": from_city,
                "date": end_date,
                "flights": flights_from
            }
        }

    except Exception as e:
        return {"error": str(e)}


# if __name__ == "__main__":
#     print("🔍 Fetching flight data from Booking.com API...\n")
#     flights = get_flight_data("Delhi", "Varanasi", "2025-11-8", "2025-11-12",1)
#
#     if not flights:
#         print("❌ No flight data found.")
#     else:
#         print(f"✅ Found {len(flights)} airlines:\n")
#         print(flights)
