# F1 Telemetry Analytics Platform

An end-to-end Formula 1 telemetry and qualifying performance analytics project built using Python, Pandas, NumPy, Plotly and Streamlit.

The project analyses publicly available Formula 1 data from the **2024 Bahrain Grand Prix Qualifying** session using the OpenF1 API.

## Live Dashboard

**Coming soon:** The interactive Streamlit dashboard will be published here.

## Project Overview

The platform explores driver telemetry, lap performance, sector performance, data quality and comparative driver statistics across all 20 drivers.

### Key Features

- Multi-driver telemetry analysis
- Speed, throttle, brake, RPM and gear analysis
- Driver coverage and telemetry data-quality checks
- Lap-time and sector-time analysis
- Fastest recorded lap comparisons
- Exploratory representative-lap analysis
- Driver lap consistency and sector performance comparisons
- Combined driver performance analysis
- Interactive Streamlit dashboard
- CSV exports of processed analytical results

## Dataset

| Attribute | Details |
|---|---|
| Event | 2024 Bahrain Grand Prix |
| Session | Qualifying |
| Circuit | Bahrain International Circuit, Sakhir |
| Session Key | 9468 |
| Meeting Key | 1229 |
| Telemetry Drivers | 20 |
| Raw Telemetry Records | 350,480 |
| Cleaned Telemetry Records | 349,500 |
| Data Source | OpenF1 API |

The dataset contains publicly available historical data. It is not proprietary Formula 1 team engineering telemetry.

## Technology Stack

- Python
- Pandas
- NumPy
- Matplotlib
- Plotly
- Streamlit
- Jupyter Notebook
- OpenF1 API

## Project Structure

```text
F1-Telemetry-Analytics/
├── dashboard/
│   └── app.py
├── data/
│   ├── raw/
│   └── processed/
├── notebooks/
├── reports/
├── src/
├── tests/
├── .gitignore
├── README.md
└── requirements.txt
```

## Running the Dashboard Locally

### 1. Clone the repository

```bash
git clone YOUR_GITHUB_REPOSITORY_URL
cd F1-Telemetry-Analytics
```

### 2. Create and activate a virtual environment

```bash
python -m venv .venv
```

Windows PowerShell:

```powershell
.venv\Scripts\Activate.ps1
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Launch the dashboard

```bash
python -m streamlit run dashboard/app.py
```

The dashboard will normally be available at:

```text
http://localhost:8501
```

## Analysis Scripts

The `src/` directory contains scripts for:

- Data collection and loading
- Telemetry analysis
- Data-quality checks
- Duplicate-record investigation
- Driver coverage analysis
- Lap quality and performance analysis
- Lap distribution analysis
- Near-best lap analysis
- Representative-lap analysis
- Candidate-lap consistency
- Sector performance analysis
- Combined driver performance

Run an individual analysis script from the project root:

```bash
python src/data_analysis.py
```

## Important Methodology Notes

- Missing-timestamp telemetry records are excluded from the cleaned dataset; the original raw data is preserved locally.
- The representative-lap analysis uses an exploratory 85–95 second filter. This is not an official FIA clean-lap classification.
- Candidate-lap samples are relatively small and are not fully controlled for tyre condition, fuel load, traffic or track evolution.
- Lap consistency and combined sector rankings are exploratory comparisons, not definitive measures of driver ability.
- Telemetry averages can include stationary or inactive periods and should be interpreted carefully.

## Project Status

Core data collection, data cleaning, exploratory analysis, driver comparisons and interactive dashboard development have been completed.

Final documentation, validation and public dashboard deployment are being