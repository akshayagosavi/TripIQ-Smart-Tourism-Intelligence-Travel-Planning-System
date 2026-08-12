"""Download a 7-day weather forecast and create simple travel advice."""

import os

import pandas as pd
import requests


BASE = os.path.dirname(os.path.abspath(__file__))
OUTPUT_FILE = os.path.join(BASE, "data_processed", "weather_advisories.csv")
FORECAST_URL = "https://api.open-meteo.com/v1/forecast"

# The hotel-review dataset contains these 25 US cities.
CITIES = {
    "New York City": (40.7128, -74.0060),
    "Los Angeles": (34.0522, -118.2437),
    "Houston": (29.7604, -95.3698),
    "Chicago": (41.8781, -87.6298),
    "Philadelphia": (39.9526, -75.1652),
    "Phoenix": (33.4484, -112.0740),
    "San Antonio": (29.4241, -98.4936),
    "San Diego": (32.7157, -117.1611),
    "Dallas": (32.7767, -96.7970),
    "San Jose": (37.3382, -121.8863),
    "Jacksonville": (30.3322, -81.6557),
    "Indianapolis": (39.7684, -86.1581),
    "Austin": (30.2672, -97.7431),
    "San Francisco": (37.7749, -122.4194),
    "Columbus": (39.9612, -82.9988),
    "Detroit": (42.3314, -83.0458),
    "Charlotte": (35.2271, -80.8431),
    "Fort Worth": (32.7555, -97.3308),
    "El Paso": (31.7619, -106.4850),
    "Memphis": (35.1495, -90.0490),
    "Seattle": (47.6062, -122.3321),
    "Boston": (42.3601, -71.0589),
    "Baltimore": (39.2904, -76.6122),
    "Denver": (39.7392, -104.9903),
    "Washington DC": (38.9072, -77.0369),
}


def get_advisory(weather_code, rain_chance, max_temp, min_temp, max_wind):
    """Return one short piece of travel advice for the day's main condition."""
    if weather_code >= 95:
        return "Thunderstorms possible. Keep outdoor plans flexible."
    if weather_code in [71, 73, 75, 77, 85, 86]:
        return "Snow expected. Allow extra travel time."
    if rain_chance >= 60:
        return "Rain likely. Carry an umbrella and plan indoor activities."
    if max_temp >= 35:
        return "Very hot. Carry water and avoid long midday walks."
    if min_temp <= 0:
        return "Freezing temperatures. Dress warmly and check road conditions."
    if max_wind >= 50:
        return "Windy conditions. Secure outdoor plans."
    return "Good conditions for sightseeing."


def get_city_forecast(city, latitude, longitude):
    """Request the next seven days of daily weather for one city."""
    parameters = {
        "latitude": latitude,
        "longitude": longitude,
        "daily": "weather_code,temperature_2m_max,temperature_2m_min,precipitation_probability_max,wind_speed_10m_max",
        "timezone": "auto",
        "forecast_days": 7,
    }
    response = requests.get(FORECAST_URL, params=parameters, timeout=30)
    response.raise_for_status()
    daily = response.json()["daily"]

    rows = []
    for index, date in enumerate(daily["time"]):
        weather_code = daily["weather_code"][index]
        rain_chance = daily["precipitation_probability_max"][index]
        max_temp = daily["temperature_2m_max"][index]
        min_temp = daily["temperature_2m_min"][index]
        max_wind = daily["wind_speed_10m_max"][index]

        rows.append({
            "city": city,
            "date": date,
            "weather_code": weather_code,
            "max_temperature_c": max_temp,
            "min_temperature_c": min_temp,
            "rain_probability_pct": rain_chance,
            "max_wind_kmh": max_wind,
            "advisory": get_advisory(weather_code, rain_chance, max_temp, min_temp, max_wind),
        })
    return rows


def main():
    all_rows = []

    for city, coordinates in CITIES.items():
        print(f"Downloading forecast for {city}...")
        latitude, longitude = coordinates
        all_rows.extend(get_city_forecast(city, latitude, longitude))

    weather_df = pd.DataFrame(all_rows)
    weather_df.to_csv(OUTPUT_FILE, index=False)
    print(f"Saved {len(weather_df)} weather advisories to {OUTPUT_FILE}")


if __name__ == "__main__":
    main()
