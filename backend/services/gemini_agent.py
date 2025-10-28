import os
from langchain.agents import initialize_agent, Tool
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.agents.agent_types import AgentType
import json

# Import service functions - adjust these imports based on your actual structure
try:
    from services.weather_service import parse_weather_data
    from services.hotel_service import parse_hotel_info
    from services.train_service import get_trains_to_and_from_city
except ImportError:
    # If running from within services folder
    from weather_service import parse_weather_data
    from hotel_service import parse_hotel_info
    from train_service import get_trains_to_and_from_city

# Get API key - it should already be in environment from app.py
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")

if not GOOGLE_API_KEY:
    raise ValueError(
        "GOOGLE_API_KEY not found in environment variables. Make sure it's loaded before importing this module.")


class WeatherTool:
    def __call__(self, to_city, start_date, end_date):
        try:
            return json.dumps(parse_weather_data(to_city, start_date, end_date), indent=2)
        except Exception as e:
            return f"Could not get weather data: {str(e)}"


class HotelTool:
    def __call__(self, to_city, start_date, end_date, adults):
        try:
            return parse_hotel_info(to_city, start_date, end_date, adults)
        except Exception as e:
            return f"Hotel tool failed: {str(e)}"


class TrainTool:
    def __call__(self, from_city, to_city, start_date, end_date):
        try:
            return get_trains_to_and_from_city(from_city, to_city, start_date, end_date)
        except Exception as e:
            return f"Train tool failed: {str(e)}"


def build_itinerary_prompt(from_city, to_city, start_date, end_date, adults, budget):
    return f"""
    Plan a detailed family trip from {from_city} to {to_city}:
    - Dates: {start_date} to {end_date}
    - Number of People: {adults}
    - Budget: ₹{budget}
    Include:
                1. How to reach (train/bus/flight):
                    -steps for getting train data 
                            1) call get_trains once for {from_city} to {to_city}
                            2) it will return a list of trains data including train name ,departure ,arrival, duration,price for both on start date and end date.
                            3) your task is suggest best 3 trains for traveling to city and 3 trains for returning.(suggestion includes minimum travel duration,all night travel is prefered for saving time in trip, and classes availbale should be good)
                            4) give train names, travel time ,departure and arrival and classes.
                            if api fails to fetch train data then tell 'no train data found due to api limit exausted' nothing else.
                2. Local travel options(Don't give this at above or below of itinerary ,instead of give this with day wise plan for better understanding)
                3. Places to visit each day (with timings and time needed at each place)
                4. What to pack
                5. Call `get_hotels` once and get all hotel information. 
                    - You are a travel assistant. Based on the itinerary you have made, recommend top 3 best-reviewed hotels for a trip to {to_city}.
                    - Total budget: ₹{budget} for {adults} people
                    - Hotels should be affordable, well-reviewed , and closer to most of the places in the itinerary so user has to travel minimum.(do this by comparing lat,long of hotels) 
                    - cleanliness, and service.
                    - Give names, short description, and approx price per night ,also tell this hotel is near by this famous location(i.e hotel is near to kashi vishwanath temple), aslo provide link of photo (in hotels_data output there is one output like photo.)
                    if api fails to fetch hotels data then tell 'no hotel data found due to api limit exausted' nothing else.
                6. Total estimated cost breakdown
                7. Call `get_weather_forecast` once for the full range: {to_city}, {start_date}, {end_date}'.
                    - For Day 1: summarize  full weather info and say like this: temp will be around this to this,no humidity,if places are hill station then only tell about sunrise  and sunsets .
                    - From Day 2 onward:
                    - If weather is similar, just write: "Weather similar to Day 1"
                    - If weather changes (e.g., rain, high temp, strong wind), highlight only key changes or alerts.
                    - If weather is not available, just write: "Weather similar to Day 1"
                    if api fails to fetch weather data then tell 'no weather data found due to api limit exausted' nothing else.

                important notes -> Add weather information only in day wise planning not outside it ,add outside only if it is only one day planning.
                                -> output should be in markdown format for better user experience in app and do not include extra unneccessary things.

                """


def get_agent():
    """Factory function to create agent with API key"""
    # Initialize LLM with explicit API key
    llm = ChatGoogleGenerativeAI(
        model="gemini-2.0-flash-exp",  # Using available model
        google_api_key=GOOGLE_API_KEY,
        temperature=0.7
    )

    # Create tool instances
    weather_tool_instance = WeatherTool()
    hotel_tool_instance = HotelTool()
    train_tool_instance = TrainTool()

    # Define tools - these need to accept string input from the agent
    tools = [
        Tool(
            name="get_weather_forecast",
            func=lambda x: weather_tool_instance(
                x.split('|')[0] if '|' in x else x,
                x.split('|')[1] if '|' in x and len(x.split('|')) > 1 else "",
                x.split('|')[2] if '|' in x and len(x.split('|')) > 2 else ""
            ),
            description="Get weather forecast for a city. Input format: 'city|start_date|end_date'"
        ),
        Tool(
            name="get_hotels",
            func=lambda x: hotel_tool_instance(
                x.split('|')[0] if '|' in x else x,
                x.split('|')[1] if '|' in x and len(x.split('|')) > 1 else "",
                x.split('|')[2] if '|' in x and len(x.split('|')) > 2 else "",
                int(x.split('|')[3]) if '|' in x and len(x.split('|')) > 3 else 2
            ),
            description="Get hotel information for a city. Input format: 'city|start_date|end_date|adults'"
        ),
        Tool(
            name="get_trains",
            func=lambda x: train_tool_instance(
                x.split('|')[0] if '|' in x else "",
                x.split('|')[1] if '|' in x and len(x.split('|')) > 1 else x,
                x.split('|')[2] if '|' in x and len(x.split('|')) > 2 else "",
                x.split('|')[3] if '|' in x and len(x.split('|')) > 3 else ""
            ),
            description="Get train information between two cities. Input format: 'from_city|to_city|start_date|end_date'"
        )
    ]

    # Initialize agent
    return initialize_agent(
        tools,
        llm,
        agent=AgentType.ZERO_SHOT_REACT_DESCRIPTION,
        verbose=True,
        handle_parsing_errors=True,
        max_iterations=10
    )


# Create agent instance
agent = get_agent()