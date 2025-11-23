# Step 1: Download Intraday Market Data (Equity Example)
# ----------------------------------------------
# This script downloads 1-minute intraday historical data for AAPL
# and saves it locally into a CSV file with columns:
# Datetime, Open, High, Low, Close, Volume

import yfinance as yf

# Parameters
ticker = "TSLA"            # stock ticker symbol
period = "7d"              # past 7 days
interval = "1m"            # 1-minute bars

# Download data
data = yf.download(
    tickers=ticker,
    period=period,
    interval=interval
)

# Reset index so Datetime becomes a column instead of index
data = data.reset_index()

# Save to CSV
filename = f"{ticker}_intraday_{interval}.csv"
data.to_csv(filename, index=False)

print(f"Data downloaded and saved to: {filename}")
print(data.head())
