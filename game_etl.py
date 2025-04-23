import pandas as pd
from sqlalchemy import create_engine
from dotenv import load_dotenv 
import os

# Load DB credentials
load_dotenv()
DB_URL = os.getenv("DB_URL")



# Step 1: Extract
df = pd.read_csv("SteamCharts.csv", encoding="ISO-8859-1")
print("✅ Loaded:", df.shape)

# Step 2: Transform
# Create a datetime column from year and month
df["date"] = pd.to_datetime(df["year"].astype(str) + "-" + df["month"].astype(str) + "-01")

# Clean column names
df.columns = [c.strip().lower().replace(" ", "_") for c in df.columns]

# Drop game names with too many unicode patterns
df = df[~df['gamename'].str.contains('<U\+', regex=True)]

# Sort by date
df = df.sort_values("date")

# Create a derived metric: player drop ratio
df["drop_ratio"] = -df["gain"] / df["avg"]
df["drop_ratio"] = df["drop_ratio"].fillna(0).round(2)

# Step 3: Save to Parquet
df.to_parquet("cleaned_steamcharts.parquet", index=False)
print("✅ Saved to Parquet")

# Step 4: Load to PostgreSQL
engine = create_engine(DB_URL)
df.to_sql("steam_charts", engine, if_exists="replace", index=False)
print("✅ Loaded to PostgreSQL")
