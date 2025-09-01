import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

# --------------------------
# Global Page Config & Font
# --------------------------
st.set_page_config(page_title='Expected Outcomes – Baseline', layout='wide')

# Apply Times New Roman globally
st.markdown(
    """
    <style>
    html, body, [class*="css"]  {
        font-family: 'Times New Roman', serif !important;
    }
    </style>
    """,
    unsafe_allow_html=True
)

plt.rcParams["font.family"] = "Times New Roman"

# --------------------------
# Sidebar Inputs
# --------------------------
st.sidebar.header("⚙️ Baseline Assumptions")
initial_property_price = st.sidebar.number_input("Initial Property Price (RM)", value=500000, step=10000)
mortgage_rate = st.sidebar.number_input("Mortgage Rate (%)", value=4.0, step=0.1) / 100
loan_term_years = st.sidebar.number_input("Loan Term (Years)", value=30, step=1)
annual_property_appreciation = st.sidebar.number_input("Annual Property Appreciation (%)", value=3.0, step=0.1) / 100
annual_epf_return = st.sidebar.number_input("Annual EPF Return (%)", value=5.0, step=0.1) / 100
annual_epf_contribution = st.sidebar.number_input("Annual EPF Contribution (RM)", value=20000, step=1000)
projection_years = st.sidebar.number_input("Projection Period (Years)", value=30, step=1)

# --------------------------
# Mortgage Calculation
# --------------------------
def calculate_mortgage_payment(P, r, n):
    if r > 0:
        PMT = P * (r * (1 + r)**n) / ((1 + r)**n - 1)
    else:
        PMT = P / n
    return PMT

annual_mortgage_payment = calculate_mortgage_payment(initial_property_price, mortgage_rate, loan_term_years)

# --------------------------
# Wealth Projection
# --------------------------
def project_wealth(years, P, r, n, annual_appreciation, epf_return, annual_epf_contribution):
    buy_wealth, epf_wealth = [], []
    property_value = P
    epf_balance = 0

    for year in range(1, years+1):
        # Property path
        property_value *= (1 + annual_appreciation)
        outstanding_mortgage = calculate_mortgage_payment(P, r, n) * min(year, n)
        buy_wealth.append(property_value - outstanding_mortgage)

        # EPF path (same cashflow as mortgage goes into EPF)
        annual_investment = annual_mortgage_payment + annual_epf_contribution
        epf_balance = (epf_balance + annual_investment) * (1 + epf_return)
        epf_wealth.append(epf_balance)

    df = pd.DataFrame({
        "Year": list(range(1, years+1)),
        "Buy Wealth (RM)": buy_wealth,
        "EPF Wealth (RM)": epf_wealth
    })
    return df

df = project_wealth(projection_years, initial_property_price, mortgage_rate, loan_term_years,
                    annual_property_appreciation, annual_epf_return, annual_epf_contribution)

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
        buy_cagr[i] = (buy_values[i] / buy_values[0])**(1/years[i]) - 1
        epf_cagr[i] = (epf_values[i] / epf_values[0])**(1/years[i]) - 1

    return years, buy_cagr, epf_cagr

def plot_cagr_over_time(df):
    years, buy_cagr, epf_cagr = compute_cagr_over_time(df)
    fig, ax = plt.subplots(figsize=(10,6))
    
    ax.plot(years, buy_cagr*100, label="Buy Property CAGR", color="blue", linewidth=2)
    ax.plot(years, epf_cagr*100, label="Rent+EPF CAGR", color="green", linewidth=2)
    
    ax.set_title("CAGR Over Time", fontsize=14, weight="bold")
    ax.set_xlabel("Year")
    ax.set_ylabel("CAGR (% p.a.)")
    ax.legend()
    ax.grid(True, linestyle="--", alpha=0.6)
    return fig

# --------------------------
# Charts
# --------------------------
def plot_wealth_chart(df):
    fig, ax = plt.subplots(figsize=(10,6))
    ax.plot(df["Year"], df["Buy Wealth (RM)"], label="Buy Property Wealth", linewidth=2, color="blue")
    ax.plot(df["Year"], df["EPF Wealth (RM)"], label="Rent + EPF Wealth", linewidth=2, color="green")
    
    ax.set_title("Wealth Projection: Buy vs. Rent + EPF", fontsize=14, weight="bold")
    ax.set_xlabel("Year")
    ax.set_ylabel("Wealth (RM)")
    ax.legend()
    ax.grid(True, linestyle="--", alpha=0.6)
    return fig

# --------------------------
# Summary Stats
# --------------------------
def generate_summary(df, years):
    buy_final = df["Buy Wealth (RM)"].iloc[-1]
    epf_final = df["EPF Wealth (RM)"].iloc[-1]

    buy_cagr = (buy_final / df["Buy Wealth (RM)"].iloc[0])**(1/years) - 1
    epf_cagr = (epf_final / df["EPF Wealth (RM)"].iloc[0])**(1/years) - 1

    if buy_final > epf_final:
        conclusion = f"🏠 Buying property yields **higher wealth** after {years} years."
    else:
        conclusion = f"💼 Renting and investing in EPF yields **higher wealth** after {years} years."

    summary = f"""
    ### 📊 Summary
    - Final Buy Property Wealth: **RM {buy_final:,.0f}**
    - Final Rent + EPF Wealth: **RM {epf_final:,.0f}**
    - CAGR (Buy Property): **{buy_cagr*100:.2f}% p.a.**
    - CAGR (Rent + EPF): **{epf_cagr*100:.2f}% p.a.**

    👉 {conclusion}
    """
    return summary

# --------------------------
# Streamlit Tabs
# --------------------------
st.title("📌 Expected Outcomes – Baseline Comparison")

tab1, tab2, tab3, tab4 = st.tabs(["📈 Wealth Chart","📊 Projection Table","📝 Summary","📊 CAGR Chart"])

with tab1:
    st.pyplot(plot_wealth_chart(df))

with tab2:
    st.dataframe(df.style.format({"Buy Wealth (RM)": "RM {:,.0f}", "EPF Wealth (RM)": "RM {:,.0f}"}))

with tab3:
    st.markdown(generate_summary(df, projection_years))

with tab4:
    st.pyplot(plot_cagr_over_time(df))
