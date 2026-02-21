# pages/2_🗺️_NDVI_Карти.py
import streamlit as st
import folium
from folium.plugins import Fullscreen
from streamlit_folium import st_folium
from utils import apply_theme

st.set_page_config(layout="wide", page_title="NDVI Карти", page_icon="🗺️")
is_dark = apply_theme()

st.markdown("<h2 style='text-align: center; padding-top: 0;'>🗺️ Моніторинг NDVI</h2>", unsafe_allow_html=True)

# Панель налаштувань для NDVI
col1, col2 = st.columns(2)
with col1:
    st.date_input("Оберіть дату зйомки:")
with col2:
    st.selectbox("Оберіть індекс", ["NDVI", "EVI", "NDWI"])

st.markdown("---")

# Створення базової карти
tiles = "CartoDB Positron" if not is_dark else "CartoDB Dark Matter"
m = folium.Map(location=[49.55, 25.59], zoom_start=9, tiles=tiles) # Центр по замовчуванню (Тернопіль)
Fullscreen().add_to(m)

# TODO: Тут ми додамо логіку завантаження GeoTIFF через rasterio / leafmap
# та відображення векторних меж полів.

st_folium(m, width="100%", height=650)