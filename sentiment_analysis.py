"""Score TripAdvisor review sentiment with VADER."""

import os
import time
from multiprocessing import Pool

import pandas as pd
from nltk.sentiment import SentimentIntensityAnalyzer


BASE = os.path.dirname(os.path.abspath(__file__))
PROCESSED = os.path.join(BASE, "data_processed")
INPUT_FILE = os.path.join(PROCESSED, "fact_reviews_with_trip_type.parquet")
REVIEW_OUTPUT = os.path.join(PROCESSED, "fact_reviews_with_sentiment.parquet")
HOTEL_OUTPUT = os.path.join(PROCESSED, "agg_hotel_sentiment.parquet")
WORKERS = 4


def start_analyzer():
    """Create one VADER analyzer inside each worker process."""
    global analyzer
    analyzer = SentimentIntensityAnalyzer()


def get_sentiment_score(text):
    """Return VADER's compound score for one review."""
    return analyzer.polarity_scores(text)["compound"]


def get_sentiment_label(score):
    """Turn VADER's compound score into a simple category."""
    if score >= 0.05:
        return "positive"
    if score <= -0.05:
        return "negative"
    return "neutral"


def main():
    print("Loading reviews...")
    start = time.time()
    reviews = pd.read_parquet(INPUT_FILE)
    print(f"Loaded {len(reviews):,} reviews in {time.time() - start:.1f}s")

    print("Calculating VADER sentiment...")
    start = time.time()

    # Score the first 1,000 characters. This keeps long reviews fast to process
    # while still capturing the reviewer's main opening opinion.
    review_text = reviews["text"].fillna("").str[:1000]

    # The compound score ranges from -1 (very negative) to +1 (very positive).
    # Four workers score different reviews at the same time.
    with Pool(WORKERS, initializer=start_analyzer) as pool:
        reviews["sentiment_score"] = pool.map(get_sentiment_score, review_text, chunksize=1000)
    reviews["sentiment_label"] = reviews["sentiment_score"].apply(get_sentiment_label)
    print(f"Sentiment scoring finished in {time.time() - start:.1f}s")

    print("Saving review-level sentiment...")
    reviews.to_parquet(REVIEW_OUTPUT, index=False)

    print("Building hotel-level sentiment summary...")
    hotel_summary = reviews.groupby("hotel_id").agg(
        average_sentiment=("sentiment_score", "mean"),
        review_count=("review_id", "count"),
    ).reset_index()

    sentiment_counts = pd.crosstab(
        reviews["hotel_id"], reviews["sentiment_label"]
    ).reset_index()

    # Ensure every sentiment column exists, even if a hotel has zero reviews of one type.
    for label in ["positive", "neutral", "negative"]:
        if label not in sentiment_counts.columns:
            sentiment_counts[label] = 0

    hotel_summary = hotel_summary.merge(sentiment_counts, on="hotel_id")
    hotel_summary = hotel_summary.rename(columns={
        "positive": "positive_reviews",
        "neutral": "neutral_reviews",
        "negative": "negative_reviews",
    })
    hotel_summary["average_sentiment"] = hotel_summary["average_sentiment"].round(3)
    hotel_summary.to_parquet(HOTEL_OUTPUT, index=False)

    print("\nSentiment distribution:")
    print(reviews["sentiment_label"].value_counts().to_string())
    print(f"\nSaved review-level file: {REVIEW_OUTPUT}")
    print(f"Saved hotel summary: {HOTEL_OUTPUT}")


if __name__ == "__main__":
    main()
