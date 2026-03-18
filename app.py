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
    "date_start": "2025-01-01",
    "date_end": "2026-03-17"
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
df["duration_hours"] = df["duration_seconds"].fillna(0) / 3600
df["month"] = df["start_date"].dt.to_period("M").astype(str)

# --- LĪNIJU NOTEIKŠANA ---
location_parts = df["device_location"].fillna("").str.split(" / ")

def extract_line(parts):
    for part in parts:
        part = part.strip()
        if (
            "LĪNIJA" in part
            or "STARLINGER" in part
            or "VABEC" in part
            or "WET" in part
            or "ST R3/R4" in part
        ):
            return part
    return "Cits"

df["line"] = location_parts.apply(extract_line)

# --- FILTRI ---
st.sidebar.header("Filtri")

lines = sorted(df["line"].dropna().unique())
selected_lines = st.sidebar.multiselect(
    "Izvēlies līnijas",
    options=lines,
    default=lines
)

date_range = st.sidebar.date_input(
    "Izvēlies periodu",
    [df["start_date"].min(), df["start_date"].max()]
)

df_filtered = df[
    (df["line"].isin(selected_lines)) &
    (df["start_date"] >= pd.to_datetime(date_range[0])) &
    (df["start_date"] <= pd.to_datetime(date_range[1]))
]

# --- MTTR ---
df_closed = df_filtered[df_filtered["is_ended"] == True]

if len(df_closed) > 0:
    mttr = df_closed["duration_hours"].mean()
else:
    mttr = 0

st.metric("MTTR (vidējais remonta laiks, stundās)", round(mttr, 2))

# --- MTTR pa mēnešiem ---
mttr_by_month = (
    df_closed.groupby("month")["duration_hours"]
    .mean()
    .reset_index()
)

st.subheader("MTTR pa mēnešiem")
st.line_chart(mttr_by_month.set_index("month"))

# --- TOP līnijas pēc dīkstāves ---
top_lines = (
    df_filtered.groupby("line")["duration_hours"]
    .sum()
    .sort_values(ascending=False)
    .reset_index()
)

st.subheader("Dīkstāve pa līnijām (stundas)")
st.bar_chart(top_lines.set_index("line"))

# --- TABULA ---
st.subheader("Dīkstāves dati")
st.dataframe(df_filtered, use_container_width=True)