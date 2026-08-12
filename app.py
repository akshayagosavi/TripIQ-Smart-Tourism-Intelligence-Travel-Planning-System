"""Interactive Streamlit travel planner for the TripIQ project."""

import os

import pandas as pd
import streamlit as st


BASE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(BASE, "data_processed")


@st.cache_data
def load_data():
    """Load summary files once, so dashboard interactions stay fast."""
    return {
        "vfm": pd.read_parquet(os.path.join(DATA, "hotel_vfm_scores.parquet")),
        "crowd": pd.read_parquet(os.path.join(DATA, "city_monthly_crowd_scores.parquet")),
        "trip_type": pd.read_parquet(os.path.join(DATA, "agg_trip_type_ratings.parquet")),
        "sentiment": pd.read_parquet(os.path.join(DATA, "agg_hotel_sentiment.parquet")),
        "recommendations": pd.read_parquet(os.path.join(DATA, "hotel_recommendations.parquet")),
        "weather": pd.read_csv(os.path.join(DATA, "weather_advisories.csv")),
        "forecast": pd.read_parquet(os.path.join(DATA, "demand_forecasts_2025.parquet")),
    }


def add_style():
    """Add a small visual theme without adding another front-end framework."""
    st.markdown("""
    <style>
        .stApp { background: #f7fafc; color: #18212f; }
        [data-testid="stSidebar"] { background: #0f2537; }
        [data-testid="stSidebar"] * { color: #f7fafc; }
        .hero { background: linear-gradient(120deg, #0f2537, #146c94);
                border-radius: 18px; padding: 2.2rem; color: white; margin-bottom: 1.5rem; }
        .hero h1 { color: white; margin: 0; font-size: 2.4rem; }
        .hero p { color: #dcecf4; font-size: 1.1rem; margin-bottom: 0; }
        .trip-card { background: white; border: 1px solid #e3ebf0; border-left: 5px solid #17a2b8;
                     border-radius: 12px; padding: 1rem 1.2rem; margin: 0.7rem 0;
                     box-shadow: 0 2px 8px rgba(15, 37, 55, 0.05); }
        .trip-card h4 { margin: 0 0 0.35rem 0; color: #0f2537; }
        .muted { color: #667085; }
    </style>
    """, unsafe_allow_html=True)


def get_daily_activity(advisory, trip_type):
    """Choose a simple day plan from the saved weather advisory."""
    indoor = "Visit a museum or local indoor attraction, then enjoy a relaxed dinner."
    if "Thunderstorms" in advisory or "Rain likely" in advisory or "Snow" in advisory:
        return indoor
    if "Very hot" in advisory:
        return "Plan outdoor sightseeing in the morning, rest indoors at midday, and explore in the evening."
    if trip_type == "family":
        return "Choose a family-friendly attraction, add a park break, and finish with an early dinner."
    if trip_type == "couple":
        return "Explore a scenic neighbourhood, enjoy a café break, and reserve the evening for a special meal."
    if trip_type == "friends":
        return "Explore a popular district together, try a group activity, and enjoy the city nightlife."
    if trip_type == "solo":
        return "Take a self-guided city walk, visit a local attraction, and choose a well-reviewed restaurant."
    return "Explore a landmark or local neighbourhood, with time for food and flexible sightseeing."


def hotel_details(data, hotel_id):
    """Return one selected hotel's related summary data."""
    hotel = data["vfm"][data["vfm"]["hotel_id"] == hotel_id].iloc[0]
    sentiment = data["sentiment"]
    sentiment = sentiment[sentiment["hotel_id"] == hotel_id]
    trip_type = data["trip_type"]
    trip_type = trip_type[trip_type["hotel_id"] == hotel_id]
    return hotel, sentiment, trip_type


def show_trip_planner(data):
    st.markdown('<div class="hero"><h1>Plan your next trip</h1><p>Build a simple itinerary using hotel quality, travel style, crowd history, and weather advice.</p></div>', unsafe_allow_html=True)

    cities = sorted(data["weather"]["city"].unique())
    first, second, third = st.columns(3)
    city = first.selectbox("Destination", cities)
    trip_type = second.selectbox("Travel style", ["family", "couple", "solo", "friends"])
    days = third.slider("Number of days", min_value=1, max_value=7, value=3)

    city_hotels = data["vfm"][data["vfm"]["city"] == city].sort_values("vfm_score", ascending=False)
    hotel_names = city_hotels["hotel_name"].tolist()
    hotel_name = st.selectbox("Suggested hotel", hotel_names)
    hotel_id = city_hotels[city_hotels["hotel_name"] == hotel_name].iloc[0]["hotel_id"]
    hotel, sentiment, trip_ratings = hotel_details(data, hotel_id)

    st.subheader("Your stay")
    first, second, third, fourth = st.columns(4)
    first.metric("Overall rating", f"{hotel['avg_rating_overall']:.1f} / 5")
    second.metric("Value score", f"{hotel['vfm_score']:.2f}")
    third.metric("Hotel class", f"{hotel['hotel_class']:.1f} star")
    average_sentiment = sentiment["average_sentiment"].iloc[0] if not sentiment.empty else 0
    fourth.metric("Review sentiment", f"{average_sentiment:.2f}")

    trip_score = trip_ratings[trip_ratings["trip_type"] == trip_type]
    if not trip_score.empty:
        score = trip_score["rating_overall_mean"].iloc[0]
        st.info(f"Travellers on a {trip_type} trip gave this hotel an average rating of {score:.2f} / 5.")

    weather = data["weather"]
    weather = weather[weather["city"] == city].head(days).copy()
    weather["date"] = pd.to_datetime(weather["date"])

    st.subheader("Day-by-day itinerary")
    for day_number, (_, day) in enumerate(weather.iterrows(), start=1):
        activity = get_daily_activity(day["advisory"], trip_type)
        date = day["date"].strftime("%A, %d %b")
        st.markdown(
            f'<div class="trip-card"><h4>Day {day_number} · {date}</h4>'
            f'<span class="muted">{day["min_temperature_c"]:.0f}°C to {day["max_temperature_c"]:.0f}°C · '
            f'Rain chance {day["rain_probability_pct"]}%</span><br><br>'
            f'<b>Travel advice:</b> {day["advisory"]}<br>'
            f'<b>Suggested plan:</b> {activity}</div>',
            unsafe_allow_html=True,
        )

    st.subheader("Similar hotels to consider")
    recommendations = data["recommendations"]
    recommendations = recommendations[recommendations["hotel_id"] == hotel_id][
        ["rank", "recommended_hotel_name", "recommended_city", "similarity_score"]
    ]
    st.dataframe(recommendations, hide_index=True, width="stretch")


def show_hotel_explorer(data):
    st.header("Find a hotel")
    vfm = data["vfm"].merge(data["sentiment"], on="hotel_id", how="left")
    city = st.selectbox("Choose a city", sorted(vfm["city"].dropna().unique()))
    hotel_class = st.slider("Minimum hotel class", 0.0, 5.0, 3.0, 0.5)

    hotels = vfm[(vfm["city"] == city) & (vfm["hotel_class"] >= hotel_class)]
    hotels = hotels.sort_values("vfm_score", ascending=False)
    st.dataframe(
        hotels[["hotel_name", "hotel_class", "avg_rating_overall", "vfm_score", "average_sentiment"]],
        hide_index=True,
        width="stretch",
    )


def show_city_insights(data):
    st.header("City insights")
    city = st.selectbox("Choose a city", sorted(data["crowd"]["city"].dropna().unique()))
    crowd = data["crowd"]
    crowd = crowd[crowd["city"] == city].copy()
    crowd["month"] = pd.to_datetime(dict(year=crowd["review_year"], month=crowd["review_month"], day=1))
    crowd = crowd.sort_values("month")

    st.subheader("Historical crowd score")
    st.line_chart(crowd.set_index("month")["crowd_score"])
    st.caption("A higher score means more hotel-review activity in that city and month.")

    weather = data["weather"]
    weather = weather[weather["city"] == city]
    st.subheader("Current saved weather advisory")
    st.dataframe(weather[["date", "advisory", "max_temperature_c", "rain_probability_pct"]], hide_index=True, width="stretch")


def show_demand_forecast(data):
    st.header("Tourism demand forecast")
    forecast = data["forecast"]
    continent = st.selectbox("Choose a continent", ["All"] + sorted(forecast["continent"].dropna().unique()))
    if continent != "All":
        forecast = forecast[forecast["continent"] == continent]

    forecast = forecast.sort_values("forecast_arrivals", ascending=False)
    st.bar_chart(forecast.head(15).set_index("country")["forecast_arrivals"])
    st.dataframe(forecast, hide_index=True, width="stretch")
    st.caption("Forecasts are model estimates from historical international-arrival data.")


def main():
    st.set_page_config(page_title="TripIQ", page_icon="✈️", layout="wide")
    add_style()
    data = load_data()

    st.sidebar.title("TripIQ")
    page = st.sidebar.radio(
        "Menu",
        ["Plan my trip", "Find a hotel", "City insights", "Demand forecast"],
    )
    st.sidebar.caption("Smart tourism intelligence for better travel decisions.")

    if page == "Plan my trip":
        show_trip_planner(data)
    elif page == "Find a hotel":
        show_hotel_explorer(data)
    elif page == "City insights":
        show_city_insights(data)
    else:
        show_demand_forecast(data)


if __name__ == "__main__":
    main()
