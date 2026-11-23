
"""
F1 Telemetry Analytics Platform
Data Analysis Module

Analyses:
1. Fastest recorded lap leaderboard
2. Verstappen telemetry summary
3. All 20 drivers telemetry comparison
4. Speed, throttle, brake, RPM and gear statistics

Inputs:
    data/raw/laps.csv
    data/raw/drivers.csv
    data/raw/verstappen_telemetry.csv
    data/processed/all_drivers_telemetry_clean.csv

Outputs:
    data/processed/fastest_lap_leaderboard.csv
    data/processed/telemetry_summary.csv
    data/processed/all_drivers_summary.csv
    data/processed/driver_speed_ranking.csv
    data/processed/driver_control_comparison.csv
"""

from pathlib import Path

import pandas as pd


# --------------------------------------------------
# 1. PROJECT PATHS
# --------------------------------------------------

PROJECT_ROOT = Path(__file__).resolve().parent.parent

RAW_DATA_DIR = PROJECT_ROOT / "data" / "raw"
PROCESSED_DATA_DIR = PROJECT_ROOT / "data" / "processed"

PROCESSED_DATA_DIR.mkdir(parents=True, exist_ok=True)

ALL_DRIVER_TELEMETRY = (
    PROCESSED_DATA_DIR / "all_drivers_telemetry_clean.csv"
)


# --------------------------------------------------
# 2. LOAD DATA
# --------------------------------------------------

def load_data():
    """Load raw and processed datasets."""

    laps_path = RAW_DATA_DIR / "laps.csv"
    drivers_path = RAW_DATA_DIR / "drivers.csv"
    verstappen_path = RAW_DATA_DIR / "verstappen_telemetry.csv"

    required_files = [
        laps_path,
        drivers_path,
        verstappen_path,
        ALL_DRIVER_TELEMETRY
    ]

    for file_path in required_files:
        if not file_path.exists():
            raise FileNotFoundError(
                f"Required file not found: {file_path}"
            )

    laps = pd.read_csv(laps_path)
    drivers = pd.read_csv(drivers_path)
    verstappen_telemetry = pd.read_csv(verstappen_path)

    all_telemetry = pd.read_csv(
        ALL_DRIVER_TELEMETRY,
        parse_dates=["date"]
    )

    print("\nData loaded successfully!")
    print(f"Laps records: {len(laps)}")
    print(f"Drivers records: {len(drivers)}")
    print(f"Verstappen telemetry: {len(verstappen_telemetry)}")
    print(f"All-driver telemetry: {len(all_telemetry)}")
    print(
        "Unique telemetry drivers:",
        all_telemetry["driver_number"].nunique()
    )

    return laps, drivers, verstappen_telemetry, all_telemetry


# --------------------------------------------------
# 3. FASTEST LAP ANALYSIS
# --------------------------------------------------

def analyze_fastest_laps(laps, drivers):
    """Find each driver's fastest recorded lap."""

    required_columns = [
        "driver_number",
        "lap_duration"
    ]

    for column in required_columns:
        if column not in laps.columns:
            raise ValueError(
                f"Missing column in laps.csv: {column}"
            )

    laps = laps.copy()

    laps["lap_duration"] = pd.to_numeric(
        laps["lap_duration"],
        errors="coerce"
    )

    valid_laps = laps.dropna(
        subset=["driver_number", "lap_duration"]
    ).copy()

    if "is_pit_out_lap" in valid_laps.columns:
        pit_out = (
            valid_laps["is_pit_out_lap"]
            .astype(str)
            .str.lower()
            .isin(["true", "1"])
        )
        valid_laps = valid_laps[~pit_out].copy()

    fastest_laps = (
        valid_laps
        .sort_values("lap_duration")
        .groupby("driver_number", as_index=False)
        .first()
    )

    driver_columns = [
        column for column in [
            "driver_number",
            "full_name",
            "team_name",
            "name_acronym"
        ]
        if column in drivers.columns
    ]

    driver_info = drivers[driver_columns].drop_duplicates(
        subset=["driver_number"]
    )

    leaderboard = fastest_laps.merge(
        driver_info,
        on="driver_number",
        how="left"
    )

    for column, default in [
        ("full_name", "Unknown"),
        ("team_name", "Unknown"),
        ("name_acronym", "N/A")
    ]:
        if column not in leaderboard.columns:
            leaderboard[column] = default

    leaderboard = leaderboard.sort_values(
        "lap_duration"
    ).reset_index(drop=True)

    leaderboard.insert(
        0,
        "position",
        range(1, len(leaderboard) + 1)
    )

    output_columns = [
        "position",
        "driver_number",
        "full_name",
        "team_name",
        "lap_number",
        "lap_duration",
        "duration_sector_1",
        "duration_sector_2",
        "duration_sector_3",
        "name_acronym"
    ]

    leaderboard = leaderboard[
        [c for c in output_columns if c in leaderboard.columns]
    ]

    output_path = (
        PROCESSED_DATA_DIR / "fastest_lap_leaderboard.csv"
    )

    leaderboard.to_csv(output_path, index=False)

    print("\nFASTEST RECORDED LAP LEADERBOARD")
    print(
        leaderboard[
            [
                "position",
                "full_name",
                "team_name",
                "lap_duration"
            ]
        ].to_string(index=False)
    )

    print(f"\nSaved: {output_path}")

    return leaderboard


# --------------------------------------------------
# 4. VERSTAPPEN TELEMETRY ANALYSIS
# --------------------------------------------------

def analyze_telemetry(telemetry):
    """Calculate telemetry statistics for Verstappen."""

    telemetry = telemetry.copy()

    numeric_columns = [
        "speed",
        "throttle",
        "brake",
        "rpm",
        "n_gear"
    ]

    for column in numeric_columns:
        if column not in telemetry.columns:
            raise ValueError(
                f"Missing telemetry column: {column}"
            )

        telemetry[column] = pd.to_numeric(
            telemetry[column],
            errors="coerce"
        )

    telemetry = telemetry.dropna(
        subset=numeric_columns
    )

    if telemetry.empty:
        raise ValueError("No valid Verstappen telemetry.")

    summary = {
        "Total telemetry records": len(telemetry),
        "Average speed (km/h)": round(telemetry["speed"].mean(), 2),
        "Maximum speed (km/h)": round(telemetry["speed"].max(), 2),
        "Minimum speed (km/h)": round(telemetry["speed"].min(), 2),
        "Average throttle (raw)": round(telemetry["throttle"].mean(), 2),
        "Maximum throttle (raw)": round(telemetry["throttle"].max(), 2),
        "Average RPM": round(telemetry["rpm"].mean(), 2),
        "Maximum RPM": round(telemetry["rpm"].max(), 2),
        "Average gear": round(telemetry["n_gear"].mean(), 2),
        "Maximum gear": int(telemetry["n_gear"].max()),
        "Non-zero brake records (%)": round(
            telemetry["brake"].gt(0).mean() * 100, 2
        )
    }

    summary_df = pd.DataFrame(
        list(summary.items()),
        columns=["Metric", "Value"]
    )

    output_path = (
        PROCESSED_DATA_DIR / "telemetry_summary.csv"
    )

    summary_df.to_csv(output_path, index=False)

    print("\nVERSTAPPEN TELEMETRY SUMMARY")

    for metric, value in summary.items():
        print(f"{metric}: {value}")

    print(f"\nSaved: {output_path}")

    return summary_df


# --------------------------------------------------
# 5. ALL-DRIVER TELEMETRY ANALYSIS
# --------------------------------------------------

def analyze_all_drivers(telemetry, drivers):
    """Compare telemetry statistics across all drivers."""

    required_columns = [
        "driver_number",
        "speed",
        "throttle",
        "brake",
        "rpm",
        "n_gear"
    ]

    for column in required_columns:
        if column not in telemetry.columns:
            raise ValueError(
                f"Missing all-driver telemetry column: {column}"
            )

    telemetry = telemetry.copy()

    numeric_columns = [
        "driver_number",
        "speed",
        "throttle",
        "brake",
        "rpm",
        "n_gear"
    ]

    for column in numeric_columns:
        telemetry[column] = pd.to_numeric(
            telemetry[column],
            errors="coerce"
        )

    telemetry = telemetry.dropna(
        subset=numeric_columns
    )

    # Group telemetry by driver
    summary = (
        telemetry
        .groupby("driver_number")
        .agg(
            telemetry_records=("speed", "count"),
            average_speed=("speed", "mean"),
            maximum_speed=("speed", "max"),
            minimum_speed=("speed", "min"),
            speed_std=("speed", "std"),
            average_throttle=("throttle", "mean"),
            maximum_throttle=("throttle", "max"),
            average_brake=("brake", "mean"),
            maximum_brake=("brake", "max"),
            brake_active_percentage=(
                "brake",
                lambda x: x.gt(0).mean() * 100
            ),
            average_rpm=("rpm", "mean"),
            maximum_rpm=("rpm", "max"),
            average_gear=("n_gear", "mean"),
            maximum_gear=("n_gear", "max")
        )
        .reset_index()
    )

    # Attach driver and team names
    driver_columns = [
        column for column in [
            "driver_number",
            "full_name",
            "team_name",
            "name_acronym"
        ]
        if column in drivers.columns
    ]

    driver_info = drivers[driver_columns].drop_duplicates(
        subset=["driver_number"]
    )

    summary = summary.merge(
        driver_info,
        on="driver_number",
        how="left"
    )

    summary["full_name"] = (
        summary["full_name"].fillna("Unknown")
        if "full_name" in summary.columns
        else "Unknown"
    )

    summary["team_name"] = (
        summary["team_name"].fillna("Unknown")
        if "team_name" in summary.columns
        else "Unknown"
    )

    summary["name_acronym"] = (
        summary["name_acronym"].fillna("N/A")
        if "name_acronym" in summary.columns
        else "N/A"
    )

    # Round numeric results
    decimal_columns = [
        "average_speed",
        "maximum_speed",
        "minimum_speed",
        "speed_std",
        "average_throttle",
        "maximum_throttle",
        "average_brake",
        "maximum_brake",
        "brake_active_percentage",
        "average_rpm",
        "maximum_rpm",
        "average_gear"
    ]

    summary[decimal_columns] = summary[
        decimal_columns
    ].round(2)

    summary["maximum_gear"] = summary[
        "maximum_gear"
    ].astype(int)

    summary = summary.sort_values(
        "average_speed",
        ascending=False
    ).reset_index(drop=True)

    output_path = (
        PROCESSED_DATA_DIR / "all_drivers_summary.csv"
    )

    summary.to_csv(output_path, index=False)

    print("\nALL-DRIVER TELEMETRY COMPARISON")
    print(
        summary[
            [
                "driver_number",
                "full_name",
                "team_name",
                "average_speed",
                "maximum_speed",
                "average_rpm",
                "average_throttle",
                "brake_active_percentage"
            ]
        ].to_string(index=False)
    )

    print(f"\nSaved: {output_path}")

    return summary


# --------------------------------------------------
# 6. DRIVER RANKINGS AND CONTROL COMPARISON
# --------------------------------------------------

def create_driver_rankings(summary):
    """Create separate driver ranking and control CSV files."""

    # Descriptive speed ranking
    speed_ranking = summary[
        [
            "driver_number",
            "full_name",
            "team_name",
            "average_speed",
            "maximum_speed",
            "speed_std"
        ]
    ].sort_values(
        "average_speed",
        ascending=False
    ).reset_index(drop=True)

    speed_ranking.insert(
        0,
        "average_speed_rank",
        range(1, len(speed_ranking) + 1)
    )

    speed_path = (
        PROCESSED_DATA_DIR / "driver_speed_ranking.csv"
    )

    speed_ranking.to_csv(speed_path, index=False)

    # Control comparison
    control_comparison = summary[
        [
            "driver_number",
            "full_name",
            "team_name",
            "average_throttle",
            "maximum_throttle",
            "average_brake",
            "maximum_brake",
            "brake_active_percentage",
            "average_rpm",
            "average_gear"
        ]
    ].copy()

    control_path = (
        PROCESSED_DATA_DIR / "driver_control_comparison.csv"
    )

    control_comparison.to_csv(
        control_path,
        index=False
    )

    print("\nDRIVER SPEED RANKING")
    print(speed_ranking.to_string(index=False))

    print("\nDRIVER CONTROL COMPARISON")
    print(control_comparison.to_string(index=False))

    print(f"\nSaved: {speed_path}")
    print(f"Saved: {control_path}")


# --------------------------------------------------
# 7. MAIN FUNCTION
# --------------------------------------------------

def main():
    """Run the complete F1 data analysis pipeline."""

    print("=" * 60)
    print("F1 TELEMETRY ANALYTICS - DATA ANALYSIS")
    print("=" * 60)

    laps, drivers, verstappen_telemetry, all_telemetry = (
        load_data()
    )

    analyze_fastest_laps(laps, drivers)

    analyze_telemetry(verstappen_telemetry)

    all_driver_summary = analyze_all_drivers(
        all_telemetry,
        drivers
    )

    create_driver_rankings(all_driver_summary)

    print("\n" + "=" * 60)
    print("ALL DATA ANALYSIS COMPLETED SUCCESSFULLY!")
    print("=" * 60)


# --------------------------------------------------
# 8. EXECUTION
# --------------------------------------------------

if __name__ == "__main__":
    try:
        main()

    except (FileNotFoundError, ValueError, KeyError) as error:
        print(f"\nData Error: {error}")

    except Exception as error:
        print(f"\nUnexpected Error: {error}")
        raise
