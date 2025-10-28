from flask import Flask, request, jsonify
from flask_cors import CORS
import os
from dotenv import load_dotenv
load_dotenv()

from services.weather_service import parse_weather_data
from services.hotel_service import parse_hotel_info
from services.train_service import get_trains_to_and_from_city
from services.gemini_agent import agent, build_itinerary_prompt


GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
if not GOOGLE_API_KEY:
    raise ValueError("GOOGLE_API_KEY not found in .env file")

# Set it in environment (for services that might need it)
os.environ["GOOGLE_API_KEY"] = GOOGLE_API_KEY
app = Flask(__name__)
CORS(app)
@app.route('/')
def home():
    return jsonify({"message": "AI Travel Planner API is running "})


@app.route('/api/weather', methods=['POST'])
def weather():
    data = request.get_json()
    city = data.get("city")
    start_date = data.get("start_date")
    end_date = data.get("end_date")
    try:
        result = parse_weather_data(city, start_date, end_date)
        return jsonify(result)
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/api/hotels', methods=['POST'])
def hotels():
    data = request.get_json()
    city = data.get("city")
    start_date = data.get("start_date")
    end_date = data.get("end_date")
    adults = data.get("adults", 2)
    try:
        result = parse_hotel_info(city, start_date, end_date, adults)
        return jsonify(result)
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/api/trains', methods=['POST'])
def trains():
    data = request.get_json()
    from_city = data.get("from_city")
    to_city = data.get("to_city")
    start_date = data.get("start_date")
    end_date = data.get("end_date")
    try:
        result = get_trains_to_and_from_city(from_city, to_city, start_date, end_date)
        return jsonify(result)
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/api/itinerary', methods=['POST'])
def generate_itinerary():
    data = request.get_json()
    from_city = data["from_city"]
    to_city = data["to_city"]
    start_date = data["start_date"]
    end_date = data["end_date"]
    adults = data.get("adults", 2)
    budget = data.get("budget", 15000)

    if not all([from_city, to_city, start_date, end_date]):
        return jsonify({"error": "Missing required fields"}), 400

    query = build_itinerary_prompt(from_city, to_city, start_date, end_date, adults, budget)

    try:
        result = agent.run(query)
        return jsonify({"itinerary": result})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    app.run(debug=True)
