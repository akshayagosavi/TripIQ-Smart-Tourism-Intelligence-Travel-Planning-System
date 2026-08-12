"""Forecast 2025 international tourist arrivals with XGBoost."""

import os

import numpy as np
import pandas as pd
from sklearn.metrics import mean_absolute_error, mean_absolute_percentage_error
from xgboost import XGBRegressor


BASE = os.path.dirname(os.path.abspath(__file__))
PROCESSED = os.path.join(BASE, "data_processed")
INPUT_FILE = os.path.join(PROCESSED, "fact_visits.csv")
OUTPUT_FILE = os.path.join(PROCESSED, "demand_forecasts_2025.parquet")
FEATURES = ["year", "arrivals_last_year", "arrivals_two_years_ago", "arrivals_three_years_ago", "recent_growth_rate"]


def add_history_features(visits):
    """Add each country's previous arrival values to every yearly record."""
    visits = visits.sort_values(["country", "year"]).copy()
    country_groups = visits.groupby("country")

    visits["previous_year"] = country_groups["year"].shift(1)
    visits["arrivals_last_year"] = country_groups["arrivals"].shift(1)
    visits["arrivals_two_years_ago"] = country_groups["arrivals"].shift(2)
    visits["arrivals_three_years_ago"] = country_groups["arrivals"].shift(3)
    visits["two_years_ago"] = country_groups["year"].shift(2)
    visits["three_years_ago"] = country_groups["year"].shift(3)

    # Keep only consecutive years so a missing year is never treated as a real value.
    consecutive_years = (
        (visits["year"] - visits["previous_year"] == 1) &
        (visits["year"] - visits["two_years_ago"] == 2) &
        (visits["year"] - visits["three_years_ago"] == 3)
    )
    visits = visits[consecutive_years].copy()

    visits["recent_growth_rate"] = (
        (visits["arrivals_last_year"] - visits["arrivals_two_years_ago"])
        / visits["arrivals_two_years_ago"]
    )
    return visits.replace([np.inf, -np.inf], np.nan).dropna(subset=FEATURES + ["arrivals"])


def create_model():
    """Return a small XGBoost regression model."""
    return XGBRegressor(
        n_estimators=300,
        max_depth=4,
        learning_rate=0.05,
        subsample=0.8,
        colsample_bytree=0.8,
        objective="reg:squarederror",
        random_state=42,
    )


def main():
    print("Loading historical tourism arrivals...")
    visits = pd.read_csv(INPUT_FILE)
    model_data = add_history_features(visits)
    print(f"Usable country-year records: {len(model_data):,}")

    # Validate using 2023 because the model only learns from earlier years.
    training_data = model_data[model_data["year"] <= 2022]
    validation_data = model_data[model_data["year"] == 2023]

    print("Training and validating the model...")
    model = create_model()
    model.fit(training_data[FEATURES], np.log1p(training_data["arrivals"]))

    validation_predictions = np.expm1(model.predict(validation_data[FEATURES]))
    mae = mean_absolute_error(validation_data["arrivals"], validation_predictions)
    mape = mean_absolute_percentage_error(validation_data["arrivals"], validation_predictions) * 100
    print(f"2023 validation MAE: {mae:,.0f} arrivals")
    print(f"2023 validation MAPE: {mape:.1f}%")

    # Refit with all available records before creating the 2025 forecast.
    print("Training final model and forecasting 2025...")
    model = create_model()
    model.fit(model_data[FEATURES], np.log1p(model_data["arrivals"]))

    latest_data = model_data[model_data["year"] == 2024].copy()
    latest_data["forecast_arrivals"] = np.expm1(model.predict(latest_data[FEATURES]))
    latest_data["forecast_arrivals"] = latest_data["forecast_arrivals"].round().astype(int)
    latest_data["forecast_growth_pct"] = (
        (latest_data["forecast_arrivals"] - latest_data["arrivals"]) / latest_data["arrivals"] * 100
    ).round(1)

    forecasts = latest_data[[
        "country", "iso_code", "continent", "year", "arrivals",
        "forecast_arrivals", "forecast_growth_pct",
    ]].rename(columns={
        "year": "last_actual_year",
        "arrivals": "last_actual_arrivals",
    })
    forecasts.insert(3, "forecast_year", 2025)
    forecasts = forecasts.sort_values("forecast_arrivals", ascending=False)
    forecasts.to_parquet(OUTPUT_FILE, index=False)

    print(f"Saved {len(forecasts)} country forecasts to {OUTPUT_FILE}")
    print("\nTop five forecasted destinations:")
    print(forecasts.head(5).to_string(index=False))


if __name__ == "__main__":
    main()
