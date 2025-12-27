import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots

# ---------------- PAGE CONFIG ----------------
st.set_page_config(
    page_title="QualSteam Analytics | Zydus",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ---------------- CONFIG ----------------
DATA_FILES = {
    "Scenario 1": "data/df_1_cleaned.csv",
    "Scenario 2": "data/df_2_cleaned.csv",
    "Scenario 3": "data/df_3_cleaned.csv",
    "Scenario 4": "data/df_4_cleaned.csv"
}

COLS = {
    "ts": "Timestamp",
    "temp_pv": "Process Temp",
    "temp_sp": "Process Temp SP",
    "flow": "Steam Flow Rate",
    "totalizer": "Steam Totalizer",
    "valve": "QualSteam Valve Opening",
    "p1": "Inlet Steam Pressure",
    "p2": "Outlet Steam Pressure",
    "p2_sp": "Pressure SP"
}

# ---------------- DATA LOADER ----------------
@st.cache_data
def load_data(path):
    df = pd.read_csv(path)
    df[COLS["ts"]] = pd.to_datetime(df[COLS["ts"]])
    df = df.sort_values(COLS["ts"])
    return df

# ---------------- STEAM CONSUMPTION ----------------
def calculate_steam_consumed(df):
    if COLS["totalizer"] in df.columns:
        return df[COLS["totalizer"]].iloc[-1] - df[COLS["totalizer"]].iloc[0]
    else:
        df["dt_hr"] = df[COLS["ts"]].diff().dt.total_seconds() / 3600
        df["steam_kg"] = df[COLS["flow"]] * df["dt_hr"]
        return df["steam_kg"].sum()

# ---------------- PLOT ----------------
def plot_dashboard(df, title):

    steam_consumed = calculate_steam_consumed(df)

    fig = make_subplots(
        rows=4, cols=1,
        shared_xaxes=True,
        vertical_spacing=0.12,
        subplot_titles=[
            "Temperature Control",
            "Pressure Dynamics",
            "Steam Flow Rate",
            "Control Valve Output"
        ]
    )

    # ---- TEMP ----
    fig.add_trace(go.Scatter(
        x=df[COLS["ts"]],
        y=df[COLS["temp_sp"]],
        name="Temp SP",
        line=dict(color="black", dash="dot")
    ), row=1, col=1)

    fig.add_trace(go.Scatter(
        x=df[COLS["ts"]],
        y=df[COLS["temp_pv"]],
        name="Temp PV",
        line=dict(color="#D32F2F")
    ), row=1, col=1)

    # ---- PRESSURE ----
    fig.add_trace(go.Scatter(
        x=df[COLS["ts"]],
        y=df[COLS["p2"]],
        name="Outlet P2",
        fill="tozeroy",
        line=dict(color="#1A237E")
    ), row=2, col=1)

    if COLS["p2_sp"] in df.columns:
        fig.add_trace(go.Scatter(
            x=df[COLS["ts"]],
            y=df[COLS["p2_sp"]],
            name="Pressure SP",
            line=dict(color="black", dash="dot")
        ), row=2, col=1)

    # ---- STEAM FLOW ----
    fig.add_trace(go.Scatter(
        x=df[COLS["ts"]],
        y=df[COLS["flow"]],
        name=f"Steam Flow (Consumed: {steam_consumed:.1f} kg)",
        fill="tozeroy",
        line=dict(color="#7B1FA2")
    ), row=3, col=1)

    # ---- VALVE ----
    fig.add_trace(go.Scatter(
        x=df[COLS["ts"]],
        y=df[COLS["valve"]],
        name="Valve %",
        fill="tozeroy",
        line=dict(color="#B8860B")
    ), row=4, col=1)

    # ---- LAYOUT FIXES ----
    fig.update_layout(
        height=1300,
        title=dict(text=title, font=dict(size=22, color="black")),
        paper_bgcolor="white",
        plot_bgcolor="white",
        hovermode="x unified",
        margin=dict(t=100, b=60),
        legend=dict(
            orientation="h",
            y=1.05,
            font=dict(color="black")
        ),
        font=dict(color="black")
    )

    fig.update_xaxes(
        showgrid=True,
        gridcolor="#E0E0E0",
        tickfont=dict(color="black"),
        title_font=dict(color="black")
    )

    fig.update_yaxes(
        showgrid=True,
        gridcolor="#E0E0E0",
        tickfont=dict(color="black"),
        title_font=dict(color="black")
    )

    fig.update_yaxes(title_text="Temp (°C)", row=1, col=1)
    fig.update_yaxes(title_text="Pressure (bar)", row=2, col=1)
    fig.update_yaxes(title_text="Steam Flow (kg/hr)", row=3, col=1)
    fig.update_yaxes(title_text="Valve (%)", row=4, col=1, range=[0, 105])

    return fig, steam_consumed

# ---------------- APP ----------------
st.sidebar.title("QualSteam Analytics")
scenario = st.sidebar.radio("Select Scenario", list(DATA_FILES.keys()))

df = load_data(DATA_FILES[scenario])
fig, steam_kg = plot_dashboard(df, f"Forensic Analysis – {scenario}")

st.title("QualSteam Forensic Dashboard")
st.metric("Total Steam Consumed", f"{steam_kg:.1f} kg")
st.plotly_chart(fig, use_container_width=True)

