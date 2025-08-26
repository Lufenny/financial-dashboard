import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from itertools import product
import seaborn as sns

st.set_page_config(page_title='Expected Outcomes', layout='wide')
st.title("📌 Expected Outcomes – Baseline Comparison (Data-driven)")

# --------------------------
# Sidebar Inputs
# --------------------------
st.sidebar.header("⚙️ Assumptions & Parameters")

uploaded_file = st.sidebar.file_uploader("Upload Historical Data (CSV)", type=["csv"])
initial_property_price = st.sidebar.number_input("Initial Property Price (RM)", value=300_000, step=10_000)
mortgage_years = st.sidebar.slider("Mortgage Term (Years)", 10, 35, 30)
monthly_contribution = st.sidebar.number_input("Monthly Mortgage Contribution (RM)", value=1_200, step=100)
initial_investment = st.sidebar.number_input("Initial Investment for Rent & Invest (RM)", value=50_000, step=10_000)
analysis_years = st.sidebar.slider("Analysis Horizon (Years)", 10, 40, 20)

# --------------------------
# Load Dataset and Calculate Averages
# --------------------------
if uploaded_file is not None:
    df_data = pd.read_csv(uploaded_file)
    df_data.columns = df_data.columns.str.strip()
    annual_property_growth = df_data["PriceGrowth"].mean() / 100
    annual_investment_return = df_data["EPF"].mean() / 100
    mortgage_rate = df_data["OPR_avg"].mean() / 100 + 0.01
    rent_yield = df_data["RentYield"].mean() / 100
else:
    st.warning("Please upload a valid CSV with columns: PriceGrowth, EPF, OPR_avg, RentYield")
    st.stop()

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
# Baseline Simulation Loop
# --------------------------
years = list(range(2025, 2025 + analysis_years))
loan_balance = initial_property_price

buy_wealth, rent_wealth, property_value, loan_balances = [], [], [], []

for i, year in enumerate(years):
    # Property value
    value = initial_property_price * ((1 + annual_property_growth) ** i)
    property_value.append(value)

    # Loan balance with interest
    loan_balance = max(0, loan_balance * (1 + mortgage_rate) - monthly_mortgage*12)
    loan_balances.append(loan_balance)

    # Buy wealth
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
df = pd.DataFrame({
    "Year": [int(y) for y in years],
    "PropertyValue": property_value,
    "MortgageBalance": loan_balances,
    "BuyWealth": buy_wealth,
    "RentWealth": rent_wealth
})

# --------------------------
# Display Baseline Table
# --------------------------
st.subheader("📊 Baseline Outcomes Data")
st.dataframe(df)

# --------------------------
# Plot Wealth Comparison
# --------------------------
st.subheader("💰 Wealth Projection – Buy vs Rent & Invest")
fig, ax = plt.subplots(figsize=(10, 5))
ax.plot(df["Year"], df["BuyWealth"], label="Buy (Property Equity)", color="blue")
ax.plot(df["Year"], df["RentWealth"], label="Rent & Invest", color="green")
ax.set_xlabel("Year")
ax.set_ylabel("Value (RM)")
ax.set_title("Baseline Wealth Projection – Buy vs Rent & Invest")
ax.grid(True, linestyle="--", alpha=0.5)
ax.legend()
st.pyplot(fig)

# --------------------------
# Baseline Interpretation
# --------------------------
st.header("📝 Interpretation of Expected Outcomes")
st.write(f"""
Based on historical averages (2010–2025 data):
- Property growth ≈ {annual_property_growth*100:.1f}% per year
- EPF-like investment return ≈ {annual_investment_return*100:.1f}% per year
- Mortgage rate ≈ {mortgage_rate*100:.1f}%
- Rental yield ≈ {rent_yield*100:.1f}%

**Key Insights:**
- BuyWealth grows steadily but depends on property appreciation and mortgage interest.
- Rent & Invest can outperform Buy if EPF-like returns exceed property growth + mortgage cost.
- Final Year (Year {years[-1]}):
  - BuyWealth ≈ RM{buy_wealth[-1]:,.0f}
  - RentWealth ≈ RM{rent_wealth[-1]:,.0f}
""")

# --------------------------
# Mini Sensitivity Analysis
# --------------------------
st.header("🔬 Sensitivity Analysis – Final Year Wealth")
st.write("Explore how Buy vs Rent wealth changes under different assumptions:")

# User can select ranges
prop_growth_range = st.slider("Property Growth (%)", 1.0, 6.0, (2.0, 4.0), 0.5)
investment_return_range = st.slider("Investment Return (%)", 2.0, 12.0, (4.0, 8.0), 1.0)
rent_yield_range = st.slider("Rental Yield (%)", 2.0, 6.0, (3.0, 5.0), 0.5)

growth_values = np.arange(prop_growth_range[0]/100, prop_growth_range[1]/100 + 0.001, 0.005)
return_values = np.arange(investment_return_range[0]/100, investment_return_range[1]/100 + 0.001, 0.01)
rent_values = np.arange(rent_yield_range[0]/100, rent_yield_range[1]/100 + 0.001, 0.005)

records = []
for pg, ir, ry in product(growth_values, return_values, rent_values):
    loan = initial_property_price
    invest_val = initial_investment
    buy_final = rent_final = None

    for _ in range(analysis_years):
        # Buy
        value = initial_property_price * ((1 + pg) ** _)
        loan = max(0, loan * (1 + mortgage_rate) - monthly_mortgage*12)
        buy_final = value - loan

        # Rent
        annual_rent = initial_property_price * ry
        invest_val = invest_val * (1 + ir) + monthly_mortgage*12 - annual_rent
        rent_final = invest_val

    records.append([pg*100, ir*100, ry*100, buy_final, rent_final, buy_final - rent_final])

df_sens = pd.DataFrame(records, columns=["PropGrowth(%)","InvestReturn(%)","RentYield(%)","BuyWealth","RentWealth","Difference"])
st.dataframe(df_sens.sort_values("Difference", ascending=False).reset_index(drop=True))

# --------------------------
# Heatmap – Tipping Points
# --------------------------
st.header("🌡️ Sensitivity Heatmap – Buy vs Rent (Final Year)")

# Pivot: average over RentYield
pivot = df_sens.groupby(["PropGrowth(%)","InvestReturn(%)"])["Difference"].mean().reset_index()
heatmap_data = pivot.pivot(index="PropGrowth(%)", columns="InvestReturn(%)", values="Difference")

fig, ax = plt.subplots(figsize=(8,6))
sns.heatmap(heatmap_data, annot=True, fmt=".0f", center=0, cmap="RdBu_r", cbar_kws={'label':'Buy - Rent (RM)'})
ax.set_title("Tipping Point Heatmap – Buy vs Rent (Final Year)")
ax.set_xlabel("Investment Return (%)")
ax.set_ylabel("Property Growth (%)")
st.pyplot(fig)
