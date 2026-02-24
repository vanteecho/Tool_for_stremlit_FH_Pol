# utils.py
import streamlit as st
import pandas as pd
import geopandas as gpd
import zipfile
import os
import tempfile
import numpy as np
from gradations import GRADATIONS

DATA_FILE = "Data_to transfer/data.zip"
DEFAULT_ENCODING = "utf-8"

UA_LABELS = {
    'K2O': 'Калій (K2O)', 'P2O5': 'Фосфор (P2O5)', 'P_olsen': 'Фосфор (Olsen)',
    'Organic_ma': 'Органічна речовина', 'pH__H2O_': 'pH водний', 'pH__KCl_': 'pH сольовий',
    'pH__DN_': 'pH (DN)', 'рН__CH3C': 'Гідролітична кислотність',
    'pH__hydroly': 'Гідролітична кислотність', 'NO3': 'Азот (N)',
    'S': 'Сірка (S)', 'B': 'Бор (B)', 'Ca': 'Кальцій (Ca)', 'Mg': 'Магній (Mg)',
    'Na': 'Натрій (Na)', 'Zn': 'Цинк (Zn)', 'Fe': 'Залізо (Fe)', 'Mn': 'Марганець (Mn)',
    'Cu': 'Мідь (Cu)', 'BS': 'Насиченість основами (BS)', 'EC_': 'Електропровідність (EC)',
    'Satur_H': 'Насиченість воднем (H)', 'Satur_Ca': 'Насиченість кальцієм (Ca)',
    'Satur_Mg': 'Насиченість магнієм (Mg)', 'Satur_K': 'Насиченість калієм (K)',
    'Satur_Na': 'Насиченість натрієм (Na)', 'SVO': 'Сума ввібраних основ (SVO)', 
    'SOC': 'Сума ввібраних основ (SVO)', 'Salinity': 'Засоленість'
}

def apply_theme():
    """Застосовує глобальну тему (Світла/Темна) та повертає статус is_dark."""
    if 'map_theme' not in st.session_state:
        st.session_state.map_theme = "Світла"

    with st.sidebar:
        st.header("⚙️ Налаштування")
        st.session_state.map_theme = st.radio("Оберіть тему інтерфейсу:", ["Світла", "Темна"], horizontal=True)

    is_dark = st.session_state.map_theme == "Темна"
    v_bg = "#0f172a" if is_dark else "#ffffff"
    v_text = "#f1f5f9" if is_dark else "#1e293b" 
    v_card = "#1e293b" if is_dark else "#f8f9fa"
    v_border = "#334155" if is_dark else "#e2e8f0"
    v_table_bg = "#1e293b" if is_dark else "#ffffff"

    st.markdown(f"""
        <style>
        .stApp {{ background-color: {v_bg}; color: {v_text}; }}
        h1, h2, h3, h4, span, p, label, .stMarkdown, [data-testid="stHeader"] {{ color: {v_text} !important; }}
        [data-testid="stDataFrame"], [data-testid="stTable"] {{ background-color: {v_table_bg} !important; border-radius: 10px; }}
        [data-testid="stSidebar"] {{ background-color: {v_card}; border-right: 1px solid {v_border}; }}
        
        .legend-card {{
            background-color: {v_card}; padding: 10px; border-radius: 10px; 
            border: 1px solid {v_border}; margin-bottom: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.05);
        }}
        .legend-title {{ color: {v_text}; opacity: 0.6; font-size: 11px; font-weight: bold; margin-bottom: 4px; }}
        .legend-item {{ display: flex; align-items: center; margin-bottom: 2px; }}
        .legend-label {{ color: {v_text}; font-size: 12px; }}
        .stTabs [data-baseweb="tab"] {{ color: {v_text}; }}
        </style>
        """, unsafe_allow_html=True)
    return is_dark

def detect_scale_type(column_name):
    col = str(column_name).lower()
    if 'dn' in col or 'ph' in col:
        if 'kcl' in col: return "pH Salt (KCl)"
        if 'ch3c' in col or 'hydroly' in col: return "Hydrolytic Acidity"
        return "pH Water"
    if 'soc' in col or 'svo' in col: return "Sum of Absorbed Bases (SVO)"
    if 'k2o' in col: return "Potassium (K2O)"
    if 'p2o5' in col or 'olsen' in col: return "Phosphate (P2O5)"
    if 'no3' in col: return "Nitrogen (N)"
    if 'ec_' in col: return "Electrical Conductivity (EC)"
    if 'salinity' in col: return "Salinity (Засоленість)"
    if 'organic' in col: return "Organic Matter"
    if 'b' == col or '_b_' in col: return "Boron (B)"
    if 'ca' == col: return "Calcium (Ca)"
    if 'mg' == col: return "Magnesium (Mg)"
    if 'bs' in col or 'satur_' in col: return "Percentage Scale"
    return None

def get_style_info(scale_type, value, method="default"):
    if pd.isna(value): return "#808080", "Немає даних"
    if not scale_type or scale_type not in GRADATIONS: return "#3388ff", "Значення"
    scales = GRADATIONS[scale_type]
    m_key = method.lower().strip() if method else "default"
    active_key = m_key if m_key in scales else "default"
    scale = scales.get(active_key, list(scales.values())[0])
    for grade in scale:
        if value <= grade['max']: return grade['color'], grade['label']
    return "#404040", "Максимум"

@st.cache_data
def load_data():
    if not os.path.exists(DATA_FILE): return None
    try:
        with tempfile.TemporaryDirectory() as tmp_dir:
            with zipfile.ZipFile(DATA_FILE, 'r') as zip_ref:
                zip_ref.extractall(tmp_dir)
            shp_files = [f for f in os.listdir(tmp_dir) if f.endswith('.shp')]
            if not shp_files: return None
            gdf = gpd.read_file(os.path.join(tmp_dir, shp_files[0]), encoding=DEFAULT_ENCODING)
            num_cols = gdf.select_dtypes(include=[np.number]).columns
            gdf[num_cols] = gdf[num_cols].round(2)
            for col in gdf.columns:
                if col != 'geometry' and not pd.api.types.is_numeric_dtype(gdf[col]):
                    gdf[col] = gdf[col].astype(str).replace(['NaT', 'None', 'nan', 'NaN'], '')
            if gdf.crs != "EPSG:4326": gdf = gdf.to_crs("EPSG:4326")
            if 'N_exemplar' in gdf.columns:
                gdf['sort_val'] = pd.to_numeric(gdf['N_exemplar'], errors='coerce')
                gdf = gdf.sort_values('sort_val').drop(columns=['sort_val'])
            return gdf
    except Exception as e:
        st.error(f"Помилка завантаження: {e}")
        return None