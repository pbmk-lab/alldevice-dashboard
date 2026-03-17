import requests
import pandas as pd
import streamlit as st

st.set_page_config(page_title="Alldevice Downtimes", layout="wide")

st.title("Alldevice — простои оборудования")

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
    st.error(f"Ошибка API: {data}")
    st.stop()

rows = data.get("response", [])

if not rows:
    st.warning("Нет данных по простоям")
    st.stop()

df = pd.DataFrame(rows)

df["start_date"] = pd.to_datetime(df["start_date"], errors="coerce")
df["end_date"] = pd.to_datetime(df["end_date"], errors="coerce")
df["duration_hours"] = df["duration_seconds"] / 3600
df["month"] = df["start_date"].dt.to_period("M").astype(str)

st.subheader("Таблица простоев")
st.dataframe(df, use_container_width=True)

top_devices = (
    df.groupby("device_name", dropna=False)["duration_hours"]
    .sum()
    .sort_values(ascending=False)
    .reset_index()
)

st.subheader("Суммарный простой по устройствам, часы")
st.bar_chart(top_devices.set_index("device_name"))

top_categories = (
    df.groupby("cat_name", dropna=False)["duration_hours"]
    .sum()
    .sort_values(ascending=False)
    .reset_index()
)

st.subheader("Суммарный простой по категориям, часы")
st.bar_chart(top_categories.set_index("cat_name"))

by_month = (
    df.groupby("month", dropna=False)["duration_hours"]
    .sum()
    .sort_index()
    .reset_index()
)

st.subheader("Простой по месяцам, часы")
st.line_chart(by_month.set_index("month"))