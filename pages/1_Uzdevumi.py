import streamlit as st
from ui import apply_style, page_header

st.set_page_config(page_title="Uzdevumi", layout="wide")

apply_style()

page_header(
    "Uzdevumi",
    "Servisa uzdevumu pārskats"
)

st.write("✅ Lapa darbojas")
