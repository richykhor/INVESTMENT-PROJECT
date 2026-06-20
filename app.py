import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px

# --- PAGE CONFIGURATION ---
st.set_page_config(page_title="The Retirement Race", layout="wide")

# --- CUSTOM CSS FOR BRANDING ---
st.markdown("""
    <style>
    .main-title { font-size: 40px; font-weight: bold; color: #2E4053; text-align: center; }
    .sub-title { font-size: 20px; color: #5D6D7E; text-align: center; margin-bottom: 30px; }
    </style>
""", unsafe_allow_html=True)

# --- HEADER ---
st.markdown('<div class="main-title">The Retirement Race 🏁</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-title">EPF vs. The Stock Market – Where Should Your Ringgit Grow?</div>', unsafe_allow_html=True)

# --- ASSUMED RATES ---
EPF_RATE_ANNUAL = 0.055  # 5.5%
STOCK_RATE_ANNUAL = 0.09 # 9.0%
INFLATION_RATE = 0.03    # 3.0%
YEARS = 30
MONTHS = YEARS * 12

# --- INTERACTIVE SIDEBAR (USER INPUT) ---
st.sidebar.header("💰 Your Investment Plan")
st.sidebar.write("Imagine you have extra money every month. How will you split it?")

total_investment = st.sidebar.number_input("Total Monthly Surplus (RM)", min_value=100, max_value=5000, value=500, step=50)

st.sidebar.subheader("Asset Allocation")
epf_percentage = st.sidebar.slider("Allocation to EPF (%)", min_value=0, max_value=100, value=50, step=10)
stock_percentage = 100 - epf_percentage

st.sidebar.write(f"**EPF Monthly:** RM {(epf_percentage/100)*total_investment:.2f}")
st.sidebar.write(f"**Stocks Monthly:** RM {(stock_percentage/100)*total_investment:.2f}")

# --- CALCULATION FUNCTIONS (Future Value of Annuity) ---
def calculate_fva(monthly_pmt, annual_rate, months):
    if monthly_pmt == 0:
        return np.zeros(months + 1)
    monthly_rate = annual_rate / 12
    # Calculate cumulative value month by month for the graph
    values = [0]
    for m in range(1, months + 1):
        # FV formula applied iteratively
        val = monthly_pmt * (((1 + monthly_rate)**m - 1) / monthly_rate)
        values.append(val)
    return np.array(values)

# --- CALCULATING THE 3 PATHS ---
# 1. 100% EPF Path
epf_100_path = calculate_fva(total_investment, EPF_RATE_ANNUAL, MONTHS)

# 2. 100% Stock Path
stock_100_path = calculate_fva(total_investment, STOCK_RATE_ANNUAL, MONTHS)

# 3. Hybrid Path (User's Custom Split)
epf_hybrid = calculate_fva(total_investment * (epf_percentage/100), EPF_RATE_ANNUAL, MONTHS)
stock_hybrid = calculate_fva(total_investment * (stock_percentage/100), STOCK_RATE_ANNUAL, MONTHS)
hybrid_path = epf_hybrid + stock_hybrid

# --- INFLATION ADJUSTMENT (Real Value of the Hybrid Path) ---
real_value_hybrid = hybrid_path[-1] / ((1 + INFLATION_RATE) ** YEARS)

# --- VOLATILITY RATING ---
# Simple scale: 100% EPF = 1 (Very Safe), 100% Stocks = 10 (Very Volatile)
volatility_score = 1 + (stock_percentage / 100) * 9

# --- MAIN DASHBOARD AREA ---
col1, col2, col3 = st.columns(3)

with col1:
    st.info("🛡️ **100% EPF (Wealth Protector)**")
    st.metric(label="Estimated Value (30 Yrs)", value=f"RM {epf_100_path[-1]:,.2f}")

with col2:
    st.success("⚖️ **Your Custom Hybrid Path**")
    st.metric(label="Estimated Value (30 Yrs)", value=f"RM {hybrid_path[-1]:,.2f}")

with col3:
    st.warning("📈 **100% Stocks (Wealth Creator)**")
    st.metric(label="Estimated Value (30 Yrs)", value=f"RM {stock_100_path[-1]:,.2f}")

st.divider()

# --- GRAPHING MULTIPLE PATHS ---
st.subheader("📈 30-Year Wealth Projection")

# Creating a DataFrame for Plotly
df = pd.DataFrame({
    'Month': np.arange(MONTHS + 1),
    '100% EPF': epf_100_path,
    'Your Hybrid': hybrid_path,
    '100% Stocks': stock_100_path
})

fig = px.line(df, x='Month', y=['100% EPF', 'Your Hybrid', '100% Stocks'],
              labels={'value': 'Total Wealth (RM)', 'variable': 'Investment Path'},
              color_discrete_map={'100% EPF': 'blue', 'Your Hybrid': 'green', '100% Stocks': 'orange'})
fig.update_layout(hovermode="x unified")
st.plotly_chart(fig, use_container_width=True)

# --- MATHEMATICAL ANALYSIS & RISK/RETURN SECTION ---
st.divider()
st.subheader("📊 Investment Mathematics Breakdown")

col_a, col_b = st.columns(2)

with col_a:
    st.write("### Risk-Return Trade-Off")
    st.progress(int(volatility_score * 10))
    st.write(f"**Volatility Rating: {volatility_score:.1f} / 10**")
    if volatility_score <= 4:
        st.write("Current Status: **Conservative.** You have a guaranteed floor, but you might lose out to inflation.")
    elif volatility_score <= 7:
        st.write("Current Status: **Balanced.** Good mathematical harmony between protection and aggressive growth.")
    else:
        st.write("Current Status: **Aggressive.** High potential for capital gains, but mathematically exposed to high market drops.")

with col_b:
    st.write("### The Silent Thief: Inflation")
    st.write(f"In nominal terms (raw numbers), your hybrid strategy yields **RM {hybrid_path[-1]:,.2f}**.")
    st.write(f"However, using Interest Rate Analysis, we adjust for a {INFLATION_RATE*100}% annual inflation rate.")
    st.write(f"**Real Purchasing Power in today's money:**")
    st.markdown(f"<h3 style='color: red;'>RM {real_value_hybrid:,.2f}</h3>", unsafe_allow_html=True)

st.caption("Project by: Ho Jun Chi, Lee Jing Wei, Ku Yong Jie, Tan Qian Yin, Nurul Iman Hannani Binti Ridzuan (MTM3023 K1)")
