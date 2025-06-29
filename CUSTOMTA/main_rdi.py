import pandas as pd
import numpy as np

from ta.volatility import AverageTrueRange


def compute_rdi(df: pd.DataFrame, period: int = 10, buy_threshold: float = 0.35, sell_threshold: float = -0.3) -> pd.DataFrame:
    """
    Compute the Relative Directional Index (RDI) and track entry streaks for buying and selling signals.

    The RDI is calculated as the exponential moving average (EMA) of the product of
    price direction and conviction, where:
      - Conviction = (absolute difference between close and open) / (high - low)
      - Direction = +1 if price increased, -1 if price decreased

    The streak values help introduce a delay before confirming a signal:
      - Buy streak tracks consecutive periods where RDI is above `buy_threshold`.
      - Sell streak tracks consecutive periods where RDI is below `sell_threshold`.

    Args:
        df (pd.DataFrame): DataFrame containing 'open', 'high', 'low', and 'close' columns.
        period (int, optional): The period for the EMA calculation. Defaults to 10.
        buy_threshold (float, optional): Threshold for confirming buy signal. Defaults to 0.3.
        sell_threshold (float, optional): Threshold for confirming sell signal. Defaults to -0.3.

    Returns:
        pd.DataFrame: A DataFrame with columns:
            'rdi'       : The computed Relative Directional Index.
            'buy_streak': The consecutive count of periods where RDI > buy_threshold.
            'sell_streak': The consecutive count of periods where RDI < sell_threshold.
    """
    required_columns = {"open", "high", "low", "close"}
    if not required_columns.issubset(df.columns):
        missing = required_columns - set(df.columns)
        raise ValueError(f"Input DataFrame is missing required columns: {missing}")

    # Calculate candle body and range
    body = (df["close"] - df["open"]).abs()
    range_ = df["high"] - df["low"]

    # Conviction measure (avoids division by zero)
    conviction = body / range_.replace(0, 1e-9)

    # Directional indicator (+1 for up, -1 for down)
    direction = (df["close"] > df["open"]).astype(int) * 2 - 1

    # Compute directional conviction
    directional_conviction = direction * conviction

    # Compute RDI using exponential moving average
    rdi_series = directional_conviction.ewm(span=period, adjust=False).mean()

    #rdi_series = directional_conviction.rolling(window=period).mean()

    # Check ATR -----------------------------------------------
    
    atr_indicator = AverageTrueRange(high=df['high'], low=df['low'], close=df['close'], window=14)

    df['ATR'] = atr_indicator.average_true_range()

    # Calculate the 60th percentile of ATR values
    atr_60th_percentile = np.percentile(df['ATR'].dropna(), 60)

    is_active = atr_indicator.average_true_range() > atr_60th_percentile

    clean_RDI = [1 if r else 0 for r in is_active ]

    #tp_sl_exit = (df["close"] < df["close"].shift(1)).astype(int)

    # ---------------------END---------------------------------


    # Check Simple Moving Average
    #sma = ta.sma

    # Initialize streaks for buy/sell thresholds
    buy_streak = [0] * len(rdi_series)
    sell_streak = [0] * len(rdi_series)

    for i, value in enumerate(rdi_series):

        if value > buy_threshold:
            if clean_RDI[i] == 1: #& tp_sl_exit[i] != 1:
                buy_streak[i] = buy_streak[i-1] + 1 if i > 0 else 1
        else:
            buy_streak[i] = 0
        
        if value < sell_threshold:
            if clean_RDI[i] == 1:
                sell_streak[i] = 0#ell_streak[i-1] + 1 if i > 0 else 1
        else:
            sell_streak[i] = 0

    # Return DataFrame with computed values
    return pd.DataFrame({'rdi': rdi_series, 'buy_streak': buy_streak, 'sell_streak': sell_streak})