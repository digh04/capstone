"""Streamlit web app: sunlight exposure and pediatric depression."""

from __future__ import annotations

import json
from pathlib import Path

import pandas as pd
import streamlit as st

PROJECT_ROOT = Path(__file__).resolve().parent.parent
SPREADSHEETS_DIR = PROJECT_ROOT / "outputs" / "spreadsheets"
FIGURES_DIR = PROJECT_ROOT / "outputs" / "figures"
RESULTS_DIR = PROJECT_ROOT / "outputs" / "results"

SHEET_FILES = {
    "Raw data": "01_raw_data.csv",
    "Cleaned data": "02_cleaned_data.csv",
    "Summary statistics": "03_summary_statistics.csv",
    "Correlation results": "04_correlation_results.csv",
    "Regression results": "05_regression_results.csv",
    "Findings summary": "06_findings_summary.csv",
}

FIGURE_META = {
    "main_finding.png": {
        "title": "Combined time series (main finding)",
        "caption": (
            "Youth depression and sunlight over 2019–2023. Depression varies more than sun; "
            "the 2021 peak is not matched by a proportional sunlight change."
        ),
    },
    "depression_by_year.png": {
        "title": "Youth depression by year",
        "caption": "Pediatric depressive symptoms (%) across observation years.",
    },
    "sunlight_by_year.png": {
        "title": "Sunlight exposure by year",
        "caption": "Average daily sunlight (MJ/m²/day) across observation years.",
    },
    "scatter_regression.png": {
        "title": "Sunlight vs youth depression",
        "caption": "Exploratory scatter plot with descriptive regression line (n=3; not inferential).",
    },
}

REQUIRED_OUTPUTS = [
    SPREADSHEETS_DIR / "06_findings_summary.csv",
    FIGURES_DIR / "main_finding.png",
]


def pipeline_outputs_exist() -> bool:
    return all(path.exists() for path in REQUIRED_OUTPUTS)


def load_csv(filename: str) -> pd.DataFrame:
    return pd.read_csv(SPREADSHEETS_DIR / filename)


def discover_figure_files() -> list[Path]:
    if not FIGURES_DIR.exists():
        return []
    figures = [
        path
        for path in sorted(FIGURES_DIR.iterdir())
        if path.suffix.lower() in {".png", ".svg", ".jpg", ".jpeg", ".webp"}
        and path.is_file()
    ]
    return figures


def figure_title(path: Path) -> str:
    meta = FIGURE_META.get(path.name, {})
    if meta.get("title"):
        return str(meta["title"])
    return path.stem.replace("_", " ").title()


def figure_caption(path: Path) -> str:
    meta = FIGURE_META.get(path.name, {})
    return str(meta.get("caption", f"Pipeline figure: {path.name}"))


def render_figure(path: Path) -> None:
    st.subheader(figure_title(path))
    st.image(str(path), caption=figure_caption(path), use_container_width=True)


def render_figure_gallery(figures: list[Path], columns: int = 1) -> None:
    if not figures:
        st.info("No figures found. Run `bash setup/run_pipeline.sh` to generate charts.")
        return

    if columns > 1:
        for index in range(0, len(figures), columns):
            row = figures[index : index + columns]
            cols = st.columns(columns)
            for col, path in zip(cols, row):
                with col:
                    st.image(str(path), caption=figure_title(path), use_container_width=True)
        return

    for path in figures:
        render_figure(path)


def render_metrics(summary_df: pd.DataFrame, correlation_df: pd.DataFrame, metadata: dict) -> None:
    dep = summary_df.loc[summary_df["variable"] == "youth_depression_pct"].iloc[0]
    sun = summary_df.loc[summary_df["variable"] == "avg_sun_mj_m2_day"].iloc[0]
    pearson = correlation_df.loc[correlation_df["method"] == "Pearson r", "statistic"].iloc[0]

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Observations", int(metadata.get("n_observations", dep["n"])))
    c2.metric("Depression range (%)", f"{dep['min']:.1f} – {dep['max']:.1f}")
    c3.metric("Sunlight range (MJ/m²/day)", f"{sun['min']:.3f} – {sun['max']:.3f}")
    c4.metric("Pearson r (exploratory)", f"{pearson:.3f}")


def render_interactive_charts(cleaned_df: pd.DataFrame) -> None:
    st.subheader("Interactive data charts")
    st.caption("Live charts from cleaned pipeline data — useful for exploration during presentation.")

    chart_df = cleaned_df.set_index("year")
    left, right = st.columns(2)

    with left:
        st.markdown("**Youth depression (%)**")
        st.line_chart(chart_df["youth_depression_pct"], use_container_width=True)
        st.bar_chart(chart_df["youth_depression_pct"], use_container_width=True)

    with right:
        st.markdown("**Average sunlight (MJ/m²/day)**")
        st.line_chart(chart_df["avg_sun_mj_m2_day"], use_container_width=True)
        st.bar_chart(chart_df["avg_sun_mj_m2_day"], use_container_width=True)

    st.markdown("**Side-by-side comparison (normalized 0–1 for shape comparison only)**")
    normalized = chart_df.copy()
    for column in normalized.columns:
        span = normalized[column].max() - normalized[column].min()
        normalized[column] = (normalized[column] - normalized[column].min()) / span if span else 0.0
    st.line_chart(normalized, use_container_width=True)


def render_overview(findings_df: pd.DataFrame, correlation_df: pd.DataFrame) -> None:
    st.header("Research question")
    st.markdown(
        "**Does the amount of sunlight exposure impact how much the pediatric population "
        "reports depressive symptoms?**"
    )

    takeaway = findings_df.loc[findings_df["finding"] == "Overall takeaway", "evidence"]
    if not takeaway.empty:
        st.success(str(takeaway.iloc[0]))

    pearson = correlation_df.loc[correlation_df["method"] == "Pearson r", "statistic"]
    if not pearson.empty:
        st.info(
            f"Descriptive Pearson r = **{pearson.iloc[0]:.3f}** "
            f"(exploratory only; n=3 annual observations)."
        )

    st.warning(
        "This dataset has only three yearly observations. Results are descriptive and "
        "exploratory — they do not support causal or confirmatory conclusions."
    )


def main() -> None:
    st.set_page_config(
        page_title="Sunlight & Youth Depression",
        page_icon="☀️",
        layout="wide",
    )
    st.title("Sunlight Exposure and Pediatric Depressive Symptoms")
    st.caption("Capstone analysis dashboard · Data source: setup/capstone.csv")

    if not pipeline_outputs_exist():
        st.error("Pipeline outputs not found.")
        st.markdown(
            "From the repository root, run:\n\n"
            "```bash\n"
            "conda activate capstone_env\n"
            "bash setup/run_pipeline.sh\n"
            "```\n\n"
            "Then restart this app."
        )
        st.stop()

    findings_df = load_csv("06_findings_summary.csv")
    correlation_df = load_csv("04_correlation_results.csv")
    summary_df = load_csv("03_summary_statistics.csv")
    cleaned_df = load_csv("02_cleaned_data.csv")
    metadata_path = RESULTS_DIR / "analysis_metadata.json"
    metadata = json.loads(metadata_path.read_text(encoding="utf-8")) if metadata_path.exists() else {}
    figures = discover_figure_files()

    tab_overview, tab_visuals, tab_sheets, tab_methods = st.tabs(
        ["Overview", "Visuals", "Spreadsheets", "Methods"]
    )

    with tab_overview:
        render_overview(findings_df, correlation_df)
        render_metrics(summary_df, correlation_df, metadata)
        st.subheader("Primary visualization")
        main_figure = FIGURES_DIR / "main_finding.png"
        if main_figure.exists():
            render_figure(main_figure)
        st.subheader("Key findings")
        st.dataframe(findings_df, use_container_width=True, hide_index=True)

    with tab_visuals:
        st.markdown(
            f"**{len(figures)} pipeline figure(s)** from `outputs/figures/` plus interactive charts "
            "from the cleaned dataset. Re-run `bash setup/run_pipeline.sh` to refresh static images."
        )
        render_metrics(summary_df, correlation_df, metadata)
        st.divider()
        st.subheader("All pipeline figures")
        render_figure_gallery(figures)
        st.divider()
        render_interactive_charts(cleaned_df)
        st.divider()
        st.subheader("Source data (for reference)")
        st.dataframe(cleaned_df, use_container_width=True, hide_index=True)

    with tab_sheets:
        st.subheader("Analysis spreadsheets")
        sheet_name = st.selectbox("Select spreadsheet", list(SHEET_FILES.keys()))
        df = load_csv(SHEET_FILES[sheet_name])
        st.dataframe(df, use_container_width=True, hide_index=True)
        st.download_button(
            label=f"Download {SHEET_FILES[sheet_name]}",
            data=df.to_csv(index=False),
            file_name=SHEET_FILES[sheet_name],
            mime="text/csv",
        )

    with tab_methods:
        st.subheader("Methods")
        st.markdown(
            """
            **Data:** `setup/capstone.csv` — annual youth depression rate (%) and average daily
            sunlight (MJ/m²/day) for 2019, 2021, and 2023.

            **Processing:** Schema validation, type checks, and column standardization.

            **Analysis:**
            - Descriptive summary statistics (mean, SD, min, max)
            - Pearson and Spearman correlation (exploratory)
            - Simple linear regression of depression on sunlight (descriptive trend)

            **Visualization:**
            - Combined dual time-series panel (main finding)
            - Individual year charts for depression and sunlight
            - Scatter plot with descriptive regression line
            - Interactive Streamlit charts in the Visuals tab

            **Limitations:**
            - n = 3: insufficient for reliable inference or causation claims
            - Aggregate yearly data, not individual pediatric records
            - Sunlight is a regional average, not measured individual exposure
            """
        )
        st.subheader("How to reproduce")
        st.code(
            "conda activate capstone_env\n"
            "bash setup/run_pipeline.sh\n"
            "streamlit run webapp/app.py --server.port 2026",
            language="bash",
        )


if __name__ == "__main__":
    main()
