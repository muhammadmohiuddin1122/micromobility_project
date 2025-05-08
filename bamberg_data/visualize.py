import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# Load cleaned data
df = pd.read_csv("bamberg_zeus_data.csv")

# 1. Time-of-Day Usage (Line Chart)
# ------------------------------------------
# Define the correct time order
time_order = ["9:00:00 AM", "1:00:00 PM", "5:00:00 PM", "9:00:00 PM"]

# Convert 'time' to a categorical variable with defined order
df["time"] = pd.Categorical(df["time"], categories=time_order, ordered=True)

# Group and sort by the custom time order
time_charge = df.groupby("time", observed=True)["Charge in Km"].mean().reset_index()
time_charge = time_charge.set_index("time").reindex(time_order)

# Plot
plt.figure(figsize=(12, 6))
time_charge.plot(
    kind="line",
    marker="o",
    color="navy",
    linestyle="--",
    legend=False
)
plt.title("Average Charge Level by Time of Day", fontsize=14)
plt.xlabel("Time of Day", fontsize=12)
plt.ylabel("Average Charge (Km)", fontsize=12)
plt.grid(True, alpha=0.3)
plt.xticks(rotation=45)
plt.tight_layout()
plt.savefig("time_usage.png", dpi=300)
plt.show()
# ------------------------------------------
# 2. Location Popularity (Bar Chart)
# Shows which locations have the most usage
# ------------------------------------------
plt.figure(figsize=(12, 6))
location_usage = df.groupby("Location")["Charge in Km"].mean().sort_values()
location_usage.plot(kind="barh", color="teal")  # Horizontal bar chart
plt.title("Most Active Locations (Lower Charge = More Usage)", fontsize=14)
plt.xlabel("Average Charge (Km)", fontsize=12)
plt.ylabel("Location", fontsize=12)
plt.grid(axis="x", alpha=0.3)
plt.tight_layout()
plt.savefig("location_popularity.png", dpi=300)
plt.show()

# ------------------------------------------
# 3. Discount Impact (Box Plot)
# Compares charge levels for discounted vs non-discounted rides
# ------------------------------------------
plt.figure(figsize=(10, 6))
df["Discount Status"] = df["Discount"].apply(lambda x: "Discounted" if x == -20.0 else "Regular")
df.boxplot(
    column="Charge in Km",
    by="Discount Status",
    patch_artist=True,
    boxprops=dict(facecolor="lightblue"),
    medianprops=dict(color="red")
)
plt.title("Charge Levels: Discounted vs Regular Rides", fontsize=14)
plt.suptitle("")
plt.xlabel("Discount Status", fontsize=12)
plt.ylabel("Charge in Km", fontsize=12)
plt.tight_layout()
plt.savefig("discount_impact.png", dpi=300)
plt.show()

# ------------------------------------------
# 4. Zone Distribution (Pie Chart)
# Shows distribution of Bonus/Parking/Service zones
# ------------------------------------------
zone_counts = df[["Bonus zone", "No parking zone", "Service fee"]].eq("Yes").sum()
plt.figure(figsize=(8, 8))
plt.pie(
    zone_counts,
    labels=["Bonus Zone", "No Parking Zone", "Service Fee Active"],
    autopct="%1.1f%%",
    colors=["#ff9999","#66b3ff","#99ff99"],
    explode=(0.1, 0, 0),  # Highlight Bonus Zone
    shadow=True
)
plt.title("Distribution of Special Zones/Features", fontsize=14)
plt.savefig("zone_distribution.png", dpi=300)
plt.show()

# Scooter Utilization Distribution

plt.figure(figsize=(12, 6))
plt.hist(df["Charge in Km"], bins=20, color="orange", edgecolor="black")
plt.title("Distribution of Scooter Charge Levels", fontsize=14)
plt.xlabel("Charge in Km", fontsize=12)
plt.ylabel("Frequency", fontsize=12)
plt.grid(True, alpha=0.3)
plt.tight_layout()
plt.savefig("charge_distribution.png", dpi=300)
plt.show()

# Discount Effectiveness
# Create a "Discount Applied" column
df["Discount Applied"] = df["Discount"].apply(lambda x: "Yes" if x == -20.0 else "No")

# Group by Location and Discount
discount_usage = df.groupby(["Location", "Discount Applied"])["Charge in Km"].mean().unstack()

# Plot
discount_usage.plot(kind="bar", figsize=(14, 7))
plt.title("Discount Impact by Location", fontsize=14)
plt.xlabel("Location", fontsize=12)
plt.ylabel("Avg Charge (Km)", fontsize=12)
plt.xticks(rotation=45)
plt.grid(axis="y", alpha=0.3)
plt.tight_layout()
plt.savefig("discount_by_location.png", dpi=300)
plt.show()

# Correlation Matrix

# Convert "Yes"/"No" to 1/0
df_numeric = df.replace({"Yes": 1, "No": 0})

# Calculate correlations
corr = df_numeric[["Charge in Km", "Discount", "Service fee"]].corr()

# Plot
plt.figure(figsize=(10, 6))
sns.heatmap(corr, annot=True, cmap="coolwarm", vmin=-1, vmax=1)
plt.title("Correlation Matrix", fontsize=14)
plt.tight_layout()
plt.savefig("correlation_matrix.png", dpi=300)
plt.show()

#  Battery Health Analysis
plt.figure(figsize=(14, 7))
sns.scatterplot(
    data=df,
    x="Scooter Id",
    y="Charge in Km",
    hue="Location",
    palette="viridis",
    alpha=0.7
)
plt.title("Scooter Charge Levels by ID", fontsize=14)
plt.xlabel("Scooter ID", fontsize=12)
plt.ylabel("Charge in Km", fontsize=12)
plt.xticks(rotation=90)
plt.grid(True, alpha=0.3)
plt.tight_layout()
plt.savefig("scooter_health.png", dpi=300)
plt.show()

# Service Fee Activation

service_counts = df.groupby(["Location", "Service fee"]).size().unstack()
service_counts.plot(kind="bar", stacked=True, figsize=(12, 6))
plt.title("Service Fee Activation by Location", fontsize=14)
plt.xlabel("Location", fontsize=12)
plt.ylabel("Count", fontsize=12)
plt.xticks(rotation=45)
plt.grid(axis="y", alpha=0.3)
plt.tight_layout()
plt.savefig("service_fee_activation.png", dpi=300)
plt.show()

# Daily Trends (Usage Over Days)
# Extract day of the week from 'date'
df["date"] = pd.to_datetime(df["date"])
df["Day_of_Week"] = df["date"].dt.day_name()

# Group by day and calculate average charge
daily_charge = df.groupby("Day_of_Week")["Charge in Km"].mean().reindex([
    "Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"
])

# Plot
plt.figure(figsize=(12, 6))
daily_charge.plot(kind="line", marker="o", color="purple")
plt.title("Average Charge by Day of the Week", fontsize=14)
plt.xlabel("Day of the Week", fontsize=12)
plt.ylabel("Avg Charge (Km)", fontsize=12)
plt.grid(True, alpha=0.3)
plt.tight_layout()
plt.savefig("daily_trends.png", dpi=300)
plt.show()