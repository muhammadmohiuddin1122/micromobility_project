import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import os

OUTPUT_DIR = os.path.join("..", "output")

# === 1. Load data ===
df = pd.read_csv(os.path.join("..", "brussels_mobility_data", "micromobility_september_2024.csv"))

# === 2. Parse timestamps ===
df["timestamp_requested"] = pd.to_datetime(df["timestamp_requested"])
df["hour"] = df["timestamp_requested"].dt.hour
df["weekday"] = df["timestamp_requested"].dt.day_name()
df["is_weekend"] = df["weekday"].isin(["Saturday", "Sunday"])

# === 3. Extract coordinates from geometry ===
df["lon"] = df["geometry"].str.extract(r"\(([^ ]+)").astype(float)
df["lat"] = df["geometry"].str.extract(r" ([^ ]+)\)").astype(float)

# === 4. Create zones by rounding coordinates ===
df["zone"] = df["lat"].round(3).astype(str) + "," + df["lon"].round(3).astype(str)

# === 5. Plot hourly usage ===
plt.figure(figsize=(10, 5))
df.groupby("hour").size().plot(kind="bar", color="skyblue")
plt.title("Scooter Usage by Hour (September 2024)")
plt.xlabel("Hour of Day")
plt.ylabel("Number of Scooters Observed")
plt.grid(True)
plt.tight_layout()
plt.savefig(os.path.join(OUTPUT_DIR, "september_usage_by_hour.png"))

plt.close()

# === 6. Plot weekday vs weekend usage ===
plt.figure(figsize=(6, 4))
df.groupby("is_weekend").size().plot(kind="bar", color=["green", "orange"])
plt.xticks([0, 1], ["Weekday", "Weekend"], rotation=0)
plt.title("Weekend vs Weekday Usage")
plt.ylabel("Scooters Observed")
plt.grid(True)
plt.tight_layout()
plt.savefig(os.path.join(OUTPUT_DIR, "september_weekend_vs_weekday.png"))

plt.close()

# === 7. Plot usage by weekday ===
plt.figure(figsize=(8, 5))
df.groupby("weekday").size().reindex(
    ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
).plot(kind="bar", color="mediumpurple")
plt.title("Scooter Usage by Day of Week")
plt.xlabel("Day")
plt.ylabel("Scooter Requests")
plt.grid(True)
plt.tight_layout()
plt.savefig(os.path.join(OUTPUT_DIR, "september_usage_by_weekday.png"))

plt.close()

# === 8. Hour vs Day heatmap ===
pivot = df.pivot_table(index="hour", columns="weekday", aggfunc="size", fill_value=0)
pivot = pivot[["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]]
plt.figure(figsize=(10, 6))
sns.heatmap(pivot, cmap="YlGnBu", linewidths=0.5)
plt.title("Hourly Scooter Usage by Day")
plt.ylabel("Hour of Day")
plt.tight_layout()
plt.savefig(os.path.join(OUTPUT_DIR, "september_hourly_heatmap.png"))

plt.close()

# === 9. Zone demand ===
zone_counts = df["zone"].value_counts()
zone_counts.to_csv(os.path.join(OUTPUT_DIR, "september_zone_demand.csv"), header=["count"])

print("\n🔝 Top 10 High-Demand Zones:")
print(zone_counts.head(10))
print("\n🔻 Bottom 10 Low-Demand Zones:")
print(zone_counts.tail(10))

# === 10. Weekend vs Weekday Zone Ratio (visualized) ===
zone_daytype = df.groupby(["zone", "is_weekend"]).size().unstack(fill_value=0)
zone_daytype["weekend_weekday_ratio"] = zone_daytype[True] / (zone_daytype[False] + 1)

# Top 10 weekend-preferred zones
top_weekend = zone_daytype.sort_values("weekend_weekday_ratio", ascending=False).head(10)
plt.figure(figsize=(10, 5))
top_weekend["weekend_weekday_ratio"].plot(kind="bar", color="coral")
plt.title("Top 10 Weekend-Dominant Zones (by Ratio)")
plt.ylabel("Weekend / (Weekday + 1)")
plt.xlabel("Zone")
plt.xticks(rotation=45, ha="right")
plt.tight_layout()
plt.grid(True)
plt.savefig(os.path.join(OUTPUT_DIR, "september_top_weekend_zones.png"))

plt.close()

# Top 10 weekday-preferred zones
top_weekday = zone_daytype.sort_values("weekend_weekday_ratio", ascending=True).head(10)
plt.figure(figsize=(10, 5))
top_weekday["weekend_weekday_ratio"].plot(kind="bar", color="teal")
plt.title("Top 10 Weekday-Dominant Zones (by Ratio)")
plt.ylabel("Weekend / (Weekday + 1)")
plt.xlabel("Zone")
plt.xticks(rotation=45, ha="right")
plt.tight_layout()
plt.grid(True)
plt.savefig(os.path.join(OUTPUT_DIR, "september_top_weekday_zones.png"))

plt.close()
