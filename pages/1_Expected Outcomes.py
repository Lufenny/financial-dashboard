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

# --------------------------
# 2. Sidebar – Baseline Assumptions
# --------------------------
st.sidebar.header("⚙️ Baseline Assumptions")

initial_property_price = st.sidebar.number_input("Initial Property Price (RM)", value=500000, step=10000)
mortgage_rate = st.sidebar.number_input("Mortgage Interest Rate (%)", value=4.0, step=0.1) / 100
loan_term_years = st.sidebar.number_input("Loan Term (Years)", value=30, step=1)
property_growth = st.sidebar.number_input("Property Growth Rate (%)", value=3.0, step=0.1) / 100
epf_rate = st.sidebar.number_input("EPF Growth Rate (%)", value=5.0, step=0.1) / 100
rent_yield = st.sidebar.number_input("Rent Yield (%)", value=3.0, step=0.1) / 100
projection_years = st.sidebar.number_input("Projection Horizon (Years)", value=30, step=1)

# --------------------------
# 3. Helper Functions
# --------------------------
def calculate_mortgage_payment(P, r, n):
    """Annual mortgage repayment using annuity formula"""
    if r > 0:
        return P * (r * (1 + r) ** n) / ((1 + r) ** n - 1)
    else:
        return P / n

def calculate_cagr(final_value, initial_value, years):
    """Compound Annual Growth Rate (CAGR)"""
    if initial_value <= 0 or final_value <= 0 or years <= 0:
        return 0
    return (final_value / initial_value) ** (1 / years) - 1

def project_outcomes(P, r, n, g, epf_rate, rent_yield, years):
    """Simulate Buy vs Rent+Invest outcomes"""
    annual_mortgage = calculate_mortgage_payment(P, r, n)

    buy_wealth, epf_wealth, rent_costs = [], [], []
    property_value, epf_balance, rent_cumulative = P, 0, 0

    for year in range(1, years + 1):
        # Property scenario
        property_value *= (1 + g)
        if year <= n:
            property_value -= annual_mortgage
        buy_wealth.append(property_value)

        # Rent scenario: assume mortgage payment goes into EPF after paying rent
        annual_rent = P * rent_yield
        investable = max(annual_mortgage - annual_rent, 0)
        epf_balance = (epf_balance + investable) * (1 + epf_rate)
        epf_wealth.append(epf_balance)
        rent_cumulative += annual_rent
        rent_costs.append(rent_cumulative)

    df = pd.DataFrame({
        "Year": np.arange(1, years + 1),
        "Buy Wealth (RM)": buy_wealth,
        "EPF Wealth (RM)": epf_wealth,
        "Cumulative Rent (RM)": rent_costs
    })

    buy_cagr = calculate_cagr(df["Buy Wealth (RM)"].iloc[-1], df["Buy Wealth (RM)"].iloc[0], years)
    epf_cagr = calculate_cagr(df["EPF Wealth (RM)"].iloc[-1], df["EPF Wealth (RM)"].iloc[0], years)

    return df, buy_cagr, epf_cagr

def format_table(df, buy_cagr, epf_cagr):
    """Format table with CAGR rows"""
    df_fmt = df.copy()
    df_fmt["Buy Wealth (RM)"] = df_fmt["Buy Wealth (RM)"].map("RM {:,.0f}".format)
    df_fmt["EPF Wealth (RM)"] = df_fmt["EPF Wealth (RM)"].map("RM {:,.0f}".format)
    df_fmt["Cumulative Rent (RM)"] = df_fmt["Cumulative Rent (RM)"].map("RM {:,.0f}".format)

    summary_row = pd.DataFrame({
        "Year": ["CAGR"],
        "Buy Wealth (RM)": [f"{buy_cagr*100:.2f}%"],
        "EPF Wealth (RM)": [f"{epf_cagr*100:.2f}%"],
        "Cumulative Rent (RM)": ["-"]
    })
    df_fmt = pd.concat([df_fmt, summary_row], ignore_index=True)
    return df_fmt

def plot_outcomes(df, buy_cagr, epf_cagr, years):
    """Plot Buy vs EPF outcomes with CAGR in legend"""
    fig, ax = plt.subplots(figsize=(10, 6))
    ax.plot(df["Year"], df["Buy Wealth (RM)"], label=f"Buy Wealth (CAGR {buy_cagr*100:.2f}%)", linewidth=2)
    ax.plot(df["Year"], df["EPF Wealth (RM)"], label=f"EPF Wealth (CAGR {epf_cagr*100:.2f}%)", linewidth=2)
    ax.plot(df["Year"], df["Cumulative Rent (RM)"], label="Cumulative Rent", linestyle="--")

    ax.set_title("Wealth Accumulation Comparison", fontsize=14, fontweight="bold")
    ax.set_xlabel("Year")
    ax.set_ylabel("RM Amount")
    ax.legend()
    ax.grid(True, linestyle="--", alpha=0.7)
    return fig

def generate_summary(df, years, buy_cagr, epf_cagr):
    """Generate natural language summary"""
    buy_final = df["Buy Wealth (RM)"].iloc[-1]
    epf_final = df["EPF Wealth (RM)"].iloc[-1]
    rent_final = df["Cumulative Rent (RM)"].iloc[-1]

    if buy_final > epf_final:
        better = "Buying property"
    else:
        better = "Renting + Investing in EPF"

    return f"""
    ### Key Insights
    - After **{years} years**:
        - **Buy Wealth:** RM {buy_final:,.0f} (CAGR {buy_cagr*100:.2f}%)
        - **EPF Wealth:** RM {epf_final:,.0f} (CAGR {epf_cagr*100:.2f}%)
        - **Cumulative Rent Paid:** RM {rent_final:,.0f}
    - ✅ **Better Option:** {better}
    """

# --------------------------
# 4. Run Projection
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
# 5. Tabs
# --------------------------
tab1, tab2, tab3 = st.tabs(["📈 Chart", "📊 Table", "📝 Summary"])

with tab1:
    st.pyplot(plot_outcomes(df, buy_cagr, epf_cagr, projection_years))

with tab2:
    st.dataframe(format_table(df, buy_cagr, epf_cagr), use_container_width=True)

with tab3:
    st.markdown(generate_summary(df, projection_years, buy_cagr, epf_cagr), unsafe_allow_html=True)

# --------------------------
# 6. Download CSV
# --------------------------
csv = df.to_csv(index=False).encode('utf-8')
st.download_button("📥 Download Projection Data (CSV)", csv, "projection.csv", "text/csv", key='download-csv')
