import streamlit as st
import pandas as pd
import altair as alt
from pathlib import Path

@st.cache_data
def load_data():
    BASE_DIR = Path(__file__).resolve().parent.parent
    DATA_DIR = BASE_DIR / "Data"
    # Load player stats and player info
    ps = pd.read_csv(DATA_DIR / "PlayerStatistics.csv")
    pl = pd.read_csv(DATA_DIR / "Players.csv")
    # Create fullName
    pl["firstName"] = pl["firstName"].fillna("")
    pl["lastName"]  = pl["lastName"].fillna("")
    pl["fullName"]  = (pl["firstName"] + " " + pl["lastName"]).str.strip()
    # Merge
    ps = ps.merge(pl[["personId","fullName"]], on="personId", how="left")
    # Convert date
    ps["gameDate"] = pd.to_datetime(ps["gameDate"], errors="coerce")
    return ps


def app():
    st.header("Top-Game Highlights")
    st.write("Menampilkan 5 penampilan terbaik satu game untuk metrik terpilih.")

    player_stats = load_data()

    # Sidebar: pilih metrik
    metrics = ["points","reboundsTotal","assists","steals","blocks",
               "fieldGoalsMade","threePointersMade","freeThrowsMade"]
    sel_metric = st.selectbox("Pilih Metrik", metrics)

    # Get top 5 game records
    top5 = player_stats.sort_values(sel_metric, ascending=False).head(5)
    top5 = top5[["fullName","gameDate", sel_metric]]
    top5 = top5.rename(columns={"fullName":"Pemain","gameDate":"Tanggal", sel_metric:sel_metric.capitalize()})

    # Display as table
    st.subheader(f"Top 5 Single-Game {sel_metric.capitalize()}")
    st.dataframe(top5)

    # Bar chart
    chart = alt.Chart(top5).mark_bar().encode(
        x=alt.X(f"{sel_metric.capitalize()}:Q", title=sel_metric.capitalize()),
        y=alt.Y("Pemain:N", sort="-x", title="Pemain"),
        color=alt.Color("Pemain:N", legend=None),
        tooltip=["Pemain","Tanggal",f"{sel_metric.capitalize()}"]
    ).properties(height=300)

    st.altair_chart(chart, use_container_width=True)

if __name__ == "__main__":
    app()
