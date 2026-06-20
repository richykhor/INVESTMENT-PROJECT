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

# Dynamic Years Slider
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
st.sidebar.subheader("📊 Advanced: Change
