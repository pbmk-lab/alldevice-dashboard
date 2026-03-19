import requests
import pandas as pd
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go

st.set_page_config(page_title="Alldevice dīkstāves", layout="wide")

# ---------- KRĀSAS ----------
CUSTOM_BG = "#0E1117"
CARD_BG = "#151A22"
SIDEBAR_BG = "#11161F"
TEXT_COLOR = "#F3F6FA"
BORDER_COLOR = "rgba(255,255,255,0.08)"

ANALYSIS_MAX_HOURS = 240

# ---------- CSS ----------
st.markdown(f"""
<style>
.stApp {{
    background-color: {CUSTOM_BG};
    color: {TEXT_COLOR};
}}

[data-testid="stSidebar"] {{
    background: {SIDEBAR_BG};
}}

[data-testid="stSidebar"] * {{
    color: {TEXT_COLOR} !important;
}}

/* FIX DATE INPUT */
[data-testid="stSidebar"] input {{
    background-color: #1A2330 !important;
    color: #F3F6FA !important;
    -webkit-text-fill-color: #F3F6FA !important;
    border-radius: 6px !important;
}}

[data-testid="stSidebar"] svg {{
    fill: #F3F6FA !important;
}}

</style>
""", unsafe_allow_html=True)

# ---------- API ----------
BASE_URL = st.secrets["BASE_URL"]
USERNAME = st.secrets["USERNAME"]
PASSWORD = st.secrets["PASSWORD"]
API_KEY = st.secrets["API_KEY"]

payload = {
    "auth": {
        "username": USERNAME,
        "password": PASSWORD,
        "key": API_KEY
    },
    "date_start": "2023-01-01",
    "date_end": "2026-12-31"
}

@st.cache_data(ttl=300)
def load_data():
    r = requests.post(BASE_URL, json=payload, timeout=10)
    r.raise_for_status()
    return r.json()

data = load_data()

df = pd.DataFrame(data["response"])

df["start_date"] = pd.to_datetime(df["start_date"])
df["duration_hours"] = df["duration_seconds"] / 3600
df["month"] = df["start_date"].dt.to_period("M").astype(str)

df["cat_name"] = df["cat_name"].fillna("Nav norādīts")

# ---------- FILTRI ----------
st.sidebar.markdown("## Filtri")

lines = df["device_location"].unique()
selected_lines = st.sidebar.multiselect("Izvēlies līnijas", lines, default=lines)

date_range = st.sidebar.date_input(
    "Izvēlies periodu",
    value=(df["start_date"].min(), df["start_date"].max())
)

# ---------- NAV ----------
page = st.sidebar.radio(
    "Navigācija",
    ["📊 Analīze", "📈 Paplašināta analīze", "🛠 Debug"]
)

# ---------- FILTER ----------
df = df[
    (df["device_location"].isin(selected_lines)) &
    (df["start_date"] >= pd.to_datetime(date_range[0])) &
    (df["start_date"] <= pd.to_datetime(date_range[1]))
]

# ---------- ANOMĀLIJAS ----------
df["is_anomaly"] = df["duration_hours"] > ANALYSIS_MAX_HOURS
df_analysis = df[df["duration_hours"] <= ANALYSIS_MAX_HOURS]

# ---------- KPI ----------
mttr = df_analysis["duration_hours"].mean()
total = df_analysis["duration_hours"].sum()

# ---------- MAIN ----------
if page == "📊 Analīze":

    st.metric("MTTR", f"{mttr:.2f}")
    st.metric("Kopējā dīkstāve", f"{total:.0f}")

    fig = px.bar(
        df_analysis.groupby("device_location")["duration_hours"].sum().reset_index(),
        x="duration_hours",
        y="device_location",
        orientation="h"
    )
    st.plotly_chart(fig, use_container_width=True)

elif page == "📈 Paplašināta analīze":

    # TOP CĒLOŅI
    top_causes = (
        df_analysis.groupby("cat_name")["duration_hours"]
        .sum()
        .sort_values(ascending=False)
        .head(10)
        .reset_index()
    )

    fig = px.bar(
        top_causes,
        x="duration_hours",
        y="cat_name",
        orientation="h",
        color="duration_hours",
        color_continuous_scale="Reds"
    )

    st.plotly_chart(fig, use_container_width=True)

elif page == "🛠 Debug":

    st.write("Rows:", len(df))
    st.write("Anomalies:", df["is_anomaly"].sum())
    st.write(df.head())
