def format_change(value, is_percent=False):
    """Format price changes with proper sign and color"""
    if value is None:
        return '<span class="neutral">N/A</span>'
    try:
        value = float(value)
        sign = "+" if value >= 0 else ""
        value_str = f"{sign}{abs(value):.2f}{'%' if is_percent else ''}"
        color_class = "positive" if value >= 0 else "negative"
        return f'<span class="{color_class}">{value_str}</span>'
    except (TypeError, ValueError):
        return '<span class="neutral">N/A</span>'

def format_currency(value, symbol="₹"):
    """Format currency values"""
    if value is None:
        return "N/A"
    try:
        value = float(value)
        if abs(value) >= 1e9:
            return f"{symbol}{value/1e9:.2f}B"
        elif abs(value) >= 1e6:
            return f"{symbol}{value/1e6:.2f}M"
        return f"{symbol}{value:,.2f}"
    except (TypeError, ValueError):
        return "N/A"