import pandas as pd
unwto = pd.read_csv("C:\Users\aksha\TripIQ-Smart-Tourism-Intelligence-Travel-Planning-System\structured_UNWTO_tourism_data.csv")

owid = pd.read_csv(r"C:\Users\aksha\TripIQ-Smart-Tourism-Intelligence-Travel-Planning-System\international-tourist-trips.csv")
print(owid.shape)
print(owid.columns.tolist())
print(owid.head(5).to_string())
print(owid.dtypes)
print(owid.isnull().sum())
print(owid["Year"].min(), owid["Year"].max())  # check year range

print(owid[owid["Code"].isnull()]["Entity"].unique())
owid = owid.dropna(subset=["Code"])

print(owid["Entity"].nunique())          # how many countries
print(owid["Year"].value_counts().sort_index().tail(5))  # recent year coverage
print(owid[owid["Year"] == 2024]["Entity"].count())      # how many countries have 2024 data