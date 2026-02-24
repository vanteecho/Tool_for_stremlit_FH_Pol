# pages/3_🚜_Лінії_заїзду.py
import streamlit as st
import geopandas as gpd
import folium
from folium.plugins import Draw
from streamlit_folium import st_folium
import pandas as pd
import numpy as np
import os, io, json, zipfile, tempfile, datetime
from shapely.geometry import shape

# ─── КОНФІГ ───────────────────────────────────────────────────────────────────
st.set_page_config(layout="wide", page_title="Лінії заїзду", page_icon="🚜",
                   initial_sidebar_state="expanded")

st.markdown("""
<style>
    .main .block-container { padding: 0 !important; max-width: 100% !important; }
    header[data-testid="stHeader"] { display: none !important; }
    footer { display: none !important; }
    section[data-testid="stSidebar"] {
        min-width: 270px !important; max-width: 270px !important;
        background: #f8f9fa;
    }
    section[data-testid="stSidebar"] > div { padding: 1rem 0.8rem !important; }
    .sidebar-title { font-size: 1.1rem; font-weight: 700; color: #1a1a2e; margin-bottom: 0.8rem; }
    .s-box {
        background: white; border-radius: 10px;
        padding: 11px 13px; margin-bottom: 9px;
        box-shadow: 0 1px 3px rgba(0,0,0,0.08);
    }
    .s-label {
        font-size: 0.68rem; font-weight: 700; text-transform: uppercase;
        letter-spacing: 0.08em; color: #999; margin-bottom: 7px;
    }
    .stat-row { display: flex; gap: 8px; }
    .stat-box { flex:1; background:#f0f4f8; border-radius:8px; padding:7px 8px; text-align:center; }
    .stat-val { font-size:1.1rem; font-weight:700; color:#0078ff; line-height:1.1; }
    .stat-lbl { font-size:0.6rem; color:#aaa; text-transform:uppercase; }
    .drawn-count {
        font-size: 1.8rem; font-weight: 800; color: #e74c3c;
        text-align: center; line-height: 1;
    }
    .drawn-lbl { font-size: 0.65rem; color: #aaa; text-align: center; margin-bottom: 8px; }
    .tip {
        font-size: 0.7rem; color: #666; background: #fffbe6;
        border-left: 3px solid #f0a500; padding: 5px 8px;
        border-radius: 0 6px 6px 0; margin-bottom: 8px;
    }
    /* Компактний multiselect */
    div[data-testid="stMultiSelect"] { margin-bottom: 0 !important; }
    div[data-testid="stMultiSelect"] > label { font-size: 0.75rem !important; }
</style>
""", unsafe_allow_html=True)


# ─── ІНІЦІАЛІЗАЦІЯ SESSION STATE ──────────────────────────────────────────────
# Робимо це НА ПОЧАТКУ — до будь-якого рендеру
if "drawn_features" not in st.session_state:
    st.session_state["drawn_features"] = []
if "clear_requested" not in st.session_state:
    st.session_state["clear_requested"] = False


# ─── ФУНКЦІЇ ──────────────────────────────────────────────────────────────────

@st.cache_data(show_spinner="Завантаження ліній заїзду…")
def load_lines():
    path = "Data_to transfer/Enter_line.zip"
    if not os.path.exists(path):
        return None
    return gpd.read_file(f"zip://{path}").to_crs(epsg=4326)


@st.cache_data(show_spinner="Завантаження полів…")
def load_fields():
    for path in ["Data_to transfer/Field.zip", "Data_to transfer/Field.shp"]:
        if os.path.exists(path):
            src = f"zip://{path}" if path.endswith(".zip") else path
            gdf = gpd.read_file(src).to_crs(epsg=4326)
            gdf.columns = [c.lower() if c.lower() != "geometry" else "geometry"
                           for c in gdf.columns]
            return gdf
    return None


@st.cache_data(show_spinner="Розрахунок буферу…")
def compute_buffer_geojson(lines_json: str, buf_m: float) -> str:
    gdf = gpd.GeoDataFrame.from_features(json.loads(lines_json)["features"], crs="EPSG:4326")
    lon = gdf.geometry.centroid.x.mean()
    utm_epsg = int(32600 + np.floor((lon + 180) / 6) + 1)
    gdf_utm = gdf.to_crs(epsg=utm_epsg)
    gdf_utm["geometry"] = gdf_utm.buffer(buf_m)
    return gdf_utm.to_crs(epsg=4326).to_json()


def sanitize_gdf(gdf: gpd.GeoDataFrame) -> gpd.GeoDataFrame:
    """Конвертує Timestamp/date колонки → str щоб folium не падав."""
    gdf = gdf.copy()
    for col in gdf.columns:
        if col == "geometry":
            continue
        dtype = str(gdf[col].dtype)
        if any(t in dtype for t in ("datetime", "date", "timedelta")):
            gdf[col] = gdf[col].astype(str)
        elif dtype == "object":
            sample = gdf[col].dropna()
            if not sample.empty and isinstance(
                sample.iloc[0], (datetime.date, datetime.datetime, pd.Timestamp)
            ):
                gdf[col] = gdf[col].astype(str)
    return gdf


def parse_drawn_features(result: dict) -> list:
    """
    Витягує список Feature з результату st_folium.
    Повертає [] якщо all_drawings явно порожній (користувач очистив карту).
    Повертає None якщо all_drawings взагалі не прийшов (нічого не змінилось).
    """
    raw = result.get("all_drawings")

    # all_drawings прийшов — парсимо (навіть якщо порожній)
    if raw is not None:
        features = []
        if isinstance(raw, dict):
            features = raw.get("features", [])
        elif isinstance(raw, list):
            for item in raw:
                if not isinstance(item, dict):
                    continue
                if item.get("type") == "FeatureCollection":
                    features.extend(item.get("features", []))
                elif item.get("type") == "Feature":
                    features.append(item)
        return features  # може бути [] — це ок, значить очищено

    # all_drawings не прийшов — повертаємо None (без змін)
    return None


def make_shp_zip(geojson_features: list) -> bytes:
    rows = []
    for i, feat in enumerate(geojson_features):
        geom = shape(feat["geometry"])
        if geom.geom_type not in ("LineString", "MultiLineString"):
            geom = geom.boundary
        rows.append({"id": i + 1, "geometry": geom})
    if not rows:
        return b""
    gdf = gpd.GeoDataFrame(rows, crs="EPSG:4326")
    with tempfile.TemporaryDirectory() as tmp:
        gdf.to_file(os.path.join(tmp, "New_line.shp"))
        buf = io.BytesIO()
        with zipfile.ZipFile(buf, "w") as zf:
            for fname in os.listdir(tmp):
                zf.write(os.path.join(tmp, fname), fname)
        return buf.getvalue()


# ─── ДАНІ ─────────────────────────────────────────────────────────────────────
lines_gdf  = load_lines()
fields_gdf = load_fields()

if lines_gdf is None:
    st.error("❌ Enter_line.zip не знайдено у Data_to transfer/")
    st.stop()

has_fields = (
    fields_gdf is not None
    and "group" in fields_gdf.columns
    and "f_name" in fields_gdf.columns
)


# ─── SIDEBAR ──────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown('<div class="sidebar-title">🚜 Лінії заїзду</div>', unsafe_allow_html=True)

    # ── Статистика ──
    n_drawn_now = len(st.session_state["drawn_features"])
    st.markdown(f"""
    <div class="s-box">
        <div class="s-label">📊 Дані</div>
        <div class="stat-row">
            <div class="stat-box">
                <div class="stat-val">{len(lines_gdf)}</div>
                <div class="stat-lbl">Ліній</div>
            </div>
            <div class="stat-box">
                <div class="stat-val">{len(fields_gdf) if fields_gdf is not None else 0}</div>
                <div class="stat-lbl">Полів</div>
            </div>
            <div class="stat-box">
                <div class="stat-val" style="color:#e74c3c">{n_drawn_now}</div>
                <div class="stat-lbl">Намальовано</div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # ── Підкладка ──
    st.markdown('<div class="s-box"><div class="s-label">🗺️ Підкладка</div>', unsafe_allow_html=True)
    basemap_choice = st.radio(
        "bm", ["🛰️ Супутник", "☀️ Світла", "🌑 Темна", "🗺️ OSM"],
        index=0, label_visibility="collapsed",
    )
    st.markdown('</div>', unsafe_allow_html=True)

    # ── Шари ──
    st.markdown('<div class="s-box"><div class="s-label">👁️ Шари</div>', unsafe_allow_html=True)
    show_lines   = st.checkbox("Лінії заїзду",            value=True)
    show_fields  = st.checkbox("Межі полів",               value=has_fields) if has_fields else False
    show_buffer  = st.checkbox("Буфер 25 м",              value=False)
    show_drawing = st.checkbox("Інструмент малювання",    value=False)
    st.markdown('</div>', unsafe_allow_html=True)

    # ── Фільтри — компактні multiselect замість selectbox зі скролом ──
    filtered_lines  = lines_gdf.copy()
    filtered_fields = fields_gdf.copy() if fields_gdf is not None else None

    if has_fields:
        st.markdown('<div class="s-box"><div class="s-label">🔍 Фільтри</div>', unsafe_allow_html=True)

        all_groups = sorted(fields_gdf["group"].dropna().astype(str).unique().tolist())

        # Кластер: pills через multiselect (компактно, без скролу)
        sel_groups = st.multiselect(
            "Кластер:",
            options=all_groups,
            default=[],
            placeholder="Всі кластери",
        )

        # Залежно від кластеру — список полів
        if sel_groups:
            mask_g = fields_gdf["group"].astype(str).isin(sel_groups)
            avail_fields = sorted(fields_gdf[mask_g]["f_name"].dropna().unique().tolist())
        else:
            avail_fields = sorted(fields_gdf["f_name"].dropna().unique().tolist())

        sel_fields = st.multiselect(
            "Поле:",
            options=avail_fields,
            default=[],
            placeholder="Всі поля",
        )

        # Фільтруємо
        filtered_fields = fields_gdf.copy()
        if sel_groups:
            filtered_fields = filtered_fields[filtered_fields["group"].astype(str).isin(sel_groups)]
        if sel_fields:
            filtered_fields = filtered_fields[filtered_fields["f_name"].isin(sel_fields)]

        # Лінії — просторове перетинання
        if (sel_groups or sel_fields) and not filtered_fields.empty:
            try:
                union = filtered_fields.geometry.union_all()
                idx = lines_gdf.sindex.query(union, predicate="intersects")
                filtered_lines = lines_gdf.iloc[idx].copy()
            except Exception:
                mask = lines_gdf.geometry.intersects(filtered_fields.geometry.union_all())
                filtered_lines = lines_gdf[mask].copy()
        elif (sel_groups or sel_fields) and filtered_fields.empty:
            filtered_lines = lines_gdf.iloc[0:0].copy()

        st.caption(f"Показано: {len(filtered_lines)} ліній / {len(filtered_fields)} полів")
        st.markdown('</div>', unsafe_allow_html=True)

    # ── Малювання ──
    if show_drawing:
        st.markdown('<div class="s-box"><div class="s-label">✏️ Малювання</div>', unsafe_allow_html=True)
        st.markdown(
            '<div class="tip">Намалюйте лінію на карті (подвійний клік — завершити). '
            'Лічильник оновиться після наступної дії на карті.</div>',
            unsafe_allow_html=True,
        )

        drawn_data = st.session_state["drawn_features"]
        if drawn_data:
            zip_bytes = make_shp_zip(drawn_data)
            if zip_bytes:
                st.download_button(
                    "⬇️ Завантажити New_line.zip",
                    data=zip_bytes,
                    file_name="New_line.zip",
                    mime="application/zip",
                    use_container_width=True,
                )
            st.caption("🗑️ Для видалення ліній з карти — використовуйте кошик у панелі інструментів карти, потім «Save».")
        else:
            st.caption("Намальованих ліній немає")

        st.markdown('</div>', unsafe_allow_html=True)


# ─── ПОБУДОВА КАРТИ ───────────────────────────────────────────────────────────
TILES = {
    "🛰️ Супутник": (
        "https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}",
        "Esri, Maxar",
    ),
    "☀️ Світла":  ("CartoDB positron",    "CartoDB"),
    "🌑 Темна":   ("CartoDB dark_matter", "CartoDB"),
    "🗺️ OSM":     ("OpenStreetMap",       "OSM"),
}
tile_url, tile_attr = TILES[basemap_choice]

cx = (filtered_lines.geometry.centroid.x.mean()
      if not filtered_lines.empty else lines_gdf.geometry.centroid.x.mean())
cy = (filtered_lines.geometry.centroid.y.mean()
      if not filtered_lines.empty else lines_gdf.geometry.centroid.y.mean())

m = folium.Map(location=[cy, cx], zoom_start=14, tiles=None,
               zoom_control=True, scrollWheelZoom=True)

folium.TileLayer(
    tiles=tile_url, attr=tile_attr,
    name=basemap_choice.split()[-1],  # назва без емодзі для легенди
    control=True,
).add_to(m)

# ── Межі полів ────────────────────────────────────────────────────────────────
if show_fields and filtered_fields is not None and not filtered_fields.empty:
    ff = sanitize_gdf(filtered_fields)
    palette = ["#FF6B35","#4ECDC4","#45B7D1","#96CEB4","#FFEAA7",
               "#DDA0DD","#98D8C8","#F7DC6F","#BB8FCE","#85C1E9"]
    groups_u = sorted(str(x) for x in ff["group"].unique()) if "group" in ff.columns else []
    g_colors = {g: palette[i % len(palette)] for i, g in enumerate(groups_u)}

    folium.GeoJson(
        ff.__geo_interface__,
        name="Поля",
        style_function=lambda feat: {
            "fillColor": g_colors.get(str(feat["properties"].get("group", "")), "#aaa"),
            "color": "#555", "weight": 1.5, "fillOpacity": 0.25,
        },
        tooltip=folium.GeoJsonTooltip(
            fields=[c for c in ["f_name", "group"] if c in ff.columns],
            aliases=["Поле:", "Кластер:"],
        ),
    ).add_to(m)

# ── Буфер ─────────────────────────────────────────────────────────────────────
if show_buffer and not filtered_lines.empty:
    with st.spinner("Розрахунок буферу 25 м…"):
        buf_json = compute_buffer_geojson(sanitize_gdf(filtered_lines).to_json(), 25)
    folium.GeoJson(
        json.loads(buf_json), name="Буфер 25 м",
        style_function=lambda _: {
            "fillColor": "#FFD700", "color": "#FFA500",
            "weight": 1, "fillOpacity": 0.3,
        },
    ).add_to(m)

# ── Лінії заїзду ──────────────────────────────────────────────────────────────
if show_lines and not filtered_lines.empty:
    fl = sanitize_gdf(filtered_lines)
    tooltip_cols = [c for c in fl.columns if c != "geometry"][:3]
    folium.GeoJson(
        fl.__geo_interface__, name="Лінії заїзду",
        style_function=lambda _: {"color": "#00AAFF", "weight": 2.5, "opacity": 0.9},
        tooltip=folium.GeoJsonTooltip(fields=tooltip_cols) if tooltip_cols else None,
    ).add_to(m)

# ── Інструмент малювання ──────────────────────────────────────────────────────
if show_drawing:
    Draw(
        draw_options={
            "polyline":     {"shapeOptions": {"color": "#e74c3c", "weight": 3}},
            "polygon":      False,
            "rectangle":    False,
            "circle":       False,
            "marker":       False,
            "circlemarker": False,
        },
        edit_options={"edit": True, "remove": True},
    ).add_to(m)

if not filtered_lines.empty:
    b = filtered_lines.total_bounds
    m.fit_bounds([[b[1], b[0]], [b[3], b[2]]])

folium.LayerControl(collapsed=False).add_to(m)

# ─── РЕНДЕР ───────────────────────────────────────────────────────────────────
result = st_folium(
    m,
    use_container_width=True,
    height=820,
    returned_objects=["all_drawings", "last_active_drawing"],
)

# ─── ОНОВЛЕННЯ СТАНУ МАЛЮВАННЯ ────────────────────────────────────────────────
# Правило: довіряємо ТІЛЬКИ тому що повертає Leaflet через all_drawings.
# Якщо all_drawings = [] — значить на карті нічого немає (користувач очистив).
# Якщо all_drawings = None/відсутній — карта не повернула дані (нічого не змінилось).

if result and show_drawing:
    raw = result.get("all_drawings")
    existing = st.session_state["drawn_features"]

    # all_drawings повернувся явно (навіть якщо порожній список/dict)
    if raw is not None:
        new_features = parse_drawn_features(result)

        # Оновлюємо якщо кількість змінилась (додали або видалили)
        if len(new_features) != len(existing):
            st.session_state["drawn_features"] = new_features
            st.rerun()

    # last_active_drawing без all_drawings — просто нова лінія додана
    elif result.get("last_active_drawing"):
        feat = result["last_active_drawing"]
        if isinstance(feat, dict) and feat.get("type") == "Feature":
            if feat not in existing:
                st.session_state["drawn_features"] = existing + [feat]
                st.rerun()