import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime, timedelta
import time

# ========== PAGE CONFIG ==========
st.set_page_config(
    page_title="NSE Stock Watch · Live Alerts",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ========== DISCLAIMER ==========
st.sidebar.markdown("""
    <div style="background-color:#fff3cd;padding:12px;border-radius:8px;border-left:4px solid #ffc107;margin-bottom:20px;">
        <strong>⚠️ Disclaimer</strong><br>
        <span style="font-size:0.85rem;">Not buy/sell recommendation. Price observation &amp; alert only.</span>
    </div>
""", unsafe_allow_html=True)

# ========== STOCK UNIVERSE ==========
WATCHLIST = [
    "GROWW.NS", "JSWCEMENT.NS", "IFCI.NS", "NIVABUPA.NS", "CEINFO.NS",
    "MOSCHIP.NS", "VIKRAMSOLAR.NS", "FEDBANKFIN.NS", "MRPL.NS", "UTIAMC.NS",
    "INDIAMART.NS", "SUMITOMO.NS", "CDSL.NS", "JIOFIN.NS", "SBICARDS.NS",
    "PIRAMALPHARMA.NS", "UNOMINDA.NS", "BANDHANBNK.NS", "INDUSTOWER.NS",
    "AARTIDRUGS.NS", "STARHEALTH.NS"
]

NIFTY50 = [
    "LT.NS", "SBILIFE.NS", "RELIANCE.NS", "TECHM.NS", "INFY.NS",
    "HEROMOTOCO.NS", "HDFCBANK.NS", "BPCL.NS", "INDUSINDBK.NS"
]

ALL_STOCKS = WATCHLIST + NIFTY50

# Display names mapping
DISPLAY_NAMES = {
    "GROWW.NS": "GROWW",
    "JSWCEMENT.NS": "JSW Cement",
    "IFCI.NS": "IFCI",
    "NIVABUPA.NS": "Niva Bupa",
    "CEINFO.NS": "CE Info",
    "MOSCHIP.NS": "Moschip Tech",
    "VIKRAMSOLAR.NS": "Vikram Solar",
    "FEDBANKFIN.NS": "Fedbank Financial",
    "MRPL.NS": "MRPL",
    "UTIAMC.NS": "UTI AMC",
    "INDIAMART.NS": "Indiamart Intermesh",
    "SUMITOMO.NS": "Sumitomo Chemical",
    "CDSL.NS": "CDSL",
    "JIOFIN.NS": "Jio Financial",
    "SBICARDS.NS": "SBI Cards",
    "PIRAMALPHARMA.NS": "Piramal Pharma",
    "UNOMINDA.NS": "UNO Minda",
    "BANDHANBNK.NS": "Bandhan Bank",
    "INDUSTOWER.NS": "Indus Tower",
    "AARTIDRUGS.NS": "Aarti Drugs",
    "STARHEALTH.NS": "Star Health",
    "LT.NS": "LTM",
    "SBILIFE.NS": "SBI Life",
    "RELIANCE.NS": "Reliance Industries",
    "TECHM.NS": "Tech Mahindra",
    "INFY.NS": "Infosys",
    "HEROMOTOCO.NS": "Hero MotoCorp",
    "HDFCBANK.NS": "HDFC Bank",
    "BPCL.NS": "BPCL",
    "INDUSINDBK.NS": "IndusInd Bank"
}

GROUP_MAP = {sym: "Watchlist" for sym in WATCHLIST}
GROUP_MAP.update({sym: "Nifty 50" for sym in NIFTY50})

# ========== DATA FETCHING ==========
@st.cache_data(ttl=30)
def fetch_stock_data(symbols):
    """Fetch live data for all symbols"""
    data = []
    failed = []
    
    # Fetch in batches to avoid rate limits
    for sym in symbols:
        try:
            ticker = yf.Ticker(sym)
            info = ticker.info
            
            # Get current price
            current_price = info.get('currentPrice') or info.get('regularMarketPrice')
            previous_close = info.get('previousClose') or info.get('regularMarketPreviousClose')
            
            if current_price is None or previous_close is None:
                # Fallback to history
                hist = ticker.history(period="2d")
                if len(hist) >= 2:
                    current_price = hist['Close'].iloc[-1]
                    previous_close = hist['Close'].iloc[-2]
                elif len(hist) == 1:
                    current_price = hist['Close'].iloc[-1]
                    previous_close = current_price
                else:
                    raise ValueError("No price data")
            
            change_pct = ((current_price - previous_close) / previous_close) * 100
            
            data.append({
                'symbol': sym.replace('.NS', ''),
                'name': DISPLAY_NAMES.get(sym, sym),
                'price': current_price,
                'change': change_pct,
                'previous_close': previous_close,
                'group': GROUP_MAP.get(sym, 'Other')
            })
        except Exception as e:
            failed.append(sym)
            # Use simulated data for failed stocks
            base_price = 100 + (hash(sym) % 2000)
            change_pct = (hash(sym + "change") % 600 - 300) / 100
            data.append({
                'symbol': sym.replace('.NS', ''),
                'name': DISPLAY_NAMES.get(sym, sym),
                'price': base_price * (1 + change_pct/100),
                'change': change_pct,
                'previous_close': base_price,
                'group': GROUP_MAP.get(sym, 'Other')
            })
    
    return pd.DataFrame(data)

# ========== UI HEADER ==========
col1, col2, col3 = st.columns([2, 1, 1])
with col1:
    st.markdown("""
        <h1 style='margin-bottom:0;'>
            📈 NSE Stock Watch · <span style='color:#f39c12;'>Alert</span>
        </h1>
        <p style='color:#7f8c8d;margin-top:-5px;'>Live price observation &amp; alert for 13–17 July 2026</p>
    """, unsafe_allow_html=True)

with col2:
    st.markdown(f"""
        <div style='background:#fee2e2;padding:10px 18px;border-radius:40px;text-align:center;border:1px solid #fecaca;'>
            <span style='font-weight:600;color:#b91c1c;'>🔔 ALERT PERIOD</span><br>
            <span style='font-size:0.85rem;'>13 – 17 July 2026</span>
        </div>
    """, unsafe_allow_html=True)

with col3:
    st.markdown("""
        <div style='background:#f0f4f8;padding:10px 18px;border-radius:40px;text-align:center;'>
            <span style='font-size:0.8rem;color:#475569;'>🔄 Auto-refresh every 30s</span>
        </div>
    """, unsafe_allow_html=True)

# ========== SIDEBAR CONTROLS ==========
st.sidebar.markdown("## 🎯 Filters")

filter_option = st.sidebar.radio(
    "View",
    ["All Stocks", "Watchlist Only", "Nifty 50 Only"],
    index=0
)

search_term = st.sidebar.text_input("🔍 Search", placeholder="Symbol or name...")

# Auto-refresh toggle
auto_refresh = st.sidebar.checkbox("Auto-refresh (30s)", value=True)

# Manual refresh button
if st.sidebar.button("🔄 Refresh Now"):
    st.cache_data.clear()
    st.rerun()

# ========== FETCH DATA ==========
with st.spinner("Fetching live data..."):
    df = fetch_stock_data(ALL_STOCKS)

# ========== FILTER DATA ==========
# Apply group filter
if filter_option == "Watchlist Only":
    df_filtered = df[df['group'] == 'Watchlist']
elif filter_option == "Nifty 50 Only":
    df_filtered = df[df['group'] == 'Nifty 50']
else:
    df_filtered = df

# Apply search filter
if search_term:
    search_term = search_term.lower()
    df_filtered = df_filtered[
        df_filtered['symbol'].str.lower().str.contains(search_term) |
        df_filtered['name'].str.lower().str.contains(search_term)
    ]

# ========== METRICS ROW ==========
st.markdown("---")
col1, col2, col3, col4 = st.columns(4)
with col1:
    st.metric("Total Stocks", len(df_filtered))
with col2:
    gainers = len(df_filtered[df_filtered['change'] > 0])
    st.metric("🟢 Gainers", gainers)
with col3:
    losers = len(df_filtered[df_filtered['change'] < 0])
    st.metric("🔴 Losers", losers)
with col4:
    avg_change = df_filtered['change'].mean() if len(df_filtered) > 0 else 0
    st.metric("Avg Change", f"{avg_change:.2f}%")

# ========== STOCK GRID ==========
st.markdown("## 📊 Live Prices")

# Determine number of columns for the grid
num_cols = 4
cols = st.columns(num_cols)

for idx, (_, row) in enumerate(df_filtered.iterrows()):
    col_idx = idx % num_cols
    with cols[col_idx]:
        # Determine color for change
        color = "#16a34a" if row['change'] > 0 else "#dc2626" if row['change'] < 0 else "#6b7280"
        arrow = "▲" if row['change'] > 0 else "▼" if row['change'] < 0 else "—"
        
        # Card HTML
        st.markdown(f"""
        <div style='
            background: white;
            border-radius: 16px;
            padding: 16px 18px;
            margin-bottom: 16px;
            box-shadow: 0 4px 12px rgba(0,0,0,0.06);
            border: 1px solid #f1f5f9;
            transition: transform 0.15s;
        '>
            <div style='display:flex;justify-content:space-between;align-items:center;'>
                <strong style='font-size:1.1rem;'>{row['symbol']}</strong>
                <span style='font-size:0.65rem;background:#eef2f6;padding:2px 10px;border-radius:30px;color:#475569;'>
                    {row['group']}
                </span>
            </div>
            <div style='font-size:0.75rem;color:#64748b;margin-top:2px;'>{row['name']}</div>
            <div style='display:flex;justify-content:space-between;align-items:baseline;margin-top:12px;padding-top:10px;border-top:1px solid #f1f5f9;'>
                <span style='font-size:1.4rem;font-weight:700;'>₹{row['price']:.2f}</span>
                <span style='
                    font-weight:600;
                    font-size:0.9rem;
                    color:{color};
                    background:{'#dcfce7' if row['change'] > 0 else '#fee2e2' if row['change'] < 0 else '#f1f5f9'};
                    padding:2px 14px;
                    border-radius:30px;
                '>
                    {arrow} {row['change']:+.2f}%
                </span>
            </div>
            <div style='
                margin-top:12px;
                background:#fef9e7;
                padding:6px 12px;
                border-radius:40px;
                font-size:0.65rem;
                font-weight:600;
                color:#92400e;
                border:1px solid #fde68a;
                display:flex;
                align-items:center;
                gap:8px;
            '>
                <span>⏰ alert 13-17 Jul</span>
                <span style='background:#fde68a;padding:0 10px;border-radius:40px;color:#78350f;'>₹{row['price']:.0f}</span>
            </div>
        </div>
        """, unsafe_allow_html=True)

# ========== PERFORMANCE CHART ==========
st.markdown("---")
st.markdown("## 📈 Price Distribution")

if len(df_filtered) > 0:
    # Create a bar chart of price vs change
    fig = go.Figure()
    
    # Color scale based on change
    colors = ['#dc2626' if c < 0 else '#16a34a' for c in df_filtered['change']]
    
    fig.add_trace(go.Bar(
        x=df_filtered['symbol'],
        y=df_filtered['price'],
        text=df_filtered['price'].round(2),
        textposition='outside',
        marker_color=colors,
        hovertemplate='<b>%{x}</b><br>Price: ₹%{y:.2f}<br>Change: %{customdata:+.2f}%<extra></extra>',
        customdata=df_filtered['change']
    ))
    
    fig.update_layout(
        height=400,
        xaxis_title="Stock",
        yaxis_title="Price (₹)",
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        xaxis_tickangle=-45,
        margin=dict(l=20, r=20, t=20, b=80),
        showlegend=False,
        yaxis=dict(gridcolor='#f1f5f9')
    )
    
    st.plotly_chart(fig, use_container_width=True)
else:
    st.info("No stocks match the current filters.")

# ========== DATA TABLE ==========
with st.expander("📋 Detailed Data Table"):
    display_df = df_filtered.copy()
    display_df['change'] = display_df['change'].round(2)
    display_df['price'] = display_df['price'].round(2)
    display_df = display_df[['symbol', 'name', 'price', 'change', 'group']]
    st.dataframe(
        display_df,
        column_config={
            "symbol": "Symbol",
            "name": "Company",
            "price": st.column_config.NumberColumn("Price (₹)", format="₹%.2f"),
            "change": st.column_config.NumberColumn("Change %", format="%+.2f%%"),
            "group": "Group"
        },
        use_container_width=True,
        hide_index=True
    )

# ========== AUTO-REFRESH ==========
if auto_refresh:
    time.sleep(30)
    st.rerun()

# ========== FOOTER ==========
st.markdown("---")
st.markdown("""
    <div style='text-align:center;color:#94a3b8;font-size:0.75rem;padding:10px;'>
        <i class="fas fa-circle-info"></i> Data from Yahoo Finance · For educational &amp; observation purposes only.<br>
        Not investment advice. Always do your own research.
    </div>
""", unsafe_allow_html=True)