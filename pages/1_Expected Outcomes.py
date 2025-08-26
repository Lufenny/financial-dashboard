import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import seaborn as sns

st.set_page_config(page_title='Expected Outcomes Dashboard', layout='wide')
st.title("📌 Expected Outcomes – Dashboard")

# --------------------------
# Sidebar Inputs
# --------------------------
st.sidebar.header("⚙️ Assumptions & Parameters")

uploaded_file = st.sidebar.file_uploader("Upload Historical Data (CSV, optional)", type=["csv"])
initial_property_price = st.sidebar.number_input("Initial Property Price (RM)", value=300_000, step=10_000)
mortgage_years = st.sidebar.slider("Mortgage Term (Years)", 10, 35, 30)
monthly_contribution = st.sidebar.number_input("Monthly Mortgage Contribution (RM)", value=1_200, step=100)
initial_investment = st.sidebar.number_input("Initial Investment for Rent & Invest (RM)", value=50_000, step=10_000)
analysis_years = st.sidebar.slider("Analysis Horizon (Years)", 10, 40, 20)

# --------------------------
# Load Dataset or Use Defaults
# --------------------------
if uploaded_file is not None:
    df_data = pd.read_csv(uploaded_file)
    df_data.columns = df_data.columns.str.strip()
    annual_property_growth = df_data["PriceGrowth"].mean() / 100
    annual_investment_return = df_data["EPF"].mean() / 100
    mortgage_rate = df_data["OPR_avg"].mean() / 100 + 0.01
    rent_yield = df_data["RentYield"].mean() / 100
else:
    # Default historical averages (2010–2025 example)
    annual_property_growth = 0.03        # 3%
    annual_investment_return = 0.06      # 6%
    mortgage_rate = 0.04 + 0.01          # 4% + margin
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
    "Year": [int(y) for y in years],  # ensure no decimals
    "PropertyValue": property_value,
    "MortgageBalance": loan_balances,
    "BuyWealth": buy_wealth,
    "RentWealth": rent_wealth
})

# --------------------------
# Optimized Sensitivity Analysis
# --------------------------
prop_growth_range = st.sidebar.slider("Property Growth (%)", 1.0, 6.0, (2.0, 4.0), 0.5)
investment_return_range = st.sidebar.slider("Investment Return (%)", 2.0, 12.0, (4.0, 8.0), 1.0)
rent_yield_range = st.sidebar.slider("Rental Yield (%)", 2.0, 6.0, (3.0, 5.0), 0.5)

growth_values = np.arange(prop_growth_range[0]/100, prop_growth_range[1]/100 + 0.001, 0.005)
return_values = np.arange(investment_return_range[0]/100, investment_return_range[1]/100 + 0.001, 0.01)
rent_values = np.arange(rent_yield_range[0]/100, rent_yield_range[1]/100 + 0.001, 0.005)

PG, IR, RY = np.meshgrid(growth_values, return_values, rent_values, indexing='ij')
PG = PG.ravel()
IR = IR.ravel()
RY = RY.ravel()
n = analysis_years

buy_final = (initial_property_price * (1 + PG) ** n) - (initial_property_price * (1 + mortgage_rate) ** n - monthly_mortgage*12 * ((1 + mortgage_rate) ** n - 1) / mortgage_rate)
invest_final = initial_investment * (1 + IR) ** n + (monthly_mortgage*12 - initial_property_price*RY) * (((1+IR)**n - 1)/IR)
diff = buy_final - invest_final

df_sens_opt = pd.DataFrame({
    "PropGrowth(%)": PG*100,
    "InvestReturn(%)": IR*100,
    "RentYield(%)": RY*100,
    "BuyWealth": buy_final,
    "RentWealth": invest_final,
    "Difference": diff
})

# --------------------------
# Dashboard Layout
# --------------------------
col1, col2 = st.columns(2)

# Left: Baseline Table + Plot
with col1:
    st.subheader("📊 Baseline Outcomes")
    st.dataframe(df_baseline)
    fig, ax = plt.subplots(figsize=(8,4))
    ax.plot(df_baseline["Year"], df_baseline["BuyWealth"], label="Buy (Equity)", color="blue")
    ax.plot(df_baseline["Year"], df_baseline["RentWealth"], label="Rent & Invest", color="green")
    ax.set_xlabel("Year")
    ax.set_ylabel("Value (RM)")
    ax.set_title("Baseline Wealth Projection")
    ax.grid(True, linestyle="--", alpha=0.5)
    ax.legend()
    st.pyplot(fig)

# Right: Sensitivity Table + Heatmap
with col2:
    st.subheader("📋 Sensitivity Analysis (Final Year)")
    st.dataframe(df_sens_opt.sort_values("Difference", ascending=False).reset_index(drop=True))
    st.subheader("🌡️ Heatmap – Buy vs Rent")
    pivot = df_sens_opt.groupby(["PropGrowth(%)","InvestReturn(%)"])["Difference"].mean().reset_index()
    heatmap_data = pivot.pivot(index="PropGrowth(%)", columns="InvestReturn(%)", values="Difference")
    fig2, ax2 = plt.subplots(figsize=(8,6))
    sns.heatmap(heatmap_data, annot=True, fmt=".0f", center=0, cmap="RdBu_r", cbar_kws={'label':'Buy - Rent (RM)'})
    ax2.set_title("Tipping Point Heatmap – Buy vs Rent (Final Year)")
    ax2.set_xlabel("Investment Return (%)")
    ax2.set_ylabel("Property Growth (%)")
    st.pyplot(fig2)
