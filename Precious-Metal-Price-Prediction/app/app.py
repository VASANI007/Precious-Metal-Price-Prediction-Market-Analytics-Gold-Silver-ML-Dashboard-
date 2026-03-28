import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import streamlit as st
import pandas as pd
import numpy as np
import joblib
import plotly.graph_objects as go
import yfinance as yf
from datetime import datetime, timedelta
from streamlit_autorefresh import st_autorefresh
from src.data.fetch_data import fetch_all
from src.processing.preprocess import preprocess
#  PATH FIX

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
if "last_update_day" not in st.session_state:
    st.session_state.last_update_day = None

today_real = datetime.now().date()

if st.session_state.last_update_day != today_real:
    fetch_all()
    preprocess()
    st.session_state.last_update_day = today_real


#  LOAD DATA
@st.cache_data
def load_data():
    try:
        df = pd.read_csv("data/processed/final_data.csv")

        if df.empty:
            raise ValueError("Empty dataset")

        df['Date'] = pd.to_datetime(df['Date'], errors='coerce')
        df = df.dropna(subset=['Date'])

        return df

    except Exception as e:
        st.error("Failed to load data. Please update data.")
        return pd.DataFrame()
# LOAD MODEL
try:
    model = joblib.load("models/model.pkl")
except:
    model = None
df = load_data()

latest = df.iloc[-1]
previous = df.iloc[-2]

today_date = latest['Date'].date()
yesterday_date = previous['Date'].date()

#  SCROLLING TICKER
@st.cache_data(ttl=300)
def get_usd_data():
    return yf.download("USDINR=X", period="2d")
#  CALCULATE CHANGES
g24_change = latest['Gold_24K_1g'] - previous['Gold_24K_1g']
g22_change = latest['Gold_22K_1g'] - previous['Gold_22K_1g']
silver_change = latest['Silver_1g'] - previous['Silver_1g']
try:
    usd_live = get_usd_data()

    if usd_live.empty:
        raise ValueError("No USD data")

    if len(usd_live) >= 2:
        usd_price = float(usd_live['Close'].iloc[-1])
        usd_prev = float(usd_live['Close'].iloc[-2])
        usd_change = usd_price - usd_prev
    else:
        usd_price = float(usd_live['Close'].iloc[-1])
        usd_change = 0

except Exception as e:
    st.warning("USD data not available, showing last known value")
    usd_price = 0
    usd_change = 0

#  SCROLLING TICKER
def format_change(val):
    if val > 0:
        return f"<span style='color:#02ff99; font-weight:bold;'>▲ {abs(val):.2f}</span>"
    elif val < 0:
        return f"<span style='color:#ff4d4d; font-weight:bold;'>▼ {abs(val):.2f}</span>"
    else:
        return "<span style='color:gray;'>0</span>"

#  PREPARE VALUES
g24_html = format_change(g24_change)
g22_html = format_change(g22_change)
silver_html = format_change(silver_change)
usd_html = format_change(usd_change)
#  SINGLE LINE STRING (IMPORTANT)
ticker_text = f"""
Gold 24K: ₹ {latest['Gold_24K_1g']:.2f}&nbsp;&nbsp;&nbsp;&nbsp; ({g24_html})
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp; | &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;
Gold 22K: ₹ {latest['Gold_22K_1g']:.2f}&nbsp;&nbsp;&nbsp;&nbsp; ({g22_html})
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp; | &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;
Silver: ₹ {latest['Silver_1g']:.2f}&nbsp;&nbsp;&nbsp;&nbsp; ({silver_html})
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp; | &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;
USD/INR: ₹ {usd_price:.2f}&nbsp;&nbsp;&nbsp;&nbsp; ({usd_html})
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

#  TABS
tab1, tab2, tab3, tab4 = st.tabs(["🪙 Gold 24K", "🧈 Gold 22K", "🔘 Silver", "💱 USD → INR"])

#  COMMON UI
def show_section(metal, column_name):

    styled_subheader(f"{metal} Overview")

    #  DATE + WEIGHT 
    colA, colB = st.columns(2)
    max_date = df['Date'].max().date()
    with colA:
        selected_date = st.date_input(
            "Choose Date",
            value=max_date,
            key=f"{metal}_date"
        )

    with colB:
        weight_options = ["1g", "10g", "100g", "1kg"]
        selected_weight = st.selectbox(
            "Select Weight",
            weight_options,
            index=0,
            key=f"{metal}_weight"
        )

    # IMPORTANT: dynamic column
    column_name = f"{metal}_{selected_weight}"

    filtered_df = df[df['Date'].dt.date == selected_date]

    max_date = df['Date'].max().date()

    # 🔥 CASE 1: FUTURE DATE
    if filtered_df.empty and selected_date > max_date:
        st.warning("Future date selected — showing prediction")

        last_row = df.iloc[-1]
        prev_row = df.iloc[-2]

        last_val = float(last_row[column_name])
        prev_val = float(prev_row[column_name])

        days_ahead = (selected_date - max_date).days

        temp_prev = prev_val
        temp_last = last_val

        for _ in range(days_ahead):
            input_data = np.array([[temp_prev, temp_last]])
            next_pred = model.predict(input_data)[0]

            temp_prev = temp_last
        temp_last = next_pred

        today = temp_last
        yesterday = temp_prev

        selected_datetime = pd.to_datetime(selected_date)

    # ✅ IMPORTANT FIX (TABLE KE LIYE)
        selected_row = {}

        for w in ["1g", "10g", "100g", "1kg"]:
            col = f"{metal}_{w}"

            last_val_w = float(df.iloc[-1][col])
            prev_val_w = float(df.iloc[-2][col])

            temp_prev_w = prev_val_w
            temp_last_w = last_val_w

            for _ in range(days_ahead):
                input_data = np.array([[temp_prev_w, temp_last_w]])
                next_pred_w = model.predict(input_data)[0]

                temp_prev_w = temp_last_w
                temp_last_w = next_pred_w

            selected_row[col] = temp_last_w

    # 🔥 CASE 2: NORMAL DATE
    elif not filtered_df.empty:
        selected_row = filtered_df.iloc[0]

        today = float(selected_row[column_name])

        prev_df = df[df['Date'] < pd.to_datetime(selected_date)]

        if not prev_df.empty:
            yesterday = float(prev_df.iloc[-1][column_name])
        else:
            yesterday = today

        selected_datetime = pd.to_datetime(selected_date)

# 🔥 CASE 3: INVALID
    else:
        st.error("Data Not Found for selected date")
        return

    prev_df = df[df['Date'] < pd.to_datetime(selected_date)]

    if not prev_df.empty:
        yesterday = prev_df.iloc[-1][column_name]
    else:
        yesterday = today

    change = today - yesterday

    if change > 0:
        arrow = "▲"
        delta_color = "normal"
    else:
        arrow = "▼"
        delta_color = "inverse"

    #  METRICS 
    col1, col2, col3, col4 = st.columns(4)
    selected_datetime = pd.to_datetime(selected_date)
    # 🎯 PREDICTION
    if model is not None:
        try:

            last_value = float(today)
            prev_value = float(yesterday)

            input_data = np.array([[prev_value, last_value]])
            prediction = model.predict(input_data)[0]

            pred_change = prediction - last_value

            arrow = "▲" if pred_change > 0 else "▼"
            color = "normal" if pred_change > 0 else "inverse"

            st.metric(
                "🎯 Predicted Next Day",
                f"₹ {prediction:.2f}",
                f"{arrow} {abs(pred_change):.2f}",
                delta_color=color
            )

        except Exception as e:
            st.error(f"Prediction error: {e}")
    else:
        st.warning(" Model not loaded")
    # 🎯 FUTURE 7 DAYS PREDICTION
    future_days = 7
    future_preds = []
    future_dates = []

    last_val = float(today)
    prev_val = float(yesterday)

    for i in range(future_days):
        input_data = np.array([[prev_val, last_val]])
        next_pred = model.predict(input_data)[0]

        future_preds.append(next_pred)
        future_dates.append(selected_datetime + timedelta(days=i+1))

        prev_val = last_val
        last_val = next_pred

    col1.metric("📅 Selected Day", f"₹ {today:.2f}", f"{arrow} {change:.2f}", delta_color=delta_color)
    col2.metric("🗓️ Previous Day", f"₹ {yesterday:.2f}")
    col3.metric("📈 Highest", f"₹ {df[column_name].max():.2f}")
    col4.metric("📉 Lowest", f"₹ {df[column_name].min():.2f}")

    st.caption(f"Selected Date: {selected_date} | Weight: {selected_weight}")

    #  TABLE 
    styled_subheader("Price Table")

    weights = ["1g", "10g", "100g", "1kg"]
    rows = []

    for w in weights:
        col = f"{metal}_{w}"
        t = selected_row[col] if isinstance(selected_row, dict) else selected_row[col]

        if not prev_df.empty:
            y = prev_df.iloc[-1][col]
        else:
            y = t

        c = t - y

        if c > 0:
            change_html = f"<span style='color:#02ff99'>▲ ₹{abs(c):,.2f}</span>"
        else:
            change_html = f"<span style='color:#ff4d4d'>▼ ₹{abs(c):,.2f}</span>"

        rows.append({
            "Gram": w,
            "Today": f"₹{t:,.2f}",
            "Yesterday": f"₹{y:,.2f}",
            "Change": change_html
        })

    table_df = pd.DataFrame(rows)

    st.markdown(table_df.to_html(escape=False, index=False), unsafe_allow_html=True)
    styled_subheader(" 7 Day Prediction")

    pred_rows = []

    for i in range(len(future_preds)):
        if i == 0:
            prev_val = today
        else:
            prev_val = future_preds[i-1]

        curr = future_preds[i]
        diff = curr - prev_val

        if diff > 0:
            change_html = f"<span style='color:#02ff99'>▲ ₹{abs(diff):,.2f}</span>"
        else:
            change_html = f"<span style='color:#ff4d4d'>▼ ₹{abs(diff):,.2f}</span>"

        pred_rows.append({
            "Date": future_dates[i].date(),
            "Predicted Price": f"₹{curr:,.2f}",
            "Change": change_html
        })

    pred_df = pd.DataFrame(pred_rows)

    st.markdown(pred_df.to_html(escape=False, index=False), unsafe_allow_html=True)
    #  GRAPH 
    styled_subheader("Price Trend")

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
    selected_datetime = pd.to_datetime(selected_date)

    if selected == "1W":
        dff = df[df['Date'] <= selected_datetime].tail(7)
    elif selected == "1M":
        dff = df[df['Date'] <= selected_datetime].tail(30)
    elif selected == "3M":
        dff = df[df['Date'] <= selected_datetime].tail(90)
    elif selected == "6M":
        dff = df[df['Date'] <= selected_datetime].tail(180)
    elif selected == "1Y":
        dff = df[df['Date'] <= selected_datetime].tail(365)
    else:
        dff = df[df['Date'] <= selected_datetime]

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
    # ADD PREDICTION LINE
    fig.add_trace(go.Scatter(
        x=future_dates,
        y=future_preds,
        mode='lines+markers',
        line=dict(color='#f39c12', width=3, dash='dash'),
        name="Prediction"
    ))

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

        if isinstance(usd.columns, pd.MultiIndex):
            usd.columns = usd.columns.get_level_values(0)

        usd.reset_index(inplace=True)
        usd = usd[['Date', 'Close']].dropna()
        usd['Date'] = pd.to_datetime(usd['Date'])

        # DATE PICKER
        selected_date = st.date_input(
            "Choose Date",
            value=usd['Date'].iloc[-1].date(),
            key="usd_date"
        )

        filtered_usd = usd[usd['Date'].dt.date == selected_date]
        max_date = usd['Date'].max().date()

        # 🔥 FUTURE DATE FIX
        if filtered_usd.empty and selected_date > max_date:
            st.warning("Future date selected — showing prediction")

            last_row = usd.iloc[-1]
            prev_row = usd.iloc[-2]

            last_val = float(last_row['Close'])
            prev_val = float(prev_row['Close'])

            days_ahead = (selected_date - max_date).days

            temp_prev = prev_val
            temp_last = last_val

            for _ in range(days_ahead):
                input_data = np.array([[temp_prev, temp_last]])
                next_pred = model.predict(input_data)[0]

                temp_prev = temp_last
                temp_last = next_pred

            latest = temp_last
            prev = temp_prev
            selected_datetime = pd.to_datetime(selected_date)

        # 🔥 NORMAL DATE
        elif not filtered_usd.empty:
            selected_row = filtered_usd.iloc[0]
            latest = float(selected_row['Close'])

            prev_df = usd[usd['Date'] < pd.to_datetime(selected_date)]

            if not prev_df.empty:
                prev = float(prev_df.iloc[-1]['Close'])
            else:
                prev = latest

            selected_datetime = pd.to_datetime(selected_date)

        else:
            st.error("Data Not Found for selected date")
            st.stop()

        change = latest - prev

        # METRICS
        col1, col2, col3, col4 = st.columns(4)

        arrow = "▲" if change > 0 else "▼"
        color = "normal" if change > 0 else "inverse"

        col1.metric("📅 Selected Day", f"₹ {latest:.2f}", f"{arrow} {change:.2f}", delta_color=color)
        col2.metric("🗓️ Yesterday", f"₹ {prev:.2f}")
        col3.metric("📈 Highest", f"₹ {float(usd['Close'].max()):.2f}")
        col4.metric("📉 Lowest", f"₹ {float(usd['Close'].min()):.2f}")

        # 🎯 NEXT DAY PREDICTION
        if model is not None:
            try:
                input_data = np.array([[prev, latest]])
                prediction = model.predict(input_data)[0]

                pred_change = prediction - latest

                arrow = "▲" if pred_change > 0 else "▼"
                color = "normal" if pred_change > 0 else "inverse"

                st.metric(
                    "🎯 Predicted Next Day",
                    f"₹ {prediction:.2f}",
                    f"{arrow} {abs(pred_change):.2f}",
                    delta_color=color
                )

            except Exception as e:
                st.error(f"Prediction error: {e}")

        # LAST 5 DAYS TABLE
        styled_subheader("Last 5 Days USD-INR")

        last5 = usd[usd['Date'] <= pd.to_datetime(selected_date)].tail(5).copy().reset_index(drop=True)

        rows = []

        for i in range(len(last5)):
            today_val = float(last5.loc[i, 'Close'])

            if i == 0:
                change_html = "-"
            else:
                prev_val = float(last5.loc[i-1, 'Close'])
                diff = today_val - prev_val

                if diff > 0:
                    change_html = f"<span style='color:#02ff99'>▲ ₹{abs(diff):.2f}</span>"
                else:
                    change_html = f"<span style='color:#ff4d4d'>▼ ₹{abs(diff):.2f}</span>"

            rows.append({
                "Date": last5.loc[i, 'Date'].date(),
                "Price": f"₹{today_val:.2f}",
                "Change": change_html
            })

        table_df = pd.DataFrame(rows)
        st.markdown(table_df.to_html(escape=False, index=False), unsafe_allow_html=True)

        # 🔮 7 DAYS PREDICTION
        if model is not None:
            future_days = 7
            future_preds = []
            future_dates = []

            last_val = float(latest)
            prev_val = float(prev)

            for i in range(future_days):
                input_data = np.array([[prev_val, last_val]])
                next_pred = model.predict(input_data)[0]

                future_preds.append(next_pred)
                future_dates.append(selected_datetime + timedelta(days=i+1))

                prev_val = last_val
                last_val = next_pred

            styled_subheader("7 Day USD Prediction")

            pred_rows = []

            for i in range(len(future_preds)):
                if i == 0:
                    prev_val = latest
                else:
                    prev_val = future_preds[i-1]

                curr = future_preds[i]
                diff = curr - prev_val

                if diff > 0:
                    change_html = f"<span style='color:#02ff99'>▲ ₹{abs(diff):.2f}</span>"
                else:
                    change_html = f"<span style='color:#ff4d4d'>▼ ₹{abs(diff):.2f}</span>"

                pred_rows.append({
                    "Date": future_dates[i].date(),
                    "Predicted Price": f"₹{curr:.2f}",
                    "Change": change_html
                })

            pred_df = pd.DataFrame(pred_rows)
            st.markdown(pred_df.to_html(escape=False, index=False), unsafe_allow_html=True)

        # GRAPH
        styled_subheader("USD-INR Trend")

        options = ["1W", "1M", "3M", "6M", "1Y", "ALL"]
        key_name = "usd_range"

        if key_name not in st.session_state:
            st.session_state[key_name] = "3M"

        left, c1, c2, c3, c4, c5, c6, right = st.columns([2,1,1,1,1,1,1,2])
        cols = [c1, c2, c3, c4, c5, c6]

        for i, opt in enumerate(options):
            if cols[i].button(opt, key=f"usd_{opt}"):
                st.session_state[key_name] = opt

        selected = st.session_state[key_name]

        if selected == "1W":
            usd_filtered = usd[usd['Date'] <= selected_datetime].tail(7)
        elif selected == "1M":
            usd_filtered = usd[usd['Date'] <= selected_datetime].tail(30)
        elif selected == "3M":
            usd_filtered = usd[usd['Date'] <= selected_datetime].tail(90)
        elif selected == "6M":
            usd_filtered = usd[usd['Date'] <= selected_datetime].tail(180)
        elif selected == "1Y":
            usd_filtered = usd[usd['Date'] <= selected_datetime].tail(365)
        else:
            usd_filtered = usd[usd['Date'] <= selected_datetime]

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

        # 🔮 Prediction Line
        if model is not None:
            fig.add_trace(go.Scatter(
                x=future_dates,
                y=future_preds,
                mode='lines+markers',
                line=dict(color='#f39c12', width=3, dash='dash'),
                name="Prediction"
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