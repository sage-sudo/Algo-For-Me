import pandas as pd
from abc import ABC, abstractmethod
from CUSTOMTA.main_rdi import compute_rdi


class Strategy(ABC):
    @abstractmethod
    def generate_signals(self, data: pd.DataFrame) -> pd.DataFrame:
        """
        Given a DataFrame containing OHLC data, generate trading signals.
        The returned DataFrame must contain a 'signal' column.
        """
        pass


class RDIBacktestStrategy(Strategy):
    def __init__(self, entry_threshold: int = 3):
        """
        Initialize the RDI-based strategy.

        Args:
            entry_threshold (int): Number of consecutive bars (streak) required to generate a buy signal.
        """
        self.entry_threshold = entry_threshold

    def generate_signals(self, data: pd.DataFrame) -> pd.DataFrame:
        """
        Generate trading signals using the RDI and streak logic.
        
        A signal of 1 indicates a buy condition (streak >= entry_threshold), 0 otherwise.
        """
        # Compute RDI and streak using our previously developed compute_rdi logic.

        rdi_result = compute_rdi(data)

        data["buy_streak"] = rdi_result["buy_streak"]
        data["sell_streak"] = rdi_result["sell_streak"]
        data["rdi"] = rdi_result["rdi"]

        # 🚨 Remove or modify 'streak' logic since it's now split into buy/sell streaks
        data["signal"] = 0

        # 📌 Adjust signal logic:
        # Set signal to 1 when buy streak meets or exceeds entry_threshold
        data.loc[data["buy_streak"] >= self.entry_threshold, "signal"] = 1

        # Set signal to -1 when sell streak meets or exceeds entry_threshold (if selling is needed)
        data.loc[data["sell_streak"] >= self.entry_threshold, "signal"] = -1  

        return data
    