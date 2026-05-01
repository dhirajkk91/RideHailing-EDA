# NYC Ride-Hailing Trip Analysis

Author: Dhiraj Karki

This project analyzes January 2026 high-volume ride-hailing trips in New York City using NYC Taxi & Limousine Commission trip records. The project includes a data cleaning and EDA notebook, a dashboard data preparation script, a Streamlit dashboard prototype, and a written Milestone 3 narrative.

The main project question is:

**How do time of day, pickup location, and provider shape ride-hailing demand and fare patterns in New York City?**

## Files

- `data.ipynb` - Jupyter notebook for data loading, cleaning, feature engineering, and exploratory data analysis.
- `dashboard_data.py` - Script that creates precomputed CSV files for the Streamlit dashboard.
- `streamlit_app.py` - Streamlit dashboard prototype with interactive Plotly visualizations.
- `milestone_3_draft.md` - Draft written narrative for Milestone 3 covering question, findings, and limitations.
- `dashboard_data/` - Generated dashboard data files, including summary tables, demand aggregates, pickup zone metrics, trip sample data, and TLC taxi zone lookup data.
- `requirements.txt` - Python packages required for the project.

## Data Source

The project uses the January 2026 NYC TLC High Volume For-Hire Vehicle trip record file. The dashboard also uses the official TLC taxi zone lookup table to convert pickup location IDs into readable borough and zone names.

Provider mapping:

- `HV0003` - Uber
- `HV0005` - Lyft

## Work Completed

### 1. Data Cleaning and EDA

The notebook loads the raw parquet file, keeps the fields most relevant to trip behavior and fare analysis, checks data quality, removes invalid records, engineers new features, and creates exploratory visualizations.

Cleaning removes rows where:

- trip miles are less than or equal to zero
- trip time is less than or equal to zero
- base passenger fare is less than or equal to zero
- driver pay is less than or equal to zero
- pickup time occurs after dropoff time

Feature engineering creates:

- `trip_minutes`
- `total_fare`
- `fare_per_mile`
- `speed_mph`
- `pickup_date`
- `pickup_hour`
- `pickup_day`
- provider name

### 2. Dashboard Data Preparation

The dashboard uses precomputed CSV files so Streamlit does not need to load the full raw dataset every time. Run:

```bash
python dashboard_data.py
```

This creates:

- `dashboard_data/summary.csv`
- `dashboard_data/hourly_metrics.csv`
- `dashboard_data/day_hour_metrics.csv`
- `dashboard_data/pickup_zone_metrics.csv`
- `dashboard_data/trip_sample.csv`

### 3. Streamlit Dashboard Prototype

The dashboard includes tabs for:

- **Overview** - filter-aware KPI cards and cleaning summary
- **Demand Timing** - interactive Plotly line chart by pickup hour and heatmap by day/hour
- **Pickup Locations** - top pickup areas using TLC taxi zone names
- **Provider Comparison** - Uber and Lyft trip volume and average trip metric comparison
- **Fare Analysis** - fare vs distance scatterplot using sampled trip-level data

Dashboard filters include:

- provider
- pickup borough
- pickup time range
- pickup date range

## Initial Findings

- Ride-hailing demand is highest in the late afternoon and evening, with 6 PM as the busiest pickup hour in the cleaned January 2026 data.
- Saturday has the highest overall trip volume, followed by Friday and Thursday.
- Pickup activity is concentrated in a smaller set of high-volume areas, including airports, dense residential areas, entertainment districts, and central business districts.
- Uber accounts for a larger share of cleaned trips than Lyft in this month.
- Trip distance and total fare have a strong positive relationship, although fares still vary for trips of similar distance.

## Limitations

- The analysis is descriptive and does not prove causation.
- The dataset covers only January 2026, so results should not be generalized to the full year without more data.
- Weather, events, traffic, transit disruptions, and surge pricing are not included.
- The fare-distance scatterplot uses a sampled trip-level dataset for dashboard performance.

## Setup

Create and activate a virtual environment, then install dependencies:

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

On Windows:

```bash
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
```

Generate dashboard data:

```bash
python dashboard_data.py
```

Run the Streamlit dashboard:

```bash
streamlit run streamlit_app.py
```

## Milestone 3 Deliverables

- Working Streamlit dashboard prototype: `streamlit_app.py`
- At least two interactive Plotly views: included in the Demand Timing tab and additional dashboard tabs
- Draft written narrative: `milestone_3_draft.md`
- Dashboard data preparation pipeline: `dashboard_data.py`
