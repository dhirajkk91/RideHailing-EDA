from pathlib import Path

import pandas as pd
import plotly.express as px
import streamlit as st


SUMMARY_PATH = Path("dashboard_data/summary.csv")
HOURLY_PATH = Path("dashboard_data/hourly_metrics.csv")
DAY_HOUR_PATH = Path("dashboard_data/day_hour_metrics.csv")

DAY_ORDER = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]

HOUR_LABELS = {
    hour: f"{hour % 12 or 12} {'AM' if hour < 12 else 'PM'}"
    for hour in range(24)
}

st.set_page_config(
    page_title="NYC Ride-Hailing Trip Analysis",
    layout="wide",
)

@st.cache_data
def load_data():
    summary = pd.read_csv(SUMMARY_PATH)
    hourly = pd.read_csv(HOURLY_PATH)
    day_hour = pd.read_csv(DAY_HOUR_PATH)

    hourly["hour_label"] = hourly["pickup_hour"].map(HOUR_LABELS)
    day_hour["hour_label"] = day_hour["pickup_hour"].map(HOUR_LABELS)

    return summary, hourly, day_hour


summary, hourly, day_hour = load_data()
summary_row = summary.iloc[0]

st.sidebar.header("Filters")

providers = sorted(hourly["provider"].unique())

selected_providers = st.sidebar.multiselect(
    "Provider",
    options=providers,
    default=providers,
)

filtered_hourly = hourly[hourly["provider"].isin(selected_providers)].copy()

st.title("NYC Ride-Hailing Trip Analysis")
st.caption("Milestone 3 Dashboard Prototype")

st.header("Dataset Cleaning Summary")

metric_cols = st.columns(3)

metric_cols[0].metric("Raw trips", f"{summary_row['raw_rows']:,.0f}")
metric_cols[1].metric("Cleaned trips", f"{summary_row['clean_rows']:,.0f}")
metric_cols[2].metric("Rows removed", f"{summary_row['removed_rows']:,.0f}")

st.header("Demand Timing")

left_col, right_col = st.columns(2)

with left_col:
    fig_hourly = px.line(
        filtered_hourly,
        x="pickup_hour",
        y="trip_count",
        color="provider",
        markers=True,
        title="Ride-Hailing Demand by Pickup Hour",
        labels={
            "pickup_hour": "Pickup time",
            "trip_count": "Trip count",
            "provider": "Provider",
        },
        custom_data=["hour_label"],
    )

    fig_hourly.update_traces(
        hovertemplate="<b>%{customdata[0]}</b><br>%{y:,.0f} trips<extra>%{fullData.name}</extra>"
    )

    fig_hourly.update_xaxes(
        tickmode="array",
        tickvals=[0, 3, 6, 9, 12, 15, 18, 21, 23],
        ticktext=[HOUR_LABELS[h] for h in [0, 3, 6, 9, 12, 15, 18, 21, 23]],
    )

    fig_hourly.update_layout(hovermode="x unified")

    st.plotly_chart(fig_hourly, use_container_width=True)

with right_col:
    heatmap_data = day_hour.pivot_table(
        index="pickup_day",
        columns="pickup_hour",
        values="trip_count",
        aggfunc="sum",
        fill_value=0,
    ).reindex(DAY_ORDER)

    fig_heatmap = px.imshow(
        heatmap_data,
        aspect="auto",
        color_continuous_scale="YlGnBu",
        title="Trip Demand by Day and Hour",
        labels={
            "x": "Pickup time",
            "y": "Pickup day",
            "color": "Trips",
        },
    )

    fig_heatmap.update_xaxes(
        tickmode="array",
        tickvals=[0, 3, 6, 9, 12, 15, 18, 21, 23],
        ticktext=[HOUR_LABELS[h] for h in [0, 3, 6, 9, 12, 15, 18, 21, 23]],
    )

    st.plotly_chart(fig_heatmap, use_container_width=True)

st.subheader("Filtered Hourly Metrics Data")

st.dataframe(
    filtered_hourly,
    hide_index=True,
    use_container_width=True,
)
