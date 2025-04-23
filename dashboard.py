import pandas as pd
import plotly.express as px
import streamlit as st
import datetime

# === App Settings ===
# Configures page layout and tab info
st.set_page_config(layout="wide", page_title="Steam Game Dashboard", page_icon="🎮")

# === Load and Clean Data ===
@st.cache_data
def load_data():
    df = pd.read_parquet("cleaned_steamcharts.parquet")
    df = df[~df['gamename'].str.contains('<U\\+', na=False, regex=True)]
    df['gamename'] = df['gamename'].apply(lambda x: x if '<U+' not in x else 'Unknown Game')
    df['date'] = pd.to_datetime(df['date'])
    df = df[df['avg'].notnull() & df['peak'].notnull()]
    return df

df = load_data()

# === Styling ===
# Background color and top spacing
st.markdown("""
    <style>
    .block-container {
        padding-top: 1rem;
        background-color: #ffffff
    }
    .stApp {
        background-color: #f0f2f6;
    }
    </style>
""", unsafe_allow_html=True)

# === Header ===
st.markdown("<h1 style='text-align: center; color: #1c1c1c;'>🎮 Steam Game Popularity Dashboard</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center; color: #666;'>Analyze key trends in average and peak player behavior across top Steam games</p><hr>", unsafe_allow_html=True)

# === KPI Metrics ===
# Shows summary stats and date selector
col1, col2, col3 = st.columns(3)
col1.metric("Total Games", df["gamename"].nunique())
col2.metric("Total Records", len(df))

df['date'] = pd.to_datetime(df['date'])
min_date = df['date'].min().date()
max_date = df['date'].max().date()

with col3:
    start_date, end_date = st.date_input(
        "Select Date Range",
        value=(min_date, max_date),
        min_value=min_date,
        max_value=max_date
    )

# === Game Filter and Feature Engineering ===
selected_game = st.selectbox("🎯 Select a Game", sorted(df["gamename"].unique()))
filtered_df = df[df["gamename"] == selected_game].copy()
filtered_df["avg_peak_ratio"] = filtered_df["avg"] / filtered_df["peak"]
filtered_df["drop_ratio"] = -filtered_df["gain"] / filtered_df["avg"]

# === Dynamic Viz 1: Peak Player Trend ===
st.subheader("🚀 Peak Player Trend")
fig5 = px.area(
    filtered_df,
    x="date",
    y="peak",
    title=f"Peak Player Trend for {selected_game}",
    labels={"peak": "Peak Players"},
    hover_data={"peak": ".0f"}
)
fig5.update_layout(margin=dict(t=40, b=20), height=400)
st.plotly_chart(fig5, use_container_width=True)

# === Dynamic Viz 2: Drop Ratio Trend ===
st.subheader("🔻 Drop Ratio Trend")
fig2 = px.line(
    filtered_df,
    x="date",
    y="drop_ratio",
    title="Drop Ratio (Player Loss Indicator)",
    labels={"drop_ratio": "Drop Ratio", "date": "Month"},
    hover_data={"drop_ratio": ".2f"}
)
fig2.update_layout(margin=dict(t=40, b=20), height=350)
st.plotly_chart(fig2, use_container_width=True)

# === Dynamic Viz 3 & 4: Monthly Gain and Avg/Peak Ratio ===
col_left2, col_right2 = st.columns(2)

with col_left2:
    st.subheader("📊 Monthly Gain/Loss")
    fig3 = px.bar(
        filtered_df,
        x="date",
        y="gain",
        title="Monthly Player Gain or Loss",
        labels={"gain": "Net Gain", "date": "Month"},
        hover_data={"gain": ".0f"}
    )
    fig3.update_layout(margin=dict(t=40, b=20), height=350)
    st.plotly_chart(fig3, use_container_width=True)

with col_right2:
    st.subheader("📉 Avg/Peak Consistency Ratio")
    fig4 = px.line(
        filtered_df,
        x="date",
        y="avg_peak_ratio",
        title="Ratio of Average to Peak Players Over Time",
        labels={"avg_peak_ratio": "Avg/Peak Ratio"},
        hover_data={"avg_peak_ratio": ".2f"}
    )
    fig4.update_layout(margin=dict(t=40, b=20), height=350)
    st.plotly_chart(fig4, use_container_width=True)

# === Static Table Viz: Avg vs Peak Comparison ===
st.subheader("🌍 Top Games: Avg vs Peak Players")
# Shows a grouped bar chart for top 10 games by average player count
top_games = df.groupby("gamename")[["avg", "peak"]].mean().nlargest(10, "avg").reset_index()
fig_static = px.bar(
    top_games.melt(id_vars="gamename", value_vars=["avg", "peak"], var_name="Metric", value_name="Players"),
    x="Players",
    y="gamename",
    color="Metric",
    barmode="group",
    title="Top 10 Games by Average and Peak Player Count",
    height=450
)
st.plotly_chart(fig_static, use_container_width=True)
