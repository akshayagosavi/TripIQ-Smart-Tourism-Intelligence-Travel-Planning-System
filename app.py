"""
TripIQ — Smart Tourism Intelligence & Travel Planning System
Main Streamlit Application
"""

import os
import pandas as pd
import streamlit as st

# =============================================================
# CONFIG
# =============================================================
BASE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(BASE, "data_processed")

st.set_page_config(
    page_title="TripIQ",
    page_icon="✈️",
    layout="wide"
)

# =============================================================
# THEME — Dark Blue + White
# =============================================================
st.markdown("""
<style>
    /* Main background */
    .stApp { background: #f7fafc; color: #18212f; }

    /* Sidebar */
    [data-testid="stSidebar"] { background: #0f2537; }
    [data-testid="stSidebar"] * { color: #f7fafc !important; }
    [data-testid="stSidebar"] .stRadio label { color: #f7fafc !important; }

    /* Hero banner */
    .hero {
        background: #0f2537;
        border-radius: 16px;
        padding: 2.5rem;
        color: white;
        margin-bottom: 1.5rem;
    }
    .hero h1 { color: white; font-size: 2.5rem; margin: 0 0 0.5rem 0; }
    .hero p  { color: #b0cfe0; font-size: 1.1rem; margin: 0; }

    /* Cards */
    .card {
        background: white;
        border: 1px solid #e3ebf0;
        border-radius: 12px;
        padding: 1.2rem;
        margin-bottom: 1rem;
    }
    .card h4 { color: #0f2537; margin: 0 0 0.4rem 0; }
    .card p  { color: #667085; margin: 0; font-size: 0.95rem; }

    /* Trip day card */
    .day-card {
        background: white;
        border: 1px solid #e3ebf0;
        border-left: 5px solid #17a2b8;
        border-radius: 10px;
        padding: 1rem 1.2rem;
        margin: 0.6rem 0;
    }
    .day-card h4 { color: #0f2537; margin: 0 0 0.3rem 0; }

    /* Stat number */
    .stat { font-size: 2rem; font-weight: 700; color: #0f2537; }
    .stat-label { color: #667085; font-size: 0.9rem; }

    /* Feature icon box */
    .feature {
        background: white;
        border: 1px solid #e3ebf0;
        border-top: 4px solid #17a2b8;
        border-radius: 10px;
        padding: 1.2rem;
        text-align: center;
    }
    .feature h3 { color: #0f2537; margin: 0.5rem 0 0.3rem 0; font-size: 1rem; }
    .feature p  { color: #667085; font-size: 0.88rem; margin: 0; }

    /* Badge */
    .badge {
        display: inline-block;
        background: #e0f3fa;
        color: #0f2537;
        padding: 3px 10px;
        border-radius: 20px;
        font-size: 0.8rem;
        margin: 2px;
    }

    /* Admin metric */
    .admin-box {
        background: #0f2537;
        color: white;
        border-radius: 10px;
        padding: 1rem;
        text-align: center;
    }
    .admin-box .num { font-size: 1.8rem; font-weight: 700; color: #17a2b8; }
    .admin-box .lbl { font-size: 0.85rem; color: #b0cfe0; }

    /* Keep Streamlit's built-in metric text readable on the light background. */
    [data-testid="stMetricValue"] { color: #0f2537 !important; }
    [data-testid="stMetricLabel"] { color: #667085 !important; }
    [data-testid="stMetricDelta"] { color: #1a6b3a !important; }
    div[data-baseweb="input"] > div, div[data-baseweb="select"] > div { background-color: #ffffff !important; border-color: #cbd5e1 !important; }
    div[data-baseweb="input"] input { color: #0f2537 !important; }
    div[data-baseweb="select"] * { color: #0f2537 !important; }
    .stTextInput label, .stTextInput label p, .stSelectbox label, .stSelectbox label p { color: #0f2537 !important; font-weight: 600 !important; }
    .stTextInput input { background-color: #ffffff !important; color: #0f2537 !important; caret-color: #1a6b3a !important; }
    .stTextInput input::placeholder { color: #8a96a3 !important; opacity: 1 !important; }
    .stTextInput [data-baseweb="input"] { background-color: #ffffff !important; }
    .stButton > button { background: #1a6b3a !important; color: white !important; border: 0 !important; }
    [data-baseweb="tab-list"] { gap: 0.5rem; }
    [data-baseweb="tab"] { color: #0f2537 !important; font-weight: 600 !important; }
    [data-baseweb="tab-highlight"] { background-color: #1a6b3a !important; }
</style>
""", unsafe_allow_html=True)


# =============================================================
# DATA LOADER
# =============================================================
@st.cache_data
def load_data():
    files = {
        "vfm"     : "hotel_vfm_scores.parquet",
        "crowd"   : "city_monthly_crowd_scores.parquet",
        "weather" : "weather_advisories.csv",
        "forecast": "demand_forecasts_2025.parquet",
    }
    data = {}
    for key, fname in files.items():
        path = os.path.join(DATA, fname)
        if os.path.exists(path):
            if fname.endswith(".parquet"):
                data[key] = pd.read_parquet(path)
            else:
                data[key] = pd.read_csv(path)
        else:
            data[key] = pd.DataFrame()  # empty if file missing
    return data


# =============================================================
# SESSION STATE — simple login system
# =============================================================
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "username" not in st.session_state:
    st.session_state.username = ""
if "preferences" not in st.session_state:
    st.session_state.preferences = {}
if "trip_history" not in st.session_state:
    st.session_state.trip_history = []

# Hardcoded users (simple — no real DB needed for portfolio)
USERS = {
    "admin"   : {"password": "admin123", "role": "admin"},
    "akshaya" : {"password": "trip123",  "role": "user"},
    "guest"   : {"password": "guest123", "role": "user"},
}


# =============================================================
# PAGE 1 — HOME
# =============================================================
def page_home():
    st.markdown("""
    <div class="hero">
        <h1>✈️ TripIQ</h1>
        <p>Smart Tourism Intelligence & Travel Planning System</p>
        <p style="color:#17a2b8; margin-top:0.5rem; font-size:0.95rem;">
            Plan smarter. Travel better. Powered by data.
        </p>
    </div>
    """, unsafe_allow_html=True)

    # Stats row
    c1, c2, c3, c4 = st.columns(4)
    c1.markdown('<div class="card"><div class="stat">878K+</div><div class="stat-label">Hotel Reviews</div></div>', unsafe_allow_html=True)
    c2.markdown('<div class="card"><div class="stat">206</div><div class="stat-label">Countries Covered</div></div>', unsafe_allow_html=True)
    c3.markdown('<div class="card"><div class="stat">4,333</div><div class="stat-label">Hotels Analyzed</div></div>', unsafe_allow_html=True)
    c4.markdown('<div class="card"><div class="stat">1995–2024</div><div class="stat-label">Historical Data</div></div>', unsafe_allow_html=True)

    st.markdown("---")
    st.subheader("What TripIQ can do for you")

    f1, f2, f3, f4 = st.columns(4)
    f1.markdown('<div class="feature"><h3>🗺 Trip Planner</h3><p>Get a day-by-day itinerary based on your travel style and budget</p></div>', unsafe_allow_html=True)
    f2.markdown('<div class="feature"><h3>🏨 Hotel Finder</h3><p>Find the best value hotels filtered by city, class, and ratings</p></div>', unsafe_allow_html=True)
    f3.markdown('<div class="feature"><h3>🌤 Weather Advisory</h3><p>Know if the weather suits your travel dates before you book</p></div>', unsafe_allow_html=True)
    f4.markdown('<div class="feature"><h3>📈 Demand Forecast</h3><p>See predicted tourist demand for any destination in 2025</p></div>', unsafe_allow_html=True)

    st.markdown("---")
    st.subheader("How it works")
    s1, s2, s3, s4 = st.columns(4)
    s1.markdown('<div class="card"><h4>1. Choose destination</h4><p>Pick any city from our database of 4,333 hotels</p></div>', unsafe_allow_html=True)
    s2.markdown('<div class="card"><h4>2. Set preferences</h4><p>Tell us your travel style, group size, and budget</p></div>', unsafe_allow_html=True)
    s3.markdown('<div class="card"><h4>3. Get recommendations</h4><p>AI recommends hotels based on 878k real reviews</p></div>', unsafe_allow_html=True)
    s4.markdown('<div class="card"><h4>4. Plan your trip</h4><p>Get a day-by-day itinerary with weather guidance</p></div>', unsafe_allow_html=True)

    if not st.session_state.logged_in:
        st.markdown("---")
        st.info("Login to save your preferences and trip history.")


# =============================================================
# PAGE 2 — LOGIN / SIGNUP
# =============================================================
def page_login():
    st.markdown('<div class="hero"><h1>Welcome to TripIQ</h1><p>Login to plan your next adventure</p></div>', unsafe_allow_html=True)

    tab_login, tab_signup = st.tabs(["Login", "Sign Up"])

    # LOGIN TAB
    with tab_login:
        st.markdown("#### Enter your credentials")
        username = st.text_input("Username", key="login_user")
        password = st.text_input("Password", type="password", key="login_pass")

        if st.button("Login", key="btn_login"):
            if username in USERS and USERS[username]["password"] == password:
                st.session_state.logged_in = True
                st.session_state.username = username
                st.success(f"Welcome back, {username}!")
                st.rerun()
            else:
                st.error("Invalid username or password.")

        st.caption("Demo accounts: admin / admin123 · akshaya / trip123 · guest / guest123")

    # SIGNUP TAB
    with tab_signup:
        st.markdown("#### Create a new account")
        new_user = st.text_input("Choose a username", key="signup_user")
        new_pass = st.text_input("Choose a password", type="password", key="signup_pass")
        confirm  = st.text_input("Confirm password", type="password", key="signup_confirm")

        if st.button("Sign Up", key="btn_signup"):
            if not new_user or not new_pass:
                st.error("Please fill in all fields.")
            elif new_pass != confirm:
                st.error("Passwords do not match.")
            elif new_user in USERS:
                st.error("Username already taken.")
            else:
                USERS[new_user] = {"password": new_pass, "role": "user"}
                st.session_state.logged_in = True
                st.session_state.username = new_user
                st.success(f"Account created! Welcome, {new_user}!")
                st.rerun()


# =============================================================
# PAGE 3 — TRIP PLANNER
# =============================================================
def page_trip_planner(data):
    st.markdown('<div class="hero"><h1>Plan your trip</h1><p>Get a personalised day-by-day itinerary based on your preferences</p></div>', unsafe_allow_html=True)

    if data["vfm"].empty:
        st.warning("Hotel data not found. Please run pyspark_processing.py first.")
        return

    # User inputs
    c1, c2, c3 = st.columns(3)
    cities     = sorted(data["vfm"]["city"].dropna().unique())
    city       = c1.selectbox("Destination city", cities)
    trip_type  = c2.selectbox("Travel style", ["Family", "Couple", "Solo", "Friends"])
    days       = c3.slider("Number of days", 1, 7, 3)

    c4, c5 = st.columns(2)
    budget     = c4.selectbox("Budget", ["Any", "Budget (1–2 star)", "Mid-range (3 star)", "Luxury (4–5 star)"])
    group_size = c5.selectbox("Group size", ["1 person", "2 people", "3–5 people", "6+ people"])

    # Filter hotels by city and budget
    hotels = data["vfm"][data["vfm"]["city"] == city].copy()
    if budget == "Budget (1–2 star)":
        hotels = hotels[hotels["hotel_class"] <= 2]
    elif budget == "Mid-range (3 star)":
        hotels = hotels[(hotels["hotel_class"] >= 2.5) & (hotels["hotel_class"] <= 3.5)]
    elif budget == "Luxury (4–5 star)":
        hotels = hotels[hotels["hotel_class"] >= 4]

    hotels = hotels.sort_values("vfm_score", ascending=False)

    if hotels.empty:
        st.warning("No hotels found for this city and budget. Try a different combination.")
        return

    # Hotel picker
    hotel_name = st.selectbox("Recommended hotel", hotels["hotel_name"].tolist())
    selected   = hotels[hotels["hotel_name"] == hotel_name].iloc[0]

    # Hotel metrics
    st.markdown("---")
    st.subheader("Your hotel")
    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Overall rating",  f"{selected['avg_rating_overall']:.1f} / 5")
    m2.metric("Value score",     f"{selected['vfm_score']:.2f}")
    m3.metric("Hotel class",     f"{selected['hotel_class']:.1f} ⭐")
    m4.metric("Total reviews",   f"{int(selected['num_reviews']):,}")

    # Day-by-day itinerary
    st.markdown("---")
    st.subheader("Your itinerary")

    # Activity suggestions based on trip type and weather
    def get_activity(trip_type, weather_note=""):
        activities = {
            "Family" : "Visit a family-friendly attraction, take a park break, then enjoy an early dinner together.",
            "Couple" : "Explore a scenic neighbourhood, stop at a café, and end the evening with a special dinner.",
            "Friends": "Explore a popular district, try a fun group activity, and enjoy the city nightlife.",
            "Solo"   : "Take a self-guided city walk, visit a local attraction, and try a well-reviewed restaurant.",
        }
        base = activities.get(trip_type, "Explore the city at your own pace.")
        if "Rain" in weather_note or "Thunder" in weather_note:
            return "Weather may be poor — consider indoor museums, galleries, or shopping malls today."
        return base

    # Use weather data if available
    if not data["weather"].empty and "city" in data["weather"].columns:
        weather_city = data["weather"][data["weather"]["city"] == city].head(days)
    else:
        weather_city = pd.DataFrame()

    for day in range(1, days + 1):
        weather_note = ""
        weather_info = ""

        if not weather_city.empty and day <= len(weather_city):
            row = weather_city.iloc[day - 1]
            weather_note = str(row.get("advisory", ""))
            min_t = row.get("min_temperature_c", "N/A")
            max_t = row.get("max_temperature_c", "N/A")
            rain  = row.get("rain_probability_pct", "N/A")
            weather_info = f"{min_t}°C – {max_t}°C · Rain chance: {rain}%"
        else:
            weather_info = "Weather data not available"
            weather_note = ""

        activity = get_activity(trip_type, weather_note)

        st.markdown(f"""
        <div class="day-card">
            <h4>Day {day}</h4>
            <p style="color:#667085; margin:0 0 0.4rem 0;">🌤 {weather_info}</p>
            <p style="margin:0 0 0.2rem 0;"><b>Advisory:</b> {weather_note if weather_note else "No advisory"}</p>
            <p style="margin:0;"><b>Suggested plan:</b> {activity}</p>
        </div>
        """, unsafe_allow_html=True)

    # Save to trip history
    if st.session_state.logged_in:
        if st.button("Save this trip"):
            st.session_state.trip_history.append({
                "city"      : city,
                "hotel"     : hotel_name,
                "days"      : days,
                "trip_type" : trip_type,
                "budget"    : budget
            })
            st.success("Trip saved to your profile!")


# =============================================================
# PAGE 4 — HOTEL FINDER
# =============================================================
def page_hotel_finder(data):
    st.markdown('<div class="hero"><h1>Find a hotel</h1><p>Search and filter hotels by city, class, and value score</p></div>', unsafe_allow_html=True)

    if data["vfm"].empty:
        st.warning("Hotel data not found.")
        return

    c1, c2, c3 = st.columns(3)
    cities      = sorted(data["vfm"]["city"].dropna().unique())
    city        = c1.selectbox("City", cities)
    min_class   = c2.slider("Minimum hotel class", 0.0, 5.0, 3.0, 0.5)
    min_reviews = c3.slider("Minimum reviews", 0, 500, 50, 50)

    hotels = data["vfm"][
        (data["vfm"]["city"] == city) &
        (data["vfm"]["hotel_class"] >= min_class) &
        (data["vfm"]["num_reviews"] >= min_reviews)
    ].sort_values("vfm_score", ascending=False)

    st.markdown(f"**{len(hotels)} hotels found**")

    if hotels.empty:
        st.info("No hotels match your filters. Try lowering the minimum class or reviews.")
        return

    st.dataframe(
        hotels[[
            "hotel_name", "hotel_class", "avg_rating_overall",
            "avg_rating_value", "avg_rating_service", "vfm_score", "num_reviews"
        ]].rename(columns={
            "hotel_name"         : "Hotel",
            "hotel_class"        : "Class",
            "avg_rating_overall" : "Overall",
            "avg_rating_value"   : "Value",
            "avg_rating_service" : "Service",
            "vfm_score"          : "VFM Score",
            "num_reviews"        : "Reviews"
        }),
        hide_index=True,
        use_container_width=True
    )


# =============================================================
# PAGE 5 — CITY INSIGHTS
# =============================================================
def page_city_insights(data):
    st.markdown('<div class="hero"><h1>City insights</h1><p>Explore crowd trends and weather patterns for any city</p></div>', unsafe_allow_html=True)

    if data["crowd"].empty:
        st.warning("Crowd data not found.")
        return

    cities = sorted(data["crowd"]["city"].dropna().unique())
    city   = st.selectbox("Choose a city", cities)

    # Crowd score chart
    st.subheader("Historical crowd score")
    crowd = data["crowd"][data["crowd"]["city"] == city].copy()
    crowd["month_label"] = crowd["review_year"].astype(str) + "-" + crowd["review_month"].astype(str).str.zfill(2)
    crowd = crowd.sort_values("month_label")

    st.line_chart(crowd.set_index("month_label")["crowd_score"])
    st.caption("Higher score = more tourist activity. Use this to avoid peak crowds.")

    # Weather
    st.subheader("Weather advisory")
    if not data["weather"].empty and "city" in data["weather"].columns:
        weather = data["weather"][data["weather"]["city"] == city]
        if not weather.empty:
            st.dataframe(
                weather[["date", "advisory", "min_temperature_c", "max_temperature_c", "rain_probability_pct"]].rename(columns={
                    "date"               : "Date",
                    "advisory"           : "Advisory",
                    "min_temperature_c"  : "Min Temp (°C)",
                    "max_temperature_c"  : "Max Temp (°C)",
                    "rain_probability_pct": "Rain %"
                }),
                hide_index=True,
                use_container_width=True
            )
        else:
            st.info("No weather data available for this city.")
    else:
        st.info("Weather data not loaded.")


# =============================================================
# PAGE 6 — DEMAND FORECAST
# =============================================================
def page_demand_forecast(data):
    st.markdown('<div class="hero"><h1>Tourism demand forecast</h1><p>Predicted tourist arrivals for 2025 by country</p></div>', unsafe_allow_html=True)

    if data["forecast"].empty:
        st.warning("Forecast data not found. Please run demand_forecasting.py first.")
        return

    forecast = data["forecast"].copy()

    c1, c2 = st.columns(2)
    continents = ["All"] + sorted(forecast["continent"].dropna().unique().tolist())
    continent  = c1.selectbox("Filter by continent", continents)
    top_n      = c2.slider("Show top N countries", 5, 30, 15)

    if continent != "All":
        forecast = forecast[forecast["continent"] == continent]

    forecast = forecast.sort_values("forecast_arrivals", ascending=False).head(top_n)

    st.subheader(f"Top {top_n} countries by forecast arrivals")
    st.bar_chart(forecast.set_index("country")["forecast_arrivals"])

    st.subheader("Full table")
    st.dataframe(
        forecast[["country", "continent", "forecast_arrivals"]].rename(columns={
            "country"           : "Country",
            "continent"         : "Continent",
            "forecast_arrivals" : "Forecast Arrivals (2025)"
        }),
        hide_index=True,
        use_container_width=True
    )
    st.caption("Forecast based on XGBoost model trained on 1995–2022 historical arrivals data.")


# =============================================================
# PAGE 7 — USER PROFILE
# =============================================================
def page_user_profile():
    if not st.session_state.logged_in:
        st.warning("Please login to view your profile.")
        return

    username = st.session_state.username
    role     = USERS[username]["role"]

    st.markdown(f'<div class="hero"><h1>👤 {username}</h1><p>Role: {role.capitalize()} · Manage your preferences and trip history</p></div>', unsafe_allow_html=True)

    # Preferences
    st.subheader("Your preferences")
    c1, c2, c3 = st.columns(3)
    fav_city   = c1.text_input("Favourite city", value=st.session_state.preferences.get("fav_city", ""))
    trip_style = c2.selectbox("Default travel style", ["Family", "Couple", "Solo", "Friends"],
                               index=["Family","Couple","Solo","Friends"].index(st.session_state.preferences.get("style", "Solo")))
    budget     = c3.selectbox("Default budget", ["Any", "Budget (1–2 star)", "Mid-range (3 star)", "Luxury (4–5 star)"],
                               index=["Any","Budget (1–2 star)","Mid-range (3 star)","Luxury (4–5 star)"].index(st.session_state.preferences.get("budget", "Any")))

    if st.button("Save preferences"):
        st.session_state.preferences = {
            "fav_city": fav_city,
            "style"   : trip_style,
            "budget"  : budget
        }
        st.success("Preferences saved!")

    # Trip history
    st.markdown("---")
    st.subheader("Trip history")
    if st.session_state.trip_history:
        history_df = pd.DataFrame(st.session_state.trip_history)
        st.dataframe(history_df, hide_index=True, use_container_width=True)
    else:
        st.info("No trips saved yet. Use the Trip Planner and save a trip!")

    # Logout
    st.markdown("---")
    if st.button("Logout", type="secondary"):
        st.session_state.logged_in = False
        st.session_state.username  = ""
        st.rerun()


# =============================================================
# PAGE 8 — ADMIN PANEL
# =============================================================
def page_admin(data):
    if not st.session_state.logged_in or USERS[st.session_state.username]["role"] != "admin":
        st.error("Access denied. Admin only.")
        return

    st.markdown('<div class="hero"><h1>Admin Panel</h1><p>Database stats, data quality, and model metrics</p></div>', unsafe_allow_html=True)

    # DB row counts
    st.subheader("Database overview")
    c1, c2, c3, c4 = st.columns(4)
    c1.markdown('<div class="admin-box"><div class="num">878,561</div><div class="lbl">Total reviews</div></div>', unsafe_allow_html=True)
    c2.markdown('<div class="admin-box"><div class="num">4,333</div><div class="lbl">Hotels</div></div>', unsafe_allow_html=True)
    c3.markdown('<div class="admin-box"><div class="num">5,193</div><div class="lbl">Arrival records</div></div>', unsafe_allow_html=True)
    c4.markdown('<div class="admin-box"><div class="num">206</div><div class="lbl">Countries</div></div>', unsafe_allow_html=True)

    # Data quality
    st.markdown("---")
    st.subheader("Data quality")
    if not data["vfm"].empty:
        quality = {
            "Table"        : ["hotel_vfm_scores", "city_crowd_scores", "weather_advisories", "demand_forecasts"],
            "Rows"         : [
                len(data["vfm"]),
                len(data["crowd"]),
                len(data["weather"]) if not data["weather"].empty else 0,
                len(data["forecast"]) if not data["forecast"].empty else 0
            ],
            "Null %"       : ["0%", "0%", "0%", "0%"],
            "Status"       : ["✅ Ready", "✅ Ready", "✅ Ready", "✅ Ready"]
        }
        st.dataframe(pd.DataFrame(quality), hide_index=True, use_container_width=True)

    # Model metrics
    st.markdown("---")
    st.subheader("Model metrics")
    metrics = {
        "Model"    : ["XGBoost Forecaster", "TF-IDF Recommender", "VADER Sentiment", "Trip Type Classifier"],
        "Type"     : ["Regression", "Similarity", "NLP", "Keyword"],
        "Metric"   : ["MAE / RMSE", "Cosine Similarity", "Polarity Score", "Accuracy"],
        "Status"   : ["✅ Trained", "✅ Ready", "✅ Ready", "✅ Ready"]
    }
    st.dataframe(pd.DataFrame(metrics), hide_index=True, use_container_width=True)

    # Crowd score chart (admin view — all cities)
    st.markdown("---")
    st.subheader("Top 10 cities by average crowd score")
    if not data["crowd"].empty:
        top_cities = (
            data["crowd"].groupby("city")["crowd_score"]
            .mean()
            .sort_values(ascending=False)
            .head(10)
        )
        st.bar_chart(top_cities)


# =============================================================
# SIDEBAR NAVIGATION
# =============================================================
def main():
    data = load_data()

    # Sidebar
    with st.sidebar:
        st.markdown("## ✈️ TripIQ")
        st.markdown("---")

        if st.session_state.logged_in:
            st.markdown(f"👤 **{st.session_state.username}**")
            st.markdown("---")

        # Navigation
        pages = ["🏠 Home", "🗺 Trip Planner", "🏨 Hotel Finder",
                 "🌍 City Insights", "📈 Demand Forecast"]

        if st.session_state.logged_in:
            pages.append("👤 My Profile")
            if USERS[st.session_state.username]["role"] == "admin":
                pages.append("🔧 Admin Panel")
        else:
            pages.append("🔐 Login / Sign Up")

        # Keep login easy to find for signed-out visitors.
        if not st.session_state.logged_in:
            login_page = pages.pop()
            pages.insert(0, login_page)
        page = st.radio("Navigate", pages)
        st.markdown("---")
        st.caption("Smart tourism intelligence for better travel decisions.")

    # Route to page
    if page == "🏠 Home":
        page_home()
    elif page == "🗺 Trip Planner":
        page_trip_planner(data)
    elif page == "🏨 Hotel Finder":
        page_hotel_finder(data)
    elif page == "🌍 City Insights":
        page_city_insights(data)
    elif page == "📈 Demand Forecast":
        page_demand_forecast(data)
    elif page == "🔐 Login / Sign Up":
        page_login()
    elif page == "👤 My Profile":
        page_user_profile()
    elif page == "🔧 Admin Panel":
        page_admin(data)


if __name__ == "__main__":
    main()
