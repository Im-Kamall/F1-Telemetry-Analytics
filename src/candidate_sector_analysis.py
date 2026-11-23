
import pandas as pd
from pathlib import Path

# --------------------------------------------------
# CONFIGURATION
# --------------------------------------------------

INPUT_FILE = Path(
    "data/processed/representative_lap_candidates.csv"
)

OUTPUT_DIR = Path("data/processed")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

SECTORS = {
    "Sector 1": "duration_sector_1",
    "Sector 2": "duration_sector_2",
    "Sector 3": "duration_sector_3"
}

# --------------------------------------------------
# LOAD DATA
# --------------------------------------------------

laps = pd.read_csv(INPUT_FILE)

# Ensure numeric sector values
for column in SECTORS.values():
    laps[column] = pd.to_numeric(
        laps[column],
        errors="coerce"
    )

# Keep only candidate laps
candidates = laps[
    laps["candidate_representative_lap"] == True
].copy()

# Require all three sector values
candidates = candidates.dropna(
    subset=list(SECTORS.values())
)

# --------------------------------------------------
# DRIVER-LEVEL SECTOR ANALYSIS
# --------------------------------------------------

results = []

for (driver_number, full_name, team_name), group in candidates.groupby(
    ["driver_number", "full_name", "team_name"]
):

    row = {
        "driver_number": driver_number,
        "full_name": full_name,
        "team_name": team_name,
        "candidate_laps": len(group)
    }

    for sector_name, column in SECTORS.items():

        row[f"{sector_name.lower().replace(' ', '_')}_average"] = (
            group[column].mean()
        )

        row[f"{sector_name.lower().replace(' ', '_')}_best"] = (
            group[column].min()
        )

        row[f"{sector_name.lower().replace(' ', '_')}_std"] = (
            group[column].std()
        )

    # Average of total lap times
    row["average_lap_seconds"] = (
        group["lap_duration"].mean()
    )

    results.append(row)

summary = pd.DataFrame(results)

# --------------------------------------------------
# SECTOR RANKINGS
# Lower sector time = faster
# --------------------------------------------------

for sector in ["sector_1", "sector_2", "sector_3"]:

    summary[f"{sector}_rank"] = (
        summary[f"{sector}_average"]
        .rank(method="min")
        .astype(int)
    )

# --------------------------------------------------
# SECTOR CONTRIBUTION
# --------------------------------------------------

summary["sector_1_share_pct"] = (
    summary["sector_1_average"]
    / summary["average_lap_seconds"] * 100
)

summary["sector_2_share_pct"] = (
    summary["sector_2_average"]
    / summary["average_lap_seconds"] * 100
)

summary["sector_3_share_pct"] = (
    summary["sector_3_average"]
    / summary["average_lap_seconds"] * 100
)

# --------------------------------------------------
# SAVE RESULTS
# --------------------------------------------------

output_file = (
    OUTPUT_DIR / "candidate_sector_performance.csv"
)

summary.to_csv(
    output_file,
    index=False
)

# --------------------------------------------------
# DISPLAY SECTOR 1
# --------------------------------------------------

print("=" * 75)
print("CANDIDATE SECTOR PERFORMANCE ANALYSIS")
print("=" * 75)

print(f"\nCandidate laps analysed: {len(candidates)}")
print(f"Drivers analysed: {len(summary)}")

for sector in ["sector_1", "sector_2", "sector_3"]:

    print("\n" + "=" * 75)
    print(f"{sector.upper()} RANKING")
    print("=" * 75)

    columns = [
        "driver_number",
        "full_name",
        "candidate_laps",
        f"{sector}_average",
        f"{sector}_best",
        f"{sector}_std",
        f"{sector}_rank"
    ]

    print(
        summary[columns]
        .sort_values(f"{sector}_average")
        .round(3)
        .to_string(index=False)
    )

# --------------------------------------------------
# SECTOR CONTRIBUTION
# --------------------------------------------------

print("\n" + "=" * 75)
print("AVERAGE SECTOR CONTRIBUTION")
print("=" * 75)

contribution_columns = [
    "driver_number",
    "full_name",
    "sector_1_share_pct",
    "sector_2_share_pct",
    "sector_3_share_pct"
]

print(
    summary[contribution_columns]
    .sort_values("driver_number")
    .round(2)
    .to_string(index=False)
)

# --------------------------------------------------
# OVERALL BEST SECTOR TIMES
# --------------------------------------------------

print("\n" + "=" * 75)
print("OVERALL BEST CANDIDATE SECTOR TIMES")
print("=" * 75)

for sector_name, column in SECTORS.items():

    best_index = candidates[column].idxmin()
    best_row = candidates.loc[best_index]

    print(
        f"{sector_name}: "
        f"{best_row[column]:.3f}s - "
        f"{best_row['full_name']} "
        f"(Lap {int(best_row['lap_number'])})"
    )

# --------------------------------------------------
# COMPLETION
# --------------------------------------------------

print("\n" + "=" * 75)
print("ANALYSIS COMPLETED")
print("=" * 75)

print(f"\nResults saved to: {output_file}")
