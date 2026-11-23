
import pandas as pd
from pathlib import Path

# --------------------------------------------------
# CONFIGURATION
# --------------------------------------------------

OUTPUT_DIR = Path("data/processed")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# --------------------------------------------------
# LOAD DATA
# --------------------------------------------------

laps = pd.read_csv("data/raw/laps.csv")
drivers = pd.read_csv("data/raw/drivers.csv")

# --------------------------------------------------
# DATA TYPE CONVERSION
# --------------------------------------------------

numeric_columns = [
    "lap_duration",
    "duration_sector_1",
    "duration_sector_2",
    "duration_sector_3"
]

for column in numeric_columns:
    laps[column] = pd.to_numeric(
        laps[column],
        errors="coerce"
    )

laps["date_start"] = pd.to_datetime(
    laps["date_start"],
    errors="coerce",
    utc=True
)

# --------------------------------------------------
# LAP QUALITY FLAGS
# --------------------------------------------------

laps["is_pit_out_lap"] = (
    laps["is_pit_out_lap"]
    .fillna(False)
    .astype(bool)
)

laps["valid_timed_lap"] = (
    (~laps["is_pit_out_lap"])
    & laps["lap_duration"].notna()
    & (laps["lap_duration"] > 0)
)

sector_columns = [
    "duration_sector_1",
    "duration_sector_2",
    "duration_sector_3"
]

laps["missing_sector_count"] = (
    laps[sector_columns].isna().sum(axis=1)
)

laps["all_sectors_present"] = (
    laps["missing_sector_count"] == 0
)

# --------------------------------------------------
# SECTOR SUM COMPARISON
# --------------------------------------------------

laps["sector_sum"] = laps[sector_columns].sum(
    axis=1,
    min_count=3
)

laps["sector_sum_minus_lap_duration"] = (
    laps["sector_sum"] - laps["lap_duration"]
)

# --------------------------------------------------
# NEAR-BEST LAP FLAGS
# --------------------------------------------------

valid = laps[laps["valid_timed_lap"]].copy()

best_times = (
    valid.groupby("driver_number")["lap_duration"]
    .min()
    .rename("best_lap_seconds")
)

laps = laps.merge(
    best_times,
    on="driver_number",
    how="left"
)

laps["near_best_2pct"] = (
    laps["valid_timed_lap"]
    & (
        laps["lap_duration"]
        <= laps["best_lap_seconds"] * 1.02
    )
)

laps["near_best_5pct"] = (
    laps["valid_timed_lap"]
    & (
        laps["lap_duration"]
        <= laps["best_lap_seconds"] * 1.05
    )
)

# --------------------------------------------------
# ADD DRIVER INFORMATION
# --------------------------------------------------

laps = laps.merge(
    drivers[["driver_number", "full_name", "team_name"]],
    on="driver_number",
    how="left"
)

# --------------------------------------------------
# SAVE DETAILED LAP INSPECTION
# --------------------------------------------------

inspection_columns = [
    "driver_number",
    "full_name",
    "team_name",
    "lap_number",
    "date_start",
    "is_pit_out_lap",
    "lap_duration",
    "duration_sector_1",
    "duration_sector_2",
    "duration_sector_3",
    "missing_sector_count",
    "all_sectors_present",
    "sector_sum",
    "sector_sum_minus_lap_duration",
    "valid_timed_lap",
    "near_best_2pct",
    "near_best_5pct"
]

inspection = laps[inspection_columns].sort_values(
    ["driver_number", "lap_number"]
)

inspection.to_csv(
    OUTPUT_DIR / "lap_attempt_inspection.csv",
    index=False
)

# --------------------------------------------------
# DRIVER-LEVEL QUALITY SUMMARY
# --------------------------------------------------

summary = (
    laps.groupby(
        ["driver_number", "full_name", "team_name"]
    )
    .agg(
        total_lap_records=("lap_number", "count"),
        pit_out_laps=("is_pit_out_lap", "sum"),
        missing_duration_laps=("lap_duration", lambda x: x.isna().sum()),
        valid_timed_laps=("valid_timed_lap", "sum"),
        complete_sector_laps=(
            "all_sectors_present",
            "sum"
        )
    )
    .reset_index()
)

summary["valid_laps_with_missing_sectors"] = (
    summary["valid_timed_laps"]
    - summary["complete_sector_laps"]
)

summary.to_csv(
    OUTPUT_DIR / "lap_attempt_quality_summary.csv",
    index=False
)

# --------------------------------------------------
# DISPLAY RESULTS
# --------------------------------------------------

print("=" * 75)
print("LAP ATTEMPT QUALITY INSPECTION")
print("=" * 75)

print(f"\nTotal lap records: {len(laps)}")
print(f"Drivers analysed: {laps['driver_number'].nunique()}")
print(f"Valid timed laps: {laps['valid_timed_lap'].sum()}")
print(f"Pit-out laps: {laps['is_pit_out_lap'].sum()}")

print(
    "\nValid timed laps with all three sectors:",
    int(
        (
            laps["valid_timed_lap"]
            & laps["all_sectors_present"]
        ).sum()
    )
)

print(
    "\nValid timed laps with missing sector data:",
    int(
        (
            laps["valid_timed_lap"]
            & (~laps["all_sectors_present"])
        ).sum()
    )
)

print("\n" + "=" * 75)
print("DRIVER-LEVEL LAP QUALITY SUMMARY")
print("=" * 75)

print(
    summary[
        [
            "driver_number",
            "full_name",
            "total_lap_records",
            "pit_out_laps",
            "missing_duration_laps",
            "valid_timed_laps",
            "complete_sector_laps",
            "valid_laps_with_missing_sectors"
        ]
    ]
    .sort_values("driver_number")
    .to_string(index=False)
)

# --------------------------------------------------
# SECTOR SUM VALIDATION
# --------------------------------------------------

complete_valid = laps[
    laps["valid_timed_lap"]
    & laps["all_sectors_present"]
].copy()

print("\n" + "=" * 75)
print("SECTOR SUM VALIDATION")
print("=" * 75)

print(f"\nLaps compared: {len(complete_valid)}")

if len(complete_valid) > 0:
    print(
        "\nSector sum difference statistics (seconds):"
    )

    print(
        complete_valid[
            "sector_sum_minus_lap_duration"
        ].describe().round(6)
    )

    print(
        "\nLaps where absolute difference exceeds 0.1 seconds:",
        int(
            (
                complete_valid[
                    "sector_sum_minus_lap_duration"
                ].abs() > 0.1
            ).sum()
        )
    )

# --------------------------------------------------
# SAVE CONFIRMATION
# --------------------------------------------------

print("\n" + "=" * 75)
print("ANALYSIS COMPLETED")
print("=" * 75)

print(
    "\nDetailed output:",
    OUTPUT_DIR / "lap_attempt_inspection.csv"
)

print(
    "Quality summary:",
    OUTPUT_DIR / "lap_attempt_quality_summary.csv"
)
