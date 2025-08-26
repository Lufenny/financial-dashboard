import streamlit as st
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

st.set_page_config(page_title="Buy vs Rent Model", layout="wide")
st.title("🏡 Buy vs Rent Modelling and Sensitivity Analysis")

# --------------------------
# Sidebar Inputs
# --------------------------
st.sidebar.header("📌 Assumptions")

purchase_price = st.sidebar.number_input("Property Price (RM)", value=500000, step=10000)
down_payment_pct = st.sidebar.slider("Down Payment (%)", 0.0, 0.5, 0.1)
mortgage_term = st.sidebar.slider("Mortgage Term (years)", 10, 35, 30)
years = st.sidebar.slider("Analysis Horizon (years)", 5, 40, 20)

# Base-case rates
mortgage_rate = st.sidebar.slider("Mortgage Rate (%)", 2.0, 8.0, 4.0, step=0.1)
prop_appreciation = st.sidebar.slider("Property Appreciation (%)", 0.0, 6.0, 3.0, step=0.1)
rent_yield = st.sidebar.slider("Rental Yield (%)", 2.0, 6.0, 4.0, step=0.1)
investment_return = st.sidebar.slider("Investment Return (%)", 2.0, 12.0, 6.0, step=0.1)

# --------------------------
# Functions
# --------------------------
def mortgage_payment(principal, annual_rate, n_years):
    r = annual_rate / 12
    n = n_years * 12
    if r == 0:
        return principal / n
    return principal * r / (1 - (1 + r) ** -n)

def outstanding_balance(principal, annual_rate, n_years, months_elapsed):
    r = annual_rate / 12
    n = n_years * 12
    pmt = mortgage_payment(principal, annual_rate, n_years)
    balance = principal * (1 + r)**months_elapsed - pmt * ((1 + r)**months_elapsed - 1) / r
    return balance

# --------------------------
# Base-case Buy vs Rent Simulation
# --------------------------
dp = purchase_price * down_payment_pct
loan = purchase_price - dp
pmt = mortgage_payment(loan, mortgage_rate/100, mortgage_term)

years_list = np.arange(1, years+1)
buy_equity, rent_portfolio = [], []

for t in years_list:
    Vt = purchase_price * (1 + prop_appreciation/100)**t
    bal = outstanding_balance(loan, mortgage_rate/100, mortgage_term, t*12)
    eq = Vt - bal
    buy_equity.append(eq)
    
    annual_rent = purchase_price * rent_yield * (1.02**(t-1))  # rent grows 2% annually
    invested = (rent_portfolio[-1] if t > 1 else dp)
    invested = invested * (1 + investment_return/100) + (pmt*12 - annual_rent)
    rent_portfolio.append(invested)

df_base = pd.DataFrame({
    "Year": years_list,
    "BuyEquity": buy_equity,
    "RentPortfolio": rent_portfolio,
    "Difference": np.array(buy_equity) - np.array(rent_portfolio)
})

# --------------------------
# Base-case Charts
# --------------------------
st.subheader("📊 Wealth Accumulation Over Time")
st.line_chart(df_base.set_index("Year")[["BuyEquity","RentPortfolio"]])

st.subheader("📈 Final Comparison")
st.write(f"After {years} years:")
st.write(f"- Buy Equity: RM{buy_equity[-1]:,.0f}")
st.write(f"- Rent & Invest Portfolio: RM{rent_portfolio[-1]:,.0f}")
st.write(f"- Difference: RM{df_base['Difference'].iloc[-1]:,.0f}")

# --------------------------
# Sensitivity Analysis (4 Parameters) with Year
# --------------------------
st.subheader("🧮 Sensitivity Analysis (4 Parameters)")

mortgage_rates = [3, 4, 5, 6, 7]          # Mortgage %
investment_returns = [4, 5, 6, 7, 8]      # Investment %
appreciations = [2, 3, 4]                 # Property appreciation %
rent_yields = [3, 4, 5]                   # Rental yields %

records = []

for t in range(1, years+1):  # loop over years
    for mr in mortgage_rates:
        for ir in investment_returns:
            for g in appreciations:
                for ry in rent_yields:
                    # Buy side
                    Vt = purchase_price * (1 + g/100)**t
                    bal = outstanding_balance(loan, mr/100, mortgage_term, t*12)
                    eq = Vt - bal
                    
                    # Rent side
                    annual_rent = purchase_price * ry
                    rent_val = dp * (1 + ir/100)**t + (pmt*12 - annual_rent) * (((1 + ir/100)**t - 1) / (ir/100))
                    
                    diff = eq - rent_val
                    records.append([t, mr, ir, g, ry, eq, rent_val, diff])

df_sens = pd.DataFrame(
    records,
    columns=["Year","MortgageRate","InvestReturn","Appreciation","RentYield","BuyEquity","RentPortfolio","Difference"]
)

# --------------------------
# Download CSV
# --------------------------
csv = df_sens.to_csv(index=False).encode("utf-8")
st.download_button(
    "⬇️ Download Sensitivity Results (CSV)",
    data=csv,
    file_name="buy_vs_rent_sensitivity.csv",
    mime="text/csv"
)

# --------------------------
# Optional: Quick Heatmap Preview (Final Year)
# --------------------------
st.subheader("Heatmap Preview – Final Year Scenarios")
df_final_year = df_sens[df_sens['Year']==years]
pivot = df_final_year.pivot_table(
    index='MortgageRate',
    columns='InvestReturn',
    values='Difference',
    aggfunc='mean'
).fillna(0)

fig, ax = plt.subplots(figsize=(6,4))
sns.heatmap(pivot, annot=True, fmt=".0f", center=0, cmap="RdBu_r", cbar_kws={'label':'Buy - Rent (RM)'})
plt.title(f"Tipping Map – {years} yrs")
st.pyplot(fig)
