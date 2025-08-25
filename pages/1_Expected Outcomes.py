import streamlit as st
import numpy as np
import pandas as pd

# ---- Page Content ----

st.set_page_config(page_title='Expected Outcomes', layout='wide')
st.title('🎯 Expected Outcomes')

st.markdown("### ✅ Key Deliverables")
st.write("""
- Insights on financial performance under multiple conditions  
- Visualization of scenario-based growth trends    
""")

st.success("The expected outcomes serve as the foundation for deeper analysis and modelling.")

# ---------------------------------------------
# Page setup
# ---------------------------------------------
st.set_page_config(
    page_title="Buying vs Renting in Kuala Lumpur: 30-Year Wealth Simulation",
    page_icon="🏠",
    layout="wide",
)

st.title("🏠 Buying vs Renting in Kuala Lumpur: 30-Year Wealth Simulation")

# ---------------------------------------------
# Core financial functions
# ---------------------------------------------
def monthly_mortgage_payment(principal: float, annual_rate: float, years: int) -> float:
    """Calculate monthly mortgage payment."""
    r = annual_rate / 12.0
    n = years * 12
    if annual_rate == 0:
        return principal / n
    return principal * (r * (1 + r) ** n) / ((1 + r) ** n - 1)

def fv_lump_sum(pv: float, annual_rate: float, years: int) -> float:
    """Future value of a lump sum investment."""
    return pv * ((1 + annual_rate) ** years)

def fv_monthly_annuity(pmt: float, annual_rate: float, years: int) -> float:
    """Future value of monthly contributions."""
    r = annual_rate / 12.0
    n = years * 12
    if annual_rate == 0:
        return pmt * n
    return pmt * (((1 + r) ** n - 1) / r)

def buy_vs_rent_wealth(
    house_price: float = 800_000.0,
    down_pct: float = 0.10,
    mortgage_rate: float = 0.04,
    term_years: int = 30,
    rent_yield: float = 0.045,
    invest_return: float = 0.06,
    home_appreciation: float = 0.02,
):
    """Compare long-term wealth between buying and renting."""
    loan = house_price * (1 - down_pct)
    down = house_price * down_pct

    # Monthly mortgage and rent
    m_mort = monthly_mortgage_payment(loan, mortgage_rate, term_years)
    monthly_rent = (house_price * rent_yield) / 12.0
    monthly_contribution = m_mort - monthly_rent

    # Wealth calculations
    buy_wealth = fv_lump_sum(house_price, home_appreciation, term_years)
    rent_wealth = fv_lump_sum(down, invest_return, term_years) + \
                  fv_monthly_annuity(monthly_contribution, invest_return, term_years)
    diff = buy_wealth - rent_wealth
    return buy_wealth, rent_wealth, diff

# ---------------------------------------------
# Sidebar — Inputs
# ---------------------------------------------
st.sidebar.header("Inputs")
house_price = st.sidebar.number_input(
    "House Price (RM)", min_value=100000, max_value=5_000_000,
    value=800_000, step=10_000, format="%d"
)
down_pct = st.sidebar.slider("Down Payment (%)", 0.0, 0.9, 0.10, 0.01)
mortgage_rate = st.sidebar.slider("Mortgage Rate (%)", 0.0, 10.0, 4.0, 0.1) / 100.0
term_years = st.sidebar.slider("Loan Term (years)", 5, 40, 30, 1)
rent_yield = st.sidebar.slider("Rent Yield (% of property / year)", 0.0, 10.0, 4.5, 0.1) / 100.0
invest_return = st.sidebar.slider("Investment Return (%)", 0.0, 15.0, 6.0, 0.1) / 100.0
home_appreciation = st.sidebar.slider("Home Appreciation (%)", 0.0, 10.0, 2.0, 0.1) / 100.0

# Compute base case
buy_wealth, rent_wealth, diff = buy_vs_rent_wealth(
    house_price=house_price,
    down_pct=down_pct,
    mortgage_rate=mortgage_rate,
    term_years=term_years,
    rent_yield=rent_yield,
    invest_return=invest_return,
    home_appreciation=home_appreciation,
)

# ---------------------------------------------
# Results — Metrics
# ---------------------------------------------
col1, col2, col3 = st.columns(3)
col1.metric("Buying Wealth (RM)", f"RM {buy_wealth:,.0f}")
col2.metric("Renting Wealth (RM)", f"RM {rent_wealth:,.0f}")
col3.metric("Buy − Rent (RM)", f"RM {diff:,.0f}",
            help="Positive means buying leads; negative means renting + investing leads.")

st.divider()

# ---------------------------------------------
# Expected Outcomes
# ---------------------------------------------
st.subheader("Simple Expected Outcomes")

exp_cols = st.columns(2)
with exp_cols[0]:
    st.markdown("""
    **When Buying Wins**
    - Mortgage rates are **low (≤ 4%)**
    - Property appreciation is **steady (≥ 2%/yr)**
    - Rent is **expensive (≥ 4.5% of price)**
    - Over **long horizons (≈30 yrs)**
    """)

with exp_cols[1]:
    st.markdown("""
    **When Renting Wins**
    - Mortgage rates are **high (≥ 5.5%)**
    - Property prices **stagnate (~0%)**
    - Investments return **≥ 7–8%**
    - Rent is **cheap (≤ 3.5% of price)**
    """)

st.info(
    "These summaries align with the uploaded report's base-case logic for Kuala Lumpur "
    "and are meant as quick decision cues."
)

st.divider()

# ---------------------------------------------
# Sources
# ---------------------------------------------
st.subheader("Sources (from the document)")

# List of references as (Title, URL) tuples directly in the script
sources = [
    ("[1] Malaysia's Residential Property Market Analysis 2025 — Global Property Guide",
     "https://www.globalpropertyguide.com/asia/malaysia/price-history"),
    ("[2] Rental Yields in Malaysia in 2025, Q1 — Global Property Guide",
     "https://www.globalpropertyguide.com/asia/malaysia/rental-yields"),
    ("[3] Base Lending Rates — Maybank Malaysia",
     "https://www.maybank2u.com.my/maybank2u/malaysia/en/personal/rates/blr_rates.page"),
    ("[4] Malaysia c.bank lowers key rate to 2.75% — Reuters",
     "https://www.reuters.com/world/asia-pacific/malaysia-cbank-lowers-key-rate-275-2025-07-09/"),
    ("[5] Malaysia Inflation (CPI) — FocusEconomics",
     "https://www.focus-economics.com/country-indicator/malaysia/inflation/"),
    ("[6] EPF Dividend 2024 — KWSP Malaysia",
     "https://www.kwsp.gov.my/en/others/resource-centre/dividend"),
    ("[7] Buy vs Rent in Malaysia — KWSP Malaysia",
     "https://www.kwsp.gov.my/en/w/article/buy-vs-rent-malaysia"),
    ("[8] Archer, W. R., & Smith, B. C. (2013). Residential real estate and rent-versus-own decisions.",
     "https://doi.org/10.1080/10835547.2013.12092057"),
    # ... add all remaining references here ...
    ("[21] Yusof, R., & Ismail, R. (2020). Housing affordability and financing in Malaysia: Issues and policy directions.",
     "https://doi.org/10.3923/ajef.2020.45.58")
]

# Display references in Streamlit
for label, url in sources:
    st.markdown(f"- {label}  \n  [Link]({url})", unsafe_allow_html=True)

st.caption("*App logic is based on the assumptions in the uploaded report for comparability.*")
