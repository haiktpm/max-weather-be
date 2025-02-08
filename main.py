from fastapi import FastAPI, Query
import requests

app = FastAPI()

# Open-Meteo APIs
GEO_URL = "https://geocoding-api.open-meteo.com/v1/search"
WEATHER_URL = "https://api.open-meteo.com/v1/forecast"

def get_coordinates(city: str):
    """Fetches latitude and longitude for a city using Open-Meteo Geocoding API."""
    response = requests.get(GEO_URL, params={"name": city, "count": 1})
    data = response.json()

    if "results" in data and len(data["results"]) > 0:
        location = data["results"][0]
        return location["latitude"], location["longitude"]
    return None, None

@app.get("/weather")
def get_weather(city: str = Query(..., description="City name"), days: int = Query(1, description="Forecast days (1-7)")):
    """Fetches weather forecast for a given city."""
    
    lat, lon = get_coordinates(city)
    if lat is None or lon is None:
        return {"error": "City not found"}

    params = {
        "latitude": lat,
        "longitude": lon,
        "daily": ["temperature_2m_max", "temperature_2m_min"],
        "timezone": "auto",
    }
    
    response = requests.get(WEATHER_URL, params=params)
    
    if response.status_code == 200:
        return response.json()
    return {"error": "Failed to fetch weather data"}

# Run the app: uvicorn main:app --reload
