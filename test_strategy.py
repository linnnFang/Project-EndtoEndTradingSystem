# test_strategy.py
# --------------------------------------------------
# This is a simple unit-style test for TrendMomentumStrategy
# It loads cleaned intraday data, applies the strategy,
# prints basic outputs, and checks if signals are generated.

import pandas as pd
from TrendMomentumStrategy import TrendMomentumStrategy  # make sure file name matches

def test_strategy():
    # Load sample clean data
    df = pd.read_csv("TSLA_intraday_1m_clean.csv")

    print("\n--- Loaded Data ---")
    print(df.head())

    # Initialize strategy with sample parameters
    strategy = TrendMomentumStrategy(
        short_window=20,
        long_window=60,
        mom_lookback=30
    )

    # Generate strategy signals
    result = strategy.generate_signals(df)

    print("\n--- Strategy Output (Head) ---")
    print(result[["Close", "SMA_short", "SMA_long", "momentum",
                  "combined_signal", "position", "side"]].head(20))

    print("\n--- Strategy Output (Tail) ---")
    print(result[["Close", "combined_signal", "position", "side"]].tail(10))

    # Basic logic verification
    long_signals = (result["combined_signal"] == 1).sum()
    short_signals = (result["combined_signal"] == -1).sum()

    print("\n--- Signal Summary ---")
    print(f"Long signals generated: {long_signals}")
    print(f"Short signals generated: {short_signals}")

    # Save output result
    result.to_csv("strategy_test_output.csv")
    print("\nOutput saved to strategy_test_output.csv")

if __name__ == "__main__":
    test_strategy()
