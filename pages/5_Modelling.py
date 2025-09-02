import streamlit as st
import numpy as np
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="Buy vs Rent Modelling", layout="wide")
st.title("🏡 Buy vs Rent Modelling and Sensitivity Analysis (Fair Comparison)")

# --------------------------
# 1. Sidebar Inputs
# --------------------------
st.sidebar.header("📌 Assumptions")

purchase_price = st.sidebar.number_input("Property Price (RM)", value=500000, step=10000)
down_payment_pct = st.sidebar.slider("Down Payment (%)", 0.0, 0.5, 0.1)
mortgage_term = st.sidebar.slider("Mortgage Term (years)", 10, 35, 30)
projection_years = st.sidebar.slider("Projection Horizon (years)", 5, 40, 20)

# Base-case rates
mortgage_rate = st.sidebar.slider("Mortgage Rate (%)", 2.0, 8.0, 4.0, step=0.1)
prop_appreciation = st.sidebar.slider("Property Appreciation (%)", 0.0, 6.0, 3.0, step=0.1)
rent_yield = st.sidebar.slider("Rental Yield (%)", 2.0, 6.0, 4.0, step=0.1)
investment_return = st.sidebar.slider("Investment Return (%)", 2.0, 12.0, 6.0, step=0.1)

# --------------------------
# 2. Functions
# --------------------------
def mortgage_payment(principal, annual_rate, n_years):
    r = annual_rate / 12
    n = n_years * 12
    if r == 0:
        return principal / n
    return principal * r / (1 - (1 + r) ** -n)

def outstanding_balance(principal, annual_rate, n_years, months_elapsed):
    r = annual_rate / 12
    n = n_years * 12
    pmt = mortgage_payment(principal, annual_rate, n_years)
    balance = principal * (1 + r)**months_elapsed - pmt * ((1 + r)**months_elapsed - 1) / r
    return balance

def project_buy_rent(price, dp_pct, mortgage_rate, mortgage_term, prop_growth,
                     rent_yield, invest_return, years):
    dp = price * dp_pct
    loan = price - dp
    pmt = mortgage_payment(loan, mortgage_rate, mortgage_term)

    buy_wealth, rent_wealth = [dp], [dp]
    years_list = np.arange(1, years+1)

    for t in years_list:
        # Buy
        Vt = price * (1 + prop_growth)**t
        bal = outstanding_balance(loan, mortgage_rate, mortgage_term, t*12)
        eq = Vt - bal
        buy_wealth.append(eq)

        # Rent + Invest
        annual_rent = price * rent_yield * (1.02**(t-1))  # rent grows 2% p.a.
        invested = rent_wealth[-1] * (1 + invest_return) + (pmt*12 - annual_rent)
        rent_wealth.append(invested)

    df = pd.DataFrame({
        "Year": np.arange(0, years+1),
        "Buy Wealth (RM)": buy_wealth,
        "EPF Wealth (RM)": rent_wealth
    })

    # CAGR
    df["Buy CAGR"] = [( (df["Buy Wealth (RM)"].iloc[i]/df["Buy Wealth (RM)"].iloc[0])**(1/i)-1 if i>0 else 0)
                      for i in range(len(df))]
    df["EPF CAGR"] = [( (df["EPF Wealth (RM)"].iloc[i]/df["EPF Wealth (RM)"].iloc[0])**(1/i)-1 if i>0 else 0)
                      for i in range(len(df))]

    return df

# --------------------------
# 3. Base-case Projection
# --------------------------
df_base = project_buy_rent(
    purchase_price, down_payment_pct, mortgage_rate/100, mortgage_term,
    prop_appreciation/100, rent_yield/100, investment_return/100, projection_years
)

break_even_year = next((row.Year for i,row in df_base.iterrows()
                        if row["Buy Wealth (RM)"]>row["EPF Wealth (RM)"]), None)

# --------------------------
# 4. Base-case Charts & Table
# --------------------------
st.subheader("📊 Wealth Accumulation Over Time – Base-case")
st.line_chart(df_base.set_index("Year")[["Buy Wealth (RM)", "EPF Wealth (RM)"]])

st.subheader("📈 Base-case Summary")
final_buy = df_base["Buy Wealth (RM)"].iloc[-1]
final_epf = df_base["EPF Wealth (RM)"].iloc[-1]
cagr_buy = df_base["Buy CAGR"].iloc[-1]*100
cagr_epf = df_base["EPF CAGR"].iloc[-1]*100

st.markdown(f"""
- **Final Wealth:** Buy RM {final_buy:,.0f} vs Rent+Invest RM {final_epf:,.0f}  
- **CAGR:** Buy {cagr_buy:.2f}% vs Rent+Invest {cagr_epf:.2f}%  
- **Break-even Year:** {break_even_year if break_even_year else 'No break-even'}
""")

# --------------------------
# 5. Sensitivity Analysis
# --------------------------
st.subheader("🧮 Sensitivity Analysis – Final Year Outcomes")

mortgage_rates = [0.03, 0.04, 0.05, 0.06, 0.07]
investment_returns = [0.04, 0.05, 0.06, 0.07, 0.08]
appreciations = [0.02, 0.03, 0.04]
rent_yields = [0.03, 0.04, 0.05]

records = []

for mr in mortgage_rates:
    for ir in investment_returns:
        for g in appreciations:
            for ry in rent_yields:
                df_temp = project_buy_rent(purchase_price, down_payment_pct, mr, mortgage_term,
                                           g, ry, ir, projection_years)
                final_buy = df_temp["Buy Wealth (RM)"].iloc[-1]
                final_epf = df_temp["EPF Wealth (RM)"].iloc[-1]
                diff = final_buy - final_epf
                records.append([mr, ir, g, ry, final_buy, final_epf, diff])

df_sens = pd.DataFrame(records, columns=["MortgageRate","InvestReturn","Appreciation","RentYield",
                                         "BuyWealth","EPFWealth","Difference"])

st.dataframe(df_sens, use_container_width=True)

# --------------------------
# 6. Interactive Heatmap
# --------------------------
st.subheader("📊 Heatmap – Impact of Parameters on Buy vs Rent")

param_x = st.selectbox("X-axis parameter", ["MortgageRate", "InvestReturn", "Appreciation", "RentYield"], index=0)
param_y = st.selectbox("Y-axis parameter", ["MortgageRate", "InvestReturn", "Appreciation", "RentYield"], index=1)

pivot_heatmap = df_sens.pivot_table(
    index=param_y,
    columns=param_x,
    values="Difference",
    aggfunc="mean"
).fillna(0)

fig_heatmap = px.imshow(
    pivot_heatmap.values,
    x=pivot_heatmap.columns,
    y=pivot_heatmap.index,
    color_continuous_scale="RdBu_r",
    text_auto=True,
    aspect="auto"
)

fig_heatmap.update_layout(
    title=f"Tipping Map – Buy vs Rent Difference (RM)",
    xaxis_title=param_x,
    yaxis_title=param_y,
    coloraxis_colorbar=dict(title="Buy - Rent (RM)")
)

st.plotly_chart(fig_heatmap, use_container_width=True)

# --------------------------
# 7. Download CSV
# --------------------------
csv = df_sens.to_csv(index=False).encode("utf-8")
st.download_button(
    "⬇️ Download Sensitivity Results (CSV)",
    data=csv,
    file_name="buy_vs_rent_sensitivity.csv",
    mime="text/csv"
)
