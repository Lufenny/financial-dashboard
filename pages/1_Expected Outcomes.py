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
# 2. Helper Functions
# --------------------------
def calculate_mortgage_payment(P, r, n):
    """Annual mortgage repayment (annuity formula)."""
    if r > 0:
        return P * (r * (1 + r) ** n) / ((1 + r) ** n - 1)
    else:
        return P / n

def calculate_cagr(begin_value, end_value, years):
    """Compound Annual Growth Rate (CAGR)."""
    if begin_value <= 0 or end_value <= 0 or years <= 0:
        return 0
    return (end_value / begin_value) ** (1 / years) - 1

def project_outcomes(P, r, n, g, epf_rate, rent_yield, years):
    """Simulate buy vs EPF outcomes including rent impact."""
    PMT = calculate_mortgage_payment(P, r, n)
    property_values, mortgage_balances = [P], [P]
    buy_wealth, epf_wealth, rents, cum_rent = [0], [0], [P * rent_yield], [P * rent_yield]
    
    for t in range(1, years + 1):
        # Property appreciation
        new_property_value = property_values[-1] * (1 + g)
        property_values.append(new_property_value)

        # Mortgage repayment
        interest_payment = mortgage_balances[-1] * r
        principal_payment = PMT - interest_payment
        new_mortgage_balance = max(0, mortgage_balances[-1] - principal_payment)
        mortgage_balances.append(new_mortgage_balance)

        # Buy wealth = property value - mortgage
        new_buy_wealth = new_property_value - new_mortgage_balance
        buy_wealth.append(new_buy_wealth)

        # Rent grows with property value
        rent_payment = new_property_value * rent_yield
        rents.append(rent_payment)
        cum_rent.append(cum_rent[-1] + rent_payment)

        # EPF wealth = invest mortgage - rent
        investable = max(0, PMT - rent_payment)
        new_epf_wealth = epf_wealth[-1] * (1 + epf_rate) + investable
        epf_wealth.append(new_epf_wealth)

    # Build dataframe
    df = pd.DataFrame({
        "Year": np.arange(0, years + 1),
        "Property (RM)": property_values,
        "Mortgage (RM)": mortgage_balances,
        "Buy Wealth (RM)": buy_wealth,
        "EPF Wealth (RM)": epf_wealth,
        "Annual Rent (RM)": rents,
        "Cumulative Rent (RM)": cum_rent
    })

    # CAGR calculations
    buy_cagr = calculate_cagr(df["Buy Wealth (RM)"].iloc[1], df["Buy Wealth (RM)"].iloc[-1], years)
    epf_cagr = calculate_cagr(df["EPF Wealth (RM)"].iloc[1], df["EPF Wealth (RM)"].iloc[-1], years)

    # Insert CAGR values only on last row
    df["Buy CAGR"] = [""] * (len(df) - 1) + [f"{buy_cagr*100:.2f}%"]
    df["EPF CAGR"] = [""] * (len(df) - 1) + [f"{epf_cagr*100:.2f}%"]

    return df, buy_cagr, epf_cagr

def plot_outcomes(df, buy_cagr, epf_cagr, years):
    """Plot outcomes with CAGR shown in the legend."""
    plt.figure(figsize=(10, 6))
    
    plt.plot(df["Year"], df["Buy Wealth (RM)"], 
             label=f"🏠 Buy Wealth (CAGR {buy_cagr*100:.2f}%)", linewidth=2)
    plt.plot(df["Year"], df["EPF Wealth (RM)"], 
             label=f"📈 EPF Wealth (CAGR {epf_cagr*100:.2f}%)", linewidth=2, linestyle="--")
    
    plt.xlabel("Year", fontname="Times New Roman")
    plt.ylabel("RM (Amount)", fontname="Times New Roman")
    plt.title("Buy vs EPF Wealth Projection", fontname="Times New Roman", fontsize=14)
    plt.legend()
    plt.grid(True, linestyle="--", alpha=0.6)
    plt.tight_layout()
    return plt.gcf()

def generate_summary(df, years):
    """Generate a text summary of the outcomes."""
    buy_final = df["Buy Wealth (RM)"].iloc[-1]
    epf_final = df["EPF Wealth (RM)"].iloc[-1]
    rent_final = df["Cumulative Rent (RM)"].iloc[-1]
    
    if buy_final > epf_final:
        winner = "Buying property"
        diff = buy_final - epf_final
    else:
        winner = "Investing in EPF"
        diff = epf_final - buy_final
    
    return (
        f"After {years} years:\n"
        f"- Buy Wealth: RM {buy_final:,.0f}\n"
        f"- EPF Wealth: RM {epf_final:,.0f}\n"
        f"- Total Rent Paid: RM {rent_final:,.0f}\n\n"
        f"👉 **{winner} leads by RM {diff:,.0f}.**"
    )


# --------------------------
# 3. Sidebar Inputs
# --------------------------
st.sidebar.header("⚙️ Baseline Assumptions")

initial_property_price = st.sidebar.number_input("Initial Property Price (RM)", value=300000, step=10000)
mortgage_rate = st.sidebar.number_input("Mortgage Rate (%)", value=0.04)
loan_term_years = st.sidebar.number_input("Loan Term (Years)", value=30)
growth_rate = st.sidebar.number_input("Property Growth Rate (%)", value=0.03)
epf_rate = st.sidebar.number_input("EPF Annual Return (%)", value=0.05)
rent_yield = st.sidebar.number_input("Rent Yield (%)", value=0.04)
projection_years = st.sidebar.slider("Projection Horizon (Years)", min_value=5, max_value=40, value=30)


# --------------------------
# 4. Projection
# --------------------------
df, buy_cagr, epf_cagr = project_outcomes(
    P=initial_property_price,
    r=mortgage_rate,
    n=loan_term_years,
    g=growth_rate,
    epf_rate=epf_rate,
    rent_yield=rent_yield,
    years=projection_years
)

# Highlight CAGR winner
def highlight_cagr(val, col_name):
    if isinstance(val, str) and "%" in val:
        val_num = float(val.strip("%"))
        if col_name == "Buy CAGR":
            return "color: green; font-weight: bold;" if val_num > epf_cagr*100 else "color: red;"
        elif col_name == "EPF CAGR":
            return "color: green; font-weight: bold;" if val_num > buy_cagr*100 else "color: red;"
    return ""

# Show Data
st.subheader("📊 Projection Table")
styled_df = df.style.format({
    "Property (RM)": "{:,.0f}",
    "Mortgage (RM)": "{:,.0f}",
    "Buy Wealth (RM)": "{:,.0f}",
    "EPF Wealth (RM)": "{:,.0f}",
    "Annual Rent (RM)": "{:,.0f}",
    "Cumulative Rent (RM)": "{:,.0f}"
}).applymap(lambda v: highlight_cagr(v, "Buy CAGR"), subset=["Buy CAGR"]) \
  .applymap(lambda v: highlight_cagr(v, "EPF CAGR"), subset=["EPF CAGR"])
st.dataframe(styled_df)

# Plot
st.subheader("📈 Wealth Growth Over Time")
st.pyplot(plot_outcomes(df, buy_cagr, epf_cagr, projection_years))

# Summary
st.subheader("📝 Summary")
st.write(generate_summary(df, projection_years))
# --------------------------
# 5. Tabs
# --------------------------
tab1, tab2, tab3 = st.tabs(["📈 Chart","📊 Table","📝 Summary"])

with tab1:
    st.pyplot(plot_outcomes(df, projection_years))

with tab2:
    st.dataframe(format_table(df), use_container_width=True)

with tab3:
    st.markdown(generate_summary(df, projection_years), unsafe_allow_html=True)

# --------------------------
# 6. Download CSV
# --------------------------
csv = df.to_csv(index=False).encode('utf-8')
st.download_button("📥 Download Projection Data (CSV)", csv, "projection.csv", "text/csv", key='download-csv')
