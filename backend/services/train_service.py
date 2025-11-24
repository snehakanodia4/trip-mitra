import requests
import os
from langchain_google_genai import ChatGoogleGenerativeAI
from dotenv import load_dotenv
load_dotenv()
IRCTC_API_KEY = os.getenv("IRCTC_API_KEY")
llm = ChatGoogleGenerativeAI(model="gemini-2.0-flash")

def get_station_code(city_name):
    prompt = f"What is the main IRCTC station code for {city_name}? Return only the code."
    response = llm.invoke(prompt)
    return response.content.strip().upper()


def get_train_details(from_station, to_station, date_of_journey):
    url = "https://irctc1.p.rapidapi.com/api/v3/trainBetweenStations"
    headers = {
        "x-rapidapi-host": "irctc1.p.rapidapi.com",
        "x-rapidapi-key": IRCTC_API_KEY
    }
    params = {
        "fromStationCode": from_station,
        "toStationCode": to_station,
        "dateOfJourney": date_of_journey
    }

    res = requests.get(url, headers=headers, params=params)
    res.raise_for_status()
    data = res.json()

    if not data.get("status") or "data" not in data:
        return []

    trains = []
    for t in data["data"]:
        trains.append({
            "train_name": t.get("train_name"),
            "train_number": t.get("train_number"),
            "departure_time": t.get("from_std"),
            "arrival_time": t.get("to_std"),
            "duration": t.get("duration"),
            "classes": t.get("class_type", [])
        })
    return trains


def get_trains_to_and_from_city(from_city, to_city, start_date, end_date):
    try:
        from_station = get_station_code(from_city)
        to_station = get_station_code(to_city)

        trains_to = get_train_details(from_station, to_station, start_date)
        trains_from = get_train_details(to_station, from_station, end_date)

        return {
            to_city: {"from": from_city, "to": to_city, "trains": trains_to},
            from_city: {"from": to_city, "to": from_city, "trains": trains_from}
        }
    except Exception as e:
        return {"error": str(e)}

