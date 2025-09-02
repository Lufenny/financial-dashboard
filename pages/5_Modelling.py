import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go

# --------------------------
# 1. Page Config & Style
# --------------------------
st.set_page_config(page_title='Buy vs Rent + EPF Modelling', layout='wide')
st.markdown("""
<style>
html, body, [class*="css"] {
    font-family: 'Times New Roman', serif !important;
}
</style>
""", unsafe_allow_html=True)

st.title("🏡 Buy Property vs 💰 Rent+EPF: Wealth Projection & Sensitivity Analysis")

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

    annual_rent = custom_rent if custom_rent else P * rent_yield
    rents.append(annual_rent)
    cum_rent.append(annual_rent)

    for t in range(1, years + 1):
        new_property_value = property_values[-1] * (1 + property_growth)
        property_values.append(new_property_value)

        interest_payment = mortgage_balances[-1] * mortgage_rate
        principal_payment = monthly_PMT*12 - interest_payment
        new_balance = max(0, mortgage_balances[-1] - principal_payment)
        mortgage_balances.append(new_balance)

        buy_wealth.append(new_property_value - new_balance)

        annual_rent = custom_rent if custom_rent else new_property_value * rent_yield
        rents.append(annual_rent)
        cum_rent.append(cum_rent[-1] + annual_rent)

        investable = max(0, monthly_PMT*12 - annual_rent)
        epf_wealth.append(epf_wealth[-1]*(1 + epf_rate/12)**12 + investable)

    buy_cagr = [( (buy_wealth[i]/buy_wealth[0])**(1/i) - 1 if i>0 else 0) for i in range(len(buy_wealth))]
    epf_cagr = [( (epf_wealth[i]/epf_wealth[0])**(1/i) - 1 if i>0 else 0) for i in range(len(epf_wealth))]

    return pd.DataFrame({
        "Year": np.arange(0, years + 1),
        "Property Value": property_values,
        "Mortgage Balance": mortgage_balances,
        "Buy Wealth (RM)": buy_wealth,
        "EPF Wealth (RM)": epf_wealth,
        "Annual Rent": rents,
        "Cumulative Rent": cum_rent,
        "Buy CAGR": buy_cagr,
        "EPF CAGR": epf_cagr
    })

# --------------------------
# 3. Sidebar Inputs
# --------------------------
st.sidebar.header("⚙️ Assumptions")
purchase_price = st.sidebar.number_input("Property Price (RM)", value=500_000, step=50_000)
down_payment = st.sidebar.number_input("Down Payment (RM)", value=100_000, step=10_000)
loan_amount = purchase_price - down_payment

mortgage_rate = st.sidebar.slider("Mortgage Rate (Annual)", 0.01, 0.08, 0.04, 0.005)
property_growth = st.sidebar.slider("Property Growth Rate (Annual)", 0.01, 0.10, 0.05, 0.005)
rent_yield = st.sidebar.slider("Rent Yield", 0.01, 0.10, 0.04, 0.005)
epf_rate = st.sidebar.slider("EPF Return Rate (Annual)", 0.01, 0.10, 0.06, 0.005)

mortgage_term = st.sidebar.number_input("Mortgage Term (Years)", value=30, step=5)
projection_years = st.sidebar.number_input("Projection Years", value=30, step=5)

use_custom_rent = st.sidebar.checkbox("Use Custom Starting Rent?")
custom_rent = st.sidebar.number_input("Custom Starting Annual Rent (RM)", value=20000, step=1000) if use_custom_rent else None

sensitivity_pct = st.sidebar.slider("Sensitivity Range (%)", min_value=1, max_value=50, value=10, step=1)

# --------------------------
# 4. Run Projection
# --------------------------
df = project_buy_rent(
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

break_even_year = next((row.Year for i,row in df.iterrows() if row["Buy Wealth (RM)"] > row["EPF Wealth (RM)"]), None)

# --------------------------
# 5. Tabs
# --------------------------
tab1, tab2, tab3 = st.tabs(["📈 Chart", "📊 Table", "📝 Summary"])

with tab1:
    st.subheader("📈 Wealth Projection Over Time")
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=df["Year"], y=df["Buy Wealth (RM)"], mode='lines+markers', name='🏡 Buy Property', line=dict(color='royalblue', width=3)))
    fig.add_trace(go.Scatter(x=df["Year"], y=df["EPF Wealth (RM)"], mode='lines+markers', name='💰 Rent+EPF', line=dict(color='seagreen', width=3)))
    if break_even_year:
        fig.add_vline(x=break_even_year, line=dict(color='orange', dash='dash', width=2))
        fig.add_annotation(x=break_even_year, y=max(df["Buy Wealth (RM)"].max(), df["EPF Wealth (RM)"].max()),
                           text=f"📍 Break-even Year: {break_even_year}", showarrow=True, arrowhead=2, ax=-40, ay=-40, font=dict(color="orange", size=12))
    fig.update_layout(title=f"Wealth Projection ({projection_years} Years)", xaxis_title="Year", yaxis_title="Wealth (RM)", template="plotly_white")
    st.plotly_chart(fig, use_container_width=True)

with tab2:
    st.subheader("📊 Projection Table")
    st.dataframe(df, use_container_width=True)

with tab3:
    st.subheader("📝 Summary")
    final_buy = df["Buy Wealth (RM)"].iloc[-1]
    final_epf = df["EPF Wealth (RM)"].iloc[-1]
    winner_value = "🏡 Buy Property" if final_buy>final_epf else "💰 Rent+EPF"
    st.markdown(f"""
### Key Outcomes
- **Final Buy Wealth:** RM {final_buy:,.0f}  
- **Final EPF Wealth:** RM {final_epf:,.0f}  
- **Winner (Final Wealth):** {winner_value}  
- **Break-even Year:** {break_even_year if break_even_year else 'No break-even'}  
""")

# --------------------------
# 6. Sensitivity Analysis
# --------------------------
params = {
    "Mortgage Rate": mortgage_rate,
    "Property Growth": property_growth,
    "EPF Rate": epf_rate,
    "Rent Yield": rent_yield
}

sensitivity_results = []

for param_name, base_val in params.items():
    low = base_val*(1 - sensitivity_pct/100)
    high = base_val*(1 + sensitivity_pct/100)

    kwargs_low = dict(P=purchase_price, loan_amount=loan_amount, mortgage_rate=mortgage_rate, mortgage_term=mortgage_term,
                      property_growth=property_growth, epf_rate=epf_rate, rent_yield=rent_yield, years=projection_years,
                      down_payment=down_payment, custom_rent=custom_rent)
    kwargs_low[param_name.replace(" ", "_").lower()] = low
    df_low = project_buy_rent(**kwargs_low)

    kwargs_high = kwargs_low.copy()
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

st.subheader(f"🌪️ Sensitivity Analysis (±{sensitivity_pct}%)")
st.dataframe(df_sensitivity, use_container_width=True)

# Tornado charts for presentation clarity
st.subheader("🎯 Tornado Charts")

# Buy Wealth
df_buy = df_sensitivity[['Parameter', 'Buy Low', 'Buy High']].copy()
df_buy['Impact'] = df_buy['Buy High'] - df_buy['Buy Low']
df_buy = df_buy.sort_values('Impact', ascending=True)
fig_buy = go.Figure(go.Bar(x=df_buy['Impact'], y=df_buy['Parameter'], orientation='h', marker_color='royalblue'))
fig_buy.update_layout(title='Buy Wealth Sensitivity', xaxis_title='Impact (RM)', yaxis_title='')
st.plotly_chart(fig_buy, use_container_width=True)

# EPF Wealth
df_epf = df_sensitivity[['Parameter', 'EPF Low', 'EPF High']].copy()
df_epf['Impact'] = df_epf['EPF High'] - df_epf['EPF Low']
df_epf = df_epf.sort_values('Impact', ascending=True)
fig_epf = go.Figure(go.Bar(x=df_epf['Impact'], y=df_epf['Parameter'], orientation='h', marker_color='seagreen'))
fig_epf.update_layout(title='EPF Wealth Sensitivity', xaxis_title='Impact (RM)', yaxis_title='')
st.plotly_chart(fig_epf, use_container_width=True)

# Top drivers summary cards
top_buy = df_sensitivity.sort_values("Buy Impact", ascending=False).iloc[0]
top_epf = df_sensitivity.sort_values("EPF Impact", ascending=False).iloc[0]

st.markdown(f"""
### 🏆 Top Drivers
- **Buy Property – Most Sensitive Factor:** {top_buy['Parameter']} (Impact: RM {top_buy['Buy Impact']:,.0f})  
- **Rent+EPF – Most Sensitive Factor:** {top_epf['Parameter']} (Impact: RM {top_epf['EPF Impact']:,.0f})  
""")

# --------------------------
# 7. CSV Download
# --------------------------
csv_bytes = df.to_csv(index=False).encode('utf-8')
st.download_button("📥 Download Projection Data (CSV)", data=csv_bytes, file_name="buy_vs_rent_epf_projection.csv", mime="text/csv")
