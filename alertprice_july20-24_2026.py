import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime, timedelta
import requests
import time

# Page configuration
st.set_page_config(
    page_title="NSE Stock Alert Dashboard",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
    <style>
        .stAlert {
            padding: 1rem;
            border-radius: 10px;
        }
        .stock-card {
            background: #f8f9fa;
            padding: 1rem;
            border-radius: 10px;
            margin: 0.5rem 0;
            border-left: 4px solid #ff6b6b;
        }
        .stock-card-positive {
            border-left-color: #51cf66;
        }
        .stock-card-negative {
            border-left-color: #ff6b6b;
        }
        .disclaimer {
            background: #fff3cd;
            padding: 1rem;
            border-radius: 10px;
            border: 1px solid #ffc107;
            margin: 1rem 0;
        }
        .price-up {
            color: #51cf66;
            font-weight: bold;
        }
        .price-down {
            color: #ff6b6b;
            font-weight: bold;
        }
        .metric-card {
            background: white;
            padding: 1rem;
            border-radius: 10px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            text-align: center;
        }
        h1, h2, h3 {
            color: #1a1a2e;
        }
        .stTabs [data-baseweb="tab-list"] {
            gap: 2px;
        }
        .stTabs [data-baseweb="tab"] {
            border-radius: 4px 4px 0 0;
            padding: 10px 20px;
            background-color: #f0f2f6;
        }
        .stTabs [aria-selected="true"] {
            background-color: #1a1a2e;
            color: white;
        }
    </style>
""", unsafe_allow_html=True)

# App title and description
st.title("📊 NSE Stock Alert Dashboard")
st.markdown("### Live Price Monitoring & Alerts")

# Disclaimer
st.markdown("""
    <div class="disclaimer">
        ⚠️ <strong>DISCLAIMER:</strong> This application is for <strong>educational and informational purposes only</strong>. 
        It provides price observations and alert notifications. <strong>NOT</strong> a buy/sell recommendation. 
        Please consult with a qualified financial advisor before making any investment decisions.
    </div>
""", unsafe_allow_html=True)

# Define stock lists
STOCKS = [
    "IRCTC.NS", "SIGACHI.NS", "CASTROLIND.NS", "ZEEL.NS", "CYIENT.NS",
    "AVANTIFEED.NS", "IEX.NS", "GRAPHITE.NS", "NUVOCO.NS", "HEG.NS",
    "IDBI.NS", "SBICARD.NS", "TATATECH.NS", "TITAGARH.NS", "LGEINDIA.NS"
]

NIFTY_50 = ["BPCL.NS", "TCS.NS"]

ALL_STOCKS = STOCKS + NIFTY_50

# Date range for alerts (20-24 July 2026)
ALERT_START = datetime(2026, 6, 29)
ALERT_END = datetime(2026, 7, 24)

# Function to fetch stock data with error handling
@st.cache_data(ttl=60)
def fetch_stock_data(symbol):
    """Fetch stock data from yfinance with error handling"""
    try:
        stock = yf.Ticker(symbol)
        # Get current price
        current_data = stock.history(period="1d")
        if current_data.empty:
            return None
        
        # Get historical data for alert period
        hist_data = stock.history(start=ALERT_START, end=ALERT_END + timedelta(days=1))
        
        info = stock.info
        return {
            "symbol": symbol.replace(".NS", ""),
            "current_price": current_data['Close'].iloc[-1],
            "previous_close": current_data['Close'].iloc[-2] if len(current_data) > 1 else None,
            "volume": current_data['Volume'].iloc[-1],
            "high": current_data['High'].iloc[-1],
            "low": current_data['Low'].iloc[-1],
            "historical": hist_data,
            "info": info
        }
    except Exception as e:
        st.error(f"Error fetching {symbol}: {str(e)}")
        return None

# Function to calculate alert signals
def calculate_alerts(data):
    """Calculate price alerts based on 13-17 July 2026 data"""
    if data is None or data['historical'].empty:
        return None
    
    hist = data['historical']
    if len(hist) < 2:
        return None
    
    # Calculate key metrics
    start_price = hist['Close'].iloc[0]
    end_price = hist['Close'].iloc[-1]
    max_price = hist['High'].max()
    min_price = hist['Low'].min()
    avg_price = hist['Close'].mean()
    
    # Calculate percentage changes
    total_change = ((end_price - start_price) / start_price) * 100
    max_gain = ((max_price - start_price) / start_price) * 100
    max_loss = ((min_price - start_price) / start_price) * 100
    
    # Determine alert type
    if total_change > 5:
        alert_type = "🚀 Strong Bullish"
        color = "green"
    elif total_change > 2:
        alert_type = "📈 Bullish"
        color = "lightgreen"
    elif total_change < -5:
        alert_type = "🔻 Strong Bearish"
        color = "red"
    elif total_change < -2:
        alert_type = "📉 Bearish"
        color = "orange"
    else:
        alert_type = "➡️ Neutral"
        color = "gray"
    
    return {
        "start_price": start_price,
        "end_price": end_price,
        "max_price": max_price,
        "min_price": min_price,
        "avg_price": avg_price,
        "total_change": total_change,
        "max_gain": max_gain,
        "max_loss": max_loss,
        "alert_type": alert_type,
        "color": color,
        "volume_avg": hist['Volume'].mean()
    }

# Create sidebar
with st.sidebar:
    st.header("🔍 Controls")
    st.markdown("---")
    
    # Refresh button
    if st.button("🔄 Refresh Data", use_container_width=True):
        st.cache_data.clear()
        st.rerun()
    
    st.markdown("---")
    st.markdown("### 📅 Alert Period")
    st.info(f"**{ALERT_START.strftime('%d %b %Y')}** to **{ALERT_END.strftime('%d %b %Y')}**")
    
    st.markdown("---")
    st.markdown("### 📊 Filter Stocks")
    show_all = st.checkbox("Show All Stocks", value=True)
    
    # Stock selection
    selected_stocks = []
    if show_all:
        selected_stocks = ALL_STOCKS
    else:
        st.subheader("Select Stocks")
        for stock in ALL_STOCKS:
            if st.checkbox(stock.replace(".NS", ""), value=True):
                selected_stocks.append(stock)
    
    st.markdown("---")
    st.markdown("### 📌 Legend")
    st.markdown("🚀 Strong Bullish (>5%)")
    st.markdown("📈 Bullish (2-5%)")
    st.markdown("➡️ Neutral (-2% to 2%)")
    st.markdown("📉 Bearish (-2% to -5%)")
    st.markdown("🔻 Strong Bearish (<-5%)")

# Main content area
tab1, tab2, tab3 = st.tabs(["📈 Price Dashboard", "🔔 Alerts", "📊 Historical View"])

# Tab 1: Price Dashboard
with tab1:
    # Fetch all data
    all_data = {}
    progress_bar = st.progress(0)
    status_text = st.empty()
    
    for i, symbol in enumerate(selected_stocks):
        status_text.text(f"Fetching {symbol}...")
        data = fetch_stock_data(symbol)
        if data:
            all_data[symbol] = data
        progress_bar.progress((i + 1) / len(selected_stocks))
    
    status_text.text("Complete!")
    progress_bar.empty()
    
    # Display current prices in cards
    if all_data:
        cols = st.columns(3)
        for idx, (symbol, data) in enumerate(all_data.items()):
            with cols[idx % 3]:
                # Calculate daily change
                prev_close = data['previous_close']
                current_price = data['current_price']
                daily_change = ((current_price - prev_close) / prev_close * 100) if prev_close else 0
                
                # Determine color
                color_class = "stock-card-positive" if daily_change >= 0 else "stock-card-negative"
                price_class = "price-up" if daily_change >= 0 else "price-down"
                
                with st.container():
                    st.markdown(f"""
                        <div class="stock-card {color_class}">
                            <h4>{data['symbol']}</h4>
                            <h2>₹{current_price:.2f}</h2>
                            <p class="{price_class}">{daily_change:+.2f}%</p>
                            <small>Volume: {data['volume']:,.0f}</small><br>
                            <small>High: ₹{data['high']:.2f} | Low: ₹{data['low']:.2f}</small>
                        </div>
                    """, unsafe_allow_html=True)

# Tab 2: Alerts
with tab2:
    st.header("🔔 Stock Alerts for 13-17 July 2026")
    
    if all_data:
        alert_data = []
        for symbol, data in all_data.items():
            alert = calculate_alerts(data)
            if alert:
                alert_data.append({
                    "symbol": data['symbol'],
                    **alert
                })
        
        # Sort by total change
        alert_data.sort(key=lambda x: x['total_change'], reverse=True)
        
        # Display alerts in a table
        df_alerts = pd.DataFrame(alert_data)
        if not df_alerts.empty:
            # Format columns
            display_df = df_alerts[['symbol', 'alert_type', 'total_change', 'start_price', 'end_price', 'max_price', 'min_price']].copy()
            display_df.columns = ['Stock', 'Alert', 'Change %', 'Start Price', 'End Price', 'Max Price', 'Min Price']
            display_df['Change %'] = display_df['Change %'].apply(lambda x: f"{x:+.2f}%")
            display_df['Start Price'] = display_df['Start Price'].apply(lambda x: f"₹{x:.2f}")
            display_df['End Price'] = display_df['End Price'].apply(lambda x: f"₹{x:.2f}")
            display_df['Max Price'] = display_df['Max Price'].apply(lambda x: f"₹{x:.2f}")
            display_df['Min Price'] = display_df['Min Price'].apply(lambda x: f"₹{x:.2f}")
            
            st.dataframe(
                display_df,
                use_container_width=True,
                hide_index=True,
                column_config={
                    "Alert": st.column_config.TextColumn("Alert Type", width="medium"),
                }
            )
            
            # Summary stats
            st.markdown("---")
            col1, col2, col3 = st.columns(3)
            with col1:
                bullish = len([x for x in alert_data if x['total_change'] > 2])
                st.metric("Bullish Stocks", bullish)
            with col2:
                bearish = len([x for x in alert_data if x['total_change'] < -2])
                st.metric("Bearish Stocks", bearish)
            with col3:
                neutral = len([x for x in alert_data if -2 <= x['total_change'] <= 2])
                st.metric("Neutral Stocks", neutral)
        else:
            st.warning("No alert data available for the selected period")
    else:
        st.warning("No data available. Please refresh or check your internet connection.")

# Tab 3: Historical View
with tab3:
    st.header("📊 Historical Price Charts")
    
    if all_data:
        # Stock selector for chart
        chart_stock = st.selectbox(
            "Select Stock for Historical View",
            options=list(all_data.keys()),
            format_func=lambda x: x.replace(".NS", "")
        )
        
        if chart_stock and chart_stock in all_data:
            data = all_data[chart_stock]
            hist = data['historical']
            
            if not hist.empty:
                # Create candlestick chart
                fig = go.Figure(data=[go.Candlestick(
                    x=hist.index,
                    open=hist['Open'],
                    high=hist['High'],
                    low=hist['Low'],
                    close=hist['Close'],
                    name='Candlesticks'
                )])
                
                fig.update_layout(
                    title=f"{data['symbol']} Price Movement (13-17 July 2026)",
                    yaxis_title='Price (₹)',
                    xaxis_title='Date',
                    template='plotly_white',
                    height=500,
                    hovermode='x unified'
                )
                
                # Add volume as bar chart
                fig2 = go.Figure(data=[go.Bar(
                    x=hist.index,
                    y=hist['Volume'],
                    name='Volume',
                    marker_color='lightblue'
                )])
                
                fig2.update_layout(
                    title=f"{data['symbol']} Trading Volume",
                    yaxis_title='Volume',
                    xaxis_title='Date',
                    template='plotly_white',
                    height=300
                )
                
                st.plotly_chart(fig, use_container_width=True)
                st.plotly_chart(fig2, use_container_width=True)
                
                # Show statistics
                st.subheader("📊 Price Statistics")
                col1, col2, col3, col4 = st.columns(4)
                with col1:
                    st.metric("Start Price", f"₹{hist['Close'].iloc[0]:.2f}")
                with col2:
                    st.metric("End Price", f"₹{hist['Close'].iloc[-1]:.2f}")
                with col3:
                    st.metric("Highest", f"₹{hist['High'].max():.2f}")
                with col4:
                    st.metric("Lowest", f"₹{hist['Low'].min():.2f}")
            else:
                st.warning("No historical data available for this stock")
    else:
        st.warning("No data available. Please refresh or check your internet connection.")

# Footer
st.markdown("---")
st.markdown("""
    <div style="text-align: center; color: #666; padding: 1rem;">
        <p>📅 Data as of: {date} | ⏰ Last Updated: {time}</p>
        <p style="font-size: 0.8rem;">Data sourced from Yahoo Finance. For educational purposes only.</p>
    </div>
""".format(
    date=datetime.now().strftime("%d %b %Y"),
    time=datetime.now().strftime("%H:%M:%S")
), unsafe_allow_html=True)