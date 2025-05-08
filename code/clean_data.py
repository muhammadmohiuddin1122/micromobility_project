import pandas as pd

# Configuration
INPUT_CSV = 'micromobility_september_2024.csv'
CLEANED_CSV = 'cleaned_micromobility_september_2024.csv'
HOURLY_CSV = 'micromobility_september_2024_hour_00.csv'  # New file for hourly data
COLUMNS_TO_REMOVE = ['pricing_plan_id', 'rental_uris.android', 'rental_uris.ios']
TARGET_HOUR = '2024-09-01 00:00:00'  # Adjust this to your desired hour


def clean_and_filter_data(input_file, cleaned_file, hourly_file):
    try:
        # Read CSV with optimized parsing
        df = pd.read_csv(input_file, parse_dates=['timestamp_requested'])

        # Remove specified columns
        df = df.drop(columns=[c for c in COLUMNS_TO_REMOVE if c in df.columns], errors='ignore')

        # Remove completely empty columns
        df = df.dropna(axis=1, how='all')

        # Save cleaned data
        df.to_csv(cleaned_file, index=False)
        print(f"Cleaned data saved to {cleaned_file}")

        # Filter for target hour
        if 'timestamp_requested' not in df.columns:
            raise ValueError("Timestamp column missing!")

        # Create hourly filter
        target_time = pd.to_datetime(TARGET_HOUR)
        hourly_data = df[df['timestamp_requested'].dt.floor('H') == target_time]

        # Save hourly data
        hourly_data.to_csv(hourly_file, index=False)
        print(f"Hourly data ({TARGET_HOUR}) saved to {hourly_file}")
        print(f"Found {len(hourly_data)} records in this hour")

    except Exception as e:
        print(f"Error: {str(e)}")


if __name__ == "__main__":
    clean_and_filter_data(INPUT_CSV, CLEANED_CSV, HOURLY_CSV)