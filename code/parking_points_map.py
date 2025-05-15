import pandas as pd
import folium
import os
import numpy as np

from math import radians, cos, sin, asin, sqrt

# Configuration
OUTPUT_DIR = os.path.join("..", "output")
DATA_DIR = os.path.join("..", "brussels_mobility_data")
PARKING_CSV = os.path.join(DATA_DIR, "brussels_point_of_parkings.csv")
SCOOTER_CSV = os.path.join(DATA_DIR, "micromobility_september_2024.csv")

# Distance threshold (in meters)
DISTANCE_THRESHOLD_METERS = 100


def haversine(lat1, lon1, lat2, lon2):
    """Calculate the great-circle distance between two points on the Earth (in meters)."""
    R = 6371000  # Earth radius in meters
    lat1, lon1, lat2, lon2 = map(radians, [lat1, lon1, lat2, lon2])
    dlat = lat2 - lat1
    dlon = lon2 - lon1
    a = sin(dlat / 2) ** 2 + cos(lat1) * cos(lat2) * sin(dlon / 2) ** 2
    return 2 * R * asin(sqrt(a))


def main():
    # === 1. Load both datasets ===
    parking_df = pd.read_csv(PARKING_CSV)
    scooter_df = pd.read_csv(SCOOTER_CSV)

    # Filter scooter data to one day
    scooter_df["timestamp_requested"] = pd.to_datetime(scooter_df["timestamp_requested"])
    scooter_df = scooter_df[scooter_df["timestamp_requested"].dt.date == pd.to_datetime("2024-09-01").date()]

    # Extract scooter coordinates
    coord_pattern = r"POINT \(([\d.]+) ([\d.]+)\)"
    coords = scooter_df["geometry"].str.extract(coord_pattern)
    scooter_df["lat"] = coords[1].astype(float)
    scooter_df["lon"] = coords[0].astype(float)

    # Extract parking coordinates
    coord_split = parking_df["Geographical coordinates"].str.split(",", expand=True)
    parking_df["lat"] = coord_split[0].astype(float)
    parking_df["lon"] = coord_split[1].astype(float)

    # === 2. Count scooters within 100m of each parking point ===
    scooter_counts = []
    for _, park in parking_df.iterrows():
        count = scooter_df.apply(
            lambda s: haversine(park["lat"], park["lon"], s["lat"], s["lon"]) <= DISTANCE_THRESHOLD_METERS,
            axis=1
        ).sum()
        scooter_counts.append(count)

    parking_df["scooter_count"] = scooter_counts

    # === 2b. Identify high and low-demand zones ===
    high_demand = parking_df.sort_values("scooter_count", ascending=False).head(9)
    low_demand = parking_df.sort_values("scooter_count").head(9)

    print("\n🔝 Top 9 High-Demand Parking Zones:")
    for _, row in high_demand.iterrows():
        print(f"{row['Name']} - {row['Address']}, {row['Municipality']}: {row['scooter_count']} scooters nearby")

    print("\n🔻 Bottom 9 Low-Demand Parking Zones:")
    for _, row in low_demand.iterrows():
        print(f"{row['Name']} - {row['Address']}, {row['Municipality']}: {row['scooter_count']} scooters nearby")

    # === 3. Create map ===
    m = folium.Map(location=[50.8508, 4.3517], zoom_start=13, tiles="CartoDB positron")

    # === 4. Add parking zones with scooter counts ===
    LAT_DELTA = 0.0009
    LON_DELTA = 0.0014

    for _, row in parking_df.iterrows():
        popup_text = f"""
        <b>Name:</b> {row['Name']}<br>
        <b>Status:</b> {row['Status']}<br>
        <b>Address:</b> {row['Address']}<br>
        <b>Municipality:</b> {row['Municipality']}<br>
        <b>Total Hour:</b> {row['Total hour']}<br>
        <b>Scooters nearby (100m):</b> {row['scooter_count']}<br>
        <b>Google Maps:</b> <a href="{row['Google Maps']}" target="_blank">View</a><br>
        """

        # Color based on demand
        color = (
            "red" if row["scooter_count"] >= 100 else
            "orange" if row["scooter_count"] >= 50 else
            "green" if row["scooter_count"] > 0 else
            "gray"
        )

        bounds = [
            [row["lat"] - LAT_DELTA / 2, row["lon"] - LON_DELTA / 2],
            [row["lat"] + LAT_DELTA / 2, row["lon"] + LON_DELTA / 2]
        ]

        folium.Rectangle(
            bounds=bounds,
            color=color,
            fill=True,
            fill_opacity=0.4,
            popup=folium.Popup(popup_text, max_width=300)
        ).add_to(m)

    # === 5. Save output ===
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    output_path = os.path.join(OUTPUT_DIR, "parking_with_scooters_map.html")
    m.save(output_path)
    print(f"\n✅ Combined parking/scooter map saved to: {output_path}")


if __name__ == "__main__":
    main()
