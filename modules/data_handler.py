import yfinance as yf
import pandas as pd
from datetime import datetime
import streamlit as st
from modules.config import CACHE_TTL

@st.cache_data(ttl=CACHE_TTL)
def get_stock_data(tickers, start_date, end_date):
    """Fetch stock data for multiple tickers"""
    try:
        return yf.download(tickers, start=start_date, end=end_date, group_by='ticker')
    except Exception as e:
        st.error(f"Error fetching data: {str(e)}")
        return None

def get_current_info(ticker):
    """Get current price and daily change for a ticker"""
    try:
        stock = yf.Ticker(ticker)
        hist = stock.history(period="1d")
        if not hist.empty:
            current = hist['Close'].iloc[-1]
            previous = hist['Open'].iloc[-1]
            change = current - previous
            percent_change = (change / previous) * 100
            return current, change, percent_change
        return None, None, None
    except Exception as e:
        st.error(f"Error getting info for {ticker}: {str(e)}")
        return None, None, None

def get_stock_metrics(ticker):
    """Get fundamental metrics for a stock"""
    try:
        stock = yf.Ticker(ticker)
        info = stock.info
        return {
            "52 Week High": info.get('fiftyTwoWeekHigh', 'N/A'),
            "52 Week Low": info.get('fiftyTwoWeekLow', 'N/A'),
            "PE Ratio": info.get('trailingPE', 'N/A'),
            "Market Cap": info.get('marketCap', 'N/A'),
            "Volume": info.get('volume', 'N/A'),
            "Beta": info.get('beta', 'N/A')
        }
    except Exception as e:
        st.error(f"Error fetching metrics: {str(e)}")
        return None