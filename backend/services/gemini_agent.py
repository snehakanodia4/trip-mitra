import os
from langchain.agents import initialize_agent, Tool
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.agents.agent_types import AgentType
from langchain.tools import StructuredTool

import json

# Import service functions - adjust these imports based on your actual structure
try:
    from services.weather_service import parse_weather_data
    from services.hotel_service import parse_hotel_info
    from services.train_service import get_trains_to_and_from_city
    from services.flight_service import get_flight_data
except ImportError:

    from weather_service import parse_weather_data
    from hotel_service import parse_hotel_info
    from train_service import get_trains_to_and_from_city
    from flight_service import get_flight_data


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

class FlightTool:
    def __call__(self,from_city, to_city, start_date,end_date,adults):
        try:
            return get_flight_data(from_city,to_city, start_date, end_date, adults)
        except Exception as e:
            return f"Hotel tool failed: {str(e)}"


class TrainTool:
    def __call__(self, from_city, to_city, start_date, end_date):
        try:
            return get_trains_to_and_from_city(from_city, to_city, start_date, end_date)
        except Exception as e:
            return f"Train tool failed: {str(e)}"



def get_agent(from_city, to_city, start_date, end_date, adults):
    """
    Creates a LangChain agent with travel planning tools.
    """
    llm = ChatGoogleGenerativeAI(
        model="gemini-2.5-pro",
        google_api_key=GOOGLE_API_KEY,
        temperature=0.7
    )

    # Create tool instances
    weather_tool_instance = WeatherTool()
    hotel_tool_instance = HotelTool()
    train_tool_instance = TrainTool()
    flight_tool_instance = FlightTool()

    # Wrapper functions that accept a dummy input
    def get_weather_wrapper(query: str = "fetch") -> str:
        """Get weather forecast for the destination city."""
        return weather_tool_instance(to_city, str(start_date), str(end_date))

    def get_hotels_wrapper(query: str = "fetch") -> str:
        """Get hotel information for the destination city."""
        return hotel_tool_instance(to_city, str(start_date), str(end_date), adults)

    def get_trains_wrapper(query: str = "fetch") -> str:
        """Get train information between origin and destination."""
        return train_tool_instance(from_city, to_city, str(start_date), str(end_date))

    def get_flights_wrapper(query: str= "fetch") -> str:
        """Get flight information between origin and destination."""
        return flight_tool_instance(from_city, to_city, str(start_date), str(end_date),adults)
    # Define tools using StructuredTool
    tools = [
        StructuredTool.from_function(
            func=get_weather_wrapper,
            name="get_weather_forecast",
            description=f"Use this to get weather forecast for {to_city} from {start_date} to {end_date}. Just pass any string like 'fetch' or 'get weather'."
        ),
        StructuredTool.from_function(
            func=get_hotels_wrapper,
            name="get_hotels",
            description=f"Use this to get hotel listings in {to_city} for {adults} adults from {start_date} to {end_date}. Just pass any string like 'fetch' or 'get hotels'."
        ),
        StructuredTool.from_function(
            func=get_trains_wrapper,
            name="get_trains",
            description=f"Use this to get train schedules from {from_city} to {to_city}. Outbound on {start_date}, return on {end_date}. Just pass any string like 'fetch' or 'get trains'."
        ),
        StructuredTool.from_function(
            func=get_flights_wrapper,
            name="get_flights",
            description=f"Use this to get flights schedules from {from_city} to {to_city} for {adults}. Outbound on {start_date}, return on {end_date}. Just pass any string like 'fetch' or 'get flights'."
        )

    ]

    return initialize_agent(
        tools,
        llm,
        agent=AgentType.ZERO_SHOT_REACT_DESCRIPTION,
        verbose=True,
        handle_parsing_errors="Check your output and make sure it conforms! If you're done, use 'Final Answer:' to provide your response.",
        max_iterations=15,
        early_stopping_method="generate",
        return_intermediate_steps=False
    )