import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime, timedelta
from modules.ui_components import setup_page_config, create_stock_card, display_metrics
from modules.data_handler import get_stock_data, get_current_info, get_stock_metrics
from modules.charts import create_price_chart, create_comparison_chart
from modules.config import DEFAULT_TICKERS

# Page setup
setup_page_config()

# Custom compact dark theme styling
st.markdown("""
    <style>
    html, body, [class*="css"] {
        font-size: 12px !important;
        background-color: #0e1117;
        color: #f0f0f0;
    }
    .block-container {
        padding: 0.5rem 0.5rem;
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

# Sidebar
ALL_TICKERS = [
    "RELIANCE.NS", "TCS.NS", "HDFCBANK.NS", "INFY.NS", "ICICIBANK.NS", "LT.NS", "SBIN.NS",
    "ITC.NS", "AXISBANK.NS", "KOTAKBANK.NS", "WIPRO.NS", "ONGC.NS", "BHARTIARTL.NS", "BAJFINANCE.NS"
]

st.sidebar.markdown("### Stock Options")
additional_tickers = st.sidebar.multiselect("Popular Stocks",
                                            options=[t for t in ALL_TICKERS if t not in DEFAULT_TICKERS])
manual_input = st.sidebar.text_input("Custom Tickers (comma-separated)", placeholder="e.g. BHEL.NS, ADANIENT.NS")
custom_tickers = [t.strip().upper() for t in manual_input.split(",") if t.strip()]
ticker_list = DEFAULT_TICKERS + additional_tickers + custom_tickers

start_date = st.sidebar.date_input("Start Date", datetime.today() - timedelta(days=365))
end_date = st.sidebar.date_input("End Date", datetime.today())
selected_ticker = st.sidebar.selectbox("Detailed View", ticker_list)

# Main
st.markdown("""
    <div style='
        font-size: 40px;
        color: #d8eaff;
        font-weight: 800;
        margin-top: 20px;
        margin-bottom: 1px;
    '>
        Indian Stock Market Dashboard
    </div>
""", unsafe_allow_html=True)

st.markdown("---")

try:
    stock_data = get_stock_data(ticker_list, start_date, end_date)

    if stock_data is not None:
        st.markdown("#### Stock Summary")
        cols = st.columns(len(ticker_list))

        for i, ticker in enumerate(ticker_list):
            try:
                current_price, change, pct_change = get_current_info(ticker)
                with cols[i]:
                    create_stock_card(ticker, current_price, change, pct_change)
            except Exception as e:
                st.warning(f"Could not load card for {ticker}: {e}")

        st.markdown("---")
        col1, col2 = st.columns([7, 3])

        with col1:
            st.markdown(f"#### {selected_ticker} Price History")
            try:
                df = (
                    stock_data.reset_index()[['Date', 'Close']].rename(columns={'Close': 'Price'})
                    if len(ticker_list) == 1
                    else stock_data[selected_ticker].reset_index()[['Date', 'Close']].rename(columns={'Close': 'Price'})
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

        st.markdown("---")
        st.markdown("#### Comparison")
        comparison_data = []

        for ticker in ticker_list:
            try:
                current_price, _, pct_change = get_current_info(ticker)
                metrics = get_stock_metrics(ticker)
                if current_price is not None and metrics:
                    comparison_data.append({
                        'Symbol': ticker,
                        'Price': current_price,
                        'Change (%)': pct_change,
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
                use_container_width=True
            )
        else:
            st.warning("No comparison data available.")
except Exception as e:
    st.error(f"An error occurred: {str(e)}")
