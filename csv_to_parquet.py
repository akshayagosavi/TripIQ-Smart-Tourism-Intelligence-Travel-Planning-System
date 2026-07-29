import pandas as pd
import pyarrow as pa
import pyarrow.parquet as pq
import os

csv_file = "data_processed/fact_reviews.csv"
parquet_file = "data_processed/fact_reviews.parquet"

chunksize = 100000

writer = None

print("Converting CSV to Parquet...")

for i, chunk in enumerate(pd.read_csv(csv_file, chunksize=chunksize)):
    table = pa.Table.from_pandas(chunk)

    if writer is None:
        writer = pq.ParquetWriter(parquet_file, table.schema)

    writer.write_table(table)
    print(f"Processed chunk {i+1}")

if writer:
    writer.close()

csv_size = os.path.getsize(csv_file) / (1024 * 1024)
parquet_size = os.path.getsize(parquet_file) / (1024 * 1024)

print("\nDone!")
print(f"CSV Size      : {csv_size:.2f} MB")
print(f"Parquet Size  : {parquet_size:.2f} MB")
print(f"Space Saved   : {csv_size - parquet_size:.2f} MB")