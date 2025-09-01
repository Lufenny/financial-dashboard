import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib
import matplotlib.ticker as mticker

# --------------------------
# 1. Global Settings
# --------------------------
st.set_page_config(page_title='Expected Outcomes – Fair Comparison', layout='wide')

# Times New Roman font for Streamlit
st.markdown(
    """
    <style>
    html, body, [class*="css"]  {
        font-family: 'Times New Roman', serif !important;
    }
    </style>
    """,
    unsafe_allow_html=True
)

# Times New Roman for matplotlib
matplotlib.rcParams['font.family'] = 'Times New Roman'

st.title("📌 Expected Outcomes – Buy Property vs Rent+EPF")

import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

st.set_page_config(page_title='Expected Outcomes – Baseline', layout='wide')
st.title("📌 Expected Outcomes – Baseline Comparison")

# --------------------------
# 1. Baseline Assumptions (Sidebar)
# --------------------------
st.sidebar.header("⚙️ Baseline Assumptions")
initial_property_price = st.sidebar.number_input("Initial Property Price (RM)", value=500000, step=10000)
mortgage_rate = st.sidebar.number_input("Mortgage Rate (%)", value=4.0, step=0.1) / 100
loan_term_years = st.sidebar.number_input("Loan Term (Years)", value=30, step=1)
property_growth = st.sidebar.number_input("Property Growth Rate (%)", value=3.0, step=0.1) / 100
epf_rate = st.sidebar.number_input("EPF Annual Return (%)", value=5.0, step=0.1) / 100
rent_yield = st.sidebar.number_input("Rent Yield (%)", value=4.0, step=0.1) / 100
projection_years = st.sidebar.slider("Projection Period (Years)", min_value=5, max_value=40, value=30)

# --------------------------
# 2. Helper Functions
# --------------------------
def calculate_mortgage_payment(P, r, n):
    """Annual mortgage repayment (PMT formula)."""
    if r > 0:
        return P * (r * (1 + r)**n) / ((1 + r)**n - 1)
    else:
        return P / n

def calculate_cagr(final_value, initial_value, years):
    """Compound Annual Growth Rate."""
    if final_value <= 0 or initial_value <= 0:
        return 0
    return (final_value / initial_value) ** (1 / years) - 1

# --------------------------
# 3. Projection Function
# --------------------------
def project_outcomes(P, r, n, g, epf_rate, rent_yield, years):
    mortgage_payment = calculate_mortgage_payment(P, r, n)
    annual_rent = P * rent_yield

    buy_wealth, epf_wealth = [], []
    cumulative_rent = []

    total_buy, total_epf, total_rent = 0, 0, 0

    for year in range(1, years + 1):
        # Property wealth (buy case)
        property_value = P * (1 + g) ** year
        equity = max(property_value - (mortgage_payment * min(year, n)), 0)
        buy_wealth.append(equity)

        # EPF wealth (invest instead of mortgage)
        total_epf = total_epf * (1 + epf_rate) + mortgage_payment
        epf_wealth.append(total_epf)

        # Rent accumulation
        total_rent += annual_rent
        cumulative_rent.append(total_rent)

    df = pd.DataFrame({
        "Year": range(1, years + 1),
        "Buy Wealth (RM)": buy_wealth,
        "EPF Wealth (RM)": epf_wealth,
        "Cumulative Rent (RM)": cumulative_rent
    })

    buy_cagr = calculate_cagr(df["Buy Wealth (RM)"].iloc[-1], P, years)
    epf_cagr = calculate_cagr(df["EPF Wealth (RM)"].iloc[-1], mortgage_payment, years)

    return df, buy_cagr, epf_cagr

# --------------------------
# 4. Visualization
# --------------------------
def plot_outcomes(df, buy_cagr, epf_cagr, years):
    plt.figure(figsize=(10, 6))
    plt.plot(df["Year"], df["Buy Wealth (RM)"], label=f"Buy Wealth (CAGR {buy_cagr:.2%})")
    plt.plot(df["Year"], df["EPF Wealth (RM)"], label=f"EPF Wealth (CAGR {epf_cagr:.2%})")
    plt.plot(df["Year"], df["Cumulative Rent (RM)"], label="Cumulative Rent")

    plt.title(f"Expected Outcomes Over {years} Years", fontsize=14)
    plt.xlabel("Year", fontsize=12)
    plt.ylabel("RM Amount", fontsize=12)
    plt.legend()
    plt.grid(True, linestyle="--", alpha=0.6)
    plt.tight_layout()
    return plt

# --------------------------
# 5. Table Formatting
# --------------------------
def format_table(df):
    return df.style.format({
        "Buy Wealth (RM)": "RM {:,.0f}",
        "EPF Wealth (RM)": "RM {:,.0f}",
        "Cumulative Rent (RM)": "RM {:,.0f}"
    })

# --------------------------
# 6. Summary Generator
# --------------------------
def generate_summary(df, years):
    buy_final = df["Buy Wealth (RM)"].iloc[-1]
    epf_final = df["EPF Wealth (RM)"].iloc[-1]
    rent_final = df["Cumulative Rent (RM)"].iloc[-1]

    return f"""
    ### 📝 Key Summary (After {years} Years)
    - **Final Buy Wealth:** RM {buy_final:,.0f}  
    - **Final EPF Wealth:** RM {epf_final:,.0f}  
    - **Total Rent Paid:** RM {rent_final:,.0f}  

    ✅ This gives a clear comparison between *buying* vs *investing in EPF while renting*.
    """

# --------------------------
# 7. Run Projection
# --------------------------
df, buy_cagr, epf_cagr = project_outcomes(
    P=initial_property_price,
    r=mortgage_rate,
    n=loan_term_years,
    g=property_growth,
    epf_rate=epf_rate,
    rent_yield=rent_yield,
    years=projection_years
)

# --------------------------
# 8. Tabs
# --------------------------
tab1, tab2, tab3 = st.tabs(["📈 Chart", "📊 Table", "📝 Summary"])

with tab1:
    st.pyplot(plot_outcomes(df, buy_cagr, epf_cagr, projection_years))

with tab2:
    st.dataframe(format_table(df), use_container_width=True)

with tab3:
    st.markdown(generate_summary(df, projection_years), unsafe_allow_html=True)

