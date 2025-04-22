import yfinance as yf
import pandas as pd
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)

INDIAN_INDICES = {
    "NIFTY 50": "^NSEI",
    "SENSEX": "^BSESN",
    "NIFTY BANK": "^NSEBANK"
}

def get_live_price(ticker):
    try:
        stock = yf.Ticker(ticker)
        data = stock.history(period="1d", interval="5m")
        if not data.empty:
            return {
                'current': data['Close'].iloc[-1],
                'open': data['Open'].iloc[-1],
                'high': data['High'].iloc[-1],
                'low': data['Low'].iloc[-1],
                'volume': data['Volume'].iloc[-1]
            }
        return None
    except Exception as e:
        logger.error(f"Error fetching live price for {ticker}: {str(e)}")
        return None

def get_historical_data(ticker, period="1y"):
    try:
        return yf.Ticker(ticker).history(period=period)
    except Exception as e:
        logger.error(f"Error fetching historical data for {ticker}: {str(e)}")
        return None

def get_stock_info(ticker):
    try:
        stock = yf.Ticker(ticker)
        return {
            'info': stock.info,
            'recommendations': stock.recommendations,
            'dividends': stock.dividends
        }
    except Exception as e:
        logger.error(f"Error fetching info for {ticker}: {str(e)}")
        return None

def get_index_data():
    indices = {}
    for name, symbol in INDIAN_INDICES.items():
        try:
            data = yf.Ticker(symbol).history(period="1d")
            if not data.empty:
                current = data['Close'].iloc[-1]
                prev_close = data['Close'].iloc[-2] if len(data) > 1 else current
                change = current - prev_close
                pct_change = (change / prev_close) * 100
                indices[name] = {
                    'current': current,
                    'change': change,
                    'pct_change': pct_change
                }
        except Exception as e:
            logger.error(f"Error fetching index {name}: {str(e)}")
    return indices