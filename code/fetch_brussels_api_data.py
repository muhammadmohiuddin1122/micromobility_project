import requests
import geopandas as gpd
import pandas as pd
from datetime import datetime, timedelta
import time
import os

# Configuration
API_KEY = "9a2cb3a0c7af0e5689d9f175e330f5ccea5e29dec62076baf1ce96d876451362c505e0f7d2b8cdb0025b9402404712b68d426bcc1652d050b85b5e102693af70"  # Replace with your valid API key
OUTPUT_DIR = os.path.join("..", "brussels_mobility_data")
MERGED_FILENAME = "micromobility_october_2024.csv"
PROVIDERS = ["lime", "dott", "pony", "bolt"]

# Time range: Entire month of September 2024
START_TIME = datetime(2024, 10, 1, 0, 0)
END_TIME = datetime(2024, 10, 2, 0, 0)
TIME_INTERVAL = timedelta(hours=1)

def fetch_provider_data(provider, timestamp):
    """Fetch data from the API for a single provider at a given timestamp."""
    url = f"https://api.mobilitytwin.brussels/{provider}/vehicle-position?timestamp={int(timestamp.timestamp())}"
    try:
        response = requests.get(
            url,
            headers={"Authorization": f"Bearer {API_KEY}"},
            timeout=10
        )
        response.raise_for_status()
        data = response.json()
        gdf = gpd.GeoDataFrame.from_features(data["features"])
        gdf["provider"] = provider
        gdf["timestamp_requested"] = timestamp.isoformat()
        return gdf
    except Exception as e:
        print(f"❌ Error fetching data for {provider} at {timestamp}: {e}")
        return None

def main():
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    all_data = []  # To collect all rows for the entire month

    current_time = START_TIME
    while current_time < END_TIME:
        print(f"\n📅 Fetching data for: {current_time}")
        for provider in PROVIDERS:
            print(f"   → {provider}")
            gdf = fetch_provider_data(provider, current_time)
            if gdf is not None and not gdf.empty:
                all_data.append(gdf)

        current_time += TIME_INTERVAL
        time.sleep(1)  # Gentle delay to avoid hitting API rate limits

    if all_data:
        combined_df = pd.concat(all_data, ignore_index=True)
        merged_path = os.path.join(OUTPUT_DIR, MERGED_FILENAME)
        combined_df.to_csv(merged_path, index=False)
        print(f"\n✅ All data saved to: {merged_path}")
    else:
        print("⚠️ No data was collected.")

if __name__ == "__main__":
    main()
