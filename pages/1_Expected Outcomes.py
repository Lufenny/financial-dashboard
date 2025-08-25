import streamlit as st
import numpy as np
import pandas as pd

# ---- Page Content ----

st.set_page_config(page_title='Expected Outcomes', layout='wide')
st.title('🎯 Expected Outcomes')
st.markdown('This section outlines the intended results of the analysis, ensuring clear alignment between objectives and deliverables.')

st.markdown("### ✅ Key Deliverables")
st.write("""
- Insights on financial performance under multiple conditions  
- Visualization of scenario-based growth trends  
- Identification of potential risks and opportunities  
- Structured reporting for decision-making  
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
SOURCES = [
Archer, W. R., & Smith, B. C. (2013). *Residential real estate and rent-versus-own decisions.* _Journal of Real Estate Research, 35_(1), 1–29.

Bank Negara Malaysia. (2022). *Monetary policy statement and OPR trends.* Kuala Lumpur: Bank Negara Malaysia. https://www.bnm.gov.my

Employees Provident Fund. (2022). *Annual report and dividend announcement.* Kuala Lumpur: EPF.

Employees Provident Fund. (2024). *EPF Dividend 2024.* https://www.kwsp.gov.my/en/others/resource-centre/dividend

Employees Provident Fund. (2025). *Buy vs rent in Malaysia: 5 questions to help you decide.* https://www.kwsp.gov.my/en/w/article/buy-vs-rent-malaysia

Global Property Guide. (2025a). *Malaysia's residential property market analysis 2025.* https://www.globalpropertyguide.com/asia/malaysia/price-history

Global Property Guide. (2025b). *Rental yields in Malaysia in 2025, Q1.* https://www.globalpropertyguide.com/asia/malaysia/rental-yields

Maybank Malaysia. (2025). *Base lending rates.* https://www.maybank2u.com.my/maybank2u/malaysia/en/personal/rates/blr_rates.page

Reuters. (2025, July 9). *Malaysia c.bank lowers key rate to 2.75%.* https://www.reuters.com/world/asia-pacific/malaysia-cbank-lowers-key-rate-275-2025-07-09/

FocusEconomics. (2025). *Malaysia inflation (CPI).* https://www.focus-economics.com/country-indicator/malaysia/inflation/

Goodman, L., & Mayer, C. (2018). *Homeownership and the American dream.* _Journal of Economic Perspectives, 32_(1), 31–58.

Henderson, J. V., & Ioannides, Y. M. (1983). *A model of housing tenure choice.* _American Economic Review, 73_(1), 98–113.

Leung, C. (2004). *Macroeconomics and housing: A review of the literature.* _Journal of Housing Economics, 13_(4), 249–267.

Lufenny. (2025). *Wealth accumulation through homeownership versus renting and investing: Evidence from Kuala Lumpur* [Computer software]. GitHub. https://github.com/Lufenny/financial-dashboard.git

Malpezzi, S. (1999). *A simple error correction model of house prices.* _Journal of Housing Economics, 8_(1), 27–62.

Painter, G., & Redfearn, C. L. (2002). *The role of interest rates in influencing long-run homeownership rates.* _Journal of Real Estate Finance and Economics, 25_(2–3), 243–267.

Sinai, T., & Souleles, N. S. (2005). *Owner-occupied housing as a hedge against rent risk.* _Quarterly Journal of Economics, 120_(2), 763–789.

Tan, T. H. (2012). *Housing satisfaction in medium- and high-cost housing: The case of Greater Kuala Lumpur, Malaysia.* _Habitat International, 36_(1), 108–116.

Yusof, R., & Ismail, R. (2020). *Housing affordability and financing in Malaysia: Issues and policy directions.* _Asian Journal of Economics and Finance, 2_(1), 45–58.    
]

for label, url in SOURCES:
    st.markdown(
        f"- {label}  \\\n"
        f"  <small><a href='{url}' target='_blank'>{url}</a></small>",
        unsafe_allow_html=True,
    )

st.caption("*App logic is based on the assumptions in the uploaded report for comparability.*")
