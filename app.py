import requests
import pandas as pd
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go

st.set_page_config(page_title="Alldevice dīkstāves", layout="wide")

# ---------- TĒMA / KRĀSAS ----------
PLOT_TEMPLATE = "plotly_dark"
CUSTOM_BG = "#0E1117"
CARD_BG = "#151A22"
GRID_COLOR = "rgba(255,255,255,0.08)"
BORDER_COLOR = "rgba(255,255,255,0.08)"
TEXT_COLOR = "#F3F6FA"
MUTED_TEXT = "#A9B4C2"
ACCENT_1 = "#00E5FF"
ACCENT_2 = "#FFB300"
ACCENT_SUCCESS = "#00E676"
ACCENT_WARNING = "#FFC107"
ACCENT_DANGER = "#FF5252"

def apply_common_layout(fig, height=420):
    fig.update_layout(
        template=PLOT_TEMPLATE,
        height=height,
        paper_bgcolor=CUSTOM_BG,
        plot_bgcolor=CARD_BG,
        margin=dict(l=20, r=20, t=30, b=20),
        font=dict(color=TEXT_COLOR),
        xaxis=dict(
            showgrid=True,
            gridcolor=GRID_COLOR,
            zeroline=False
        ),
        yaxis=dict(
            showgrid=True,
            gridcolor=GRID_COLOR,
            zeroline=False
        ),
        legend=dict(
            bgcolor="rgba(0,0,0,0)",
            font=dict(color=TEXT_COLOR)
        )
    )
    return fig

# ---------- CSS ----------
st.markdown(
    f"""
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

    .kpi-card {{
        background: linear-gradient(180deg, #171D26 0%, #121720 100%);
        border: 1px solid {BORDER_COLOR};
        border-radius: 18px;
        padding: 18px 18px 14px 18px;
        box-shadow: 0 8px 24px rgba(0,0,0,0.22);
        min-height: 110px;
    }}

    .kpi-label {{
        color: {MUTED_TEXT};
        font-size: 0.92rem;
        margin-bottom: 0.35rem;
    }}

    .kpi-value {{
        color: {TEXT_COLOR};
        font-size: 2rem;
        font-weight: 800;
        line-height: 1.1;
    }}

    .chart-card {{
        background: linear-gradient(180deg, #161C25 0%, #10151D 100%);
        border: 1px solid {BORDER_COLOR};
        border-radius: 18px;
        padding: 14px 14px 6px 14px;
        box-shadow: 0 8px 24px rgba(0,0,0,0.22);
        margin-bottom: 14px;
    }}

    .chart-title {{
        color: {TEXT_COLOR};
        font-size: 1.15rem;
        font-weight: 700;
        margin-bottom: 0.6rem;
    }}

    .insight-card {{
        background: linear-gradient(180deg, #161C25 0%, #10151D 100%);
        border: 1px solid {BORDER_COLOR};
        border-radius: 18px;
        padding: 16px 18px 10px 18px;
        box-shadow: 0 8px 24px rgba(0,0,0,0.22);
        margin-top: 6px;
        margin-bottom: 14px;
    }}

    .insight-title {{
        color: {TEXT_COLOR};
        font-size: 1.1rem;
        font-weight: 700;
        margin-bottom: 0.6rem;
    }}

    .insight-list {{
        color: {TEXT_COLOR};
        font-size: 0.98rem;
        line-height: 1.8;
    }}

    div[data-testid="stDataFrame"] {{
        border: 1px solid {BORDER_COLOR};
        border-radius: 16px;
        overflow: hidden;
    }}

    hr {{
        border: none;
        border-top: 1px solid {BORDER_COLOR};
        margin-top: 1rem;
        margin-bottom: 1rem;
    }}
    </style>
    """,
    unsafe_allow_html=True
)

# ---------- VIRSRAKSTS ----------
st.markdown('<div class="pro-title">Alldevice — iekārtu dīkstāves</div>', unsafe_allow_html=True)
st.markdown(
    '<div class="pro-subtitle">Vadības panelis: MTTR, MTBF, prioritātes, līniju un iekārtu dīkstāves analīze</div>',
    unsafe_allow_html=True
)

# ---------- SECRETS ----------
BASE_URL = st.secrets["BASE_URL"]
st.write(BASE_URL)
USERNAME = st.secrets["USERNAME"]
PASSWORD = st.secrets["PASSWORD"]
API_KEY = st.secrets["API_KEY"]

# ---------- API ----------
payload = {
    "auth": {
        "username": USERNAME,
        "password": PASSWORD,
        "key": API_KEY
    },
    "date_start": "2023-01-01",
    "date_end": "2026-12-31"
}

try:
    response = requests.post(BASE_URL, json=payload, timeout=60)
    response.raise_for_status()
    data = response.json()
except Exception as e:
    st.error(f"Neizdevās iegūt datus no API: {e}")
    st.stop()

if not data.get("success"):
    st.error(f"API kļūda: {data}")
    st.stop()

rows = data.get("response", [])
if not rows:
    st.warning("Nav atrasti dīkstāves dati")
    st.stop()

# ---------- DATI ----------
df = pd.DataFrame(rows)

df["start_date"] = pd.to_datetime(df.get("start_date"), errors="coerce")
df["end_date"] = pd.to_datetime(df.get("end_date"), errors="coerce")
df["duration_seconds"] = pd.to_numeric(df.get("duration_seconds"), errors="coerce").fillna(0)
df["duration_hours"] = df["duration_seconds"] / 3600
df["month"] = df["start_date"].dt.to_period("M").astype(str)

df["cat_name"] = df.get("cat_name", "").fillna("").replace("", "Nav norādīts")
df["device_name"] = df.get("device_name", "").fillna("Nav norādīts")
df["device_location"] = df.get("device_location", "").fillna("Nav norādīts")
df["comments"] = df.get("comments", "").fillna("")
df["is_ended"] = df.get("is_ended", False).fillna(False)

# ---------- LĪNIJU KARTE ----------
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

def extract_line(location: str) -> str:
    location = str(location).upper()
    for line_name, keywords in LINE_MAPPING.items():
        for keyword in keywords:
            if keyword.upper() in location:
                return line_name
    return "Cits"

df["line"] = df["device_location"].apply(extract_line)

# ---------- FILTRI ----------
st.sidebar.markdown("## Filtri")

lines = list(LINE_MAPPING.keys())
selected_lines = st.sidebar.multiselect(
    "Izvēlies līnijas",
    options=lines,
    default=lines
)

min_date = df["start_date"].min()
max_date = df["start_date"].max()

if pd.isna(min_date) or pd.isna(max_date):
    st.error("Datu kopā nav korektu datumu")
    st.stop()

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

if df_filtered.empty:
    st.warning("Izvēlētajiem filtriem nav datu")
    st.stop()

df_filtered["month"] = df_filtered["start_date"].dt.to_period("M").astype(str)

# ---------- TIPS: PLĀNOTS / AVĀRIJA ----------
def classify_type(cat_name: str) -> str:
    cat_upper = str(cat_name).upper()
    if "PLĀNOTS" in cat_upper:
        return "Plānots"
    return "Avārija"

df_filtered["type"] = df_filtered["cat_name"].apply(classify_type)

# ---------- KPI ----------
df_closed = df_filtered[
    (df_filtered["is_ended"] == True) &
    (df_filtered["duration_hours"] > 0) &
    (df_filtered["duration_hours"] < 24)
].copy()

mttr = df_closed["duration_hours"].mean() if not df_closed.empty else 0

df_failures = df_filtered.sort_values("start_date").copy()
if len(df_failures) > 1:
    df_failures["prev_start"] = df_failures["start_date"].shift(1)
    df_failures["mtbf_hours"] = (
        (df_failures["start_date"] - df_failures["prev_start"]).dt.total_seconds() / 3600
    )
    mtbf = df_failures["mtbf_hours"].dropna().mean()
else:
    df_failures["mtbf_hours"] = pd.NA
    mtbf = 0

total_downtime_hours = df_filtered["duration_hours"].sum()
total_events = len(df_filtered)

k1, k2, k3, k4 = st.columns(4)

with k1:
    st.markdown(
        f'<div class="kpi-card"><div class="kpi-label">MTTR (stundas)</div><div class="kpi-value">{mttr:.2f}</div></div>',
        unsafe_allow_html=True
    )
with k2:
    st.markdown(
        f'<div class="kpi-card"><div class="kpi-label">MTBF (stundas)</div><div class="kpi-value">{mtbf:.2f}</div></div>',
        unsafe_allow_html=True
    )
with k3:
    st.markdown(
        f'<div class="kpi-card"><div class="kpi-label">Kopējā dīkstāve</div><div class="kpi-value">{total_downtime_hours:.0f}</div></div>',
        unsafe_allow_html=True
    )
with k4:
    st.markdown(
        f'<div class="kpi-card"><div class="kpi-label">Dīkstāves gadījumi</div><div class="kpi-value">{total_events}</div></div>',
        unsafe_allow_html=True
    )

# ---------- ALERT ----------
if mttr > 10:
    st.error("⚠️ Augsts MTTR! Nepieciešama uzmanība — remonta laiks ir pārāk liels.")
elif mttr > 5:
    st.warning("⚠️ MTTR virs normas.")
else:
    st.success("✅ MTTR ir normas robežās.")

st.markdown("<hr>", unsafe_allow_html=True)

# ---------- AGREGĀCIJAS ----------
mttr_by_month = (
    df_closed.groupby("month", as_index=False)["duration_hours"]
    .mean()
    .sort_values("month")
)

mtbf_by_month = (
    df_failures.dropna(subset=["mtbf_hours"])
    .groupby("month", as_index=False)["mtbf_hours"]
    .mean()
    .sort_values("month")
)

downtime_by_line = (
    df_filtered.groupby("line", as_index=False)["duration_hours"]
    .sum()
    .sort_values("duration_hours", ascending=True)
)

downtime_by_device = (
    df_filtered.groupby("device_name", as_index=False)["duration_hours"]
    .sum()
    .sort_values("duration_hours", ascending=False)
    .head(10)
    .sort_values("duration_hours", ascending=True)
)

type_hours = (
    df_filtered.groupby("type", as_index=False)["duration_hours"]
    .sum()
    .sort_values("duration_hours", ascending=False)
)

# ---------- PRIORITĀTES LĪNIJĀM ----------
if not downtime_by_line.empty:
    downtime_by_line["priority"] = downtime_by_line["duration_hours"].apply(
        lambda x: "HIGH" if x > 500 else ("MEDIUM" if x > 100 else "LOW")
    )

# ---------- GRAFIKI ----------
fig_mttr = None
if not mttr_by_month.empty:
    fig_mttr = go.Figure()

    fig_mttr.add_trace(go.Scatter(
        x=mttr_by_month["month"],
        y=mttr_by_month["duration_hours"],
        mode="lines",
        line=dict(width=10, color="rgba(0,229,255,0.15)"),
        hoverinfo="skip",
        showlegend=False
    ))

    fig_mttr.add_trace(go.Scatter(
        x=mttr_by_month["month"],
        y=mttr_by_month["duration_hours"],
        mode="lines+markers",
        line=dict(width=3, color=ACCENT_1),
        marker=dict(size=7),
        fill="tozeroy",
        fillcolor="rgba(0,229,255,0.18)",
        name="MTTR"
    ))

    fig_mttr.update_layout(
        title="",
        yaxis_title="MTTR (stundas)",
        xaxis_title="Mēnesis"
    )
    apply_common_layout(fig_mttr, height=360)

fig_mtbf = None
if not mtbf_by_month.empty:
    fig_mtbf = go.Figure()

    fig_mtbf.add_trace(go.Scatter(
        x=mtbf_by_month["month"],
        y=mtbf_by_month["mtbf_hours"],
        mode="lines",
        line=dict(width=10, color="rgba(255,179,0,0.15)"),
        hoverinfo="skip",
        showlegend=False
    ))

    fig_mtbf.add_trace(go.Scatter(
        x=mtbf_by_month["month"],
        y=mtbf_by_month["mtbf_hours"],
        mode="lines+markers",
        line=dict(width=3, color=ACCENT_2),
        marker=dict(size=7),
        fill="tozeroy",
        fillcolor="rgba(255,179,0,0.18)",
        name="MTBF"
    ))

    fig_mtbf.update_layout(
        title="",
        yaxis_title="MTBF (stundas)",
        xaxis_title="Mēnesis"
    )
    apply_common_layout(fig_mtbf, height=360)

fig_lines = None
if not downtime_by_line.empty:
    fig_lines = px.bar(
        downtime_by_line,
        x="duration_hours",
        y="line",
        orientation="h",
        text="duration_hours",
        color="priority",
        color_discrete_map={
            "HIGH": ACCENT_DANGER,
            "MEDIUM": ACCENT_WARNING,
            "LOW": ACCENT_SUCCESS
        },
        labels={"duration_hours": "Stundas", "line": "Līnija", "priority": "Prioritāte"}
    )
    fig_lines.update_traces(
        texttemplate="%{text:.1f}",
        textposition="outside",
        marker_line_width=1.5
    )
    apply_common_layout(fig_lines, height=430)

fig_devices = None
if not downtime_by_device.empty:
    fig_devices = px.bar(
        downtime_by_device,
        x="duration_hours",
        y="device_name",
        orientation="h",
        text="duration_hours",
        color="duration_hours",
        color_continuous_scale="Tealgrn",
        labels={"duration_hours": "Stundas", "device_name": "Iekārta"}
    )
    fig_devices.update_traces(
        texttemplate="%{text:.1f}",
        textposition="outside",
        marker_line_width=1.5
    )
    fig_devices.update_layout(coloraxis_showscale=False)
    apply_common_layout(fig_devices, height=520)

fig_cat = None
if not type_hours.empty:
    fig_cat = px.pie(
        type_hours,
        names="type",
        values="duration_hours",
        hole=0.60,
        color="type",
        color_discrete_map={
            "Plānots": ACCENT_SUCCESS,
            "Avārija": ACCENT_DANGER
        }
    )
    fig_cat.update_traces(
        textinfo="percent+label",
        marker=dict(line=dict(color="#000000", width=1))
    )
    apply_common_layout(fig_cat, height=430)

# ---------- IZKĀRTOJUMS ----------
r1c1, r1c2 = st.columns(2)

with r1c1:
    st.markdown('<div class="chart-card"><div class="chart-title">MTTR pa mēnešiem</div>', unsafe_allow_html=True)
    if fig_mttr is not None:
        st.plotly_chart(fig_mttr, use_container_width=True)
    else:
        st.info("Izvēlētajā periodā nav datu MTTR aprēķinam")
    st.markdown("</div>", unsafe_allow_html=True)

with r1c2:
    st.markdown('<div class="chart-card"><div class="chart-title">MTBF pa mēnešiem</div>', unsafe_allow_html=True)
    if fig_mtbf is not None:
        st.plotly_chart(fig_mtbf, use_container_width=True)
    else:
        st.info("Izvēlētajā periodā nav datu MTBF aprēķinam")
    st.markdown("</div>", unsafe_allow_html=True)

r2c1, r2c2 = st.columns(2)

with r2c1:
    st.markdown('<div class="chart-card"><div class="chart-title">Dīkstāve pa līnijām</div>', unsafe_allow_html=True)
    if fig_lines is not None:
        st.plotly_chart(fig_lines, use_container_width=True)
    else:
        st.info("Nav datu izvēlētajiem filtriem")
    st.markdown("</div>", unsafe_allow_html=True)

with r2c2:
    st.markdown('<div class="chart-card"><div class="chart-title">Dīkstāves sadalījums: plānots / avārija</div>', unsafe_allow_html=True)
    if fig_cat is not None:
        st.plotly_chart(fig_cat, use_container_width=True)
    else:
        st.info("Nav datu kategoriju grafikam")
    st.markdown("</div>", unsafe_allow_html=True)

st.markdown('<div class="chart-card"><div class="chart-title">Top 10 iekārtas pēc dīkstāves</div>', unsafe_allow_html=True)
if fig_devices is not None:
    st.plotly_chart(fig_devices, use_container_width=True)
else:
    st.info("Nav datu izvēlētajiem filtriem")
st.markdown("</div>", unsafe_allow_html=True)

# ---------- AUTOMĀTISKIE SECINĀJUMI ----------
top_line = "-"
top_device = "-"

if not downtime_by_line.empty:
    top_line = downtime_by_line.sort_values("duration_hours", ascending=False).iloc[0]["line"]

if not downtime_by_device.empty:
    top_device = downtime_by_device.sort_values("duration_hours", ascending=False).iloc[0]["device_name"]

st.markdown('<div class="insight-card"><div class="insight-title">Automātiskie secinājumi</div>', unsafe_allow_html=True)
st.markdown(
    f"""
    <div class="insight-list">
    🔴 Kritiskākā līnija: <b>{top_line}</b><br>
    ⚙️ Problemātiskākā iekārta: <b>{top_device}</b><br>
    ⏱️ Vidējais MTTR: <b>{mttr:.2f} h</b><br>
    🔁 Vidējais MTBF: <b>{mtbf:.2f} h</b><br>
    📉 Kopējā dīkstāve filtrētajā periodā: <b>{total_downtime_hours:.1f} h</b>
    </div>
    """,
    unsafe_allow_html=True
)
st.markdown("</div>", unsafe_allow_html=True)

# ---------- TABULA ----------
st.markdown('<div class="chart-card"><div class="chart-title">Dīkstāves dati</div>', unsafe_allow_html=True)

show_columns = [
    "id",
    "start_date",
    "end_date",
    "device_name",
    "line",
    "device_location",
    "cat_name",
    "type",
    "comments",
    "duration_hours",
    "is_ended"
]

existing_columns = [col for col in show_columns if col in df_filtered.columns]
st.dataframe(df_filtered[existing_columns], use_container_width=True)

st.markdown("</div>", unsafe_allow_html=True)
