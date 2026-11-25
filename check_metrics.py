import pandas as pd

from src.metrics import prepare_window, summarize

days = pd.bdate_range("2026-01-01", periods=60)
close = pd.Series(range(1, 61), index=days)
history = pd.DataFrame({"Close": close, "High": close + 1, "Low": close - 1})
window = prepare_window(history, days[49].date(), days[51].date())

assert window["Close"].tolist() == [50, 51, 52]
assert window["SMA_20"].iloc[0] == 40.5
assert window["SMA_50"].iloc[0] == 25.5

kpis = summarize(window)
assert kpis["highest_high"] == 53
assert kpis["lowest_low"] == 49
assert abs(kpis["period_return_pct"] - 4) < 1e-9

print("PASS: Date range, SMA lookback, and all three KPIs.")
