import pandas as pd
import folium
import os

# Load dataset
csv_path = "../brussels_public_transportation/public_transportation.csv"
df = pd.read_csv(csv_path, sep=";")

# Extract lat/lon
df[['lat', 'lon']] = df['Geo Point'].str.split(',', expand=True).astype(float)

# Create map
m = folium.Map(location=[50.8503, 4.3517], zoom_start=12)

# Define color per category
category_colors = {
    'Bus': 'blue',
    'Tram': 'green',
    'Métro': 'red'
}

# Add lightweight circle markers
for _, row in df.iterrows():
    color = category_colors.get(row['Category'], 'gray')
    folium.CircleMarker(
        location=[row['lat'], row['lon']],
        radius=4,  # smaller marker
        color=color,
        fill=True,
        fill_color=color,
        fill_opacity=0.7,
        popup=f"{row['Name']} ({row['Category']})"
    ).add_to(m)

# Save map
output_path = "../output/brussels_transport_map.html"
os.makedirs(os.path.dirname(output_path), exist_ok=True)
m.save(output_path)

print(f"Map saved to {output_path}")
