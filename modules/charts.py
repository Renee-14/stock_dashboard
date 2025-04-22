import plotly.express as px
import pandas as pd
import streamlit as st

def create_price_chart(data, title):
    """Create a line chart for price history"""
    fig = px.line(
        data,
        x='Date',
        y='Price',
        title=title,
        labels={'Price': 'Price (Indian Rupees)', 'Date': 'Date'}
    )

    # Update layout for dark mode and compactness
    fig.update_layout(
        hovermode="x unified",
        showlegend=False,
        height=350,  # Shrink height for better fit
        margin=dict(l=20, r=20, t=40, b=20),
        plot_bgcolor='#121212',  # Dark background
        paper_bgcolor='#121212',  # Dark background for paper
        font=dict(color='white'),  # Light font color
        title_font=dict(size=16, color='white', family='Arial'),  # Title font adjustments
        xaxis=dict(
            tickfont=dict(size=10, color='white'),
            showgrid=True,
            gridcolor='rgba(255, 255, 255, 0.1)',  # Light grid lines
        ),
        yaxis=dict(
            tickfont=dict(size=10, color='white'),
            showgrid=True,
            gridcolor='rgba(255, 255, 255, 0.1)',  # Light grid lines
        )
    )
    return fig






def create_comparison_chart(df, x_col, y_col, title):
    """Create a comparison bar chart"""
    fig = px.bar(
        df,
        x=x_col,
        y=y_col,
        title=title,
        color=y_col,
        color_continuous_scale=['red', 'green']
    )

    # Update layout for dark mode and compactness
    fig.update_layout(
        height=350,  # Shrink height for better fit
        plot_bgcolor='#121212',  # Dark background for the plot
        paper_bgcolor='#121212',  # Dark background for the paper
        font=dict(color='white'),  # Light font color
        title_font=dict(size=16, color='white', family='Arial'),  # Title font adjustments
        xaxis=dict(
            tickfont=dict(size=10, color='white'),
            showgrid=True,
            gridcolor='rgba(255, 255, 255, 0.1)',  # Light grid lines
            zerolinecolor='rgba(255, 255, 255, 0.1)',  # Line on x-axis at zero
        ),
        yaxis=dict(
            tickfont=dict(size=10, color='white'),
            showgrid=True,
            gridcolor='rgba(255, 255, 255, 0.1)',  # Light grid lines
            zerolinecolor='rgba(255, 255, 255, 0.1)',  # Line on y-axis at zero
        ),
        barmode='group',  # Group bars for comparison
        showlegend=False,  # Hide legend to save space
        margin=dict(l=20, r=20, t=40, b=20),  # Adjust margins for better fit within rows
    )

    return fig



def display_comparison_table(df_comparison):
    """Style the comparison dataframe with a black table fill"""

    # Apply CSS styling for dark mode and black table rows
    st.markdown(
        """
        <style>
        .stDataFrame {
            background-color: #121212;  /* Black background for the table */
            color: white;
        }
        .stDataFrame thead {
            background-color: #1e1e1e;  /* Darker header background */
        }
        .stDataFrame th {
            color: white;
            font-weight: bold;
        }
        .stDataFrame td {
            color: white;
        }
        .stDataFrame tbody tr:nth-child(even) {
            background-color: #1e1e1e;  /* Dark alternating row colors */
        }
        .stDataFrame tbody tr:nth-child(odd) {
            background-color: #121212;  /* Lighter alternating row colors */
        }
        </style>
        """,
        unsafe_allow_html=True
    )

    # Remove any empty rows in the dataframe
    df_comparison = df_comparison.dropna(how="all")  # Drop rows where all values are NaN

    # Limiting the table height and adding scroll if too long
    st.dataframe(
        df_comparison.style.format({
            'Price': '₹{:.2f}',
            'Change (%)': '{:.2f}%',
            'Market Cap': '₹{:,.0f}',
            'Volume': '{:,.0f}'
        }, na_rep="N/A"),
        height=100,  # Adjust height of table to limit rows displayed
        use_container_width=True
    )



