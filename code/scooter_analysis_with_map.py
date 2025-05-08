import pandas as pd
import folium
import os

# Configuration
OUTPUT_DIR = os.path.join("..", "output")
DATA_DIR = os.path.join("..", "brussels_mobility_data")
INPUT_CSV = os.path.join(DATA_DIR, "micromobility_september_2024.csv")

# Brussels-specific grid parameters (250m cells)
LAT_STEP = 0.002247  # Exact 250m north-south at 50.85°N
LON_STEP = 0.003561  # Exact 250m east-west at 50.85°N


def main():
    # === 1. Load and filter data ===
    df = pd.read_csv(INPUT_CSV)
    df["timestamp_requested"] = pd.to_datetime(df["timestamp_requested"])
    df = df[df["timestamp_requested"].dt.date == pd.to_datetime("2024-09-01").date()]

    # === 2. Extract coordinates ===
    coord_pattern = r"POINT \(([\d.]+) ([\d.]+)\)"
    coords = df["geometry"].str.extract(coord_pattern)
    df["lat"] = coords[1].astype(float)
    df["lon"] = coords[0].astype(float)

    # === 3. Create grid system ===
    df["grid_row"] = ((df["lat"] - 50.7964) / LAT_STEP).astype(int)
    df["grid_col"] = ((df["lon"] - 4.3124) / LON_STEP).astype(int)

    # === 4. Analyze demand ===
    grid_counts = df.groupby(["grid_row", "grid_col"]).size().reset_index(name="count")

    # Add approximate coordinates for readability
    grid_counts["approx_lat"] = 50.7964 + (grid_counts["grid_row"] + 0.5) * LAT_STEP
    grid_counts["approx_lon"] = 4.3124 + (grid_counts["grid_col"] + 0.5) * LON_STEP

    # === 5. Print demand analysis ===
    print("\n🔝 Top 10 High-Demand Zones:")
    top_zones = grid_counts.sort_values("count", ascending=False).head(10)
    for _, zone in top_zones.iterrows():
        print(f"Grid [{zone['grid_row']},{zone['grid_col']}]")
        print(f"≈ Location: {zone['approx_lat']:.5f}, {zone['approx_lon']:.5f}")
        print(f"Scooters: {zone['count']}\n")

    print("\n🔻 Bottom 10 Low-Demand Zones:")
    bottom_zones = grid_counts.sort_values("count").head(10)
    for _, zone in bottom_zones.iterrows():
        print(f"Grid [{zone['grid_row']},{zone['grid_col']}]")
        print(f"≈ Location: {zone['approx_lat']:.5f}, {zone['approx_lon']:.5f}")
        print(f"Scooters: {zone['count']}\n")

    # === 6. Generate optimized map ===
    m = folium.Map(location=[50.8508, 4.3517], zoom_start=13, tiles="CartoDB positron")

    # Batch add grid cells
    for _, row in grid_counts.iterrows():
        lat_min = 50.7964 + row["grid_row"] * LAT_STEP
        lat_max = lat_min + LAT_STEP
        lon_min = 4.3124 + row["grid_col"] * LON_STEP
        lon_max = lon_min + LON_STEP

        folium.Rectangle(
            bounds=[[lat_min, lon_min], [lat_max, lon_max]],
            color="red" if row["count"] >= 100 else "orange" if row["count"] >= 50 else "green",
            fill=True,
            fill_opacity=0.6,
            popup=f"Scooters: {row['count']}"
        ).add_to(m)

    # === 7. Save outputs ===
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    grid_counts.to_csv(os.path.join(OUTPUT_DIR, "grid_demand.csv"), index=False)
    m.save(os.path.join(OUTPUT_DIR, "optimized_scooter_map.html"))

    print(f"\n✅ Analysis complete. Map saved to {OUTPUT_DIR}")


if __name__ == "__main__":
    main()