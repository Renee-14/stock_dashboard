import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
import streamlit as st
from datetime import datetime
def create_price_chart(data, title, chart_type="line", live=True):
    """
    Create interactive price chart with live updating capabilities
    Args:
        data: DataFrame with historical data plus new points
        title: Chart title
        chart_type: 'line', 'candlestick', or 'area'
        live: Whether this is a live updating chart
    """
    fig = go.Figure()

    # Create the appropriate trace based on chart type
    if chart_type == "candlestick" and all(col in data.columns for col in ['Open', 'High', 'Low', 'Close']):
        fig.add_trace(go.Candlestick(
            x=data['Date'],
            open=data['Open'],
            high=data['High'],
            low=data['Low'],
            close=data['Close'],
            name='Price',
            increasing_line_color='#4CAF50',
            decreasing_line_color='#F44336'
        ))
    elif chart_type == "area":
        fig.add_trace(go.Scatter(
            x=data['Date'],
            y=data['Price'],
            fill='tozeroy',
            line=dict(color='#4CAF50'),
            name='Price',
            hovertemplate='%{x|%b %d %H:%M}<br>₹%{y:.2f}<extra></extra>'
        ))
    else:  # Default line chart
        fig.add_trace(go.Scatter(
            x=data['Date'],
            y=data['Price'],
            line=dict(color='#4CAF50', width=2),
            name='Price',
            hovertemplate='%{x|%b %d %H:%M}<br>₹%{y:.2f}<extra></extra>'
        ))

    # Common layout updates
    fig.update_layout(
        title=dict(
            text=title,
            font=dict(size=16, color='white', family='Arial')
        ),
        xaxis_title='Date',
        yaxis_title='Price (₹)',
        hovermode="x unified",
        template="plotly_dark",
        height=350,
        margin=dict(l=20, r=20, t=40, b=20),
        plot_bgcolor='#121212',
        paper_bgcolor='#121212',
        font=dict(color='white'),
        xaxis=dict(
            tickfont=dict(size=10),
            showgrid=True,
            gridcolor='rgba(255, 255, 255, 0.1)',
            autorange=True,  # Ensure live auto-scrolling
            fixedrange=False
        ),
        yaxis=dict(
            tickfont=dict(size=10),
            showgrid=True,
            gridcolor='rgba(255, 255, 255, 0.1)',
            autorange=True,  # Dynamic y-axis adjustment
            fixedrange=False
        )
    )

    # Special handling for live charts
    if live:
        fig.update_layout(
            transition={'duration': 300, 'easing': 'cubic-in-out'},  # Smooth transitions
            xaxis=dict(
                rangeslider=dict(visible=False),
                autorange=True  # Ensures x-axis auto-scrolls to latest points
            )
        )

    return fig


def create_live_chart(data, title, indicators=None):
    """
    Create optimized chart for live price updates
    Args:
        data: DataFrame with 'time' and 'price' columns
        title: Chart title
        indicators: List of indicators to show ('sma', 'ema')
    """
    if indicators is None:
        indicators = []

    fig = go.Figure()

    # Main price line
    fig.add_trace(go.Scatter(
        x=data['time'],
        y=data['price'],
        line=dict(color='#4CAF50', width=2),
        name='Price',
        hovertemplate='%{x|%H:%M:%S}<br>₹%{y:.2f}<extra></extra>'
    ))

    # Add indicators
    if 'sma' in indicators and len(data) > 20:
        fig.add_trace(go.Scatter(
            x=data['time'],
            y=data['price'].rolling(window=20).mean(),
            line=dict(color='#FFA500', width=1.5),
            name='SMA 20',
            hovertemplate='SMA 20: ₹%{y:.2f}<extra></extra>'
        ))

    if 'ema' in indicators and len(data) > 50:
        fig.add_trace(go.Scatter(
            x=data['time'],
            y=data['price'].ewm(span=50, adjust=False).mean(),
            line=dict(color='#00BFFF', width=1.5),
            name='EMA 50',
            hovertemplate='EMA 50: ₹%{y:.2f}<extra></extra>'
        ))

    fig.update_layout(
        title=dict(
            text=title,
            font=dict(size=16, color='white')
        ),
        xaxis_title='Time',
        yaxis_title='Price (₹)',
        template="plotly_dark",
        height=350,
        margin=dict(l=20, r=20, t=40, b=20),
        plot_bgcolor='#121212',
        paper_bgcolor='#121212',
        showlegend=True,
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1
        ),
        transition={'duration': 300}
    )

    return fig

import plotly.graph_objects as go

def create_comparison_chart(df, x_col, y_col, title):
    """Create comparison chart with CSS-protected labels and white text"""
    # Convert to percentages if needed
    df = df.copy()
    if df[y_col].max() <= 1:
        df[y_col] = df[y_col] * 100

    fig = go.Figure()

    # Add bars with absolute label protection
    fig.add_trace(go.Bar(
        x=df[x_col],
        y=df[y_col],
        marker_color=df[y_col].apply(lambda x: '#4CAF50' if x >= 0 else '#F44336'),
        width=0.6,
        text=df[y_col].apply(lambda x: f"{'+' if x >= 0 else ''}{x:.2f}%"),
        textposition='outside',
        textfont=dict(size=12, color='white'),  # White text for bar labels
        cliponaxis=False,
        insidetextanchor='middle'
    ))

    # Calculate dynamic padding
    y_pad = max(1, 0.3 * max(abs(df[y_col].max()), abs(df[y_col].min())))

    fig.update_layout(
        title=dict(
            text=title,
            x=0.5,
            xanchor='center',
            font=dict(color='white')  # White title
        ),
        plot_bgcolor='rgba(0,0,0,0)',  # Transparent background
        paper_bgcolor='rgba(0,0,0,0)',
        xaxis=dict(
            showgrid=False,
            tickfont=dict(color='white'),  # White x-axis tick labels
            titlefont=dict(color='white')  # White x-axis title (if any)
        ),
        yaxis=dict(
            title='Change (%)',
            titlefont=dict(color='white'),  # White y-axis title
            tickfont=dict(color='white'),  # White y-axis tick labels
            range=[df[y_col].min() - y_pad, df[y_col].max() + y_pad],
            gridcolor='rgba(255,255,255,0.1)'
        ),
        margin=dict(t=80, b=120),  # Extra bottom margin
        bargap=0.4,
        font=dict(color='white')  # Global white text (fallback)
    )

    return fig

def display_comparison_table(df_comparison):
    """Style the comparison dataframe with dark theme"""
    st.markdown("""
        <style>
        .stDataFrame {
            background-color: #121212 !important;
            color: white !important;
            
        }
        .stDataFrame thead {
            background-color: #1e1e1e !important;
        }
        .stDataFrame th {
            color: white !important;
            font-weight: bold !important;
        }
        .stDataFrame td {
            color: white !important;
            background-color: #121212 !important;
        }
        .stDataFrame tr:nth-child(even) {
            background-color: #1e1e1e !important;
        }
        .stDataFrame tr:hover {
            background-color: #2a2a2a !important;
        }
        </style>
    """, unsafe_allow_html=True)

    # Format numbers and display
    formatted_df = df_comparison.style.format({
        'Price': '₹{:,.2f}',
        'Change (%)': '{:+.2f}%',
        'Market Cap': '₹{:,.0f}',
        'Volume': '{:,.0f}',
        'PE Ratio': '{:.2f}'
    })

    st.dataframe(
        formatted_df,
        height=min(300, 35 * len(df_comparison)),
        use_container_width=True
    )