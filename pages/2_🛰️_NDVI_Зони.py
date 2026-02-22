# pages/2_🛰️_NDVI_Зони.py
import streamlit as st
import geopandas as gpd
import folium
from streamlit_folium import st_folium
import branca.colormap as cm

st.set_page_config(layout="wide", page_title="Зони NDVI", page_icon="🛰️")
st.title("🛰️ Зони продуктивності (NDVI)")

# Функція завантаження даних
@st.cache_data
def load_ndvi_data():
    try:
        # Читаємо ZIP архів напряму
        file_path = "zip://Data_to transfer/NDVI_zoen.zip"
        gdf = gpd.read_file(file_path)
        # Обов'язково переводимо в WGS84 для відображення на веб-карті
        return gdf.to_crs(epsg=4326)
    except Exception as e:
        st.error(f"⚠️ Не вдалося завантажити дані NDVI. Помилка: {e}")
        return None

gdf = load_ndvi_data()

if gdf is not None and not gdf.empty:
    # Перевіряємо, чи є потрібні колонки
    if 'NDVI' in gdf.columns and 'ZONE' in gdf.columns:
        
        # Блок метрик
        c1, c2, c3 = st.columns(3)
        c1.metric("Кількість зон", len(gdf['ZONE'].unique()))
        c2.metric("Максимальний NDVI", f"{gdf['NDVI'].max():.3f}")
        c3.metric("Мінімальний NDVI", f"{gdf['NDVI'].min():.3f}")
        
        st.markdown("---")
        
        # Створюємо кольорову шкалу (від червоного до зеленого)
        colormap = cm.LinearColormap(
            colors=['#d7191c', '#fdae61', '#ffffbf', '#a6d96a', '#1a9641'], 
            vmin=gdf['NDVI'].min(), 
            vmax=gdf['NDVI'].max(),
            caption='Значення NDVI'
        )

        # Центруємо карту
        center_y = gdf.geometry.centroid.y.mean()
        center_x = gdf.geometry.centroid.x.mean()
        m = folium.Map(location=[center_y, center_x], zoom_start=14, tiles="CartoDB Positron")

        # Додаємо полігони на карту
        folium.GeoJson(
            gdf,
            style_function=lambda feature: {
                'fillColor': colormap(feature['properties']['NDVI']) if feature['properties']['NDVI'] is not None else 'gray',
                'color': '#000000', # Колір контуру
                'weight': 1,        # Товщина контуру
                'fillOpacity': 0.7  # Прозорість
            },
            tooltip=folium.GeoJsonTooltip(
                fields=['ZONE', 'NDVI'], 
                aliases=['Зона:', 'Індекс NDVI:'],
                style="font-family: sans-serif; font-size: 14px;"
            )
        ).add_to(m)
        
        # Додаємо легенду на карту
        colormap.add_to(m)

        st_folium(m, width="100%", height=600, returned_objects=[])
    else:
        st.warning("У файлі відсутні колонки 'ZONE' або 'NDVI'. Перевірте структуру даних.")
