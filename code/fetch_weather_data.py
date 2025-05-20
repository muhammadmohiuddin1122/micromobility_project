import requests
import csv
import os
from datetime import datetime, timedelta

# 1. Create full path to ../brussels_weather_data/
script_dir = os.path.dirname(os.path.abspath(__file__))
output_dir = os.path.abspath(os.path.join(script_dir, "..", "brussels_weather_data"))
os.makedirs(output_dir, exist_ok=True)

csv_filename = os.path.join(output_dir, "weather_september_2024.csv")

# 2. Generate timestamps for each day in September 2024 at 11:00 AM
start_date = datetime(2024, 9, 1, 11, 0)
timestamps = [int((start_date + timedelta(days=i)).timestamp()) for i in range(30)]

# 3. CSV headers
fieldnames = [
    'date', 'lat', 'lon',
    'temp', 'feels_like', 'temp_min', 'temp_max',
    'pressure', 'humidity',
    'weather_main', 'weather_desc',
    'wind_speed', 'wind_deg',
    'clouds_all', 'visibility',
    'sunrise', 'sunset'
]

# 4. API setup
url = "https://api.mobilitytwin.brussels/environment/weather"
api_key = "9a2cb3a0c7af0e5689d9f175e330f5ccea5e29dec62076baf1ce96d876451362c505e0f7d2b8cdb0025b9402404712b68d426bcc1652d050b85b5e102693af70"  # Replace with your valid API key

# 5. Make requests and save data to CSV
with open(csv_filename, mode='w', newline='') as csv_file:
    writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
    writer.writeheader()

    for ts in timestamps:
        response = requests.get(url, params={'timestamp': ts}, headers={
            'Authorization': f'Bearer {api_key}'
        })

        print(f"Fetching: {datetime.fromtimestamp(ts)} - Status: {response.status_code}")

        if response.status_code == 200:
            data = response.json()
            try:
                row = {
                    'date': datetime.fromtimestamp(ts).strftime("%Y-%m-%d %H:%M"),
                    'lat': data['coord']['lat'],
                    'lon': data['coord']['lon'],
                    'temp': data['main']['temp'],
                    'feels_like': data['main']['feels_like'],
                    'temp_min': data['main']['temp_min'],
                    'temp_max': data['main']['temp_max'],
                    'pressure': data['main']['pressure'],
                    'humidity': data['main']['humidity'],
                    'weather_main': data['weather'][0]['main'],
                    'weather_desc': data['weather'][0]['description'],
                    'wind_speed': data['wind']['speed'],
                    'wind_deg': data['wind']['deg'],
                    'clouds_all': data['clouds']['all'],
                    'visibility': data['visibility'],
                    'sunrise': datetime.fromtimestamp(data['sys']['sunrise']).strftime('%H:%M'),
                    'sunset': datetime.fromtimestamp(data['sys']['sunset']).strftime('%H:%M')
                }
                writer.writerow(row)
            except (KeyError, IndexError) as e:
                print(f"Missing data on {datetime.fromtimestamp(ts)}: {e}")
        else:
            print(f"Failed to fetch data for {ts}")
