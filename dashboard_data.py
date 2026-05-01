from pathlib import Path

import pandas as pd


DATA_PATH = Path("fhvhv_tripdata_2026-01.parquet")
OUTPUT_DIR = Path("dashboard_data")

COLUMNS_TO_KEEP = [
    "hvfhs_license_num",
    "pickup_datetime",
    "dropoff_datetime",
    "PULocationID",
    "DOLocationID",
    "trip_miles",
    "trip_time",
    "base_passenger_fare",
    "tolls",
    "tips",
    "driver_pay",
]

PROVIDER_MAP = {
    "HV0003": "Uber",
    "HV0005": "Lyft",
}

def clean_data(df):
    invalid_miles = df["trip_miles"] <= 0
    invalid_time = df["trip_time"] <= 0
    invalid_fare = df["base_passenger_fare"] <= 0
    invalid_pay = df["driver_pay"] <= 0
    invalid_time_order = df["pickup_datetime"] > df["dropoff_datetime"]

    valid_rows = (
        (~invalid_miles)
        & (~invalid_time)
        & (~invalid_fare)
        & (~invalid_pay)
        & (~invalid_time_order)
    )

    clean_df = df[valid_rows].copy()

    clean_df["provider"] = (
        clean_df["hvfhs_license_num"].map(PROVIDER_MAP).fillna(clean_df["hvfhs_license_num"])
    )
    clean_df["trip_minutes"] = clean_df["trip_time"] / 60
    clean_df["total_fare"] = (
        clean_df["base_passenger_fare"] + clean_df["tolls"] + clean_df["tips"]
    )
    clean_df["pickup_date"] = clean_df["pickup_datetime"].dt.date
    clean_df["pickup_hour"] = clean_df["pickup_datetime"].dt.hour
    clean_df["pickup_day"] = clean_df["pickup_datetime"].dt.day_name()
    clean_df["day_order"] = clean_df["pickup_datetime"].dt.dayofweek

    summary = pd.DataFrame(
        [
            {
                "raw_rows": len(df),
                "clean_rows": len(clean_df),
                "removed_rows": len(df) - len(clean_df),
                "non_positive_miles": int(invalid_miles.sum()),
                "non_positive_time": int(invalid_time.sum()),
                "non_positive_base_fare": int(invalid_fare.sum()),
                "non_positive_driver_pay": int(invalid_pay.sum()),
                "pickup_after_dropoff": int(invalid_time_order.sum()),
            }
        ]
    )

    return clean_df, summary


def build_hourly_metrics(clean_df):
    hourly_metrics = (
        clean_df.groupby(
            ["provider", "pickup_date", "pickup_day", "day_order", "pickup_hour"],
            as_index=False,
        )
        .agg(
            trip_count=("pickup_datetime", "size"),
            avg_fare=("total_fare", "mean"),
            avg_miles=("trip_miles", "mean"),
            avg_minutes=("trip_minutes", "mean"),
        )
    )

    return hourly_metrics


def build_day_hour_metrics(clean_df):
    day_hour_metrics = (
        clean_df.groupby(
            ["provider", "pickup_date", "pickup_day", "day_order", "pickup_hour"],
            as_index=False,
        )
        .agg(
            trip_count=("pickup_datetime", "size"),
            avg_fare=("total_fare", "mean"),
            avg_miles=("trip_miles", "mean"),
            avg_minutes=("trip_minutes", "mean"),
        )
        .sort_values(["provider", "pickup_date", "day_order", "pickup_hour"])
    )

    return day_hour_metrics

def build_pickup_zone_metrics(clean_df):
    pickup_zone_metrics = (
        clean_df.groupby(["provider", "PULocationID"], as_index=False)
        .agg(
            trip_count=("pickup_datetime", "size"),
            avg_fare=("total_fare", "mean"),
            avg_miles=("trip_miles", "mean"),
            avg_minutes=("trip_minutes", "mean"),
        )
        .sort_values("trip_count", ascending=False)
    )

    return pickup_zone_metrics
    
def main():
    OUTPUT_DIR.mkdir(exist_ok=True)

    df = pd.read_parquet(DATA_PATH, columns=COLUMNS_TO_KEEP)

    clean_df, summary = clean_data(df)
    hourly_metrics = build_hourly_metrics(clean_df)
    day_hour_metrics = build_day_hour_metrics(clean_df)
    pickup_zone_metrics = build_pickup_zone_metrics(clean_df)

    summary.to_csv(OUTPUT_DIR / "summary.csv", index=False)
    hourly_metrics.to_csv(OUTPUT_DIR / "hourly_metrics.csv", index=False)
    day_hour_metrics.to_csv(OUTPUT_DIR / "day_hour_metrics.csv", index=False)
    pickup_zone_metrics.to_csv(OUTPUT_DIR / "pickup_zone_metrics.csv", index=False)

    print("Created dashboard_data/summary.csv")
    print("Created dashboard_data/hourly_metrics.csv")
    print("Created dashboard_data/day_hour_metrics.csv")
    print("Created dashboard_data/pickup_zone_metrics.csv")
    print(pickup_zone_metrics.head().to_string(index=False))


if __name__ == "__main__":
    main()
