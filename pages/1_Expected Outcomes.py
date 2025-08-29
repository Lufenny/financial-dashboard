import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

# --------------------------
# Page Setup
# --------------------------
st.set_page_config(page_title='Expected Outcomes – Baseline', layout='wide')
st.title("📌 Expected Outcomes — Model Baseline (not a forecast)")

st.info("""
**Note on Terminology:**
This page shows a **Model Baseline** — default parameters for illustration 
(e.g., 3% property growth, 6% investment return, 5% mortgage rate, 4% rental yield).

In contrast, the **Scenario Baseline (5%)** in the Scenario Analysis 
is a forward-looking projection based on Malaysia’s EPF long-run average. 
""")

# --------------------------
# Baseline Assumptions (Sidebar)
# --------------------------
st.sidebar.header("⚙️ Model Baseline Assumptions (illustrative)")
initial_property_price = st.sidebar.number_input("Initial Property Price (RM)", value=300_000, step=10_000)
mortgage_years = st.sidebar.slider("Mortgage Term (Years)", 10, 35, 30)
monthly_contribution = st.sidebar.number_input("Monthly Mortgage Contribution (RM)", value=1_200, step=100)
initial_investment = st.sidebar.number_input("Initial Investment for Rent & Invest (RM)", value=50_000, step=10_000)
analysis_years = st.sidebar.slider("Analysis Horizon (Years)", 10, 40, 20)

# Baseline averages (default)
annual_property_growth = 0.03        # 3%
annual_investment_return = 0.06      # 6%
mortgage_rate = 0.05                 # 5%
rent_yield = 0.04                    # 4%

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
    
    # Mortgage/Loan balance
    loan_balance = max(0, loan_balance * (1 + mortgage_rate) - monthly_mortgage*12)
    loan_balances.append(loan_balance)
    
    # Buy equity
    buy_equity = value - loan_balance
    buy_wealth.append(buy_equity)
    
    # Rent & invest
    if i == 0:
        invest_value = initial_investment
    else:
        invest_value = rent_wealth[-1]
    annual_rent = initial_property_price * rent_yield
    invest_value = invest_value * (1 + annual_investment_return) + monthly_mortgage*12 - annual_rent
    rent_wealth.append(invest_value)

# --------------------------
# Convert to DataFrame
# --------------------------
df_baseline = pd.DataFrame({
    "Year": years,
    "PropertyValue": property_value,
    "MortgageBalance": loan_balances,
    "BuyWealth": buy_wealth,
    "RentWealth": rent_wealth
})
df_baseline["Year"] = df_baseline["Year"].astype(int)

# --------------------------
# Display Table
# --------------------------
st.subheader("📊 Model Baseline Outcomes (Illustrative)")
st.dataframe(df_baseline)

# --------------------------
# Plot Wealth Projection
# --------------------------
st.subheader("💰 Wealth Projection – Model Baseline")
fig, ax = plt.subplots(figsize=(12, 5))

ax.plot(df_baseline["Year"], df_baseline["BuyWealth"], label="Buy (Property Equity)", color="blue", marker="o")
ax.plot(df_baseline["Year"], df_baseline["RentWealth"], label="Rent & Invest", color="green", marker="o")

# Year spacing
year_interval = max(1, len(df_baseline)//10)
ax.set_xticks(df_baseline["Year"][::year_interval])
ax.set_xticklabels(df_baseline["Year"][::year_interval], rotation=45)

ax.set_xlabel("Year")
ax.set_ylabel("Value (RM)")
ax.set_title("Model Baseline Wealth Projection – Buy vs Rent & Invest")
ax.grid(True, linestyle="--", alpha=0.5)
ax.legend()
st.pyplot(fig)

# --------------------------
# Interpretation
# --------------------------
st.header("📝 Interpretation (Model Baseline)")
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

# --------------------------
# Sources / References
# --------------------------
st.subheader("📚 Sources / References")
st.markdown("""
- **Property Growth (3% p.a.)**: NAPIC Malaysia, Residential Property Price Index 2010–2025  
- **Investment Return (6% p.a.)**: EPF Annual Dividends 2010–2025  
- **Mortgage Rate (~5%)**: Bank Negara Malaysia OPR + typical bank margin  
- **Rental Yield (4%)**: NAPIC Malaysia / Property portals (iProperty, PropertyGuru)  
- **Initial Property Price (RM300k)**: Example mid-range condo in Kuala Lumpur  
- **Analysis Horizon (20 years)**: Standard long-term financial planning horizon
""")
