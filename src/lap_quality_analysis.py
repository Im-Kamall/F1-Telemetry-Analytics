import pandas as pd
from pathlib import Path

# Project paths
DATA_PATH = Path("data/raw/laps.csv")
OUTPUT_DIR = Path("data/processed")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# Load original lap data
df = pd.read_csv(DATA_PATH)

# Convert relevant columns
df["lap_duration"] = pd.to_numeric(df["lap_duration"], errors="coerce")
df["date_start"] = pd.to_datetime(df["date_start"], errors="coerce", utc=True)

# Classify lap records
df["valid_timed_lap"] = (
    (~df["is_pit_out_lap"])
    & df["lap_duration"].notna()
    & (df["lap_duration"] > 0)
)

# --------------------------------------------------
# 1. LAP DATA QUALITY SUMMARY
# --------------------------------------------------

quality = df.groupby("driver_number").agg(
    total_lap_records=("lap_number", "count"),
    pit_out_laps=("is_pit_out_lap", "sum"),
    missing_lap_durations=("lap_duration", lambda x: x.isna().sum()),
    valid_timed_laps=("valid_timed_lap", "sum")
).reset_index()

quality["invalid_or_excluded_records"] = (
    quality["total_lap_records"] - quality["valid_timed_laps"]
)

print("=" * 75)
print("LAP DATA QUALITY SUMMARY")
print("=" * 75)
print(quality.to_string(index=False))

quality.to_csv(
    OUTPUT_DIR / "lap_quality_summary.csv",
    index=False
)

# --------------------------------------------------
# 2. VALID LAP LEADERBOARD
# --------------------------------------------------

valid_laps = df[df["valid_timed_lap"]].copy()

leaderboard = valid_laps.groupby("driver_number").agg(
    valid_lap_count=("lap_duration", "count"),
    best_lap_seconds=("lap_duration", "min"),
    average_lap_seconds=("lap_duration", "mean"),
    median_lap_seconds=("lap_duration", "median")
).reset_index()

leaderboard = leaderboard.sort_values("best_lap_seconds")

print("\n" + "=" * 75)
print("VALID LAP LEADERBOARD")
print("=" * 75)
print(leaderboard.to_string(index=False))

leaderboard.to_csv(
    OUTPUT_DIR / "valid_lap_leaderboard.csv",
    index=False
)

# --------------------------------------------------
# 3. MISSING DURATION INVESTIGATION
# --------------------------------------------------

print("\n" + "=" * 75)
print("MISSING LAP DURATION INVESTIGATION")
print("=" * 75)

missing_duration = df[df["lap_duration"].isna()]

print("Total missing lap durations:", len(missing_duration))
print(
    "Missing durations on pit-out laps:",
    missing_duration["is_pit_out_lap"].sum()
)
print(
    "Missing durations on non-pit-out laps:",
    (~missing_duration["is_pit_out_lap"]).sum()
)

print("\nNon-pit-out records with missing lap duration:")
print(
    missing_duration[
        ~missing_duration["is_pit_out_lap"]
    ][
        ["driver_number", "lap_number", "date_start", "is_pit_out_lap"]
    ].to_string(index=False)
)

print("\n" + "=" * 75)
print("LAP ANALYSIS COMPLETED")
print("=" * 75)
print("Reports saved in:", OUTPUT_DIR.resolve())
