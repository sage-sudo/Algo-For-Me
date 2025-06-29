import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from BACKTEST.main_backtesting import load_data, run_backtest
from BACKTEST.rdi_backtest import RDIBacktestStrategy

def upgraged_backtest_dashboard():
    # Page configuration
    st.set_page_config(page_title="Backtest Dashboard", layout="wide", initial_sidebar_state="expanded")

    # Title and intro
    st.title("📊 Backtest Dashboard for RDI-Based Strategy")
    st.markdown("""
    This dashboard runs a backtest simulation using a loosely coupled strategy interface. 
    You can adjust parameters on the sidebar and view performance metrics, the equity curve, and the detailed trade log.
    """)

    # Sidebar settings for simulation parameters
    st.sidebar.header("Simulation Parameters")
    initial_capital = st.sidebar.number_input("Initial Capital", value=100000, step=1000)
    entry_threshold = st.sidebar.slider("RDI Entry Streak Threshold", min_value=-3, max_value=10, value=3)
    run_simulation = st.sidebar.button("Run Backtest")

    # Load historical OHLC data
    data = load_data()
    if data.empty:
        st.error("No data available for backtesting. Please check your data file or path!")
    else:
        st.write(f"Loaded {len(data)} records from the data source.")

    # Run simulation when button is pressed
    if run_simulation:
        st.info("Running backtest simulation...")
        
        # Instantiate our RDI-based strategy (it adheres to the Strategy interface)
        strategy = RDIBacktestStrategy(entry_threshold=entry_threshold)
        # Run the backtest engine
        results = run_backtest(strategy, data, initial_capital=initial_capital)

        # Unpack results from the backtest simulation
        sim_data = results["data"]
        trades = results["trades"]
        summary = results["summary"]

        # Display performance summary
        st.subheader("Performance Summary")
        summary_df = pd.DataFrame.from_dict(summary, orient="index", columns=["Value"])
        st.table(summary_df)

        # Plot the equity curve using Plotly
        st.subheader("Equity Curve")
        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=sim_data["timestamp"],
            y=sim_data["equity_curve"],
            mode="lines",
            name="Equity Curve",
            line=dict(color="lime")
        ))
        fig.update_layout(
            template="plotly_dark",
            xaxis_title="Time",
            yaxis_title="Equity",
            height=500,
            margin=dict(t=40, b=40)
        )
        st.plotly_chart(fig, use_container_width=True)

        # Display the trade log as an interactive table
        st.subheader("Trade Log")
        if not trades.empty:
            st.dataframe(trades)
        else:
            st.info("No trades were executed during the backtest.")

        # Feature: Monthly Returns Breakdown
        st.subheader("📅 Monthly Returns Breakdown")

        # Extract month and year from timestamps
        sim_data["month_year"] = sim_data["timestamp"].dt.to_period("M")

        # Calculate percentage return per month
        monthly_returns = sim_data.groupby("month_year")["equity_curve"].last().pct_change().dropna()

        # Convert to DataFrame
        monthly_returns_df = monthly_returns.reset_index()
        monthly_returns_df.columns = ["Month", "Monthly Return (%)"]
        monthly_returns_df["Monthly Return (%)"] *= 100  # Convert to percentage

        # Display as a table
        st.table(monthly_returns_df)

        # Plot the monthly returns as a bar chart
        fig_monthly = go.Figure()
        fig_monthly.add_trace(go.Bar(
            x=monthly_returns_df["Month"].astype(str),
            y=monthly_returns_df["Monthly Return (%)"],
            name="Monthly Returns",
            marker=dict(color="cornflowerblue")
        ))
        fig_monthly.update_layout(
            template="plotly_dark",
            xaxis_title="Month",
            yaxis_title="Return (%)",
            height=500,
            margin=dict(t=40, b=40)
        )
        st.plotly_chart(fig_monthly, use_container_width=True)

        # Optionally, show raw simulation data (toggle with an expander)
        with st.expander("Show Simulation Data"):
            st.dataframe(sim_data)
            