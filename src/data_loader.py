
"""
F1 Telemetry Analytics Platform
OpenF1 Data Collection Module

Collects public historical Formula 1 data
for the 2024 Bahrain Grand Prix qualifying session.

Downloads:
1. Session information
2. Driver information
3. Lap information
4. Telemetry for all session drivers
5. Separate Max Verstappen telemetry dataset
"""

from pathlib import Path

import pandas as pd
import requests


# --------------------------------------------------
# 1. PROJECT CONFIGURATION
# --------------------------------------------------

PROJECT_ROOT = Path(__file__).resolve().parent.parent

DATA_DIR = PROJECT_ROOT / "data" / "raw"

API_BASE_URL = "https://api.openf1.org/v1"

SESSION_KEY = 9468
VERSTAPPEN_NUMBER = 1

DATA_DIR.mkdir(parents=True, exist_ok=True)


# --------------------------------------------------
# 2. API DATA FETCHING
# --------------------------------------------------

def fetch_data(endpoint: str, params: dict) -> pd.DataFrame:
    """Fetch data from an OpenF1 API endpoint."""

    url = f"{API_BASE_URL}/{endpoint}"

    print(f"\nFetching {endpoint} data...")
    print(f"Parameters: {params}")

    response = requests.get(
        url,
        params=params,
        timeout=120
    )

    response.raise_for_status()

    data = response.json()

    if not data:
        print(f"No data returned for {endpoint}.")
        return pd.DataFrame()

    df = pd.DataFrame(data)

    print(f"Retrieved {len(df):,} records.")

    return df


# --------------------------------------------------
# 3. SAVE DATA
# --------------------------------------------------

def save_data(df: pd.DataFrame, filename: str) -> None:
    """Save a DataFrame as a CSV file."""

    if df.empty:
        print(f"Skipping {filename}: no data available.")
        return

    file_path = DATA_DIR / filename

    df.to_csv(
        file_path,
        index=False
    )

    print(f"Saved: {file_path}")
    print(f"Rows: {len(df):,}")


# --------------------------------------------------
# 4. COLLECT SESSION INFORMATION
# --------------------------------------------------

def collect_session_data():
    """Download session, driver and lap information."""

    session_df = fetch_data(
        "sessions",
        {"session_key": SESSION_KEY}
    )

    save_data(
        session_df,
        "session_info.csv"
    )

    drivers_df = fetch_data(
        "drivers",
        {"session_key": SESSION_KEY}
    )

    save_data(
        drivers_df,
        "drivers.csv"
    )

    laps_df = fetch_data(
        "laps",
        {"session_key": SESSION_KEY}
    )

    save_data(
        laps_df,
        "laps.csv"
    )

    return drivers_df


# --------------------------------------------------
# 5. COLLECT ALL DRIVER TELEMETRY
# --------------------------------------------------

def collect_all_driver_telemetry(drivers_df):
    """
    Download car telemetry separately for every driver
    participating in the session.
    """

    if drivers_df.empty:
        raise ValueError(
            "Driver dataset is empty. Cannot collect telemetry."
        )

    if "driver_number" not in drivers_df.columns:
        raise ValueError(
            "driver_number column is missing from drivers data."
        )

    driver_numbers = sorted(
        drivers_df["driver_number"]
        .dropna()
        .astype(int)
        .unique()
    )

    print("\n" + "=" * 55)
    print("COLLECTING TELEMETRY FOR ALL DRIVERS")
    print("=" * 55)

    telemetry_datasets = []

    for index, driver_number in enumerate(
        driver_numbers,
        start=1
    ):

        driver_name = "Unknown"

        if "full_name" in drivers_df.columns:

            matching_driver = drivers_df[
                drivers_df["driver_number"].astype(int)
                == driver_number
            ]

            if not matching_driver.empty:
                driver_name = matching_driver.iloc[0]["full_name"]

        print(
            f"\nDriver {index}/{len(driver_numbers)}: "
            f"{driver_name} (#{driver_number})"
        )

        try:

            telemetry_df = fetch_data(
                "car_data",
                {
                    "session_key": SESSION_KEY,
                    "driver_number": driver_number
                }
            )

            if not telemetry_df.empty:
                telemetry_datasets.append(telemetry_df)

        except requests.exceptions.RequestException as error:

            print(
                f"Could not collect driver #{driver_number}: {error}"
            )

    if not telemetry_datasets:
        raise RuntimeError(
            "No driver telemetry was collected."
        )

    # Combine every driver's telemetry
    all_telemetry = pd.concat(
        telemetry_datasets,
        ignore_index=True
    )

    # Sort records chronologically
    all_telemetry["date"] = pd.to_datetime(
        all_telemetry["date"],
        errors="coerce",
        utc=True
    )

    all_telemetry = all_telemetry.sort_values(
        ["driver_number", "date"]
    ).reset_index(drop=True)

    save_data(
        all_telemetry,
        "all_drivers_telemetry.csv"
    )

    # Preserve the existing Verstappen dataset
    verstappen_telemetry = all_telemetry[
        all_telemetry["driver_number"] == VERSTAPPEN_NUMBER
    ].copy()

    save_data(
        verstappen_telemetry,
        "verstappen_telemetry.csv"
    )

    print("\nAll-driver telemetry collection summary:")
    print(f"Drivers collected: {len(telemetry_datasets)}")
    print(f"Total telemetry records: {len(all_telemetry):,}")

    return all_telemetry


# --------------------------------------------------
# 6. MAIN DATA COLLECTION PIPELINE
# --------------------------------------------------

def load_session_data():

    print("=" * 55)
    print("F1 TELEMETRY DATA COLLECTION")
    print("2024 Bahrain Grand Prix - Qualifying")
    print("=" * 55)

    # Download session, driver and lap information
    drivers_df = collect_session_data()

    # Download telemetry for every driver
    all_telemetry = collect_all_driver_telemetry(
        drivers_df
    )

    print("\n" + "=" * 55)
    print("F1 DATA COLLECTION COMPLETED!")
    print("=" * 55)

    return all_telemetry


# --------------------------------------------------
# 7. MAIN EXECUTION
# --------------------------------------------------

if __name__ == "__main__":

    try:
        load_session_data()

    except requests.exceptions.RequestException as error:
        print(f"\nAPI connection error: {error}")

    except Exception as error:
        print(f"\nUnexpected error: {error}")
