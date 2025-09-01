import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

st.set_page_config(page_title='Expected Outcomes – Baseline', layout='wide')
st.title("📌 Expected Outcomes – Baseline Comparison")

# --------------------------
# Helper Functions
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

    # CAGR calculations (only final row)
    buy_cagr = calculate_cagr(df["Buy Wealth (RM)"].iloc[1], df["Buy Wealth (RM)"].iloc[-1], years)
    epf_cagr = calculate_cagr(df["EPF Wealth (RM)"].iloc[1], df["EPF Wealth (RM)"].iloc[-1], years)

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
# Sidebar Inputs
# --------------------------
st.sidebar.header("⚙️ Baseline Assumptions")

initial_property_price = st.sidebar.number_input("Initial Property Price (RM)", value=300000, step=10000)
mortgage_rate = st.sidebar.number_input("Mortgage Rate (%)", value=0.04)  # annual interest
loan_term_years = st.sidebar.number_input("Loan Term (Years)", value=30)
growth_rate = st.sidebar.number_input("Property Growth Rate (%)", value=0.03)
epf_rate = st.sidebar.number_input("EPF Annual Return (%)", value=0.05)
rent_yield = st.sidebar.number_input("Rent Yield (%)", value=0.04)
projection_years = st.sidebar.slider("Projection Horizon (Years)", min_value=5, max_value=40, value=30)

# --------------------------
# Run Projection
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

# Show Data
st.subheader("📊 Projection Table")
st.dataframe(df.style.format({
    "Property (RM)": "{:,.0f}",
    "Mortgage (RM)": "{:,.0f}",
    "Buy Wealth (RM)": "{:,.0f}",
    "EPF Wealth (RM)": "{:,.0f}",
    "Annual Rent (RM)": "{:,.0f}",
    "Cumulative Rent (RM)": "{:,.0f}"
}))

# Plot
st.subheader("📈 Wealth Growth Over Time")
st.pyplot(plot_outcomes(df, buy_cagr, epf_cagr, projection_years))

# Summary
st.subheader("📝 Summary")
st.write(generate_summary(df, projection_years))
