"""Draw an interactive price chart with optional aligned volume bars."""
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots


def build_chart(
    prices: pd.DataFrame, currency: str, averages: list[int], show_volume: bool
) -> go.Figure:
    fig = make_subplots(
        rows=2 if show_volume else 1, cols=1, shared_xaxes=True,
        row_heights=[0.73, 0.27] if show_volume else None,
        vertical_spacing=0.06,
    )
    fig.add_trace(go.Candlestick(
        x=prices.index, open=prices.Open, high=prices.High, low=prices.Low,
        close=prices.Close, name="Daily price",
        increasing_line_color="#008578", decreasing_line_color="#c34150",
    ), row=1, col=1)

    for days, color in [(20, "#4668da"), (50, "#a55a16")]:
        if days in averages:
            fig.add_trace(go.Scatter(
                x=prices.index, y=prices[f"SMA_{days}"], mode="lines",
                name=f"SMA {days}", line=dict(color=color, width=2),
            ), row=1, col=1)

    if show_volume:
        colors = ["#008578" if up else "#c34150"
                  for up in prices.Close.ge(prices.Open)]
        fig.add_trace(go.Bar(
            x=prices.index, y=prices.Volume, marker_color=colors,
            name="Volume", showlegend=False,
        ), row=2, col=1)
        fig.update_yaxes(title_text="Volume", row=2, col=1)

    fig.update_yaxes(title_text=f"Price ({currency})", row=1, col=1)
    fig.update_xaxes(rangeslider_visible=False)
    fig.update_layout(
        height=620 if show_volume else 470, margin=dict(l=10, r=10, t=35, b=10),
        legend=dict(orientation="h", y=1.04), hovermode="x unified",
    )
    return fig
