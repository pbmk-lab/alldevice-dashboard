import streamlit as st
from ui import apply_style, page_header

st.set_page_config(page_title="Uzdevumi", layout="wide")

apply_style()
page_header(
    "Uzdevumi",
    "Servisa uzdevumu pārskats un analīze"
)

st.markdown('<div class="chart-card">', unsafe_allow_html=True)
st.write("Šeit būs uzdevumu datu panelis.")
st.markdown('</div>', unsafe_allow_html=True)
