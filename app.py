import requests
import pandas as pd
import streamlit as st
import plotly.express as px

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
df["cat_name"] = df["cat_name"].fillna("").replace("", "Nav norādīts")
df["device_name"] = df["device_name"].fillna("Nav norādīts")
df["device_location"] = df["device_location"].fillna("Nav norādīts")

LINE_MAPPING = {
    "01. 1 LĪNIJA": ["1 LĪNIJA"],
    "02. 2 LĪNIJA": ["2 LĪNIJA"],
    "03. 3 LĪNIJA RIPLAST": ["RIPLAST", "3 LĪNIJA"],
    "04. 4 LĪNIJA": ["4 LĪNIJA"],
    "05. SMALKUMU LĪNIJA SM1": ["SM1"],
    "06. SMALKUMU LĪNIJA SM2 (VIOLIA)": ["SM2", "VIOLIA"],
    "07. SMALKUMU LĪNIJA SM 3": ["SM 3", "SM3"],
    "08. SMALKUMU LĪNIJA (KORKU)": ["KORKU"],
    "09. TOMRA KORKU LĪNIJA": ["TOMRA KORKU", "TOMRA"],
    "10. WIPA": ["WIPA"],
    "11. ĶĪPU PRESE": ["PRESE", "ĶĪPU PRESE"],
    "12. KOMPRESORI": ["KOMPRESOR", "KOMPRESORI"],
    "13. STARLINGER NEW": ["STARLINGER NEW"],
    "14. STARLINGER OLD": ["STARLINGER OLD"],
    "15. Steiner Meyer": ["STEINER MEYER", "STEINER", "MEYER"],
    "16. NTomra": ["NTOMRA", "N TOMRA"],
    "17. LUMSU LĪNIJA": ["LUMSU LĪNIJA", "LUMSU"],
    "18. ATTĪRĪŠANAS IEKĀRTAS": ["ATTĪRĪŠANAS IEKĀRTAS"]
}

def extract_line(location):
    location = str(location).upper()
    for line_name, keywords in LINE_MAPPING.items():
        for keyword in keywords:
            if keyword.upper() in location:
                return line_name
    return "Cits"

df["line"] = df["device_location"].apply(extract_line)

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

df_closed = df_filtered[
    (df_filtered["is_ended"] == True) &
    (df_filtered["duration_hours"] > 0) &
    (df_filtered["duration_hours"] < 24)
].copy()

if len(df_closed) > 0:
    mttr = df_closed["duration_hours"].mean()
else:
    mttr = 0

total_downtime_hours = df_filtered["duration_hours"].sum()
total_events = len(df_filtered)
closed_events = len(df_closed)

c1, c2, c3 = st.columns(3)
c1.metric("MTTR (stundas)", round(mttr, 2))
c2.metric("Kopējā dīkstāve (stundas)", round(total_downtime_hours, 2))
c3.metric("Dīkstāves gadījumu skaits", total_events)

mttr_by_month = (
    df_closed.groupby("month", as_index=False)["duration_hours"]
    .mean()
    .sort_values("month")
)

st.subheader("MTTR pa mēnešiem")
if not mttr_by_month.empty:
    fig_mttr = px.line(
        mttr_by_month,
        x="month",
        y="duration_hours",
        markers=True,
        labels={"month": "Mēnesis", "duration_hours": "MTTR, stundas"},
        title=""
    )
    fig_mttr.update_layout(height=420)
    st.plotly_chart(fig_mttr, use_container_width=True)
else:
    st.info("Izvēlētajā periodā nav datu MTTR aprēķinam")

downtime_by_line = (
    df_filtered.groupby("line", as_index=False)["duration_hours"]
    .sum()
    .sort_values("duration_hours", ascending=True)
)

st.subheader("Dīkstāve pa līnijām")
if not downtime_by_line.empty:
    fig_lines = px.bar(
        downtime_by_line,
        x="duration_hours",
        y="line",
        orientation="h",
        text="duration_hours",
        labels={"duration_hours": "Stundas", "line": "Līnija"},
        title=""
    )
    fig_lines.update_traces(texttemplate="%{text:.2f}", textposition="outside")
    fig_lines.update_layout(height=650)
    st.plotly_chart(fig_lines, use_container_width=True)
else:
    st.info("Nav datu izvēlētajiem filtriem")

downtime_by_device = (
    df_filtered.groupby("device_name", as_index=False)["duration_hours"]
    .sum()
    .sort_values("duration_hours", ascending=False)
    .head(10)
    .sort_values("duration_hours", ascending=True)
)

st.subheader("Top 10 iekārtas pēc dīkstāves")
if not downtime_by_device.empty:
    fig_devices = px.bar(
        downtime_by_device,
        x="duration_hours",
        y="device_name",
        orientation="h",
        text="duration_hours",
        labels={"duration_hours": "Stundas", "device_name": "Iekārta"},
        title=""
    )
    fig_devices.update_traces(texttemplate="%{text:.2f}", textposition="outside")
    fig_devices.update_layout(height=520)
    st.plotly_chart(fig_devices, use_container_width=True)
else:
    st.info("Nav datu izvēlētajiem filtriem")

category_hours = (
    df_filtered.groupby("cat_name", as_index=False)["duration_hours"]
    .sum()
    .sort_values("duration_hours", ascending=False)
)

st.subheader("Dīkstāves sadalījums pa kategorijām")
if not category_hours.empty:
    fig_cat = px.pie(
        category_hours,
        names="cat_name",
        values="duration_hours",
        hole=0.45
    )
    fig_cat.update_layout(height=500)
    st.plotly_chart(fig_cat, use_container_width=True)
else:
    st.info("Nav datu kategoriju grafikam")

st.subheader("Dīkstāves dati")
show_columns = [
    "id",
    "start_date",
    "end_date",
    "device_name",
    "line",
    "device_location",
    "cat_name",
    "comments",
    "duration_hours",
    "is_ended"
]

existing_columns = [col for col in show_columns if col in df_filtered.columns]
st.dataframe(df_filtered[existing_columns], use_container_width=True)
