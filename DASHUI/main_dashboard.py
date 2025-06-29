import pandas as pd
import numpy as np

from dash import Dash, dcc, html
from dash.dependencies import Input, Output

import plotly.graph_objs as go
#from plotly.subplots import make_subplots


from DYNAMICS.dynamic_params import PARQUET_PATH

from DASHUI.sub_dashboard import sub_plot

from CUSTOMTA.main_rdi import compute_rdi
from CUSTOMTA.main_sma import compute_sma


#from backtest.rdi_backtest_skeleton import rdi_candles  # Function to build RDI chart
#from custom_ta.backbone_sma import compute_sma, sma_candles  # SMA computation and optional SMA candlestick function

#from custom_ta.rdi import compute_rdi         # Custom RDI computation with buy/sell streaks

#from ui.update_dashboard import sub_plot

# Import custom modules for data path, RDI, and SMA computation

# ------------------------------
# Safely Load Data
# ------------------------------
def load_data() -> pd.DataFrame:
    """
    Load historical data from a Parquet file defined by PARQUET_PATH.
    Returns an empty DataFrame with expected columns if there is an error.
    """
    try:
        df = pd.read_parquet(PARQUET_PATH)
        df['timestamp'] = pd.to_datetime(df['timestamp'])
        return df
    except Exception as e:
        print(f"❌ Error loading data: {e}")
        return pd.DataFrame(columns=["timestamp", "open", "high", "low", "close", "volume"])

# ------------------------------
# Build the Dash App
# ------------------------------
def build_dash_app() -> Dash:
    app = Dash(__name__)
    app.title = "Crypto Dashboard"

    # Layout includes two charts: one for candlesticks + SMA and one for RDI
    app.layout = html.Div(
        [
            html.H1("📊 Real-Time Candlestick Charts", style={"textAlign": "center"}),
            dcc.Interval(id="interval", interval=60 * 1000, n_intervals=0),  # Refresh every minute
            html.Div(dcc.Graph(id="clean-chart"), style={"padding": "10px"}),   # Clean Candlestick
            html.Div(dcc.Graph(id="populated-chart"), style={"padding": "10px", "marginTop": "5px"}),  # Populated chart
            dcc.Interval(id="interval-chart", interval=60 * 1000, n_intervals=1),
            html.Div(id="last-update", style={"textAlign": "center", "color": "gray", "marginTop": "10px"})
        ],
        style={
            "backgroundColor": "#121212",
            "minHeight": "100vh",
            "padding": "20px",
            "color": "white"
        }
    )

    # ------------------------------
    # Graph Update Callback
    # ------------------------------
    @app.callback(
        [Output("clean-chart", "figure"),
         Output("populated-chart", "figure"),
         Output("last-update", "children")],
        [Input("interval", "n_intervals")]
    )
    def update_graph(n: int):
        # Load the data
        df = load_data()
        if df.empty:
            empty_fig = go.Figure()
            return empty_fig, empty_fig, "No data available"
        
        # ------------------------------
        # Build the Candlestick ("clean-chart")
        # ------------------------------

        clean_fig = go.Figure(
            data=[
                go.Candlestick(
                    x=df["timestamp"],
                    open=df["open"],
                    high=df["high"],
                    low=df["low"],
                    close=df["close"],
                    name="Candles"
                ),
            ]
        )
        clean_fig.update_layout(template="plotly_dark", xaxis_rangeslider_visible=False, height=700)
        # -----------------------------------------------------------------------------------------------------

    
        # ------------------------------
        # Compute RDI and its streaks
        # ------------------------------
        rdi_result = compute_rdi(df)
        df["rdi"] = rdi_result["rdi"]
        df["buy_streak"] = rdi_result["buy_streak"]
        df["sell_streak"] = rdi_result["sell_streak"]


        # ---------------------------------
        # Compute SMA 
        # ---------------------------------
        sma_results = compute_sma(df)
        df["SMA"] = sma_results["SMA"]
        df["EWA"] = sma_results["EWA"]
        df["SMA2"] = sma_results["SMA2"]
        # ---------------------------------------------------


        sub_fig,  rdi_fig, sma_rdi, last_update_text = sub_plot(df)



        # ------------------------------
        # Compute RDI and its streaks
        # ------------------------------
        #rdi_result = compute_rdi(df)
        #df["rdi"] = rdi_result["rdi"]
        #df["buy_streak"] = rdi_result["buy_streak"]
        #df["sell_streak"] = rdi_result["sell_streak"]

        # ------------------------------
        # Compute SMA, trading signals, and returns
        # ------------------------------
        #df = compute_sma(df, period=20)


        # ------------------------------
        # Build the RDI Chart ("rdi-chart")
        # ------------------------------
        # Generate the RDI chart using the custom function,
        # then overlay the SMA line on it as well.

        #rdi_fig, sma_fig, _ = sub_plot(df)
        #sma_fig, _ = sma_plot(df)
        #sma_fig, _ = rdi_candles(df)
        #sma_fig.add_trace(
         #   go.Scatter(
          #      x=df["timestamp"],
           #     y=df["SMA"],
            #    mode="lines",
             #   name="SMA",
              #  line=dict(color="blue")
            #)
        #)
        #rdi_fig.update_layout(template="plotly_dark", height=700)

        # ------------------------------
        # Return figures and last update text
        # ------------------------------
        update_text = f"Last updated: {pd.Timestamp.now().strftime('%Y-%m-%d %H:%M:%S')}"
        return clean_fig, sub_fig, update_text 

    return app

# ------------------------------
# Run the Dash App
# ------------------------------
if __name__ == "__main__":
    app = build_dash_app()
    app.run_server(debug=True)