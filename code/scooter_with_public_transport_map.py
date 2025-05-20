import pandas as pd
import folium
import os

# Paths
OUTPUT_DIR = os.path.join("..", "output")
SCOOTER_CSV = os.path.join("..", "brussels_mobility_data", "micromobility_september_2024.csv")
TRANSPORT_CSV = os.path.join("..", "brussels_public_transportation", "public_transportation.csv")

# Grid steps
LAT_STEP = 0.002247
LON_STEP = 0.003561

# === 1. Load scooter data ===
scooter_df = pd.read_csv(SCOOTER_CSV)
scooter_df["timestamp_requested"] = pd.to_datetime(scooter_df["timestamp_requested"])
scooter_df = scooter_df[scooter_df["timestamp_requested"].dt.date == pd.to_datetime("2024-09-01").date()]

coord_pattern = r"POINT \(([\d.]+) ([\d.]+)\)"
coords = scooter_df["geometry"].str.extract(coord_pattern)
scooter_df["lat"] = coords[1].astype(float)
scooter_df["lon"] = coords[0].astype(float)

scooter_df["grid_row"] = ((scooter_df["lat"] - 50.7964) / LAT_STEP).astype(int)
scooter_df["grid_col"] = ((scooter_df["lon"] - 4.3124) / LON_STEP).astype(int)

grid_counts = scooter_df.groupby(["grid_row", "grid_col"]).size().reset_index(name="count")
grid_counts["approx_lat"] = 50.7964 + (grid_counts["grid_row"] + 0.5) * LAT_STEP
grid_counts["approx_lon"] = 4.3124 + (grid_counts["grid_col"] + 0.5) * LON_STEP

# === 2. Load public transportation data ===
transport_df = pd.read_csv(TRANSPORT_CSV, sep=";")
transport_df[['lat', 'lon']] = transport_df['Geo Point'].str.split(',', expand=True).astype(float)

# === 2b. Add grid position to public transport stations ===
transport_df["grid_row"] = ((transport_df["lat"] - 50.7964) / LAT_STEP).astype(int)
transport_df["grid_col"] = ((transport_df["lon"] - 4.3124) / LON_STEP).astype(int)

# Count number of stations by type per grid cell
transport_counts = transport_df.groupby(["grid_row", "grid_col", "Category"]).size().unstack(fill_value=0).reset_index()

# Merge with scooter grid counts
combined_counts = pd.merge(grid_counts, transport_counts, on=["grid_row", "grid_col"], how="left")
combined_counts.fillna(0, inplace=True)

# Optional: Round approx coordinates for better readability
combined_counts["approx_lat"] = combined_counts["approx_lat"].round(6)
combined_counts["approx_lon"] = combined_counts["approx_lon"].round(6)

# Save to CSV inside brussels_public_transportation
transport_output_path = os.path.join("..", "brussels_public_transportation", "grid_transport_counts.csv")
combined_counts.to_csv(transport_output_path, index=False)
print(f"📄 Saved grid-level scooter and transport counts to: {transport_output_path}")


# === 3. Create the map ===
m = folium.Map(location=[50.8503, 4.3517], zoom_start=12, tiles="CartoDB positron")

# === 4. Add scooter demand grid ===
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

# === 5. Add public transport CircleMarkers ===
category_colors = {
    'Bus': 'blue',
    'Tram': 'green',
    'Métro': 'red'
}

for _, row in transport_df.iterrows():
    color = category_colors.get(row['Category'], 'gray')
    folium.CircleMarker(
        location=[row['lat'], row['lon']],
        radius=4,
        color=color,
        fill=True,
        fill_color=color,
        fill_opacity=0.7,
        popup=f"{row['Name']} ({row['Category']})"
    ).add_to(m)

# === 6. Save the final combined map ===
os.makedirs(OUTPUT_DIR, exist_ok=True)
m.save(os.path.join(OUTPUT_DIR, "grid_transportation_with_scooter_map.html"))
print(f"✅ Combined map saved to: {OUTPUT_DIR}/combined_transport_grid_map.html")
