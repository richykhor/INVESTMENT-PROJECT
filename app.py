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

# ==========================================
# --- INTERACTIVE SIDEBAR (USER INPUT) ---
# ==========================================
st.sidebar.header("💰 Your Investment Plan")
st.sidebar.write("Imagine you have extra money every month. How will you split it?")

total_investment = st.sidebar.number_input("Total Monthly Surplus (RM)", min_value=100, max_value=5000, value=500, step=50)
investment_years = st.sidebar.slider("Investment Duration (Years)", min_value=5, max_value=50, value=30, step=1)
months = investment_years * 12

st.sidebar.subheader("Asset Allocation")
epf_percentage = st.sidebar.slider("Allocation to EPF (%)", min_value=0, max_value=100, value=50, step=10)
stock_percentage = 100 - epf_percentage

epf_monthly_pmt = (epf_percentage/100) * total_investment
stock_monthly_pmt = (stock_percentage/100) * total_investment

st.sidebar.write(f"**EPF Monthly:** RM {epf_monthly_pmt:.2f}")
st.sidebar.write(f"**Stocks Monthly:** RM {stock_monthly_pmt:.2f}")

# --- ADVANCED: LET USERS CHANGE THE RATES ---
st.sidebar.divider()
st.sidebar.subheader("📊 Advanced: Change the Rates")
EPF_RATE_ANNUAL = st.sidebar.slider("EPF Expected Dividend (%)", min_value=3.0, max_value=8.0, value=5.5, step=0.1) / 100
STOCK_RATE_ANNUAL = st.sidebar.slider("Stock Expected Return (%)", min_value=4.0, max_value=15.0, value=9.0, step=0.5) / 100
INFLATION_RATE = st.sidebar.slider("Expected Inflation Rate (%)", min_value=1.0, max_value=8.0, value=3.0, step=0.5) / 100

# ==========================================
# --- MATHEMATICAL CALCULATION ENGINE ---
# ==========================================
def calculate_fva(monthly_pmt, annual_rate, total_months):
    if monthly_pmt == 0:
        return np.zeros(total_months + 1)
    monthly_rate = annual_rate / 12
    values = [0]
    for m in range(1, total_months + 1):
        val = monthly_pmt * (((1 + monthly_rate)**m - 1) / monthly_rate)
        values.append(val)
    return np.array(values)

epf_100_path = calculate_fva(total_investment, EPF_RATE_ANNUAL, months)
stock_100_path = calculate_fva(total_investment, STOCK_RATE_ANNUAL, months)

epf_hybrid = calculate_fva(epf_monthly_pmt, EPF_RATE_ANNUAL, months)
stock_hybrid = calculate_fva(stock_monthly_pmt, STOCK_RATE_ANNUAL, months)
hybrid_path = epf_hybrid + stock_hybrid

real_value_hybrid = hybrid_path[-1] / ((1 + INFLATION_RATE) ** investment_years)
volatility_score = 1 + (stock_percentage / 100) * 9

# ==========================================
# --- MAIN DASHBOARD UI ---
# ==========================================
col1, col2, col3 = st.columns(3)

with col1:
    st.info("🛡️ **100% EPF (Wealth Protector)**")
    st.metric(label=f"Expected Value ({investment_years} Yrs)", value=f"RM {epf_100_path[-1]:,.2f}")

with col2:
    st.success("⚖️ **Your Custom Hybrid Path**")
    st.metric(label=f"Expected Value ({investment_years} Yrs)", value=f"RM {hybrid_path[-1]:,.2f}")

with col3:
    st.warning("📈 **100% Stocks (Wealth Creator)**")
    st.metric(label=f"Expected Value ({investment_years} Yrs)", value=f"RM {stock_100_path[-1]:,.2f}")

st.divider()

# --- INTERACTIVE GRAPH ---
st.subheader(f"📈 {investment_years}-Year Wealth Projection")
st.write("This projection uses assumed average compound growth rates to forecast long-term wealth accumulation.")

df = pd.DataFrame({
    'Month': np.arange(months + 1),
    '100% EPF': epf_100_path,
    'Your Hybrid': hybrid_path,
    '100% Stocks': stock_100_path
})

fig = px.line(df, x='Month', y=['100% EPF', 'Your Hybrid', '100% Stocks'],
              labels={'value': 'Total Wealth (RM)', 'variable': 'Investment Path'},
              color_discrete_map={'100% EPF': '#3498DB', 'Your Hybrid': '#2ECC71', '100% Stocks': '#E67E22'})
fig.update_layout(hovermode="x unified", legend_title_text='Strategy')
st.plotly_chart(fig, use_container_width=True)

# ==========================================
# --- MATHEMATICAL EXPLANATION SECTION ---
# ==========================================
with st.expander("🧮 Click here to see the Step-by-Step Mathematical Formulas"):
    st.write("### 1. Future Value of an Annuity (FVA)")
    st.write("We use this formula to calculate the future value of a series of equal monthly payments, compounding monthly.")
    st.latex(r"FV = P \times \frac{(1 + r)^n - 1}{r}")
    st.write("**Where:**")
    st.markdown(f"""
    * **$FV$** = Future Value (Final Amount)
    * **$P$** = Monthly Payment
    * **$r$** = Monthly Interest Rate (Annual Rate ÷ 12)
    * **$n$** = Total number of months ({investment_years} years × 12 = **{months} months**)
    """)
    st.write("#### Your EPF Portion Calculation:")
    epf_r = EPF_RATE_ANNUAL / 12
    st.latex(rf"FV_{{EPF}} = {epf_monthly_pmt:.2f} \times \frac{{(1 + {epf_r:.5f})^{{{months}}} - 1}}{{{epf_r:.5f}}} = RM \ {epf_hybrid[-1]:,.2f}")

    st.write("#### Your Stocks Portion Calculation:")
    stock_r = STOCK_RATE_ANNUAL / 12
    st.latex(rf"FV_{{Stocks}} = {stock_monthly_pmt:.2f} \times \frac{{(1 + {stock_r:.5f})^{{{months}}} - 1}}{{{stock_r:.5f}}} = RM \ {stock_hybrid[-1]:,.2f}")
    
    st.write(f"**Total Hybrid Value** = RM {epf_hybrid[-1]:,.2f} + RM {stock_hybrid[-1]:,.2f} = **RM {hybrid_path[-1]:,.2f}**")

    st.divider()

    st.write("### 2. Real vs. Nominal Value (Inflation Adjustment)")
    st.latex(r"Real\ Value = \frac{Nominal\ Value}{(1 + i)^t}")
    
    # --- THIS IS THE NEWLY ADDED EXPLANATION PART ---
    st.write("**Where:**")
    st.markdown(f"""
    * **$Nominal\ Value$** = Final calculated wealth (RM {hybrid_path[-1]:,.2f})
    * **$i$** = Annual Inflation Rate ({INFLATION_RATE*100:.1f}%)
    * **$t$** = Total number of years ({investment_years} years)
    """)
    # ------------------------------------------------

    st.latex(rf"Real\ Value = \frac{{{hybrid_path[-1]:,.2f}}}{{(1 + {INFLATION_RATE})^{{{investment_years}}}}} = RM \ {real_value_hybrid:,.2f}")


# ==========================================
# --- STRESS TEST MODULE ---
# ==========================================
st.divider()
st.subheader("⚠️ Stress Test: Evaluating Sequence of Returns Risk")

st.info("In real-world investing, average returns do not protect you from market timing. **'Sequence of Returns Risk'** occurs when a major market downturn happens just as you need to withdraw your funds (e.g., at retirement). Use the slider below to simulate a sudden market crash and observe how the guaranteed nature of EPF acts as a financial anchor, protecting your capital when stocks fall.")

crash_percent = st.slider("Simulate a sudden Stock Market Crash (%)", min_value=0, max_value=60, value=30, step=5) / 100

# Recalculate values after crash
epf_crash_value = epf_100_path[-1] # EPF is guaranteed, it does not crash
stock_crash_value = stock_100_path[-1] * (1 - crash_percent)
hybrid_crash_value = epf_hybrid[-1] + (stock_hybrid[-1] * (1 - crash_percent)) # Only the stock portion crashes

col_c1, col_c2, col_c3 = st.columns(3)

with col_c1:
    st.metric(label="100% EPF After Crash", value=f"RM {epf_crash_value:,.2f}", delta="RM 0.00 (Protected)", delta_color="off")
with col_c2:
    loss_hybrid = hybrid_path[-1] - hybrid_crash_value
    st.metric(label="Your Hybrid After Crash", value=f"RM {hybrid_crash_value:,.2f}", delta=f"- RM {loss_hybrid:,.2f} lost", delta_color="inverse")
with col_c3:
    loss_stock = stock_100_path[-1] - stock_crash_value
    st.metric(label="100% Stocks After Crash", value=f"RM {stock_crash_value:,.2f}", delta=f"- RM {loss_stock:,.2f} lost", delta_color="inverse")

# ==========================================
# --- RISK & INFLATION ANALYSIS ---
# ==========================================
st.divider()
col_a, col_b = st.columns(2)

with col_a:
    st.write("### The Danger of 100% Stocks")
    st.write("As the Stress Test above proves, mathematically, maximum returns equal maximum risk. If you put 100% in stocks, you expose decades of compound interest to sudden market corrections. A **Hybrid Strategy** ensures that even during a crash, your EPF portion guarantees a solid financial floor.")
    st.progress(int(volatility_score * 10))
    st.write(f"**Your Volatility Exposure: {volatility_score:.1f} / 10**")

with col_b:
    st.write("### The Silent Thief: Inflation")
    st.write("If stocks are dangerous, why not put 100% in EPF? Because of **Inflation**. EPF protects your *nominal numbers*, but inflation constantly erodes your *purchasing power*.")
    st.write(f"In nominal terms, your hybrid strategy yields **RM {hybrid_path[-1]:,.2f}**.")
    st.write(f"But adjusted for a {INFLATION_RATE*100:.1f}% annual inflation rate over {investment_years} years:")
    st.markdown(f"**Real Purchasing Power in today's money:** <h3 style='color: red;'>RM {real_value_hybrid:,.2f}</h3>", unsafe_allow_html=True)

st.divider()
st.caption("Group Project by: Ho Jun Chi, Lee Jing Wei, Ku Yong Jie, Tan Qian Yin, Nurul Iman Hannani Binti Ridzuan (MTM3023 K1)")
