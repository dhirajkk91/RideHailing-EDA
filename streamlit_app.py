from pathlib import Path

import pandas as pd
import streamlit as st


SUMMARY_PATH = Path("dashboard_data/summary.csv")


st.set_page_config(
    page_title="NYC Ride-Hailing Trip Analysis",
    layout="wide",
)


@st.cache_data
def load_summary():
    return pd.read_csv(SUMMARY_PATH)


summary = load_summary()
summary_row = summary.iloc[0]

st.title("NYC Ride-Hailing Trip Analysis")
st.caption("Milestone 3 Dashboard Prototype")

st.header("Project Topic")

st.write(
    """
    This project analyzes high-volume ride-hailing trips in New York City using
    January 2026 NYC Taxi & Limousine Commission trip data.
    """
)

st.header("Dataset Cleaning Summary")

metric_cols = st.columns(3)

metric_cols[0].metric("Raw trips", f"{summary_row['raw_rows']:,.0f}")
metric_cols[1].metric("Cleaned trips", f"{summary_row['clean_rows']:,.0f}")
metric_cols[2].metric("Rows removed", f"{summary_row['removed_rows']:,.0f}")

st.subheader("Cleaning Checks")

cleaning_checks = pd.DataFrame(
    {
        "Check": [
            "Trip miles <= 0",
            "Trip time <= 0",
            "Base passenger fare <= 0",
            "Driver pay <= 0",
            "Pickup after dropoff",
        ],
        "Rows flagged": [
            summary_row["non_positive_miles"],
            summary_row["non_positive_time"],
            summary_row["non_positive_base_fare"],
            summary_row["non_positive_driver_pay"],
            summary_row["pickup_after_dropoff"],
        ],
    }
)

st.dataframe(
    cleaning_checks,
    hide_index=True,
    use_container_width=True,
)
