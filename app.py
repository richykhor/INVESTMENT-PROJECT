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

# --- INTERACTIVE SIDEBAR (USER INPUT) ---
st.sidebar.header("💰 Your Investment Plan")
st.sidebar.write("Imagine you have extra money every month. How will you split it?")

total_investment = st.sidebar.number_input("Total Monthly Surplus (RM)", min_value=100, max_value=5000, value=500, step=50)

# NEW: Dynamic Years Slider
investment_years = st.sidebar.slider("Investment Duration (Years)", min_value=5, max_value=50, value=30, step=1)
months = investment_years * 12

st.sidebar.subheader("Asset Allocation")
epf_percentage = st.sidebar.slider("Allocation to EPF (%)", min_value=0, max_value=100, value=50, step=10)
stock_percentage = 100 - epf_percentage

epf_monthly_pmt = (epf_percentage/100) * total_investment
stock_monthly_pmt = (stock_percentage/100) * total_investment

st.sidebar.write(f"**EPF Monthly:** RM {epf_monthly_pmt:.2f}")
st.sidebar.write(f"**Stocks Monthly:** RM {stock_monthly_pmt:.2f}")

# --- CALCULATION FUNCTIONS (Future Value of Annuity) ---
def calculate_fva(monthly_pmt, annual_rate, total_months):
    if monthly_pmt == 0:
        return np.zeros(total_months + 1)
    monthly_rate = annual_rate / 12
    values = [0]
    for m in range(1, total_months + 1):
        val = monthly_pmt * (((1 + monthly_rate)**m - 1) / monthly_rate)
        values.append(val)
    return np.array(values)

# --- CALCULATING THE 3 PATHS ---
epf_100_path = calculate_fva(total_investment, EPF_RATE_ANNUAL, months)
stock_100_path = calculate_fva(total_investment, STOCK_RATE_ANNUAL, months)

epf_hybrid = calculate_fva(epf_monthly_pmt, EPF_RATE_ANNUAL, months)
stock_hybrid = calculate_fva(stock_monthly_pmt, STOCK_RATE_ANNUAL, months)
hybrid_path = epf_hybrid + stock_hybrid

# --- INFLATION ADJUSTMENT (Real Value of the Hybrid Path) ---
real_value_hybrid = hybrid_path[-1] / ((1 + INFLATION_RATE) ** investment_years)

# --- VOLATILITY RATING ---
volatility_score = 1 + (stock_percentage / 100) * 9

# --- MAIN DASHBOARD AREA ---
col1, col2, col3 = st.columns(3)

with col1:
    st.info("🛡️ **100% EPF (Wealth Protector)**")
    st.metric(label=f"Estimated Value ({investment_years} Yrs)", value=f"RM {epf_100_path[-1]:,.2f}")

with col2:
    st.success("⚖️ **Your Custom Hybrid Path**")
    st.metric(label=f"Estimated Value ({investment_years} Yrs)", value=f"RM {hybrid_path[-1]:,.2f}")

with col3:
    st.warning("📈 **100% Stocks (Wealth Creator)**")
    st.metric(label=f"Estimated Value ({investment_years} Yrs)", value=f"RM {stock_100_path[-1]:,.2f}")

st.divider()

# --- GRAPHING MULTIPLE PATHS ---
st.subheader(f"📈 {investment_years}-Year Wealth Projection")

df = pd.DataFrame({
    'Month': np.arange(months + 1),
    '100% EPF': epf_100_path,
    'Your Hybrid': hybrid_path,
    '100% Stocks': stock_100_path
})

fig = px.line(df, x='Month', y=['100% EPF', 'Your Hybrid', '100% Stocks'],
              labels={'value': 'Total Wealth (RM)', 'variable': 'Investment Path'},
              color_discrete_map={'100% EPF': 'blue', 'Your Hybrid': 'green', '100% Stocks': 'orange'})
fig.update_layout(hovermode="x unified")
st.plotly_chart(fig, use_container_width=True)


# --- NEW: MATHEMATICAL CALCULATIONS SECTION ---
st.divider()
st.subheader("🧮 Investment Mathematics Breakdown")

with st.expander("Click here to see the Step-by-Step Mathematical Formulas"):
    st.write("### 1. Future Value of an Annuity (FVA)")
    st.write("We use this formula to calculate the future value of a series of equal monthly payments, compounding monthly.")
    
    # Using LaTeX for mathematical formulas
    st.latex(r"FV = P \times \frac{(1 + r)^n - 1}{r}")
    
    st.write("**Where based on your current inputs:**")
    st.markdown(f"""
    * **$FV$** = Future Value (Final Amount)
    * **$P$** = Monthly Payment
    * **$r$** = Monthly Interest Rate (Annual Rate ÷ 12)
    * **$n$** = Total number of months ({investment_years} years × 12 = **{months} months**)
    """)
    
    st.write("#### Example: Calculating Your EPF Portion")
    epf_r = EPF_RATE_ANNUAL / 12
    st.latex(rf"FV_{{EPF}} = {epf_monthly_pmt:.2f} \times \frac{{(1 + {epf_r:.5f})^{{{months}}} - 1}}{{{epf_r:.5f}}}")
    st.latex(rf"FV_{{EPF}} = RM \ {epf_hybrid[-1]:,.2f}")

    st.write("#### Example: Calculating Your Stocks Portion")
    stock_r = STOCK_RATE_ANNUAL / 12
    st.latex(rf"FV_{{Stocks}} = {stock_monthly_pmt:.2f} \times \frac{{(1 + {stock_r:.5f})^{{{months}}} - 1}}{{{stock_r:.5f}}}")
    st.latex(rf"FV_{{Stocks}} = RM \ {stock_hybrid[-1]:,.2f}")
    
    st.write(f"**Total Hybrid Value** = RM {epf_hybrid[-1]:,.2f} + RM {stock_hybrid[-1]:,.2f} = **RM {hybrid_path[-1]:,.2f}**")

    st.divider()

    st.write("### 2. Real vs. Nominal Value (Inflation Adjustment)")
    st.write("To find the *Real Purchasing Power* in today's money, we discount the final amount by the average inflation rate.")
    
    st.latex(r"Real\ Value = \frac{Nominal\ Value}{(1 + i)^t}")
    
    st.write("**Where:**")
    st.markdown(f"""
    * **$Nominal\ Value$** = Final calculated wealth (RM {hybrid_path[-1]:,.2f})
    * **$i$** = Annual Inflation Rate ({INFLATION_RATE*100}%)
    * **$t$** = Number of Years ({investment_years})
    """)
    
    st.latex(rf"Real\ Value = \frac{{{hybrid_path[-1]:,.2f}}}{{(1 + 0.03)^{{{investment_years}}}}}")
    st.latex(rf"Real\ Value = RM \ {real_value_hybrid:,.2f}")


# --- ANALYSIS & RISK/RETURN SECTION ---
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
