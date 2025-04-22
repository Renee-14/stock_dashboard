from datetime import datetime, timedelta

# Default configuration
DEFAULT_TICKERS = ["RELIANCE.NS", "TCS.NS", "HDFCBANK.NS", "INFY.NS", "ICICIBANK.NS"]
DEFAULT_START_DATE = datetime.now() - timedelta(days=365)
DEFAULT_END_DATE = datetime.now()
CACHE_TTL = 3600  # 1 hour