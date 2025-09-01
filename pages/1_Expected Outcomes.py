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
        font-family: 'Times New Roman', serif;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# --------------------------
# 2. Sidebar Inputs
# --------------------------
st.sidebar.header("⚙️ Assumptions")

initial_property_price = st.sidebar.number_input("Initial Property Price (RM)", value=300000, step=10000)
property_growth = st.sidebar.slider("Annual Property Growth Rate (%)", 1, 10, 5) / 100
mortgage_rate = st.sidebar.slider("Mortgage Interest Rate (%)", 1, 10, 4) / 100
loan_term_years = st.sidebar.number_input("Loan Term (Years)", value=30, step=5)
epf_rate = st.sidebar.slider("EPF Annual Return (%)", 1, 10, 5) / 100
rent_cost = st.sidebar.number_input("Annual Rent (RM)", value=12000, step=1000)
projection_years = st.sidebar.slider("Projection Period (Years)", 5, 40, 30)

# --------------------------
# 3. Helper Functions
# --------------------------
def calculate_cagr(final_value, initial_value, years):
    if years <= 0 or initial_value <= 0 or final_value <= 0:
        return 0
    return (final_value / initial_value) ** (1 / years) - 1

# --------------------------
# 4. Wealth Projection
# --------------------------
def project_wealth(initial_property_price, property_growth, r, n, epf_rate, rent_cost, years):
    property_value = []
    buy_wealth = []
    epf_wealth = []
    rent_expense = []
    
    current_property_value = initial_property_price
    buy_cashflow = 0
    epf_balance = 0
    
    P = initial_property_price
    if r > 0:
        PMT = P * (r * (1 + r)**n) / ((1 + r)**n - 1)
    else:
        PMT = P / n
    
    for year in range(1, years + 1):
        current_property_value *= (1 + property_growth)
        property_value.append(current_property_value)
        
        buy_cashflow -= PMT
        buy_wealth.append(current_property_value + buy_cashflow)
        
        epf_balance = (epf_balance + (PMT - rent_cost)) * (1 + epf_rate)
        epf_wealth.append(epf_balance)
        
        rent_expense.append(rent_cost * year)
    
    return pd.DataFrame({
        "Year": range(1, years + 1),
        "Property Value (RM)": property_value,
        "Buy Wealth (RM)": buy_wealth,
        "EPF Wealth (RM)": epf_wealth,
        "Cumulative Rent (RM)": rent_expense
    })

# --------------------------
# 5. Run Projection
# --------------------------
df = project_wealth(initial_property_price, property_growth=property_growth, r=mortgage_rate, n=loan_term_years,
                    epf_rate=epf_rate, rent_cost=rent_cost, years=projection_years)

buy_final = df["Buy Wealth (RM)"].iloc[-1]
epf_final = df["EPF Wealth (RM)"].iloc[-1]
rent_final = df["Cumulative Rent (RM)"].iloc[-1]

buy_cagr = calculate_cagr(buy_final, initial_property_price, projection_years)
epf_cagr = calculate_cagr(epf_final, 0.01, projection_years)

winner_name = "🏠 Buy" if buy_final > epf_final else "📈 EPF"
winner_value = max(buy_final, epf_final)

# --------------------------
# 6. Table Display with Highlights
# --------------------------
def highlight_cagr(val):
    color = "green" if isinstance(val, str) and "%" in val else ""
    return f"color: {color}; font-weight: bold" if color else ""

def format_table(df, buy_cagr, epf_cagr):
    styled_df = df.style.format({
        "Property Value (RM)": "RM {:,.0f}",
        "Buy Wealth (RM)": "RM {:,.0f}",
        "EPF Wealth (RM)": "RM {:,.0f}",
        "Cumulative Rent (RM)": "RM {:,.0f}"
    }).applymap(highlight_cagr)
    return styled_df

# --------------------------
# 7. Plotting Function
# --------------------------
def plot_outcomes(df, buy_cagr, epf_cagr, years):
    plt.figure(figsize=(10, 6))
    plt.plot(df["Year"], df["Buy Wealth (RM)"], label=f"🏠 Buy Wealth (CAGR {buy_cagr*100:.2f}%)", linewidth=2)
    plt.plot(df["Year"], df["EPF Wealth (RM)"], label=f"📈 EPF Wealth (CAGR {epf_cagr*100:.2f}%)", linewidth=2, linestyle="--")
    plt.xlabel("Year", fontname="Times New Roman")
    plt.ylabel("RM (Amount)", fontname="Times New Roman")
    plt.title("Buy vs EPF Wealth Projection", fontname="Times New Roman", fontsize=14)
    plt.legend()
    plt.grid(True, linestyle="--", alpha=0.6)
    return plt.gcf()

# --------------------------
# 8. Streamlit Layout
# --------------------------
st.title("📊 Buy vs EPF: Expected Outcomes – Fair Comparison")

tab1, tab2, tab3 = st.tabs(["📈 Projection Graph", "📋 Wealth Table", "🏆 Outcome Summary"])

with tab1:
    st.pyplot(plot_outcomes(df, buy_cagr, epf_cagr, projection_years))

with tab2:
    styled_df = format_table(df, buy_cagr, epf_cagr)
    st.dataframe(styled_df, use_container_width=True)

with tab3:
    st.subheader("🏆 Final Comparison")
    st.write(f"**🏠 Buy Wealth (Final):** RM {buy_final:,.0f} (CAGR: {buy_cagr*100:.2f}%)")
    st.write(f"**📈 EPF Wealth (Final):** RM {epf_final:,.0f} (CAGR: {epf_cagr*100:.2f}%)")
    st.write(f"**💸 Cumulative Rent Paid:** RM {rent_final:,.0f}")
    st.success(f"✅ **Winner: {winner_name} with RM {winner_value:,.0f}**")

# --------------------------
# 9. Additional Styling
# --------------------------
def calculate_cagr(final_value, initial_value, years):
    if years <= 0 or initial_value <= 0:
        return 0
    return (final_value / initial_value) ** (1 / years) - 1

styled_df = df.style.format({
    "Property Value (RM)": "RM {:,.0f}",
    "Buy Wealth (RM)": "RM {:,.0f}",
    "EPF Wealth (RM)": "RM {:,.0f}",
    "Cumulative Rent (RM)": "RM {:,.0f}"
}).applymap(highlight_cagr)

st.dataframe(styled_df, use_container_width=True)
