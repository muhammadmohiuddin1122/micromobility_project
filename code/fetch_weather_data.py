import requests
import csv
import os
from datetime import datetime, timedelta, timezone

# Set up the output folder path relative to the script's parent directory
script_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.abspath(os.path.join(script_dir, '..'))
output_folder = os.path.join(project_root, 'brussels_weather_data')
os.makedirs(output_folder, exist_ok=True)

# API endpoint and token
url = "https://api.mobilitytwin.brussels/environment/weather"
headers = {
    'Authorization': 'Bearer 69dcb55e29bf5e591c447540f8145a55d2e7f88f9faafc90db36203240b31b09bf87162cb197e8d9ae9f8183b794071d8b5664dd4817f1453b7d9e4a1d864f94'
}

# Generate hourly timestamps for September 2024 (UTC time)
start_date = datetime(2024, 9, 1, 0, 0, tzinfo=timezone.utc)
end_date = datetime(2024, 9, 30, 23, 0, tzinfo=timezone.utc)

timestamps = []
current = start_date
while current <= end_date:
    timestamps.append(int(current.timestamp()))
    current += timedelta(hours=1)

# Fetch data
all_records = []

for ts in timestamps:
    response = requests.get(url, params={'timestamp': ts}, headers=headers)
    print(f"Timestamp {ts} → Status {response.status_code}")

    if response.status_code == 200:
        data = response.json()
        all_records.append(data)
    else:
        print(f"Error for timestamp {ts}")

# Flatten function
def flatten_weather(record):
    return {
        'timestamp': datetime.utcfromtimestamp(record['dt']).strftime('%Y-%m-%d %H:%M:%S'),
        'lon': record['coord']['lon'],
        'lat': record['coord']['lat'],
        'name': record['name'],
        'country': record['sys']['country'],
        'timezone': record['timezone'],
        'temp': record['main']['temp'],
        'feels_like': record['main']['feels_like'],
        'temp_min': record['main']['temp_min'],
        'temp_max': record['main']['temp_max'],
        'pressure': record['main']['pressure'],
        'humidity': record['main']['humidity'],
        'visibility': record.get('visibility'),
        'wind_speed': record['wind'].get('speed'),
        'wind_deg': record['wind'].get('deg'),
        'wind_gust': record['wind'].get('gust'),
        'clouds_all': record['clouds']['all'],
        'rain_1h': record.get('rain', {}).get('1h'),
        'weather_id': record['weather'][0]['id'],
        'weather_main': record['weather'][0]['main'],
        'weather_description': record['weather'][0]['description'],
        'sunrise': datetime.utcfromtimestamp(record['sys']['sunrise']).strftime('%Y-%m-%d %H:%M:%S'),
        'sunset': datetime.utcfromtimestamp(record['sys']['sunset']).strftime('%Y-%m-%d %H:%M:%S'),
    }

# Save to CSV
csv_path = os.path.join(output_folder, 'brussels_weather_hourly_september_2024.csv')
with open(csv_path, 'w', newline='', encoding='utf-8') as f:
    writer = csv.DictWriter(f, fieldnames=flatten_weather(all_records[0]).keys())
    writer.writeheader()
    for record in all_records:
        writer.writerow(flatten_weather(record))

print(f"\n✅ Saved hourly weather data to {csv_path}")
