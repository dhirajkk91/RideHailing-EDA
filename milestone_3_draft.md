# Milestone 3 Narrative Draft: NYC Ride-Hailing Trip Analysis

## Question

This project analyzes January 2026 high-volume ride-hailing trips in New York City. The main question is: **How do time of day, pickup location, and provider shape ride-hailing demand and fare patterns?** This question fits the ride-hailing trip analysis topic because the dashboard connects temporal demand, pickup geography, provider differences, and fare behavior in one interactive prototype.

The goal of the Milestone 3 dashboard is not only to show charts, but to make the cleaned dataset easier to explore. A user can filter by provider, pickup borough, pickup date range, and pickup time range, then compare demand timing, pickup locations, provider-level patterns, and fare-distance relationships. This structure turns the previous notebook EDA into a more usable data story.

## Data and Methods

The data comes from the NYC Taxi & Limousine Commission high-volume for-hire vehicle trip records for January 2026. The raw dataset contains 20,940,373 trips. The analysis keeps fields related to provider license number, pickup and dropoff times, pickup and dropoff location IDs, trip miles, trip time, base passenger fare, tolls, tips, and driver pay.

Before building the dashboard, I cleaned the dataset by removing records with non-positive trip miles, non-positive trip time, non-positive base passenger fare, non-positive driver pay, or pickup times after dropoff times. After cleaning, 20,835,764 trips remain, meaning 104,609 records were removed. Most removed rows came from non-positive base passenger fare and non-positive driver pay. I then created features for trip minutes, total fare, fare per mile, estimated speed, pickup date, pickup hour, pickup day of week, and provider name. Provider codes were mapped so `HV0003` is shown as Uber and `HV0005` is shown as Lyft.

To keep the Streamlit dashboard fast, I used precomputed CSV files instead of loading the full parquet file directly in the app. These files include a cleaning summary, hourly demand metrics, day-hour demand metrics, pickup-zone metrics, and a sampled trip-level file for fare analysis. Pickup location IDs were joined to the TLC taxi zone lookup table so the dashboard can show readable pickup areas such as LaGuardia Airport, Queens instead of only numeric zone IDs.

## Findings

The dashboard shows that ride-hailing demand is strongly shaped by time of day. Across the cleaned January dataset, the busiest pickup hour is 6 PM, with 1,266,593 trips. The next busiest hours are 7 PM, 5 PM, 8 PM, and 4 PM. This suggests that late afternoon and evening travel is the strongest demand period in this month. The day-and-hour heatmap adds more context by showing that demand also varies by day of week. Saturday has the highest trip volume with 4,044,377 trips, followed by Friday and Thursday. Monday and Sunday have the lowest total trip counts.

Pickup activity is also geographically concentrated. The top pickup areas include LaGuardia Airport, JFK Airport, Crown Heights North, Bushwick South, East New York, East Village, Times Square/Theatre District, Midtown Center, Park Slope, and TriBeCa/Civic Center. These locations suggest that ride-hailing demand is clustered around airports, dense residential neighborhoods, entertainment districts, and business areas. Using taxi zone names makes this pattern much easier to interpret than using raw pickup location IDs.

The provider comparison shows that Uber and Lyft do not contribute equally to the January 2026 trip volume. Uber accounts for about 72.9% of cleaned trips, while Lyft accounts for about 27.1%. Uber also has a slightly higher average fare, about $28.38 compared with Lyft’s $26.73, and a slightly longer average trip distance, about 4.70 miles compared with Lyft’s 4.47 miles. These differences are descriptive and should not be treated as proof that one provider causes higher fares, because the providers may serve different trip mixes, locations, and times.

Fare patterns are closely related to trip distance. The full cleaned dataset has an average total fare of about $27.93, an average trip distance of 4.64 miles, and an average duration of 18.76 minutes. In the sampled trip-level data used for the scatterplot, the correlation between trip miles and total fare is strongly positive. After trimming the most extreme 1% of fare and distance values for visualization, the correlation is about 0.80. This supports the expected relationship that longer trips usually cost more. However, the scatterplot also shows variation among trips with similar distances, which may reflect tolls, tips, airport trips, congestion, time of day, or provider pricing differences.

## Limitations

This analysis is descriptive, not causal. The dashboard can show when demand is highest, where pickups cluster, and how fares relate to distance, but it cannot prove why those patterns happen. For example, higher fares in airport zones may be caused by longer distances, tolls, airport fees, tipping behavior, or a combination of these factors.

The project only uses January 2026 data, so the results should not be generalized to the entire year. Weather, holidays, tourism, special events, school schedules, and transit disruptions could all affect ride-hailing patterns in other months. The dataset also does not include exact pickup coordinates, real-time traffic, surge pricing, rider demographics, or weather conditions.

Another limitation is performance. Most dashboard views use precomputed aggregate tables from the full cleaned dataset, which is appropriate for Streamlit. The fare-distance scatterplot uses a sampled trip-level dataset so the dashboard stays responsive. Because of that, the scatterplot should be interpreted as a sample-based visual rather than a complete display of all 20.8 million cleaned trips.

Overall, the Milestone 3 prototype provides a strong interactive foundation for the final project. It connects the notebook cleaning and EDA work to a dashboard that lets users explore demand timing, pickup geography, provider differences, and fare behavior in a clear and reproducible way.
