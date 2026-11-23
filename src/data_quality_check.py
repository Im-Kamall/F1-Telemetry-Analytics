
import pandas as pd
from pathlib import Path

# ============================================================
# PROJECT PATHS
# ============================================================

PROJECT_ROOT = Path(__file__).resolve().parent.parent

RAW_FILE = (
    PROJECT_ROOT
    / "data"
    / "raw"
    / "all_drivers_telemetry.csv"
)

CLEAN_FILE = (
    PROJECT_ROOT
    / "data"
    / "processed"
    / "all_drivers_telemetry_clean.csv"
)


# ============================================================
# DATASET INSPECTION
# ============================================================

def inspect_dataset(file_path, dataset_name):

    print("\n" + "=" * 65)
    print(f"DATA QUALITY REPORT: {dataset_name}")
    print("=" * 65)

    if not file_path.exists():
        print(f"ERROR: File not found: {file_path}")
        return None

    df = pd.read_csv(file_path)

    # Basic information
    print("\n1. DATASET INFORMATION")
    print("-" * 40)

    print(f"Rows: {len(df):,}")
    print(f"Columns: {len(df.columns)}")
    print(f"Memory usage: {df.memory_usage(deep=True).sum() / (1024 ** 2):.2f} MB")

    print("\nColumn names:")
    print(df.columns.tolist())

    # Missing values
    print("\n2. MISSING VALUE ANALYSIS")
    print("-" * 40)

    missing = df.isnull().sum()

    print(missing)
    print(f"\nTotal missing values: {missing.sum():,}")

    # Duplicate analysis
    print("\n3. DUPLICATE ANALYSIS")
    print("-" * 40)

    print(f"Fully identical rows: {df.duplicated().sum():,}")

    # Driver analysis
    if "driver_number" in df.columns:

        print("\n4. DRIVER ANALYSIS")
        print("-" * 40)

        print(f"Unique drivers: {df['driver_number'].nunique()}")

        print("\nRecords per driver:")
        print(
            df.groupby("driver_number")
            .size()
            .sort_index()
            .to_string()
        )

    # Timestamp analysis
    if "date" in df.columns:

        print("\n5. TIMESTAMP ANALYSIS")
        print("-" * 40)

        timestamps = pd.to_datetime(
            df["date"],
            errors="coerce",
            utc=True
        )

        print("Earliest timestamp:", timestamps.min())
        print("Latest timestamp:", timestamps.max())

        print(
            "Invalid or missing timestamps:",
            timestamps.isna().sum()
        )

        print(
            "Unique valid timestamps:",
            timestamps.nunique()
        )

    # Numeric statistics
    numeric_columns = df.select_dtypes(include="number").columns

    print("\n6. NUMERIC DATA SUMMARY")
    print("-" * 40)

    if len(numeric_columns) > 0:
        print(df[numeric_columns].describe().round(2).to_string())
    else:
        print("No numeric columns found.")

    return df


# ============================================================
# RAW VS CLEANED DATASET COMPARISON
# ============================================================

def compare_datasets(raw_df, clean_df):

    print("\n" + "=" * 65)
    print("RAW VS CLEANED DATASET COMPARISON")
    print("=" * 65)

    if raw_df is None or clean_df is None:
        print("Comparison skipped because a dataset could not be loaded.")
        return

    raw_rows = len(raw_df)
    clean_rows = len(clean_df)

    removed_rows = raw_rows - clean_rows

    print(f"\nRaw dataset rows: {raw_rows:,}")
    print(f"Cleaned dataset rows: {clean_rows:,}")
    print(f"Rows removed: {removed_rows:,}")

    if raw_rows > 0:
        removal_percentage = removed_rows / raw_rows * 100
        print(f"Removal percentage: {removal_percentage:.2f}%")

    print("\nDriver comparison:")

    if "driver_number" in raw_df.columns:

        print(
            "Raw unique drivers:",
            raw_df["driver_number"].nunique()
        )

        print(
            "Cleaned unique drivers:",
            clean_df["driver_number"].nunique()
        )

    print("\nTimestamp comparison:")

    for name, df in [
        ("Raw", raw_df),
        ("Cleaned", clean_df)
    ]:

        if "date" in df.columns:

            timestamps = pd.to_datetime(
                df["date"],
                errors="coerce",
                utc=True
            )

            print(f"\n{name} dataset:")
            print("Valid timestamps:", timestamps.notna().sum())
            print("Unique timestamps:", timestamps.nunique())


# ============================================================
# MAIN FUNCTION
# ============================================================

def main():

    print("\n" + "#" * 65)
    print("F1 TELEMETRY ANALYTICS")
    print("DATA QUALITY INSPECTION SYSTEM")
    print("#" * 65)

    raw_df = inspect_dataset(
        RAW_FILE,
        "RAW TELEMETRY"
    )

    clean_df = inspect_dataset(
        CLEAN_FILE,
        "CLEANED TELEMETRY"
    )

    compare_datasets(raw_df, clean_df)

    print("\n" + "=" * 65)
    print("DATA QUALITY INSPECTION COMPLETED")
    print("=" * 65)


if __name__ == "__main__":
    main()
