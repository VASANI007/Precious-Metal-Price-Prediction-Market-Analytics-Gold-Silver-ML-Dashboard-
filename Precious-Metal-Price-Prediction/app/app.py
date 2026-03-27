import sys
import os
import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import yfinance as yf
from datetime import datetime, timedelta

#  PATH FIX
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

#  CONFIG
st.set_page_config(page_title="Gold & Silver Market Insights", page_icon="🪙", layout="wide")
#  STYLES Title
st.markdown("""
<h1 style='
    color:white;
    border-left:6px solid #888;
    padding-left:12px;
    font-weight:bold;
'>
Gold & Silver Market Insights
</h1>
<p style='color:#aaa; margin-left:12px;'>
Advanced Analytics for Gold, Silver & Currency
</p>
""", unsafe_allow_html=True)

#  STYLES TABLE
st.markdown("""
<style>
table {
    width: 100% !important;
    border-collapse: collapse;
    text-align: center;
    font-size: 16px;
}
th {
    background-color: #111;
    color: white;
    padding: 14px;
    text-align: center !important;
}
td {
    padding: 12px;
    border-bottom: 1px solid #333;
    text-align: center !important;
}
tr:hover {
    background-color: #1a1a1a;
}
</style>
""", unsafe_allow_html=True)

#  STYLES SUBHEADER
def styled_subheader(text):
    st.markdown(f"""
    <h3 style='
        border-left: 5px solid #4FC3F7;
        padding-left: 10px;
        font-weight: 400;
        margin-top: 20px;
    '>
    {text}
    </h3><br>
    """, unsafe_allow_html=True)

#  AUTO REFRESH
if "last_refresh" not in st.session_state:
    st.session_state.last_refresh = datetime.now()

# auto refresh every 24 hours
if datetime.now() - st.session_state.last_refresh > timedelta(hours=24):
    st.cache_data.clear()
    st.session_state.last_refresh = datetime.now()
    st.rerun()

#  LOAD DATA
@st.cache_data
def load_data():
    df = pd.read_csv("data/processed/final_data.csv")
    df['Date'] = pd.to_datetime(df['Date'], errors='coerce')
    return df.dropna(subset=['Date'])

df = load_data()

latest = df.iloc[-1]
previous = df.iloc[-2]

today_date = latest['Date'].date()
yesterday_date = previous['Date'].date()

# USD VALUE
usd_live = yf.download("USDINR=X", period="1d")
usd_price = float(usd_live['Close'].iloc[-1])

#  SCROLLING TICKER

#  CALCULATE CHANGES
g24_change = latest['Gold_24K_1g'] - previous['Gold_24K_1g']
g22_change = latest['Gold_22K_1g'] - previous['Gold_22K_1g']
silver_change = latest['Silver_1g'] - previous['Silver_1g']

def format_change(val):
    if val > 0:
        return f"<span style='color:#00ff99'>▲ {abs(val):.0f}</span>"
    else:
        return f"<span style='color:#ff4d4d'>▼ {abs(val):.0f}</span>"

#  SCROLLING TICKER
def format_change(val):
    if val > 0:
        return f"<span style='color:#00ff99; font-weight:bold;'>▲ {abs(val):.0f}</span>"
    elif val < 0:
        return f"<span style='color:#ff4d4d; font-weight:bold;'>▼ {abs(val):.0f}</span>"
    else:
        return "<span style='color:gray;'>0</span>"

#  PREPARE VALUES
g24_html = format_change(g24_change)
g22_html = format_change(g22_change)
silver_html = format_change(silver_change)

#  SINGLE LINE STRING (IMPORTANT)
ticker_text = f"""
Gold 24K: ₹ {latest['Gold_24K_1g']:.0f}&nbsp;&nbsp;&nbsp;&nbsp; ({g24_html})
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp; | &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;
Gold 22K: ₹ {latest['Gold_22K_1g']:.0f}&nbsp;&nbsp;&nbsp;&nbsp; ({g22_html})
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp; | &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;
Silver: ₹ {latest['Silver_1g']:.0f}&nbsp;&nbsp;&nbsp;&nbsp; ({silver_html})
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp; | &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;
USD/INR: ₹ {usd_price:.2f}
""".replace("\n", " ")

#  RENDER
st.markdown(f"""
<style>
.ticker-container {{
    width: 100%;
    overflow: hidden;
    background: #0e1117;
    padding: 10px 0;
}}

.ticker-text {{
    display: inline-block;
    white-space: nowrap;
    animation: scroll-left 12s linear infinite;
    color: white;
    font-size: 17px;
    padding-left: 100%;
}}

@keyframes scroll-left {{
    0% {{ transform: translateX(0%); }}
    100% {{ transform: translateX(-100%); }}
}}
</style>

<div class="ticker-container">
    <div class="ticker-text">
        {ticker_text}
    </div>
</div>
""", unsafe_allow_html=True)
#  UPDATE BUTTON
if st.sidebar.button("🆕 Update Data"):
    from src.data.fetch_data import fetch_all
    from src.processing.preprocess import preprocess
    from src.models.train_model import train_model

    fetch_all()
    preprocess()
    train_model()
    st.cache_data.clear()
    st.success("Updated Successfully!")

#  TABS
tab1, tab2, tab3, tab4 = st.tabs(["🪙 Gold 24K", "🧈 Gold 22K", "🔘 Silver", "💱 USD → INR"])

#  COMMON UI
def show_section(metal, column_name):

    styled_subheader(f"{metal} Overview")

    today = latest[column_name]
    yesterday = previous[column_name]
    change = today - yesterday

    if change > 0:
        arrow = "▲"
        delta_color = "normal"
    else:
        arrow = "▼"
        delta_color = "inverse"

    #  METRICS 
    col1, col2, col3, col4 = st.columns(4)

    col1.metric("📅 Today", f"₹ {today:.2f}", f"{arrow} {change:.2f}", delta_color=delta_color)
    col2.metric("🗓️ Yesterday", f"₹ {yesterday:.2f}")
    col3.metric("📈 Highest", f"₹ {df[column_name].max():.2f}")
    col4.metric("📉 Lowest", f"₹ {df[column_name].min():.2f}")

    st.caption(f"Data Date: {today_date}")

#  TABLE
    styled_subheader("Price Table")

    weights = ["1g", "10g", "100g", "1kg"]
    rows = []

    for w in weights:
        t = latest[f"{metal}_{w}"]
        y = previous[f"{metal}_{w}"]
        c = t - y

        if c > 0:
            change_html = f"<span style='color:#00ff99'>▲ ₹{abs(c):,.0f}</span>"
        else:
            change_html = f"<span style='color:#ff4d4d'>▼ ₹{abs(c):,.0f}</span>"

        rows.append({
            "Gram": w,
            "Today": f"₹{t:,.0f}",
            "Yesterday": f"₹{y:,.0f}",
            "Change": change_html
        })

    table_df = pd.DataFrame(rows)

    # IMPORTANT: NO st.dataframe() here
    st.markdown(table_df.to_html(escape=False, index=False), unsafe_allow_html=True)
    #  GRAPH
    styled_subheader("Price Trend")

# DROPDOWN ADD
    weight_options = ["1g", "10g", "100g", "1kg"]

    selected_weight = st.selectbox(
        "Select Weight",
        weight_options,
        index=0,
        key=f"{metal}_weight"
    )

    column_name = f"{metal}_{selected_weight}"

#  RANGE BUTTONS
    options = ["1W", "1M", "3M", "6M", "1Y", "ALL"]

    key_name = f"{metal}_range"

    if key_name not in st.session_state:
        st.session_state[key_name] = "3M"

    left, c1, c2, c3, c4, c5, c6, right = st.columns([2,1,1,1,1,1,1,2])

    cols = [c1, c2, c3, c4, c5, c6]

    for i, opt in enumerate(options):
        if cols[i].button(opt, key=f"{opt}_{metal}"):
            st.session_state[key_name] = opt

    selected = st.session_state[key_name]

#  FILTER
    if selected == "1W":
        dff = df.tail(7)
    elif selected == "1M":
        dff = df.tail(30)
    elif selected == "3M":
        dff = df.tail(90)
    elif selected == "6M":
        dff = df.tail(180)
    elif selected == "1Y":
        dff = df.tail(365)
    else:
        dff = df

#  GRAPH 
    fig = go.Figure()

    fig.add_trace(go.Scatter(
    x=dff['Date'],
    y=dff[column_name],
    mode='lines',
    line=dict(color='#2ecc71', width=3),
    name=f"{selected_weight} Price"
    ))

    fig.add_trace(go.Scatter(
    x=dff['Date'],
    y=dff[column_name],
    fill='tozeroy',
    mode='none',
    fillcolor='rgba(46,204,113,0.1)'
    ))

    fig.update_layout(
    template="plotly_dark",
    hovermode="x unified",
    margin=dict(l=20, r=20, t=30, b=20),
    yaxis_title=f"Price ({selected_weight})"
    )

    st.plotly_chart(fig, use_container_width=True)

#  TABS CONTENT
with tab1:
    show_section("Gold_24K", "Gold_24K_1g")

with tab2:
    show_section("Gold_22K", "Gold_22K_1g")

with tab3:
    show_section("Silver", "Silver_1g")

#  USD TAB
with tab4:
    styled_subheader(" USD to INR")

    try:
        usd = yf.download("USDINR=X", period="1y")

        if usd.empty:
            st.error("No USD-INR data available")
            st.stop()

        #  multi-index fix
        if isinstance(usd.columns, pd.MultiIndex):
            usd.columns = usd.columns.get_level_values(0)

        usd.reset_index(inplace=True)
        usd = usd[['Date', 'Close']].dropna()
        usd['Date'] = pd.to_datetime(usd['Date'])

        #  METRICS
        latest = float(usd['Close'].iloc[-1])
        prev = float(usd['Close'].iloc[-2])
        change = latest - prev

        col1, col2, col3 = st.columns(3)

        arrow = "▲" if change > 0 else "▼"
        color = "normal" if change > 0 else "inverse"

        col1.metric("Current", f"₹ {latest:.2f}", f"{arrow} {change:.2f}", delta_color=color)
        col2.metric("Highest", f"₹ {float(usd['Close'].max()):.2f}")
        col3.metric("Lowest", f"₹ {float(usd['Close'].min()):.2f}")

        #  TABLE (LAST 5 DAYS)
        styled_subheader("Last 5 Days USD-INR")

        last5 = usd.tail(5).copy().reset_index(drop=True)

        rows = []

        for i in range(len(last5)):
            today = float(last5.loc[i, 'Close'])

            if i == 0:
                change_html = "-"
            else:
                prev_val = float(last5.loc[i-1, 'Close'])
                diff = today - prev_val

                if diff > 0:
                    change_html = f"<span style='color:#00ff99'>▲ ₹{abs(diff):.2f}</span>"
                else:
                    change_html = f"<span style='color:#ff4d4d'>▼ ₹{abs(diff):.2f}</span>"

            rows.append({
                "Date": last5.loc[i, 'Date'].date(),
                "Price": f"₹{today:.2f}",
                "Change": change_html
            })

        table_df = pd.DataFrame(rows)

        st.markdown(table_df.to_html(escape=False, index=False), unsafe_allow_html=True)

        #  GRAPH
        styled_subheader("USD-INR Trend")

        #  BIG RANGE BUTTONS
        options = ["1W", "1M", "3M", "6M", "1Y", "ALL"]
        # unique key for USD
        key_name = "usd_range"
        if key_name not in st.session_state:
            st.session_state[key_name] = "3M"
        # CENTER ALIGN (same as metals)
        left, c1, c2, c3, c4, c5, c6, right = st.columns([2,1,1,1,1,1,1,2])
        cols = [c1, c2, c3, c4, c5, c6]
        for i, opt in enumerate(options):
            if cols[i].button(opt, key=f"usd_{opt}"):
                st.session_state[key_name] = opt
        selected = st.session_state[key_name]
        #  FILTER DATA
        if selected == "1W":
            usd_filtered = usd.tail(7)
        elif selected == "1M":
            usd_filtered = usd.tail(30)
        elif selected == "3M":
            usd_filtered = usd.tail(90)
        elif selected == "6M":
            usd_filtered = usd.tail(180)
        elif selected == "1Y":
            usd_filtered = usd.tail(365)
        else:
            usd_filtered = usd

        #  GRAPH
        fig = go.Figure()

        fig.add_trace(go.Scatter(
            x=usd_filtered['Date'],
            y=usd_filtered['Close'],
            mode='lines',
            line=dict(color='#2ecc71', width=3),
            name="USD-INR"
        ))

        fig.add_trace(go.Scatter(
            x=usd_filtered['Date'],
            y=usd_filtered['Close'],
            fill='tozeroy',
            mode='none',
            fillcolor='rgba(46,204,113,0.15)'
        ))

        fig.update_layout(
            template="plotly_dark",
            hovermode="x unified",
            margin=dict(l=20, r=20, t=30, b=20),
            xaxis_title="Date",
            yaxis_title="Price (₹)"
        )

        st.plotly_chart(fig, use_container_width=True)
    except Exception as e:
        st.error(f"Error: {e}")
#  FOOTER
st.markdown("---")
st.caption("© 2026 • Developed by Daksh Vasani | Advanced Analytics • Machine Learning • Financial Insights")