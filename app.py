import requests
import pandas as pd
import streamlit as st

st.set_page_config(page_title="Alldevice dīkstāves", layout="wide")

st.title("Alldevice — iekārtu dīkstāves")

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

response = requests.post(BASE_URL, json=payload, timeout=60)
data = response.json()

if not data.get("success"):
    st.error(f"API kļūda: {data}")
    st.stop()

rows = data.get("response", [])

if not rows:
    st.warning("Nav atrasti dīkstāves dati")
    st.stop()

df = pd.DataFrame(rows)

df["start_date"] = pd.to_datetime(df["start_date"], errors="coerce")
df["end_date"] = pd.to_datetime(df["end_date"], errors="coerce")
df["duration_seconds"] = pd.to_numeric(df["duration_seconds"], errors="coerce").fillna(0)
df["duration_hours"] = df["duration_seconds"] / 3600
df["month"] = df["start_date"].dt.to_period("M").astype(str)

# --- FIKSĒTS LĪNIJU SARAKSTS ---
LINE_MAPPING = {
    "01. 1 LĪNIJA": ["1 LĪNIJA"],
    "02. 2 LĪNIJA": ["2 LĪNIJA"],
    "03. 3 LĪNIJA RIPLAST": ["RIPLAST"],
    "04. 4 LĪNIJA": ["4 LĪNIJA"],
    "05. SMALKUMU LĪNIJA SM1": ["SM1"],
    "06. SMALKUMU LĪNIJA SM2 (VIOLIA)": ["SM2", "VIOLIA"],
    "07. SMALKUMU LĪNIJA SM 3": ["SM 3", "SM3"],
    "08. SMALKUMU LĪNIJA (KORKU)": ["KORKU"],
    "09. TOMRA KORKU LĪNIJA": ["TOMRA"],
    "10. WIPA": ["WIPA"],
    "11. ĶĪPU PRESE": ["PRESE"],
    "12. KOMPRESORI": ["KOMPRESOR"]
}

def extract_line(location):
    location = str(location).upper()
    for line_name, keywords in LINE_MAPPING.items():
        for keyword in keywords:
            if keyword.upper() in location:
                return line_name
    return "Cits"

df["line"] = df["device_location"].apply(extract_line)

# --- FILTRI ---
st.sidebar.header("Filtri")

lines = list(LINE_MAPPING.keys())
selected_lines = st.sidebar.multiselect(
    "Izvēlies līnijas",
    options=lines,
    default=lines
)

min_date = df["start_date"].min()
max_date = df["start_date"].max()

date_range = st.sidebar.date_input(
    "Izvēlies periodu",
    value=(min_date.date(), max_date.date())
)

if isinstance(date_range, tuple) and len(date_range) == 2:
    start_filter = pd.to_datetime(date_range[0])
    end_filter = pd.to_datetime(date_range[1])
else:
    start_filter = min_date
    end_filter = max_date

df_filtered = df[
    (df["line"].isin(selected_lines)) &
    (df["start_date"] >= start_filter) &
    (df["start_date"] <= end_filter)
].copy()

# --- MTTR ---
df_closed = df_filtered[
    (df_filtered["is_ended"] == True) &
    (df_filtered["duration_hours"] > 0) &
    (df_filtered["duration_hours"] < 24)
].copy()

if len(df_closed) > 0:
    mttr = df_closed["duration_hours"].mean()
else:
    mttr = 0

st.metric("MTTR (vidējais remonta laiks, stundās)", round(mttr, 2))

# --- MTTR PA MĒNEŠIEM ---
mttr_by_month = (
    df_closed.groupby("month")["duration_hours"]
    .mean()
    .reset_index()
    .sort_values("month")
)

st.subheader("MTTR pa mēnešiem")
if not mttr_by_month.empty:
    st.line_chart(mttr_by_month.set_index("month"))
else:
    st.info("Izvēlētajā periodā nav datu MTTR aprēķinam")

# --- DĪKSTĀVE PA LĪNIJĀM ---
downtime_by_line = (
    df_filtered.groupby("line")["duration_hours"]
    .sum()
    .reset_index()
    .sort_values("duration_hours", ascending=False)
)

st.subheader("Dīkstāve pa līnijām (stundas)")
if not downtime_by_line.empty:
    st.bar_chart(downtime_by_line.set_index("line"))
else:
    st.info("Nav datu izvēlētajiem filtriem")

# --- TOP IEKĀRTAS PĒC DĪKSTĀVES ---
downtime_by_device = (
    df_filtered.groupby("device_name")["duration_hours"]
    .sum()
    .reset_index()
    .sort_values("duration_hours", ascending=False)
    .head(10)
)

st.subheader("Top 10 iekārtas pēc dīkstāves (stundas)")
if not downtime_by_device.empty:
    st.bar_chart(downtime_by_device.set_index("device_name"))
else:
    st.info("Nav datu izvēlētajiem filtriem")

# --- TABULA ---
st.subheader("Dīkstāves dati")
st.dataframe(df_filtered, use_container_width=True)
