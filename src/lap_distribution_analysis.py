
import pandas as pd
from pathlib import Path

laps = pd.read_csv("data/raw/laps.csv")
drivers = pd.read_csv("data/raw/drivers.csv")

laps["lap_duration"] = pd.to_numeric(
    laps["lap_duration"], errors="coerce"
)

laps["is_pit_out_lap"] = laps["is_pit_out_lap"].astype(bool)

valid = laps[
    (laps["is_pit_out_lap"] == False)
    & laps["lap_duration"].notna()
    & (laps["lap_duration"] > 0)
].copy()

valid = valid.merge(
    drivers[["driver_number", "full_name"]],
    on="driver_number",
    how="left"
)

print("=" * 75)
print("LAP DISTRIBUTION INVESTIGATION")
print("=" * 75)

print("\nVALID LAP COUNT CHECK")
print("All non-pit-out laps with duration:", len(valid))

print("\nLAP TIME DISTRIBUTION BY DRIVER")

summary = valid.groupby(
    ["driver_number", "full_name"]
)["lap_duration"].agg(
    lap_count="count",
    minimum="min",
    q1=lambda x: x.quantile(0.25),
    median="median",
    q3=lambda x: x.quantile(0.75),
    maximum="max",
    mean="mean",
    std="std"
).reset_index()

summary["range_seconds"] = (
    summary["maximum"] - summary["minimum"]
)

print(
    summary.sort_values("median").round(3).to_string(index=False)
)

print("\n" + "=" * 75)
print("VERSTAPPEN LAP-BY-LAP RECORDS")
print("=" * 75)

verstappen = valid[
    valid["driver_number"] == 1
].sort_values("lap_number")

print(
    verstappen[
        [
            "lap_number",
            "date_start",
            "lap_duration",
            "duration_sector_1",
            "duration_sector_2",
            "duration_sector_3",
            "is_pit_out_lap"
        ]
    ].to_string(index=False)
)

print("\n" + "=" * 75)
print("LECLERC LAP-BY-LAP RECORDS")
print("=" * 75)

leclerc = valid[
    valid["driver_number"] == 16
].sort_values("lap_number")

print(
    leclerc[
        [
            "lap_number",
            "date_start",
            "lap_duration",
            "duration_sector_1",
            "duration_sector_2",
            "duration_sector_3",
            "is_pit_out_lap"
        ]
    ].to_string(index=False)
)

print("\n" + "=" * 75)
print("DISTRIBUTION INVESTIGATION COMPLETED")
print("=" * 75)
