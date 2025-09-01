import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

st.set_page_config(page_title='Expected Outcomes – Baseline', layout='wide')
st.title("📌 Expected Outcomes – Buy vs Rent+EPF Comparison")

# --------------------------
# Sidebar Inputs (Baseline Assumptions)
# --------------------------
st.sidebar.header("⚙️ Baseline Assumptions")

initial_property_price = st.sidebar.number_input("Initial Property Price (RM)", value=500_000, step=50_000)
mortgage_rate = st.sidebar.number_input("Mortgage Rate (%)", value=4.0, step=0.1) / 100
loan_term_years = st.sidebar.number_input("Loan Term (Years)", value=30, step=1)
property_growth_rate = st.sidebar.number_input("Property Growth Rate (%)", value=3.0, step=0.1) / 100
epf_rate = st.sidebar.number_input("EPF Annual Return (%)", value=5.0, step=0.1) / 100
projection_years = st.sidebar.slider("Projection Horizon (Years)", min_value=5, max_value=40, value=30, step=1)

# --------------------------
# Mortgage Payment (PMT)
# --------------------------
def calculate_mortgage_payment(P, r, n):
    if r > 0:
        return P * (r * (1 + r)**n) / ((1 + r)**n - 1)
    else:
        return P / n

PMT = calculate_mortgage_payment(initial_property_price, mortgage_rate, loan_term_years)

# --------------------------
# Wealth Projection
# --------------------------
def project_wealth(P, r, n, g, epf_rate, years):
    mortgage_balance = P
    buy_wealth = []
    epf_wealth = []
    property_value = P
    
    for t in range(1, years+1):
        # Property wealth
        property_value *= (1 + g)
        if t <= n:
            interest = mortgage_balance * r
            principal = PMT - interest
            mortgage_balance -= principal
        buy_wealth.append(property_value - max(mortgage_balance, 0))
        
        # Rent + EPF (use PMT as contribution)
        if t == 1:
            epf_wealth.append(PMT)
        else:
            epf_wealth.append(epf_wealth[-1] * (1 + epf_rate) + PMT)
    
    df = pd.DataFrame({
        "Year": np.arange(1, years+1),
        "Buy Wealth (RM)": buy_wealth,
        "EPF Wealth (RM)": epf_wealth
    })
    return df

df = project_wealth(initial_property_price, mortgage_rate, loan_term_years,
                    property_growth_rate, epf_rate, projection_years)

# --------------------------
# CAGR Calculation
# --------------------------
def compute_cagr_over_time(df):
    years = df["Year"].astype(float).values
    buy_values = df["Buy Wealth (RM)"].values
    epf_values = df["EPF Wealth (RM)"].values

    buy_cagr = np.zeros_like(years, dtype=float)
    epf_cagr = np.zeros_like(years, dtype=float)

    for i in range(1, len(years)):
        buy_cagr[i] = (buy_values[i] / buy_values[0])**(1/years[i]) - 1 if buy_values[0] > 0 else 0
        epf_cagr[i] = (epf_values[i] / epf_values[0])**(1/years[i]) - 1 if epf_values[0] > 0 else 0

    return years, buy_cagr, epf_cagr

# --------------------------
# Breakeven Finder
# --------------------------
def find_breakeven(df):
    for i in range(len(df)):
        if df["EPF Wealth (RM)"].iloc[i] > df["Buy Wealth (RM)"].iloc[i]:
            return df["Year"].iloc[i]
    return None

# --------------------------
# Plots
# --------------------------
def plot_wealth_projection(df):
    fig, ax = plt.subplots(figsize=(10,6))
    ax.plot(df["Year"], df["Buy Wealth (RM)"], label="Buy Property", color="blue", linewidth=2)
    ax.plot(df["Year"], df["EPF Wealth (RM)"], label="Rent + EPF", color="green", linewidth=2)
    
    # Add breakeven marker
    breakeven_year = find_breakeven(df)
    if breakeven_year:
        ax.axvline(breakeven_year, color="red", linestyle="--", alpha=0.7, linewidth=2)
        ax.text(breakeven_year+0.5, ax.get_ylim()[1]*0.9,
                f"Breakeven Year: {breakeven_year}",
                color="red", fontsize=10, weight="bold")
    
    ax.set_title("Wealth Projection", fontsize=14, weight="bold")
    ax.set_xlabel("Year")
    ax.set_ylabel("Wealth (RM)")
    ax.legend()
    ax.grid(True, linestyle="--", alpha=0.6)
    return fig

def plot_cagr_over_time(df):
    years, buy_cagr, epf_cagr = compute_cagr_over_time(df)
    fig, ax = plt.subplots(figsize=(10,6))
    
    ax.plot(years, buy_cagr*100, label="Buy Property CAGR", color="blue", linewidth=2)
    ax.plot(years, epf_cagr*100, label="Rent+EPF CAGR", color="green", linewidth=2)
    
    # Add breakeven marker
    breakeven_year = find_breakeven(df)
    if breakeven_year:
        ax.axvline(breakeven_year, color="red", linestyle="--", alpha=0.7, linewidth=2)
        ax.text(breakeven_year+0.5, ax.get_ylim()[1]*0.9,
                f"Breakeven Year: {breakeven_year}",
                color="red", fontsize=10, weight="bold")
    
    ax.set_title("CAGR Over Time", fontsize=14, weight="bold")
    ax.set_xlabel("Year")
    ax.set_ylabel("CAGR (% p.a.)")
    ax.legend()
    ax.grid(True, linestyle="--", alpha=0.6)
    return fig

# --------------------------
# Layout Tabs
# --------------------------
tab1, tab2, tab3 = st.tabs(["📈 Wealth Projection", "📊 CAGR Over Time", "📋 Data Table"])

with tab1:
    st.pyplot(plot_wealth_projection(df))

with tab2:
    st.pyplot(plot_cagr_over_time(df))

with tab3:
    st.dataframe(df.style.format({"Buy Wealth (RM)": "RM{:,.0f}", "EPF Wealth (RM)": "RM{:,.0f}"}))
