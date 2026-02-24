# pages/2_🛰️_NDVI_Зони.py
import streamlit as st
import geopandas as gpd
import folium
from streamlit_folium import st_folium
import matplotlib.colors as mcolors
import numpy as np
import os, io, base64
from PIL import Image
import json

try:
    import rasterio
    from rasterio.warp import transform_bounds
    RASTERIO_INSTALLED = True
except ImportError:
    RASTERIO_INSTALLED = False

# ─── КОНФІГ ───────────────────────────────────────────────────────────────────
st.set_page_config(layout="wide", page_title="NDVI Pro", initial_sidebar_state="expanded")

st.markdown("""
<style>
    /* Прибираємо відступи */
    .main .block-container { padding: 0 !important; max-width: 100% !important; }
    header[data-testid="stHeader"] { display: none !important; }
    footer { display: none !important; }

    /* Сайдбар — чистий мінімалістичний вигляд */
    section[data-testid="stSidebar"] {
        min-width: 260px !important;
        max-width: 260px !important;
        background: #f8f9fa;
    }
    section[data-testid="stSidebar"] > div { padding: 1rem 0.8rem !important; }

    /* Заголовок сайдбару */
    .sidebar-title {
        font-size: 1.1rem;
        font-weight: 700;
        color: #1a1a2e;
        margin-bottom: 1rem;
        display: flex;
        align-items: center;
        gap: 8px;
    }

    /* Секція-блок */
    .sidebar-section {
        background: white;
        border-radius: 10px;
        padding: 12px 14px;
        margin-bottom: 10px;
        box-shadow: 0 1px 3px rgba(0,0,0,0.08);
    }
    .section-label {
        font-size: 0.7rem;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.08em;
        color: #888;
        margin-bottom: 8px;
    }

    /* Статистика NDVI */
    .ndvi-stats {
        display: flex;
        gap: 10px;
        margin-top: 4px;
    }
    .ndvi-stat-box {
        flex: 1;
        background: #f0f4f8;
        border-radius: 8px;
        padding: 8px 10px;
        text-align: center;
    }
    .ndvi-stat-val {
        font-size: 1.3rem;
        font-weight: 700;
        color: #1a9641;
        line-height: 1.1;
    }
    .ndvi-stat-val.low { color: #d7191c; }
    .ndvi-stat-lbl {
        font-size: 0.65rem;
        color: #999;
        text-transform: uppercase;
        letter-spacing: 0.05em;
    }
    .ndvi-count {
        font-size: 0.75rem;
        color: #aaa;
        margin-top: 6px;
        text-align: right;
    }

    /* Підкладки — кнопки-картки */
    .basemap-grid {
        display: grid;
        grid-template-columns: 1fr 1fr;
        gap: 6px;
    }
    .basemap-btn {
        background: #f0f4f8;
        border: 2px solid transparent;
        border-radius: 8px;
        padding: 8px 6px;
        text-align: center;
        cursor: pointer;
        font-size: 0.75rem;
        font-weight: 500;
        color: #444;
        transition: all 0.15s;
        line-height: 1.3;
    }
    .basemap-btn:hover { border-color: #4a9eff; background: #e8f0fe; }
    .basemap-btn.active { border-color: #1a7bff; background: #e8f0fe; color: #1a7bff; font-weight: 700; }
    .basemap-icon { font-size: 1.2rem; display: block; margin-bottom: 2px; }

    /* Легенда */
    .legend-item {
        display: flex;
        align-items: center;
        gap: 8px;
        padding: 4px 0;
        font-size: 0.8rem;
        color: #333;
        font-weight: 500;
    }
    .legend-dot {
        width: 16px;
        height: 16px;
        border-radius: 4px;
        flex-shrink: 0;
        box-shadow: 0 1px 2px rgba(0,0,0,0.15);
    }

    /* Radio → приховуємо стандартний label, лишаємо стиль */
    div[data-testid="stRadio"] label {
        font-size: 0.82rem !important;
    }
    div[data-testid="stSelectbox"] label {
        font-size: 0.75rem !important;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.06em;
        color: #888 !important;
    }
</style>
""", unsafe_allow_html=True)


# ─── КЕШУВАННЯ ────────────────────────────────────────────────────────────────

@st.cache_data(show_spinner="Завантаження векторних даних…")
def load_vector_data():
    zip_path = "Data_to transfer/NDVI_zoen.zip"
    if not os.path.exists(zip_path):
        return None
    gdf = gpd.read_file(f"zip://{zip_path}")
    gdf.columns = [c.upper() if c.lower() != "geometry" else "geometry" for c in gdf.columns]
    gdf = gdf.to_crs(epsg=4326)
    keep_cols = [c for c in ["ZONE", "NDVI", "geometry"] if c in gdf.columns]
    return gdf[keep_cols]


@st.cache_data(show_spinner="Підготовка GeoJSON…")
def build_geojson(gdf_json_str: str, tolerance: float) -> dict:
    gdf_temp = gpd.GeoDataFrame.from_features(json.loads(gdf_json_str)["features"])
    if tolerance > 0:
        gdf_temp["geometry"] = gdf_temp["geometry"].simplify(tolerance=tolerance, preserve_topology=True)
    data = json.loads(gdf_temp.to_json())

    def round_coords(coords):
        if isinstance(coords[0], (list, tuple)):
            return [round_coords(c) for c in coords]
        return [round(c, 6) for c in coords]

    for feat in data["features"]:
        feat["geometry"]["coordinates"] = round_coords(feat["geometry"]["coordinates"])
    return data


@st.cache_data(show_spinner="Завантаження растру…")
def get_raster_layer(path):
    """Завантажує TIF у WGS84 і повертає (base64_png, bounds_folium).
    Файли вже у WGS84 — читаємо напряму без перепроектування."""
    if not os.path.exists(path) or not RASTERIO_INSTALLED:
        return None, None
    try:
        with rasterio.open(path) as src:
            n_bands = src.count
            dtype   = src.dtypes[0]
            nodata  = src.nodata
            b       = src.bounds  # вже WGS84

            bounds_folium = [[b.bottom, b.left], [b.top, b.right]]

            def read_band(idx):
                return src.read(idx).astype(np.float32)

            # ── RGB uint8 ──────────────────────────────────────────────────
            if n_bands >= 3 and dtype == "uint8":
                r  = src.read(1)
                g  = src.read(2)
                bl = src.read(3)
                dark  = (r < 10)  & (g < 10)  & (bl < 10)
                light = (r > 245) & (g > 245) & (bl > 245)
                nd    = np.zeros_like(r, dtype=bool)
                if nodata is not None:
                    nd = (r == nodata)
                alpha = np.where(dark | light | nd, 0, 255).astype(np.uint8)
                rgba  = np.dstack((r, g, bl, alpha))

            # ── Однобандний float (NDVI) ───────────────────────────────────
            elif n_bands == 1:
                band  = read_band(1)
                valid = np.isfinite(band)
                if nodata is not None:
                    valid &= (band != nodata)
                v_min = float(np.nanpercentile(band[valid], 2))  if valid.any() else 0.0
                v_max = float(np.nanpercentile(band[valid], 98)) if valid.any() else 1.0
                norm  = np.clip((band - v_min) / (v_max - v_min + 1e-9), 0, 1)
                import matplotlib.cm as cm
                rgba_f = cm.get_cmap("RdYlGn")(norm)
                rgba_u = (rgba_f * 255).astype(np.uint8)
                rgba_u[~valid, 3] = 0
                rgba = rgba_u

            # ── Мультибандний float ────────────────────────────────────────
            else:
                channels = []
                for i in range(1, min(4, n_bands + 1)):
                    ch = read_band(i)
                    vld = np.isfinite(ch)
                    p2  = float(np.nanpercentile(ch[vld], 2))  if vld.any() else 0.0
                    p98 = float(np.nanpercentile(ch[vld], 98)) if vld.any() else 255.0
                    ch  = np.clip((ch - p2) / (p98 - p2 + 1e-9) * 255, 0, 255).astype(np.uint8)
                    channels.append(ch)
                r, g, bl = channels[0], channels[1], channels[2]
                dark  = (r < 10) & (g < 10) & (bl < 10)
                nd    = np.zeros_like(r, dtype=bool)
                if nodata is not None:
                    nd = (channels[0] == nodata)
                alpha = np.where(dark | nd, 0, 255).astype(np.uint8)
                rgba  = np.dstack((r, g, bl, alpha))

            pil_img = Image.fromarray(rgba, mode="RGBA")
            buf = io.BytesIO()
            pil_img.save(buf, format="PNG")
            b64 = base64.b64encode(buf.getvalue()).decode()
            return f"data:image/png;base64,{b64}", bounds_folium

    except Exception as e:
        st.warning(f"Помилка растру '{os.path.basename(path)}': {e}")
        return None, None


# ─── КОНФІГ ПІДКЛАДОК ─────────────────────────────────────────────────────────
# Підкладки: (назва_відображення, іконка, folium_tiles_або_url, attribution)
BASEMAPS = {
    "Світла": {
        "icon": "☀️",
        "tiles": "CartoDB positron",
        "attr": None,
    },
    "Темна": {
        "icon": "🌑",
        "tiles": "CartoDB dark_matter",
        "attr": None,
    },
    "OpenStreetMap": {
        "icon": "🗺️",
        "tiles": "OpenStreetMap",
        "attr": None,
    },
    "Супутник": {
        "icon": "🛰️",
        "tiles": "https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}",
        "attr": "Esri, Maxar, Earthstar Geographics",
    },
    "Супутник+підписи": {
        "icon": "🏷️",
        "tiles": "https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}",
        "attr": "Esri, Maxar, Earthstar Geographics",
        "overlay": "https://services.arcgisonline.com/ArcGIS/rest/services/Reference/World_Boundaries_and_Places/MapServer/tile/{z}/{y}/{x}",
        "overlay_attr": "Esri",
    },
}


# ─── ДАНІ ─────────────────────────────────────────────────────────────────────
gdf = load_vector_data()
if gdf is None:
    st.error("❌ Файл NDVI_zoen.zip не знайдено у папці Data_to transfer/")
    st.stop()

n_polygons = len(gdf)
zones      = sorted(gdf["ZONE"].unique())
COLORS     = ["#d7191c", "#fdae61", "#ffffbf", "#a6d96a", "#1a9641", "#3288bd", "#5e4fa2"]
c_dict     = {z: COLORS[i % len(COLORS)] for i, z in enumerate(zones)}


# ─── SIDEBAR ──────────────────────────────────────────────────────────────────
with st.sidebar:

    # ── Заголовок ──
    st.markdown('<div class="sidebar-title">🛰️ NDVI Аналіз</div>', unsafe_allow_html=True)

    # ── 1. Шар ──────────────────────────────────────────────────────────────
    st.markdown('<div class="sidebar-section">', unsafe_allow_html=True)
    st.markdown('<div class="section-label">📂 Шар даних</div>', unsafe_allow_html=True)
    mode = st.selectbox(
        "Шар даних",
        ["Векторні зони", "Растровий знімок"],
        index=1,
        label_visibility="collapsed",
    )
    st.markdown('</div>', unsafe_allow_html=True)

    # ── 2. Статистика NDVI ──────────────────────────────────────────────────
    ndvi_max = gdf["NDVI"].max()
    ndvi_min = gdf["NDVI"].min()
    st.markdown(f"""
    <div class="sidebar-section">
        <div class="section-label">📊 Статистика NDVI</div>
        <div class="ndvi-stats">
            <div class="ndvi-stat-box">
                <div class="ndvi-stat-val">{ndvi_max:.3f}</div>
                <div class="ndvi-stat-lbl">Максимум</div>
            </div>
            <div class="ndvi-stat-box">
                <div class="ndvi-stat-val low">{ndvi_min:.3f}</div>
                <div class="ndvi-stat-lbl">Мінімум</div>
            </div>
        </div>
        <div class="ndvi-count">Полігонів: {n_polygons}</div>
    </div>
    """, unsafe_allow_html=True)

    # ── 3. Підкладка — вибір через selectbox ────────────────────────────────
    st.markdown('<div class="sidebar-section">', unsafe_allow_html=True)
    st.markdown('<div class="section-label">🗺️ Підкладка</div>', unsafe_allow_html=True)

    basemap_options = list(BASEMAPS.keys())
    basemap_labels  = [f"{BASEMAPS[k]['icon']}  {k}" for k in basemap_options]

    selected_idx = st.radio(
        "Підкладка",
        range(len(basemap_options)),
        format_func=lambda i: basemap_labels[i],
        index=0,
        label_visibility="collapsed",
    )
    base_map = basemap_options[selected_idx]
    st.markdown('</div>', unsafe_allow_html=True)

    # ── 4. Колір зон + легенда (тільки для вектору) ─────────────────────────
    color_type = "ZONE"
    if mode == "Векторні зони":

        st.markdown('<div class="sidebar-section">', unsafe_allow_html=True)
        st.markdown('<div class="section-label">🎨 Колір полігонів</div>', unsafe_allow_html=True)
        color_type = st.radio(
            "Колір за",
            ["За зоною", "За NDVI"],
            label_visibility="collapsed",
        )
        color_type = "ZONE" if color_type == "За зоною" else "NDVI"
        st.markdown('</div>', unsafe_allow_html=True)

        # Легенда
        st.markdown('<div class="sidebar-section">', unsafe_allow_html=True)
        st.markdown('<div class="section-label">📋 Легенда зон</div>', unsafe_allow_html=True)

        legend_html = ""
        for z, clr in c_dict.items():
            legend_html += (
                f'<div class="legend-item">'
                f'<div class="legend-dot" style="background:{clr}"></div>'
                f'Зона {z}'
                f'</div>'
            )
        st.markdown(legend_html, unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)


# ─── ПОБУДОВА КАРТИ ───────────────────────────────────────────────────────────
bm_cfg = BASEMAPS[base_map]

m = folium.Map(
    tiles=bm_cfg["tiles"],
    attr=bm_cfg.get("attr", ""),
    zoom_control=True,
    scrollWheelZoom=True,
    dragging=True,
)

# Накладаємо підписи поверх супутника (якщо є overlay)
if "overlay" in bm_cfg:
    folium.TileLayer(
        tiles=bm_cfg["overlay"],
        attr=bm_cfg.get("overlay_attr", ""),
        name="Підписи",
        overlay=True,
        control=False,
    ).add_to(m)


# ── Растровий шар (кілька файлів) ────────────────────────────────────────────
if mode == "Растровий знімок":
    # Автоматично знаходимо всі NDVI_raster_RGB*.tif у папці
    raster_dir   = "Data_to transfer"
    raster_files = sorted([
        os.path.join(raster_dir, f)
        for f in os.listdir(raster_dir)
        if f.lower().startswith("ndvi_raster_rgb") and f.lower().endswith(".tif")
    ]) if os.path.isdir(raster_dir) else []

    if not raster_files:
        st.warning("Растрові файли NDVI_raster_RGB*.tif не знайдено у Data_to transfer/")
    else:
        all_bounds = []
        loaded = 0
        for rpath in raster_files:
            b64, bounds = get_raster_layer(rpath)
            if b64 and bounds:
                folium.raster_layers.ImageOverlay(
                    b64, bounds=bounds, opacity=1.0,
                    name=os.path.basename(rpath),
                ).add_to(m)
                all_bounds.append(bounds)
                loaded += 1

        if all_bounds:
            # Зум на об'єднані межі всіх тайлів
            s = min(b[0][0] for b in all_bounds)
            w = min(b[0][1] for b in all_bounds)
            n = max(b[1][0] for b in all_bounds)
            e = max(b[1][1] for b in all_bounds)
            m.fit_bounds([[s, w], [n, e]])
        if loaded < len(raster_files):
            st.warning(f"Завантажено {loaded} з {len(raster_files)} файлів.")


# ── Векторний шар ─────────────────────────────────────────────────────────────
else:
    norm = mcolors.Normalize(vmin=gdf["NDVI"].min(), vmax=gdf["NDVI"].max())
    cmap = mcolors.LinearSegmentedColormap.from_list(
        "ndvi", ["#d7191c", "#fdae61", "#ffffbf", "#a6d96a", "#1a9641"]
    )

    def style_function(feature):
        if color_type == "ZONE":
            fill = c_dict.get(feature["properties"].get("ZONE"), "#888")
        else:
            val  = feature["properties"].get("NDVI")
            fill = mcolors.to_hex(cmap(norm(val))) if val is not None else "#888"
        return {"fillColor": fill, "color": "#222", "weight": 0.4, "fillOpacity": 0.82}

    geojson_data = build_geojson(gdf.to_json(), 0.00002)

    folium.GeoJson(
        geojson_data,
        style_function=style_function,
        tooltip=folium.GeoJsonTooltip(
            fields=["ZONE", "NDVI"],
            aliases=["Зона:", "NDVI:"],
            localize=True,
        ),
    ).add_to(m)

    bounds = [
        [gdf.total_bounds[1], gdf.total_bounds[0]],
        [gdf.total_bounds[3], gdf.total_bounds[2]],
    ]
    m.fit_bounds(bounds)


# ── Рендер ────────────────────────────────────────────────────────────────────
st_folium(m, use_container_width=True, height=820, returned_objects=[])