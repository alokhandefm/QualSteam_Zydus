import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots

# ---------------- PAGE CONFIG ----------------
st.set_page_config(
    page_title="QualSteam | Pressure Control Forensics",
    layout="wide"
)

# ---------------- FILES ----------------
DATA_FILES = {
    "Scenario 1": "data/df_1_cleaned.csv",
    "Scenario 2": "data/df_2_cleaned.csv",
    "Scenario 3": "data/df_3_cleaned.csv",
    "Scenario 4": "data/df_4_cleaned.csv"
}

# ---------------- COLUMNS ----------------
COLS = {
    "ts": "Timestamp",
    "p2": "Outlet Steam Pressure",
    "p2_sp": "Pressure SP"
}

# ---------------- PHASE WINDOWS ----------------
PHASES = {
    "Scenario 1": {
        "Ramp Up": ("00:18", "00:21"),
        "Stable": ("00:26", "01:03")
    },
    "Scenario 2": {
        "Ramp Up": ("06:50", "06:54"),
        "Stable": ("06:59", "07:44")
    },
    "Scenario 3": {
        "Ramp Up": ("05:13", "05:17"),
        "Stable": ("05:20", "06:08")
    },
    "Scenario 4": {
        "Ramp Up": ("11:31", "11:35"),
        "Stable": ("11:39", "12:25")
    }
}

# ---------------- LOAD DATA ----------------
@st.cache_data
def load_data(path):
    df = pd.read_csv(path)
    df[COLS["ts"]] = pd.to_datetime(df[COLS["ts"]])
    return df.sort_values(COLS["ts"])

# ---------------- FILTER PHASE ----------------
def filter_phase(df, start_time, end_time):
    date = df[COLS["ts"]].dt.date.iloc[0]
    start = pd.to_datetime(f"{date} {start_time}")
    end = pd.to_datetime(f"{date} {end_time}")
    return df[(df[COLS["ts"]] >= start) & (df[COLS["ts"]] <= end)]

# ---------------- PLOT ----------------
def plot_pressure(df_ramp, df_stable, scenario):

    fig = make_subplots(
        rows=2, cols=1,
        shared_xaxes=False,
        vertical_spacing=0.18,
        subplot_titles=[
            "Ramp-Up Phase: Pressure SP vs Outlet P2",
            "Stable Phase: Pressure SP vs Outlet P2"
        ]
    )

    # ---- RAMP UP ----
    fig.add_trace(go.Scatter(
        x=df_ramp[COLS["ts"]],
        y=df_ramp[COLS["p2_sp"]],
        name="Pressure SP",
        line=dict(color="black", dash="dot", width=2)
    ), row=1, col=1)

    fig.add_trace(go.Scatter(
        x=df_ramp[COLS["ts"]],
        y=df_ramp[COLS["p2"]],
        name="Outlet P2",
        line=dict(color="#1A237E", width=2)
    ), row=1, col=1)

    # ---- STABLE ----
    fig.add_trace(go.Scatter(
        x=df_stable[COLS["ts"]],
        y=df_stable[COLS["p2_sp"]],
        showlegend=False,
        line=dict(color="black", dash="dot", width=2)
    ), row=2, col=1)

    fig.add_trace(go.Scatter(
        x=df_stable[COLS["ts"]],
        y=df_stable[COLS["p2"]],
        showlegend=False,
        line=dict(color="#1A237E", width=2)
    ), row=2, col=1)

    fig.update_layout(
        height=850,
        title=f"Pressure Control Performance — {scenario}",
        paper_bgcolor="white",
        plot_bgcolor="white",
        hovermode="x unified",
        font=dict(color="black"),
        margin=dict(t=100)
    )

    fig.update_xaxes(
        showgrid=True,
        gridcolor="#E0E0E0",
        tickfont=dict(color="black"),
        title_font=dict(color="black")
    )

    fig.update_yaxes(
        title_text="Pressure (bar)",
        showgrid=True,
        gridcolor="#E0E0E0",
        tickfont=dict(color="black"),
        title_font=dict(color="black")
    )

    return fig

# ---------------- APP ----------------
st.sidebar.title("QualSteam – Sales View")
scenario = st.sidebar.radio("Select Scenario", list(DATA_FILES.keys()))

df = load_data(DATA_FILES[scenario])

ramp_start, ramp_end = PHASES[scenario]["Ramp Up"]
stable_start, stable_end = PHASES[scenario]["Stable"]

df_ramp = filter_phase(df, ramp_start, ramp_end)
df_stable = filter_phase(df, stable_start, stable_end)

st.title("Pressure Control Forensic Summary")
st.caption("Ramp-Up and Stable Phase Comparison (Pressure SP vs Outlet P2)")

fig = plot_pressure(df_ramp, df_stable, scenario)
st.plotly_chart(fig, use_container_width=True)

