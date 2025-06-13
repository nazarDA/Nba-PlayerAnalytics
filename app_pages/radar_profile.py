import streamlit as st
import pandas as pd
import plotly.express as px
from pathlib import Path

@st.cache_data
def load_data():
    BASE_DIR = Path(__file__).resolve().parent.parent
    DATA_DIR = BASE_DIR / "Data"

    ps = pd.read_csv(DATA_DIR / "PlayerStatistics.csv")
    pl = pd.read_csv(DATA_DIR / "Players.csv")

    # Buat fullName
    pl["firstName"] = pl["firstName"].fillna("")
    pl["lastName"]  = pl["lastName"].fillna("")
    pl["fullName"]  = (pl["firstName"] + " " + pl["lastName"]).str.strip()

    # Merge fullName ke stats
    ps = ps.merge(pl[["personId","fullName"]], on="personId", how="left")

    # Konversi tanggal & hitung season
    ps["gameDate"] = pd.to_datetime(ps["gameDate"], errors="coerce")
    ps["season"]   = ps["gameDate"].dt.year

    return ps, pl

def app():
    # Load data
    player_stats, players = load_data()

    # (Debug) tampilkan kolom untuk memverifikasi nama-nama
    # st.write("Kolom PlayerStatistics:", player_stats.columns.tolist())

    # Sidebar: filter season
    seasons = ["All Seasons"] + sorted(player_stats["season"].dropna().unique().astype(int).tolist())
    sel_season = st.sidebar.selectbox("Pilih Musim", seasons)
    if sel_season != "All Seasons":
        df = player_stats[player_stats["season"] == int(sel_season)]
    else:
        df = player_stats.copy()

    # Sidebar: pilih hingga 2 pemain
    all_names = players["fullName"].dropna().tolist()
    all_names = [n for n in all_names if n]  # hanya non-empty
    all_names.sort()
    sel_players = st.sidebar.multiselect(
        "Pilih 1–2 Pemain untuk Radar",
        options=all_names,
        default=all_names[:2]
    )
    if not sel_players:
        st.warning("Pilih setidaknya satu pemain.")
        return
    if len(sel_players) > 2:
        st.warning("Pilih maksimal dua pemain.")
        sel_players = sel_players[:2]

    # Definisikan metrik sesuai kolom
    metrics = {
        "points": "Pts",
        "reboundsTotal": "Reb",
        "assists": "Ast",
        "steals": "Stl",
        "blocks": "Blk",
        "fieldGoalsPercentage": "FG%",
        # Pastikan nama kolom di bawah ini sesuai dengan yang ada di DataFrame:
        "threePointersPercentage": "3P%",      # ← ganti dengan nama kolom sesungguhnya
        "freeThrowsPercentage": "FT%"
    }

    # Agregasi rata-rata
    subset = df[df["fullName"].isin(sel_players)]
    df_mean = subset.groupby("fullName")[list(metrics.keys())].mean().reset_index()

    # Normalisasi min–max
    df_norm = df_mean.copy()
    for col in metrics.keys():
        mn, mx = df_norm[col].min(), df_norm[col].max()
        df_norm[col] = 0.5 if mx == mn else (df_norm[col] - mn) / (mx - mn)

    # Transform untuk radar
    df_long = df_norm.melt(
        id_vars="fullName",
        value_vars=list(metrics.keys()),
        var_name="Metric",
        value_name="Value"
    )
    df_long["Metric"] = df_long["Metric"].map(metrics)

    # Tampilkan chart
    st.header("Player Radar Profile")
    st.write("Perbandingan performa pemain dalam berbagai metrik (dinormalisasi).")
    fig = px.line_polar(
        df_long,
        r="Value",
        theta="Metric",
        color="fullName",
        line_close=True,
        template="plotly_dark"
    )
    fig.update_traces(fill="toself")
    fig.update_layout(legend_title_text="Pemain")
    st.plotly_chart(fig, use_container_width=True)

if __name__ == "__main__":
    app()
# Entry-point
# if __name__ == "__main__":