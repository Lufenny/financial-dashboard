import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

# --------------------------
# Page Setup
# --------------------------
st.set_page_config(page_title="Expected Outcomes – Buy vs EPF", layout="wide")
st.title("📌 Expected Outcomes – Buy vs EPF Wealth")

# --------------------------
# Baseline Assumptions
# --------------------------
st.sidebar.header("⚙️ Baseline Assumptions")
initial_property_price = st.sidebar.number_input("Initial Property Price (RM)", value=300000, step=10000)
property_growth_rate = st.sidebar.slider("Annual Property Growth Rate (%)", 0.0, 10.0, 5.0) / 100
mortgage_rate = st.sidebar.slider("Mortgage Interest Rate (%)", 0.0, 10.0, 4.0) / 100
loan_term_years = st.sidebar.number_input("Loan Term (Years)", value=20, step=1)
epf_rate = st.sidebar.slider("Annual EPF Dividend Rate (%)", 0.0, 10.0, 5.0) / 100
annual_epf_contribution = st.sidebar.number_input("Annual EPF Contribution (RM)", value=12000, step=1000)
years = st.sidebar.number_input("Projection Horizon (Years)", value=30, step=1)

# --------------------------
# Mortgage Calculation
# --------------------------
P = initial_property_price
r = mortgage_rate
n = loan_term_years
if r > 0:
    PMT = P * (r * (1 + r)**n) / ((1 + r)**n - 1)  # Monthly payment equivalent annualized
else:
    PMT = P / n

# --------------------------
# Projection Loop
# --------------------------
property_values = [P]
mortgage_balances = [P]
buy_wealth = [0]
epf_wealth = [0]

for t in range(1, years + 1):
    # Property growth
    new_property_value = property_values[-1] * (1 + property_growth_rate)
    property_values.append(new_property_value)

    # Mortgage repayment
    interest_payment = mortgage_balances[-1] * r
    principal_payment = PMT - interest_payment
    new_mortgage_balance = max(0, mortgage_balances[-1] - principal_payment)
    mortgage_balances.append(new_mortgage_balance)

    # Buy Wealth = Property Value - Mortgage Balance
    new_buy_wealth = new_property_value - new_mortgage_balance
    buy_wealth.append(new_buy_wealth)

    # EPF Wealth = previous * (1+rate) + contribution
    new_epf_wealth = epf_wealth[-1] * (1 + epf_rate) + annual_epf_contribution
    epf_wealth.append(new_epf_wealth)

# --------------------------
# DataFrame Results
# --------------------------
df = pd.DataFrame({
    "Year": np.arange(0, years + 1),
    "Property Value (RM)": property_values,
    "Mortgage Balance (RM)": mortgage_balances,
    "Buy Wealth (RM)": buy_wealth,
    "EPF Wealth (RM)": epf_wealth
})

# --------------------------
# Plot
# --------------------------
fig, ax = plt.subplots(figsize=(10, 6))
ax.plot(df["Year"], df["Buy Wealth (RM)"], label="🏡 Buy Wealth (Property Equity)", linewidth=2, color="blue")
ax.plot(df["Year"], df["EPF Wealth (RM)"], label="💰 EPF Wealth", linewidth=2, color="green")
ax.set_xlabel("Year")
ax.set_ylabel("Wealth (RM)")
ax.set_title("Buy vs EPF Wealth Projection")
ax.legend()
ax.grid(True)

# --------------------------
# Streamlit Outputs
# --------------------------
st.pyplot(fig)
st.subheader("📊 Projection Table")
st.dataframe(df.style.format({
    "Property Value (RM)": "RM {:,.0f}",
    "Mortgage Balance (RM)": "RM {:,.0f}",
    "Buy Wealth (RM)": "RM {:,.0f}",
    "EPF Wealth (RM)": "RM {:,.0f}"
}), use_container_width=True)

# --------------------------
# Download CSV
# --------------------------
csv = df.to_csv(index=False).encode("utf-8")
st.download_button(
    "⬇️ Download Results (CSV)",
    data=csv,
    file_name="expected_outcomes_buy_vs_epf.csv",
    mime="text/csv"
)
