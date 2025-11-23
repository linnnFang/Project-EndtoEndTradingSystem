import pandas as pd

class TrendMomentumStrategy:
    """
    Trend + Momentum Strategy supporting Long and Short positions.
    - Moving Average Crossover (trend direction)
    - Momentum filter (trend strength)
    """

    def __init__(self, short_window=20, long_window=60, mom_lookback=30):
        """
        Initialize strategy parameter settings.
        :param short_window: Short SMA lookback
        :param long_window: Long SMA lookback
        :param mom_lookback: Momentum lookback window
        """
        self.short_window = short_window
        self.long_window = long_window
        self.mom_lookback = mom_lookback

    def generate_signals(self, data: pd.DataFrame) -> pd.DataFrame:
        """
        Generate buy/sell signals based on trend + momentum.
        Returns a DataFrame including:
        SMA_short, SMA_long, momentum, combined_signal, position, side
        """
        
        df = data.copy()

        # Ensure datetime index
        if "Datetime" in df.columns:
            df["Datetime"] = pd.to_datetime(df["Datetime"])
            df.set_index("Datetime", inplace=True)

        df.sort_index(inplace=True)

        # Return calculation if missing
        if "Return" not in df.columns:
            df["Return"] = df["Close"].pct_change()

        # --- Indicators ---
        df["SMA_short"] = df["Close"].rolling(self.short_window).mean()
        df["SMA_long"] = df["Close"].rolling(self.long_window).mean()

        df["momentum"] = (
            (1 + df["Return"])
            .rolling(self.mom_lookback)
            .apply(lambda x: x.prod() - 1, raw=False)
        )

        # --- Signal generation ---
        df["combined_signal"] = 0  # default flat / neutral

        # Long entry condition
        df.loc[(df["SMA_short"] > df["SMA_long"]) & (df["momentum"] > 0), "combined_signal"] = 1
        
        # Short entry condition
        df.loc[(df["SMA_short"] < df["SMA_long"]) & (df["momentum"] < 0), "combined_signal"] = -1

        # --- Position (avoid look-ahead bias using shift) ---
        df["position"] = df["combined_signal"].shift(1).fillna(0).astype(int)

        # --- Trading Side (action labels) ---
        df["position_change"] = df["position"].diff().fillna(0)

        def trade_side(delta):
            if delta > 0:
                return "BUY"   # open long or reverse from short
            elif delta < 0:
                return "SELL"  # open short or close long
            return "HOLD"

        df["side"] = df["position_change"].apply(trade_side)

        # --- Strategy return computation ---
        df["strategy_return"] = df["position"] * df["Return"]
        df["equity_curve"] = (1 + df["strategy_return"]).cumprod()

        return df

