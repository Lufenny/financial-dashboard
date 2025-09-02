# ========================================
# Buy vs Rent + EPF Modelling - Streamlit
# ========================================

import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go

# --------------------------
# 1. Page Config
# --------------------------
st.set_page_config(page_title="Buy vs Rent + EPF Modelling", layout="wide")
st.title("📊 Buy vs Rent + EPF Modelling")

# --------------------------
# 2. Helper Functions
# --------------------------
def calculate_monthly_mortgage(loan_amount, annual_rate, years):
    r = annual_rate / 12
    n = years * 12
    return loan_amount * (r * (1 + r)**n) / ((1 + r)**n - 1) if r > 0 else loan_amount / n

def project_buy_rent(P, loan_amount, mortgage_rate, mortgage_term,
                     property_growth, epf_rate, rent_yield, years,
                     down_payment=0, custom_rent=None):
    
    monthly_PMT = calculate_monthly_mortgage(loan_amount, mortgage_rate, mortgage_term)
    
    property_values = [P]
    mortgage_balances = [loan_amount]
    buy_wealth = [down_payment]
    epf_wealth = [down_payment]
    rents = []
    cum_rent = []

    annual_rent = custom_rent if custom_rent is not None else P * rent_yield
    rents.append(annual_rent)
    cum_rent.append(annual_rent)

    for t in range(1, years+1):
        new_property_value = property_values[-1] * (1 + property_growth)
        property_values.append(new_property_value)

        interest_payment = mortgage_balances[-1] * mortgage_rate
        principal_payment = monthly_PMT*12 - interest_payment
        new_balance = max(0, mortgage_balances[-1] - principal_payment)
        mortgage_balances.append(new_balance)

        buy_wealth.append(new_property_value - new_balance)

        annual_rent = custom_rent if custom_rent is not None else new_property_value * rent_yield
        rents.append(annual_rent)
        cum_rent.append(cum_rent[-1] + annual_rent)

        investable = max(0, monthly_PMT*12 - annual_rent)
        epf_wealth.append(epf_wealth[-1]*(1 + epf_rate/12)**12 + investable)

    buy_cagr = [( (buy_wealth[i]/buy_wealth[0])**(1/i) - 1 if i>0 else 0) for i in range(len(buy_wealth))]
    epf_cagr = [( (epf_wealth[i]/epf_wealth[0])**(1/i) - 1 if i>0 else 0) for i in range(len(epf_wealth))]

    df = pd.DataFrame({
        "Year": np.arange(0, years+1),
        "Property Value": property_values,
        "Mortgage Balance": mortgage_balances,
        "Buy Wealth (RM)": buy_wealth,
        "EPF Wealth (RM)": epf_wealth,
        "Annual Rent": rents,
        "Cumulative Rent": cum_rent,
        "Buy CAGR": buy_cagr,
        "EPF CAGR": epf_cagr
    })
    return df

# --------------------------
# 3. Sidebar Inputs
# --------------------------
st.sidebar.header("⚙️ Input Parameters")
purchase_price = st.sidebar.number_input("Property Price (RM)", value=500_000, step=50_000)
down_payment = st.sidebar.number_input("Down Payment (RM)", value=100_000, step=10_000)
loan_amount = purchase_price - down_payment

mortgage_rate = st.sidebar.slider("Mortgage Rate (%)", 1.0, 8.0, 4.0)/100
mortgage_term = st.sidebar.number_input("Loan Term (Years)", value=30, step=5)
property_growth = st.sidebar.slider("Property Growth Rate (%)", 1.0, 10.0, 5.0)/100
epf_rate = st.sidebar.slider("EPF Annual Return (%)", 1.0, 10.0, 6.0)/100
rent_yield = st.sidebar.slider("Rent Yield (%)", 1.0, 10.0, 4.0)/100
projection_years = st.sidebar.number_input("Projection Years", value=30, step=5)

use_custom_rent = st.sidebar.checkbox("Use Custom Starting Rent?")
custom_rent = st.sidebar.number_input("Custom Annual Rent (RM)", value=20000, step=1000) if use_custom_rent else None

# --------------------------
# 4. Run Projection
# --------------------------
df_results = project_buy_rent(
    P=purchase_price,
    loan_amount=loan_amount,
    mortgage_rate=mortgage_rate,
    mortgage_term=mortgage_term,
    property_growth=property_growth,
    epf_rate=epf_rate,
    rent_yield=rent_yield,
    years=projection_years,
    down_payment=down_payment,
    custom_rent=custom_rent
)

# Break-even year
break_even_year = next((row.Year for i,row in df_results.iterrows() if row["Buy Wealth (RM)"] > row["EPF Wealth (RM)"]), None)

# --------------------------
# 5. Display Results
# --------------------------
st.subheader("📊 Projection Table (First 10 Years)")
st.dataframe(df_results.head(10))

st.subheader("📈 Wealth Comparison")
fig = go.Figure()
fig.add_trace(go.Scatter(x=df_results["Year"], y=df_results["Buy Wealth (RM)"], mode='lines+markers', name="🏡 Buy Property"))
fig.add_trace(go.Scatter(x=df_results["Year"], y=df_results["EPF Wealth (RM)"], mode='lines+markers', name="💰 Rent+EPF"))
if break_even_year:
    fig.add_vline(x=break_even_year, line=dict(color='orange', dash='dash'))
    fig.add_annotation(x=break_even_year, y=max(df_results["Buy Wealth (RM)"].max(), df_results["EPF Wealth (RM)"].max()),
                       text=f"📍 Break-even: Year {break_even_year}", showarrow=False, yanchor="bottom")
st.plotly_chart(fig, use_container_width=True)

st.subheader("💡 Summary")
st.write(f"Final Buy Wealth: RM {df_results['Buy Wealth (RM)'].iloc[-1]:,.0f}")
st.write(f"Final EPF Wealth: RM {df_results['EPF Wealth (RM)'].iloc[-1]:,.0f}")
st.write(f"Break-even Year: {break_even_year if break_even_year else 'No break-even within projection horizon'}")

# --------------------------
# 6. Sensitivity Analysis (±10%)
# --------------------------
st.subheader("🧩 Sensitivity Analysis (±10%)")
sensitivity_pct = 0.10
params = {
    "Mortgage Rate": (mortgage_rate*(1-sensitivity_pct), mortgage_rate*(1+sensitivity_pct)),
    "Property Growth": (property_growth*(1-sensitivity_pct), property_growth*(1+sensitivity_pct)),
    "EPF Rate": (epf_rate*(1-sensitivity_pct), epf_rate*(1+sensitivity_pct)),
    "Rent Yield": (rent_yield*(1-sensitivity_pct), rent_yield*(1+sensitivity_pct))
}

sensitivity_results = []

for param_name, (low, high) in params.items():
    kwargs = {
        "P": purchase_price,
        "loan_amount": loan_amount,
        "mortgage_rate": mortgage_rate,
        "mortgage_term": mortgage_term,
        "property_growth": property_growth,
        "epf_rate": epf_rate,
        "rent_yield": rent_yield,
        "years": projection_years,
        "down_payment": down_payment,
        "custom_rent": custom_rent
    }
    kwargs_low = kwargs.copy()
    kwargs_low[param_name.replace(" ", "_").lower()] = low
    df_low = project_buy_rent(**kwargs_low)
    kwargs_high = kwargs.copy()
    kwargs_high[param_name.replace(" ", "_").lower()] = high
    df_high = project_buy_rent(**kwargs_high)

    sensitivity_results.append({
        "Parameter": param_name,
        "Buy Low": df_low["Buy Wealth (RM)"].iloc[-1],
        "Buy High": df_high["Buy Wealth (RM)"].iloc[-1],
        "Buy Impact": df_high["Buy Wealth (RM)"].iloc[-1] - df_low["Buy Wealth (RM)"].iloc[-1],
        "EPF Low": df_low["EPF Wealth (RM)"].iloc[-1],
        "EPF High": df_high["EPF Wealth (RM)"].iloc[-1],
        "EPF Impact": df_high["EPF Wealth (RM)"].iloc[-1] - df_low["EPF Wealth (RM)"].iloc[-1]
    })

df_sensitivity = pd.DataFrame(sensitivity_results)
st.dataframe(df_sensitivity)

# Highlight most sensitive factors
most_sensitive_buy = df_sensitivity.loc[df_sensitivity["Buy Impact"].idxmax()]
most_sensitive_epf = df_sensitivity.loc[df_sensitivity["EPF Impact"].idxmax()]

st.markdown(f"**Most sensitive factor for Buy Wealth:** {most_sensitive_buy['Parameter']} (Impact: RM {most_sensitive_buy['Buy Impact']:,.0f})")
st.markdown(f"**Most sensitive factor for EPF Wealth:** {most_sensitive_epf['Parameter']} (Impact: RM {most_sensitive_epf['EPF Impact']:,.0f})")

# --------------------------
# 7. Tornado Charts for Sensitivity Analysis
# --------------------------
st.subheader("🌪️ Tornado Charts - Sensitivity Impact")

import plotly.express as px

# Buy Wealth Tornado
df_buy = df_sensitivity[['Parameter', 'Buy Low', 'Buy High']].copy()
df_buy['Impact'] = df_buy['Buy High'] - df_buy['Buy Low']
df_buy = df_buy.sort_values('Impact', ascending=True)

fig_buy = go.Figure()
fig_buy.add_trace(go.Bar(
    x=df_buy['Impact'],
    y=df_buy['Parameter'],
    orientation='h',
    name='Impact on Buy Wealth',
    marker_color='teal'
))
fig_buy.update_layout(title='Buy Wealth Sensitivity (±10%)', xaxis_title='Impact (RM)', yaxis_title='')
st.plotly_chart(fig_buy, use_container_width=True)

# EPF Wealth Tornado
df_epf = df_sensitivity[['Parameter', 'EPF Low', 'EPF High']].copy()
df_epf['Impact'] = df_epf['EPF High'] - df_epf['EPF Low']
df_epf = df_epf.sort_values('Impact', ascending=True)

fig_epf = go.Figure()
fig_epf.add_trace(go.Bar(
    x=df_epf['Impact'],
    y=df_epf['Parameter'],
    orientation='h',
    name='Impact on EPF Wealth',
    marker_color='orange'
))
fig_epf.update_layout(title='EPF Wealth Sensitivity (±10%)', xaxis_title='Impact (RM)', yaxis_title='')
st.plotly_chart(fig_epf, use_container_width=True)
