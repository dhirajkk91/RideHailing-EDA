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


def main():
    OUTPUT_DIR.mkdir(exist_ok=True)

    df = pd.read_parquet(DATA_PATH, columns=COLUMNS_TO_KEEP)

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

    summary = pd.DataFrame(
        [
            {
                "raw_rows": len(df),
                "clean_rows": int(valid_rows.sum()),
                "removed_rows": int((~valid_rows).sum()),
                "non_positive_miles": int(invalid_miles.sum()),
                "non_positive_time": int(invalid_time.sum()),
                "non_positive_base_fare": int(invalid_fare.sum()),
                "non_positive_driver_pay": int(invalid_pay.sum()),
                "pickup_after_dropoff": int(invalid_time_order.sum()),
            }
        ]
    )

    summary.to_csv(OUTPUT_DIR / "summary.csv", index=False)

    print("Created dashboard_data/summary.csv")
    print(summary.to_string(index=False))


if __name__ == "__main__":
    main()
