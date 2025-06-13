import streamlit as st
import pandas as pd
import altair as alt
from pathlib import Path

# Matikan batas default 5000 baris di Altair
alt.data_transformers.disable_max_rows()

def app():
    # --- Path & Load Data (cached) ---
    BASE_DIR = Path(__file__).resolve().parent.parent
    DATA_DIR = BASE_DIR / "Data"

    @st.cache_data
    def load_data():
        ps = pd.read_csv(DATA_DIR / "PlayerStatistics.csv")
        pl = pd.read_csv(DATA_DIR / "Players.csv")
        # Buat fullName
        pl["fullName"] = pl["firstName"] + " " + pl["lastName"]
        # Merge ke stats
        ps = ps.merge(pl[["personId","fullName"]], on="personId", how="left")
        # Tambah kolom date & season
        ps["gameDate"] = pd.to_datetime(ps["gameDate"])
        ps["season"]   = ps["gameDate"].dt.year
        return ps, pl

    player_stats, players = load_data()

    # --- Hitung debut & retirement season per pemain ---
    debut_year  = player_stats.groupby("personId")["season"].min()
    retire_year = player_stats.groupby("personId")["season"].max()

    # --- Sidebar: Pilih Musim ---
    seasons    = ["All Seasons"] + sorted(player_stats["season"].unique().tolist())
    sel_season = st.sidebar.selectbox("Pilih Musim", seasons)

    # --- Sidebar: Filter pemain aktif di musim terpilih ---
    if sel_season == "All Seasons":
        valid_ids = players["personId"].unique()
    else:
        year      = int(sel_season)
        valid_ids = debut_year[
            (debut_year <= year) & (retire_year >= year)
        ].index

    valid_players = (
        players[players["personId"].isin(valid_ids)]
        .sort_values("fullName")["fullName"]
        .tolist()
    )

    # --- Sidebar: Pilih Dua Pemain ---
    p1 = st.sidebar.selectbox("Pemain 1", valid_players)
    p2 = st.sidebar.selectbox(
        "Pemain 2",
        [n for n in valid_players if n != p1]
    )

    # --- Sidebar: Pilih Statistik ---
    metrics = [
        "points","reboundsTotal","assists","blocks","steals",
        "fieldGoalsMade","threePointersMade","freeThrowsMade"
    ]
    sel_metric = st.sidebar.selectbox("Pilih Statistik", metrics)

    # --- Filter Data untuk Plot ---
    if sel_season == "All Seasons":
        df = player_stats
    else:
        df = player_stats[player_stats["season"] == year]

    id1 = players.loc[players["fullName"] == p1, "personId"].iat[0]
    id2 = players.loc[players["fullName"] == p2, "personId"].iat[0]
    df1 = df[df["personId"] == id1]
    df2 = df[df["personId"] == id2]

    # --- Page Content ---
    st.header(f"Perbandingan {sel_metric.upper()} : {p1} vs {p2}")

    # 1) Bar chart total
    tot1, tot2 = df1[sel_metric].sum(), df2[sel_metric].sum()
    comp_df = pd.DataFrame({
        "Pemain": [p1, p2],
        f"Total {sel_metric}": [tot1, tot2]
    }).set_index("Pemain")
    st.bar_chart(comp_df)

    # 2) Tren per Game
    st.subheader("Tren per Game")
    chart = (
        alt.Chart(df[df["personId"].isin([id1, id2])])
        .mark_line(point=True)
        .encode(
            x=alt.X("gameDate:T", title="Tanggal Game"),
            y=alt.Y(f"{sel_metric}:Q", title=sel_metric.capitalize()),
            color=alt.Color("fullName:N", title="Pemain"),
            tooltip=["gameDate:T", "fullName:N", f"{sel_metric}:Q"]
        )
        .interactive()
    )
    st.altair_chart(chart, use_container_width=True)


if __name__ == "__main__":
    app()
