from pathlib import Path

import pandas as pd
import plotly.express as px
import streamlit as st


SUMMARY_PATH = Path("dashboard_data/summary.csv")
HOURLY_PATH = Path("dashboard_data/hourly_metrics.csv")
PICKUP_ZONE_PATH = Path("dashboard_data/pickup_zone_metrics.csv")
ZONE_LOOKUP_PATH = Path("dashboard_data/taxi_zone_lookup.csv")
TRIP_SAMPLE_PATH = Path("dashboard_data/trip_sample.csv")

DAY_ORDER = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]

HOUR_LABELS = {
    hour: f"{hour % 12 or 12} {'AM' if hour < 12 else 'PM'}"
    for hour in range(24)
}

st.set_page_config(
    page_title="NYC Ride-Hailing Trip Analysis",
    layout="wide",
    initial_sidebar_state="expanded",
)


@st.cache_data
def load_data():
    # Loading precomputed dashboard tables and attaching readable TLC pickup zone names.
    summary = pd.read_csv(SUMMARY_PATH)
    hourly = pd.read_csv(HOURLY_PATH, parse_dates=["pickup_date"])
    pickup_zones = pd.read_csv(PICKUP_ZONE_PATH, parse_dates=["pickup_date"])
    trip_sample = pd.read_csv(TRIP_SAMPLE_PATH, parse_dates=["pickup_date"])

    zone_lookup = pd.read_csv(ZONE_LOOKUP_PATH)
    zone_lookup = zone_lookup.rename(columns={"LocationID": "PULocationID"})
    zone_lookup["pickup_zone"] = zone_lookup["Zone"] + ", " + zone_lookup["Borough"]

    pickup_zones = pickup_zones.merge(
        zone_lookup[["PULocationID", "Borough", "Zone", "pickup_zone"]],
        on="PULocationID",
        how="left",
    )

    trip_sample = trip_sample.merge(
        zone_lookup[["PULocationID", "Borough", "Zone", "pickup_zone"]],
        on="PULocationID",
        how="left",
    )

    hourly["hour_label"] = hourly["pickup_hour"].map(HOUR_LABELS)
    pickup_zones["hour_label"] = pickup_zones["pickup_hour"].map(HOUR_LABELS)
    trip_sample["hour_label"] = trip_sample["pickup_hour"].map(HOUR_LABELS)

    return summary, hourly, pickup_zones, trip_sample


summary, hourly, pickup_zones, trip_sample = load_data()
summary_row = summary.iloc[0]


def weighted_average(df, value_col):
    # Averaging aggregate rows by trip volume so large groups count proportionally.
    total_trips = df["trip_count"].sum()
    if total_trips == 0:
        return 0
    return (df[value_col] * df["trip_count"]).sum() / total_trips


def summarize_by_group(df, group_cols):
    # Summarizing an already-aggregated table without losing trip-volume weighting.
    if df.empty:
        return pd.DataFrame(
            columns=group_cols + ["trip_count", "avg_fare", "avg_miles", "avg_minutes"]
        )

    rows = []
    for key, group in df.groupby(group_cols):
        if not isinstance(key, tuple):
            key = (key,)
        row = dict(zip(group_cols, key))
        row.update(
            {
                "trip_count": group["trip_count"].sum(),
                "avg_fare": weighted_average(group, "avg_fare"),
                "avg_miles": weighted_average(group, "avg_miles"),
                "avg_minutes": weighted_average(group, "avg_minutes"),
            }
        )
        rows.append(row)
    return pd.DataFrame(rows)


def describe_correlation(value):
    # Convering a correlation value into plain-language strength for the dashboard.
    abs_value = abs(value)
    if abs_value >= 0.75:
        return "strong"
    if abs_value >= 0.45:
        return "moderate"
    return "weak"


# Sidebar filters
st.sidebar.header("Filters")

providers = sorted(hourly["provider"].unique())

selected_providers = st.sidebar.multiselect(
    "Provider",
    options=providers,
    default=providers,
)

boroughs = sorted(pickup_zones["Borough"].dropna().unique())

selected_boroughs = st.sidebar.multiselect(
    "Pickup borough",
    options=boroughs,
    default=boroughs,
)

if not selected_providers:
    st.warning("Select at least one provider to view the dashboard.")
    st.stop()

if not selected_boroughs:
    st.warning("Select at least one pickup borough to view the dashboard.")
    st.stop()

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

# Filtering data based on sidebar selections

filtered_hourly = hourly[
    hourly["provider"].isin(selected_providers)
    & hourly["pickup_hour"].isin(selected_hours)
    & hourly["pickup_date"].between(start_date, end_date)
].copy()

filtered_pickup_zones = pickup_zones[
    pickup_zones["provider"].isin(selected_providers)
    & pickup_zones["Borough"].isin(selected_boroughs)
    & pickup_zones["pickup_hour"].isin(selected_hours)
    & pickup_zones["pickup_date"].between(start_date, end_date)
].copy()

filtered_trip_sample = trip_sample[
    trip_sample["provider"].isin(selected_providers)
    & trip_sample["Borough"].isin(selected_boroughs)
    & trip_sample["pickup_hour"].isin(selected_hours)
    & trip_sample["pickup_date"].between(start_date, end_date)
].copy()

if filtered_pickup_zones.empty:
    st.warning("No trips match the selected provider, date, and time filters.")
    st.stop()

# Use the pickup-zone aggregate as the main analysis table so every sidebar
# filter, including borough, affects the KPI cards and comparison charts.

hourly_plot = (
    filtered_pickup_zones.groupby(["provider", "pickup_hour", "hour_label"], as_index=False)
    .agg(trip_count=("trip_count", "sum"))
)

filtered_trip_count = filtered_pickup_zones["trip_count"].sum()

if filtered_trip_count > 0:
    avg_fare = weighted_average(filtered_pickup_zones, "avg_fare")
    avg_miles = weighted_average(filtered_pickup_zones, "avg_miles")
    avg_minutes = weighted_average(filtered_pickup_zones, "avg_minutes")

    peak_hour_row = (
        filtered_pickup_zones.groupby("pickup_hour", as_index=False)["trip_count"]
        .sum()
        .sort_values("trip_count", ascending=False)
        .head(1)
    )

    peak_hour = HOUR_LABELS[int(peak_hour_row.iloc[0]["pickup_hour"])]
    peak_hour_count = int(peak_hour_row.iloc[0]["trip_count"])
else:
    avg_fare = 0
    avg_miles = 0
    avg_minutes = 0
    peak_hour = "N/A"
    peak_hour_count = 0

day_summary = (
    filtered_pickup_zones.groupby(["pickup_day", "day_order"], as_index=False)["trip_count"]
    .sum()
    .sort_values(["trip_count"], ascending=False)
)
busiest_day = day_summary.iloc[0]["pickup_day"]
busiest_day_count = int(day_summary.iloc[0]["trip_count"])

# Main Page Content

st.title("NYC Ride-Hailing Trip Analysis")
st.caption("Final Project Dashboard")

st.write(
    """
    This dashboard explores January 2026 NYC high-volume ride-hailing trips by
    demand timing, pickup location, provider, and fare behavior.
    """
)

overview_tab, timing_tab, location_tab, provider_tab, fare_tab = st.tabs(
    ["Overview", "Demand Timing", "Pickup Locations", "Provider Comparison", "Fare Analysis"]
)

# Display summary metrics in the Overview tab

with overview_tab:
    st.header("Dashboard Overview")

    metric_cols = st.columns(5)

    metric_cols[0].metric("Filtered trips", f"{filtered_trip_count:,.0f}")
    metric_cols[1].metric("Avg fare", f"${avg_fare:,.2f}")
    metric_cols[2].metric("Avg distance", f"{avg_miles:,.2f} mi")
    metric_cols[3].metric("Avg duration", f"{avg_minutes:,.1f} min")
    metric_cols[4].metric("Peak hour", peak_hour)

    st.markdown(
        f"""
        **Current filter takeaway:** The selected trips average **${avg_fare:,.2f}**
        for **{avg_miles:,.2f} miles** and **{avg_minutes:,.1f} minutes**. The
        highest-volume pickup hour is **{peak_hour}** with **{peak_hour_count:,.0f}**
        trips, while **{busiest_day}** is the busiest selected day with
        **{busiest_day_count:,.0f}** trips. These summary numbers are descriptive:
        they show where demand is concentrated, not why the pattern happened.
        """
    )

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
            width="stretch",
        )

# Demand Timing tab with hourly line chart and day-hour heatmap

with timing_tab:
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

        st.plotly_chart(fig_hourly, width="stretch")

        st.markdown(
            f"""
            **What this means:** Demand is not evenly spread across the selected
            time range. The strongest pickup period is **{peak_hour}**, which
            suggests ride-hailing activity is concentrated around specific daily
            routines such as commuting, evening travel, airport movement, or
            nightlife. This chart is best for comparing how Uber and Lyft demand
            changes by hour under the same filters.
            """
        )

    with right_col:
        heatmap_data = filtered_pickup_zones.pivot_table(
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

        st.plotly_chart(fig_heatmap, width="stretch")

        heatmap_peak = heatmap_data.stack().idxmax()
        heatmap_peak_day, heatmap_peak_hour = heatmap_peak
        heatmap_peak_trips = int(heatmap_data.stack().max())

        st.markdown(
            f"""
            **What this means:** The heatmap shows the combined effect of weekday
            and time of day. The darkest cell in the current selection is
            **{heatmap_peak_day} at {HOUR_LABELS[int(heatmap_peak_hour)]}**
            with **{heatmap_peak_trips:,.0f}** trips. This helps identify whether
            demand is mostly a weekday pattern, a weekend pattern, or a specific
            hour-of-day pattern.
            """
        )

# Pickup Location tab with top pickup zones bar chart and data table

with location_tab:
    st.header("Pickup Location Patterns")

    top_pickup_zones = (
        summarize_by_group(filtered_pickup_zones, ["pickup_zone", "Borough", "Zone"])
        .sort_values("trip_count", ascending=False)
        .head(10)
    )

    fig_pickup_zones = px.bar(
        top_pickup_zones.sort_values("trip_count"),
        x="trip_count",
        y="pickup_zone",
        color="Borough",
        orientation="h",
        title="Top 10 Pickup Areas",
        labels={
            "trip_count": "Trip count",
            "pickup_zone": "Pickup area",
            "Borough": "Borough",
        },
    )

    st.plotly_chart(fig_pickup_zones, width="stretch")

    top_zone = top_pickup_zones.iloc[0]
    top_zone_share = top_zone["trip_count"] / filtered_trip_count

    st.markdown(
        f"""
        **What this means:** Pickups are geographically concentrated rather than
        evenly distributed across the city. The highest-volume selected pickup
        area is **{top_zone["pickup_zone"]}**, with **{top_zone["trip_count"]:,.0f}**
        trips, or about **{top_zone_share:.1%}** of filtered trips. High-ranking
        zones usually point to airports, dense residential neighborhoods,
        entertainment areas, and central business districts.
        """
    )

    st.dataframe(
        top_pickup_zones,
        hide_index=True,
        width="stretch",
    )
# Provider Comparison tab with trip count and average metrics bar charts, and data table

with provider_tab:
    st.header("Provider Comparison")

    provider_summary = summarize_by_group(filtered_pickup_zones, ["provider"]).sort_values(
        "trip_count", ascending=False
    )

    provider_summary_long = provider_summary.melt(
        id_vars="provider",
        value_vars=["avg_fare", "avg_miles", "avg_minutes"],
        var_name="metric",
        value_name="value",
    )

    provider_summary_long["metric"] = provider_summary_long["metric"].map(
        {
            "avg_fare": "Average Fare",
            "avg_miles": "Average Miles",
            "avg_minutes": "Average Minutes",
        }
    )

    left_col, right_col = st.columns(2)

    with left_col:
        fig_provider_trips = px.bar(
            provider_summary,
            x="provider",
            y="trip_count",
            color="provider",
            title="Trip Count by Provider",
            labels={
                "provider": "Provider",
                "trip_count": "Trip count",
            },
        )

        st.plotly_chart(fig_provider_trips, width="stretch")

        leading_provider = provider_summary.iloc[0]
        leading_provider_share = leading_provider["trip_count"] / filtered_trip_count

        st.markdown(
            f"""
            **What this means:** The provider mix is uneven in the current
            selection. **{leading_provider["provider"]}** has the largest trip
            volume with **{leading_provider["trip_count"]:,.0f}** trips, about
            **{leading_provider_share:.1%}** of filtered demand. This shows market
            share within the selected filters, not customer preference by itself.
            """
        )

    with right_col:
        fig_provider_metrics = px.bar(
            provider_summary_long,
            x="provider",
            y="value",
            color="metric",
            barmode="group",
            title="Average Trip Metrics by Provider",
            labels={
                "provider": "Provider",
                "value": "Value",
                "metric": "Metric",
            },
        )

        st.plotly_chart(fig_provider_metrics, width="stretch")

        highest_fare_provider = provider_summary.sort_values("avg_fare", ascending=False).iloc[0]

        st.markdown(
            f"""
            **What this means:** Average trip characteristics differ by provider.
            In this selection, **{highest_fare_provider["provider"]}** has the
            highest average fare at **${highest_fare_provider["avg_fare"]:,.2f}**.
            This should be interpreted carefully because fare differences can
            reflect different trip distances, pickup areas, tolls, tips, and time
            periods, not only provider pricing.
            """
        )

    st.dataframe(
        provider_summary,
        hide_index=True,
        width="stretch",
    )

# Fare Analysis tab with fare vs distance scatter plot and correlation metric
with fare_tab:
    st.header("Fare and Distance Relationship")

    if filtered_trip_sample.empty:
        st.warning("No sampled trips match the selected filters.")
    else:
        fig_fare_distance = px.scatter(
            filtered_trip_sample,
            x="trip_miles",
            y="total_fare",
            color="provider",
            hover_name="pickup_zone",
            hover_data={
                "Borough": True,
                "pickup_day": True,
                "hour_label": True,
                "trip_minutes": ":.1f",
                "fare_per_mile": ":$.2f",
                "provider": False,
            },
            opacity=0.5,
            title="Total Fare vs Trip Distance",
            labels={
                "trip_miles": "Trip miles",
                "total_fare": "Total fare",
                "provider": "Provider",
            },
        )

        st.plotly_chart(fig_fare_distance, width="stretch")

        fare_distance_corr = filtered_trip_sample[["trip_miles", "total_fare"]].corr().iloc[0, 1]

        st.metric(
            "Fare-distance correlation in sample",
            f"{fare_distance_corr:.2f}",
        )

        corr_strength = describe_correlation(fare_distance_corr)

        st.markdown(
            f"""
            **What this means:** The sample shows a **{corr_strength} positive
            relationship** between trip distance and total fare. Longer trips
            usually cost more, which matches expectations, but the spread around
            the trend matters too: trips with similar mileage can still have
            different fares because of tolls, tips, airport trips, congestion,
            provider mix, and pickup time.
            """
        )

    with st.expander("Filtered hourly metrics data"):
        st.dataframe(
            filtered_hourly,
            hide_index=True,
            width="stretch",
        )
