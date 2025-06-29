# backtest.py

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from abc import ABC, abstractmethod
from DYNAMICS.dynamic_params import PARQUET_PATH

#from custom_ta.rdi import compute_rdi
#from backtest.rdi_backtest_skeleton import RDIBacktestStrategy

class Strategy(ABC):
    @abstractmethod
    def generate_signals(self, data: pd.DataFrame) -> pd.DataFrame:
        """
        Given a DataFrame containing OHLC data, generate trading signals.
        The returned DataFrame must contain a 'signal' column.
        """
        pass

def load_data(filepath=PARQUET_PATH) -> pd.DataFrame:
    """Load historical OHLC data from a Parquet file and return a time-sorted DataFrame."""
    try:
        df = pd.read_parquet(filepath)
        df["timestamp"] = pd.to_datetime(df["timestamp"])
        return df.sort_values("timestamp").reset_index(drop=True)
    except Exception as e:
        print(f"Error loading data: {e}")
        return pd.DataFrame()

def compute_max_drawdown(equity_curve: pd.Series) -> float:
    """
    Compute the maximum drawdown given a time series of equity values.
    Returns the maximum drawdown as a percentage (negative value).
    """
    running_max = equity_curve.cummax()
    drawdowns = (equity_curve - running_max) / running_max
    return drawdowns.min()

def compute_sortino_ratio(returns: pd.Series, required_return: float = 0.0) -> float:
    """
    Sortino ratio = (mean(returns) - required_return) / downside_deviation
    """
    downside_returns = returns[returns < required_return]
    downside_dev = downside_returns.std(ddof=0)
    if downside_dev == 0:
        return np.nan
    excess_return = returns.mean() - required_return
    return excess_return / downside_dev

def compute_sharpe_ratio(returns: pd.Series, risk_free_rate: float = 0.0) -> float:
    """
    Sharpe ratio = (mean(returns) - risk_free_rate) / std_dev(returns)
    """
    excess_return = returns.mean() - risk_free_rate
    vol = returns.std(ddof=0)
    if vol == 0:
        return np.nan
    return excess_return / vol

def annualized_return(final_equity: float, initial_capital: float, n_periods: int, periods_per_year: float) -> float:
    """
    Compute CAGR = (final/initial)^(periods_per_year / n_periods) - 1
    """
    if initial_capital <= 0 or final_equity <= 0:
        return np.nan
    return (final_equity / initial_capital) ** (periods_per_year / n_periods) - 1

def run_backtest(strategy: Strategy,
                 data: pd.DataFrame,
                 initial_capital: float = 100_000,
                 periods_per_year: float = 12) -> dict: #252
    """
    Run a backtest simulation using the provided strategy.

    - Long entry when signal flips 0→1, exit 1→0
    - Equity curve tracks realized + unrealized PnL

    Returns dict with:
      - 'data': DataFrame with simulation
      - 'trades': DataFrame of each trade
      - 'summary': dict of performance metrics
    """
    data = strategy.generate_signals(data.copy())
    data["position"]      = 0
    data["trade_price"]   = np.nan
    data["equity"]        = initial_capital
    data["signal_change"] = data["signal"].diff().fillna(0)

    current_capital = initial_capital
    position        = 0
    buy_price       = None
    trade_log       = []
    equity_curve    = []

    # Iterate bars
    for i, row in data.iterrows():
        sig   = row["signal"]
        price = row["close"]

        # ENTRY
        if position == 0 and sig == 1:
            position  = 1
            buy_price = price
            data.at[i, "trade_price"] = buy_price
            trade   = {
                "entry_time": row["timestamp"],
                "entry_price": buy_price,
                "exit_time": None,
                "exit_price": None,
                "return": None,
                "duration_bars": None
            }

        # EXIT
        elif position == 1 and sig == 0:
            sell_price   = price
            trade_return = (sell_price - buy_price) / buy_price
            current_capital *= (1 + trade_return)
            position = 0
            data.at[i, "trade_price"] = sell_price

            trade["exit_time"]    = row["timestamp"]
            trade["exit_price"]   = sell_price
            trade["return"]       = trade_return
            trade["duration_bars"]= i - data.index[data["trade_price"].first_valid_index()]  # or custom
            trade_log.append(trade)
            buy_price = None

        data.at[i, "position"] = position

        # Update equity
        if position == 1:
            data.at[i, "equity"] = current_capital * (price / buy_price)
        else:
            data.at[i, "equity"] = current_capital

        equity_curve.append(data.at[i, "equity"])

    data["equity_curve"] = equity_curve
    eq_series           = pd.Series(equity_curve, index=data["timestamp"])
    returns             = eq_series.pct_change().fillna(0)

    # Basic stats
    final_equity     = equity_curve[-1]
    cumulative_ret   = (final_equity - initial_capital) / initial_capital
    max_dd           = compute_max_drawdown(eq_series)
    cagr             = annualized_return(final_equity, initial_capital, len(returns), periods_per_year)

    # Ratios
    sharpe   = compute_sharpe_ratio(returns)
    sortino  = compute_sortino_ratio(returns)
    calmar   = np.nan
    if max_dd < 0:
        calmar = cumulative_ret / abs(max_dd)

    # Trade stats
    trades_df      = pd.DataFrame(trade_log)
    total_trades   = len(trades_df)
    wins           = trades_df[trades_df["return"] >= 0]
    losses         = trades_df[trades_df["return"] <= 0]
    win_rate       = len(wins) / total_trades if total_trades else np.nan
    avg_win        = wins["return"].mean() if not wins.empty else np.nan
    avg_loss       = losses["return"].mean() if not losses.empty else np.nan
    profit_factor  = wins["return"].sum() / abs(losses["return"].sum()) if not losses.empty else np.nan
    expectancy     = (win_rate * avg_win) + ((1 - win_rate) * avg_loss)

    summary = {
        "initial_capital": initial_capital,
        "final_equity": final_equity,
        "cumulative_return": cumulative_ret,
        "CAGR": cagr,
        "max_drawdown": max_dd,
        "Sharpe_ratio": sharpe,
        "Sortino_ratio": sortino,
        "Calmar_ratio": calmar,
        "total_trades": total_trades,
        "win_rate": win_rate,
        "avg_win": avg_win,
        "avg_loss": avg_loss,
        "profit_factor": profit_factor,
        "expectancy": expectancy
    }

    return {
        "data": data,
        "trades": trades_df,
        "summary": summary
    }