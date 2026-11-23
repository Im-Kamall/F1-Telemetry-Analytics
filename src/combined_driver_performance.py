
import pandas as pd
from pathlib import Path

# --------------------------------------------------
# CONFIGURATION
# --------------------------------------------------

DATA_DIR = Path("data/processed")

LAP_FILE = DATA_DIR / "candidate_lap_consistency.csv"
SECTOR_FILE = DATA_DIR / "candidate_sector_performance.csv"

OUTPUT_FILE = DATA_DIR / "combined_driver_performance.csv"

# --------------------------------------------------
# LOAD DATA
# --------------------------------------------------

print("=" * 75)
print("COMBINED DRIVER PERFORMANCE ANALYSIS")
print("=" * 75)

lap_data = pd.read_csv(LAP_FILE)
sector_data = pd.read_csv(SECTOR_FILE)

print(f"\nLap consistency records: {len(lap_data)}")
print(f"Sector performance records: {len(sector_data)}")

# --------------------------------------------------
# VALIDATE REQUIRED COLUMNS
# --------------------------------------------------

lap_columns = [
    "driver_number",
    "full_name",
    "team_name",
    "candidate_laps",
    "best_lap_seconds",
    "average_lap_seconds",
    "median_lap_seconds",
    "std_lap_seconds",
    "worst_lap_seconds",
    "lap_time_range_seconds",
    "average_minus_best_seconds",
    "average_pace_rank",
    "best_lap_rank"
]

sector_columns = [
    "driver_number",
    "full_name",
    "team_name",
    "sector_1_average",
    "sector_1_best",
    "sector_1_std",
    "sector_2_average",
    "sector_2_best",
    "sector_2_std",
    "sector_3_average",
    "sector_3_best",
    "sector_3_std",
    "sector_1_share_pct",
    "sector_2_share_pct",
    "sector_3_share_pct"
]

missing_lap = [
    col for col in lap_columns
    if col not in lap_data.columns
]

missing_sector = [
    col for col in sector_columns
    if col not in sector_data.columns
]

if missing_lap or missing_sector:
    raise ValueError(
        f"Missing lap columns: {missing_lap}\n"
        f"Missing sector columns: {missing_sector}"
    )

lap_data = lap_data[lap_columns].copy()
sector_data = sector_data[sector_columns].copy()

# --------------------------------------------------
# MERGE DATASETS
# --------------------------------------------------

combined = pd.merge(
    lap_data,
    sector_data,
    on="driver_number",
    how="inner",
    validate="one_to_one",
    suffixes=("_lap", "_sector")
)

# Validate driver identity
for column in ["full_name", "team_name"]:
    if not (
        combined[f"{column}_lap"]
        == combined[f"{column}_sector"]
    ).all():
        raise ValueError(
            f"{column} mismatch between datasets."
        )

combined = combined.rename(
    columns={
        "full_name_lap": "full_name",
        "team_name_lap": "team_name"
    }
)

combined = combined.drop(
    columns=["full_name_sector", "team_name_sector"]
)

# --------------------------------------------------
# SECTOR RANKINGS
# --------------------------------------------------

for sector in ["sector_1", "sector_2", "sector_3"]:

    combined[f"{sector}_rank"] = (
        combined[f"{sector}_average"]
        .rank(method="min")
        .astype(int)
    )

# --------------------------------------------------
# COMBINED SECTOR PERFORMANCE
# --------------------------------------------------

combined["sector_rank_total"] = (
    combined["sector_1_rank"]
    + combined["sector_2_rank"]
    + combined["sector_3_rank"]
)

combined["average_sector_rank"] = (
    combined["sector_rank_total"] / 3
)

combined["combined_sector_rank"] = (
    combined["average_sector_rank"]
    .rank(method="min")
    .astype(int)
)

# --------------------------------------------------
# LAP CONSISTENCY RANKING
# --------------------------------------------------

combined["lap_consistency_rank"] = (
    combined["std_lap_seconds"]
    .rank(method="min")
    .astype(int)
)

# --------------------------------------------------
# SAVE CONSOLIDATED DATASET
# --------------------------------------------------

combined = combined.sort_values(
    "average_pace_rank"
).reset_index(drop=True)

combined.to_csv(
    OUTPUT_FILE,
    index=False
)

# --------------------------------------------------
# DISPLAY DRIVER PERFORMANCE
# --------------------------------------------------

print("\n" + "=" * 75)
print("COMBINED DRIVER PERFORMANCE RANKING")
print("=" * 75)

display_columns = [
    "driver_number",
    "full_name",
    "candidate_laps",
    "best_lap_seconds",
    "average_lap_seconds",
    "average_pace_rank",
    "sector_1_rank",
    "sector_2_rank",
    "sector_3_rank",
    "combined_sector_rank",
    "std_lap_seconds",
    "lap_consistency_rank"
]

print(
    combined[display_columns]
    .round(3)
    .to_string(index=False)
)

# --------------------------------------------------
# SECTOR LEADERS
# --------------------------------------------------

print("\n" + "=" * 75)
print("SECTOR LEADERS")
print("=" * 75)

for sector in ["sector_1", "sector_2", "sector_3"]:

    leader = combined.loc[
        combined[f"{sector}_average"].idxmin()
    ]

    print(
        f"{sector.upper()}: "
        f"{leader['full_name']} - "
        f"{leader[f'{sector}_average']:.3f}s average"
    )

# --------------------------------------------------
# OVERALL PACE LEADER
# --------------------------------------------------

pace_leader = combined.loc[
    combined["average_pace_rank"].idxmin()
]

print("\n" + "=" * 75)
print("AVERAGE PACE LEADER")
print("=" * 75)

print(f"Driver: {pace_leader['full_name']}")
print(
    f"Average candidate lap: "
    f"{pace_leader['average_lap_seconds']:.3f}s"
)
print(f"Candidate laps: {pace_leader['candidate_laps']}")

# --------------------------------------------------
# DATA VALIDATION
# --------------------------------------------------

print("\n" + "=" * 75)
print("DATA VALIDATION")
print("=" * 75)

print(f"Combined drivers: {len(combined)}")
print(
    "Duplicate driver numbers: "
    f"{combined['driver_number'].duplicated().sum()}"
)
print(
    f"Missing values: {combined.isna().sum().sum()}"
)

print(f"\nSaved file: {OUTPUT_FILE}")

print("\n" + "=" * 75)
print("ANALYSIS COMPLETED")
print("=" * 75)
