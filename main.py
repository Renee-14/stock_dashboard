import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime, timedelta
import time
from pytz import timezone
from modules.ui_components import setup_page_config, create_stock_card, display_metrics
from modules.data_handler import get_stock_data, get_current_info, get_stock_metrics, get_live_price, get_market_status
from modules.charts import create_price_chart, create_comparison_chart, create_live_chart
from modules.config import DEFAULT_TICKERS

# Page setup
setup_page_config()

# Enhanced CSS for smooth transitions
st.markdown("""
    <style>
    html, body, [class*="css"] {
        font-size: 12px !important;
        background-color: #0e1117;
        color: #f0f0f0;
    }
    .block-container {
        padding: 0.5rem 0.5rem;
        transition: opacity 0.3s ease;
    }
    .main {
        padding-top: 0.5rem;
    }
    .stock-card {
        border-radius: 6px;
        padding: 8px;
        background-color: #1c1c1e;
        box-shadow: 0 1px 2px rgba(0,0,0,0.2);
        margin-bottom: 8px;
        transition: all 0.3s ease;
    }
    .stock-card:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 6px rgba(0,0,0,0.3);
    }
    .positive {
        color: #4CAF50;
        font-weight: 600;
        font-size: 11px;
    }
    .negative {
        color: #F44336;
        font-weight: 600;
        font-size: 11px;
    }
    .neutral {
        color: #AAAAAA;
    }
    .header {
        font-size: 16px;
        font-weight: 600;
        margin-bottom: 8px;
        color: #ffffff;
    }
    .ticker-header {
        font-size: 12px;
        font-weight: 600;
        margin-bottom: 2px;
    }
    .price {
        font-size: 18px;
        font-weight: 600;
        margin-bottom: 1px;
    }
    .change {
        font-size: 11px;
    }
    .live-badge {
        background-color: #ff4b4b;
        color: white;
        padding: 2px 8px;
        border-radius: 12px;
        font-size: 10px;
        font-weight: bold;
        margin-left: 8px;
        display: inline-block;
        animation: pulse 1.5s infinite;
    }
    @keyframes pulse {
        0% { transform: scale(1); }
        50% { transform: scale(1.05); }
        100% { transform: scale(1); }
    }
    .stButton>button {
        font-size: 12px !important;
        padding: 0.25rem 0.6rem !important;
    }
    .stSelectbox label, .stMultiSelect label, .stTextInput label, .stDateInput label {
        font-size: 12px !important;
    }
    .element-container .markdown-text-container {
        font-size: 12px !important;
    }
    .stMarkdown h1, .stMarkdown h2, .stMarkdown h3 {
        font-size: 32px !important;
        font-weight: 800 !important;
        margin-top: 2px;
        color: #d8ffe5 !important;
    }
    
    </style>
""", unsafe_allow_html=True)

# Initialize session state for smooth updates
if 'price_data' not in st.session_state:
    st.session_state.price_data = {}
    st.session_state.last_update = datetime.now()

# Sidebar
ALL_TICKERS = [
    "RELIANCE.NS", "TCS.NS", "HDFCBANK.NS", "INFY.NS", "ICICIBANK.NS", "LT.NS", "SBIN.NS",
    "ITC.NS", "AXISBANK.NS", "KOTAKBANK.NS", "WIPRO.NS", "ONGC.NS", "BHARTIARTL.NS", "BAJFINANCE.NS"
]

# Get market status
is_market_open, market_status_text = get_market_status()

st.sidebar.markdown(f"""
    <div style='display: flex; align-items: center; margin-bottom: 15px;'>
        <h3 style='margin: 0;'>Stock Options</h3>
        <span class='live-badge'>{market_status_text}</span>
    </div>
""", unsafe_allow_html=True)

additional_tickers = st.sidebar.multiselect("Popular Stocks",
                                            options=[t for t in ALL_TICKERS if t not in DEFAULT_TICKERS])
manual_input = st.sidebar.text_input("Custom Tickers (comma-separated)", placeholder="e.g. BHEL.NS, ADANIENT.NS")
custom_tickers = [t.strip().upper() for t in manual_input.split(",") if t.strip()]
ticker_list = DEFAULT_TICKERS + additional_tickers + custom_tickers

# Refresh control
refresh_rate = st.sidebar.slider("Refresh rate (seconds)", 1, 60, 5, disabled=not is_market_open)

start_date = st.sidebar.date_input("Start Date", datetime.today() - timedelta(days=365))
end_date = st.sidebar.date_input("End Date", datetime.today())
selected_ticker = st.sidebar.selectbox("Detailed View", ticker_list)

# Main
st.markdown(f"""
    <div style='
        font-size: 40px;
        color: #d8eaff;
        font-weight: 800;
        margin-top: 20px;
        margin-bottom: 1px;
    '>
        Indian Stock Market Dashboard
    </div>
    <div style='font-size: 12px; color: #aaa; margin-bottom: 10px;'>
        Last updated: {datetime.now().strftime("%d %b %Y %H:%M:%S")} IST
    </div>
""", unsafe_allow_html=True)

st.markdown("---")

# Placeholders for live content
live_cards_placeholder = st.empty()
main_content_placeholder = st.empty()


def update_live_data():
    """Update live price data without full refresh"""
    current_time = datetime.now()
    if (current_time - st.session_state.last_update).seconds >= refresh_rate:
        new_data = {}
        for ticker in ticker_list:
            live_data = get_live_price(ticker)
            if live_data:
                new_data[ticker] = {
                    'price': live_data['price'],
                    'change': live_data.get('change', 0),
                    'pct_change': live_data.get('pct_change', 0),
                    'time': live_data['time']
                }

        if new_data:
            st.session_state.price_data = new_data
            st.session_state.last_update = current_time


def display_main_content():
    """Display the main content with historical data"""
    try:
        stock_data = get_stock_data(ticker_list, start_date, end_date)

        if stock_data is not None:
            with main_content_placeholder.container():
                # Historical charts and metrics
                col1, col2 = st.columns([7, 3])

                with col1:
                    st.markdown(f"#### {selected_ticker} Price History")
                    try:
                        df = (
                            stock_data.reset_index()[['Date', 'Close']].rename(columns={'Close': 'Price'})
                            if len(ticker_list) == 1
                            else stock_data[selected_ticker].reset_index()[['Date', 'Close']].rename(
                                columns={'Close': 'Price'})
                        )
                        st.plotly_chart(
                            create_price_chart(df, f"{selected_ticker} Price History"),
                            use_container_width=True
                        )
                    except Exception as e:
                        st.error(f"Error displaying chart for {selected_ticker}: {str(e)}")

                with col2:
                    st.markdown("#### Metrics")
                    try:
                        metrics = get_stock_metrics(selected_ticker)
                        if metrics:
                            display_metrics(metrics)
                        else:
                            st.warning("No metrics available.")
                    except Exception as e:
                        st.warning(f"Error loading metrics: {str(e)}")

                # Comparison section
                st.markdown("---")
                st.markdown("### Comparison")
                comparison_data = []

                for ticker in ticker_list:
                    try:
                        price_data = st.session_state.price_data.get(ticker, {})
                        metrics = get_stock_metrics(ticker)
                        if price_data and metrics:
                            comparison_data.append({
                                'Symbol': ticker,
                                'Price': price_data['price'],
                                'Change (%)': price_data['pct_change'],
                                'Market Cap': metrics['Market Cap'],
                                'PE Ratio': metrics['PE Ratio'],
                                'Volume': metrics['Volume']
                            })
                    except Exception as e:
                        st.warning(f"Error fetching data for {ticker}: {str(e)}")

                if comparison_data:
                    df_comparison = pd.DataFrame(comparison_data)

                    fig_table = go.Figure(data=[go.Table(
                        header=dict(
                            values=list(df_comparison.columns),
                            fill_color='#1e1e1e',
                            font=dict(color='white', size=12),
                            align='left',
                            height=28
                        ),
                        cells=dict(
                            values=[df_comparison[col] for col in df_comparison.columns],
                            fill_color='#0e1117',
                            font=dict(color='white', size=11),
                            align='left',
                            height=26
                        )
                    )])

                    fig_table.update_layout(
                        paper_bgcolor='#0e1117',
                        plot_bgcolor='#0e1117',
                        margin=dict(l=0, r=0, t=0, b=0),
                        height=min(40 + 30 * len(df_comparison), 500)
                    )

                    st.plotly_chart(fig_table, use_container_width=True)

                    st.plotly_chart(
                        create_comparison_chart(df_comparison, 'Symbol', 'Change (%)', "Daily Change"),
                        use_container_width=True,
                        theme = None
                    )
                else:
                    st.warning("No comparison data available.")
    except Exception as e:
        st.error(f"An error occurred: {str(e)}")


# Main loop
while True:
    try:
        # Update live data
        update_live_data()

        # Display live price cards
        with live_cards_placeholder.container():
            st.markdown(f"""
                            <div style='display: flex; align-items: center; margin-bottom: 8px;'>
                                <div class="header" style='margin: 0;'>Live Stock Summary</div>
                                <span class='live-badge'>LIVE</span>
                            </div>
                        """, unsafe_allow_html=True)
            cols = st.columns(len(ticker_list))

            for i, ticker in enumerate(ticker_list):
                price_data = st.session_state.price_data.get(ticker)
                if price_data:
                    with cols[i]:
                        create_stock_card(ticker, price_data['price'], price_data['change'], price_data['pct_change'])

        # Display main content (historical data)
        display_main_content()

        # Small delay to prevent high CPU usage
        time.sleep(refresh_rate)

    except Exception as e:
        st.error(f"Update error: {str(e)}")
        time.sleep(10)