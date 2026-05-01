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

@st.cache_data(ttl=0)
def load_data():
    summary = pd.read_csv(SUMMARY_PATH)
    hourly = pd.read_csv(HOURLY_PATH, parse_dates=["pickup_date"])
    day_hour = pd.read_csv(DAY_HOUR_PATH, parse_dates=["pickup_date"])

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

st.sidebar.markdown("Pickup time range")

from_col, to_col = st.sidebar.columns(2)

start_hour = from_col.selectbox(
    "From",
    options=list(range(24)),
    index=0,
    format_func=lambda hour: HOUR_LABELS[hour],
)

end_hour = to_col.selectbox(
    "To",
    options=list(range(24)),
    index=23,
    format_func=lambda hour: HOUR_LABELS[hour],
)

st.sidebar.caption(f"{HOUR_LABELS[start_hour]} to {HOUR_LABELS[end_hour]}")


if start_hour <= end_hour:
    selected_hours = list(range(start_hour, end_hour + 1))
else:
    selected_hours = list(range(start_hour, 24)) + list(range(0, end_hour + 1))


min_date = hourly["pickup_date"].min().date()
max_date = hourly["pickup_date"].max().date()

selected_dates = st.sidebar.date_input(
    "Pickup dates",
    value=(min_date, max_date),
    min_value=min_date,
    max_value=max_date,
)

if isinstance(selected_dates, tuple) and len(selected_dates) == 2:
    start_date = pd.to_datetime(selected_dates[0])
    end_date = pd.to_datetime(selected_dates[1])
else:
    start_date = pd.to_datetime(min_date)
    end_date = pd.to_datetime(max_date)

filtered_hourly = hourly[
    hourly["provider"].isin(selected_providers)
    & hourly["pickup_hour"].isin(selected_hours)
    & hourly["pickup_date"].between(start_date, end_date)
].copy()

filtered_day_hour = day_hour[
    day_hour["provider"].isin(selected_providers)
    & day_hour["pickup_hour"].isin(selected_hours)
    & day_hour["pickup_date"].between(start_date, end_date)
].copy()

hourly_plot = (
    filtered_hourly.groupby(["provider", "pickup_hour", "hour_label"], as_index=False)
    .agg(trip_count=("trip_count", "sum"))
)

filtered_trip_count = filtered_hourly["trip_count"].sum()

if filtered_trip_count > 0:
    avg_fare = (
        (filtered_hourly["avg_fare"] * filtered_hourly["trip_count"]).sum()
        / filtered_trip_count
    )
    avg_miles = (
        (filtered_hourly["avg_miles"] * filtered_hourly["trip_count"]).sum()
        / filtered_trip_count
    )
    avg_minutes = (
        (filtered_hourly["avg_minutes"] * filtered_hourly["trip_count"]).sum()
        / filtered_trip_count
    )

    peak_hour_row = (
        filtered_hourly.groupby("pickup_hour", as_index=False)["trip_count"]
        .sum()
        .sort_values("trip_count", ascending=False)
        .head(1)
    )

    peak_hour = HOUR_LABELS[int(peak_hour_row.iloc[0]["pickup_hour"])]
else:
    avg_fare = 0
    avg_miles = 0
    avg_minutes = 0
    peak_hour = "N/A"

st.title("NYC Ride-Hailing Trip Analysis")
st.caption("Milestone 3 Dashboard Prototype")

st.header("Dataset Cleaning Summary")

metric_cols = st.columns(5)

metric_cols[0].metric("Filtered trips", f"{filtered_trip_count:,.0f}")
metric_cols[1].metric("Avg fare", f"${avg_fare:,.2f}")
metric_cols[2].metric("Avg distance", f"{avg_miles:,.2f} mi")
metric_cols[3].metric("Avg duration", f"{avg_minutes:,.1f} min")
metric_cols[4].metric("Peak hour", peak_hour)

with st.expander("Cleaning summary"):
    cleaning_checks = pd.DataFrame(
        {
            "Check": [
                "Raw trips",
                "Cleaned trips",
                "Rows removed",
                "Trip miles <= 0",
                "Trip time <= 0",
                "Base passenger fare <= 0",
                "Driver pay <= 0",
                "Pickup after dropoff",
            ],
            "Rows": [
                summary_row["raw_rows"],
                summary_row["clean_rows"],
                summary_row["removed_rows"],
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

st.header("Demand Timing")

left_col, right_col = st.columns(2)

with left_col:
    fig_hourly = px.line(
        hourly_plot,
        x="pickup_hour",
        y="trip_count",
        color="provider",
        markers=True,
        title=f"Ride-Hailing Demand by Pickup Hour ({HOUR_LABELS[start_hour]} to {HOUR_LABELS[end_hour]})",
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
    heatmap_data = filtered_day_hour.pivot_table(
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
