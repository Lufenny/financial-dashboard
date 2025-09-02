import streamlit as st
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.express as px


# --------------------------
# Page Setup
# --------------------------
st.set_page_config(page_title="Buy vs Rent Model", layout="wide")
st.title("🏡 Buy vs Rent Modelling & Sensitivity Analysis")

# --------------------------
# Sidebar Inputs
# --------------------------
st.sidebar.header("📌 Base Assumptions")
purchase_price = st.sidebar.number_input("Property Price (RM)", value=500000, step=10000)
down_payment_pct = st.sidebar.slider("Down Payment (%)", 0.0, 0.5, 0.1)
mortgage_term = st.sidebar.slider("Mortgage Term (years)", 10, 35, 30)
years = st.sidebar.slider("Analysis Horizon (years)", 5, 40, 20)

# Base-case rates
mortgage_rate = st.sidebar.slider("Mortgage Rate (%)", 2.0, 8.0, 4.0, step=0.1)
prop_appreciation = st.sidebar.slider("Property Appreciation (%)", 0.0, 6.0, 3.0, step=0.1)
rent_yield = st.sidebar.slider("Rental Yield (%)", 2.0, 6.0, 4.0, step=0.1)
investment_return = st.sidebar.slider("Investment Return (%)", 2.0, 12.0, 6.0, step=0.1)

# --------------------------
# Functions
# --------------------------
def mortgage_payment(principal, annual_rate, n_years):
    r = annual_rate / 12
    n = n_years * 12
    return principal / n if r == 0 else principal * r / (1 - (1 + r) ** -n)

def outstanding_balance(principal, annual_rate, n_years, months_elapsed):
    r = annual_rate / 12
    n = n_years * 12
    pmt = mortgage_payment(principal, annual_rate, n_years)
    return principal * (1 + r)**months_elapsed - pmt * ((1 + r)**months_elapsed - 1) / r

# --------------------------
# Base-case Simulation
# --------------------------
dp = purchase_price * down_payment_pct
loan = purchase_price - dp
pmt = mortgage_payment(loan, mortgage_rate/100, mortgage_term)

years_list = np.arange(1, years+1)
buy_equity, rent_portfolio = [], []

for t in years_list:
    Vt = purchase_price * (1 + prop_appreciation/100)**t
    bal = outstanding_balance(loan, mortgage_rate/100, mortgage_term, t*12)
    eq = Vt - bal
    buy_equity.append(eq)
    
    annual_rent = purchase_price * rent_yield * (1.02**(t-1))  # rent grows 2%
    invested = (rent_portfolio[-1] if t > 1 else dp)
    invested = invested * (1 + investment_return/100) + (pmt*12 - annual_rent)
    rent_portfolio.append(invested)

df_base = pd.DataFrame({
    "Year": years_list,
    "BuyEquity": buy_equity,
    "RentPortfolio": rent_portfolio,
    "Difference": np.array(buy_equity) - np.array(rent_portfolio)
})

# --------------------------
# Base-case Chart
# --------------------------
st.subheader("📊 Wealth Accumulation Over Time (Base-case)")
st.line_chart(df_base.set_index("Year")[["BuyEquity","RentPortfolio"]])

st.subheader("📈 Final Comparison")
st.write(f"After {years} years:")
st.write(f"- Buy Equity: RM{buy_equity[-1]:,.0f}")
st.write(f"- Rent & Invest Portfolio: RM{rent_portfolio[-1]:,.0f}")
st.write(f"- Difference: RM{df_base['Difference'].iloc[-1]:,.0f}")

# --------------------------
# Sensitivity Analysis
# --------------------------
st.subheader("🧮 Sensitivity Analysis")

st.markdown("""
This analysis evaluates how Buy vs Rent outcomes change under varying assumptions:
- Mortgage Rate: 3–7%
- Investment Return: 4–8%
- Property Appreciation: 2–4%
- Rental Yield: 3–5%
""")

mortgage_rates = [3, 4, 5, 6, 7]
investment_returns = [4, 5, 6, 7, 8]
appreciations = [2, 3, 4]
rent_yields = [3, 4, 5]

records = []
for t in range(1, years+1):
    for mr in mortgage_rates:
        for ir in investment_returns:
            for g in appreciations:
                for ry in rent_yields:
                    Vt = purchase_price * (1 + g/100)**t
                    bal = outstanding_balance(loan, mr/100, mortgage_term, t*12)
                    eq = Vt - bal
                    annual_rent = purchase_price * ry
                    rent_val = dp * (1 + ir/100)**t + (pmt*12 - annual_rent) * (((1 + ir/100)**t - 1) / (ir/100))
                    diff = eq - rent_val
                    records.append([t, mr, ir, g, ry, eq, rent_val, diff])

df_sens = pd.DataFrame(records, columns=["Year","MortgageRate","InvestReturn","Appreciation","RentYield","BuyEquity","RentPortfolio","Difference"])

# --------------------------
# Download CSV
# --------------------------
csv = df_sens.to_csv(index=False).encode("utf-8")
st.download_button("⬇️ Download Sensitivity Results (CSV)", data=csv, file_name="buy_vs_rent_sensitivity.csv", mime="text/csv")

# --------------------------
# Interactive Heatmap
# --------------------------
st.subheader("📊 Heatmap – Final Year Scenarios")

# Let user select X and Y axes
param_x = st.selectbox("X-axis parameter", ["MortgageRate", "InvestReturn", "Appreciation", "RentYield"], index=0)
param_y = st.selectbox("Y-axis parameter", ["MortgageRate", "InvestReturn", "Appreciation", "RentYield"], index=1)

# Pivot for heatmap values
pivot_plotly = df_final_year.pivot_table(
    index=param_y,
    columns=param_x,
    values='Difference',
    aggfunc='mean'
).fillna(0)

# Reset index for hover text
df_hover = df_final_year[[param_x, param_y, 'Difference', 'MortgageRate', 'InvestReturn', 'Appreciation', 'RentYield']]

# Create Plotly heatmap
fig_plotly = px.imshow(
    pivot_plotly.values,
    x=pivot_plotly.columns,
    y=pivot_plotly.index,
    color_continuous_scale='RdBu_r',
    text_auto=True,
    aspect="auto",
)

fig_plotly.update_layout(
    xaxis_title=param_x,
    yaxis_title=param_y,
    coloraxis_colorbar=dict(title="Buy - Rent (RM)"),
    title=f"Tipping Map – {years} yrs (Interactive)"
)

# Add hover info for all 4 parameters
fig_plotly.update_traces(
    hovertemplate=
    f"{param_x}: %{{x}}<br>{param_y}: %{{y}}<br>Difference: %{{z:,.0f}}<br>" +
    "MortgageRate: %{customdata[0]}%<br>InvestReturn: %{customdata[1]}%<br>Appreciation: %{customdata[2]}%<br>RentYield: %{customdata[3]}%",
    customdata=df_hover[['MortgageRate','InvestReturn','Appreciation','RentYield']].values
)

st.plotly_chart(fig_plotly, use_container_width=True)

# --------------------------
# Summary Metrics
# --------------------------
st.subheader("📌 Sensitivity Summary – Final Year")
best_case = df_final_year.loc[df_final_year['Difference'].idxmax()]
worst_case = df_final_year.loc[df_final_year['Difference'].idxmin()]

st.markdown(f"""
- **Best Case (Buy wins)**: Difference = RM{best_case['Difference']:,.0f}  
  Mortgage Rate: {best_case['MortgageRate']}%, Investment Return: {best_case['InvestReturn']}%, Appreciation: {best_case['Appreciation']}%, Rent Yield: {best_case['RentYield']}%  

- **Worst Case (Rent wins)**: Difference = RM{worst_case['Difference']:,.0f}  
  Mortgage Rate: {worst_case['MortgageRate']}%, Investment Return: {worst_case['InvestReturn']}%, Appreciation: {worst_case['Appreciation']}%, Rent Yield: {worst_case['RentYield']}%
""")
