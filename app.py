import requests
import pandas as pd
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go

st.set_page_config(page_title="Alldevice dīkstāves", layout="wide", initial_sidebar_state="expanded")

# ---------- TĒMA / KRĀSAS (Premium Neon & Glassmorphism) ----------
CUSTOM_BG = "#04070b"  # Deep dark background
CARD_BG = "rgba(16, 22, 31, 0.65)" # Translucent glass
GRID_COLOR = "rgba(255,255,255,0.04)"
BORDER_COLOR = "rgba(255,255,255,0.08)"
TEXT_COLOR = "#F3F6FA"
MUTED_TEXT = "#94A3B8"
ACCENT_1 = "#00E5FF" # Неоновый голубой
ACCENT_2 = "#FFB300" # Золотой/Янтарный
ACCENT_SUCCESS = "#00E676"
ACCENT_WARNING = "#FFC107"
ACCENT_DANGER = "#FF4081" # Неоновый розово-красный

ANALYSIS_MAX_HOURS = 240

def apply_common_layout(fig, height=400):
    fig.update_layout(
        height=height,
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)",
        font=dict(color=TEXT_COLOR, family="'Outfit', sans-serif"),
        margin=dict(l=20, r=20, t=40, b=20),
        xaxis=dict(showgrid=True, gridcolor=GRID_COLOR, zeroline=False),
        yaxis=dict(showgrid=True, gridcolor=GRID_COLOR, zeroline=False),
        legend=dict(bgcolor="rgba(0,0,0,0)", font=dict(color=TEXT_COLOR)),
        hovermode="x unified"
    )
    # Умные ховеры (тёмный дизайн тултипов)
    fig.update_traces(
        hoverlabel=dict(
            bgcolor="rgba(10, 15, 22, 0.95)",
            font_size=13,
            font_family="'Outfit', sans-serif"
        )
    )
    return fig

# ---------- УЛЬТРА CSS ----------
st.markdown(
    f"""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;500;700;900&display=swap');

    /* Режим Full App: скрываем интерфейс Streamlit */
    #MainMenu {{visibility: hidden;}}
    footer {{visibility: hidden;}}
    header {{visibility: hidden;}}
    [data-testid="stHeader"] {{display: none;}}

    html, body, [class*="css"] {{
        font-family: 'Outfit', sans-serif !important;
    }}

    /* Радиальный фон-свечение для всего приложения */
    .stApp {{
        background-color: {CUSTOM_BG} !important;
        background-image: 
            radial-gradient(circle at 15% 50%, rgba(0, 229, 255, 0.08), transparent 40%),
            radial-gradient(circle at 85% 30%, rgba(255, 64, 129, 0.06), transparent 40%),
            radial-gradient(circle at 50% 100%, rgba(255, 179, 0, 0.05), transparent 50%) !important;
        background-attachment: fixed !important;
        color: {TEXT_COLOR};
    }}

    .block-container {{
        padding-top: 1.2rem;
        padding-bottom: 2rem;
        max-width: 1550px;
    }}

    /* Стеклянный сайдбар */
    [data-testid="stSidebar"] {{
        background: rgba(10, 15, 22, 0.7) !important;
        backdrop-filter: blur(20px);
        -webkit-backdrop-filter: blur(20px);
        border-right: 1px solid rgba(255,255,255,0.05);
    }}

    [data-testid="stSidebar"] * {{
        color: {TEXT_COLOR} !important;
    }}

    /* multiselect - ārējais lauks */
    [data-testid="stSidebar"] [data-baseweb="select"] > div {{
        background-color: rgba(26,35,48,0.6) !important;
        border: 1px solid rgba(255,255,255,0.1) !important;
        border-radius: 10px !important;
        backdrop-filter: blur(10px);
    }}

    /* multiselect - izvēlētie tagi */
    [data-testid="stSidebar"] .stMultiSelect div[data-baseweb="tag"] {{
        background-color: rgba(34,48,65,0.6) !important;
        border: 1px solid rgba(255,255,255,0.1) !important;
        color: {TEXT_COLOR} !important;
    }}

    /* dropdown saraksts */
    div[role="listbox"], div[role="option"] {{
        background-color: #1A2330 !important;
        color: #F3F6FA !important;
    }}

    div[role="option"]:hover {{
        background-color: #223041 !important;
        color: #F3F6FA !important;
    }}

    /* date input */
    [data-testid="stSidebar"] [data-testid="stDateInput"] input {{
        background-color: rgba(26,35,48,0.6) !important;
        color: #F3F6FA !important;
        border: 1px solid rgba(255,255,255,0.1) !important;
        border-radius: 8px !important;
        opacity: 1 !important;
        font-weight: 500 !important;
    }}

    /* radio */
    [data-testid="stSidebar"] [role="radiogroup"] {{
        background: transparent !important;
    }}

    /* Заголовки */
    .pro-title {{
        font-size: 2.8rem;
        font-weight: 900;
        background: linear-gradient(90deg, #FFFFFF 0%, #00E5FF 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 0.2rem;
        letter-spacing: -0.5px;
    }}

    .pro-subtitle {{
        color: {MUTED_TEXT};
        font-size: 1.05rem;
        font-weight: 300;
        margin-bottom: 1.8rem;
    }}

    /* Анимации появления */
    @keyframes fadeUp {{
        from {{ opacity: 0; transform: translateY(20px); }}
        to {{ opacity: 1; transform: translateY(0); }}
    }}

    /* Карточки: Glassmorphism */
    .kpi-card, .chart-card, .insight-card {{
        background: {CARD_BG};
        backdrop-filter: blur(16px);
        -webkit-backdrop-filter: blur(16px);
        border-top: 1px solid rgba(255,255,255,0.1);
        border-left: 1px solid rgba(255,255,255,0.05);
        border-bottom: 1px solid rgba(0,0,0,0.5);
        border-right: 1px solid rgba(0,0,0,0.5);
        border-radius: 20px;
        box-shadow: 0 15px 35px rgba(0,0,0,0.5);
        transition: all 0.4s cubic-bezier(0.175, 0.885, 0.32, 1.275);
        animation: fadeUp 0.6s ease-out forwards;
    }}

    .kpi-card {{ padding: 22px 20px 18px 20px; min-height: 120px; margin-bottom: 14px;}}
    .chart-card {{ padding: 18px; margin-bottom: 20px; }}
    .insight-card {{ padding: 20px; margin-bottom: 20px; }}

    /* Неоновый Hover эффект */
    .kpi-card:hover, .chart-card:hover, .insight-card:hover {{
        transform: translateY(-7px) scale(1.01);
        box-shadow: 0 20px 40px rgba(0,0,0,0.6), 
                   0 0 20px rgba(0, 229, 255, 0.15);
        border-top: 1px solid rgba(0, 229, 255, 0.3);
    }}

    .kpi-label {{
        color: {MUTED_TEXT};
        font-size: 0.9rem;
        font-weight: 500;
        margin-bottom: 0.5rem;
        text-transform: uppercase;
        letter-spacing: 1px;
    }}

    .kpi-value {{
        color: #fff;
        font-size: 2.6rem;
        font-weight: 900;
        line-height: 1;
        text-shadow: 0 0 20px rgba(255,255,255,0.2);
    }}

    .chart-title, .insight-title {{
        color: #fff;
        font-size: 1.25rem;
        font-weight: 700;
        margin-bottom: 1rem;
        display: flex;
        align-items: center;
    }}

    .chart-title::before, .insight-title::before {{
        content: "";
        display: inline-block;
        width: 4px;
        height: 18px;
        background: {ACCENT_1};
        margin-right: 10px;
        border-radius: 4px;
        box-shadow: 0 0 8px {ACCENT_1};
    }}

    .insight-list {{
        color: {TEXT_COLOR};
        font-size: 1.05rem;
        line-height: 1.9;
    }}

    /* Тени для SVG графиков (Neon Glow) */
    .js-plotly-plot .plotly .main-svg {{ filter: drop-shadow(0px 8px 12px rgba(0,0,0,0.6)); }}
    .js-plotly-plot .plotly .trace.bars path {{ filter: drop-shadow(2px 5px 6px rgba(0,0,0,0.4)); }}
    .js-plotly-plot .plotly .pie path {{ filter: drop-shadow(4px 10px 10px rgba(0,0,0,0.5)); }}

    div[data-testid="stDataFrame"] {{
        border: 1px solid rgba(255,255,255,0.08);
        border-radius: 12px;
        background: transparent;
    }}

    hr {{
        border: none;
        height: 1px;
        background: linear-gradient(90deg, transparent, rgba(255,255,255,0.1), transparent);
        margin: 1.5rem 0;
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
try:
    BASE_URL = st.secrets["BASE_URL"]
    TASKREPORTS_URL = st.secrets["TASKREPORTS_URL"]
    USERNAME = st.secrets["USERNAME"]
    PASSWORD = st.secrets["PASSWORD"]
    API_KEY = st.secrets["API_KEY"]
except KeyError:
    # Запасной вариант на случай тестов
    BASE_URL = ""
    TASKREPORTS_URL = ""
    USERNAME = ""
    PASSWORD = ""
    API_KEY = ""

payload = {
    "auth": {
        "username": USERNAME,
        "password": PASSWORD,
        "key": API_KEY
    },
    "date_start": "2023-01-01",
    "date_end": "2026-12-31"
}

taskreports_payload = {
    "auth": {
        "username": USERNAME,
        "password": PASSWORD,
        "key": API_KEY
    },
    "date_start": "2023-01-01",
    "date_end": "2026-12-31",
    "date_type": "completed_date"
}

# ---------- API ----------
@st.cache_data(ttl=300)
def load_data():
    response = requests.post(BASE_URL, json=payload, timeout=30)
    response.raise_for_status()
    return response.json()

@st.cache_data(ttl=300)
def load_taskreports():
    response = requests.post(TASKREPORTS_URL, json=taskreports_payload, timeout=30)
    response.raise_for_status()
    return response.json()

try:
    with st.spinner("Ielādē datus..."):
        if BASE_URL:
            data = load_data()
        else:
            data = {"success": False, "error": "Missing SECRETS"}
except requests.exceptions.Timeout:
    st.error("Savienojuma noildze ar Alldevice API.")
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

ordered_lines = list(LINE_MAPPING.keys()) + ["Cits"]

selected_lines = st.sidebar.multiselect(
    "Izvēlies līnijas",
    options=ordered_lines,
    default=ordered_lines,
    placeholder="Izvēlies līnijas"
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

# ---------- NAVIGĀCIJA ----------
st.sidebar.markdown("## Navigācija")

page = st.sidebar.radio(
    "Izvēlies sadaļu",
    [
        "📊 Dīkstāves analīze",
        "📈 Paplašināta analīze",
        "🧾 Task reports",
        "🛠 API debug"
    ]
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

if df_filtered.empty and page != "🧾 Task reports":
    st.warning("Izvēlētajiem filtriem nav datu")
    st.stop()

if not df_filtered.empty:
    df_filtered["month"] = df_filtered["start_date"].dt.to_period("M").astype(str)

# ---------- ANOMĀLIJU FILTRS ----------
if not df_filtered.empty:
    df_filtered["is_anomaly"] = df_filtered["duration_hours"] > ANALYSIS_MAX_HOURS

    df_analysis = df_filtered[
        (df_filtered["duration_hours"] >= 0) &
        (df_filtered["duration_hours"] <= ANALYSIS_MAX_HOURS)
    ].copy()

    excluded_anomalies = int(df_filtered["is_anomaly"].sum())
    excluded_anomaly_hours = float(df_filtered.loc[df_filtered["is_anomaly"], "duration_hours"].sum())
else:
    df_analysis = pd.DataFrame()
    excluded_anomalies = 0
    excluded_anomaly_hours = 0.0

if page != "🧾 Task reports" and df_analysis.empty:
    st.warning("Pēc anomāli lielo dīkstāves ierakstu izslēgšanas analīzei nav datu.")
    st.stop()

# ---------- TIPS ----------
def classify_type(cat_name: str) -> str:
    cat_upper = str(cat_name).upper()
    if "PLĀNOTS" in cat_upper:
        return "Plānots"
    return "Avārija"

if not df_analysis.empty:
    df_analysis["type"] = df_analysis["cat_name"].apply(classify_type)
if not df_filtered.empty:
    df_filtered["type"] = df_filtered["cat_name"].apply(classify_type)

# ---------- KPI ----------
if not df_analysis.empty:
    df_closed = df_analysis[
        (df_analysis["is_ended"] == True) &
        (df_analysis["duration_hours"] > 0) &
        (df_analysis["duration_hours"] < 24)
    ].copy()

    mttr = df_closed["duration_hours"].mean() if not df_closed.empty else 0

    df_failures = df_analysis.sort_values("start_date").copy()
    if len(df_failures) > 1:
        df_failures["prev_start"] = df_failures["start_date"].shift(1)
        df_failures["mtbf_hours"] = (
            (df_failures["start_date"] - df_failures["prev_start"]).dt.total_seconds() / 3600
        )
        mtbf = df_failures["mtbf_hours"].dropna().mean()
    else:
        df_failures["mtbf_hours"] = pd.NA
        mtbf = 0

    total_downtime_hours = df_analysis["duration_hours"].sum()
    total_events = len(df_analysis)
else:
    df_closed = pd.DataFrame()
    df_failures = pd.DataFrame()
    mttr = 0
    mtbf = 0
    total_downtime_hours = 0
    total_events = 0

# ---------- AGREGĀCIJAS ----------
if not df_analysis.empty:
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
        df_analysis.groupby("line", as_index=False)["duration_hours"]
        .sum()
        .sort_values("duration_hours", ascending=True)
    )

    downtime_by_device = (
        df_analysis.groupby("device_name", as_index=False)["duration_hours"]
        .sum()
        .sort_values("duration_hours", ascending=False)
        .head(10)
        .sort_values("duration_hours", ascending=True)
    )

    type_hours = (
        df_analysis.groupby("type", as_index=False)["duration_hours"]
        .sum()
        .sort_values("duration_hours", ascending=False)
    )

    events_by_month = (
        df_analysis.groupby("month", as_index=False)
        .size()
        .rename(columns={"size": "events"})
        .sort_values("month")
    )

    avg_downtime_by_line = (
        df_analysis.groupby("line", as_index=False)["duration_hours"]
        .mean()
        .sort_values("duration_hours", ascending=True)
    )

    downtime_by_category = (
        df_analysis.groupby("cat_name", as_index=False)["duration_hours"]
        .sum()
        .sort_values("duration_hours", ascending=False)
        .head(10)
        .sort_values("duration_hours", ascending=True)
    )

    if not downtime_by_line.empty:
        downtime_by_line["priority"] = downtime_by_line["duration_hours"].apply(
            lambda x: "HIGH" if x > 500 else ("MEDIUM" if x > 100 else "LOW")
        )
else:
    mttr_by_month = pd.DataFrame()
    mtbf_by_month = pd.DataFrame()
    downtime_by_line = pd.DataFrame()
    downtime_by_device = pd.DataFrame()
    type_hours = pd.DataFrame()
    events_by_month = pd.DataFrame()
    avg_downtime_by_line = pd.DataFrame()
    downtime_by_category = pd.DataFrame()

# ---------- GRAFIKI ----------
fig_mttr = None
if not mttr_by_month.empty:
    fig_mttr = go.Figure()
    fig_mttr.add_trace(go.Scatter(
        x=mttr_by_month["month"], y=mttr_by_month["duration_hours"],
        mode="lines", line=dict(width=10, color="rgba(0,229,255,0.15)"), hoverinfo="skip", showlegend=False
    ))
    fig_mttr.add_trace(go.Scatter(
        x=mttr_by_month["month"], y=mttr_by_month["duration_hours"],
        mode="lines+markers", line=dict(width=4, color=ACCENT_1),
        marker=dict(size=9, line=dict(width=2, color="#fff")),
        fill="tozeroy", fillcolor="rgba(0,229,255,0.25)", name="MTTR"
    ))
    fig_mttr.update_layout(title="", yaxis_title="MTTR (stundas)", xaxis_title="Mēnesis")
    apply_common_layout(fig_mttr, height=360)

fig_mtbf = None
if not mtbf_by_month.empty:
    fig_mtbf = go.Figure()
    fig_mtbf.add_trace(go.Scatter(
        x=mtbf_by_month["month"], y=mtbf_by_month["mtbf_hours"],
        mode="lines", line=dict(width=10, color="rgba(255,179,0,0.15)"), hoverinfo="skip", showlegend=False
    ))
    fig_mtbf.add_trace(go.Scatter(
        x=mtbf_by_month["month"], y=mtbf_by_month["mtbf_hours"],
        mode="lines+markers", line=dict(width=4, color=ACCENT_2),
        marker=dict(size=9, line=dict(width=2, color="#fff")),
        fill="tozeroy", fillcolor="rgba(255,179,0,0.25)", name="MTBF"
    ))
    fig_mtbf.update_layout(title="", yaxis_title="MTBF (stundas)", xaxis_title="Mēnesis")
    apply_common_layout(fig_mtbf, height=360)

fig_lines = None
if not downtime_by_line.empty:
    fig_lines = px.bar(
        downtime_by_line, x="duration_hours", y="line", orientation="h", text="duration_hours",
        color="priority", color_discrete_map={"HIGH": ACCENT_DANGER, "MEDIUM": ACCENT_WARNING, "LOW": ACCENT_SUCCESS},
        labels={"duration_hours": "Stundas", "line": "Līnija", "priority": "Prioritāte"}
    )
    fig_lines.update_traces(texttemplate="%{text:.1f}", textposition="outside", marker_line_width=0, opacity=0.9, marker=dict(cornerradius=4))
    apply_common_layout(fig_lines, height=430)

fig_devices = None
if not downtime_by_device.empty:
    fig_devices = px.bar(
        downtime_by_device, x="duration_hours", y="device_name", orientation="h",
        text="duration_hours", color="duration_hours", color_continuous_scale="Tealgrn",
        labels={"duration_hours": "Stundas", "device_name": "Iekārta"}
    )
    fig_devices.update_traces(texttemplate="%{text:.1f}", textposition="outside", marker_line_width=0, opacity=0.95, marker=dict(cornerradius=4))
    fig_devices.update_layout(coloraxis_showscale=False)
    apply_common_layout(fig_devices, height=520)

fig_cat = None
if not type_hours.empty:
    fig_cat = px.pie(
        type_hours, names="type", values="duration_hours", hole=0.65,
        color="type", color_discrete_map={"Plānots": ACCENT_SUCCESS, "Avārija": ACCENT_DANGER}
    )
    fig_cat.update_traces(textinfo="percent+label", textfont=dict(size=14, color="#fff"), marker=dict(line=dict(color="#04070B", width=4)))
    apply_common_layout(fig_cat, height=430)

fig_events = None
if not events_by_month.empty:
    fig_events = px.bar(
        events_by_month, x="month", y="events", text="events",
        labels={"month": "Mēnesis", "events": "Gadījumu skaits"}
    )
    fig_events.update_traces(textposition="outside", marker_color=ACCENT_1, marker_line_width=0, opacity=0.9, marker=dict(cornerradius=4))
    apply_common_layout(fig_events, height=380)

fig_avg_line = None
if not avg_downtime_by_line.empty:
    fig_avg_line = px.bar(
        avg_downtime_by_line, x="duration_hours", y="line", orientation="h",
        text="duration_hours", labels={"duration_hours": "Vidējās stundas", "line": "Līnija"}
    )
    fig_avg_line.update_traces(texttemplate="%{text:.2f}", textposition="outside", marker_color=ACCENT_2, marker_line_width=0, marker=dict(cornerradius=4))
    apply_common_layout(fig_avg_line, height=430)

fig_cat_top = None
if not downtime_by_category.empty:
    fig_cat_top = px.bar(
        downtime_by_category, x="duration_hours", y="cat_name", orientation="h",
        text="duration_hours", color="duration_hours", color_continuous_scale="Reds",
        labels={"duration_hours": "Stundas", "cat_name": "Cēlonis"}
    )
    fig_cat_top.update_traces(texttemplate="%{text:.1f}", textposition="outside", marker_line_width=0, opacity=0.9, marker=dict(cornerradius=4))
    fig_cat_top.update_layout(coloraxis_showscale=False)
    apply_common_layout(fig_cat_top, height=500)

# ---------- DATU KVALITĀTE ----------
missing_category = (df_analysis["cat_name"] == "Nav norādīts").sum() if not df_analysis.empty else 0
total_records = len(df_analysis)
missing_pct = (missing_category / total_records) * 100 if total_records > 0 else 0

# ---------- DATU KVALITĀTE PĒC LĪNIJĀM ----------
if not df_analysis.empty:
    quality_by_line = (
        df_analysis.assign(missing=df_analysis["cat_name"] == "Nav norādīts")
        .groupby("line")
        .agg(
            total=("cat_name", "count"),
            missing=("missing", "sum")
        )
        .reset_index()
    )
    quality_by_line["missing_pct"] = (quality_by_line["missing"] / quality_by_line["total"]) * 100
    quality_by_line = quality_by_line.sort_values("missing_pct", ascending=False)
else:
    quality_by_line = pd.DataFrame()

fig_quality = None
if not quality_by_line.empty:
    fig_quality = px.bar(
        quality_by_line.head(10), x="missing_pct", y="line", orientation="h",
        text="missing_pct", color="missing_pct", color_continuous_scale="Reds",
        labels={"missing_pct": "% bez cēloņa", "line": "Līnija"}
    )
    fig_quality.update_traces(texttemplate="%{text:.1f}%", textposition="outside", marker_line_width=0, opacity=0.9, marker=dict(cornerradius=4))
    fig_quality.update_layout(coloraxis_showscale=False)
    apply_common_layout(fig_quality, height=500)

# ---------- REKOMENDĀCIJAS ----------
recommendations = []
if not downtime_by_category.empty:
    for _, row in downtime_by_category.sort_values("duration_hours", ascending=False).head(5).iterrows():
        cause = str(row["cat_name"]).upper()
        if "STOP" in cause: recommendations.append(f"🔧 {row['cat_name']}: pārbaudīt sensorus un automātikas kļūdas")
        elif "NAV NORĀDĪTS" in cause: recommendations.append(f"⚠️ {row['cat_name']}: jāuzlabo datu ievade (tehniķiem jānorāda cēlonis)")
        elif "PLĀNOTS" in cause: recommendations.append(f"📅 {row['cat_name']}: optimizēt plānoto apkopju grafiku")
        else: recommendations.append(f"🛠 {row['cat_name']}: nepieciešama detalizēta analīze")

# ---------- AUTOMĀTISKIE SECINĀJUMI ----------
top_line = "-"
top_device = "-"
if not downtime_by_line.empty:
    top_line = downtime_by_line.sort_values("duration_hours", ascending=False).iloc[0]["line"]
if not downtime_by_device.empty:
    top_device = downtime_by_device.sort_values("duration_hours", ascending=False).iloc[0]["device_name"]

# ---------- LAPAS ----------
if page == "📊 Dīkstāves analīze":
    if excluded_anomalies > 0:
        st.info(f"Analītikā netiek iekļauti {excluded_anomalies} anomāli ieraksti (>{ANALYSIS_MAX_HOURS} h), kopā {excluded_anomaly_hours:.1f} h.")

    st.markdown('<div class="insight-card"><div class="insight-title">Datu kvalitāte</div>', unsafe_allow_html=True)
    if missing_pct > 30: st.error(f"⚠️ {missing_pct:.1f}% ierakstu bez cēloņa (kritiska problēma)")
    elif missing_pct > 10: st.warning(f"⚠️ {missing_pct:.1f}% ierakstu bez cēloņa")
    else: st.success(f"✅ Datu kvalitāte laba ({missing_pct:.1f}% bez cēloņa)")
    st.markdown("</div>", unsafe_allow_html=True)

    st.markdown('<div class="chart-card"><div class="chart-title">Datu kvalitāte pa līnijām</div>', unsafe_allow_html=True)
    if fig_quality is not None: st.plotly_chart(fig_quality, use_container_width=True)
    else: st.info("Nav datu kvalitātes analīzei")
    st.markdown("</div>", unsafe_allow_html=True)

    st.markdown('<div class="insight-card"><div class="insight-title">Ieteikumi darbībai</div>', unsafe_allow_html=True)
    if recommendations:
        for r in recommendations: st.markdown(f"- {r}")
    else: st.write("Nav pietiekamu datu rekomendācijām")
    st.markdown("</div>", unsafe_allow_html=True)

    k1, k2, k3, k4 = st.columns(4)
    with k1: st.markdown(f'<div class="kpi-card"><div class="kpi-label">MTTR (stundas)</div><div class="kpi-value">{mttr:.2f}</div></div>', unsafe_allow_html=True)
    with k2: st.markdown(f'<div class="kpi-card"><div class="kpi-label">MTBF (stundas)</div><div class="kpi-value">{mtbf:.2f}</div></div>', unsafe_allow_html=True)
    with k3: st.markdown(f'<div class="kpi-card"><div class="kpi-label">Kopējā dīkstāve</div><div class="kpi-value">{total_downtime_hours:.0f}</div></div>', unsafe_allow_html=True)
    with k4: st.markdown(f'<div class="kpi-card"><div class="kpi-label">Dīkstāves gadījumi</div><div class="kpi-value">{total_events}</div></div>', unsafe_allow_html=True)

    if mttr > 10: st.error("⚠️ Augsts MTTR! Nepieciešama uzmanība — remonta laiks ir pārāk liels.")
    elif mttr > 5: st.warning("⚠️ MTTR virs normas.")
    else: st.success("✅ MTTR ir normas robežās.")

    st.markdown("<hr>", unsafe_allow_html=True)

    r1c1, r1c2 = st.columns(2)
    with r1c1:
        st.markdown('<div class="chart-card"><div class="chart-title">MTTR pa mēnešiem</div>', unsafe_allow_html=True)
        if fig_mttr is not None: st.plotly_chart(fig_mttr, use_container_width=True)
        else: st.info("Izvēlētajā periodā nav datu MTTR aprēķinam")
        st.markdown("</div>", unsafe_allow_html=True)

    with r1c2:
        st.markdown('<div class="chart-card"><div class="chart-title">MTBF pa mēnešiem</div>', unsafe_allow_html=True)
        if fig_mtbf is not None: st.plotly_chart(fig_mtbf, use_container_width=True)
        else: st.info("Izvēlētajā periodā nav datu MTBF aprēķinam")
        st.markdown("</div>", unsafe_allow_html=True)

    r2c1, r2c2 = st.columns(2)
    with r2c1:
        st.markdown('<div class="chart-card"><div class="chart-title">Dīkstāve pa līnijām</div>', unsafe_allow_html=True)
        if fig_lines is not None: st.plotly_chart(fig_lines, use_container_width=True)
        else: st.info("Nav datu izvēlētajiem filtriem")
        st.markdown("</div>", unsafe_allow_html=True)

    with r2c2:
        st.markdown('<div class="chart-card"><div class="chart-title">Dīkstāves sadalījums: plānots / avārija</div>', unsafe_allow_html=True)
        if fig_cat is not None: st.plotly_chart(fig_cat, use_container_width=True)
        else: st.info("Nav datu kategoriju grafikam")
        st.markdown("</div>", unsafe_allow_html=True)

    st.markdown('<div class="chart-card"><div class="chart-title">Top 10 iekārtas pēc dīkstāves</div>', unsafe_allow_html=True)
    if fig_devices is not None: st.plotly_chart(fig_devices, use_container_width=True)
    else: st.info("Nav datu izvēlētajiem filtriem")
    st.markdown("</div>", unsafe_allow_html=True)

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

    st.markdown('<div class="chart-card"><div class="chart-title">Dīkstāves dati (ar anomāliju atzīmi)</div>', unsafe_allow_html=True)
    show_columns = ["id", "start_date", "end_date", "device_name", "line", "device_location", "cat_name", "type", "comments", "duration_hours", "is_ended", "is_anomaly"]
    existing_columns = [col for col in show_columns if col in df_filtered.columns]
    st.dataframe(df_filtered[existing_columns], use_container_width=True)
    st.markdown("</div>", unsafe_allow_html=True)

elif page == "📈 Paplašināta analīze":
    if excluded_anomalies > 0:
        st.info(f"Analītikā netiek iekļauti {excluded_anomalies} anomāli ieraksti (>{ANALYSIS_MAX_HOURS} h), kopā {excluded_anomaly_hours:.1f} h.")

    st.markdown('<div class="chart-card"><div class="chart-title">Paplašināta analīze</div>', unsafe_allow_html=True)
    st.markdown(f"Šajā sadaļā tiek izmantoti tikai ieraksti līdz <b>{ANALYSIS_MAX_HOURS} h</b>, lai anomāli lielas dīkstāves neizkropļotu rezultātus.", unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)

    c1, c2 = st.columns(2)
    with c1:
        st.markdown('<div class="chart-card"><div class="chart-title">Dīkstāves gadījumu skaits pa mēnešiem</div>', unsafe_allow_html=True)
        if fig_events is not None: st.plotly_chart(fig_events, use_container_width=True)
        else: st.info("Nav datu gadījumu skaita analīzei")
        st.markdown("</div>", unsafe_allow_html=True)

    with c2:
        st.markdown('<div class="chart-card"><div class="chart-title">Vidējā dīkstāve pa līnijām</div>', unsafe_allow_html=True)
        if fig_avg_line is not None: st.plotly_chart(fig_avg_line, use_container_width=True)
        else: st.info("Nav datu vidējās dīkstāves analīzei")
        st.markdown("</div>", unsafe_allow_html=True)

    st.markdown('<div class="chart-card"><div class="chart-title">Top dīkstāves cēloņi</div>', unsafe_allow_html=True)
    if fig_cat_top is not None: st.plotly_chart(fig_cat_top, use_container_width=True)
    else: st.info("Nav datu cēloņu analīzei")
    st.markdown("</div>", unsafe_allow_html=True)

    line_summary = df_analysis.groupby("line", as_index=False).agg(total_hours=("duration_hours", "sum"), avg_hours=("duration_hours", "mean"), events=("id", "count") if "id" in df_analysis.columns else ("duration_hours", "count")).sort_values("total_hours", ascending=False)
    st.markdown('<div class="chart-card"><div class="chart-title">Kopsavilkums pa līnijām</div>', unsafe_allow_html=True)
    st.dataframe(line_summary, use_container_width=True)
    st.markdown("</div>", unsafe_allow_html=True)

elif page == "🧾 Task reports":
    st.markdown('<div class="chart-card"><div class="chart-title">Task reports</div>', unsafe_allow_html=True)

    try:
        taskreports_data = load_taskreports()
    except Exception as e:
        st.error(f"Kļūda: {e}")
        st.markdown("</div>", unsafe_allow_html=True)
        st.stop()

    response_obj = taskreports_data.get("response", {})
    if not isinstance(response_obj, dict):
        st.error("Taskreports API response formāts nav gaidītais.")
        st.markdown("</div>", unsafe_allow_html=True)
        st.stop()

    taskreports_rows = response_obj.get("data", [])
    total_reports_api = response_obj.get("total", 0)

    if not taskreports_rows:
        st.info("Taskreports API strādā, bet šobrīd neatgrieza ierakstus.")
        st.markdown("</div>", unsafe_allow_html=True)
        st.stop()

    tr_df = pd.DataFrame(taskreports_rows)
    tr_df["total_time_seconds"] = pd.to_numeric(tr_df.get("total_time_seconds"), errors="coerce").fillna(0)
    tr_df["total_hours"] = tr_df["total_time_seconds"] / 3600
    tr_df["service_name"] = tr_df.get("service_name", "").fillna("Nav norādīts")
    tr_df["device_name"] = tr_df.get("device_name", "").fillna("Nav norādīts")
    tr_df["device_location"] = tr_df.get("device_location", "").fillna("Nav norādīts")
    tr_df["user_name_list"] = tr_df.get("user_name_list", "").fillna("Nav norādīts")
    tr_df["report_nr"] = tr_df.get("report_nr", "").fillna("Nav norādīts")
    tr_df["report_line"] = tr_df["device_location"].apply(extract_line)

    total_reports = len(tr_df)
    total_hours = tr_df["total_hours"].sum()
    avg_report_hours = tr_df["total_hours"].mean() if total_reports > 0 else 0

    k1, k2, k3, k4 = st.columns(4)
    with k1: st.markdown(f'<div class="kpi-card"><div class="kpi-label">Saņemtie reporti</div><div class="kpi-value">{total_reports}</div></div>', unsafe_allow_html=True)
    with k2: st.markdown(f'<div class="kpi-card"><div class="kpi-label">API reportu skaits</div><div class="kpi-value">{total_reports_api}</div></div>', unsafe_allow_html=True)
    with k3: st.markdown(f'<div class="kpi-card"><div class="kpi-label">Kopējās stundas</div><div class="kpi-value">{total_hours:.1f}</div></div>', unsafe_allow_html=True)
    with k4: st.markdown(f'<div class="kpi-card"><div class="kpi-label">Vidēji stundas/reportu</div><div class="kpi-value">{avg_report_hours:.2f}</div></div>', unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)

    tech_hours = tr_df.groupby("user_name_list", as_index=False)["total_hours"].sum().sort_values("total_hours", ascending=False).head(10).sort_values("total_hours", ascending=True)
    fig_tech = None
    if not tech_hours.empty:
        fig_tech = px.bar(tech_hours, x="total_hours", y="user_name_list", orientation="h", text="total_hours", color="total_hours", color_continuous_scale="Blues", labels={"total_hours": "Stundas", "user_name_list": "Tehniķis"})
        fig_tech.update_traces(texttemplate="%{text:.1f}", textposition="outside", marker_line_width=0, opacity=0.9, marker=dict(cornerradius=4))
        fig_tech.update_layout(coloraxis_showscale=False)
        apply_common_layout(fig_tech, height=500)

    service_hours = tr_df.groupby("service_name", as_index=False)["total_hours"].sum().sort_values("total_hours", ascending=False).head(10).sort_values("total_hours", ascending=True)
    fig_service = None
    if not service_hours.empty:
        fig_service = px.bar(service_hours, x="total_hours", y="service_name", orientation="h", text="total_hours", color="total_hours", color_continuous_scale="Tealgrn", labels={"total_hours": "Stundas", "service_name": "Darbs"})
        fig_service.update_traces(texttemplate="%{text:.1f}", textposition="outside", marker_line_width=0, opacity=0.9, marker=dict(cornerradius=4))
        fig_service.update_layout(coloraxis_showscale=False)
        apply_common_layout(fig_service, height=500)

    hours_by_line = tr_df.groupby("report_line", as_index=False)["total_hours"].sum().sort_values("total_hours", ascending=False).head(10).sort_values("total_hours", ascending=True)
    fig_line_hours = None
    if not hours_by_line.empty:
        fig_line_hours = px.bar(hours_by_line, x="total_hours", y="report_line", orientation="h", text="total_hours", color="total_hours", color_continuous_scale="Oranges", labels={"total_hours": "Stundas", "report_line": "Līnija"})
        fig_line_hours.update_traces(texttemplate="%{text:.1f}", textposition="outside", marker_line_width=0, opacity=0.9, marker=dict(cornerradius=4))
        fig_line_hours.update_layout(coloraxis_showscale=False)
        apply_common_layout(fig_line_hours, height=520)

    c1, c2 = st.columns(2)
    with c1:
        st.markdown('<div class="chart-card"><div class="chart-title">Top tehniķi pēc stundām</div>', unsafe_allow_html=True)
        if fig_tech is not None: st.plotly_chart(fig_tech, use_container_width=True)
        else: st.info("Nav datu tehniķu analīzei")
        st.markdown("</div>", unsafe_allow_html=True)

    with c2:
        st.markdown('<div class="chart-card"><div class="chart-title">Top darbi pēc stundām</div>', unsafe_allow_html=True)
        if fig_service is not None: st.plotly_chart(fig_service, use_container_width=True)
        else: st.info("Nav datu darbu analīzei")
        st.markdown("</div>", unsafe_allow_html=True)

    st.markdown('<div class="chart-card"><div class="chart-title">Darba stundas pa līnijām</div>', unsafe_allow_html=True)
    if fig_line_hours is not None: st.plotly_chart(fig_line_hours, use_container_width=True)
    else: st.info("Nav datu līniju analīzei")
    st.markdown("</div>", unsafe_allow_html=True)

    st.markdown('<div class="chart-card"><div class="chart-title">Task reports dati</div>', unsafe_allow_html=True)
    show_cols = ["report_id", "report_nr", "service_name", "device_name", "report_line", "device_location", "user_name_list", "total_time", "total_time_seconds", "total_hours"]
    existing_cols = [c for c in show_cols if c in tr_df.columns]
    st.dataframe(tr_df[existing_cols], use_container_width=True)
    st.markdown("</div>", unsafe_allow_html=True)

elif page == "🛠 API debug":
    st.markdown('<div class="chart-card"><div class="chart-title">API debug</div>', unsafe_allow_html=True)
    st.json({"ROWS_FROM_API": len(rows), "FILTERED_ROWS_RAW": len(df_filtered), "SUCCESS_FLAG": data.get("success")})
    st.markdown("</div>", unsafe_allow_html=True)
