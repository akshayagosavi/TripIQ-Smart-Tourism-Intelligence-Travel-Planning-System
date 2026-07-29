import pandas as pd

files = ["dim_hotels.csv", "dim_destination.csv", "dim_time.csv", "fact_visits.csv"]

for f in files:
    path = f"data_processed/{f}"
    df = pd.read_csv(path, nrows=3)
    print(f"\n--- {f} ---")
    print(df.columns.tolist())
    print(df.head(3))
