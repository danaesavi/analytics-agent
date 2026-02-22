# data/preprocess_airbnb.py

import pandas as pd
from pathlib import Path


RAW_PATH = Path("data/raw/listings.csv.gz")
OUT_PATH = Path("data/sample.parquet")
NEIGHBOURHOOD_FIXES = {
    "sterbro": "Østerbro",
    "Nrrebro": "Nørrebro",
    "Amager st": "Amager Øst",
    "Brnshj-Husum": "Brønshøj-Husum",
    "Vanlse": "Vanløse",
}


def clean_airbnb():
    df = pd.read_csv(RAW_PATH, encoding="latin-1")

    # --- Select relevant columns ---
    columns = [
        "id",
        "neighbourhood_cleansed",
        "room_type",
        "price",
        "availability_30",
        "number_of_reviews",
        "review_scores_rating",
        "host_is_superhost",
        "last_review",
        "minimum_nights",
    ]

    df = df[columns].copy()

    # --- Clean price (DKK format usually without $ but still safe) ---
    df["price"] = (
        df["price"]
        .astype(str)
        .str.replace("$", "", regex=False)
        .str.replace(",", "", regex=False)
        .astype(float)
    )

    # --- Rename for clean analytical schema ---
    df = df.rename(
        columns={
            "id": "listing_id",
            "neighbourhood_cleansed": "neighbourhood",
            "review_scores_rating": "review_score",
        }
    )

    # --- Add city column explicitly ---
    df["city"] = "copenhagen"

    # --- Convert types ---
    df["last_review"] = pd.to_datetime(df["last_review"], errors="coerce")
    df["is_superhost"] = df["host_is_superhost"] == "t"
    df = df.drop(columns=["host_is_superhost"])
    df["neighbourhood"] = df["neighbourhood"].replace(NEIGHBOURHOOD_FIXES)


    # --- Remove extreme price outliers (top 1%) ---
    df = df[df["price"] < df["price"].quantile(0.99)]

    # --- Reset index ---
    df = df.reset_index(drop=True)

    # --- Save ---
    df.to_parquet(OUT_PATH, index=False)

    print("Clean dataset saved to:", OUT_PATH)
    print("Rows:", len(df))
    print("Columns:", list(df.columns))


if __name__ == "__main__":
    clean_airbnb()
