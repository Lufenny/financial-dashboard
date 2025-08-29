# expected_outcomes_app.py
import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import os

# ----------------------------
# App config
# ----------------------------
st.set_page_config(page_title="Expected Outcomes – Baseline", layout="wide")
st.title("📌 Expected Outcomes — Model Baseline (not a forecast)")

st.info("This page compares **Buy** vs **Rent & Invest** using dataset-driven assumptions when available. "
        "If no dataset is uploaded, the app falls back to illustrative defaults.")

# ----------------------------
# Helper: load dataset
# ----------------------------
@st.cache_data
def load_csv_from_path(path):
    return pd.read_csv(path)

def load_dataset(uploaded_file=None, fallback_path="Data.csv"):
    if uploaded_file is not None:
        df = pd.read_csv(uploaded_file)
    elif os.path.exists(fallback_path):
        df = load_csv_from_path(fallback_path)
    else:
        return None
    return df

# ----------------------------
# Dataset upload (optional)
# ----------------------------
uploaded_file = st.file_uploader("Upload dataset (CSV with columns: PriceGrowth, EPF, OPR_avg, RentYield) — optional", type=["csv"])
df = load_dataset(uploaded_file, fallback_path="Data.csv")

# Determine assumptions from dataset or defaults
required_cols = {"PriceGrowth", "EPF", "OPR_avg", "RentYield"}
if df is not None and required_cols.issubset(set(df.columns)):
    st.success("✅ Dataset loaded — using averages from dataset for assumptions.")
    # Convert to numeric safely
    price_growth_mean = pd.to_numeric(df["PriceGrowth"], errors="coerce").dropna().mean()
    epf_mean = pd.to_numeric(df["EPF"], errors="coerce").dropna().mean()
    opr_mean = pd.to_numeric(df["OPR_avg"], errors="coerce").dropna().mean()
    rent_yield_mean = pd.to_numeric(df["RentYield"], errors="coerce").dropna().mean()

    # Use means (divide by 100 to convert %)
    annual_property_growth = (price_growth_mean / 100.0) if not np.isnan(price_growth_mean) else 0.03
    annual_investment_return = (epf_mean / 100.0) if not np.isnan(epf_mean) else 0.06
    mortgage_rate = (opr_mean / 100.0 + 0.02) if not np.isnan(opr_mean) else 0.05  # OPR + bank spread
    rent_yield = (rent_yield_mean / 100.0) if not np.isnan(rent_yield_mean) else 0.04
else:
    if df is None:
        st.info("No dataset found — using illustrative defaults.")
    else:
        st.warning("Dataset loaded but missing some required columns — using illustrative defaults.")
    annual_property_growth = 0.03
    annual_investment_return = 0.06
    mortgage_rate = 0.05
    rent_yield = 0.04

# Show assumptions summary
with st.expander("🧾 Assumptions (click to expand)", expanded=True):
    st.write(f"- Annual property growth (used in simulation): **{annual_property_growth*100:.2f}%**")
    st.write(f"- Annual investment return (EPF avg): **{annual_investment_return*100:.2f}%**")
    st.write(f"- Mortgage rate (OPR_avg + spread): **{mortgage_rate*100:.2f}%**")
    st.write(f"- Rental yield: **{rent_yield*100:.2f}%**")
    st.write("Note: If a dataset is provided, assumptions are dataset means. Otherwise illustrative defaults are used.")

# ----------------------------
# Sidebar inputs
# ----------------------------
st.sidebar.header("⚙️ User Inputs")
initial_property_price = st.sidebar.number_input("Initial Property Price (RM)", value=300_000, step=10_000)
mortgage_years = st.sidebar.slider("Mortgage Term (Years)", 10, 35, 30)
# user can supply monthly contribution, but we compute monthly mortgage from amortization below
monthly_mortgage_user = st.sidebar.number_input("Monthly Mortgage (RM) — (optional; set 0 to compute from amortization)", value=0, step=100)
initial_investment = st.sidebar.number_input("Initial Investment for Rent & Invest (RM)", value=50_000, step=10_000)
analysis_years = st.sidebar.slider("Analysis Horizon (Years)", 5, 40, 20)

# ----------------------------
# Mortgage payment function (standard amortization)
# ----------------------------
def mortgage_payment(principal, annual_rate, n_years):
    monthly_r = annual_rate / 12.0
    n = n_years * 12
    if monthly_r == 0:
        return principal / n
    return principal * monthly_r / (1 - (1 + monthly_r) ** -n)

# If the user provided a non-zero monthly mortgage, use it; otherwise compute
if monthly_mortgage_user > 0:
    monthly_mortgage = monthly_mortgage_user
else:
    monthly_mortgage = mortgage_payment(initial_property_price, mortgage_rate, mortgage_years)

st.sidebar.markdown(f"**Monthly mortgage used:** RM {monthly_mortgage:,.2f}")

# ----------------------------
# Simulation (realistic: rent deducted every year; rent tracks property value)
# ----------------------------
start_year = 2025
years = list(range(start_year, start_year + analysis_years))
loan_balance = initial_property_price
buy_wealth = []
rent_wealth = []
property_values = []
loan_balances = []
invest_value = initial_investment

for i, year in enumerate(years):
    # 1) property value grows
    value = initial_property_price * ((1 + annual_property_growth) ** i)
    property_values.append(value)

    # 2) loan balance roll-forward (annual view)
    loan_balance = max(0.0, loan_balance * (1 + mortgage_rate) - monthly_mortgage * 12.0)
    loan_balances.append(loan_balance)

    # 3) buy equity
    buy_equity = value - loan_balance
    buy_wealth.append(buy_equity)

    # 4) rent & invest
    annual_rent = value * rent_yield          # rent tracks current property value
    invest_value = invest_value * (1 + annual_investment_return)  # investment growth
    invest_value += monthly_mortgage * 12.0   # savings (would have been mortgage payments)
    invest_value -= annual_rent               # pay rent
    rent_wealth.append(invest_value)

# ----------------------------
# Results DataFrame & Display
# ----------------------------
df_baseline = pd.DataFrame({
    "Year": years,
    "PropertyValue": np.round(property_values, 2),
    "MortgageBalance": np.round(loan_balances, 2),
    "BuyWealth": np.round(buy_wealth, 2),
    "RentWealth": np.round(rent_wealth, 2)
})

st.subheader("📊 Model Baseline Outcomes (Buy vs Rent & Invest)")
st.dataframe(df_baseline.style.format({
    "PropertyValue": "{:,.0f}",
    "MortgageBalance": "{:,.0f}",
    "BuyWealth": "{:,.0f}",
    "RentWealth": "{:,.0f}"
}), height=340)

# ----------------------------
# CSV Download for examiners
# ----------------------------
csv_data = df_baseline.to_csv(index=False).encode("utf-8")
st.download_button(
    label="⬇️ Download Results as CSV",
    data=csv_data,
    file_name="expected_outcomes.csv",
    mime="text/csv"
)

# ----------------------------
# Plot: Buy vs Rent Wealth
# ----------------------------
st.subheader("💰 Wealth Projection — Buy vs Rent & Invest")
fig, ax = plt.subplots(figsize=(12, 5))
ax.plot(df_baseline["Year"], df_baseline["BuyWealth"], label="Buy (Property Equity)", marker="o")
ax.plot(df_baseline["Year"], df_baseline["RentWealth"], label="Rent & Invest", marker="o")
ax.set_xlabel("Year")
ax.set_ylabel("Value (RM)")
ax.set_title("Model Baseline Wealth Projection — Buy vs Rent & Invest")
ax.grid(True, linestyle="--", alpha=0.5)
ax.legend()
fig.tight_layout()

st.pyplot(fig)

# ----------------------------
# Short Interpretation (for exam notes)
# ----------------------------
st.header("📝 Quick Interpretation")
st.write(f"- Property growth used: **{annual_property_growth*100:.2f}%** p.a.  \n"
         f"- Investment return used: **{annual_investment_return*100:.2f}%** p.a.  \n"
         f"- Mortgage rate used: **{mortgage_rate*100:.2f}%** p.a.  \n"
         f"- Rental yield used: **{rent_yield*100:.2f}%** p.a.  \n"
         )
st.write("""
**Key points:**  
- This is a deterministic baseline using EDA-derived averages when available.  
- Rent is applied from year 0 and scales with property value (realistic).  
- The comparison is absolute (RM). For sensitivity, see your Scenario Analysis (5% / 8% / 3%).  
""")
