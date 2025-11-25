from flask import Flask, request, jsonify
from langchain_google_genai import ChatGoogleGenerativeAI
from flask_cors import CORS
import os
from dotenv import load_dotenv
load_dotenv()
import json
from services.gemini_agent import get_agent
from sarvamai import SarvamAI
import tempfile

SARVAM_API_KEY = os.getenv("STT_API_KEY")
if not SARVAM_API_KEY:
    raise ValueError("SARVAM_API_KEY not found in .env file")

GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
if not GOOGLE_API_KEY:
    raise ValueError("GOOGLE_API_KEY not found in .env file")

# Set it in environment (for services that might need it)
os.environ["GOOGLE_API_KEY"] = GOOGLE_API_KEY
sarvam_client = SarvamAI(api_subscription_key=SARVAM_API_KEY)
app = Flask(__name__)
CORS(app)
@app.route('/')
def home():
    return jsonify({"message": "AI Travel Planner API is running "})


@app.route("/voice", methods=["POST"])
def voice_to_text():
    """Convert voice audio to text using Sarvam AI"""

    if "audio" not in request.files:
        return jsonify({"error": "No audio file provided"}), 400

    audio = request.files["audio"]

    if audio.filename == "":
        return jsonify({"error": "Empty audio file"}), 400

    tmp = tempfile.NamedTemporaryFile(delete=False, suffix=".webm")

    try:
        audio.save(tmp.name)
        tmp.close()

        with open(tmp.name, "rb") as f:
            response = sarvam_client.speech_to_text.translate(
                file=f,
                model="saaras:v2.5"
            )

        # Check if response has transcript
        if hasattr(response, 'transcript') and response.transcript:
            return jsonify({
                "text": response.transcript,
                "status": "success"
            }), 200
        else:
            # Response might have different structure
            return jsonify({
                "text": str(response),
                "status": "success"
            }), 200

    except Exception as e:
        print(f"[ERROR] Voice-to-text failed: {str(e)}")
        return jsonify({
            "error": "Failed to transcribe audio",
            "details": str(e)
        }), 500

    finally:
        # Clean up temporary file
        try:
            if os.path.exists(tmp.name):
                os.remove(tmp.name)
        except Exception as e:
            print(f"[WARNING] Could not delete temp file: {str(e)}")

# @app.route("/chat", methods=["POST"])
# def chat():
#     data = request.get_json()
#     user_message = data.get("message", "")
#
#     # Enhanced system instruction with date-handling logic
#     system_instruction = """
#     You are **TripMate**, an AI-powered travel assistant.
#
#     Your job:
#     - Understand natural chat messages from the user about trip planning.
#     - Use your tools (`get_trains`, `get_hotels`, `get_weather_forecast`) to fetch real data.
#     - Create a detailed markdown itinerary.
#
#     🔹 **Date Handling Rules (VERY IMPORTANT):**
#     - If the user does **not specify dates**, assume the trip starts **from tomorrow**.
#     - If the user mentions trip duration (like "3 days" or "5-day trip"), calculate `end_date` accordingly.
#     - Always use dates **within the year 2025**.
#     - Output all dates in `YYYY-MM-DD` format.
#     - If the user gives invalid or past dates, auto-correct to tomorrow instead.
#     - Never leave `start_date` or `end_date` empty.
#
#     🔹 **Trip Planning Rules:**
#     - If the budget seems too low, politely ask to increase it.
#     - If any tool fails (train/hotel/weather), continue with the rest.
#     - Use clean markdown formatting.
#
#     🔹 **Response Format:**
#     1️⃣ Trip Overview
#     2️⃣ How to Reach (train options)
#     3️⃣ Day-wise Plan (with weather and local travel)
#     4️⃣ Hotels
#     5️⃣ What to Pack
#     6️⃣ Total Budget Summary
#
#     Never show tool names, code, or Thought/Action reasoning in your reply.
#     """
#
#     full_prompt = f"{system_instruction}\n\nUser message: {user_message}"
#
#     try:
#         response = agent.invoke({"input": full_prompt})
#
#         # Agent returns dict — safely extract
#         if not isinstance(response, dict):
#             return jsonify({"reply": "⚠️ Unexpected response format from agent."}), 200
#
#         reply = response.get("output", "")
#         if not reply.strip():
#             reply = "⚠️ TripMate couldn’t complete the plan. Please try again later."
#
#         return jsonify({"reply": reply}), 200
#
#     except Exception as e:
#         print(f"[ERROR] Agent failed: {e}")
#         return jsonify({
#             "reply": "⚠️ TripMate encountered an internal issue and couldn’t finish your trip plan. Please try again later.",
#             "error_details": str(e)
#         }), 200

@app.route("/chat", methods=["POST"])
def chat():
    data = request.get_json()
    message = data.get("message", "")

    llm = ChatGoogleGenerativeAI(model="gemini-2.0-flash", temperature=0.2)

    extraction_prompt = f"""
    Extract the following details from this message:
    - from_city
    - to_city
    - start_date (Date of tomorrow if not mentioned, format: YYYY-MM-DD)
    - end_date (format: YYYY-MM-DD)
    - adults (default 2 if not mentioned)
    - budget (default 10000 if not mentioned)

    Message: "{message}"
    **Date Handling Rules (VERY IMPORTANT):**
    - If the user does **not specify dates**, assume the trip starts **from tomorrow**.
    - If the user mentions trip duration (like "3 days" or "5-day trip"), calculate `end_date` accordingly.
    -Output all dates in `YYYY-MM-DD` format.
    
    Respond in pure JSON like this:
    {{
      "from_city": "...",
      "to_city": "...",
      "start_date": "YYYY-MM-DD",
      "end_date": "YYYY-MM-DD",
      "adults": ,
      "budget": 
    }}
    """

    extraction_response = llm.invoke(extraction_prompt)
    raw_output = extraction_response.content.strip()

    # Handle code block formatting
    if raw_output.startswith("```"):
        raw_output = raw_output.strip("`")
        if raw_output.lower().startswith("json"):
            raw_output = raw_output[4:]
        raw_output = raw_output.strip()

    try:
        details = json.loads(raw_output)
    except json.JSONDecodeError as e:
        print("Invalid JSON output:", raw_output)
        return jsonify({"error": f"Invalid JSON: {str(e)}", "raw_output": raw_output}), 500

    from_city = details.get("from_city")
    to_city = details.get("to_city")
    start_date = details.get("start_date")
    end_date = details.get("end_date")
    adults = details.get("adults")
    budget = details.get("budget")

    # Create agent with the extracted parameters
    agent = get_agent(from_city, to_city, start_date, end_date, adults)

    prompt = f"""
You are a trip-mitra an expert travel planner creating a complete itinerary from {from_city} to {to_city}.

Trip Details:
- Travel Dates: {start_date} to {end_date}
- Travelers: {adults} adults
- Budget: ₹{budget}

IMPORTANT INSTRUCTIONS:
1. You have access to these tools: get_trains, get_flights, get_hotels, get_weather_forecast
2. Call each tool ONLY ONCE with input "fetch"
3. After collecting data from all tools, immediately provide your Final Answer
4. DO NOT ask follow-up questions or try to use tools again
5. If a tool fails, note it and continue with other tools
YOUR TASK: Create a comprehensive travel plan with the following sections:


TRANSPORTATION :
### Trains:
- Use the tool: get_trains (input: "fetch")
- This returns BOTH outbound and return journey trains in one call
- From the results, recommend:
  * Top 3 trains for outbound journey ({from_city} → {to_city} on {start_date})
  * Top 3 trains for return journey ({to_city} → {from_city} on {end_date})
- Selection criteria: Prefer overnight trains (saves daytime for activities), shorter duration, good class availability
- For each train provide: Name, Number, Departure time, Arrival time, Duration, Available classes
- If tool fails: Display "Train data unavailable due to API limit" and continue with other sections

### Flights:(Call only if budget is >10,000)
- Use the tool: get_flights (input: "fetch")
- This returns flights for complete round trip
- From the results, recommend:
  * Top 3 flight options considering both outbound and return
- Selection criteria: Lowest total cost, minimum stops, convenient timings
- For each flight provide: Airline name, Flight code(if available), Departure time, Arrival time, Total cost, Class.
-DO NOT write 'Not available' - if data is missing from API, skip that flight information.
- If tool fails: Display "Flight data unavailable due to API limit" and continue with other sections


ACCOMMODATION :

- Use the tool: get_hotels (input: "fetch")
- This returns all available hotels in {to_city}
- From the results, recommend TOP 3 hotels based on:
  * Budget-friendly (fits within ₹{budget} for {adults} people)
  * High ratings and positive reviews
  * Strategic location (close to most attractions in your itinerary - compare latitude/longitude)
  * Good cleanliness and service ratings
- For each hotel provide:
  * Hotel name
  * Brief description (2-3 sentences)
  * Price per night (approximate)
  * Nearby landmark (e.g., "500m from Kashi Vishwanath Temple")
  * Photo link (from the API response)
- If tool fails: Display "Hotel data unavailable due to API limit" and continue with other sections


DAY-WISE ITINERARY:

For each day of the trip, create a detailed plan:

### Day X Format:
**Weather:** [Insert weather info here - see weather guidelines below]

**Morning (6 AM - 12 PM):**
- Place 1: [Name] ([Time needed], [Timings: e.g., 8 AM - 10 AM])
- Place 2: [Name] ([Time needed], [Timings])

**Afternoon (12 PM - 5 PM):**
- Place 3: [Name] ([Time needed], [Timings])
- Lunch recommendation

**Evening (5 PM - 9 PM):**
- Place 4: [Name] ([Time needed], [Timings])
- Dinner recommendation

**Local Transportation for the day:**
[Suggest best local transport options: auto, cab, metro, bus, walking, etc.]

### Weather Guidelines:
- Use the tool: get_weather_forecast (input: "fetch") - CALL ONLY ONCE for entire trip
- **Day 1:** Provide complete weather summary
  * Temperature range (e.g., "22°C to 30°C")
  * Humidity level
  * Rain probability
  * For hill stations ONLY: Sunrise and sunset times
  * Example: "Pleasant weather with temperatures between 22-30°C, low humidity (40%), no rain expected"
- **Day 2 onwards:**
  * If weather is same/similar: Write "Weather similar to Day 1"
  * If weather changes significantly: Mention only the changes (e.g., "Light rain expected in afternoon, carry umbrella")
- **IMPORTANT:** Add weather info WITHIN each day's section, NOT as a separate section
- If tool fails: Display "Weather data unavailable due to API limit" and continue


PACKING LIST:

Create a practical packing checklist based on:
- Weather conditions during travel dates
- Activities planned in the itinerary
- Duration of trip
- Type of destinations (urban, hill station, beach, religious, etc.)

Group items into categories: Clothing, Documents, Toiletries, Electronics, Medicines, Miscellaneous



## SECTION 5: ESTIMATED COST BREAKDOWN

Provide a detailed budget breakdown:
- Train/Flight tickets (both ways): ₹____
- Accommodation (per night × nights): ₹____
- Local transportation (daily estimate × days): ₹____
- Food (breakfast, lunch, dinner × days): ₹____
- Entry fees for attractions: ₹____
- Shopping/Miscellaneous (10-15% buffer): ₹____
**TOTAL ESTIMATED COST:** ₹____

Compare with budget: ₹{budget}
[Mention if within budget or suggest adjustments]



FORMATTING REQUIREMENTS:
✓ Use markdown formatting for clear readability
✓ Use headers (##, ###), bullet points, and bold text appropriately
✓ Keep descriptions concise - no unnecessary verbosity
✓ If ANY tool fails, continue creating the itinerary with available data
✓ NEVER stop execution midway - always deliver a complete plan

CRITICAL RULE: Even if 1 or 2 tools fail, you MUST still generate a complete itinerary using whatever data is available. A partial plan is better than no plan.
COMPLETION CHECKLIST (for your internal use):
□ Called get_trains (or noted failure)
□ Called get_flights (or noted failure)  
□ Called get_hotels (or noted failure)
□ Called get_weather_forecast (or noted failure)
□ Created day-wise itinerary
□ Added packing list
□ Added cost breakdown

Once you have completed the above checklist, immediately provide your Final Answer with the complete itinerary in markdown format. Do not ask for more information or try to use tools again.

"""
    try:
        response = agent.run(prompt)
        return jsonify({"reply": response})
    except Exception as e:
        return jsonify({"error": f"Agent execution failed: {str(e)}"}), 500


if __name__ == "__main__":
    app.run(debug=True)
