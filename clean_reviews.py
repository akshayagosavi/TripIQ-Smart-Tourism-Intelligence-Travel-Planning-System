"""
clean_reviews.py
Rebuilds data_processed/fact_reviews.csv from data_raw/reviews.csv,
matching the fact_reviews table schema in Postgres:

review_id, hotel_id, title, text, date_stayed, num_helpful_votes, date,
via_mobile, review_year, review_month, review_quarter,
rating_overall, rating_service, rating_cleanliness, rating_value,
rating_location, rating_sleep, rating_rooms
"""

import ast
import pandas as pd

INPUT_CSV = "data_raw/reviews.csv"
OUTPUT_CSV = "data_processed/fact_reviews.csv"
CHUNKSIZE = 100_000

RATING_KEY_MAP = {
    "overall": "rating_overall",
    "service": "rating_service",
    "cleanliness": "rating_cleanliness",
    "value": "rating_value",
    "location": "rating_location",
    "sleep_quality": "rating_sleep",
    "rooms": "rating_rooms",
}


def parse_ratings(raw_value):
    """Safely parse the stringified ratings dict into a real dict."""
    if pd.isna(raw_value):
        return {}
    try:
        return ast.literal_eval(raw_value)
    except (ValueError, SyntaxError):
        return {}


def parse_date_stayed(value):
    """Convert strings like 'December 2012' into a date (first of month)."""
    if pd.isna(value):
        return pd.NaT
    try:
        return pd.to_datetime(value, format="%B %Y", errors="coerce")
    except Exception:
        return pd.NaT


def clean_chunk(chunk: pd.DataFrame) -> pd.DataFrame:
    # Rename simple columns
    chunk = chunk.rename(columns={"id": "review_id", "offering_id": "hotel_id"})

    # Expand ratings dict into separate columns
    parsed_ratings = chunk["ratings"].apply(parse_ratings)
    for raw_key, target_col in RATING_KEY_MAP.items():
        chunk[target_col] = parsed_ratings.apply(lambda d: d.get(raw_key))

    # Parse dates
    chunk["date"] = pd.to_datetime(chunk["date"], errors="coerce")
    chunk["date_stayed"] = chunk["date_stayed"].apply(parse_date_stayed)

    # Derived date parts (from review 'date', not date_stayed)
    chunk["review_year"] = chunk["date"].dt.year
    chunk["review_month"] = chunk["date"].dt.month
    chunk["review_quarter"] = chunk["date"].dt.quarter

    # Ensure via_mobile is boolean
    chunk["via_mobile"] = chunk["via_mobile"].astype(bool)

    # Final column order matching Postgres schema
    final_cols = [
        "review_id", "hotel_id", "title", "text", "date_stayed",
        "num_helpful_votes", "date", "via_mobile",
        "review_year", "review_month", "review_quarter",
        "rating_overall", "rating_service", "rating_cleanliness",
        "rating_value", "rating_location", "rating_sleep", "rating_rooms",
    ]
    return chunk[final_cols]


def main():
    print("Cleaning reviews.csv -> fact_reviews.csv ...")
    first_chunk = True
    total_rows = 0

    for i, chunk in enumerate(pd.read_csv(INPUT_CSV, chunksize=CHUNKSIZE)):
        cleaned = clean_chunk(chunk)
        cleaned.to_csv(
            OUTPUT_CSV,
            mode="w" if first_chunk else "a",
            header=first_chunk,
            index=False,
        )
        first_chunk = False
        total_rows += len(cleaned)
        print(f"  chunk {i + 1}: {total_rows:,} rows written so far")

    print(f"Done. Wrote {total_rows:,} rows to {OUTPUT_CSV}")


if __name__ == "__main__":
    main()
