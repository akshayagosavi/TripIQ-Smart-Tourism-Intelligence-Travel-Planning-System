"""
pyspark_processing.py
Two aggregations, run in local PySpark (capped at 2GB driver memory):

1. hotel_vfm_scores      -> Value-for-Money score per hotel
2. city_monthly_crowd    -> Review-volume-based crowd score per city per month

Outputs written as parquet to data_processed/.
"""

from pyspark.sql import SparkSession
from pyspark.sql import functions as F
from pyspark.sql.window import Window

DATA_DIR = "data_processed"


def get_spark():
    return (
        SparkSession.builder
        .appName("smart_tourism_aggregations")
        .master("local[*]")
        .config("spark.driver.memory", "2g")
        .config("spark.sql.shuffle.partitions", "8")  # small for local mode
        .getOrCreate()
    )


def build_vfm_scores(spark):
    reviews = spark.read.parquet(f"{DATA_DIR}/fact_reviews.parquet")
    hotels = spark.read.csv(f"{DATA_DIR}/dim_hotels.csv", header=True, inferSchema=True)

    # Per-hotel review aggregates
    hotel_agg = reviews.groupBy("hotel_id").agg(
        F.count("review_id").alias("num_reviews"),
        F.avg("rating_overall").alias("avg_rating_overall"),
        F.avg("rating_value").alias("avg_rating_value"),
        F.avg("rating_service").alias("avg_rating_service"),
        F.avg("rating_cleanliness").alias("avg_rating_cleanliness"),
        F.avg("rating_location").alias("avg_rating_location"),
    )

    # Join to hotel dimension (offering_id is the hotel key)
    joined = hotel_agg.join(
        hotels.select(
            F.col("offering_id").alias("hotel_id"),
            "hotel_name", "city", "state", "hotel_class",
        ),
        on="hotel_id",
        how="left",
    )

    # VFM score: rating quality relative to price tier (hotel_class as proxy)
    # Guard against hotel_class being null or 0
    result = joined.withColumn(
        "vfm_score",
        F.when(
            (F.col("hotel_class").isNotNull()) & (F.col("hotel_class") > 0),
            F.col("avg_rating_value") / F.col("hotel_class"),
        ).otherwise(None),
    )

    # Only keep hotels with a reasonable sample size (avoid 1-review outliers dominating)
    result = result.filter(F.col("num_reviews") >= 5)

    out_path = f"{DATA_DIR}/hotel_vfm_scores.parquet"
    result.write.mode("overwrite").parquet(out_path)
    print(f"Wrote hotel VFM scores -> {out_path}  ({result.count():,} hotels)")
    return result


def build_crowd_scores(spark):
    reviews = spark.read.parquet(f"{DATA_DIR}/fact_reviews.parquet")
    hotels = spark.read.csv(f"{DATA_DIR}/dim_hotels.csv", header=True, inferSchema=True)

    reviews_with_city = reviews.join(
        hotels.select(F.col("offering_id").alias("hotel_id"), "city", "hotel_country"),
        on="hotel_id",
        how="left",
    )

    # Review volume per city per year-month as a proxy for footfall/crowding
    monthly = reviews_with_city.filter(
        F.col("city").isNotNull() & F.col("review_year").isNotNull() & F.col("review_month").isNotNull()
    ).groupBy("city", "hotel_country", "review_year", "review_month").agg(
        F.count("review_id").alias("review_count")
    )

    # Normalize review_count into a 0-100 crowd_score, scaled within each city
    # (so it reflects relative busy/quiet months for that city, not raw volume across cities)
    window = Window.partitionBy("city")
    monthly = monthly.withColumn("city_min", F.min("review_count").over(window))
    monthly = monthly.withColumn("city_max", F.max("review_count").over(window))

    monthly = monthly.withColumn(
        "crowd_score",
        F.when(
            F.col("city_max") > F.col("city_min"),
            (F.col("review_count") - F.col("city_min"))
            / (F.col("city_max") - F.col("city_min")) * 100,
        ).otherwise(F.lit(50.0)),  # flat if no variation
    ).drop("city_min", "city_max")

    out_path = f"{DATA_DIR}/city_monthly_crowd_scores.parquet"
    monthly.write.mode("overwrite").parquet(out_path)
    print(f"Wrote city-monthly crowd scores -> {out_path}  ({monthly.count():,} rows)")
    return monthly


def main():
    spark = get_spark()
    try:
        print("Building hotel VFM scores...")
        vfm = build_vfm_scores(spark)
        vfm.orderBy(F.desc("vfm_score")).show(10, truncate=False)

        print("\nBuilding city-monthly crowd scores...")
        crowd = build_crowd_scores(spark)
        crowd.orderBy(F.desc("crowd_score")).show(10, truncate=False)
    finally:
        spark.stop()


if __name__ == "__main__":
    main()
