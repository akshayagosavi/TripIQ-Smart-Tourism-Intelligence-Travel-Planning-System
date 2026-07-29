# =============================================================
#  Smart Tourism Analytics — ETL Pipeline
#  Loads all 5 CSVs from data_processed/ into PostgreSQL
#  Run: python etl/run_pipeline.py
# =============================================================

import pandas as pd
import psycopg2
from sqlalchemy import create_engine
import os
import time

# =============================================================
# CONFIG — update password if different
# =============================================================
DB_CONFIG = {
    "host"    : "localhost",
    "port"    : 5432,
    "database": "smart_tourism",
    "user"    : "postgres",
    "password": "admin123"
}

BASE = r"C:\Users\aksha\OneDrive\Documents\New folder\Smart Project"
PROCESSED = os.path.join(BASE, "data_processed")

# =============================================================
# CONNECT
# =============================================================
print("Connecting to PostgreSQL...")
engine = create_engine(
    f"postgresql+psycopg2://{DB_CONFIG['user']}:{DB_CONFIG['password']}"
    f"@{DB_CONFIG['host']}:{DB_CONFIG['port']}/{DB_CONFIG['database']}"
)
print("✓ Connected to smart_tourism")

# =============================================================
# HELPER — load CSV and push to Postgres
# =============================================================
def load_table(filename, table_name, chunksize=None):
    path = os.path.join(PROCESSED, filename)
    print(f"\nLoading {filename} → {table_name}...")
    start = time.time()

    if chunksize:
        # chunked load for large files (fact_reviews)
        chunks = pd.read_csv(path, chunksize=chunksize)
        total = 0
        for i, chunk in enumerate(chunks):
            chunk = clean_chunk(chunk, table_name)
            chunk.to_sql(
                table_name, engine,
                if_exists="append" if i > 0 else "append",
                index=False,
                method="multi"
            )
            total += len(chunk)
            print(f"  chunk {i+1}: {total:,} rows loaded...", end="\r")
        print(f"  ✓ {total:,} rows loaded in {time.time()-start:.1f}s")
    else:
        df = pd.read_csv(path)
        df = clean_chunk(df, table_name)
        df.to_sql(table_name, engine, if_exists="append", index=False, method="multi")
        print(f"  ✓ {len(df):,} rows loaded in {time.time()-start:.1f}s")

# =============================================================
# CLEAN CHUNK — fix types before loading
# =============================================================
def clean_chunk(df, table_name):
    # Convert date columns
    if table_name == "fact_reviews":
        for col in ["date", "date_stayed"]:
            if col in df.columns:
                df[col] = pd.to_datetime(df[col], errors="coerce").dt.date

        # Fix boolean
        if "via_mobile" in df.columns:
            df["via_mobile"] = df["via_mobile"].astype(bool)

        # Fix integer columns
        for col in ["review_year", "review_month", "review_quarter", "num_helpful_votes"]:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors="coerce").astype("Int64")

        # Drop rows with null review_id (primary key)
        df = df.dropna(subset=["review_id"])
        df["review_id"] = df["review_id"].astype("int64")

    if table_name == "dim_hotels":
        df = df.dropna(subset=["offering_id"])
        df["offering_id"] = df["offering_id"].astype("int64")

    if table_name == "fact_visits":
        df["arrivals"] = pd.to_numeric(df["arrivals"], errors="coerce")

    return df

# =============================================================
# RUN ETL — order matters (dims before facts)
# =============================================================
print("\n" + "="*55)
print("Starting ETL Pipeline")
print("="*55)

total_start = time.time()

# 1. Dimension tables first (small, fast)
load_table("dim_time.csv",        "dim_time")
load_table("dim_destination.csv", "dim_destination")
load_table("dim_hotels.csv",      "dim_hotels")

# 2. Fact tables (larger)
load_table("fact_visits.csv",  "fact_visits")

# 3. fact_reviews is large — load in chunks of 50k rows
load_table("fact_reviews.csv", "fact_reviews", chunksize=50000)

# =============================================================
# VERIFY — row counts
# =============================================================
print("\n" + "="*55)
print("Verifying row counts in PostgreSQL...")
print("="*55)

tables = ["dim_time", "dim_destination", "dim_hotels", "fact_visits", "fact_reviews"]
with engine.connect() as conn:
    for table in tables:
        result = conn.execute(
            __import__("sqlalchemy").text(f"SELECT COUNT(*) FROM {table}")
        )
        count = result.scalar()
        print(f"  {table:25s} → {count:>8,} rows")

print(f"\n✓ ETL complete in {time.time()-total_start:.1f}s")
print("✓ Database ready. Move to Phase 2 — PySpark.")
