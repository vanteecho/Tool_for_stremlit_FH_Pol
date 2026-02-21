# pages/1_🌿_Агрохімія.py
import streamlit as st
import pandas as pd
import folium
from folium.plugins import Fullscreen
from streamlit_folium import st_folium
import numpy as np
from utils import apply_theme, load_data, detect_scale_type, get_style_info, UA_LABELS
from gradations import GRADATIONS

st.set_page_config(layout="wide", page_title="Агрохімія", page_icon="🌿")
is_dark = apply_theme()

gdf_raw = load_data()
if gdf_raw is None: 
    st.warning("Дані не знайдено. Перевірте наявність data.zip.")
    st.stop()

st.markdown("<h2 style='text-align: center; padding-top: 0;'>🌿 Агрохімічне обстеження ґрунтів</h2>", unsafe_allow_html=True)

c1, c2, c3 = st.columns(3)

with c1:
    farm_list = sorted(gdf_raw['Farm'].unique().tolist())
    sel_farm = st.selectbox("Підприємство", ["Всі"] + farm_list)
    gdf_farm_filtered = gdf_raw if sel_farm == "Всі" else gdf_raw[gdf_raw['Farm'] == sel_farm]

with c2:
    field_list = sorted(gdf_farm_filtered['field_name'].unique().tolist())
    sel_fields = st.multiselect("Оберіть поля", field_list, default=[], placeholder="За замовчуванням: Всі поля")
    gdf_res = gdf_farm_filtered if not sel_fields else gdf_farm_filtered[gdf_farm_filtered['field_name'].isin(sel_fields)]

with c3:
    exclude = ['OBJECTID', 'geometry', 'Area_zone', 'X_coord_Lo', 'Y_coord_La', 'till_area', 'Shape_Leng', 'Shape_Area']
    num_cols = [c for c in gdf_res.select_dtypes(include=[np.number]).columns if c not in exclude]
    if not num_cols:
        num_cols = [c for c in gdf_farm_filtered.select_dtypes(include=[np.number]).columns if c not in exclude]
    value_col = st.selectbox("Показник", num_cols, format_func=lambda x: UA_LABELS.get(x, x))

all_cols = gdf_res.columns.tolist()
try:
    idx = all_cols.index(value_col)
    method_col = all_cols[idx + 1] if idx + 1 < len(all_cols) else None
except: method_col = None
detected_scale = detect_scale_type(value_col)

t_map, t_data = st.tabs(["🗺️ Карта", "📋 Таблиця"])

with t_map:
    if not gdf_res.empty:
        tiles = "CartoDB Positron" if not is_dark else "CartoDB Dark Matter"
        m = folium.Map(tiles=tiles, zoom_start=12)
        m.fit_bounds([[gdf_res.total_bounds[1], gdf_res.total_bounds[0]], [gdf_res.total_bounds[3], gdf_res.total_bounds[2]]])
        Fullscreen().add_to(m)

        def style_f(feature):
            props = feature['properties']
            val = props.get(value_col)
            m_val = str(props.get(method_col, "default")).lower().strip() if method_col else "default"
            color, _ = get_style_info(detected_scale, val, m_val)
            return {'fillColor': color, 'color': '#2c3e50', 'weight': 0.7, 'fillOpacity': 0.75}

        t_fields = ['Farm', 'field_name', 'N_exemplar', 'Area_zone', value_col]
        t_aliases = ['Підприємство:', 'Поле:', '№ Зразка:', 'Площа (га):', f'{UA_LABELS.get(value_col, value_col)}:']
        if method_col:
            t_fields.append(method_col); t_aliases.append('Методика:')

        folium.GeoJson(gdf_res, style_function=style_f, tooltip=folium.GeoJsonTooltip(fields=t_fields, aliases=t_aliases)).add_to(m)
        st_folium(m, width="100%", height=650)

with t_data:
    st.subheader("Дані обстеження")
    cols_to_show = [c for c in gdf_res.columns if c not in ['geometry', 'OBJECTID', 'X_coord_Lo', 'Y_coord_La', 'till_area', 'Shape_Leng', 'Shape_Area']]
    df_table = gdf_res[cols_to_show].rename(columns=UA_LABELS)
    st.dataframe(df_table, use_container_width=True, height=550)

with st.sidebar:
    if detected_scale and detected_scale in GRADATIONS:
        st.markdown("### 🎨 Легенда")
        st.markdown(f"**{UA_LABELS.get(value_col, value_col)}**")
        keys = set()
        if method_col:
            for rm in gdf_res[method_col].unique():
                if pd.notna(rm) and str(rm).strip():
                    m_c = str(rm).lower().strip()
                    keys.add(m_c if m_c in GRADATIONS[detected_scale] else "default")
        else: keys.add("default")
        
        if not keys: keys.add("default")

        for k in sorted(list(keys)):
            st.markdown(f"<div class='legend-card'>", unsafe_allow_html=True)
            st.markdown(f"<div class='legend-title'>{k.upper() if k != 'default' else 'ШКАЛА'}</div>", unsafe_allow_html=True)
            for g in GRADATIONS[detected_scale].get(k, GRADATIONS[detected_scale].get("default", [])):
                st.markdown(f"""<div class='legend-item'><div style='width:16px;height:16px;background-color:{g['color']};border-radius:3px;margin-right:10px;border:1px solid rgba(0,0,0,0.1)'></div><div class='legend-label'>{g['label']}</div></div>""", unsafe_allow_html=True)
            st.markdown("</div>", unsafe_allow_html=True)