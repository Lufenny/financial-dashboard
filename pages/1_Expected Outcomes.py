import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker  # ✅ for integer year ticks

st.set_page_config(page_title='Expected Outcomes', layout='wide')
st.title("📌 Expected Outcomes – Baseline Comparison")

# --- Baseline Assumptions (Malaysia context) ---
initial_property_price = 300000   # RM (example condo price)
annual_property_growth = 0.02     # 2% appreciation
mortgage_years = 30
mortgage_rate = 0.04              # 4% interest
monthly_contribution = 200        # RM
initial_investment = 50000        # Rent & invest lump sum
annual_investment_return = 0.05   # 5% (EPF-like return)
years = list(range(2025, 2045))   # 20-year horizon

# --- Mortgage Calculation (Simplified) ---
loan_balance = initial_property_price
annual_mortgage_payment = monthly_contribution * 12

buy_wealth, rent_wealth, property_value, loan_balances = [], [], [], []

for i, year in enumerate(years):
    # Property value grows
    value = initial_property_price * ((1 + annual_property_growth) ** i)
    property_value.append(value)
    
    # Loan balance reduces (simplified linear paydown for demo)
    loan_balance = max(0, loan_balance - annual_mortgage_payment)
    loan_balances.append(loan_balance)
    
    # Buy wealth = equity (property value - outstanding mortgage)
    buy_equity = value - loan_balance
    buy_wealth.append(buy_equity)
    
    # Rent & Invest wealth
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

# --- Display table ---
st.subheader("📊 Baseline Outcomes Data")
st.dataframe(df)

# --- Plot Wealth Comparison ---
st.subheader("💰 Wealth Projection (Baseline)")
fig, ax = plt.subplots(figsize=(10, 5))
ax.plot(df["Year"], df["BuyWealth"], label="Buy (Property Equity)", color="blue", marker="o")
ax.plot(df["Year"], df["RentWealth"], label="Rent & Invest", color="green", marker="o")
ax.set_xlabel("Year")
ax.set_ylabel("Value (RM)")
ax.set_title("Baseline Wealth Projection – Buy vs Rent & Invest")
ax.grid(True, linestyle="--", alpha=0.5)
ax.legend()
ax.xaxis.set_major_locator(mticker.MaxNLocator(integer=True))  # ✅ force integer ticks
st.pyplot(fig)

# --- Plot Property vs Mortgage ---
st.subheader("🏠 Property Value vs Mortgage Balance")
fig2, ax2 = plt.subplots(figsize=(10, 5))
ax2.plot(df["Year"], df["PropertyValue"], label="Property Value", color="orange", marker="o")
ax2.plot(df["Year"], df["MortgageBalance"], label="Mortgage Balance", color="red", marker="o")
ax2.set_xlabel("Year")
ax2.set_ylabel("Value (RM)")
ax2.set_title("Property Value vs Mortgage Balance (Baseline)")
ax2.grid(True, linestyle="--", alpha=0.5)
ax2.legend()
ax2.xaxis.set_major_locator(mticker.MaxNLocator(integer=True))  # ✅ force integer ticks
st.pyplot(fig2)

# --- Interpretation ---
st.header("📝 Interpretation of Expected Outcomes")
st.write("""
Under the baseline assumptions, two distinct wealth trajectories emerge:

- **Rent & Invest** demonstrates stronger compounding effects, growing more rapidly over the 20-year horizon. 
  The combination of an initial RM50,000 lump sum and steady 5% annual returns 
  allows this strategy to accumulate wealth at a faster pace than property ownership.  

- **Buy (Property Ownership)** builds wealth gradually through equity. 
  In the early years, equity remains modest due to high outstanding mortgage balances. 
  Over time, however, property appreciation (≈2% annually) and consistent mortgage repayments 
  reduce liabilities and increase the owner’s stake in the property.  

**Key Insight:**  
Renting and investing appears financially superior under these baseline conditions, 
especially in the short to medium term. Buying becomes more attractive if property appreciation accelerates, 
mortgage rates decrease, or holding periods extend well beyond 20 years.  

This baseline analysis provides a **reference benchmark** before applying sensitivity tests and scenario comparisons, 
which examine how changes in assumptions (e.g., higher appreciation or lower returns) alter long-term outcomes.  
""")
