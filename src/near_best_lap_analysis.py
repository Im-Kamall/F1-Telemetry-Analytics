
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

laps["lap_duration"] = pd.to_numeric(
    laps["lap_duration"],
    errors="coerce"
)

# --------------------------------------------------
# FILTER VALID TIMED LAPS
# --------------------------------------------------

valid = laps[
    (~laps["is_pit_out_lap"])
    & laps["lap_duration"].notna()
    & (laps["lap_duration"] > 0)
].copy()

valid = valid.merge(
    drivers[["driver_number", "full_name", "team_name"]],
    on="driver_number",
    how="left"
)

# --------------------------------------------------
# NEAR-BEST LAP ANALYSIS
# --------------------------------------------------

print("=" * 75)
print("NEAR-BEST LAP CONSISTENCY ANALYSIS")
print("=" * 75)

print(f"\nValid timed laps: {len(valid)}")

results = []

for (driver_number, full_name, team_name), group in valid.groupby(
    ["driver_number", "full_name", "team_name"]
):

    best_lap = group["lap_duration"].min()

    row = {
        "driver_number": driver_number,
        "full_name": full_name,
        "team_name": team_name,
        "valid_laps": len(group),
        "best_lap_seconds": best_lap
    }

    # Calculate laps within 2% and 5% of best lap
    for percentage in [0.02, 0.05]:

        threshold = best_lap * (1 + percentage)

        selected = group[
            group["lap_duration"] <= threshold
        ]["lap_duration"]

        label = int(percentage * 100)

        row[f"laps_within_{label}pct"] = len(selected)

        row[f"average_within_{label}pct"] = (
            selected.mean() if len(selected) > 0 else None
        )

        row[f"std_within_{label}pct"] = (
            selected.std() if len(selected) > 1 else None
        )

    results.append(row)

# --------------------------------------------------
# CREATE SUMMARY DATAFRAME
# --------------------------------------------------

summary = pd.DataFrame(results)

# --------------------------------------------------
# 2% NEAR-BEST LAP TABLE
# --------------------------------------------------

print("\n" + "=" * 75)
print("LAPS WITHIN 2% OF BEST LAP")
print("=" * 75)

columns_2pct = [
    "driver_number",
    "full_name",
    "valid_laps",
    "best_lap_seconds",
    "laps_within_2pct",
    "average_within_2pct",
    "std_within_2pct"
]

print(
    summary[columns_2pct]
    .sort_values("best_lap_seconds")
    .round(3)
    .to_string(index=False)
)

# --------------------------------------------------
# 5% NEAR-BEST LAP TABLE
# --------------------------------------------------

print("\n" + "=" * 75)
print("LAPS WITHIN 5% OF BEST LAP")
print("=" * 75)

columns_5pct = [
    "driver_number",
    "full_name",
    "valid_laps",
    "best_lap_seconds",
    "laps_within_5pct",
    "average_within_5pct",
    "std_within_5pct"
]

print(
    summary[columns_5pct]
    .sort_values("best_lap_seconds")
    .round(3)
    .to_string(index=False)
)

# --------------------------------------------------
# SAVE RESULTS
# --------------------------------------------------

output_file = OUTPUT_DIR / "near_best_lap_consistency.csv"

summary.to_csv(output_file, index=False)

print("\n" + "=" * 75)
print("ANALYSIS COMPLETED")
print("=" * 75)

print(f"\nTotal drivers analysed: {len(summary)}")
print(f"Total valid timed laps: {len(valid)}")
print(f"Output saved to: {output_file}")
