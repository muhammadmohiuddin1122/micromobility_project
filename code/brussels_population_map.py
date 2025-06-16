import pandas as pd
import folium
from geopy.geocoders import Nominatim
import time
import os

# Step 1: Load the CSV file
csv_path = "../brussels_population_data/Brussels_Population_density_by_neighbourhoods.csv"
df = pd.read_csv(csv_path, sep=",")

# Step 2: Set up geocoder
geolocator = Nominatim(user_agent="brussels_mapper")

# Step 3: Geocode each neighborhood name
places = df['Quartier2']
locations = []

for place in places:
    try:
        location = geolocator.geocode(f"{place}, Brussels, Belgium")
        if location:
            print(f"Geocoded: {place} -> ({location.latitude}, {location.longitude})")
            locations.append({
                "name": place,
                "lat": location.latitude,
                "lon": location.longitude
            })
        else:
            print(f"Failed to geocode: {place}")
    except Exception as e:
        print(f"Error for {place}: {e}")
    time.sleep(1)

# Step 4: Create the map centered on Brussels
m = folium.Map(location=[50.8503, 4.3517], zoom_start=13)

# Step 5: Add a marker for each geocoded place
for loc in locations:
    folium.Marker(
        location=[loc["lat"], loc["lon"]],
        popup=loc["name"],
        icon=folium.Icon(color="blue", icon="info-sign")
    ).add_to(m)

# Step 6: Save the map to the output folder
output_path = "../output/brussels_population_map.html"
os.makedirs(os.path.dirname(output_path), exist_ok=True)
m.save(output_path)

print(f"Map saved to {output_path}")