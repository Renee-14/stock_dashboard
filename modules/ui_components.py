from datetime import datetime, timedelta

import streamlit as st
from modules.formatter import format_change, format_currency

DEFAULT_START_DATE = datetime.now() - timedelta(days=365)  # 1 year ago
DEFAULT_END_DATE = datetime.now()
def setup_page_config():
    """Configure the Streamlit page settings"""
    st.set_page_config(
        page_title="Stock Market Dashboard",
        page_icon="📈",
        layout="wide",
        initial_sidebar_state="expanded"
    )


def create_stock_card(ticker, current_price, change, pct_change):
    """Create a stock summary card"""
    current_display = format_currency(current_price, '₹') if current_price is not None else "N/A"
    change_display = format_change(change)
    pct_change_display = format_change(pct_change, is_percent=True)

    st.markdown(f"""
    <div class="stock-card">
        <h3 class="ticker-header">{ticker}</h3>
        <div class="price">{current_display}</div>
        <div class="change">{change_display} ({pct_change_display})</div>
    </div>
    """, unsafe_allow_html=True)


def create_sidebar(tickers):
    """Create the sidebar controls"""
    with st.sidebar:
        st.title("Dashboard Settings")
        tickers_input = st.text_input(
            "Enter stock symbols (comma separated)",
            ",".join(tickers)
        )
        start_date = st.date_input("Start date", DEFAULT_START_DATE)
        end_date = st.date_input("End date", DEFAULT_END_DATE)
        selected_ticker = st.selectbox(
            "Select stock for detailed view",
            tickers
        )
    return tickers_input, start_date, end_date, selected_ticker


def display_metrics(metrics):
    """Display performance metrics"""
    if metrics:
        for metric, value in metrics.items():
            if metric in ['Market Cap', 'Volume']:
                value = format_currency(value) if isinstance(value, (int, float)) else value
            st.metric(label=metric, value=value)