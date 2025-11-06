from flask import Flask, request, jsonify
from langchain_google_genai import ChatGoogleGenerativeAI
from flask_cors import CORS
import os
from dotenv import load_dotenv
load_dotenv()
import json

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


@app.route("/chat", methods=["POST"])
def chat():
    data = request.get_json()
    message = data.get("message", "")

    llm = ChatGoogleGenerativeAI(model="gemini-2.5-pro", temperature=0.2)

    extraction_prompt = f"""
    Extract the following details from this message:
    - from_city
    - to_city
    - start_date (Date of tomorrow if not mentioned)
    - end_date
    - adults (default 2 if not mentioned)
    - budget (default 10000 if not mentioned)

    Message: "{message}"

    Respond in pure JSON like this:
    {{
      "from_city": "...",
      "to_city": "...",
      "start_date": "...",
      "end_date": "...",
      "adults": ...,
      "budget": ...
    }}
    """

    extraction_response = llm.invoke(extraction_prompt)
    raw_output = extraction_response.content.strip()

    # Handle code block formatting
    if raw_output.startswith("```"):
        raw_output = raw_output.strip("`")
        if raw_output.lower().startswith("json"):
            raw_output = raw_output[4:]  # remove the 'json' after ```
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

    prompt = build_itinerary_prompt(from_city, to_city, start_date, end_date, adults, budget)

    response = agent.run(prompt)
    print("Gemini raw response:", response.text)
    return jsonify({"reply": response})




if __name__ == "__main__":
    app.run(debug=True)
