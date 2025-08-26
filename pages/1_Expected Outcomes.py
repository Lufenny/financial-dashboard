import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

st.set_page_config(page_title='Expected Outcomes', layout='wide')
st.title("📌 Expected Outcomes – Baseline Comparison (Data-driven)")

# --- Load Dataset ---
df_data = pd.read_csv("Data.csv")

# Calculate averages from dataset (2010–2025)
annual_property_growth = df_data["PriceGrowth"].mean() / 100   # convert % → decimal
annual_investment_return = df_data["EPF"].mean() / 100         # convert % → decimal
mortgage_rate = df_data["OPR_avg"].mean() / 100 + 0.01         # OPR avg + margin ≈ mortgage
rent_yield = df_data["RentYield"].mean()                       # for interpretation

# --- Baseline Assumptions ---
initial_property_price = 300000   # RM (example condo price)
mortgage_years = 30
monthly_contribution = 200        # RM
initial_investment = 50000        # Rent & invest lump sum
years = list(range(2025, 2045))   # 20-year horizon

# --- Mortgage Calculation (Simplified) ---
loan_balance = initial_property_price
annual_mortgage_payment = monthly_contribution * 12

buy_wealth, rent_wealth, property_value, loan_balances = [], [], [], []

for i, year in enumerate(years):
    value = initial_property_price * ((1 + annual_property_growth) ** i)
    property_value.append(value)

    loan_balance = max(0, loan_balance - annual_mortgage_payment)
    loan_balances.append(loan_balance)

    buy_equity = value - loan_balance
    buy_wealth.append(buy_equity)

    if i == 0:
        invest_value = initial_investment
    else:
        invest_value = rent_wealth[-1]
    invest_value = invest_value * (1 + annual_investment_return) + annual_mortgage_payment
    rent_wealth.append(invest_value)

# --- Convert to DataFrame ---
df = pd.DataFrame({
    "Year": years,
    "PropertyValue": property_value,
    "MortgageBalance": loan_balances,
    "BuyWealth": buy_wealth,
    "RentWealth": rent_wealth
})

# --- Display ---
st.subheader("📊 Baseline Outcomes Data")
st.dataframe(df)

# --- Plot Wealth Comparison ---
st.subheader("💰 Wealth Projection (Baseline)")
fig, ax = plt.subplots(figsize=(10, 5))
ax.plot(df["Year"], df["BuyWealth"], label="Buy (Property Equity)", color="blue", marker="o")
ax.plot(df["Year"], df["RentWealth"], label="Rent & Invest", color="green", marker="o")
ax.set_xlabel("Year")
ax.set_ylabel("Value (RM)")
ax.set_title("Baseline Wealth Projection – Buy vs Rent & Invest (Data-driven)")
ax.grid(True, linestyle="--", alpha=0.5)
ax.legend()
st.pyplot(fig)

# --- Interpretation ---
st.header("📝 Interpretation of Expected Outcomes")
st.write(f"""
Based on averages from 2010–2025 data:
- Property growth ≈ {annual_property_growth*100:.1f}% per year
- EPF-like investment return ≈ {annual_investment_return*100:.1f}% per year
- Mortgage rate ≈ {mortgage_rate*100:.1f}% 
- Rental yield ≈ {rent_yield:.1f}%

**Key Insight:**
- Rent & Invest remains attractive under current averages due to higher EPF-like returns.
- Buying builds steady equity, but growth depends heavily on property appreciation staying close to {annual_property_growth*100:.1f}%.
- This baseline now directly reflects Malaysia’s historical financial and housing trends.
""")
