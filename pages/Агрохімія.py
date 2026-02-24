# pages/1_🌿_Агрохімія.py
import streamlit as st
import pandas as pd
import folium
from folium.plugins import FloatImage
from streamlit_folium import st_folium
import numpy as np
from utils import apply_theme, load_data, detect_scale_type, get_style_info, UA_LABELS
from gradations import GRADATIONS

st.set_page_config(layout="wide", page_title="Агрохімія", page_icon="🌿",
                   initial_sidebar_state="expanded")

st.markdown("""
<style>
    /* Прибираємо зайві відступи */
    .main .block-container { padding: 0.5rem 1rem 0 1rem !important; max-width: 100% !important; }
    header[data-testid="stHeader"] { display: none !important; }
    footer { display: none !important; }

    /* Сайдбар */
    section[data-testid="stSidebar"] {
        min-width: 260px !important; max-width: 260px !important;
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
    .kpi-row { display: flex; gap: 6px; flex-wrap: wrap; }
    .kpi-box {
        flex: 1; min-width: 60px; background: #f0f4f8;
        border-radius: 8px; padding: 7px 6px; text-align: center;
    }
    .kpi-val { font-size: 1rem; font-weight: 800; color: #1a7bff; line-height: 1.1; }
    .kpi-lbl { font-size: 0.58rem; color: #aaa; text-transform: uppercase; margin-top: 2px; }

    /* Панель фільтрів над картою */
    .filter-bar {
        display: flex; gap: 12px; align-items: flex-end;
        background: white; border-radius: 10px;
        padding: 10px 14px; margin-bottom: 8px;
        box-shadow: 0 1px 4px rgba(0,0,0,0.08);
        flex-wrap: wrap;
    }

    /* Легенда на карті */
    .map-legend {
        background: rgba(255,255,255,0.96);
        border-radius: 10px;
        padding: 10px 14px;
        box-shadow: 0 2px 8px rgba(0,0,0,0.15);
        font-family: sans-serif;
        min-width: 160px;
        max-width: 220px;
    }
    .map-legend-title {
        font-size: 11px; font-weight: 700;
        text-transform: uppercase; letter-spacing: 0.06em;
        color: #888; margin-bottom: 6px;
    }
    .map-legend-item {
        display: flex; align-items: center;
        gap: 7px; padding: 2px 0;
        font-size: 12px; color: #333;
    }
    .map-legend-dot {
        width: 13px; height: 13px; border-radius: 3px;
        flex-shrink: 0; box-shadow: 0 1px 2px rgba(0,0,0,0.2);
    }

    /* Компактні лейбли selectbox */
    div[data-testid="stSelectbox"] label,
    div[data-testid="stMultiSelect"] label {
        font-size: 0.72rem !important; font-weight: 600;
        color: #888 !important;
    }

    /* Вкладки без відступів */
    div[data-testid="stTabContent"] { padding: 0 !important; }
</style>
""", unsafe_allow_html=True)

is_dark = apply_theme()

# ─── ДАНІ ─────────────────────────────────────────────────────────────────────
gdf_raw = load_data()
if gdf_raw is None:
    st.warning("⚠️ Дані не знайдено. Перевірте наявність data.zip.")
    st.stop()

# ─── SIDEBAR — тільки підкладка і статистика ──────────────────────────────────
with st.sidebar:
    st.markdown('<div class="sidebar-title">🌿 Агрохімія</div>', unsafe_allow_html=True)

    st.markdown('<div class="s-box"><div class="s-label">🗺️ Підкладка</div>', unsafe_allow_html=True)
    basemap_choice = st.radio(
        "bm", ["☀️ Світла", "🛰️ Супутник", "🌑 Темна", "🗺️ OSM"],
        index=0, label_visibility="collapsed",
    )
    st.markdown('</div>', unsafe_allow_html=True)

    # Статистика — заповнюється після фільтрів (placeholder)
    stats_placeholder = st.empty()


# ─── ФІЛЬТРИ НАД КАРТОЮ ───────────────────────────────────────────────────────
# Три колонки в одному рядку
c1, c2, c3 = st.columns([1.2, 1.8, 1.5])

with c1:
    farm_list = sorted(gdf_raw['Farm'].unique().tolist())
    sel_farm  = st.selectbox("🏢 Підприємство", ["Всі"] + farm_list)
    gdf_farm  = gdf_raw if sel_farm == "Всі" else gdf_raw[gdf_raw['Farm'] == sel_farm]

with c2:
    field_list = sorted(gdf_farm['field_name'].unique().tolist())
    sel_fields = st.multiselect("📍 Поля", field_list, default=[], placeholder="Всі поля…")
    gdf_res    = gdf_farm if not sel_fields else gdf_farm[gdf_farm['field_name'].isin(sel_fields)]

with c3:
    exclude   = ['OBJECTID', 'geometry', 'Area_zone', 'X_coord_Lo', 'Y_coord_La',
                 'till_area', 'Shape_Leng', 'Shape_Area']
    num_cols  = [c for c in gdf_res.select_dtypes(include=[np.number]).columns if c not in exclude]
    if not num_cols:
        num_cols = [c for c in gdf_farm.select_dtypes(include=[np.number]).columns if c not in exclude]
    value_col = st.selectbox("📊 Показник", num_cols, format_func=lambda x: UA_LABELS.get(x, x))

# ─── ОБЧИСЛЕННЯ ПІСЛЯ ФІЛЬТРІВ ────────────────────────────────────────────────
all_cols = gdf_res.columns.tolist()
try:
    idx        = all_cols.index(value_col)
    method_col = all_cols[idx + 1] if idx + 1 < len(all_cols) else None
except Exception:
    method_col = None

detected_scale = detect_scale_type(value_col)

# Статистика в сайдбар
if not gdf_res.empty:
    total_area = gdf_res['Area_zone'].sum()
    avg_val    = gdf_res[value_col].mean()
    min_val    = gdf_res[value_col].min()
    max_val    = gdf_res[value_col].max()
    n_zones    = len(gdf_res)

    with stats_placeholder:
        st.markdown(f"""
        <div class="s-box">
            <div class="s-label">📈 Статистика</div>
            <div class="kpi-row">
                <div class="kpi-box">
                    <div class="kpi-val">{n_zones}</div>
                    <div class="kpi-lbl">Зон</div>
                </div>
                <div class="kpi-box">
                    <div class="kpi-val">{total_area:,.0f}</div>
                    <div class="kpi-lbl">га</div>
                </div>
            </div>
            <div class="kpi-row" style="margin-top:6px">
                <div class="kpi-box">
                    <div class="kpi-val" style="color:#27ae60">{avg_val:.2f}</div>
                    <div class="kpi-lbl">Середнє</div>
                </div>
                <div class="kpi-box">
                    <div class="kpi-val" style="color:#e74c3c">{min_val:.1f}</div>
                    <div class="kpi-lbl">Мін</div>
                </div>
                <div class="kpi-box">
                    <div class="kpi-val" style="color:#2980b9">{max_val:.1f}</div>
                    <div class="kpi-lbl">Макс</div>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)

# ─── КАРТА + ТАБЛИЦЯ ──────────────────────────────────────────────────────────
tab_map, tab_data = st.tabs(["🗺️ Карта", "📋 Таблиця"])

TILES = {
    "☀️ Світла":   ("CartoDB positron",    "CartoDB"),
    "🌑 Темна":    ("CartoDB dark_matter", "CartoDB"),
    "🗺️ OSM":      ("OpenStreetMap",       "OSM"),
    "🛰️ Супутник": (
        "https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}",
        "Esri, Maxar",
    ),
}
tile_url, tile_attr = TILES[basemap_choice]

with tab_map:
    if gdf_res.empty:
        st.info("Немає даних для відображення — змініть фільтри.")
    else:
        m = folium.Map(tiles=None, zoom_control=True, scrollWheelZoom=True)
        folium.TileLayer(tiles=tile_url, attr=tile_attr, control=False).add_to(m)
        m.fit_bounds([
            [gdf_res.total_bounds[1], gdf_res.total_bounds[0]],
            [gdf_res.total_bounds[3], gdf_res.total_bounds[2]],
        ])

        # Обводка: темна на світлих підкладках, біла на темних і супутнику
        border_color = "#555555" if basemap_choice in ["☀️ Світла", "🗺️ OSM"] else "#ffffff"
        border_w     = 0.8

        def style_f(feature):
            props = feature['properties']
            val   = props.get(value_col)
            m_val = str(props.get(method_col, "default")).lower().strip() if method_col else "default"
            color, _ = get_style_info(detected_scale, val, m_val)
            return {
                'fillColor':  color,
                'color':      border_color,
                'weight':     border_w,
                'fillOpacity': 0.82,
            }

        # Тільки колонки які реально є в даних
        available = set(gdf_res.columns.tolist())
        candidate_fields   = ['Farm', 'field_name', 'N_exemplar', 'Area_zone', value_col]
        candidate_aliases  = ['Підприємство:', 'Поле:', '№ Зразка:', 'Площа (га):',
                              f'{UA_LABELS.get(value_col, value_col)}:']

        t_fields, t_aliases = [], []
        for f, a in zip(candidate_fields, candidate_aliases):
            if f in available:
                t_fields.append(f)
                t_aliases.append(a)

        if method_col and method_col in available:
            t_fields.append(method_col)
            t_aliases.append('Методика:')

        folium.GeoJson(
            gdf_res,
            style_function=style_f,
            tooltip=folium.GeoJsonTooltip(
                fields=t_fields, aliases=t_aliases,
                style="font-family: sans-serif; font-size: 13px; border-radius: 6px;",
            ),
        ).add_to(m)

        # ── Легенда прямо на карті через folium macro ──────────────────────
        if detected_scale and detected_scale in GRADATIONS:
            keys = set()
            if method_col:
                for rm in gdf_res[method_col].dropna().unique():
                    m_c = str(rm).lower().strip()
                    keys.add(m_c if m_c in GRADATIONS[detected_scale] else "default")
            if not keys:
                keys.add("default")

            # Будуємо HTML легенди
            legend_items_html = ""
            for k in sorted(keys):
                grads = GRADATIONS[detected_scale].get(k, GRADATIONS[detected_scale].get("default", []))
                if k != "default" and len(keys) > 1:
                    legend_items_html += (
                        f'<div style="font-size:10px;font-weight:700;text-transform:uppercase;'
                        f'color:#aaa;letter-spacing:0.06em;margin:6px 0 3px">{k.upper()}</div>'
                    )
                for g in grads:
                    legend_items_html += (
                        f'<div style="display:flex;align-items:center;gap:7px;padding:2px 0;'
                        f'font-size:12px;color:#333">'
                        f'<div style="width:13px;height:13px;border-radius:3px;flex-shrink:0;'
                        f'background:{g["color"]};box-shadow:0 1px 2px rgba(0,0,0,0.2)"></div>'
                        f'{g["label"]}'
                        f'</div>'
                    )

            legend_title = UA_LABELS.get(value_col, value_col)
            legend_html = f"""
            {{% macro html(this, kwargs) %}}
            <div style="
                position: fixed;
                bottom: 30px; right: 10px;
                z-index: 1000;
                background: rgba(255,255,255,0.96);
                border-radius: 10px;
                padding: 12px 15px;
                box-shadow: 0 2px 12px rgba(0,0,0,0.18);
                font-family: sans-serif;
                min-width: 160px; max-width: 230px;
                pointer-events: none;
            ">
                <div style="font-size:11px;font-weight:700;text-transform:uppercase;
                            letter-spacing:0.06em;color:#888;margin-bottom:7px">
                    {legend_title}
                </div>
                {legend_items_html}
            </div>
            {{% endmacro %}}
            """

            from branca.element import MacroElement, Template
            legend_el = MacroElement()
            legend_el._template = Template(legend_html)
            m.get_root().add_child(legend_el)

        st_folium(m, use_container_width=True, height=750, returned_objects=[])

with tab_data:
    if gdf_res.empty:
        st.info("Немає даних для відображення.")
    else:
        cols_to_show = [c for c in gdf_res.columns
                        if c not in ['geometry', 'OBJECTID', 'X_coord_Lo', 'Y_coord_La',
                                     'till_area', 'Shape_Leng', 'Shape_Area']]
        df_table  = gdf_res[cols_to_show].rename(columns=UA_LABELS)
        val_label = UA_LABELS.get(value_col, value_col)

        st.dataframe(
            df_table,
            use_container_width=True,
            height=750,
            hide_index=True,
            column_config={
                val_label: st.column_config.ProgressColumn(
                    val_label,
                    format="%.2f",
                    min_value=float(gdf_res[value_col].min()),
                    max_value=float(gdf_res[value_col].max()),
                ),
                "Площа (га)": st.column_config.NumberColumn(format="%.2f"),
            },
        )