from plotly.subplots import make_subplots
import plotly.graph_objs as go
import pandas as pd
from DRAW.rdi_draw import rdi_plot
from DRAW.sma_draw import sma_plot

#------------------------------------------------MAIN SUB PLOT ----------------------------------------------
def sub_plot(df):    

    sub_fig = make_subplots(rows=2, cols=1, shared_xaxes=True, vertical_spacing=0.03)

    sub_fig.add_trace(go.Candlestick(
         x=df["timestamp"], open=df["open"], high=df["high"], low=df["low"], close=df["close"], name="Candles"
    ), row=1 , col=1)

    sub_fig.update_layout(template="plotly_dark", xaxis_rangeslider_visible=False, height=700)

    rdi_fig = rdi_plot(df, sub_fig)
    sma_fig = sma_plot(df, sub_fig)

    last_update_text = f"Last updated: {pd.Timestamp.now().strftime('%Y-%m-%d %H:%M:%S')}"

    return sub_fig,  rdi_fig, sma_fig, last_update_text # 

# -------------------------------------------END ----------------------------------------------------------------


# -----------------------------------------RDI------------------------------------------------------------------
#def rdi_plot(df):
#     rdi_fig = sub_plot(df)
#     rdi_results = rdi_candles(df, rdi_fig)
#     return rdi_results

# -----------------------------------------END------------------------------------------------------------------

# --------------------------------------------SMA---------------------------------------------------------------#
#def sma_plot(df):
#     sma_fig = sub_plot(df)
#     sma_fig.add_trace(
#         go.Scatter(
#          x=df["timestamp"],
#          y=df["SMA"],
#          mode="lines",
#          name="SMA",
#          line=dict(color="blue")
#          )
#        )
#     sma_fig.update_layout(template="plotly_dark", height=700)

#     last_update_text = f"Last updated: {pd.Timestamp.now().str#ftime('%Y-%m-%d %H:%M:%S')}"
#     return sma_fig, last_update_text
# --------------------------------------------END---------------------------------------------------------------