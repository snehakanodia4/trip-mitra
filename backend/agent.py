import os
import json
import re
from dotenv import load_dotenv

# Load env variables
load_dotenv()

# -----------------------------
# DUMMY TOOL IMPLEMENTATIONS
# -----------------------------
def get_weather(city: str):
    """Mock or API-based weather data."""
    try:
        import requests
        key = os.getenv("OPENWEATHER_API_KEY")
        if key:
            url = f"https://api.openweathermap.org/data/2.5/weather?q={city}&appid={key}&units=metric"
            resp = requests.get(url).json()
            if "main" in resp:
                return {
                    "city": city.title(),
                    "temperature": resp["main"]["temp"],
                    "description": resp["weather"][0]["description"],
                }
    except Exception as e:
        print("Weather fetch failed:", e)

    # fallback
    return {"city": city.title(), "temperature": 28, "description": "clear skies"}

def fetch_hotels(city: str):
    """Dummy hotel list."""
    return [
        {"name": f"{city.title()} Palace Hotel", "price": "₹4000/night", "rating": 4.5},
        {"name": f"StayEasy {city.title()}", "price": "₹2500/night", "rating": 4.2},
    ]

def get_trains(src, dest, date):
    """Dummy train list."""
    return [
        {"train": "Rajdhani Express", "departure": "16:30", "arrival": "06:15", "duration": "13h 45m"},
        {"train": "Shatabdi Express", "departure": "06:00", "arrival": "12:15", "duration": "6h 15m"},
    ]

def get_flights(src, dest, date):
    """Dummy flight list."""
    return [
        {"airline": "IndiGo", "time": "07:30 → 09:20", "price": "₹4800"},
        {"airline": "Vistara", "time": "14:15 → 16:00", "price": "₹5200"},
    ]

# -----------------------------
# GEMINI CONFIG
# -----------------------------
try:
    import google.generativeai as genai
    genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
    GEMINI_AVAILABLE = True
except Exception:
    GEMINI_AVAILABLE = False

# -----------------------------
# HELPERS
# -----------------------------
def extract_city(text: str) -> str:
    """Naive city extractor using regex."""
    match = re.search(r"in\s+([A-Za-z\s]+)", text)
    if match:
        return match.group(1).strip().title()
    return "Delhi"

def format_summary(context: dict) -> str:
    return json.dumps(context, indent=2, ensure_ascii=False)

def call_gemini(prompt: str) -> str:
    """Call Gemini or fallback."""
    if not GEMINI_AVAILABLE:
        return f"(Gemini unavailable) Simulated reply:\n\nBased on your input, here's a possible travel plan.\n{prompt[:300]}..."

    try:
        resp = genai.generate_text(model="gemini-1.5-pro", prompt=prompt, max_output_tokens=800)
        return resp.text if hasattr(resp, "text") else str(resp)
    except Exception as e:
        return f"Error calling Gemini: {e}"

# -----------------------------
# AGENT MAIN FUNCTION
# -----------------------------
def run_agent(user_input: str) -> str:
    lower = user_input.lower()
    context = {"user_input": user_input, "tools": {}}

    # 1️⃣ WEATHER
    if "weather" in lower:
        city = extract_city(user_input)
        context["tools"]["weather"] = get_weather(city)

    # 2️⃣ HOTELS
    if any(x in lower for x in ["hotel", "stay", "accommodation"]):
        city = extract_city(user_input)
        context["tools"]["hotels"] = fetch_hotels(city)

    # 3️⃣ TRAINS
    if "train" in lower:
        context["tools"]["trains"] = get_trains("NDLS", "BCT", "2025-12-20")

    # 4️⃣ FLIGHTS
    if "flight" in lower or "fly" in lower:
        context["tools"]["flights"] = get_flights("DEL", "BOM", "2025-12-20")

    # 5️⃣ ITINERARY or PLAN
    if any(x in lower for x in ["plan", "itinerary", "trip"]):
        city = extract_city(user_input)
        context["tools"]["weather"] = get_weather(city)
        context["tools"]["hotels"] = fetch_hotels(city)
        context["tools"]["trains"] = get_trains("NDLS", "JP", "2025-12-20")

    prompt = (
        "You are a friendly travel assistant. "
        "Use the following context (in JSON) to generate a concise and engaging reply. "
        "If data includes weather, hotels, or transport, summarize them nicely. "
        "If user wants a plan, make a short itinerary.\n\n"
        + format_summary(context)
    )

    return call_gemini(prompt)

# -----------------------------
# Example run
# -----------------------------
if __name__ == "__main__":
    user_input = input("Ask something (e.g., 'Plan a trip to Goa for me'): ")
    print(run_agent(user_input))
