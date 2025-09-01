import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

st.set_page_config(page_title="Expected Outcomes – Baseline", layout="wide")

# --------------------------
# 1. Baseline Assumptions (Sidebar)
# --------------------------
st.sidebar.header("⚙️ Baseline Assumptions")
initial_property_price = st.sidebar.number_input("Initial Property Price (RM)", value=500000, step=50000)
mortgage_rate = st.sidebar.slider("Mortgage Rate (%)", 2.0, 7.0, 4.0) / 100
loan_term_years = st.sidebar.slider("Loan Term (Years)", 10, 35, 30)
projection_years = st.sidebar.slider("Projection Period (Years)", 5, 35, 30)

property_growth_rate = st.sidebar.slider("Property Growth Rate (%)", 1.0, 8.0, 3.0) / 100
rent_yield = st.sidebar.slider("Rent Yield (% of Property Value)", 2.0, 8.0, 4.0) / 100
rent_inflation_rate = st.sidebar.slider("Annual Rent Increase (%)", 0.0, 5.0, 2.0) / 100

epf_return_rate = st.sidebar.slider("EPF Return Rate (%)", 3.0, 8.0, 5.0) / 100
annual_contribution = st.sidebar.number_input("Annual Contribution to EPF (RM)", value=20000, step=1000)

# --------------------------
# 2. Helper Functions
# --------------------------
def calculate_mortgage_payment(P, r, n):
    """Annual mortgage payment."""
    if r > 0:
        return P * (r * (1 + r) ** n) / ((1 + r) ** n - 1)
    else:
        return P / n

def project_outcomes(price, r, n, years, growth, rent_y, rent_inf, epf_r, contrib):
    """Simulate property (buy) vs EPF (invest) outcomes."""
    mortgage_payment = calculate_mortgage_payment(price, r, n)

    data = []
    remaining_loan = price
    buy_wealth = 0
    epf_wealth = 0
    cumulative_rent = 0
    rent_cost = price * rent_y

    for year in range(1, years + 1):
        property_value = price * ((1 + growth) ** year)

        if year <= n:
            remaining_loan = remaining_loan * (1 + r) - mortgage_payment
            equity = property_value - remaining_loan
        else:
            remaining_loan = 0
            equity = property_value

        buy_wealth = equity

        # Rent grows each year
        rent_cost *= (1 + rent_inf)
        cumulative_rent += rent_cost

        # EPF grows
        epf_wealth = (epf_wealth + contrib) * (1 + epf_r)

        data.append({
            "Year": year,
            "Buy Wealth (RM)": buy_wealth,
            "EPF Wealth (RM)": epf_wealth,
            "Cumulative Rent (RM)": cumulative_rent
        })

    return pd.DataFrame(data)

def calculate_cagr(final_value, initial_value, years):
    """Compound Annual Growth Rate (CAGR)."""
    if initial_value <= 0 or final_value <= 0:
        return 0
    return (final_value / initial_value) ** (1 / years) - 1

# --------------------------
# 3. Projection
# --------------------------
df = project_outcomes(initial_property_price, mortgage_rate, loan_term_years,
                      projection_years, property_growth_rate, rent_yield,
                      rent_inflation_rate, epf_return_rate, annual_contribution)

buy_final = df["Buy Wealth (RM)"].iloc[-1]
epf_final = df["EPF Wealth (RM)"].iloc[-1]

buy_cagr = calculate_cagr(buy_final, initial_property_price, projection_years)
epf_cagr = calculate_cagr(epf_final, annual_contribution, projection_years)

# --------------------------
# 4. Chart Function
# --------------------------
def plot_outcomes(df, years, buy_cagr, epf_cagr):
    """Plot outcomes with CAGR in legend and color-coded labels."""
    plt.figure(figsize=(10, 6))

    plt.plot(df["Year"], df["Buy Wealth (RM)"],
             label=f"🏠 Buy Wealth (CAGR {buy_cagr*100:.2f}%)", linewidth=2, color="green")
    plt.plot(df["Year"], df["EPF Wealth (RM)"],
             label=f"📈 EPF Wealth (CAGR {epf_cagr*100:.2f}%)", linewidth=2, color="red", linestyle="--")

    plt.xlabel("Year", fontname="Times New Roman")
    plt.ylabel("RM (Amount)", fontname="Times New Roman")
    plt.title("Buy vs EPF Wealth Projection", fontname="Times New Roman", fontsize=14)
    plt.legend()
    plt.grid(True, linestyle="--", alpha=0.6)
    plt.tight_layout()
    return plt.gcf()

# --------------------------
# 5. Table Formatting
# --------------------------
def format_table(df):
    """Format RM values and highlight final winner."""
    df_fmt = df.copy()
    for col in df.columns[1:]:
        df_fmt[col] = df[col].apply(lambda x: f"RM {x:,.0f}")

    final_row = df.iloc[-1]
    winner = "Buy Wealth (RM)" if final_row["Buy Wealth (RM)"] > final_row["EPF Wealth (RM)"] else "EPF Wealth (RM)"

    def highlight(row):
        color = "background-color: lightgreen"
        return [color if row.name == df.index[-1] and row[winner] == row.max() else "" for _ in row]

    return df_fmt.style.apply(highlight, axis=1)

# --------------------------
# 6. Summary
# --------------------------
def generate_summary(df, years):
    buy_final = df["Buy Wealth (RM)"].iloc[-1]
    epf_final = df["EPF Wealth (RM)"].iloc[-1]

    if buy_final > epf_final:
        winner = "🏠 Buying a Property"
        diff = buy_final - epf_final
    else:
        winner = "📈 Investing in EPF"
        diff = epf_final - buy_final

    return f"""
    ### 📝 Summary of Results  
    After **{years} years**:  
    - 🏠 **Buy Wealth:** RM {buy_final:,.0f} (CAGR {buy_cagr*100:.2f}%)  
    - 📈 **EPF Wealth:** RM {epf_final:,.0f} (CAGR {epf_cagr*100:.2f}%)  

    ✅ **{winner}** yields about **RM {diff:,.0f} more** in wealth.
    """

# --------------------------
# 7. Tabs
# --------------------------
tab1, tab2, tab3 = st.tabs(["📈 Chart","📊 Table","📝 Summary"])

with tab1:
    st.pyplot(plot_outcomes(df, projection_years, buy_cagr, epf_cagr))

with tab2:
    st.dataframe(format_table(df), use_container_width=True)

with tab3:
    st.markdown(generate_summary(df, projection_years), unsafe_allow_html=True)
