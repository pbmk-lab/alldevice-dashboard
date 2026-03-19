import requests
import pandas as pd
import streamlit as st
import plotly.express as px
from ui import apply_style, page_header

st.set_page_config(page_title="Uzdevumi", layout="wide")

apply_style()
page_header(
    "Uzdevumi",
    "Servisa uzdevumu pārskats un analīze"
)

# ---------- SECRETS ----------
BASE_URL = st.secrets["BASE_URL"]
USERNAME = st.secrets["USERNAME"]
PASSWORD = st.secrets["PASSWORD"]
API_KEY = st.secrets["API_KEY"]

# No BASE_URL ar /api/downtimes/list izveidojam /api/tasks/list
TASKS_URL = BASE_URL.replace("/api/downtimes/list", "/api/tasks/list")

payload = {
    "auth": {
        "username": USERNAME,
        "password": PASSWORD,
        "key": API_KEY
    },
    "date_start": "2023-01-01",
    "date_end": "2026-12-31",
    "start": 0,
    "limit": 200
}

try:
    response = requests.post(TASKS_URL, json=payload, timeout=60)
    response.raise_for_status()
    data = response.json()
except requests.exceptions.Timeout:
    st.error("Savienojuma noildze ar Alldevice API (tasks/list).")
    st.stop()
except requests.exceptions.RequestException as e:
    st.error(f"API pieprasījuma kļūda: {e}")
    st.stop()
except ValueError:
    st.error("API atgrieza nekorektu JSON atbildi.")
    st.stop()

if not data.get("success"):
    st.error(f"API kļūda: {data}")
    st.stop()

response_data = data.get("response", {})
rows = response_data.get("data", [])

if not rows:
    st.warning("Nav atrastu uzdevumu datu")
    st.stop()

df = pd.DataFrame(rows)

# ---------- DATU APSTRĀDE ----------
if "service_date" in df.columns:
    df["service_date"] = pd.to_datetime(df["service_date"], errors="coerce")
else:
    df["service_date"] = pd.NaT

if "device_name" not in df.columns:
    df["device_name"] = "Nav norādīts"
else:
    df["device_name"] = df["device_name"].fillna("Nav norādīts")

if "service_name" not in df.columns:
    df["service_name"] = "Nav norādīts"
else:
    df["service_name"] = df["service_name"].fillna("Nav norādīts")

if "service_type" not in df.columns:
    df["service_type"] = "Nav norādīts"
else:
    df["service_type"] = df["service_type"].fillna("Nav norādīts")

if "is_completed" not in df.columns:
    df["is_completed"] = False

df["status"] = df["is_completed"].apply(lambda x: "Pabeigts" if x else "Atvērts")
df["month"] = df["service_date"].dt.to_period("M").astype(str)

# ---------- KPI ----------
open_tasks = int((df["status"] == "Atvērts").sum())
closed_tasks = int((df["status"] == "Pabeigts").sum())
total_tasks = len(df)

k1, k2, k3 = st.columns(3)
k1.metric("Atvērtie uzdevumi", open_tasks)
k2.metric("Pabeigtie uzdevumi", closed_tasks)
k3.metric("Kopējais uzdevumu skaits", total_tasks)

# ---------- GRAFIKS: UZDEVUMI PA MĒNEŠIEM ----------
tasks_by_month = (
    df.dropna(subset=["service_date"])
      .groupby("month", as_index=False)
      .size()
      .rename(columns={"size": "count"})
      .sort_values("month")
)

if not tasks_by_month.empty:
    fig = px.bar(
        tasks_by_month,
        x="month",
        y="count",
        title="Uzdevumi pa mēnešiem",
        labels={"month": "Mēnesis", "count": "Uzdevumu skaits"}
    )
    st.plotly_chart(fig, use_container_width=True)
else:
    st.info("Nav datu grafikam 'Uzdevumi pa mēnešiem'")

# ---------- TOP IEKĀRTAS ----------
top_devices = (
    df.groupby("device_name", as_index=False)
      .size()
      .rename(columns={"size": "count"})
      .sort_values("count", ascending=False)
      .head(10)
)

if not top_devices.empty:
    fig2 = px.bar(
        top_devices.sort_values("count", ascending=True),
        x="count",
        y="device_name",
        orientation="h",
        title="Top 10 iekārtas pēc uzdevumu skaita",
        labels={"count": "Uzdevumu skaits", "device_name": "Iekārta"}
    )
    st.plotly_chart(fig2, use_container_width=True)
else:
    st.info("Nav datu grafikam 'Top 10 iekārtas'")

# ---------- TABULA ----------
show_cols = [
    col for col in [
        "service_date",
        "device_name",
        "service_name",
        "service_type",
        "status",
        "task_status",
        "priority_name"
    ] if col in df.columns
]

st.dataframe(df[show_cols], use_container_width=True)
