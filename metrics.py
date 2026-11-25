"""Calculate market indicators from daily price history."""
from datetime import date

import pandas as pd


def prepare_window(history: pd.DataFrame, start: date, end: date) -> pd.DataFrame:
    """Calculate moving averages before trimming to inclusive calendar dates."""
    if start > end:
        raise ValueError("Start date must be on or before end date.")
    prices = history.sort_index().copy()
    for days in (20, 50):
        prices[f"SMA_{days}"] = prices["Close"].rolling(days).mean()
    return prices.loc[pd.Timestamp(start):pd.Timestamp(end)].copy()


def summarize(prices: pd.DataFrame) -> dict[str, float | None]:
    """Calculate the three dashboard KPIs for the selected trading days."""
    if prices.empty:
        return {"highest_high": None, "lowest_low": None, "period_return_pct": None}
    first, last = prices["Close"].iloc[[0, -1]]
    return {
        "highest_high": float(prices["High"].max()),
        "lowest_low": float(prices["Low"].min()),
        "period_return_pct": float((last - first) / first * 100) if first > 0 else None,
    }
