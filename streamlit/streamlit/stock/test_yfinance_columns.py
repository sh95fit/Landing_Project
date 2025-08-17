import yfinance as yf
import pandas as pd

# Test with a popular stock
ticker = 'AAPL'
data = yf.download(ticker, start='2024-01-01', end='2024-01-10')

print("Available columns:")
print(data.columns.tolist())
print("\nData shape:", data.shape)
print("\nFirst few rows:")
print(data.head())


