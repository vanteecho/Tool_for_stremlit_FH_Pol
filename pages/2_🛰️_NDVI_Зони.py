# pages/2_🛰️_NDVI_Зони.py
import streamlit as st
import geopandas as gpd
import folium
from streamlit_folium import st_folium
import branca.colormap as cm
import os

st.set_page_config(layout="wide", page_title="Зони NDVI", page_icon="🛰️")
st.title("🛰️ Зони продуктивності (NDVI)")

# --- РОЗУМНЕ ЗАВАНТАЖЕННЯ ДАНИХ ---
@st.cache_data
def load_ndvi_data():
    zip_path = "Data_to transfer/NDVI_zoen.zip"
    
    if not os.path.exists(zip_path):
        return None, f"Файл не знайдено за шляхом: {zip_path}"
    
    try:
        # Читаємо архів
        gdf = gpd.read_file(f"zip://{zip_path}")
        
        # 1. СЕКРЕТНИЙ ХАК: Робимо всі назви колонок ВЕЛИКИМИ літерами
        # Тепер нам байдуже, написано там zone, Zone чи ZONE
        gdf.columns = gdf.columns.str.upper()
        
        # 2. Перевіряємо проекцію
        if gdf.crs is None:
            # Якщо проекції немає, ставимо стандартну, щоб уникнути помилок
            gdf.set_crs(epsg=4326, inplace=True)
        else:
            gdf = gdf.to_crs(epsg=4326)
            
        return gdf, "OK"
    except Exception as e:
        return None, str(e)

gdf, status = load_ndvi_data()

# --- ОБРОБКА ПОМИЛОК ---
if gdf is None:
    st.error(f"⚠️ Помилка завантаження файлу: {status}")
    st.info("Переконайтеся, що файл 'NDVI_zoen.zip' лежить у папці 'Data_to transfer'")
    st.stop()

# --- БЛОК ДЕБАГУ (Щоб бачити, що всередині) ---
with st.expander("🛠️ Технічна інформація (Сирі дані)"):
    st.write(f"**Знайдені колонки:** {list(gdf.columns)}")
    st.dataframe(gdf.drop(columns=['GEOMETRY'], errors='ignore').head())

# --- ВІЗУАЛІЗАЦІЯ ---
# Оскільки ми зробили всі колонки великими, шукаємо 'ZONE' та 'NDVI'
if 'ZONE' in gdf.columns and 'NDVI' in gdf.columns:
    
    # Примусово робимо NDVI числами, щоб градієнт не зламався
    gdf['NDVI'] = pd.to_numeric(gdf['NDVI'], errors='coerce')
    
    c1, c2, c3 = st.columns(3)
    c1.metric("Кількість зон", len(gdf['ZONE'].unique()))
    c2.metric("Макс. NDVI", f"{gdf['NDVI'].max():.3f}")
    c3.metric("Мін. NDVI", f"{gdf['NDVI'].min():.3f}")
    
    st.markdown("---")
    
    # Шкала кольорів
    colormap = cm.LinearColormap(
        colors=['#d7191c', '#fdae61', '#ffffbf', '#a6d96a', '#1a9641'], 
        vmin=gdf['NDVI'].min(), 
        vmax=gdf['NDVI'].max(),
        caption='Індекс NDVI'
    )

    # Центруємо карту
    center_y = gdf.geometry.centroid.y.mean()
    center_x = gdf.geometry.centroid.x.mean()
    m = folium.Map(location=[center_y, center_x], zoom_start=14, tiles="CartoDB Positron")

    # Малюємо полігони
    def style_fn(feature):
        val = feature['properties'].get('NDVI')
        color = colormap(val) if val is not None else 'gray'
        return {'fillColor': color, 'color': '#000000', 'weight': 1, 'fillOpacity': 0.75}

    folium.GeoJson(
        gdf,
        style_function=style_fn,
        tooltip=folium.GeoJsonTooltip(
            fields=['ZONE', 'NDVI'], 
            aliases=['Зона:', 'NDVI:'],
            style="font-family: sans-serif; font-size: 14px; background-color: white;"
        )
    ).add_to(m)
    
    colormap.add_to(m)
    st_folium(m, width="100%", height=600, returned_objects=[])

else:
    st.error("❌ У файлі не знайдено колонок ZONE або NDVI.")
    st.info("Розгорніть 'Технічна інформація' вище, щоб подивитися, як ці колонки називаються насправді.")