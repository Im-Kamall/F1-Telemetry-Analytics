
import pandas as pd
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent

DATA_FILE = (
    PROJECT_ROOT
    / "data"
    / "processed"
    / "all_drivers_telemetry_clean.csv"
)

# Representative drivers
SELECTED_DRIVERS = [16, 1, 2, 24]

# OpenF1 telemetry is sampled approximately several times per second.
# A gap greater than 2 seconds starts a new segment.
MAX_GAP_SECONDS = 2


def analyze_driver_segments(df, driver_number):

    driver_df = df[
        df["driver_number"] == driver_number
    ].copy()

    driver_df = driver_df.sort_values("date").reset_index(drop=True)

    driver_df["time_gap"] = (
        driver_df["date"].diff().dt.total_seconds()
    )

    driver_df["is_moving"] = driver_df["speed"] > 0

    # Start a new segment when:
    # 1. Moving/stationary state changes
    # 2. There is a large timestamp gap
    state_changed = (
        driver_df["is_moving"] !=
        driver_df["is_moving"].shift()
    )

    large_gap = (
        driver_df["time_gap"] > MAX_GAP_SECONDS
    )

    new_segment = state_changed | large_gap

    driver_df["segment_id"] = new_segment.cumsum()

    segments = driver_df.groupby("segment_id").agg(
        start_time=("date", "first"),
        end_time=("date", "last"),
        records=("speed", "size"),
        moving=("is_moving", "first"),
        average_speed=("speed", "mean"),
        maximum_speed=("speed", "max"),
        average_rpm=("rpm", "mean")
    ).reset_index(drop=True)

    segments["duration_seconds"] = (
        segments["end_time"] -
        segments["start_time"]
    ).dt.total_seconds()

    return segments


def main():

    print("=" * 75)
    print("F1 TELEMETRY: CONTINUOUS DRIVING PERIOD ANALYSIS")
    print("=" * 75)

    df = pd.read_csv(DATA_FILE)

    df["date"] = pd.to_datetime(
        df["date"],
        errors="coerce",
        utc=True
    )

    numeric_columns = [
        "driver_number",
        "speed",
        "rpm"
    ]

    for column in numeric_columns:
        df[column] = pd.to_numeric(
            df[column],
            errors="coerce"
        )

    df = df.dropna(
        subset=["date", "driver_number", "speed", "rpm"]
    )

    all_segments = []

    for driver_number in SELECTED_DRIVERS:

        segments = analyze_driver_segments(
            df,
            driver_number
        )

        segments.insert(
            0,
            "driver_number",
            driver_number
        )

        all_segments.append(segments)

        print("\n" + "=" * 75)
        print(f"DRIVER #{driver_number}")
        print("=" * 75)

        moving_segments = segments[
            segments["moving"]
        ]

        zero_segments = segments[
            ~segments["moving"]
        ]

        print("\nMOVING PERIODS")
        print("-" * 45)

        print("Number of moving periods:", len(moving_segments))

        if not moving_segments.empty:

            print(
                moving_segments.nlargest(
                    3,
                    "duration_seconds"
                )[
                    [
                        "start_time",
                        "end_time",
                        "records",
                        "duration_seconds",
                        "average_speed",
                        "maximum_speed"
                    ]
                ].to_string(index=False)
            )

        print("\nZERO-SPEED PERIODS")
        print("-" * 45)

        print("Number of zero-speed periods:", len(zero_segments))

        if not zero_segments.empty:

            print(
                zero_segments.nlargest(
                    3,
                    "duration_seconds"
                )[
                    [
                        "start_time",
                        "end_time",
                        "records",
                        "duration_seconds",
                        "average_rpm"
                    ]
                ].to_string(index=False)
            )

    # Save all segments for further analysis
    output_df = pd.concat(
        all_segments,
        ignore_index=True
    )

    output_file = (
        PROJECT_ROOT
        / "data"
        / "processed"
        / "selected_driver_segments.csv"
    )

    output_df.to_csv(
        output_file,
        index=False
    )

    print("\n" + "=" * 75)
    print("SEGMENT ANALYSIS COMPLETED")
    print("=" * 75)

    print("Total segments:", len(output_df))
    print("Report saved to:", output_file)


if __name__ == "__main__":
    main()
