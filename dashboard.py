from pathlib import Path

import pandas as pd
import streamlit as st


st.set_page_config(
    page_title="Premarket Stock Watchlist",
    layout="wide"
)

REPORTS_DIR = Path("reports")
LOG_PATH = Path("data/paper_trades.csv")


def load_latest_log():
    if not LOG_PATH.exists():
        return pd.DataFrame()

    df = pd.read_csv(LOG_PATH)

    if "date" in df.columns:
        df["date"] = pd.to_datetime(df["date"], errors="coerce")

    return df


def get_latest_day(df: pd.DataFrame):
    if df.empty or "date" not in df.columns:
        return df

    latest_date = df["date"].max()
    return df[df["date"] == latest_date].copy()


st.title("📈 Premarket Stock Watchlist")
st.caption("Prototype only. Paper-trading review, not financial advice.")

df = load_latest_log()

if df.empty:
    st.warning("No paper_trades.csv data found yet. Run python main.py first.")
    st.stop()

latest_df = get_latest_day(df)

if latest_df.empty:
    st.warning("No latest-day rows found.")
    st.stop()

latest_date = latest_df["date"].max()
st.subheader(f"Latest Watchlist — {latest_date.date()}")

# Sidebar filters
st.sidebar.header("Filters")

min_score = st.sidebar.slider(
    "Minimum score",
    min_value=0,
    max_value=100,
    value=0,
    step=5
)

show_only_liquid = st.sidebar.checkbox("Show only liquidity_pass = True", value=False)

filtered = latest_df.copy()

if "score" in filtered.columns:
    filtered = filtered[filtered["score"] >= min_score]

if show_only_liquid and "liquidity_pass" in filtered.columns:
    filtered = filtered[filtered["liquidity_pass"] == True]

# Summary metrics
col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric("Tickers", len(filtered))

with col2:
    avg_score = filtered["score"].mean() if "score" in filtered.columns and not filtered.empty else 0
    st.metric("Avg Score", f"{avg_score:.1f}")

with col3:
    if "liquidity_pass" in filtered.columns:
        liquid_count = (filtered["liquidity_pass"] == True).sum()
    else:
        liquid_count = 0
    st.metric("Liquidity Pass", int(liquid_count))

with col4:
    if "change_pct" in filtered.columns:
        avg_move = filtered["change_pct"].mean()
    else:
        avg_move = 0
    st.metric("Avg Daily Move", f"{avg_move:.2f}%")

# Main ranked table
st.subheader("Ranked Summary")

summary_columns = [
    "ticker",
    "score",
    "change_pct",
    "premarket_change_pct",
    "catalyst_type",
    "catalyst_strength",
    "liquidity_pass",
    "risk_flags",
    "liquidity_flags"
]

existing_summary_columns = [col for col in summary_columns if col in filtered.columns]

if "score" in filtered.columns:
    filtered = filtered.sort_values("score", ascending=False)

st.dataframe(
    filtered[existing_summary_columns],
    use_container_width=True,
    hide_index=True
)

# Stock detail cards
st.subheader("Stock Details")

for _, row in filtered.iterrows():
    ticker = row.get("ticker", "UNKNOWN")
    score = row.get("score", "N/A")
    headline = row.get("latest_headline", "No headline found")
    source = row.get("news_source", "Unknown source")
    link = row.get("news_link", "")
    catalyst = row.get("catalyst_type", "unclear")
    catalyst_strength = row.get("catalyst_strength", 0)
    risk_flags = row.get("risk_flags", "")
    liquidity_flags = row.get("liquidity_flags", "")

    with st.expander(f"{ticker} — Score: {score}"):
        st.write(f"**Headline:** {headline}")
        st.write(f"**Source:** {source}")

        if isinstance(link, str) and link.strip():
            st.markdown(f"**Link:** [{link}]({link})")

        st.write(f"**Catalyst:** {catalyst}")
        st.write(f"**Catalyst Strength:** {catalyst_strength}")
        st.write(f"**Risk Flags:** {risk_flags}")
        st.write(f"**Liquidity Flags:** {liquidity_flags}")

# Historical performance section
st.subheader("Performance Tracking")

perf_cols = [
    "date",
    "ticker",
    "score",
    "result_1d_pct",
    "spy_1d_pct",
    "beat_spy_1d",
    "result_3d_pct",
    "spy_3d_pct",
    "beat_spy_3d"
]

existing_perf_cols = [col for col in perf_cols if col in df.columns]

if existing_perf_cols:
    st.dataframe(
        df[existing_perf_cols].sort_values("date", ascending=False),
        use_container_width=True,
        hide_index=True
    )
else:
    st.info("No performance tracking columns found yet.")
