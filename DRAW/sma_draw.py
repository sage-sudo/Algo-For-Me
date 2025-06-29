import plotly.graph_objs as go

def sma_candles(df, sma_fig):
    """
    Generate a Plotly candlestick chart with an SMA overlay for live dashboards.

    Parameters:
      df : pd.DataFrame
          DataFrame should contain at least:
              - 'timestamp': Timestamps for plotting on the x-axis.
              - 'SMA': Calculated SMA values.
          Optionally, if available, candlestick data should include:
              - 'open', 'high', 'low', 'close'.

    Returns:
      tuple:
          - fig: A Plotly Figure object with the candlestick chart and SMA line.
          - last_update_text: A string indicating the last update timestamp.
    """


def sma_plot(df, sma_fig):
    sma_fig.add_trace(
        go.Scatter(
        x=df["timestamp"],
        y=df["SMA"],
        mode="lines",
        name="SMA",
        line=dict(color="blue")
        ), row=1, col=[1, 2]
    )

    sma_fig.add_trace(
        go.Scatter(
        x=df["timestamp"],
        y=df["EWA"],
        mode="lines",
        name="EWA",
        line=dict(color="red")
        ), row=1, col=[1, 2]
    )

    sma_fig.add_trace(
        go.Scatter(
        x=df["timestamp"],
        y=df["SMA2"],
        mode="lines",
        name="SMA2",
        line=dict(color="orange")
        ), row=1, col=[1, 2]
    )

    sma_fig.update_layout(
        template="plotly_dark",
        xaxis_rangeslider_visible=False,
        height=700,
        title="Candlestick Chart with SMA Overlay"
    )
    sma_fig.update_layout(template="plotly_dark", height=700)

    #last_update_text = f"Last updated: {pd.Timestamp.now().str#ftime('%Y-%m-%d %H:%M:%S')}"
    return sma_fig #, last_update_text
