import streamlit as st


st.set_page_config(
    page_title="NYC Ride-Hailing Trip Analysis",
    layout="wide",
)

st.title("NYC Ride-Hailing Trip Analysis")

st.caption("Milestone 3 Dashboard Prototype")

st.header("Project Topic")

st.write(
    """
    This project analyzes high-volume ride-hailing trips in New York City using
    January 2026 NYC Taxi & Limousine Commission trip data.
    """
)

st.header("Main Analytical Question")

st.write(
    """
    How do time of day, pickup location, and provider shape ride-hailing demand
    and fare patterns in New York City?
    """
)

st.header("Dataset")

st.write(
    """
    The dataset comes from the NYC TLC High Volume For-Hire Vehicle trip records.
    It includes trip pickup and dropoff times, pickup and dropoff location IDs,
    trip distance, trip duration, passenger fare, tips, tolls, and driver pay.
    """
)

st.header("Dashboard Plan")

st.write(
    """
    This dashboard will eventually include interactive views for:
    """
)

st.markdown(
    """
    - Ride demand by hour and day of week
    - Pickup activity by NYC taxi zone
    - Fare patterns by distance and provider
    - Provider comparison between Uber and Lyft
    """
)
