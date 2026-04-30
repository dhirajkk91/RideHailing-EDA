# Ride-Hailing Data Cleaning and EDA

Author: Dhiraj Karki

This project analyzes January 2026 high-volume ride-hailing trip data using Python. The work so far focuses on loading the raw parquet dataset, cleaning invalid records, creating useful trip-level features, and performing exploratory data analysis on demand, fares, providers, pickup locations, and trip behavior.

## Files

- `data.ipynb` - Main notebook containing the data cleaning and exploratory analysis.
- `fhvhv_tripdata_2026-01.parquet` - Raw ride-hailing trip dataset used by the notebook.
- `requirements.txt` - Python packages needed to run the notebook.

## Work Completed So Far

### 1. Data Loading

The notebook loads the parquet dataset with pandas and previews the raw data. It also checks the dataset shape, column names, data types, missing values, and summary statistics.

### 2. Column Selection

The analysis keeps the columns most relevant for trip behavior and fare analysis:

- `hvfhs_license_num`
- `pickup_datetime`
- `dropoff_datetime`
- `PULocationID`
- `DOLocationID`
- `trip_miles`
- `trip_time`
- `base_passenger_fare`
- `tolls`
- `tips`
- `driver_pay`

### 3. Data Cleaning

Invalid trip records are identified and removed, including rows where:

- trip miles are less than or equal to zero
- trip time is less than or equal to zero
- base passenger fare is less than or equal to zero
- driver pay is less than or equal to zero
- pickup time occurs after dropoff time

A cleaning summary is created to show how many rows were affected by each issue.

### 4. Feature Engineering

Several new columns are created to support the analysis:

- `trip_minutes` - trip duration converted from seconds to minutes
- `total_fare` - base passenger fare plus tolls and tips
- `fare_per_mile` - total fare divided by trip miles
- `speed_mph` - estimated trip speed in miles per hour
- `pickup_hour` - hour of pickup
- `pickup_day` - day of week of pickup

### 5. Exploratory Data Analysis

The notebook includes visual and tabular analysis for:

- distributions of trip miles, trip duration, and total fare
- trip demand by pickup hour
- trip demand by day of week
- top 10 pickup location IDs
- provider-level summary for Uber and Lyft
- average fare by hour
- relationship between trip miles and total fare
- demand heatmap by day and hour
- correlation heatmap for numeric trip metrics

## Initial Findings

- Ride demand changes throughout the day, with strong activity during morning work hours and the highest activity in the late afternoon and evening.
- Demand changes across the week, with Saturday showing the highest trip volume and Sunday being less busy.
- Ride-hailing activity is concentrated in a small group of pickup location IDs, suggesting geographic clustering.
- Trip distance and total fare have a strong positive relationship, meaning longer trips usually cost more.
- Average fare changes by hour, likely because trip distance and rider behavior vary throughout the day.
- Demand depends on both day of week and hour, as shown by the day-by-hour heatmap.

## Provider Mapping

The notebook uses the following high-volume for-hire service license mapping:

- `HV0003` - Uber
- `HV0005` - Lyft

## Future Exploration

Possible next steps include:

- mapping pickup and dropoff location IDs to actual NYC taxi zones
- comparing trip patterns by provider in more detail
- investigating whether high fares are caused by longer distance, time of day, tolls, or tipping behavior
- analyzing trip efficiency using speed and duration by hour or pickup zone
- building a machine learning model to predict total fare or trip demand

## Setup

Create and activate a virtual environment, then install the dependencies:

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

Start Jupyter and open the notebook:

```bash
jupyter notebook data.ipynb
```

## Notes

The parquet dataset is large, so the notebook samples rows for some plots to keep visualization performance manageable. Make sure `fhvhv_tripdata_2026-01.parquet` stays in the same folder as `data.ipynb`, because the notebook reads it using a relative file path.
