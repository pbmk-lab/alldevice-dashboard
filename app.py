import requests
import pandas as pd
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go

st.set_page_config(page_title="Alldevice dīkstāves", layout="wide")

# ---------- TĒMA / KRĀSAS ----------
CUSTOM_BG = "#0b0f15"
CARD_BG = "#131a24"
SIDEBAR_BG = "#0d1117"
GRID_COLOR = "rgba(255,255,255,0.03)"
TEXT_COLOR = "#F3F6FA"
MUTED_TEXT = "#A9B4C2"
ACCENT_1 = "#00E5FF"
ACCENT_2 = "#FFB300"
ACCENT_SUCCESS = "#00E676"
ACCENT_WARNING = "#FFC107"
ACCENT_DANGER = "#FF5252"

# Maksimālā dīkstāve, ko iekļaujam analītikā
ANALYSIS_MAX_HOURS = 240

def apply_common_layout(fig, height=400):
    fig.update_layout(
        height=height,
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)",
        font=dict(color=TEXT_COLOR),
        margin=dict(l=20, r=20, t=40, b=20),
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

# ---------- CSS (Pseudo 3D / Neumorphism) ----------
st.markdown(
    f"""
    <style>
    .stApp {{
        background-color: {CUSTOM_BG};
        color: {TEXT_COLOR};
        /* Мягкий фоновый градиент */
        background: radial-gradient(circle at 50% 0%, #151e2b 0%, {CUSTOM_BG} 60%);
    }}

    .block-container {{
        padding-top: 1.2rem;
        padding-bottom: 2rem;
        max-width: 1500px;
    }}

    [data-testid="stSidebar"] {{
        background: {SIDEBAR_BG};
        border-right: 1px solid rgba(255,255,255,0.03);
        box-shadow: 5px 0 15px rgba(0,0,0,0.5);
    }}

    /* CSS Фильтры теней для парящего 3D эффекта самих графиков Plotly */
    .js-plotly-plot .plotly .main-svg {{
        filter: drop-shadow(0px 10px 15px rgba(0,0,0,0.8));
    }}
    
    .js-plotly-plot .plotly .trace.bars path {{
        filter: drop-shadow(3px 5px 5px rgba(0,0,0,0.6));
    }}
    
    .js-plotly-plot .plotly .trace.scatter path {{
        filter: drop-shadow(0px 8px 6px rgba(0,0,0,0.7));
    }}

    .js-plotly-plot .plotly .pie path {{
        filter: drop-shadow(4px 6px 8px rgba(0,0,0,0.6));
    }}

    .pro-title {{
        font-size: 2.4rem;
        font-weight: 900;
        color: #fff;
        margin-bottom: 0.2rem;
        text-shadow: 0px 4px 15px rgba(0, 229, 255, 0.4);
    }}

    .pro-subtitle {{
        color: {MUTED_TEXT};
        font-size: 1rem;
        margin-bottom: 1.5rem;
    }}

    /* Псевдо-3D Карточки */
    .kpi-card, .chart-card, .insight-card {{
        background: linear-gradient(145deg, #18212e 0%, #10151d 100%);
        border-top: 1px solid rgba(255,255,255,0.08);
        border-left: 1px solid rgba(255,255,255,0.05);
        border-bottom: 2px solid rgba(0,0,0,0.8);
        border-right: 2px solid rgba(0,0,0,0.8);
        border-radius: 20px;
        box-shadow: 12px 15px 25px rgba(0,0,0,0.5), 
                   -5px -5px 15px rgba(255,255,255,0.02);
        transition: transform 0.3s ease, box-shadow 0.3s ease;
    }}

    .kpi-card {{
        padding: 20px 20px 16px 20px;
        min-height: 110px;
    }}
    
    .chart-card {{
        padding: 16px 16px 10px 16px;
        margin-bottom: 18px;
    }}

    .insight-card {{
        padding: 18px 20px 12px 20px;
        margin-top: 8px;
        margin-bottom: 18px;
    }}

    .kpi-card:hover, .chart-card:hover, .insight-card:hover {{
        transform: translateY(-5px);
        box-shadow: 15px 20px 30px rgba(0,0,0,0.7), 
                   -6px -6px 20px rgba(255,255,255,0.03);
    }}

    .kpi-label {{
        color: {MUTED_TEXT};
        font-size: 0.95rem;
        margin-bottom: 0.4rem;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }}

    .kpi-value {{
        color: {TEXT_COLOR};
        font-size: 2.2rem;
        font-weight: 900;
        line-height: 1.1;
        text-shadow: 2px 4px 8px rgba(0,0,0,0.6);
    }}

    .chart-title, .insight-title {{
        color: #fff;
        font-size: 1.2rem;
        font-weight: 800;
        margin-bottom: 0.8rem;
        letter-spacing: 0.3px;
    }}

    .insight-list {{
        color: {TEXT_COLOR};
        font-size: 1.05rem;
        line-height: 1.9;
    }}

    div[data-testid="stDataFrame"] {{
        border: 1px solid rgba(255,255,255,0.05);
        border-radius: 16px;
        box-shadow: inset 0px 5px 15px rgba(0,0,0,0.5);
    }}

    hr {{
        border: none;
        border-top: 1px solid rgba(255,255,255,0.05);
        border-bottom: 1px solid rgba(0,0,0,0.8);
        margin-top: 1.5rem;
        margin-bottom: 1.5rem;
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
BASE_URL = st.secrets.get("BASE_URL", "http://example.com")
USERNAME = st.secrets.get("USERNAME", "user")
PASSWORD = st.secrets.get("PASSWORD", "pass")
API_KEY = st.secrets.get("API_KEY", "key")

payload = {
    "auth": {
        "username": USERNAME,
        "password": PASSWORD,
        "key": API_KEY
    },
    "date_start": "2023-01-01",
    "date_end": "2026-12-31"
}

# ---------- API ----------
@st.cache_data(ttl=300)
def load_data():
    try:
        response = requests.post(BASE_URL, json=payload, timeout=10)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        # Для демонстрации, если API лежит
        return {"success": False, "error": str(e)}

try:
    with st.spinner("Ielādē datus..."):
        data = load_data()
except Exception as e:
    st.error(f"Kļūda: {e}")
    st.stop()

if not data.get("success"):
    st.error(f"API nav pieejams, lūdzu pārbaudiet secrets.toml. Kļūda: {data}")
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

lines = sorted(df["line"].dropna().unique().tolist())
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

if df_filtered.empty:
    st.warning("Izvēlētajiem filtriem nav datu")
    st.stop()

df_filtered["month"] = df_filtered["start_date"].dt.to_period("M").astype(str)

# ---------- ANOMĀLIJU FILTRS ----------
df_filtered["is_anomaly"] = df_filtered["duration_hours"] > ANALYSIS_MAX_HOURS

df_analysis = df_filtered[
    (df_filtered["duration_hours"] >= 0) &
    (df_filtered["duration_hours"] <= ANALYSIS_MAX_HOURS)
].copy()

excluded_anomalies = int(df_filtered["is_anomaly"].sum())
excluded_anomaly_hours = float(df_filtered.loc[df_filtered["is_anomaly"], "duration_hours"].sum())

if df_analysis.empty:
    st.warning("Pēc anomāli lielo dīkstāves ierakstu izslēgšanas analīzei nav datu.")
    st.stop()

# ---------- TIPS ----------
def classify_type(cat_name: str) -> str:
    cat_upper = str(cat_name).upper()
    if "PLĀNOTS" in cat_upper:
        return "Plānots"
    return "Avārija"

df_analysis["type"] = df_analysis["cat_name"].apply(classify_type)
df_filtered["type"] = df_filtered["cat_name"].apply(classify_type)

# ---------- KPI ----------
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

# ---------- AGREGĀCIJAS ----------
mttr_by_month = df_closed.groupby("month", as_index=False)["duration_hours"].mean().sort_values("month")
mtbf_by_month = df_failures.dropna(subset=["mtbf_hours"]).groupby("month", as_index=False)["mtbf_hours"].mean().sort_values("month")
downtime_by_line = df_analysis.groupby("line", as_index=False)["duration_hours"].sum().sort_values("duration_hours", ascending=True)
downtime_by_device = df_analysis.groupby("device_name", as_index=False)["duration_hours"].sum().sort_values("duration_hours", ascending=False).head(10).sort_values("duration_hours", ascending=True)
type_hours = df_analysis.groupby("type", as_index=False)["duration_hours"].sum().sort_values("duration_hours", ascending=False)
events_by_month = df_analysis.groupby("month", as_index=False).size().rename(columns={"size": "events"}).sort_values("month")
avg_downtime_by_line = df_analysis.groupby("line", as_index=False)["duration_hours"].mean().sort_values("duration_hours", ascending=True)
downtime_by_category = df_analysis.groupby("cat_name", as_index=False)["duration_hours"].sum().sort_values("duration_hours", ascending=False).head(10).sort_values("duration_hours", ascending=True)

if not downtime_by_line.empty:
    downtime_by_line["priority"] = downtime_by_line["duration_hours"].apply(
        lambda x: "HIGH" if x > 500 else ("MEDIUM" if x > 100 else "LOW")
    )

# ---------- GRAFIKI ----------
fig_mttr = None
if not mttr_by_month.empty:
    fig_mttr = go.Figure()
    fig_mttr.add_trace(go.Scatter(
        x=mttr_by_month["month"], y=mttr_by_month["duration_hours"],
        mode="lines", line=dict(width=12, color="rgba(0,229,255,0.15)"), hoverinfo="skip", showlegend=False
    ))
    fig_mttr.add_trace(go.Scatter(
        x=mttr_by_month["month"], y=mttr_by_month["duration_hours"],
        mode="lines+markers", line=dict(width=4, color=ACCENT_1), 
        marker=dict(size=9, line=dict(width=2, color="#fff")),
        fill="tozeroy", fillcolor="rgba(0,229,255,0.25)", name="MTTR"
    ))
    fig_mttr.update_layout(title="", yaxis_title="MTTR (stundas)")
    apply_common_layout(fig_mttr, height=360)

fig_mtbf = None
if not mtbf_by_month.empty:
    fig_mtbf = go.Figure()
    fig_mtbf.add_trace(go.Scatter(
        x=mtbf_by_month["month"], y=mtbf_by_month["mtbf_hours"],
        mode="lines", line=dict(width=12, color="rgba(255,179,0,0.15)"), hoverinfo="skip", showlegend=False
    ))
    fig_mtbf.add_trace(go.Scatter(
        x=mtbf_by_month["month"], y=mtbf_by_month["mtbf_hours"],
        mode="lines+markers", line=dict(width=4, color=ACCENT_2),
        marker=dict(size=9, line=dict(width=2, color="#fff")),
        fill="tozeroy", fillcolor="rgba(255,179,0,0.25)", name="MTBF"
    ))
    fig_mtbf.update_layout(title="", yaxis_title="MTBF (stundas)")
    apply_common_layout(fig_mtbf, height=360)

fig_lines = None
if not downtime_by_line.empty:
    fig_lines = px.bar(
        downtime_by_line, x="duration_hours", y="line", orientation="h", text="duration_hours",
        color="priority", color_discrete_map={"HIGH": ACCENT_DANGER, "MEDIUM": ACCENT_WARNING, "LOW": ACCENT_SUCCESS}
    )
    # Скругление углов для эффекта современности
    fig_lines.update_traces(texttemplate="%{text:.1f}", textposition="outside", marker_line_width=0, opacity=0.9, marker=dict(cornerradius=4))
    apply_common_layout(fig_lines, height=430)

fig_devices = None
if not downtime_by_device.empty:
    fig_devices = px.bar(
        downtime_by_device, x="duration_hours", y="device_name", orientation="h",
        text="duration_hours", color="duration_hours", color_continuous_scale="Tealgrn"
    )
    fig_devices.update_traces(texttemplate="%{text:.1f}", textposition="outside", marker_line_width=0, opacity=0.95, marker=dict(cornerradius=4))
    fig_devices.update_layout(coloraxis_showscale=False)
    apply_common_layout(fig_devices, height=520)

fig_cat = None
if not type_hours.empty:
    fig_cat = px.pie(
        type_hours, names="type", values="duration_hours",
        hole=0.65, color="type", color_discrete_map={"Plānots": ACCENT_SUCCESS, "Avārija": ACCENT_DANGER}
    )
    # Добавляем белую границу между секторами
    fig_cat.update_traces(textinfo="percent+label", textfont=dict(size=14, color="#fff"), 
                          marker=dict(line=dict(color="#10151D", width=4)))
    apply_common_layout(fig_cat, height=430)

fig_events = None
if not events_by_month.empty:
    fig_events = px.bar(
        events_by_month, x="month", y="events", text="events"
    )
    fig_events.update_traces(textposition="outside", marker_color="#00E5FF", marker_line_width=0, opacity=0.85, marker=dict(cornerradius=4))
    apply_common_layout(fig_events, height=380)

fig_avg_line = None
if not avg_downtime_by_line.empty:
    fig_avg_line = px.bar(
        avg_downtime_by_line, x="duration_hours", y="line", orientation="h", text="duration_hours"
    )
    fig_avg_line.update_traces(texttemplate="%{text:.2f}", textposition="outside", marker_color="#FFB300", marker_line_width=0, marker=dict(cornerradius=4))
    apply_common_layout(fig_avg_line, height=430)

fig_cat_top = None
if not downtime_by_category.empty:
    fig_cat_top = px.bar(
        downtime_by_category, x="duration_hours", y="cat_name", orientation="h",
        text="duration_hours", color="duration_hours", color_continuous_scale="Reds"
    )
    fig_cat_top.update_traces(texttemplate="%{text:.1f}", textposition="outside", marker_line_width=0, opacity=0.9, marker=dict(cornerradius=4))
    fig_cat_top.update_layout(coloraxis_showscale=False)
    apply_common_layout(fig_cat_top, height=500)

# ---------- DATU KVALITĀTE ----------
missing_category = (df_analysis["cat_name"] == "Nav norādīts").sum()
total_records = len(df_analysis)
missing_pct = (missing_category / total_records) * 100 if total_records > 0 else 0

quality_by_line = df_analysis.assign(missing=df_analysis["cat_name"] == "Nav norādīts").groupby("line").agg(total=("cat_name", "count"), missing=("missing", "sum")).reset_index()
quality_by_line["missing_pct"] = (quality_by_line["missing"] / quality_by_line["total"]) * 100
quality_by_line = quality_by_line.sort_values("missing_pct", ascending=False)

fig_quality = None
if not quality_by_line.empty:
    fig_quality = px.bar(
        quality_by_line.head(10), x="missing_pct", y="line", orientation="h",
        text="missing_pct", color="missing_pct", color_continuous_scale="Reds"
    )
    fig_quality.update_traces(texttemplate="%{text:.1f}%", textposition="outside", marker_line_width=0, opacity=0.95, marker=dict(cornerradius=4))
    fig_quality.update_layout(coloraxis_showscale=False)
    apply_common_layout(fig_quality, height=500)

# ---------- SECINĀJUMI ----------
recommendations = []
for _, row in downtime_by_category.sort_values("duration_hours", ascending=False).head(5).iterrows():
    cause = str(row["cat_name"]).upper()
    if "STOP" in cause: recommendations.append(f"🔧 {row['cat_name']}: pārbaudīt sensorus un automātikas kļūdas")
    elif "NAV NORĀDĪTS" in cause: recommendations.append(f"⚠️ {row['cat_name']}: jāuzlabo datu ievade")
    elif "PLĀNOTS" in cause: recommendations.append(f"📅 {row['cat_name']}: optimizēt plānoto apkopju grafiku")
    else: recommendations.append(f"🛠 {row['cat_name']}: nepieciešama detalizēta analīze")

top_line = downtime_by_line.sort_values("duration_hours", ascending=False).iloc[0]["line"] if not downtime_by_line.empty else "-"
top_device = downtime_by_device.sort_values("duration_hours", ascending=False).iloc[0]["device_name"] if not downtime_by_device.empty else "-"

# ---------- LAPAS ----------
if page == "📊 Dīkstāves analīze":
    st.markdown('<div class="insight-card"><div class="insight-title">Datu kvalitāte</div>', unsafe_allow_html=True)
    if missing_pct > 30: st.error(f"⚠️ {missing_pct:.1f}% ierakstu bez cēloņa (kritiska problēma)")
    elif missing_pct > 10: st.warning(f"⚠️ {missing_pct:.1f}% ierakstu bez cēloņa")
    else: st.success(f"✅ Datu kvalitāte laba ({missing_pct:.1f}% bez cēloņa)")
    st.markdown("</div>", unsafe_allow_html=True)

    if recommendations:
        st.markdown('<div class="insight-card"><div class="insight-title">Ieteikumi darbībai</div>', unsafe_allow_html=True)
        for r in recommendations: st.markdown(f"- {r}")
        st.markdown("</div>", unsafe_allow_html=True)

    k1, k2, k3, k4 = st.columns(4)
    with k1: st.markdown(f'<div class="kpi-card"><div class="kpi-label">MTTR (stundas)</div><div class="kpi-value">{mttr:.2f}</div></div>', unsafe_allow_html=True)
    with k2: st.markdown(f'<div class="kpi-card"><div class="kpi-label">MTBF (stundas)</div><div class="kpi-value">{mtbf:.2f}</div></div>', unsafe_allow_html=True)
    with k3: st.markdown(f'<div class="kpi-card"><div class="kpi-label">Kopējā dīkstāve</div><div class="kpi-value">{total_downtime_hours:.0f}</div></div>', unsafe_allow_html=True)
    with k4: st.markdown(f'<div class="kpi-card"><div class="kpi-label">Dīkstāves gadījumi</div><div class="kpi-value">{total_events}</div></div>', unsafe_allow_html=True)

    st.markdown("<hr>", unsafe_allow_html=True)

    r1c1, r1c2 = st.columns(2)
    with r1c1:
        st.markdown('<div class="chart-card"><div class="chart-title">MTTR pa mēnešiem</div>', unsafe_allow_html=True)
        if fig_mttr: st.plotly_chart(fig_mttr, use_container_width=True)
        st.markdown("</div>", unsafe_allow_html=True)

    with r1c2:
        st.markdown('<div class="chart-card"><div class="chart-title">MTBF pa mēnešiem</div>', unsafe_allow_html=True)
        if fig_mtbf: st.plotly_chart(fig_mtbf, use_container_width=True)
        st.markdown("</div>", unsafe_allow_html=True)

    r2c1, r2c2 = st.columns(2)
    with r2c1:
        st.markdown('<div class="chart-card"><div class="chart-title">Dīkstāve pa līnijām</div>', unsafe_allow_html=True)
        if fig_lines: st.plotly_chart(fig_lines, use_container_width=True)
        st.markdown("</div>", unsafe_allow_html=True)

    with r2c2:
        st.markdown('<div class="chart-card"><div class="chart-title">Sadale: plānots / avārija</div>', unsafe_allow_html=True)
        if fig_cat: st.plotly_chart(fig_cat, use_container_width=True)
        st.markdown("</div>", unsafe_allow_html=True)

    st.markdown('<div class="chart-card"><div class="chart-title">Top 10 iekārtas pēc dīkstāves</div>', unsafe_allow_html=True)
    if fig_devices: st.plotly_chart(fig_devices, use_container_width=True)
    st.markdown("</div>", unsafe_allow_html=True)

    st.markdown('<div class="insight-card"><div class="insight-title">Automātiskie secinājumi</div>', unsafe_allow_html=True)
    st.markdown(f"""
        <div class="insight-list">
        🔴 Kritiskākā līnija: <b>{top_line}</b><br>
        ⚙️ Problemātiskākā iekārta: <b>{top_device}</b><br>
        ⏱️ Vidējais MTTR: <b>{mttr:.2f} h</b> | 🔁 MTBF: <b>{mtbf:.2f} h</b>
        </div>
        """, unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)

    st.markdown('<div class="chart-card"><div class="chart-title">Dati</div>', unsafe_allow_html=True)
    st.dataframe(df_filtered, use_container_width=True)
    st.markdown("</div>", unsafe_allow_html=True)

elif page == "📈 Paplašināta analīze":
    c1, c2 = st.columns(2)
    with c1:
        st.markdown('<div class="chart-card"><div class="chart-title">Gadījumu skaits</div>', unsafe_allow_html=True)
        if fig_events: st.plotly_chart(fig_events, use_container_width=True)
        st.markdown("</div>", unsafe_allow_html=True)

    with c2:
        st.markdown('<div class="chart-card"><div class="chart-title">Vidējā dīkstāve pa līnijām</div>', unsafe_allow_html=True)
        if fig_avg_line: st.plotly_chart(fig_avg_line, use_container_width=True)
        st.markdown("</div>", unsafe_allow_html=True)

    st.markdown('<div class="chart-card"><div class="chart-title">Datu kvalitāte pa līnijām</div>', unsafe_allow_html=True)
    if fig_quality: st.plotly_chart(fig_quality, use_container_width=True)
    st.markdown("</div>", unsafe_allow_html=True)

    st.markdown('<div class="chart-card"><div class="chart-title">Top dīkstāves cēloņi</div>', unsafe_allow_html=True)
    if fig_cat_top: st.plotly_chart(fig_cat_top, use_container_width=True)
    st.markdown("</div>", unsafe_allow_html=True)

elif page == "🛠 API debug":
    st.markdown('<div class="chart-card"><div class="chart-title">API debug info</div>', unsafe_allow_html=True)
    st.json({"ROWS": len(rows), "MAX_HOURS": ANALYSIS_MAX_HOURS})
    st.markdown("</div>", unsafe_allow_html=True)
