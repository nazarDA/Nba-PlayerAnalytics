import streamlit as st
import pandas as pd
import altair as alt
from pathlib import Path

def app():
    # --- Paths & Load Data ---
    BASE_DIR = Path(__file__).resolve().parent.parent
    DATA_DIR = BASE_DIR / "Data"

    @st.cache_data
    def load_team():
        df = pd.read_csv(DATA_DIR / "TeamStatistics.csv")
        df["gameDate"] = pd.to_datetime(df["gameDate"])
        df["season"]   = df["gameDate"].dt.year
        return df

    df_team = load_team()

    # --- Sidebar Filters ---
    seasons = ["All Seasons"] + sorted(df_team["season"].unique().tolist())
    sel_season = st.sidebar.selectbox("Pilih Musim", seasons)
    teams = sorted(df_team["teamName"].unique().tolist())
    sel_team = st.sidebar.selectbox("Pilih Tim", teams)

    # --- Apply Filters ---
    df = df_team.copy()
    if sel_season != "All Seasons":
        df = df[df["season"] == sel_season]
    df = df[df["teamName"] == sel_team]

    # --- Page Content ---
    st.header(f"Statistik Tim: {sel_team}")

    st.subheader("Poin per Game")
    line = (
        alt.Chart(df)
        .mark_line(point=True)
        .encode(
            x="gameDate:T",
            y="points:Q",
            tooltip=["gameDate:T", "points:Q"]
        )
        .interactive()
    )
    st.altair_chart(line, use_container_width=True)

    st.subheader("Overview Performance")
    metrics = ["pointsInPaint","pointsSecondChance","fastBreakPoints"]
    perf = df[["gameDate"] + metrics].melt("gameDate", var_name="Metric", value_name="Value")
    area = (
        alt.Chart(perf)
        .mark_area(opacity=0.5)
        .encode(
            x="gameDate:T",
            y="Value:Q",
            color="Metric:N",
            tooltip=["gameDate:T","Metric","Value"]
        )
        .interactive()
    )
    st.altair_chart(area, use_container_width=True)

# Entry-point
if __name__ == "__main__":
    app()
# If you are using the manual pattern (Option B), call this function.
# If not, Streamlit will execute this file directly.