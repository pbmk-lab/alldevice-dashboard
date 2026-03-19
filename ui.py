import streamlit as st

def apply_style():

    CUSTOM_BG = "#0E1117"
    BORDER_COLOR = "rgba(255,255,255,0.08)"
    TEXT_COLOR = "#F3F6FA"
    MUTED_TEXT = "#A9B4C2"

    st.markdown(f"""
    <style>

    .stApp {{
        background-color: {CUSTOM_BG};
        color: {TEXT_COLOR};
    }}

    section[data-testid="stSidebar"] {{
        background-color: #11161D;
        border-right: 1px solid {BORDER_COLOR};
    }}

    .block-container {{
        padding-top: 1.2rem;
        padding-bottom: 2rem;
        max-width: 1500px;
    }}

    .pro-title {{
        font-size: 2.2rem;
        font-weight: 800;
        color: {TEXT_COLOR};
        margin-bottom: 0.2rem;
    }}

    .pro-subtitle {{
        color: {MUTED_TEXT};
        font-size: 0.95rem;
        margin-bottom: 1.2rem;
    }}

    .chart-card {{
        background: linear-gradient(180deg, #161C25 0%, #10151D 100%);
        border: 1px solid {BORDER_COLOR};
        border-radius: 18px;
        padding: 14px;
        margin-bottom: 14px;
    }}

    </style>
    """, unsafe_allow_html=True)


def page_header(title, subtitle):
    st.markdown(f'<div class="pro-title">{title}</div>', unsafe_allow_html=True)
    st.markdown(f'<div class="pro-subtitle">{subtitle}</div>', unsafe_allow_html=True)
