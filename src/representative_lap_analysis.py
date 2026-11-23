
import pandas as pd
from pathlib import Path

# --------------------------------------------------
# CONFIGURATION
# --------------------------------------------------

OUTPUT_DIR = Path("data/processed")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

MIN_LAP_SECONDS = 85
MAX_LAP_SECONDS = 95

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

# --------------------------------------------------
# CLASSIFY LAP RECORDS
# --------------------------------------------------

sector_columns = [
    "duration_sector_1",
    "duration_sector_2",
    "duration_sector_3"
]

laps["all_sectors_present"] = (
    laps[sector_columns].notna().all(axis=1)
)

laps["valid_timed_lap"] = (
    (~laps["is_pit_out_lap"])
    & laps["lap_duration"].notna()
    & (laps["lap_duration"] > 0)
)

laps["within_exploratory_window"] = (
    laps["lap_duration"].between(
        MIN_LAP_SECONDS,
        MAX_LAP_SECONDS,
        inclusive="both"
    )
)

# --------------------------------------------------
# EXPLAIN INCLUSION / EXCLUSION
# --------------------------------------------------

def classify_lap(row):

    if row["is_pit_out_lap"]:
        return "Excluded: pit-out lap"

    if pd.isna(row["lap_duration"]):
        return "Excluded: missing lap duration"

    if row["lap_duration"] <= 0:
        return "Excluded: invalid lap duration"

    if not row["all_sectors_present"]:
        return "Excluded: incomplete sectors"

    if not row["within_exploratory_window"]:
        return "Excluded: outside 85-95 second window"

    return "Candidate representative lap"


laps["selection_reason"] = laps.apply(
    classify_lap,
    axis=1
)

laps["candidate_representative_lap"] = (
    laps["selection_reason"]
    == "Candidate representative lap"
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
# SAVE DETAILED DATASET
# --------------------------------------------------

output_columns = [
    "driver_number",
    "full_name",
    "team_name",
    "lap_number",
    "lap_duration",
    "duration_sector_1",
    "duration_sector_2",
    "duration_sector_3",
    "is_pit_out_lap",
    "all_sectors_present",
    "valid_timed_lap",
    "within_exploratory_window",
    "candidate_representative_lap",
    "selection_reason"
]

detailed = laps[output_columns].sort_values(
    ["driver_number", "lap_number"]
)

detailed.to_csv(
    OUTPUT_DIR / "representative_lap_candidates.csv",
    index=False
)

# --------------------------------------------------
# DRIVER-LEVEL SUMMARY
# --------------------------------------------------

summary = (
    laps.groupby(
        ["driver_number", "full_name", "team_name"]
    )
    .agg(
        total_records=("lap_number", "count"),
        valid_timed_laps=("valid_timed_lap", "sum"),
        complete_sector_laps=("all_sectors_present", "sum"),
        candidate_laps=("candidate_representative_lap", "sum"),
        best_candidate_lap=("lap_duration", lambda x: x[
            laps.loc[x.index, "candidate_representative_lap"]
        ].min() if laps.loc[x.index, "candidate_representative_lap"].any() else None)
    )
    .reset_index()
)

summary.to_csv(
    OUTPUT_DIR / "representative_lap_summary.csv",
    index=False
)

# --------------------------------------------------
# DISPLAY RESULTS
# --------------------------------------------------

print("=" * 75)
print("REPRESENTATIVE LAP CANDIDATE ANALYSIS")
print("=" * 75)

print(f"\nExploratory lap window: {MIN_LAP_SECONDS}-{MAX_LAP_SECONDS} seconds")
print(f"Total lap records: {len(laps)}")
print(f"Valid timed laps: {int(laps['valid_timed_lap'].sum())}")
print(
    "Candidate representative laps:",
    int(laps["candidate_representative_lap"].sum())
)

print("\n" + "=" * 75)
print("CANDIDATE LAPS BY DRIVER")
print("=" * 75)

print(
    summary[
        [
            "driver_number",
            "full_name",
            "valid_timed_laps",
            "candidate_laps",
            "best_candidate_lap"
        ]
    ]
    .sort_values("best_candidate_lap")
    .round(3)
    .to_string(index=False)
)

print("\n" + "=" * 75)
print("SELECTION REASONS")
print("=" * 75)

print(
    laps["selection_reason"]
    .value_counts()
    .to_string()
)

print("\n" + "=" * 75)
print("FILES SAVED")
print("=" * 75)

print(OUTPUT_DIR / "representative_lap_candidates.csv")
print(OUTPUT_DIR / "representative_lap_summary.csv")
