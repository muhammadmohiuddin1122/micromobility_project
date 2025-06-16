import json
import folium
import os

geojson_path = "../brussels_geofenching/municipalities.geojson"

with open(geojson_path, "r", encoding="utf-8") as f:
    geojson_data = json.load(f)

m = folium.Map(location=[50.8503, 4.3517], zoom_start=12)

def style_function(feature):
    return {
        'fillColor': 'blue',
        'color': 'black',
        'weight': 1,
        'fillOpacity': 0.5,
    }

def highlight_function(feature):
    return {
        'fillColor': 'yellow',
        'color': 'black',
        'weight': 3,
        'fillOpacity': 0.7,
    }

geojson_layer = folium.GeoJson(
    geojson_data,
    style_function=style_function,
    highlight_function=highlight_function,
    tooltip=folium.GeoJsonTooltip(fields=["name_fr"], aliases=["Municipality:"]),
    popup=folium.GeoJsonPopup(fields=["name_fr"], aliases=["Municipality:"]),
).add_to(m)

disable_zoom_js = f"""
function onPopupOpen(e) {{
    e.target._map.scrollWheelZoom.disable();
    e.target._map.doubleClickZoom.disable();
    e.target._map.boxZoom.disable();
}}
function onPopupClose(e) {{
    e.target._map.scrollWheelZoom.enable();
    e.target._map.doubleClickZoom.enable();
    e.target._map.boxZoom.enable();
}}

var layer = {geojson_layer.get_name()};
layer.on('popupopen', onPopupOpen);
layer.on('popupclose', onPopupClose);
"""

m.get_root().html.add_child(folium.Element(f"<script>{disable_zoom_js}</script>"))

output_path = "../brussels_geofenching/brussels_map.html"
os.makedirs(os.path.dirname(output_path), exist_ok=True)
m.save(output_path)

print(f"✅ Map saved to {output_path}")
