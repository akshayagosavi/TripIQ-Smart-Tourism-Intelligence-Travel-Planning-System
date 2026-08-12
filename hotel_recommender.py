"""Create content-based hotel recommendations with TF-IDF."""

import os

import numpy as np
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity


BASE = os.path.dirname(os.path.abspath(__file__))
PROCESSED = os.path.join(BASE, "data_processed")
HOTELS_FILE = os.path.join(PROCESSED, "dim_hotels.csv")
REVIEWS_FILE = os.path.join(PROCESSED, "fact_reviews.parquet")
OUTPUT_FILE = os.path.join(PROCESSED, "hotel_recommendations.parquet")
TOP_RECOMMENDATIONS = 5


def build_hotel_profiles(hotels, reviews):
    """Combine each hotel's basic details and review titles into one text profile."""
    review_titles = reviews[["hotel_id", "title"]].dropna()
    review_titles = review_titles.groupby("hotel_id")["title"].agg(" ".join).reset_index()
    review_titles = review_titles.rename(columns={"hotel_id": "offering_id", "title": "review_titles"})

    hotels = hotels.merge(review_titles, on="offering_id", how="left")
    hotels["review_titles"] = hotels["review_titles"].fillna("")

    # This is the text TF-IDF uses to compare hotels.
    hotels["profile"] = (
        hotels["hotel_name"].fillna("") + " " +
        hotels["city"].fillna("") + " " +
        hotels["state"].fillna("") + " " +
        hotels["hotel_class"].fillna(0).astype(str) + " star " +
        hotels["review_titles"]
    )
    return hotels


def main():
    print("Loading hotels and review titles...")
    hotels = pd.read_csv(HOTELS_FILE)
    reviews = pd.read_parquet(REVIEWS_FILE, columns=["hotel_id", "title"])

    print("Building hotel profiles...")
    hotels = build_hotel_profiles(hotels, reviews)

    print("Creating TF-IDF features...")
    vectorizer = TfidfVectorizer(stop_words="english", max_features=10000)
    tfidf_matrix = vectorizer.fit_transform(hotels["profile"])

    print("Finding similar hotels...")
    recommendation_rows = []
    for hotel_index in range(len(hotels)):
        similarity_scores = cosine_similarity(
            tfidf_matrix[hotel_index], tfidf_matrix
        ).flatten()

        # Sort from most similar to least similar and skip the hotel itself.
        similar_indexes = np.argsort(similarity_scores)[::-1]
        similar_indexes = [index for index in similar_indexes if index != hotel_index]

        for rank, similar_index in enumerate(similar_indexes[:TOP_RECOMMENDATIONS], start=1):
            recommendation_rows.append({
                "hotel_id": hotels.iloc[hotel_index]["offering_id"],
                "hotel_name": hotels.iloc[hotel_index]["hotel_name"],
                "city": hotels.iloc[hotel_index]["city"],
                "recommended_hotel_id": hotels.iloc[similar_index]["offering_id"],
                "recommended_hotel_name": hotels.iloc[similar_index]["hotel_name"],
                "recommended_city": hotels.iloc[similar_index]["city"],
                "similarity_score": round(float(similarity_scores[similar_index]), 3),
                "rank": rank,
            })

    recommendations = pd.DataFrame(recommendation_rows)
    recommendations.to_parquet(OUTPUT_FILE, index=False)
    print(f"Saved {len(recommendations):,} recommendations to {OUTPUT_FILE}")


if __name__ == "__main__":
    main()
