
import pandas as pd
import numpy as np
from pathlib import Path

# ---------------------------------------------------------
# CONFIGURATION
# ---------------------------------------------------------

LAPS_PATH = Path("data/raw/laps.csv")
DRIVERS_PATH = Path("data/raw/drivers.csv")
OUTPUT_DIR = Path("data/processed")

OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# ---------------------------------------------------------
# LOAD DATA
# ---------------------------------------------------------

print("=" * 75)
print("F1 LAP PERFORMANCE AND CONSISTENCY ANALYSIS")
print("=" * 75)

laps = pd.read_csv(LAPS_PATH)
drivers = pd.read_csv(DRIVERS_PATH)

laps["lap_duration"] = pd.to_numeric(
    laps["lap_duration"], errors="coerce"
)

sector_columns = [
    "duration_sector_1",
    "duration_sector_2",
    "duration_sector_3"
]

for column in sector_columns:
    laps[column] = pd.to_numeric(laps[column], errors="coerce")

# ---------------------------------------------------------
# FILTER VALID TIMED LAPS
# ---------------------------------------------------------

valid_laps = laps[
    (laps["is_pit_out_lap"] == False)
    & (laps["lap_duration"].notna())
    & (laps["lap_duration"] > 0)
].copy()

valid_laps = valid_laps.merge(
    drivers[["driver_number", "full_name", "team_name"]],
    on="driver_number",
    how="left"
)

print(f"\nTotal lap records: {len(laps)}")
print(f"Valid timed laps: {len(valid_laps)}")
print(f"Drivers included: {valid_laps['driver_number'].nunique()}")

# ---------------------------------------------------------
# DRIVER LAP PERFORMANCE
# ---------------------------------------------------------

performance = valid_laps.groupby(
    ["driver_number", "full_name", "team_name"]
).agg(
    valid_lap_count=("lap_duration", "count"),
    best_lap_seconds=("lap_duration", "min"),
    average_lap_seconds=("lap_duration", "mean"),
    median_lap_seconds=("lap_duration", "median"),
    lap_time_std=("lap_duration", "std")
).reset_index()

# ---------------------------------------------------------
# TOP THREE LAP AVERAGE
# ---------------------------------------------------------

top_three = (
    valid_laps.sort_values("lap_duration")
    .groupby("driver_number")
    .head(3)
    .groupby("driver_number")["lap_duration"]
    .agg(top_three_average="mean", top_three_laps="count")
    .reset_index()
)

performance = performance.merge(
    top_three,
    on="driver_number",
    how="left"
)

# ---------------------------------------------------------
# SECTOR PERFORMANCE
# ---------------------------------------------------------

sector_summary = valid_laps.groupby(
    ["driver_number", "full_name", "team_name"]
).agg(
    avg_sector_1=("duration_sector_1", "mean"),
    avg_sector_2=("duration_sector_2", "mean"),
    avg_sector_3=("duration_sector_3", "mean")
).reset_index()

performance = performance.merge(
    sector_summary,
    on=["driver_number", "full_name", "team_name"],
    how="left"
)

# ---------------------------------------------------------
# RANKINGS
# ---------------------------------------------------------

performance = performance.sort_values(
    "best_lap_seconds"
).reset_index(drop=True)

performance.insert(
    0,
    "best_lap_rank",
    range(1, len(performance) + 1)
)

performance["consistency_rank"] = (
    performance["lap_time_std"]
    .rank(method="min", ascending=True)
)

# ---------------------------------------------------------
# DISPLAY RESULTS
# ---------------------------------------------------------

print("\n" + "=" * 75)
print("BEST LAP PERFORMANCE")
print("=" * 75)

print(
    performance[
        [
            "best_lap_rank",
            "driver_number",
            "full_name",
            "valid_lap_count",
            "best_lap_seconds",
            "top_three_average",
            "lap_time_std"
        ]
    ].round(3).to_string(index=False)
)

print("\n" + "=" * 75)
print("SECTOR PERFORMANCE")
print("=" * 75)

print(
    performance[
        [
            "driver_number",
            "full_name",
            "avg_sector_1",
            "avg_sector_2",
            "avg_sector_3"
        ]
    ].round(3).to_string(index=False)
)

print("\n" + "=" * 75)
print("LAP TIME CONSISTENCY")
print("=" * 75)

print(
    performance[
        [
            "driver_number",
            "full_name",
            "valid_lap_count",
            "lap_time_std",
            "consistency_rank"
        ]
    ].sort_values("consistency_rank").round(3).to_string(index=False)
)

# ---------------------------------------------------------
# SAVE REPORTS
# ---------------------------------------------------------

performance.to_csv(
    OUTPUT_DIR / "lap_performance_summary.csv",
    index=False
)

valid_laps.to_csv(
    OUTPUT_DIR / "valid_laps_detailed.csv",
    index=False
)

print("\n" + "=" * 75)
print("LAP PERFORMANCE ANALYSIS COMPLETED")
print("=" * 75)

print("Saved: data/processed/lap_performance_summary.csv")
print("Saved: data/processed/valid_laps_detailed.csv")
