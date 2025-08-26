import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

st.set_page_config(page_title='Expected Outcomes – Baseline', layout='wide')
st.title("📌 Expected Outcomes – Baseline Comparison")

# --------------------------
# Baseline Assumptions
# --------------------------
st.sidebar.header("⚙️ Baseline Assumptions")

initial_property_price = st.sidebar.number_input("Initial Property Price (RM)", value=300_000, step=10_000)
mortgage_years = st.sidebar.slider("Mortgage Term (Years)", 10, 35, 30)
monthly_contribution = st.sidebar.number_input("Monthly Mortgage Contribution (RM)", value=1_200, step=100)
initial_investment = st.sidebar.number_input("Initial Investment for Rent & Invest (RM)", value=50_000, step=10_000)
analysis_years = st.sidebar.slider("Analysis Horizon (Years)", 10, 40, 20)

# Historical averages (default values)
annual_property_growth = 0.03        # 3%
annual_investment_return = 0.06      # 6%
mortgage_rate = 0.05                  # 5%
rent_yield = 0.04                     # 4%

# --------------------------
# Mortgage Payment Function
# --------------------------
def mortgage_payment(principal, annual_rate, n_years):
    r = annual_rate / 12
    n = n_years * 12
    if r == 0:
        return principal / n
    return principal * r / (1 - (1 + r) ** -n)

monthly_mortgage = mortgage_payment(initial_property_price, mortgage_rate, mortgage_years)

# --------------------------
# Baseline Simulation
# --------------------------
years = list(range(2025, 2025 + analysis_years))
loan_balance = initial_property_price

buy_wealth, rent_wealth, property_value, loan_balances = [], [], [], []

for i, year in enumerate(years):
    value = initial_property_price * ((1 + annual_property_growth) ** i)
    property_value.append(value)
    loan_balance = max(0, loan_balance * (1 + mortgage_rate) - monthly_mortgage*12)
    loan_balances.append(loan_balance)
    buy_equity = value - loan_balance
    buy_wealth.append(buy_equity)
    if i == 0:
        invest_value = initial_investment
    else:
        invest_value = rent_wealth[-1]
    annual_rent = initial_property_price * rent_yield
    invest_value = invest_value * (1 + annual_investment_return) + monthly_mortgage*12 - annual_rent
    rent_wealth.append(invest_value)

df_baseline = pd.DataFrame({
    "Year": [int(y) for y in years],
    "PropertyValue": property_value,
    "MortgageBalance": loan_balances,
    "BuyWealth": buy_wealth,
    "RentWealth": rent_wealth
})

# --------------------------
# Display Table and Plot
# --------------------------
st.subheader("📊 Baseline Outcomes")
st.dataframe(df_baseline)

st.subheader("💰 Wealth Projection (Baseline)")
fig, ax = plt.subplots(figsize=(10, 5))
ax.plot(df_baseline["Year"], df_baseline["BuyWealth"], label="Buy (Property Equity)", color="blue", marker="o")
ax.plot(df_baseline["Year"], df_baseline["RentWealth"], label="Rent & Invest", color="green", marker="o")
ax.set_xlabel("Year")
ax.set_ylabel("Value (RM)")
ax.set_title("Baseline Wealth Projection – Buy vs Rent & Invest")
ax.grid(True, linestyle="--", alpha=0.5)
ax.legend()
st.pyplot(fig)

# --------------------------
# Interpretation
# --------------------------
st.header("📝 Interpretation")
st.write(f"""
Based on the baseline assumptions:
- Property growth ≈ {annual_property_growth*100:.1f}% per year
- Investment return ≈ {annual_investment_return*100:.1f}% per year
- Mortgage rate ≈ {mortgage_rate*100:.1f}%
- Rental yield ≈ {rent_yield*100:.1f}%

**Key Insights:**
- Buying builds steady equity over time, with growth depending on property appreciation.
- Renting & investing can generate higher returns if investment yields exceed property growth.
- This baseline provides a simple, illustrative comparison for planning purposes.
""")
