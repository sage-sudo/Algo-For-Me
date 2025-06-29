#---------------------------------------------------FOR LIVE DASHBOARD AND SIGNALS ON THE CANDLES--------------------------
#from plotly.subplots import make_subplots
import plotly.graph_objs as go
#from ui.update_dashboard import sub_plot 

def rdi_plot(df, rdi_fig):
        # 📌 Entry and Exit Points Logic
        ENTRY_THRESHOLD = 3
        entry_points = df[df["buy_streak"] >= ENTRY_THRESHOLD]
        exit_points = df[df["sell_streak"] >= ENTRY_THRESHOLD]

        entry_points["marker_position"] = entry_points["low"] * 0.995
        exit_points["marker_position"] = exit_points["high"] * 1.005


        rdi_fig.add_trace(go.Scatter(
            x=entry_points["timestamp"], y=entry_points["marker_position"],
            mode="markers", marker=dict(color="lime", symbol="triangle-up", size=12),
            name="Buy Signals", hovertemplate="Buy at %{x}<br>Low: %{y}<extra></extra>"
        ), row=1, col=[1, 2])

        rdi_fig.add_trace(go.Scatter(
            x=exit_points["timestamp"], y=exit_points["marker_position"],
            mode="markers", marker=dict(color="red", symbol="triangle-down", size=12),
            name="Sell Signals", hovertemplate="Sell at %{x}<br>High: %{y}<extra></extra>"
        ), row=1, col=[1, 2])

        # 📊 RDI Chart
        rdi_fig.add_trace(go.Scatter(
            x=df["timestamp"], y=df["rdi"], mode="lines", name="RDI", line=dict(color="orange")
        ), row=2, col=1)

        rdi_fig.update_layout(template="plotly_dark", xaxis_rangeslider_visible=False, height=700)

        #last_update_text = f"Last updated: {pd.Timestamp.now().strftime('%Y-%m-%d %H:%M:%S')}"
        return rdi_fig #, last_update_text