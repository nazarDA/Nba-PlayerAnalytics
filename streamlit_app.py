import streamlit as st
from streamlit_option_menu import option_menu

# 1. Import semua halaman
from app_pages.main_page             import app as main_app
from app_pages.comparison_page       import app as comp_app
from app_pages.team_statistics_page  import app as team_app
from app_pages.radar_profile   import app as radar_app  # ← Tambahkan ini
from app_pages.consistency_page   import app as consistency_app
from app_pages.highlights_page    import app as highlights_app

# 2. Konfigurasi global
st.set_page_config(
    page_title="NBA Analytics",
    page_icon="🏀",
    layout="wide",
)

# 3. Branding di sidebar
st.sidebar.image("assets/logo_nba.png", width=100)
st.sidebar.markdown("## NBA Analytics")

with st.sidebar.expander("▶️ Menu Navigasi", expanded=True):
    selected = option_menu(
        menu_title=None,
        options=["Main Page", "Player Comparison","Consistency Heatmap","Top-Game Highlights","Player Radar"],
        icons=["house", "bar-chart", "people", "diagram-3-fill"],
        default_index=0,
        orientation="vertical",
        styles={
            "container": {"padding": "0px"},
            "nav-link": {"font-size": "16px", "margin":"4px 0"},
            "nav-link-selected": {"background-color": "#0047AB"}
        }
    )

# 5. Routing ke fungsi halaman
if selected == "Main Page":
    main_app()
elif selected == "Player Comparison":
    comp_app()
elif selected == "Consistency Heatmap":
    consistency_app()
elif selected == "Top-Game Highlights":
    highlights_app()
else:  # Player Radar
    radar_app()
