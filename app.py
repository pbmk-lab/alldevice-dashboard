import streamlit as st
import requests

st.set_page_config(page_title="Alldevice dīkstāves", layout="wide")

st.title("Alldevice — iekārtu dīkstāves")

# --- SECRETS ---
BASE_URL = st.secrets["BASE_URL"]
USERNAME = st.secrets["USERNAME"]
PASSWORD = st.secrets["PASSWORD"]
API_KEY = st.secrets["API_KEY"]

# --- PAYLOAD ---
payload = {
    "auth": {
        "username": USERNAME,
        "password": PASSWORD,
        "key": API_KEY
    },
    "date_start": "2023-01-01",
    "date_end": "2026-12-31"
}

# --- API CALL ---
try:
    response = requests.post(BASE_URL, json=payload, timeout=10)
    data = response.json()
    st.success("API pieslēgums OK")
    st.write(data)

except Exception as e:
    st.error("Nav savienojuma ar API")
