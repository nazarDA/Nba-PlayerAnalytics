import streamlit as st
import pandas as pd
import altair as alt
from pathlib import Path

# — Cache & load data —
@st.cache_data
def load_overview():
    base = Path(__file__).resolve().parent.parent / "Data"
    ps   = pd.read_csv(base / "PlayerStatistics.csv")
    gm   = pd.read_csv(base / "Games.csv")
    # Hitung total game, rata-rata PPG liga
    total_games = gm["gameId"].nunique()
    avg_ppg     = ps["points"].sum() / total_games
    # Top 5 skor total
    top5 = (
        ps.groupby("personId")["points"].sum()
          .nlargest(5)
          .reset_index()
    )
    # Gabung nama
    pl = pd.read_csv(base / "Players.csv")
    pl["fullName"] = pl["firstName"] + " " + pl["lastName"]
    top5 = top5.merge(pl[["personId","fullName"]], on="personId").set_index("fullName")
    return total_games, avg_ppg, top5
def _go(page_name):
    st.session_state.selected_page = page_name
    # rerun agar streamlit_app.py mengeksekusi halaman baru
    st.experimental_rerun()
def app():
    st.title("🏀 NBA Analytics Dashboard")
    st.markdown("## Ringkasan Liga & Quick Links")
    
    # — KPIs —
    games, ppg, top5 = load_overview()
    col1, col2, col3 = st.columns(3)
    col1.metric("Total Games", f"{games}")
    col2.metric("Average PPG (Liga)", f"{ppg:.1f}")
    st.markdown("---")
    
    # — Top 5 Scorers Bar Chart —
    st.subheader("Top 5 All-Time Scorers")
    chart = alt.Chart(top5.reset_index()).mark_bar().encode(
        x=alt.X("points:Q", title="Total Points"),
        y=alt.Y("fullName:N", sort="-x", title=None),
        tooltip=["fullName","points"]
    ).properties(height=300)
    st.altair_chart(chart, use_container_width=True)
    
    # — Trend Rata-Rata PPG per Musim —
    st.subheader("Rata-Rata PPG per Musim")
    ps = pd.read_csv(Path(__file__).resolve().parent.parent / "Data/PlayerStatistics.csv")
    ps["season"] = pd.to_datetime(ps["gameDate"]).dt.year
    trend = ps.groupby("season")["points"].sum() / ps.groupby("season")["gameId"].nunique()
    df_trend = trend.reset_index(name="avg_ppg")
    line = alt.Chart(df_trend).mark_line(point=True).encode(
        x="season:O", y="avg_ppg:Q", tooltip=["season","avg_ppg"]
    )
    st.altair_chart(line, use_container_width=True)
  