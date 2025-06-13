import streamlit as st
import pandas as pd
import altair as alt
from pathlib import Path

@st.cache_data
def load_data():
    BASE_DIR = Path(__file__).resolve().parent.parent
    DATA_DIR = BASE_DIR / "Data"
    # Load player stats and players
    ps = pd.read_csv(DATA_DIR / "PlayerStatistics.csv")
    pl = pd.read_csv(DATA_DIR / "Players.csv")
    # Create fullName
    pl["firstName"] = pl["firstName"].fillna("")
    pl["lastName"]  = pl["lastName"].fillna("")
    pl["fullName"]  = (pl["firstName"] + " " + pl["lastName"]).str.strip()
    # Merge fullName into stats
    ps = ps.merge(pl[["personId","fullName"]], on="personId", how="left")
    # Convert gameDate and derive season
    ps["gameDate"] = pd.to_datetime(ps["gameDate"], errors="coerce")
    ps["season"]   = ps["gameDate"].dt.year
    return ps


def app():
    st.header("Consistency Heatmap")
    st.write("Visualisasi standar deviasi poin per game setiap pemain per musim.")

    player_stats = load_data()
    # Calculate standard deviation of points per (fullName, season)
    cons = (
        player_stats
          .groupby(["fullName","season"])["points"]
          .std()
          .reset_index(name="std_ppg")
    )

    # Dropdown filter: pilih maksimal 10 pemain untuk visibilitas
    players = sorted(cons["fullName"].unique())
    sel = st.multiselect("Pilih pemain (max 10)", players, default=players[:5], max_selections=10)
    cons = cons[cons["fullName"].isin(sel)]

    # Plot heatmap
    heatmap = alt.Chart(cons).mark_rect().encode(
        x=alt.X("season:O", title="Musim"),
        y=alt.Y("fullName:N", title="Pemain"),
        color=alt.Color("std_ppg:Q", scale=alt.Scale(scheme="reds"), title="Std Dev PPG"),
        tooltip=["fullName","season","std_ppg"]
    ).properties(height=400)

    st.altair_chart(heatmap, use_container_width=True)

if __name__ == "__main__":
    app()