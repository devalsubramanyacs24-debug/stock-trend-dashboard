"""Run with python -m streamlit run app.py."""
from datetime import date, timedelta

import streamlit as st

from src.charts import build_chart
from src.data import ASSETS, fetch_prices, read_sample
from src.metrics import prepare_window, summarize

st.set_page_config(page_title="Market Trend Dashboard", page_icon="📈", layout="wide")
st.title("Market Trend Dashboard")
st.caption("Explore daily prices, moving averages, and trading volume.")


@st.cache_data(ttl=3600, show_spinner=False)
def load_history(ticker: str, offline: bool):
    if not offline:
        try:
            prices = fetch_prices(ticker)
            if not prices.empty:
                return prices, "Yahoo Finance", None
        except Exception:
            pass
    reason = None if offline else "Yahoo Finance was unavailable for this ticker."
    return read_sample(ticker), "Simulated demo CSV", reason


with st.sidebar:
    st.header("Chart settings")
    ticker = st.selectbox(
        "Asset", ASSETS,
        format_func=lambda key: f"{ASSETS[key][0]} ({key})",
    )
    offline = st.checkbox("Use offline demo data")
    show_20 = st.checkbox("Show SMA 20", value=True, help="Average of the last 20 closes.")
    show_50 = st.checkbox("Show SMA 50", value=True, help="Average of the last 50 closes.")
    show_volume = st.checkbox("Show trading volume", value=True)

try:
    with st.spinner("Loading daily prices..."):
        history, source, reason = load_history(ticker, offline)
except (OSError, ValueError):
    st.error("Could not read the market data or demo file. Run python -m src.data to recreate the samples.")
    st.stop()

if history.empty:
    st.info("No data available for this asset.")
    st.stop()

if source == "Simulated demo CSV":
    note = f"{reason} " if reason else ""
    st.info(note + "Showing simulated demo data. These are fictional prices.")

latest = history.index.max().date()
with st.sidebar:
    start = st.date_input("Start date", latest - timedelta(days=365), key=f"start-{ticker}-{source}")
    end = st.date_input("End date", latest, key=f"end-{ticker}-{source}")

if start > end:
    st.warning("Start date must be on or before end date.")
    st.stop()

prices = prepare_window(history, start, end)
if prices.empty:
    st.info("No data available for this date range. Try a wider range or include a trading day.")
    st.stop()

name, currency, _ = ASSETS[ticker]
st.subheader(f"{name} ({ticker})")
st.caption(f"{prices.index[0]:%d %b %Y} through {prices.index[-1]:%d %b %Y} · {len(prices)} daily bars")

kpis = summarize(prices)
high, low, change = st.columns(3)
high.metric("Highest high", f"{kpis['highest_high']:,.2f} {currency}")
low.metric("Lowest low", f"{kpis['lowest_low']:,.2f} {currency}")
period_return = kpis["period_return_pct"]
change.metric("Net period return", f"{period_return:+.2f}%" if period_return is not None else "Unavailable")

averages = [days for days, enabled in [(20, show_20), (50, show_50)] if enabled]
st.plotly_chart(build_chart(prices, currency, averages, show_volume), width="stretch")
if any(prices[f"SMA_{days}"].isna().any() for days in averages):
    st.caption("Some moving-average values are blank because earlier trading history is limited.")

st.download_button(
    "Download selected data (CSV)",
    prices.to_csv(index_label="Date").encode("utf-8"),
    file_name=f"{ticker}_{start}_{end}.csv",
    mime="text/csv",
)
st.caption(f"Source: {source} · Latest available bar: {latest:%d %b %Y} · Educational use only.")

