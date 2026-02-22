# pages/3_🚜_Лінії_заїзду.py
import streamlit as st
import geopandas as gpd
import folium
from streamlit_folium import st_folium

st.set_page_config(layout="wide", page_title="Лінії заїзду", page_icon="🚜")
st.title("🚜 Навігаційні лінії заїзду техніки")

@st.cache_data
def load_lines_data():
    try:
        file_path = "zip://Data_to transfer/Enter_line.zip"
        gdf = gpd.read_file(file_path)
        return gdf.to_crs(epsg=4326)
    except Exception as e:
        st.error(f"⚠️ Не вдалося завантажити лінії. Помилка: {e}")
        return None

gdf = load_lines_data()

if gdf is not None and not gdf.empty:
    st.info(f"📍 Завантажено ліній: **{len(gdf)}** шт.")
    
    # Центруємо карту
    center_y = gdf.geometry.centroid.y.mean()
    center_x = gdf.geometry.centroid.x.mean()
    m = folium.Map(location=[center_y, center_x], zoom_start=15, tiles="Esri.WorldImagery") # Для навігації краще супутник

    # Додаємо лінії
    folium.GeoJson(
        gdf,
        style_function=lambda feature: {
            'color': '#0078FF', # Яскраво-синій колір для ліній
            'weight': 3,        # Товщина лінії
            'opacity': 0.9
        },
        # Якщо в шейпі ліній є якісь атрибути (наприклад номер лінії), 
        # їх можна показати. Якщо ні - залишаємо пустим.
        tooltip=folium.GeoJsonTooltip(fields=list(gdf.columns.drop('geometry'))[:3]) if len(gdf.columns) > 1 else None
    ).add_to(m)

    st_folium(m, width="100%", height=650, returned_objects=[])