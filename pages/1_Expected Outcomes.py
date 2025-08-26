import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import os

st.set_page_config(page_title='Expected Outcomes', layout='wide')
st.title("📌 Expected Outcomes – Baseline Comparison")

# --- Load Dataset ---
def load_data(path="Data.csv"):
    if os.path.exists(path):
        return pd.read_csv(path)
    else:
        st.error("❌ Data.csv not found. Please upload or place it in the working directory.")
        st.stop()

df = load_data()

# --- Derive Baseline Assumptions from EDA (historical averages) ---
baseline_property_growth = df["PriceGrowth"].mean() / 100 if "PriceGrowth" in df.columns else 0.02
baseline_investment_return = df["EPF"].mean() / 100 if "EPF" in df.columns else 0.05

# --- Display assumptions ---
st.subheader("📌 Baseline Assumptions (from historical data)")
st.markdown(f"""
- Initial property price: **RM300,000**  
- Mortgage term: **30 years** @ 4% interest (simplified)  
- Monthly mortgage contribution: **RM200**  
- Initial lump sum for Rent & Invest: **RM50,000**  
- Property appreciation (avg PriceGrowth): **{baseline_property_growth*100:.2f}%**  
- Investment return (avg EPF dividend): **{baseline_investment_return*100:.2f}%**  
""")

# --- Parameters ---
initial_property_price = 300000
mortgage_years = 30
mortgage_rate = 0.04
monthly_contribution = 200
initial_investment = 50000
years = list(range(2025, 2045))

# --- Mortgage Calculation (Simplified) ---
loan_balance = initial_property_price
annual_mortgage_payment = monthly_contribution * 12

buy_wealth, rent_wealth, property_value, loan_balances = [], [], [], []

for i, year in enumerate(years):
    # Property value grows
    value = initial_property_price * ((1 + baseline_property_growth) ** i)
    property_value.append(value)
    
    # Loan balance reduces (simplified linear paydown)
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
    invest_value = invest_value * (1 + baseline_investment_return) + annual_mortgage_payment
    rent_wealth.append(invest_value)

# --- Convert to DataFrame ---
df_baseline = pd.DataFrame({
    "Year": years,
    "PropertyValue": property_value,
    "MortgageBalance": loan_balances,
    "BuyWealth": buy_wealth,
    "RentWealth": rent_wealth
})

# --- Display table ---
st.subheader("📊 Baseline Outcomes Data")
st.dataframe(df_baseline)

# --- Plot Wealth Comparison ---
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

# --- Plot Property vs Mortgage ---
st.subheader("🏠 Property Value vs Mortgage Balance")
fig2, ax2 = plt.subplots(figsize=(10, 5))
ax2.plot(df_baseline["Year"], df_baseline["PropertyValue"], label="Property Value", color="orange", marker="o")
ax2.plot(df_baseline["Year"], df_baseline["MortgageBalance"], label="Mortgage Balance", color="red", marker="o")
ax2.set_xlabel("Year")
ax2.set_ylabel("Value (RM)")
ax2.set_title("Property Value vs Mortgage Balance (Baseline)")
ax2.grid(True, linestyle="--", alpha=0.5)
ax2.legend()
st.pyplot(fig2)

# --- Interpretation ---
st.header("📝 Interpretation of Expected Outcomes")
st.write(f"""
- Baseline assumptions are **derived from historical data**: property appreciation ≈ {baseline_property_growth*100:.2f}%, EPF-like returns ≈ {baseline_investment_return*100:.2f}%.  
- **Rent & Invest strategy** grows faster due to compounding, especially with the RM50k initial investment.  
- **Buy strategy** builds equity slowly but steadily as property value rises and mortgage balance declines.  
- Early years favor renting (less debt, more compounding), while later years improve buying as mortgage burden falls.  

This baseline sets a **benchmark reference**, later extended in scenario analysis, sensitivity modelling, and multi-scenario interpretation.
""")
