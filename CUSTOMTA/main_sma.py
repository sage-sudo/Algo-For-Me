import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from plotly.subplots import make_subplots
import plotly.graph_objs as go

def compute_sma(df: pd.DataFrame, period: int = 20) -> pd.DataFrame:
    sma_period = 73
    ewa_period = 150
    """
    Compute the Simple Moving Average (SMA) and generate trading signals for a given DataFrame.

    Parameters:
      df : pd.DataFrame
          DataFrame containing at least the 'Close' price column.
      period : int, optional
          Window period to compute the moving average, default is 20.

    Returns:
      pd.DataFrame
          DataFrame with added columns:
              - 'SMA': The computed moving average.
              - 'Signal': Trading signal (1 for buy, -1 for sell) based on the price crossing above/below the SMA.
              - 'Position': Difference in signals indicating trade entries/exits.
              - 'Market_Return': Daily return of the underlying asset.
              - 'Strategy_Return': Return from the strategy calculated using a shifted signal.
              - 'Cumulative_Market': Cumulative return of the underlying asset.
              - 'Cumulative_Strategy': Cumulative return of the SMA strategy.
    """
    # Compute the SMA over the specified period
    df.loc[:, 'SMA'] = df['close'].rolling(window=sma_period).median()

    df.loc[:, 'SMA2'] = df['close'].rolling(window=sma_period).mean()

    df.loc[:, 'EWA'] = df['close'].ewm(span=ewa_period, adjust=False).mean()

    #df.loc[:, 'SMA'] = df.loc[:, 'SMA'].fillna(0)

        # Initialize the Signal column with zeros
    df.loc[:, 'Signal'] = 0

    # Generate signals only for the data points where SMA is available.
    # Signal = 1 when price > SMA, otherwise -1.
    df.loc[df.index[period:], 'Signal'] = np.where(
        df.loc[df.index[period:], 'close'] > df.loc[df.index[period:], 'SMA'],
        1,
        -1
    )

    # Calculate Position to indicate changes in signal (trade entries/exits)
    df.loc[:, 'Position'] = df['Signal'].diff()
    #df.loc[:, 'Position'] = df.loc[:, 'Position'].fillna(0)

    # Calculate daily market returns as percentage change
    df.loc[:, 'Market_Return'] = df['close'].pct_change()
    #df.loc[:, 'Market_Return'] = df.loc[:, 'Market_Return'].fillna(0)

    # Strategy return: we simulate execution based on the previous day's signal.
    df.loc[:, 'Strategy_Return'] = df['Market_Return'] * df['Signal'].shift(1)
    #df.loc[:, 'Strategy_Return'] = df.loc[:, 'Strategy_Return'].fillna(0)

    # Calculate cumulative returns for both market and strategy performance
    df.loc[:, 'Cumulative_Market'] = (1 + df['Market_Return']).cumprod()
    df.loc[:, 'Cumulative_Strategy'] = (1 + df['Strategy_Return']).cumprod()


    return df
