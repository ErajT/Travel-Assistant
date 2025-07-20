from typing import Any
import httpx
from mcp.server.fastmcp import FastMCP
import os
from dotenv import load_dotenv
load_dotenv()
from amadeus import Client, ResponseError

amadeus = Client()
amadeus.client_id = os.getenv('AMADEUS_CLIENT_ID')
amadeus.client_secret = os.getenv('AMADEUS_CLIENT_SECRET')

# Initialize FastMCP server
mcp = FastMCP("weather")

# Constants
NWS_API_BASE = "https://api.weather.gov"
USER_AGENT = "weather-app/1.0"

async def make_nws_request(url: str) -> dict[str, Any] | None:
    """Make a request to the NWS API with proper error handling."""
    headers = {
        "User-Agent": USER_AGENT,
        "Accept": "application/geo+json"
    }
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(url, headers=headers, timeout=30.0)
            response.raise_for_status()
            return response.json()
        except Exception:
            return None

async def make_request(url: str, headers: dict = {}) -> dict[str, Any] | None:
    """Generic HTTP request with error handling."""
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(url, headers=headers, timeout=30.0)
            response.raise_for_status()
            return response.json()
        except Exception:
            return None

def format_alert(feature: dict) -> str:
    """Format an alert feature into a readable string."""
    props = feature["properties"]
    return f"""
Event: {props.get('event', 'Unknown')}
Area: {props.get('areaDesc', 'Unknown')}
Severity: {props.get('severity', 'Unknown')}
Description: {props.get('description', 'No description available')}
Instructions: {props.get('instruction', 'No specific instructions provided')}
"""

@mcp.tool()
async def get_alerts(state: str) -> str:
    """Get weather alerts for a US state.

    Args:
        state: Two-letter US state code (e.g. CA, NY)
    """
    url = f"{NWS_API_BASE}/alerts/active/area/{state}"
    data = await make_nws_request(url)

    if not data or "features" not in data:
        return "Unable to fetch alerts or no alerts found."

    if not data["features"]:
        return "No active alerts for this state."

    alerts = [format_alert(feature) for feature in data["features"]]
    return "\n---\n".join(alerts)

@mcp.tool()
async def get_forecast(latitude: float, longitude: float) -> str:
    """Get weather forecast for a location.

    Args:
        latitude: Latitude of the location
        longitude: Longitude of the location
    """
    # First get the forecast grid endpoint
    points_url = f"{NWS_API_BASE}/points/{latitude},{longitude}"
    points_data = await make_nws_request(points_url)

    if not points_data:
        return "Unable to fetch forecast data for this location."

    # Get the forecast URL from the points response
    forecast_url = points_data["properties"]["forecast"]
    forecast_data = await make_nws_request(forecast_url)

    if not forecast_data:
        return "Unable to fetch detailed forecast."

    # Format the periods into a readable forecast
    periods = forecast_data["properties"]["periods"]
    forecasts = []
    for period in periods[:5]:  # Only show next 5 periods
        forecast = f"""
{period['name']}:
Temperature: {period['temperature']}°{period['temperatureUnit']}
Wind: {period['windSpeed']} {period['windDirection']}
Forecast: {period['detailedForecast']}
"""
        forecasts.append(forecast)

    return "\n---\n".join(forecasts)

@mcp.tool()
async def get_flights(from_city: str, to_city: str, date: str, adults: int = 1) -> str:
    """
    Search for flight offers using Amadeus.
    Args:
        from_city: IATA code for departure (e.g. 'NYC')
        to_city: IATA code for destination (e.g. 'LON')
        date: Departure date (YYYY-MM-DD)
        adults: Number of adult passengers
    """
    try:
        response = amadeus.shopping.flight_offers_search.get(
            originLocationCode=from_city,
            destinationLocationCode=to_city,
            departureDate=date,
            adults=adults
        )
        flights = response.data[:3]
        lines = [
            f"{f['itineraries'][0]['segments'][0]['carrierCode']} {f['itineraries'][0]['segments'][0]['number']}: "
            f"{f['itineraries'][0]['segments'][0]['departure']['iataCode']} → "
            f"{f['itineraries'][0]['segments'][-1]['arrival']['iataCode']} | "
            f"Price: {f['price']['total']} {f['price']['currency']}"
            for f in flights
        ]
        return "\n".join(lines)
    except ResponseError as e:
        return f"Error fetching flights: {e}"

@mcp.tool()
async def get_hotels(city_code: str, checkin: str, checkout: str, adults: int = 2) -> str:
    """
    Search for hotel offers using Amadeus.
    Args:
        city_code: IATA or Amadeus code for the city (e.g. 'PAR')
        checkin: Check-in date (YYYY-MM-DD)
        checkout: Check-out date (YYYY-MM-DD)
        adults: Number of adults
    """
    try:
        response = amadeus.shopping.hotel_offers.get(
            cityCode=city_code,
            checkInDate=checkin,
            checkOutDate=checkout,
            adults=adults
        )
        hotels = response.data[:3]
        lines = [
            f"{h['hotel']['name']} | {h['offers'][0]['price']['total']} {h['offers'][0]['price']['currency']}"
            for h in hotels
        ]
        return "\n".join(lines)
    except ResponseError as e:
        return f"Error fetching hotels: {e}"
    
@mcp.tool()
async def get_places(city_code: str) -> str:
    """
    Get top destination content (e.g., restaurants, sightseeing) using Amadeus.
    Args:
        city_code: IATA or Amadeus city code (e.g. 'PAR')
    """
    try:
        response = amadeus.duty_of_care.safety.safety_rated_locations.get(
            cityCode=city_code
        )
        places = response.data[:5]
        lines = [
            f"{p.get('category', 'N/A')} - {p.get('name', 'Unknown')} (Rating: {p.get('score', 'N/A')})"
            for p in places
        ]
        return "\n".join(lines)
    except ResponseError:
        # Fallback to basic city search
        try:
            resp2 = amadeus.reference_data.locations.get(keyword=city_code, subType='CITY')
            cities = resp2.data[:1]
            return f"Found location: {cities[0]['name']}"
        except:
            return "Unable to fetch places."


@mcp.tool()
async def plan_budget(
    flight_cost: float,
    hotel_cost: float,
    daily_food: float,
    days: int,
    activities_cost: float = 0.0,
    transport_cost: float = 0.0
) -> str:
    """
    Estimate total trip cost with optional activity and transport budget.

    Args:
        flight_cost: Roundtrip flight cost
        hotel_cost: Total hotel cost (for all days)
        daily_food: Estimated daily food expense
        days: Number of days
        activities_cost: Total cost for all activities (optional)
        transport_cost: Local transport cost for entire trip (optional)
    """
    food_total = daily_food * days
    total = flight_cost + hotel_cost + food_total + activities_cost + transport_cost

    breakdown = f"""
💸 Estimated Budget for {days} Days:

✈️ Flight: ${flight_cost:.2f}
🏨 Hotel: ${hotel_cost:.2f}
🍽️ Food: ${food_total:.2f} (${daily_food:.2f}/day)
🚕 Transport: ${transport_cost:.2f}
🎟️ Activities: ${activities_cost:.2f}

🧾 **Total Estimated Budget: ${total:.2f}**
"""
    return breakdown.strip()


@mcp.tool()
async def plan_luggage(city: str, days: int, weather: str = "mild", travel_type: str = "leisure") -> str:
    """
    Suggest a basic luggage packing list.

    Args:
        city: Travel destination
        days: Number of travel days
        weather: Expected weather (hot, cold, rainy, mild)
        travel_type: Type of travel (leisure, business, adventure)
    """
    clothing = []
    essentials = ["Toiletries", "Passport/ID", "Phone + Charger", "Medications", "Travel documents", "Power adapter (if international)"]

    if weather == "hot":
        clothing += ["Lightweight T-shirts", "Shorts", "Sunglasses", "Hat", "Sunscreen"]
    elif weather == "cold":
        clothing += ["Warm sweaters", "Jacket/coat", "Gloves", "Beanie", "Thermal wear"]
    elif weather == "rainy":
        clothing += ["Raincoat/Umbrella", "Waterproof shoes", "Extra socks"]
    else:
        clothing += ["T-shirts", "Jeans/pants", "Comfortable shoes"]

    if travel_type == "business":
        clothing += ["Formal attire", "Dress shoes", "Laptop/Tablet", "Business cards"]
    elif travel_type == "adventure":
        clothing += ["Hiking shoes", "Backpack", "Reusable water bottle", "First aid kit"]

    # Estimate clothing based on days
    clothing += [f"{max(days, 3)} sets of underwear", f"{max(days, 3)} pairs of socks", f"{min(days, 5)} shirts/tops"]

    luggage_list = f"Packing list for a {days}-day {travel_type} trip to {city}:\n\n"
    luggage_list += "**Clothing:**\n- " + "\n- ".join(clothing) + "\n\n"
    luggage_list += "**Essentials:**\n- " + "\n- ".join(essentials)

    return luggage_list


if __name__ == "__main__":
    # Initialize and run the server
    mcp.run(transport='stdio')