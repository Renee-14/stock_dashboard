import plotly.express as px
import plotly.graph_objects as go
import pandas as pd

def create_candlestick_chart(data, title):
    fig = go.Figure(data=[go.Candlestick(
        x=data.index,
        open=data['Open'],
        high=data['High'],
        low=data['Low'],
        close=data['Close'],
        increasing_line_color='green',
        decreasing_line_color='red'
    )])
    fig.update_layout(
        title=title,
        xaxis_rangeslider_visible=False,
        height=400,
        margin=dict(l=20, r=20, t=40, b=20)
    )
    return fig

def create_performance_chart(data, stocks):
    fig = go.Figure()
    for symbol in stocks:
        df = data[symbol].reset_index() if len(stocks) > 1 else data.reset_index()
        prices = df['Close'].rename('Price')
        norm_prices = (prices / prices.iloc[0]) * 100
        fig.add_trace(go.Scatter(
            x=df['Date'],
            y=norm_prices,
            mode='lines',
            name=symbol
        ))
    fig.update_layout(
        title="Normalized Price Comparison (Base 100)",
        hovermode="x unified",
        height=400
    )
    return fig