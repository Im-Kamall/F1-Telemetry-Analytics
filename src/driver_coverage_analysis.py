
import pandas as pd
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent

DATA_FILE = (
    PROJECT_ROOT
    / "data"
    / "processed"
    / "all_drivers_telemetry_clean.csv"
)


def analyze_driver_coverage():

    df = pd.read_csv(DATA_FILE)

    print("=" * 75)
    print("F1 TELEMETRY: DRIVER COVERAGE ANALYSIS")
    print("=" * 75)

    # Ensure numeric values
    numeric_columns = [
        "speed",
        "rpm",
        "throttle",
        "brake",
        "n_gear"
    ]

    for column in numeric_columns:
        df[column] = pd.to_numeric(
            df[column],
            errors="coerce"
        )

    # Classify telemetry records
    df["is_moving"] = df["speed"] > 0
    df["is_stationary"] = df["speed"] == 0
    df["engine_active"] = df["rpm"] > 0
    df["speed_and_rpm_zero"] = (
        (df["speed"] == 0) &
        (df["rpm"] == 0)
    )

    # Group by driver
    summary = df.groupby("driver_number").agg(
        total_records=("speed", "count"),
        moving_records=("is_moving", "sum"),
        stationary_records=("is_stationary", "sum"),
        engine_active_records=("engine_active", "sum"),
        both_zero_records=("speed_and_rpm_zero", "sum"),
        average_speed=("speed", "mean"),
        median_speed=("speed", "median"),
        maximum_speed=("speed", "max"),
        average_rpm=("rpm", "mean")
    )

    # Calculate percentages
    summary["moving_percentage"] = (
        summary["moving_records"] /
        summary["total_records"] * 100
    )

    summary["stationary_percentage"] = (
        summary["stationary_records"] /
        summary["total_records"] * 100
    )

    summary["engine_active_percentage"] = (
        summary["engine_active_records"] /
        summary["total_records"] * 100
    )

    summary["both_zero_percentage"] = (
        summary["both_zero_records"] /
        summary["total_records"] * 100
    )

    summary = summary.round(2)

    # Display results
    print("\n1. DRIVER COVERAGE SUMMARY")
    print("-" * 75)

    print(summary.to_string())

    # Compare moving samples
    print("\n2. MOVING SAMPLE RANKING")
    print("-" * 75)

    print(
        summary.sort_values(
            "moving_percentage",
            ascending=False
        )[
            [
                "moving_records",
                "moving_percentage",
                "average_speed",
                "median_speed"
            ]
        ].to_string()
    )

    # Overall dataset statistics
    print("\n3. OVERALL COVERAGE")
    print("-" * 75)

    print(f"Total records: {len(df):,}")
    print(f"Unique drivers: {df['driver_number'].nunique()}")
    print(f"Moving records: {df['is_moving'].sum():,}")
    print(f"Stationary records: {df['is_stationary'].sum():,}")
    print(
        "Records with zero speed and RPM:",
        f"{df['speed_and_rpm_zero'].sum():,}"
    )

    # Save report
    output_file = (
        PROJECT_ROOT
        / "data"
        / "processed"
        / "driver_coverage_summary.csv"
    )

    summary.to_csv(output_file)

    print("\nReport saved to:")
    print(output_file)

    print("\n" + "=" * 75)
    print("DRIVER COVERAGE ANALYSIS COMPLETED")
    print("=" * 75)


if __name__ == "__main__":
    analyze_driver_coverage()
