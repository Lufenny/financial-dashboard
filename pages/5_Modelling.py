import streamlit as st
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

st.set_page_config(page_title="Buy vs Rent Model", layout="wide")
st.title("🏡 Buy vs Rent Modelling and Sensitivity Analysis")

# --------------------------
# Sidebar Inputs
# --------------------------
st.sidebar.header("📌 Assumptions")

purchase_price = st.sidebar.number_input("Property Price (RM)", value=500000, step=10000)
down_payment_pct = st.sidebar.slider("Down Payment (%)", 0.0, 0.5, 0.1)
mortgage_rate = st.sidebar.slider("Mortgage Rate (%)", 2.0, 8.0, 4.0, step=0.1)
mortgage_term = st.sidebar.slider("Mortgage Term (years)", 10, 35, 30)

rent_yield = st.sidebar.slider("Rental Yield (%)", 2.0, 6.0, 4.0, step=0.1)
investment_return = st.sidebar.slider("Investment Return (%)", 2.0, 12.0, 6.0, step=0.1)
prop_appreciation = st.sidebar.slider("Property Appreciation (%)", 0.0, 6.0, 3.0, step=0.1)

years = st.sidebar.slider("Analysis Horizon (years)", 5, 40, 20)

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
# Buy Scenario
# --------------------------
dp = purchase_price * down_payment_pct
loan = purchase_price - dp
pmt = mortgage_payment(loan, mortgage_rate/100, mortgage_term)

years_list = np.arange(1, years+1)
buy_equity = []

for t in years_list:
    Vt = purchase_price * (1 + prop_appreciation/100)**t
    bal = outstanding_balance(loan, mortgage_rate/100, mortgage_term, t*12)
    eq = Vt - bal
    buy_equity.append(eq)

# --------------------------
# Rent + Invest Scenario
# --------------------------
annual_rent = purchase_price * rent_yield
rent_series = [annual_rent * (1.02**t) for t in range(years)]  # rent grows 2%/yr
invested = dp  # renter invests down payment too
rent_vs_buy = []

for t in years_list:
    invested = invested * (1 + investment_return/100) + (pmt*12 - rent_series[t-1])
    rent_vs_buy.append(invested)

# --------------------------
# Results
# --------------------------
df = pd.DataFrame({
    "Year": years_list,
    "Buy_Equity": buy_equity,
    "Rent_Portfolio": rent_vs_buy,
    "Difference": np.array(buy_equity) - np.array(rent_vs_buy)
})

st.subheader("📊 Wealth Accumulation Over Time")
st.line_chart(df.set_index("Year")[["Buy_Equity","Rent_Portfolio"]])

st.subheader("📈 Final Comparison")
st.write(f"After {years} years:")
st.write(f"- Buy Equity: RM{buy_equity[-1]:,.0f}")
st.write(f"- Rent & Invest Portfolio: RM{rent_vs_buy[-1]:,.0f}")
st.write(f"- Difference: RM{df['Difference'].iloc[-1]:,.0f}")

# --------------------------
# Sensitivity Heatmap
# --------------------------
st.subheader("🧮 Sensitivity Analysis")

mortgage_rates = [3, 4, 5, 6, 7]
investment_returns = [4, 5, 6, 7, 8]

records = []
for mr in mortgage_rates:
    for ir in investment_returns:
        buy_end = purchase_price*(1+prop_appreciation/100)**years - outstanding_balance(loan, mr/100, mortgage_term, years*12)
        rent_end = dp*(1+ir/100)**years
        records.append([mr, ir, buy_end-rent_end])

sens = pd.DataFrame(records, columns=["MortgageRate","InvestReturn","Diff"])
pivot = sens.pivot(index="MortgageRate", columns="InvestReturn", values="Diff")

fig, ax = plt.subplots(figsize=(6,4))
sns = __import__('seaborn')
sns.heatmap(pivot, annot=True, fmt=".0f", center=0, cmap="RdBu_r", cbar_kws={'label':'Buy - Rent (RM)'})
plt.title(f"Sensitivity Analysis ({years} years)")
st.pyplot(fig)

# --------------------------
# Download
# --------------------------
csv = df.to_csv(index=False).encode("utf-8")
st.download_button("⬇️ Download Results (CSV)", data=csv, file_name="buy_vs_rent_results.csv", mime="text/csv")
