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

response = requests.post(BASE_URL, json=payload)
data = response.json()

rows = data.get("response", [])

if not rows:
    st.warning("Nav datu")
    st.stop()

df = pd.DataFrame(rows)

# ---------- DATU APSTRĀDE ----------
df["start_date"] = pd.to_datetime(df["start_date"], errors="coerce")
df["end_date"] = pd.to_datetime(df["end_date"], errors="coerce")

df["device_name"] = df["device_name"].fillna("Nav norādīts")
df["cat_name"] = df["cat_name"].fillna("Nav norādīts")

# STATUSS
df["status"] = df["is_ended"].apply(
    lambda x: "Pabeigts" if x else "Atvērts"
)

# ---------- KPI ----------
open_tasks = len(df[df["status"] == "Atvērts"])
closed_tasks = len(df[df["status"] == "Pabeigts"])

k1, k2 = st.columns(2)

with k1:
    st.metric("Atvērtie uzdevumi", open_tasks)

with k2:
    st.metric("Pabeigtie uzdevumi", closed_tasks)

# ---------- GRAFIKS ----------
tasks_by_month = (
    df.groupby(df["start_date"].dt.to_period("M"))
    .size()
    .reset_index(name="count")
)

tasks_by_month["start_date"] = tasks_by_month["start_date"].astype(str)

fig = px.bar(
    tasks_by_month,
    x="start_date",
    y="count",
    title="Uzdevumi pa mēnešiem"
)

st.plotly_chart(fig, use_container_width=True)

# ---------- TOP IEKĀRTAS ----------
top_devices = (
    df.groupby("device_name")
    .size()
    .reset_index(name="count")
    .sort_values("count", ascending=False)
    .head(10)
)

fig2 = px.bar(
    top_devices,
    x="count",
    y="device_name",
    orientation="h",
    title="Top 10 iekārtas pēc uzdevumu skaita"
)

st.plotly_chart(fig2, use_container_width=True)

# ---------- TABULA ----------
st.dataframe(df[[
    "start_date",
    "device_name",
    "cat_name",
    "status",
    "comments"
]], use_container_width=True)
