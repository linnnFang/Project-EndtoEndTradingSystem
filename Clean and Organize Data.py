import pandas as pd

# Load data
data = pd.read_csv("TSLA_intraday_1m.csv")
data = pd.read_csv("TSLA_intraday_1m.csv", skiprows=[1])

# Remove missing values
data.dropna(inplace=True)

# Remove duplicate timestamps
data.drop_duplicates(subset="Datetime", keep="first", inplace=True)

# Convert Datetime to datetime format
data['Datetime'] = pd.to_datetime(data['Datetime'])

# Set as index
data.set_index('Datetime', inplace=True)

# Sort chronologically
data.sort_index(inplace=True)

# Add features
data['Return'] = data['Close'].pct_change()
data['SMA_5'] = data['Close'].rolling(5).mean()
data['SMA_20'] = data['Close'].rolling(20).mean()

# Save cleaned file
data.to_csv("TSLA_intraday_1m_clean.csv")

print("Cleaned data saved to TSLA_intraday_1m_clean.csv")
print(data.head())