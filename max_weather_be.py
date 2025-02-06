from fastapi import FastAPI, HTTPException, Depends
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jose import JWTError, jwt
from datetime import datetime, timedelta
import requests
import os
from dotenv import load_dotenv

load_dotenv()

SECRET_KEY = "your_secret_key"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/token")

GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
GOOGLE_WEATHER_API_URL = "https://maps.googleapis.com/maps/api/weather/json"

app = FastAPI()

def create_access_token(data: dict, expires_delta: timedelta | None = None):
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

def authenticate_user(token: str = Depends(oauth2_scheme)):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid or expired token")

@app.post("/token")
def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends()):
    user_dict = {"username": form_data.username}  # Dummy authentication, replace with real user validation
    access_token = create_access_token(data=user_dict)
    return {"access_token": access_token, "token_type": "bearer"}

@app.get("/weather")
def get_weather(city: str, token: str = Depends(authenticate_user)):
    if not GOOGLE_API_KEY:
        raise HTTPException(status_code=500, detail="Missing Google API Key")
    
    geocode_url = f"https://maps.googleapis.com/maps/api/geocode/json?address={city}&key={GOOGLE_API_KEY}"
    geocode_response = requests.get(geocode_url).json()
    
    if "results" not in geocode_response or not geocode_response["results"]:
        raise HTTPException(status_code=404, detail="City not found")
    
    location = geocode_response["results"][0]["geometry"]["location"]
    lat, lng = location["lat"], location["lng"]
    
    weather_url = f"{GOOGLE_WEATHER_API_URL}?lat={lat}&lon={lng}&key={GOOGLE_API_KEY}"
    weather_response = requests.get(weather_url).json()
    
    if "weather" not in weather_response:
        raise HTTPException(status_code=500, detail="Failed to fetch weather data")
    
    return {
        "city": city,
        "latitude": lat,
        "longitude": lng,
        "weather": weather_response["weather"]
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
