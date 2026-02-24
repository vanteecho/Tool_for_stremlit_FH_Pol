# app.py
import streamlit as st
import os, sys
import numpy as np
import pandas as pd
import geopandas as gpd

ROOT = os.path.dirname(os.path.abspath(__file__))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)
os.chdir(ROOT)

st.set_page_config(page_title="ГІС Портал — Головна", page_icon="🌍",
                   layout="wide", initial_sidebar_state="expanded")

st.markdown("""
<style>
    .main .block-container { padding: 0.8rem 1.2rem 0.5rem !important; max-width: 100% !important; }
    header[data-testid="stHeader"] { display: none !important; }
    footer { display: none !important; }
</style>
""", unsafe_allow_html=True)

# ─── ЗАВАНТАЖЕННЯ ДАНИХ ───────────────────────────────────────────────────────
@st.cache_data(show_spinner=False)
def load_agro():
    path = os.path.join(ROOT, "Data_to transfer", "data.zip")
    if not os.path.exists(path): return None
    try:
        gdf = gpd.read_file(f"zip://{path}")
        rename = {}
        for col in gdf.columns:
            low = col.lower()
            if low in ("farm", "farm_name"):   rename[col] = "Farm"
            if low in ("field", "field_name"): rename[col] = "field_name"
        if rename: gdf = gdf.rename(columns=rename)
        for col in gdf.select_dtypes(include="object").columns:
            try:
                gdf[col] = gdf[col].apply(
                    lambda x: x.encode("latin-1").decode("utf-8") if isinstance(x, str) else x)
            except Exception: pass
        return gdf.to_crs(epsg=4326)
    except Exception: return None

@st.cache_data(show_spinner=False)
def load_ndvi():
    path = os.path.join(ROOT, "Data_to transfer", "NDVI_zoen.zip")
    if not os.path.exists(path): return None
    try:
        g = gpd.read_file(f"zip://{path}")
        g.columns = [c.upper() if c.lower() != "geometry" else "geometry" for c in g.columns]
        return g
    except Exception: return None

@st.cache_data(show_spinner=False)
def load_lines():
    path = os.path.join(ROOT, "Data_to transfer", "Enter_line.zip")
    if not os.path.exists(path): return None
    try: return gpd.read_file(f"zip://{path}").to_crs(epsg=4326)
    except Exception: return None

@st.cache_data(show_spinner=False)
def load_fields():
    for fname in ["Field.zip", "Field.shp"]:
        path = os.path.join(ROOT, "Data_to transfer", fname)
        if os.path.exists(path):
            try:
                src = f"zip://{path}" if fname.endswith(".zip") else path
                g = gpd.read_file(src).to_crs(epsg=4326)
                g.columns = [c.lower() if c.lower() != "geometry" else "geometry" for c in g.columns]
                return g
            except Exception: return None
    return None

agro   = load_agro()
ndvi   = load_ndvi()
lines  = load_lines()
fields = load_fields()

# ─── ХЕЛПЕРИ ─────────────────────────────────────────────────────────────────
def badge_html(ok):
    if ok:
        return '<span style="background:rgba(39,174,96,.12);color:#27ae60;border:1px solid rgba(39,174,96,.3);border-radius:20px;padding:1px 8px;font-size:.58rem;font-weight:700;margin-left:6px">● OK</span>'
    return '<span style="background:rgba(231,76,60,.08);color:#e74c3c;border:1px solid rgba(231,76,60,.22);border-radius:20px;padding:1px 8px;font-size:.58rem;font-weight:700;margin-left:6px">○ —</span>'

def section_header(icon, title, color, ok):
    return f"""<div style="display:flex;align-items:center;gap:7px;margin-bottom:8px;padding-bottom:7px;border-bottom:2px solid {color}22">
        <div style="width:26px;height:26px;border-radius:7px;background:{color}18;display:flex;align-items:center;justify-content:center;font-size:.8rem;flex-shrink:0">{icon}</div>
        <span style="font-size:.88rem;font-weight:800;color:#1a1a2e">{title}</span>
        {badge_html(ok)}
    </div>"""

def kpi_html(items):
    parts = "".join(f"""
    <div style="flex:1;background:#f8f9fa;border-radius:8px;padding:7px 6px;text-align:center;min-width:0">
        <div style="font-size:1rem;font-weight:900;color:{c};line-height:1;overflow:hidden;text-overflow:ellipsis;white-space:nowrap">{v}</div>
        <div style="font-size:.48rem;color:#bbb;text-transform:uppercase;letter-spacing:.05em;margin-top:2px;white-space:nowrap">{l}</div>
    </div>""" for v, l, c in items)
    return f'<div style="display:flex;gap:4px;margin-bottom:10px">{parts}</div>'

# ─── HERO (компактний) ────────────────────────────────────────────────────────
import streamlit.components.v1 as components
components.html("""
<!DOCTYPE html><html><head><meta charset="utf-8">
<link href="https://fonts.googleapis.com/css2?family=Manrope:wght@700;800;900&display=swap" rel="stylesheet">
<style>
*{box-sizing:border-box;margin:0;padding:0}body{font-family:'Manrope',sans-serif;overflow:hidden}
.h{position:relative;overflow:hidden;padding:14px 22px 12px;
   background:linear-gradient(135deg,#0f2027 0%,#203a43 50%,#2c5364 100%);border-radius:10px}
.grid{position:absolute;inset:0;pointer-events:none;
  background-image:linear-gradient(rgba(255,255,255,.04) 1px,transparent 1px),
                   linear-gradient(90deg,rgba(255,255,255,.04) 1px,transparent 1px);
  background-size:36px 36px;
  mask-image:radial-gradient(ellipse 80% 80% at 70% 0%,black,transparent);
  -webkit-mask-image:radial-gradient(ellipse 80% 80% at 70% 0%,black,transparent)}
.glow{position:absolute;top:-60px;right:-60px;width:350px;height:250px;
  background:radial-gradient(ellipse,rgba(0,210,255,.1) 0%,transparent 70%);pointer-events:none}
.title{font-size:1.15rem;font-weight:900;color:#fff;line-height:1.1;letter-spacing:-.02em}
.grad{background:linear-gradient(135deg,#00d2ff,#7ec8e3);-webkit-background-clip:text;
  -webkit-text-fill-color:transparent;background-clip:text}
.sub{font-size:.62rem;color:rgba(255,255,255,.4);margin-top:3px}
</style></head><body>
<div class="h"><div class="grid"></div><div class="glow"></div>
  <div class="title">🌍 ГІС Портал <span class="grad">v.001 </span></div>
  <div class="sub">Агрохімія · NDVI Зони · Лінії заїзду</div>
</div></body></html>
""", height=76, scrolling=False)

st.markdown("<div style='height:6px'></div>", unsafe_allow_html=True)

# ─── ТРИ КОЛОНКИ ─────────────────────────────────────────────────────────────
col1, col2, col3 = st.columns(3)

# ══════════════════════════════
# 🌿 АГРОХІМІЯ
# ══════════════════════════════
with col1:
    ok = agro is not None
    hdr = section_header("🌿", "Агрохімія", "#27ae60", ok)

    if not ok:
        st.markdown(f"""<div style="background:#fff;border:1px solid #e8eaed;border-radius:12px;
            padding:14px 16px;border-top:3px solid #27ae60">{hdr}
            <p style="color:#bbb;font-size:.8rem;margin-top:4px">Файл не знайдено</p></div>""",
            unsafe_allow_html=True)
    else:
        ha       = agro["Area_zone"].sum() if "Area_zone" in agro.columns else 0
        n_fields = agro["field_name"].nunique() if "field_name" in agro.columns else 0
        n_farms  = agro["Farm"].nunique()       if "Farm"       in agro.columns else 0
        kpi = kpi_html([
            (len(agro),    "Зон",    "#27ae60"),
            (n_fields,     "Полів",  "#27ae60"),
            (n_farms,      "Госп-в", "#27ae60"),
            (f"{ha:,.0f}", "га",     "#27ae60"),
        ])
        st.markdown(f"""<div style="background:#fff;border:1px solid #e8eaed;border-radius:12px;
            padding:14px 16px 4px;border-top:3px solid #27ae60">{hdr}{kpi}</div>""",
            unsafe_allow_html=True)

        if "field_name" in agro.columns:
            agg = {"Зон": ("field_name", "count")}
            if "Area_zone" in agro.columns: agg["га"] = ("Area_zone", "sum")
            df_f = agro.groupby("field_name").agg(**agg).reset_index().rename(columns={"field_name": "Поле"})
            if "га" in df_f.columns:
                df_f["га"] = df_f["га"].round(1)
                df_f = df_f.sort_values("га", ascending=False)
            else:
                df_f = df_f.sort_values("Зон", ascending=False)

            col_cfg = {"Зон": st.column_config.ProgressColumn("Зон", format="%d", min_value=0, max_value=int(df_f["Зон"].max()))}
            if "га" in df_f.columns: col_cfg["га"] = st.column_config.NumberColumn(format="%.1f")
            st.dataframe(df_f, use_container_width=True, hide_index=True,
                         height=min(36 + len(df_f) * 35, 380), column_config=col_cfg)

# ══════════════════════════════
# 🛰️ NDVI ЗОНИ
# ══════════════════════════════
with col2:
    ok = ndvi is not None
    hdr = section_header("🛰️", "NDVI Зони", "#1a7bff", ok)

    if not ok:
        st.markdown(f"""<div style="background:#fff;border:1px solid #e8eaed;border-radius:12px;
            padding:14px 16px;border-top:3px solid #1a7bff">{hdr}
            <p style="color:#bbb;font-size:.8rem;margin-top:4px">Файл не знайдено</p></div>""",
            unsafe_allow_html=True)
    else:
        n_poly  = len(ndvi)
        n_zones = ndvi["ZONE"].nunique() if "ZONE" in ndvi.columns else "—"
        n_avg   = round(ndvi["NDVI"].mean(), 3) if "NDVI" in ndvi.columns else "—"
        n_min   = round(ndvi["NDVI"].min(),  3) if "NDVI" in ndvi.columns else "—"
        n_max   = round(ndvi["NDVI"].max(),  3) if "NDVI" in ndvi.columns else "—"
        kpi = kpi_html([
            (n_poly,  "Полігонів", "#1a7bff"),
            (n_zones, "Зон",       "#1a7bff"),
            (n_avg,   "Середнє",   "#1a7bff"),
            (n_min,   "Мін",       "#e74c3c"),
            (n_max,   "Макс",      "#27ae60"),
        ])
        st.markdown(f"""<div style="background:#fff;border:1px solid #e8eaed;border-radius:12px;
            padding:14px 16px 4px;border-top:3px solid #1a7bff">{hdr}{kpi}</div>""",
            unsafe_allow_html=True)

        if "ZONE" in ndvi.columns and "NDVI" in ndvi.columns:
            zs = (ndvi.groupby("ZONE")["NDVI"]
                  .agg(count="count", mean="mean", min="min", max="max")
                  .reset_index()
                  .rename(columns={"ZONE":"Зона","count":"Пол-нів","mean":"Сер. NDVI","min":"Мін","max":"Макс"}))
            for c in ["Сер. NDVI","Мін","Макс"]: zs[c] = zs[c].round(3)
            st.dataframe(zs, use_container_width=True, hide_index=True,
                         height=min(36 + len(zs) * 35, 380),
                         column_config={"Сер. NDVI": st.column_config.ProgressColumn(
                             "Сер. NDVI", format="%.3f", min_value=0, max_value=1)})

# ══════════════════════════════
# 🚜 ЛІНІЇ ЗАЇЗДУ
# ══════════════════════════════
with col3:
    ok = lines is not None
    hdr = section_header("🚜", "Лінії заїзду", "#e67e22", ok)

    if not ok:
        st.markdown(f"""<div style="background:#fff;border:1px solid #e8eaed;border-radius:12px;
            padding:14px 16px;border-top:3px solid #e67e22">{hdr}
            <p style="color:#bbb;font-size:.8rem;margin-top:4px">Файл не знайдено</p></div>""",
            unsafe_allow_html=True)
    else:
        try:
            lon = lines.geometry.centroid.x.mean()
            utm = int(32600 + np.floor((lon + 180) / 6) + 1)
            total_km = lines.to_crs(epsg=utm).geometry.length.sum() / 1000
        except Exception:
            total_km, utm = 0, 32637

        n_f     = len(fields) if fields is not None else 0
        n_clust = fields["group"].nunique() if fields is not None and "group" in fields.columns else "—"

        n_covered, pct = 0, 0
        if fields is not None and n_f > 0:
            try:
                fp = fields.to_crs(epsg=utm)
                lp = lines.to_crs(epsg=utm)
                n_covered = sum(1 for _, f in fp.iterrows() if lp.geometry.intersects(f.geometry).any())
                pct = round(n_covered / n_f * 100)
            except Exception: pass

        cov_color = "#27ae60" if pct >= 80 else "#e67e22" if pct >= 50 else "#e74c3c"
        kpi = kpi_html([
            (len(lines),           "Ліній",     "#e67e22"),
            (f"{total_km:,.1f}",   "км",        "#e67e22"),
            (n_f,                  "Полів",      "#e67e22"),
            (n_clust,              "Кластерів", "#e67e22"),
            (f"{n_covered}/{n_f}", "З лініями", cov_color),
            (f"{pct}%",            "Покриття",  cov_color),
        ])
        st.markdown(f"""<div style="background:#fff;border:1px solid #e8eaed;border-radius:12px;
            padding:14px 16px 10px;border-top:3px solid #e67e22">{hdr}{kpi}</div>""",
            unsafe_allow_html=True)