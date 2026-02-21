# app.py
import streamlit as st
from utils import apply_theme

st.set_page_config(layout="wide", page_title="AgroAnalytics Pro", page_icon="🌱")
is_dark = apply_theme()

st.markdown("<h1 style='text-align: center;'>🚜 AgroAnalytics Pro</h1>", unsafe_allow_html=True)
st.markdown("---")

st.markdown("""
### Вітаємо в системі просторового аналізу!
Використовуйте бічне меню для навігації між модулями:

* **🌿 Агрохімія** — перегляд результатів агрохімічного обстеження, картограми забезпеченості елементами живлення.
* **🗺️ NDVI Карти** — моніторинг вегетаційного індексу з накладанням векторних меж полів та растрових шарів.

*Оберіть потрібний розділ у лівій панелі (Sidebar), щоб розпочати.*
""")