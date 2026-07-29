# =============================================================
#  Smart Tourism Analytics — Week 3: Cleaning + Dimension Tables
#  Inputs : international-tourist-trips.csv (OWID)
#           offering.csv + review.csv (TripAdvisor)
#  Outputs: data_processed/
#            dim_destination.csv
#            dim_time.csv
#            fact_visits.csv
#            fact_reviews.csv
# =============================================================
 
import pandas as pd
import ast
import os
import warnings
warnings.filterwarnings("ignore")
 
# install if not already present
os.system("pip install pycountry-convert -q")
from pycountry_convert import country_alpha3_to_country_alpha2, country_alpha2_to_continent_code
 
CONTINENT_NAMES = {
    "AF": "Africa",
    "AS": "Asia",
    "EU": "Europe",
    "NA": "Americas",
    "SA": "Americas",
    "OC": "Oceania",
    "AN": "Antarctica"
}
 
def get_continent(iso3):
    try:
        iso2 = country_alpha3_to_country_alpha2(iso3)
        code = country_alpha2_to_continent_code(iso2)
        return CONTINENT_NAMES.get(code, "Unknown")
    except:
        return "Unknown"
 
# ── paths ─────────────────────────────────────────────────────
BASE     = r"C:\Users\aksha\OneDrive\Documents\New folder\Smart Project"
RAW      = os.path.join(BASE, "data_raw")
OUT      = os.path.join(BASE, "data_processed")
os.makedirs(OUT, exist_ok=True)
 
# =============================================================
# 1. LOAD RAW FILES
# =============================================================
print("Loading raw files...")
 
owid     = pd.read_csv(os.path.join(RAW, "international-tourist-trips.csv"))
offering = pd.read_csv(os.path.join(RAW, "offerings.csv"))
review   = pd.read_csv(os.path.join(RAW, "reviews.csv"))
 
print(f"  OWID     : {owid.shape}")
print(f"  Offering : {offering.shape}")
print(f"  Review   : {review.shape}")
 
 
# =============================================================
# 2. CLEAN OWID → fact_visits
# =============================================================
print("\n── Cleaning OWID (fact_visits)...")
 
# 2.1 Drop rows with missing ISO code (3 small islands)
owid = owid.dropna(subset=["Code"])
print(f"  After dropping null codes : {owid.shape[0]} rows")
 
# 2.2 Rename columns to project standard
owid = owid.rename(columns={
    "Entity"                          : "country",
    "Code"                            : "iso_code",
    "Year"                            : "year",
    "Arrivals of tourists from abroad": "arrivals"
})
 
# 2.3 Add data completeness flag
owid["data_status"] = owid["year"].apply(
    lambda y: "preliminary" if y >= 2023 else "confirmed"
)
 
# 2.4 Add continent mapping using pycountry-convert (automatic, no hardcoding)
print("  Mapping iso_code → continent via pycountry-convert...")
owid["continent"] = owid["iso_code"].apply(get_continent)
 
unknown = owid[owid["continent"] == "Unknown"]["iso_code"].unique()
if len(unknown) > 0:
    print(f"  ⚠ {len(unknown)} iso_codes not mapped to continent: {unknown[:10]}")
else:
    print("  ✓ All iso_codes mapped successfully")
 
fact_visits = owid.copy()
print(f"  fact_visits shape: {fact_visits.shape}")
print(fact_visits.head(3).to_string())
 
 
# =============================================================
# 3. CLEAN OFFERING → base for dim_destination
# =============================================================
print("\n── Cleaning Offering (dim_destination base)...")
 
# 3.1 Parse address dict
def parse_address(addr_str):
    try:
        d = ast.literal_eval(addr_str)
        return pd.Series({
            "city"        : d.get("locality", None),
            "state"       : d.get("region", None),
            "hotel_country": d.get("country-name", None),
            "street"      : d.get("street-address", None)
        })
    except:
        return pd.Series({"city":None,"state":None,"hotel_country":None,"street":None})
 
print("  Parsing address column...")
addr_parsed = offering["address"].apply(parse_address)
offering    = pd.concat([offering.reset_index(drop=True), addr_parsed], axis=1)
 
# 3.2 Drop phone (mostly null) and raw address col
offering = offering.drop(columns=["phone", "address", "url"])
 
# 3.3 Fill missing hotel_class with median
median_class = offering["hotel_class"].median()
offering["hotel_class"] = offering["hotel_class"].fillna(median_class)
print(f"  hotel_class nulls filled with median: {median_class}")
 
# 3.4 Rename id for clarity
offering = offering.rename(columns={"id": "offering_id", "name": "hotel_name"})
 
print(f"  Offering cleaned shape: {offering.shape}")
print(offering.head(3).to_string())
 
 
# =============================================================
# 4. CLEAN REVIEW → fact_reviews
# =============================================================
print("\n── Cleaning Review (fact_reviews)...")
 
# 4.1 Parse ratings dict → expand to columns
# Fast vectorized ratings parsing using json_normalize (~5 sec vs ~60 sec)
import json
 
def safe_json(s):
    try:
        return json.loads(s.replace("'", '"').replace("None", "null"))
    except:
        return {}
 
print("  Parsing ratings column (fast method, ~5-10 sec)...")
ratings_parsed = pd.json_normalize(review["ratings"].apply(safe_json))
 
# Rename to project standard: e.g. "overall" → "rating_overall"
col_rename = {
    "overall"         : "rating_overall",
    "service"         : "rating_service",
    "cleanliness"     : "rating_cleanliness",
    "value"           : "rating_value",
    "location"        : "rating_location",
    "sleep_quality"   : "rating_sleep",
    "rooms"           : "rating_rooms",
    "business_service": "rating_business"
}
ratings_parsed = ratings_parsed.rename(columns=col_rename)
 
# Keep only known rating columns (drop any unexpected ones)
keep_cols = [c for c in col_rename.values() if c in ratings_parsed.columns]
ratings_parsed = ratings_parsed[keep_cols]
 
review = pd.concat([review.reset_index(drop=True), ratings_parsed], axis=1)
print(f"  Ratings columns added: {keep_cols}")
 
# 4.2 Drop raw ratings + author (dict columns, not needed)
review = review.drop(columns=["ratings", "author"])
 
# 4.3 Parse dates
review["date"]        = pd.to_datetime(review["date"], errors="coerce")
review["date_stayed"] = pd.to_datetime(review["date_stayed"], errors="coerce")
 
# 4.4 Extract time features
review["review_year"]  = review["date"].dt.year
review["review_month"] = review["date"].dt.month
review["review_quarter"] = review["date"].dt.quarter
 
# 4.5 Drop rows with no overall rating (can't use in recommender)
before = len(review)
review = review.dropna(subset=["rating_overall"])
print(f"  Dropped {before - len(review)} rows with null overall rating")
 
# 4.6 Rename for clarity
review = review.rename(columns={
    "id"         : "review_id",
    "offering_id": "hotel_id"
})
 
print(f"  fact_reviews shape: {review.shape}")
print(review[["review_id","hotel_id","rating_overall","review_year","review_month"]].head(3).to_string())
 
 
# =============================================================
# 5. BUILD dim_destination
# =============================================================
print("\n── Building dim_destination...")
 
# Combine OWID countries + TripAdvisor hotel cities
# Part A: from OWID (country level)
owid_destinations = fact_visits[["country","iso_code","continent"]].drop_duplicates()
owid_destinations["destination_type"] = "country"
owid_destinations["city"]             = None
owid_destinations["hotel_country"]    = None
 
# Part B: from offering (hotel/city level)
hotel_destinations = offering[["city","state","hotel_country"]].drop_duplicates().dropna(subset=["city"])
hotel_destinations["destination_type"] = "hotel_city"
hotel_destinations["country"]          = hotel_destinations["hotel_country"]
hotel_destinations["iso_code"]         = None
hotel_destinations["continent"]        = None
 
# Assign destination_id
owid_destinations = owid_destinations.reset_index(drop=True)
owid_destinations.insert(0, "destination_id", ["D_C_" + str(i+1).zfill(4) for i in range(len(owid_destinations))])
 
hotel_destinations = hotel_destinations.reset_index(drop=True)
hotel_destinations.insert(0, "destination_id", ["D_H_" + str(i+1).zfill(4) for i in range(len(hotel_destinations))])
 
dim_destination = pd.concat([owid_destinations, hotel_destinations], ignore_index=True)
print(f"  dim_destination shape: {dim_destination.shape}")
print(dim_destination.head(5).to_string())
 
 
# =============================================================
# 6. BUILD dim_time
# =============================================================
print("\n── Building dim_time...")
 
years  = list(range(1995, 2025))
months = list(range(1, 13))
 
dim_time_rows = []
for y in years:
    for m in months:
        dim_time_rows.append({
            "time_id" : f"{y}{str(m).zfill(2)}",
            "year"    : y,
            "month"   : m,
            "quarter" : (m - 1) // 3 + 1,
            "season"  : (
                "Winter" if m in [12,1,2]  else
                "Spring" if m in [3,4,5]   else
                "Summer" if m in [6,7,8]   else
                "Autumn"
            ),
            "is_peak_travel" : 1 if m in [6,7,8,12] else 0
        })
 
dim_time = pd.DataFrame(dim_time_rows)
print(f"  dim_time shape: {dim_time.shape}")
print(dim_time.head(5).to_string())
 
 
# =============================================================
# 7. SAVE ALL TO data_processed/
# =============================================================
print("\n── Saving to data_processed/...")
 
fact_visits.to_csv(    os.path.join(OUT, "fact_visits.csv"),      index=False)
review.to_csv(         os.path.join(OUT, "fact_reviews.csv"),     index=False)
offering.to_csv(       os.path.join(OUT, "dim_hotels.csv"),       index=False)
dim_destination.to_csv(os.path.join(OUT, "dim_destination.csv"),  index=False)
dim_time.to_csv(       os.path.join(OUT, "dim_time.csv"),         index=False)
 
print("\n✓ All files saved:")
for f in ["fact_visits.csv","fact_reviews.csv","dim_hotels.csv","dim_destination.csv","dim_time.csv"]:
    path = os.path.join(OUT, f)
    df   = pd.read_csv(path)
    print(f"  {f:30s} → {df.shape[0]:>7,} rows × {df.shape[1]:>2} cols")
 
print("\n✓ Week 3 complete. Ready for Week 4 (Postgres + ETL pipeline).")
 






import pandas as pd, os

OUT = r"C:\Users\aksha\OneDrive\Documents\New folder\Smart Project\data_processed"

for f in ["fact_visits.csv","fact_reviews.csv","dim_hotels.csv","dim_destination.csv","dim_time.csv"]:
    df = pd.read_csv(os.path.join(OUT, f))
    print(f"{f:30s} → {df.shape[0]:>7,} rows × {df.shape[1]} cols")