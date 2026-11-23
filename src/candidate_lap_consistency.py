
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

# --------------------------------------------------
# LOAD CANDIDATE LAPS
# --------------------------------------------------

laps = pd.read_csv(INPUT_FILE)

laps["lap_duration"] = pd.to_numeric(
    laps["lap_duration"],
    errors="coerce"
)

candidates = laps[
    laps["candidate_representative_lap"] == True
].copy()

# --------------------------------------------------
# DRIVER CONSISTENCY ANALYSIS
# --------------------------------------------------

results = []

for (driver_number, full_name, team_name), group in candidates.groupby(
    ["driver_number", "full_name", "team_name"]
):

    times = group["lap_duration"]

    best = times.min()
    average = times.mean()
    median = times.median()
    standard_deviation = times.std()
    worst = times.max()

    results.append({
        "driver_number": driver_number,
        "full_name": full_name,
        "team_name": team_name,
        "candidate_laps": len(times),
        "best_lap_seconds": best,
        "average_lap_seconds": average,
        "median_lap_seconds": median,
        "std_lap_seconds": standard_deviation,
        "worst_lap_seconds": worst,
        "lap_time_range_seconds": worst - best,
        "average_minus_best_seconds": average - best
    })

summary = pd.DataFrame(results)

# --------------------------------------------------
# RANKINGS
# --------------------------------------------------

summary = summary.sort_values(
    "average_lap_seconds"
).reset_index(drop=True)

summary["average_pace_rank"] = (
    summary.index + 1
)

summary["best_lap_rank"] = (
    summary["best_lap_seconds"].rank(
        method="min"
    ).astype(int)
)

# --------------------------------------------------
# SAVE RESULTS
# --------------------------------------------------

output_file = (
    OUTPUT_DIR / "candidate_lap_consistency.csv"
)

summary.to_csv(
    output_file,
    index=False
)

# --------------------------------------------------
# DISPLAY RESULTS
# --------------------------------------------------

print("=" * 75)
print("CANDIDATE LAP CONSISTENCY ANALYSIS")
print("=" * 75)

print(f"\nCandidate laps analysed: {len(candidates)}")
print(f"Drivers analysed: {len(summary)}")

print("\n" + "=" * 75)
print("AVERAGE CANDIDATE LAP RANKING")
print("=" * 75)

columns = [
    "average_pace_rank",
    "driver_number",
    "full_name",
    "candidate_laps",
    "best_lap_seconds",
    "average_lap_seconds",
    "median_lap_seconds",
    "std_lap_seconds",
    "lap_time_range_seconds"
]

print(
    summary[columns]
    .round(3)
    .to_string(index=False)
)

print("\n" + "=" * 75)
print("RESULTS SAVED")
print("=" * 75)

print(output_file)
