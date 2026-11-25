"""Load daily market prices or read the local demo CSV."""
from pathlib import Path

import numpy as np
import pandas as pd
import yfinance as yf

ASSETS = {
    "AAPL": ("Apple", "USD", 180),
    "MSFT": ("Microsoft", "USD", 390),
    "GOOGL": ("Alphabet", "USD", 160),
    "TSLA": ("Tesla", "USD", 230),
    "RELIANCE.NS": ("Reliance Industries", "INR", 1400),
    "TCS.NS": ("Tata Consultancy Services", "INR", 3500),
    "INFY.NS": ("Infosys", "INR", 1500),
    "BTC-USD": ("Bitcoin", "USD", 80000),
}
COLUMNS = ["Open", "High", "Low", "Close", "Volume"]
SAMPLES = Path(__file__).resolve().parents[1] / "data" / "sample"


def normalize(frame: pd.DataFrame) -> pd.DataFrame:
    """Return numeric OHLCV with sorted, unique, timezone-naive dates."""
    if isinstance(frame.columns, pd.MultiIndex):
        level = next(
            (i for i in range(frame.columns.nlevels)
             if set(COLUMNS).issubset(frame.columns.get_level_values(i))),
            None,
        )
        if level is None:
            return pd.DataFrame(columns=COLUMNS, index=pd.DatetimeIndex([]))
        frame = frame.copy()
        frame.columns = frame.columns.get_level_values(level)
    if frame.empty or not set(COLUMNS).issubset(frame.columns):
        return pd.DataFrame(columns=COLUMNS, index=pd.DatetimeIndex([]))

    prices = frame[COLUMNS].apply(pd.to_numeric, errors="coerce").dropna()
    prices.index = pd.DatetimeIndex(prices.index).tz_localize(None).normalize()
    return prices.loc[~prices.index.duplicated(keep="last")].sort_index()


def fetch_prices(ticker: str) -> pd.DataFrame:
    """Fetch daily prices without needing an API key."""
    raw = yf.download(
        ticker, period="5y", interval="1d", auto_adjust=False,
        progress=False, threads=False, timeout=8,
    )
    return normalize(raw)


def read_sample(ticker: str) -> pd.DataFrame:
    path = SAMPLES / f"{ticker}.csv"
    return normalize(pd.read_csv(path, index_col="Date", parse_dates=["Date"]))


def generate_samples() -> None:
    """Create reproducible fictional prices for the offline demo."""
    SAMPLES.mkdir(parents=True, exist_ok=True)
    for seed, (ticker, (_, _, base)) in enumerate(ASSETS.items(), start=42):
        rng = np.random.default_rng(seed)
        frequency = "D" if ticker == "BTC-USD" else "B"
        days = pd.date_range("2023-01-01", "2026-11-24", freq=frequency)
        close = base * np.exp(np.cumsum(rng.normal(0.00025, 0.013, len(days))))
        opening = close * np.exp(rng.normal(0, 0.004, len(days)))
        sample = pd.DataFrame({
            "Open": opening,
            "High": np.maximum(opening, close) * 1.007,
            "Low": np.minimum(opening, close) * 0.993,
            "Close": close,
            "Volume": rng.integers(800_000, 9_000_000, len(days)),
        }, index=days)
        sample.to_csv(SAMPLES / f"{ticker}.csv", index_label="Date", float_format="%.4f")


if __name__ == "__main__":
    generate_samples()
    print(f"Created {len(ASSETS)} demo CSVs in {SAMPLES}")
