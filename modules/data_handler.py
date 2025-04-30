import yfinance as yf
import pandas as pd
from datetime import datetime, timedelta
import time
from pytz import timezone
import streamlit as st
from modules.config import CACHE_TTL, DEFAULT_TICKERS


# Cache stock data with automatic refresh
@st.cache_data(ttl=CACHE_TTL, show_spinner=False)
def get_stock_data(tickers, start_date, end_date, interval='1d'):
    """Fetch stock data for multiple tickers with enhanced error handling"""
    try:
        data = yf.download(
            tickers if isinstance(tickers, str) else ' '.join(tickers),
            start=start_date,
            end=end_date,
            interval=interval,
            group_by='ticker',
            progress=False,
            threads=True
        )
        return data if not data.empty else None
    except Exception as e:
        st.error(f"Error fetching data for {tickers}: {str(e)}")
        return None


def get_current_info(ticker):
    """Get real-time price and change with fallback to last close"""
    try:
        # First try 1m interval for most recent price
        stock = yf.Ticker(ticker)
        hist = stock.history(period='1d', interval='1m')

        if not hist.empty and len(hist) > 1:
            current = hist['Close'].iloc[-1]
            prev = hist['Close'].iloc[-2]
            change = current - prev
            pct_change = (change / prev) * 100
            return current, change, pct_change

        # Fallback to daily data if minute data unavailable
        hist = stock.history(period='2d')
        if not hist.empty:
            current = hist['Close'].iloc[-1]
            prev = hist['Close'].iloc[-2] if len(hist) > 1 else hist['Open'].iloc[-1]
            change = current - prev
            pct_change = (change / prev) * 100
            return current, change, pct_change

        return None, None, None
    except Exception as e:
        st.warning(f"Couldn't fetch current price for {ticker}: {str(e)}")
        return None, None, None


def get_live_price(ticker):
    """Get real-time price with minimal delay"""
    try:
        stock = yf.Ticker(ticker)
        hist = stock.history(period='1d', interval='1m', prepost=True)

        if not hist.empty:
            return {
                'price': hist['Close'].iloc[-1],
                'time': hist.index[-1].to_pydatetime(),
                'change': hist['Close'].iloc[-1] - hist['Close'].iloc[-2] if len(hist) > 1 else 0,
                'pct_change': ((hist['Close'].iloc[-1] - hist['Close'].iloc[-2]) / hist['Close'].iloc[-2]) * 100 if len(
                    hist) > 1 else 0,
                'volume': hist['Volume'].iloc[-1]
            }
        return None
    except Exception as e:
        st.warning(f"Error getting live price for {ticker}: {str(e)}")
        return None


def get_market_status():
    """Check if Indian market is currently open with precise timing"""
    ist = timezone('Asia/Kolkata')
    now = datetime.now(ist)
    opening_time = now.replace(hour=9, minute=15, second=0, microsecond=0)
    closing_time = now.replace(hour=15, minute=30, second=0, microsecond=0)

    if now.weekday() >= 5:  # Weekend
        return {'is_open': False, 'status': "Closed (Weekend)"}
    elif now < opening_time:
        time_left = opening_time - now
        return {
            'is_open': False,
            'status': f"Opens in {time_left.seconds // 3600}h {(time_left.seconds // 60) % 60}m"
        }
    elif now > closing_time:
        return {'is_open': False, 'status': "Closed"}
    else:
        time_left = closing_time - now
        return {
            'is_open': True,
            'status': f"Open ({time_left.seconds // 3600}h {(time_left.seconds // 60) % 60}m left)"
        }


def get_stock_metrics(ticker):
    """Get comprehensive fundamental metrics with fallback values"""
    try:
        stock = yf.Ticker(ticker)
        info = stock.info

        # Calculate additional metrics
        hist = stock.history(period='1y')
        fifty_two_week_high = hist['High'].max() if not hist.empty else None
        fifty_two_week_low = hist['Low'].min() if not hist.empty else None

        return {
            "Current Price": info.get('currentPrice', info.get('regularMarketPrice', 'N/A')),
            "52 Week High": fifty_two_week_high or info.get('fiftyTwoWeekHigh', 'N/A'),
            "52 Week Low": fifty_two_week_low or info.get('fiftyTwoWeekLow', 'N/A'),
            "PE Ratio": info.get('trailingPE', info.get('forwardPE', 'N/A')),
            "Market Cap": format_market_cap(info.get('marketCap')),
            "Volume": format_volume(info.get('volume', info.get('averageVolume', 'N/A'))),
            "Beta": info.get('beta', 'N/A'),
            "Dividend Yield": f"{info.get('dividendYield', 0) * 100:.2f}%" if info.get('dividendYield') else 'N/A',
            "Sector": info.get('sector', 'N/A'),
            "Industry": info.get('industry', 'N/A')
        }
    except Exception as e:
        st.warning(f"Error fetching metrics for {ticker}: {str(e)}")
        return None


def format_market_cap(market_cap):
    """Format market cap into readable string"""
    if not market_cap or market_cap == 'N/A':
        return 'N/A'

    if market_cap >= 1e12:
        return f"₹{market_cap / 1e12:.2f}T"
    elif market_cap >= 1e9:
        return f"₹{market_cap / 1e9:.2f}B"
    elif market_cap >= 1e6:
        return f"₹{market_cap / 1e6:.2f}M"
    return f"₹{market_cap:,.0f}"


def format_volume(volume):
    """Format volume into readable string"""
    if not volume or volume == 'N/A':
        return 'N/A'
    return f"{volume:,.0f}"