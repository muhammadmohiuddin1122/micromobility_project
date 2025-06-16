import pandas as pd
import numpy as np
import geopandas as gpd
from shapely.geometry import Point
import os

# === CONFIGURATION ===
DATA_DIR = os.path.join("..", "brussels_mobility_data")
INPUT_CSV = os.path.join(DATA_DIR, "micromobility_september_2024.csv")
GEOJSON_PATH = os.path.join("..", "brussels_geofenching", "municipalities.geojson")
OUTPUT_DIR = DATA_DIR  # Save output CSV in the same folder as input CSV

LAT_STEP = 0.002247
LON_STEP = 0.003561
LAT_ORIGIN = 50.7964
LON_ORIGIN = 4.3124

# === LOAD SCOOTER DATA ===
df = pd.read_csv(INPUT_CSV)
df["timestamp_requested"] = pd.to_datetime(df["timestamp_requested"])
df["hour"] = df["timestamp_requested"].dt.floor('h')

# === EXTRACT COORDINATES ===
coord_pattern = r"POINT \(([\d.]+) ([\d.]+)\)"
coords = df["geometry"].str.extract(coord_pattern)
df["lat"] = coords[1].astype(float)
df["lon"] = coords[0].astype(float)

# === DROP ROWS WITH MISSING COORDINATES ===
df = df.dropna(subset=["lat", "lon"])

# === ASSIGN TO GRID (using np.floor for correct binning) ===
df["grid_row"] = np.floor((df["lat"] - LAT_ORIGIN) / LAT_STEP).astype(int)
df["grid_col"] = np.floor((df["lon"] - LON_ORIGIN) / LON_STEP).astype(int)

# === CREATE GRID IDENTIFIER ===
df["grid_id"] = "Grid: (" + df["grid_row"].astype(str) + ", " + df["grid_col"].astype(str) + ")"

# === COMPUTE GRID CENTER POINTS ===
df["grid_center_lat"] = LAT_ORIGIN + (df["grid_row"] + 0.5) * LAT_STEP
df["grid_center_lon"] = LON_ORIGIN + (df["grid_col"] + 0.5) * LON_STEP

# === CONVERT TO GeoDataFrame WITH CENTER POINT GEOMETRIES ===
geometry = [Point(xy) for xy in zip(df["grid_center_lon"], df["grid_center_lat"])]
gdf = gpd.GeoDataFrame(df, geometry=geometry, crs="EPSG:4326")

# === LOAD MUNICIPALITY POLYGONS ===
muni_gdf = gpd.read_file(GEOJSON_PATH).to_crs("EPSG:4326")

# === SPATIAL JOIN: ASSIGN MUNICIPALITY TO EACH GRID CENTER POINT ===
# Use a left join so that points outside any polygon remain in gdf
gdf = gpd.sjoin(gdf, muni_gdf[["geometry", "name_fr"]], how="left", predicate="within")

# === ASSIGN MUNICIPALITY COLUMN (empty string if outside any municipality) ===
gdf["municipality"] = gdf["name_fr"].fillna("")

# === GROUP DATA: HOURLY SCOOTER COUNT PER GRID + MUNICIPALITY ===
grouped = (
    gdf
    .groupby(["hour", "grid_id", "municipality"])
    .size()
    .reset_index(name="scooter_count")
)

# === SAVE TO CSV IN brussels_mobility_data FOLDER ===
output_path = os.path.join(OUTPUT_DIR, "hourly_grid_scooter_counts_with_municipality.csv")
grouped.to_csv(output_path, index=False, columns=["grid_id", "hour", "municipality", "scooter_count"])

print(f"✅ File saved to: {output_path}")
