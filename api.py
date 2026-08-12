"""FastAPI endpoints for TripIQ tourism analytics."""

import os

import pandas as pd
from fastapi import FastAPI, HTTPException, Query


BASE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(BASE, "data_processed")

app = FastAPI(title="TripIQ API", version="1.0")


def load_data():
    """Load the small summary files used by the API."""
    return {
        "vfm": pd.read_parquet(os.path.join(DATA, "hotel_vfm_scores.parquet")),
        "sentiment": pd.read_parquet(os.path.join(DATA, "agg_hotel_sentiment.parquet")),
        "trip_type": pd.read_parquet(os.path.join(DATA, "agg_trip_type_ratings.parquet")),
        "recommendations": pd.read_parquet(os.path.join(DATA, "hotel_recommendations.parquet")),
        "weather": pd.read_csv(os.path.join(DATA, "weather_advisories.csv")),
        "forecast": pd.read_parquet(os.path.join(DATA, "demand_forecasts_2025.parquet")),
    }


data = load_data()


def records(dataframe):
    """Convert a DataFrame into JSON-friendly records."""
    return dataframe.where(pd.notna(dataframe), None).to_dict(orient="records")


@app.get("/")
def home():
    return {
        "message": "Welcome to the TripIQ API",
        "documentation": "/docs",
    }


@app.get("/hotels")
def get_hotels(city: str | None = None, limit: int = Query(default=20, ge=1, le=100)):
    """Return hotels, optionally filtered by city."""
    hotels = data["vfm"].copy()
    if city:
        hotels = hotels[hotels["city"].str.lower() == city.lower()]

    hotels = hotels.sort_values("vfm_score", ascending=False).head(limit)
    columns = ["hotel_id", "hotel_name", "city", "hotel_class", "avg_rating_overall", "vfm_score"]
    return records(hotels[columns])


@app.get("/hotels/{hotel_id}")
def get_hotel(hotel_id: int):
    """Return one hotel's value, sentiment, and trip-type summary."""
    hotel = data["vfm"][data["vfm"]["hotel_id"] == hotel_id]
    if hotel.empty:
        raise HTTPException(status_code=404, detail="Hotel not found")

    result = records(hotel)[0]
    result["sentiment"] = records(data["sentiment"][data["sentiment"]["hotel_id"] == hotel_id])
    result["trip_type_ratings"] = records(data["trip_type"][data["trip_type"]["hotel_id"] == hotel_id])
    return result


@app.get("/recommendations/{hotel_id}")
def get_recommendations(hotel_id: int):
    """Return the five most similar hotels for one hotel."""
    recommendations = data["recommendations"]
    recommendations = recommendations[recommendations["hotel_id"] == hotel_id]
    if recommendations.empty:
        raise HTTPException(status_code=404, detail="Recommendations not found")
    return records(recommendations.sort_values("rank"))


@app.get("/weather/{city}")
def get_weather(city: str):
    """Return the current saved seven-day weather advisory for a city."""
    weather = data["weather"]
    weather = weather[weather["city"].str.lower() == city.lower()]
    if weather.empty:
        raise HTTPException(status_code=404, detail="City not found")
    return records(weather.sort_values("date"))


@app.get("/forecast")
def get_forecast(continent: str | None = None):
    """Return 2025 tourism-demand forecasts, optionally filtered by continent."""
    forecast = data["forecast"].copy()
    if continent:
        forecast = forecast[forecast["continent"].str.lower() == continent.lower()]
    return records(forecast.sort_values("forecast_arrivals", ascending=False))
