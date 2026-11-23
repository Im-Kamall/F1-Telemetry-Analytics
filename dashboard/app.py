
"""
F1 Telemetry Analytics Platform
Interactive Streamlit Dashboard

Event: 2024 Bahrain Grand Prix - Qualifying
Data source: OpenF1 API
Telemetry drivers: All 20 drivers + Max Verstappen detailed analysis
"""

from pathlib import Path

import pandas as pd
import plotly.express as px
import streamlit as st


# ==================================================
# 1. CONFIGURATION
# ==================================================

PROJECT_ROOT = Path(__file__).resolve().parent.parent

RAW_DIR = PROJECT_ROOT / "data" / "raw"
PROCESSED_DIR = PROJECT_ROOT / "data" / "processed"

st.set_page_config(
    page_title="F1 Telemetry Analytics",
    page_icon="🏎️",
    layout="wide"
)


# ==================================================
# 2. LOAD DATA
# ==================================================

@st.cache_data
def load_data():

    # Raw datasets
    drivers = pd.read_csv(RAW_DIR / "drivers.csv")
    laps = pd.read_csv(RAW_DIR / "laps.csv")

    telemetry = pd.read_csv(
        RAW_DIR / "verstappen_telemetry.csv"
    )

    # Processed datasets
    leaderboard_path = (
        PROCESSED_DIR / "fastest_lap_leaderboard.csv"
    )

    all_drivers_path = (
        PROCESSED_DIR / "all_drivers_summary.csv"
    )

    if leaderboard_path.exists():
        leaderboard = pd.read_csv(leaderboard_path)
    else:
        leaderboard = pd.DataFrame()

    if all_drivers_path.exists():
        all_drivers_summary = pd.read_csv(all_drivers_path)
    else:
        all_drivers_summary = pd.DataFrame()

    # Combined candidate-lap and sector performance dataset
    combined_performance_path = (
        PROCESSED_DIR / "combined_driver_performance.csv"
    )

    if combined_performance_path.exists():
        combined_performance = pd.read_csv(
            combined_performance_path
        )
    else:
        combined_performance = pd.DataFrame()

    # Convert telemetry timestamp
    telemetry["date"] = pd.to_datetime(
        telemetry["date"],
        errors="coerce",
        utc=True
    )

    # Convert telemetry measurements to numeric
    numeric_columns = [
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

    telemetry = (
        telemetry
        .dropna(subset=["date"])
        .sort_values("date")
    )

    # Convert comparison dataset columns
    if not all_drivers_summary.empty:

        comparison_numeric_columns = [
            "driver_number",
            "telemetry_records",
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
            "average_gear",
            "maximum_gear"
        ]

        for column in comparison_numeric_columns:
            if column in all_drivers_summary.columns:
                all_drivers_summary[column] = pd.to_numeric(
                    all_drivers_summary[column],
                    errors="coerce"
                )

    # Convert combined performance measurements to numeric values
    if not combined_performance.empty:

        combined_numeric_columns = [
            "driver_number",
            "candidate_laps",
            "best_lap_seconds",
            "average_lap_seconds",
            "median_lap_seconds",
            "std_lap_seconds",
            "worst_lap_seconds",
            "lap_time_range_seconds",
            "average_minus_best_seconds",
            "average_pace_rank",
            "best_lap_rank",
            "sector_1_average",
            "sector_1_best",
            "sector_1_std",
            "sector_2_average",
            "sector_2_best",
            "sector_2_std",
            "sector_3_average",
            "sector_3_best",
            "sector_3_std",
            "sector_1_share_pct",
            "sector_2_share_pct",
            "sector_3_share_pct",
            "sector_1_rank",
            "sector_2_rank",
            "sector_3_rank",
            "sector_rank_total",
            "average_sector_rank",
            "combined_sector_rank",
            "lap_consistency_rank"
        ]

        for column in combined_numeric_columns:
            if column in combined_performance.columns:
                combined_performance[column] = pd.to_numeric(
                    combined_performance[column],
                    errors="coerce"
                )

    return (
        drivers,
        laps,
        telemetry,
        leaderboard,
        all_drivers_summary,
        combined_performance
    )


try:

    (
        drivers,
        laps,
        telemetry,
        leaderboard,
        all_drivers_summary,
        combined_performance
    ) = load_data()

except Exception as error:

    st.error(f"Unable to load project datasets: {error}")
    st.stop()


# ==================================================
# 3. HEADER
# ==================================================

st.title("🏎️ F1 TELEMETRY ANALYTICS")

st.markdown(
    "**Formula 1 Performance Analysis | 2024 Bahrain Grand Prix**"
)

st.caption(
    "Historical qualifying data | OpenF1 API | "
    "20 drivers | Max Verstappen detailed telemetry"
)

st.divider()


# ==================================================
# 4. SIDEBAR NAVIGATION
# ==================================================

st.sidebar.title("Dashboard Navigation")

page = st.sidebar.radio(
    "Select Dashboard Section",
    [
        "Overview",
        "Qualifying Analysis",
        "Telemetry Analysis",
        "Driver Comparison",
        "Combined Performance",
        "Raw Data Explorer"
    ]
)

st.sidebar.divider()

st.sidebar.info(
    "Data source: OpenF1 API\n\n"
    "Session: 2024 Bahrain Qualifying\n\n"
    "Drivers analysed: 20\n\n"
    "Detailed telemetry: Max Verstappen"
)

st.sidebar.caption(
    "F1 Telemetry Analytics Platform"
)


# ==================================================
# 5. OVERVIEW
# ==================================================

if page == "Overview":

    st.header("Performance Overview")

    col1, col2, col3, col4 = st.columns(4)

    col1.metric(
        "Total Drivers",
        len(drivers)
    )

    col2.metric(
        "Total Lap Records",
        len(laps)
    )

    col3.metric(
        "Verstappen Telemetry Records",
        f"{len(telemetry):,}"
    )

    fastest_time = (
        leaderboard["lap_duration"].min()
        if (
            not leaderboard.empty
            and "lap_duration" in leaderboard.columns
        )
        else None
    )

    col4.metric(
        "Fastest Recorded Lap",
        f"{fastest_time:.3f} s"
        if pd.notna(fastest_time)
        else "N/A"
    )

    st.divider()

    # Top 5 qualifying drivers
    st.subheader("Top 5 Qualifying Drivers")

    if not leaderboard.empty:

        top_five = leaderboard.head(5)

        fig = px.bar(
            top_five,
            x="full_name",
            y="lap_duration",
            color="team_name",
            text="lap_duration",
            title="Fastest Recorded Lap Times",
            labels={
                "full_name": "Driver",
                "lap_duration": "Lap Time (seconds)",
                "team_name": "Team"
            }
        )

        fig.update_traces(
            texttemplate="%{text:.3f}"
        )

        fig.update_layout(
            xaxis_title="Driver",
            yaxis_title="Lap Time (seconds)"
        )

        st.plotly_chart(
            fig,
            use_container_width=True
        )

    else:

        st.warning("Leaderboard dataset is unavailable.")

    # Telemetry snapshot
    st.subheader("Max Verstappen Telemetry Snapshot")

    col1, col2, col3 = st.columns(3)

    col1.metric(
        "Maximum Speed",
        f"{telemetry['speed'].max():.0f} km/h"
    )

    col2.metric(
        "Maximum RPM",
        f"{telemetry['rpm'].max():,.0f}"
    )

    col3.metric(
        "Maximum Gear",
        f"{telemetry['n_gear'].max():.0f}"
    )

    st.divider()

    st.subheader("Multi-Driver Dataset")

    if not all_drivers_summary.empty:

        col1, col2 = st.columns(2)

        col1.metric(
            "Drivers Analysed",
            all_drivers_summary["driver_number"].nunique()
        )

        col2.metric(
            "Total Telemetry Records",
            f"{all_drivers_summary['telemetry_records'].sum():,}"
        )

    else:

        st.warning("Multi-driver summary is unavailable.")


# ==================================================
# 6. QUALIFYING ANALYSIS
# ==================================================

elif page == "Qualifying Analysis":

    st.header("Qualifying Performance Analysis")

    if leaderboard.empty:

        st.warning("Leaderboard data is not available.")

    else:

        # Team filter
        selected_team = st.selectbox(
            "Filter by Team",
            ["All Teams"] + sorted(
                leaderboard["team_name"]
                .dropna()
                .unique()
                .tolist()
            )
        )

        filtered = leaderboard.copy()

        if selected_team != "All Teams":

            filtered = filtered[
                filtered["team_name"] == selected_team
            ]

        # Leaderboard table
        st.subheader("Fastest Recorded Lap Leaderboard")

        st.dataframe(
            filtered,
            use_container_width=True,
            hide_index=True
        )

        # Lap time comparison
        fig = px.bar(
            filtered.sort_values("lap_duration"),
            x="full_name",
            y="lap_duration",
            color="team_name",
            hover_data=[
                column
                for column in ["lap_number", "position"]
                if column in filtered.columns
            ],
            title="Driver Lap Time Comparison",
            labels={
                "full_name": "Driver",
                "lap_duration": "Lap Time (seconds)",
                "team_name": "Team"
            }
        )

        st.plotly_chart(
            fig,
            use_container_width=True
        )

        # Sector time analysis
        st.divider()

        st.subheader("Sector Time Analysis")

        sector_columns = [
            "duration_sector_1",
            "duration_sector_2",
            "duration_sector_3"
        ]

        available_sector_columns = [
            column
            for column in sector_columns
            if column in laps.columns
        ]

        if available_sector_columns:

            sector_data = laps[
                ["driver_number"] + available_sector_columns
            ].copy()

            sector_data = sector_data.merge(
                drivers[
                    ["driver_number", "name_acronym"]
                ],
                on="driver_number",
                how="left"
            )

            sector_data = sector_data.dropna(
                subset=available_sector_columns,
                how="all"
            )

            st.dataframe(
                sector_data,
                use_container_width=True,
                hide_index=True
            )

        else:

            st.warning("Sector timing columns are unavailable.")


# ==================================================
# 7. VERSTAPPEN TELEMETRY ANALYSIS
# ==================================================

elif page == "Telemetry Analysis":

    st.header("Max Verstappen — Car Telemetry")

    # --------------------------------------------------
    # 7.1 TELEMETRY KPI CARDS
    # --------------------------------------------------

    col1, col2, col3, col4 = st.columns(4)

    col1.metric(
        "Maximum Speed",
        f"{telemetry['speed'].max():.0f} km/h"
    )

    col2.metric(
        "Average Speed",
        f"{telemetry['speed'].mean():.1f} km/h"
    )

    col3.metric(
        "Maximum RPM",
        f"{telemetry['rpm'].max():,.0f}"
    )

    col4.metric(
        "Maximum Gear",
        f"{telemetry['n_gear'].max():.0f}"
    )

    st.divider()

    # --------------------------------------------------
    # 7.2 SPEED ANALYSIS
    # --------------------------------------------------

    st.subheader("Speed Analysis")

    speed_fig = px.line(
        telemetry,
        x="date",
        y="speed",
        title="Car Speed Over Time",
        labels={
            "date": "Timestamp",
            "speed": "Speed (km/h)"
        }
    )

    speed_fig.update_layout(
        hovermode="x unified"
    )

    st.plotly_chart(
        speed_fig,
        use_container_width=True
    )

    # --------------------------------------------------
    # 7.3 THROTTLE ANALYSIS
    # --------------------------------------------------

    st.subheader("Throttle Analysis")

    throttle_fig = px.line(
        telemetry,
        x="date",
        y="throttle",
        title="Throttle Telemetry Over Time",
        labels={
            "date": "Timestamp",
            "throttle": "Throttle Value (Raw)"
        }
    )

    throttle_fig.update_layout(
        hovermode="x unified"
    )

    st.plotly_chart(
        throttle_fig,
        use_container_width=True
    )

    st.caption(
        "Throttle is displayed using raw dataset values. "
        "Its encoding should be verified before interpreting "
        "it as a percentage."
    )

    # --------------------------------------------------
    # 7.4 ENGINE RPM ANALYSIS
    # --------------------------------------------------

    st.subheader("Engine RPM Analysis")

    rpm_fig = px.line(
        telemetry,
        x="date",
        y="rpm",
        title="Engine RPM Over Time",
        labels={
            "date": "Timestamp",
            "rpm": "RPM"
        }
    )

    rpm_fig.update_layout(
        hovermode="x unified"
    )

    st.plotly_chart(
        rpm_fig,
        use_container_width=True
    )

    # --------------------------------------------------
    # 7.5 GEAR DISTRIBUTION
    # --------------------------------------------------

    st.subheader("Gear Distribution")

    gear_data = (
        telemetry["n_gear"]
        .value_counts()
        .sort_index()
        .reset_index()
    )

    gear_data.columns = [
        "Gear",
        "Records"
    ]

    gear_fig = px.bar(
        gear_data,
        x="Gear",
        y="Records",
        title="Gear Usage Distribution",
        text="Records",
        labels={
            "Gear": "Gear",
            "Records": "Telemetry Records"
        }
    )

    gear_fig.update_layout(
        xaxis=dict(
            tickmode="linear",
            dtick=1
        )
    )

    st.plotly_chart(
        gear_fig,
        use_container_width=True
    )

    # --------------------------------------------------
    # 7.6 BRAKE ANALYSIS
    # --------------------------------------------------

    st.divider()

    st.header("Brake Application Analysis")

    st.caption(
        "Analysis of raw brake telemetry values from "
        "Max Verstappen's 2024 Bahrain qualifying session."
    )

    brake_active = telemetry[
        telemetry["brake"] > 0
    ].copy()

    brake_percentage = (
        len(brake_active) / len(telemetry) * 100
        if len(telemetry) > 0
        else 0
    )

    col1, col2, col3 = st.columns(3)

    col1.metric(
        "Total Brake Records",
        f"{len(brake_active):,}"
    )

    col2.metric(
        "Non-Zero Brake Records",
        f"{brake_percentage:.2f}%"
    )

    col3.metric(
        "Maximum Raw Brake Value",
        f"{telemetry['brake'].max():.0f}"
    )

    # --------------------------------------------------
    # 7.7 BRAKE VALUE DISTRIBUTION
    # --------------------------------------------------

    st.subheader("Brake Value Distribution")

    brake_distribution = (
        telemetry["brake"]
        .value_counts(dropna=False)
        .sort_index()
        .reset_index()
    )

    brake_distribution.columns = [
        "Brake Value",
        "Record Count"
    ]

    brake_fig = px.bar(
        brake_distribution,
        x="Brake Value",
        y="Record Count",
        text="Record Count",
        title="Distribution of Raw Brake Values",
        labels={
            "Brake Value": "Brake Value (Raw)",
            "Record Count": "Number of Records"
        }
    )

    st.plotly_chart(
        brake_fig,
        use_container_width=True
    )

    st.dataframe(
        brake_distribution,
        use_container_width=True,
        hide_index=True
    )

    # --------------------------------------------------
    # 7.8 BRAKE APPLICATION OVER TIME
    # --------------------------------------------------

    st.subheader("Brake Application Over Time")

    brake_time_fig = px.line(
        telemetry,
        x="date",
        y="brake",
        title="Brake Telemetry Over Time",
        labels={
            "date": "Timestamp",
            "brake": "Brake Value (Raw)"
        }
    )

    brake_time_fig.update_layout(
        hovermode="x unified"
    )

    st.plotly_chart(
        brake_time_fig,
        use_container_width=True
    )

    # --------------------------------------------------
    # 7.9 SPEED VS BRAKING
    # --------------------------------------------------

    st.subheader("Speed vs Brake Application")

    st.write(
        "This chart examines the relationship between "
        "car speed and recorded brake values."
    )

    speed_brake_fig = px.scatter(
        telemetry,
        x="speed",
        y="brake",
        color="brake",
        hover_data=[
            "date",
            "rpm",
            "n_gear"
        ],
        title="Speed vs Raw Brake Value",
        labels={
            "speed": "Speed (km/h)",
            "brake": "Brake Value (Raw)",
            "rpm": "Engine RPM",
            "n_gear": "Gear"
        },
        opacity=0.55
    )

    st.plotly_chart(
        speed_brake_fig,
        use_container_width=True
    )

    # --------------------------------------------------
    # 7.10 BRAKE ANALYSIS INSIGHTS
    # --------------------------------------------------

    st.subheader("Brake Analysis Insights")

    if not brake_distribution.empty:

        st.write(
            f"- Total telemetry samples: {len(telemetry):,}"
        )

        st.write(
            f"- Samples with non-zero brake values: "
            f"{len(brake_active):,}"
        )

        st.write(
            f"- Non-zero brake sample share: "
            f"{brake_percentage:.2f}%"
        )

        st.write(
            f"- Distinct brake values: "
            f"{telemetry['brake'].nunique()}"
        )

    st.info(
        "Interpretation note: The brake field contains raw values. "
        "Do not interpret these values as percentages or braking "
        "force until their encoding and units have been verified."
    )

# 8. MULTI-DRIVER COMPARISON
# ==================================================

elif page == "Driver Comparison":

    st.header("🏁 Multi-Driver Telemetry Comparison")

    st.markdown(
        "Compare telemetry statistics across all 20 drivers "
        "from the 2024 Bahrain Grand Prix qualifying session."
    )

    if all_drivers_summary.empty:

        st.warning(
            "Multi-driver analysis dataset is unavailable. "
            "Run src/data_analysis.py first."
        )

    else:

        comparison_data = all_drivers_summary.copy()

        # --------------------------------------------------
        # 8.1 TEAM FILTER
        # --------------------------------------------------

        teams = sorted(
            comparison_data["team_name"]
            .dropna()
            .unique()
            .tolist()
        )

        selected_team = st.selectbox(
            "Select Team",
            ["All Teams"] + teams
        )

        if selected_team != "All Teams":

            comparison_data = comparison_data[
                comparison_data["team_name"] == selected_team
            ]

        # --------------------------------------------------
        # 8.2 DRIVER FILTER
        # --------------------------------------------------

        available_drivers = sorted(
            comparison_data["full_name"]
            .dropna()
            .unique()
            .tolist()
        )

        default_drivers = (
            comparison_data
            .sort_values(
                "average_speed",
                ascending=False
            )
            .head(5)["full_name"]
            .tolist()
        )

        selected_drivers = st.multiselect(
            "Select Drivers to Compare",
            options=available_drivers,
            default=default_drivers
        )

        selected_data = comparison_data[
            comparison_data["full_name"].isin(selected_drivers)
        ].copy()

        if selected_data.empty:

            st.info(
                "Select at least one driver to display comparisons."
            )

        else:

            # --------------------------------------------------
            # 8.3 COMPARISON KPI CARDS
            # --------------------------------------------------

            st.subheader("Comparison Overview")

            col1, col2, col3 = st.columns(3)

            col1.metric(
                "Selected Drivers",
                len(selected_data)
            )

            col2.metric(
                "Highest Average Speed",
                f"{selected_data['average_speed'].max():.2f} km/h"
            )

            col3.metric(
                "Highest Recorded Speed",
                f"{selected_data['maximum_speed'].max():.0f} km/h"
            )

            st.divider()

            # --------------------------------------------------
            # 8.4 AVERAGE SPEED COMPARISON
            # --------------------------------------------------

            st.subheader("Average Speed Comparison")

            speed_fig = px.bar(
                selected_data.sort_values(
                    "average_speed",
                    ascending=False
                ),
                x="full_name",
                y="average_speed",
                color="team_name",
                text="average_speed",
                hover_data=[
                    "maximum_speed",
                    "speed_std"
                ],
                title="Average Speed by Driver",
                labels={
                    "full_name": "Driver",
                    "average_speed": "Average Speed (km/h)",
                    "team_name": "Team"
                }
            )

            speed_fig.update_traces(
                texttemplate="%{text:.2f}"
            )

            st.plotly_chart(
                speed_fig,
                use_container_width=True
            )

            # --------------------------------------------------
            # 8.5 MAXIMUM SPEED COMPARISON
            # --------------------------------------------------

            st.subheader("Maximum Speed Comparison")

            max_speed_fig = px.bar(
                selected_data.sort_values(
                    "maximum_speed",
                    ascending=False
                ),
                x="full_name",
                y="maximum_speed",
                color="team_name",
                text="maximum_speed",
                title="Maximum Recorded Speed",
                labels={
                    "full_name": "Driver",
                    "maximum_speed": "Maximum Speed (km/h)",
                    "team_name": "Team"
                }
            )

            st.plotly_chart(
                max_speed_fig,
                use_container_width=True
            )

            # --------------------------------------------------
            # 8.6 ENGINE RPM COMPARISON
            # --------------------------------------------------

            st.subheader("Engine RPM Comparison")

            rpm_fig = px.bar(
                selected_data.sort_values(
                    "average_rpm",
                    ascending=False
                ),
                x="full_name",
                y="average_rpm",
                color="team_name",
                text="average_rpm",
                title="Average Engine RPM by Driver",
                labels={
                    "full_name": "Driver",
                    "average_rpm": "Average RPM",
                    "team_name": "Team"
                }
            )

            st.plotly_chart(
                rpm_fig,
                use_container_width=True
            )

            # --------------------------------------------------
            # 8.7 THROTTLE COMPARISON
            # --------------------------------------------------

            st.subheader("Throttle Telemetry Comparison")

            throttle_fig = px.bar(
                selected_data.sort_values(
                    "average_throttle",
                    ascending=False
                ),
                x="full_name",
                y="average_throttle",
                color="team_name",
                text="average_throttle",
                title="Average Raw Throttle Value",
                labels={
                    "full_name": "Driver",
                    "average_throttle": "Average Throttle (Raw)",
                    "team_name": "Team"
                }
            )

            st.plotly_chart(
                throttle_fig,
                use_container_width=True
            )

            # --------------------------------------------------
            # 8.8 BRAKE ACTIVITY COMPARISON
            # --------------------------------------------------

            st.subheader("Brake Activity Comparison")

            brake_fig = px.bar(
                selected_data.sort_values(
                    "brake_active_percentage",
                    ascending=False
                ),
                x="full_name",
                y="brake_active_percentage",
                color="team_name",
                text="brake_active_percentage",
                title=(
                    "Share of Telemetry Records "
                    "with Non-Zero Brake Values"
                ),
                labels={
                    "full_name": "Driver",
                    "brake_active_percentage": (
                        "Non-Zero Brake Records (%)"
                    ),
                    "team_name": "Team"
                }
            )

            brake_fig.update_traces(
                texttemplate="%{text:.2f}%"
            )

            st.plotly_chart(
                brake_fig,
                use_container_width=True
            )

            # --------------------------------------------------
            # 8.9 DETAILED DRIVER STATISTICS
            # --------------------------------------------------

            st.divider()

            st.subheader("Detailed Driver Statistics")

            display_columns = [
                "driver_number",
                "full_name",
                "team_name",
                "telemetry_records",
                "average_speed",
                "maximum_speed",
                "speed_std",
                "average_rpm",
                "average_throttle",
                "average_brake",
                "brake_active_percentage",
                "average_gear"
            ]

            st.dataframe(
                selected_data[display_columns].sort_values(
                    "average_speed",
                    ascending=False
                ),
                use_container_width=True,
                hide_index=True
            )

            # --------------------------------------------------
            # 8.10 DATA INTERPRETATION
            # --------------------------------------------------

            st.divider()

            st.subheader("Data Interpretation")

            st.info(
                "Average speed and other statistics are calculated "
                "across available telemetry records, including "
                "stationary samples. They should not be treated as "
                "direct driver-performance rankings. Throttle and "
                "brake are raw sensor values, not verified percentages "
                "or physical forces. Brake activity percentage "
                "represents the share of records with a non-zero "
                "brake value."
            )

            st.caption(
                "Source: OpenF1 historical public telemetry. "
                "These data are not proprietary F1 team engineering data."
            )


# ==================================================

# 9. COMBINED CANDIDATE PERFORMANCE
# ==================================================

elif page == "Combined Performance":

    st.header("Combined Driver Performance")
    st.markdown(
        "Explore candidate-lap pace, sector performance, and lap-time "
        "variation for the 2024 Bahrain qualifying dataset."
    )

    if combined_performance.empty:
        st.warning(
            "Combined performance dataset is unavailable. "
            "Run src/combined_driver_performance.py first."
        )
    else:
        required_columns = [
            "driver_number", "full_name", "team_name", "candidate_laps",
            "best_lap_seconds", "average_lap_seconds", "std_lap_seconds",
            "sector_1_average", "sector_2_average", "sector_3_average",
            "average_pace_rank", "combined_sector_rank"
        ]

        missing_columns = [
            column for column in required_columns
            if column not in combined_performance.columns
        ]

        if missing_columns:
            st.error(
                "Combined performance CSV is missing required columns: "
                + ", ".join(missing_columns)
            )
        else:
            performance_data = combined_performance.copy()

            teams = sorted(
                performance_data["team_name"].dropna().unique().tolist()
            )

            selected_team = st.selectbox(
                "Filter by Team",
                ["All Teams"] + teams,
                key="combined_performance_team"
            )

            if selected_team != "All Teams":
                performance_data = performance_data[
                    performance_data["team_name"] == selected_team
                ]

            driver_options = (
                performance_data["full_name"].dropna().tolist()
            )

            default_selection = (
                performance_data.sort_values("average_pace_rank")
                .head(min(5, len(performance_data)))["full_name"].tolist()
            )

            selected_drivers = st.multiselect(
                "Select drivers to compare",
                options=driver_options,
                default=default_selection,
                key="combined_performance_drivers"
            )

            selected_data = performance_data[
                performance_data["full_name"].isin(selected_drivers)
            ].copy()

            if selected_data.empty:
                st.info("Select at least one driver to view the analysis.")
            else:
                # KPI cards describe the currently selected drivers.
                fastest_average = selected_data.loc[
                    selected_data["average_lap_seconds"].idxmin()
                ]

                fastest_best = selected_data.loc[
                    selected_data["best_lap_seconds"].idxmin()
                ]

                best_sector_rank = selected_data.loc[
                    selected_data["combined_sector_rank"].idxmin()
                ]

                kpi1, kpi2, kpi3, kpi4 = st.columns(4)

                kpi1.metric(
                    "Drivers Selected", len(selected_data)
                )

                kpi2.metric(
                    "Fastest Average Candidate Lap",
                    f"{fastest_average['average_lap_seconds']:.3f} s",
                    fastest_average["full_name"]
                )

                kpi3.metric(
                    "Fastest Best Candidate Lap",
                    f"{fastest_best['best_lap_seconds']:.3f} s",
                    fastest_best["full_name"]
                )

                kpi4.metric(
                    "Best Combined Sector Rank",
                    f"{int(best_sector_rank['combined_sector_rank'])}",
                    best_sector_rank["full_name"]
                )

                st.divider()
                st.subheader("Average Candidate Lap Comparison")

                pace_plot = selected_data.sort_values(
                    "average_lap_seconds", ascending=True
                )

                pace_fig = px.bar(
                    pace_plot,
                    x="full_name",
                    y="average_lap_seconds",
                    color="team_name",
                    text="average_lap_seconds",
                    hover_data=["candidate_laps", "best_lap_seconds"],
                    labels={
                        "full_name": "Driver",
                        "average_lap_seconds": "Average candidate lap (s)",
                        "team_name": "Team",
                        "candidate_laps": "Candidate laps",
                        "best_lap_seconds": "Best candidate lap (s)"
                    },
                    title="Average Candidate Lap Time (Lower is Faster)"
                )

                pace_fig.update_traces(texttemplate="%{text:.3f}")

                st.plotly_chart(
                    pace_fig,
                    use_container_width=True
                )

                st.subheader("Sector-by-Sector Average Comparison")

                sector_long = selected_data.melt(
                    id_vars=["full_name", "team_name"],
                    value_vars=[
                        "sector_1_average",
                        "sector_2_average",
                        "sector_3_average"
                    ],
                    var_name="sector",
                    value_name="average_sector_seconds"
                )

                sector_long["sector"] = sector_long["sector"].map({
                    "sector_1_average": "Sector 1",
                    "sector_2_average": "Sector 2",
                    "sector_3_average": "Sector 3"
                })

                sector_fig = px.bar(
                    sector_long,
                    x="full_name",
                    y="average_sector_seconds",
                    color="sector",
                    barmode="group",
                    hover_data=["team_name"],
                    labels={
                        "full_name": "Driver",
                        "average_sector_seconds": "Average sector time (s)",
                        "sector": "Sector",
                        "team_name": "Team"
                    },
                    title="Average Sector Times by Driver (Lower is Faster)"
                )

                st.plotly_chart(
                    sector_fig,
                    use_container_width=True
                )

                st.subheader("Combined Sector Ranking")

                sector_rank_columns = [
                    "driver_number", "full_name", "team_name",
                    "sector_1_average", "sector_1_rank",
                    "sector_2_average", "sector_2_rank",
                    "sector_3_average", "sector_3_rank",
                    "average_sector_rank", "combined_sector_rank"
                ]

                available_rank_columns = [
                    column for column in sector_rank_columns
                    if column in selected_data.columns
                ]

                sector_rank_table = selected_data[
                    available_rank_columns
                ].sort_values("combined_sector_rank")

                st.dataframe(
                    sector_rank_table.round(3),
                    use_container_width=True,
                    hide_index=True
                )

                st.subheader("Candidate Lap Variation")

                if "std_lap_seconds" in selected_data.columns:

                    consistency_plot = selected_data.sort_values(
                        "std_lap_seconds", ascending=True
                    )

                    consistency_fig = px.bar(
                        consistency_plot,
                        x="full_name",
                        y="std_lap_seconds",
                        color="team_name",
                        hover_data=[
                            "candidate_laps",
                            "lap_time_range_seconds"
                        ],
                        labels={
                            "full_name": "Driver",
                            "std_lap_seconds": (
                                "Lap-time standard deviation (s)"
                            ),
                            "team_name": "Team"
                        },
                        title=(
                            "Standard Deviation of Candidate Lap Times "
                            "(Lower Variation)"
                        )
                    )

                    st.plotly_chart(
                        consistency_fig,
                        use_container_width=True
                    )

                st.subheader("Detailed Combined Performance Table")

                table_columns = [
                    "driver_number", "full_name", "team_name",
                    "candidate_laps", "best_lap_seconds",
                    "average_lap_seconds", "average_pace_rank",
                    "sector_1_average", "sector_2_average",
                    "sector_3_average", "combined_sector_rank",
                    "std_lap_seconds", "lap_consistency_rank"
                ]

                available_table_columns = [
                    column for column in table_columns
                    if column in selected_data.columns
                ]

                display_data = selected_data[
                    available_table_columns
                ].sort_values("average_pace_rank")

                st.dataframe(
                    display_data.round(3),
                    use_container_width=True,
                    hide_index=True
                )

                csv_bytes = selected_data.to_csv(
                    index=False
                ).encode("utf-8")

                st.download_button(
                    label="Download Selected Driver Performance CSV",
                    data=csv_bytes,
                    file_name="combined_driver_performance_selected.csv",
                    mime="text/csv",
                    key="download_combined_performance"
                )

            st.divider()

            st.info(
                "Interpretation limits: the 85–95 second candidate-lap filter "
                "is exploratory, and each driver has only 2–6 selected laps. "
                "Tyre compound and age, fuel load, traffic, track evolution, "
                "and run conditions are not controlled. Lap-time standard "
                "deviation is descriptive for this small selected sample, "
                "not a definitive driver-consistency measure. Sector ranks "
                "summarize average sector times only. These are historical "
                "public OpenF1 data, not proprietary F1 team engineering data."
            )


# ==================================================

# 10. RAW DATA EXPLORER
# ==================================================

elif page == "Raw Data Explorer":

    st.header("Raw Dataset Explorer")

    dataset_map = {
        "Drivers": drivers,
        "Laps": laps,
        "Verstappen Telemetry": telemetry,
        "All Drivers Summary": all_drivers_summary,
        "Combined Driver Performance": combined_performance
    }

    dataset_name = st.selectbox(
        "Choose Dataset",
        list(dataset_map.keys())
    )

    selected_data = dataset_map[dataset_name]

    if selected_data.empty:

        st.warning(
            f"{dataset_name} dataset is empty or unavailable."
        )

    else:

        st.write(
            "Dataset dimensions:",
            selected_data.shape
        )

        st.dataframe(
            selected_data,
            use_container_width=True,
            hide_index=True
        )

        csv_data = selected_data.to_csv(
            index=False
        ).encode("utf-8")

        st.download_button(
            label="Download Selected Dataset",
            data=csv_data,
            file_name=(
                f"{dataset_name.lower().replace(' ', '_')}.csv"
            ),
            mime="text/csv"
        )


# ==================================================
# 11. FOOTER
# ==================================================

st.divider()

st.caption(
    "F1 Telemetry Analytics Platform | "
    "Developed by Kamal Solanki | "
    "Data source: OpenF1 API"
)
