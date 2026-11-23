
import pandas as pd
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent

RAW_FILE = (
    PROJECT_ROOT
    / "data"
    / "raw"
    / "all_drivers_telemetry.csv"
)


def investigate_duplicates():

    df = pd.read_csv(RAW_FILE)

    print("=" * 65)
    print("F1 TELEMETRY: DUPLICATE INVESTIGATION")
    print("=" * 65)

    # Convert timestamps for reliable analysis
    df["date"] = pd.to_datetime(
        df["date"],
        errors="coerce",
        utc=True
    )

    # 1. Overall duplicate analysis
    full_duplicate_mask = df.duplicated(keep=False)

    print("\n1. OVERALL DUPLICATES")
    print("-" * 45)

    print("Duplicate rows beyond first occurrence:",
          df.duplicated().sum())

    print("Rows belonging to duplicate groups:",
          full_duplicate_mask.sum())

    # 2. Duplicate analysis involving missing timestamps
    missing_date_df = df[df["date"].isna()]

    print("\n2. MISSING TIMESTAMP RECORDS")
    print("-" * 45)

    print("Rows with missing timestamps:", len(missing_date_df))

    print(
        "Fully duplicated rows among missing timestamps:",
        missing_date_df.duplicated().sum()
    )

    # 3. Duplicate analysis with valid timestamps
    valid_df = df[df["date"].notna()].copy()

    print("\n3. VALID TIMESTAMP RECORDS")
    print("-" * 45)

    print("Valid timestamp rows:", len(valid_df))

    print(
        "Fully duplicated rows with valid timestamps:",
        valid_df.duplicated().sum()
    )

    # 4. Duplicate driver and timestamp combinations
    driver_time_duplicates = valid_df.duplicated(
        subset=["driver_number", "date"],
        keep=False
    )

    print("\n4. DRIVER + TIMESTAMP DUPLICATES")
    print("-" * 45)

    print(
        "Duplicate driver/timestamp rows:",
        driver_time_duplicates.sum()
    )

    # 5. Missing timestamp distribution by driver
    print("\n5. MISSING TIMESTAMPS BY DRIVER")
    print("-" * 45)

    print(
        missing_date_df.groupby("driver_number")
        .size()
        .to_string()
    )

    # 6. Drivers contributing to full duplicate groups
    print("\n6. DUPLICATE GROUPS BY DRIVER")
    print("-" * 45)

    duplicate_rows = df[full_duplicate_mask]

    if duplicate_rows.empty:
        print("No duplicate groups found.")
    else:
        print(
            duplicate_rows.groupby("driver_number")
            .size()
            .to_string()
        )

    # 7. Display sample duplicate records
    print("\n7. SAMPLE DUPLICATE RECORDS")
    print("-" * 45)

    if duplicate_rows.empty:
        print("No duplicate records to display.")
    else:
        print(
            duplicate_rows.head(10).to_string(index=False)
        )

    print("\n" + "=" * 65)
    print("DUPLICATE INVESTIGATION COMPLETED")
    print("=" * 65)


if __name__ == "__main__":
    investigate_duplicates()
