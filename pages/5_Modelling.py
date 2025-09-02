import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go

# --------------------------
# 1. Global Settings
# --------------------------
st.set_page_config(page_title="Buy vs Rent Full Model", layout="wide")
st.title("🏡 Buy vs Rent + EPF Model with Sensitivity Analysis")

st.markdown("""
<style>
html, body, [class*="css"] {
    font-family: 'Times New Roman', serif !important;
}
</style>
""", unsafe_allow_html=True)

# --------------------------
# 2. Helper Functions
# --------------------------
def calculate_monthly_mortgage(P, annual_rate, years):
    r = annual_rate / 12
    n = years * 12
    return P * (r * (1 + r)**n) / ((1 + r)**n - 1) if r > 0 else P / n

def project_buy_rent(P, loan_amount, mortgage_rate, mortgage_term, property_growth,
                     epf_rate, rent_yield, years, down_payment=0):
    monthly_PMT = calculate_monthly_mortgage(loan_amount, mortgage_rate, mortgage_term)
    property_values = [P]
    mortgage_balances = [loan_amount]
    buy_wealth = [down_payment]  # Year 0
    epf_wealth = [down_payment]  # Year 0
    rents = []
    cum_rent = []

    annual_rent = P * rent_yield
    rents.append(annual_rent)
    cum_rent.append(annual_rent)

    for t in range(1, years+1):
        # Property growth
        new_property_value = property_values[-1] * (1 + property_growth)
        property_values.append(new_property_value)

        # Mortgage balance
        interest_payment = mortgage_balances[-1] * mortgage_rate
        principal_payment = monthly_PMT*12 - interest_payment
        new_balance = max(0, mortgage_balances[-1] - principal_payment)
        mortgage_balances.append(new_balance)

        # Buy wealth
        buy_wealth.append(new_property_value - new_balance)

        # Rent & cumulative
        annual_rent = new_property_value * rent_yield
        rents.append(annual_rent)
        cum_rent.append(cum_rent[-1] + annual_rent)

        # EPF investment
        investable = max(0, monthly_PMT*12 - annual_rent)
        epf_wealth.append(epf_wealth[-1]*(1 + epf_rate/12)**12 + investable)

    # CAGR
    buy_cagr = [( (buy_wealth[i]/buy_wealth[0])**(1/i) - 1 if i>0 else 0) for i in range(len(buy_wealth))]
    epf_cagr = [( (epf_wealth[i]/epf_wealth[0])**(1/i) - 1 if i>0 else 0) for i in range(len(epf_wealth))]

    return pd.DataFrame({
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

# --------------------------
# 3. Sidebar Inputs
# --------------------------
st.sidebar.header("📌 Baseline Assumptions")
purchase_price = st.sidebar.number_input("Property Price (RM)", value=500_000, step=50_000)
down_payment = st.sidebar.number_input("Down Payment (RM)", value=100_000, step=10_000)
loan_amount = purchase_price - down_payment
mortgage_rate = st.sidebar.number_input("Mortgage Rate (Annual)", value=0.04, step=0.01)
mortgage_term = st.sidebar.number_input("Mortgage Term (Years)", value=30, step=5)
property_growth = st.sidebar.number_input("Property Growth Rate (Annual)", value=0.05, step=0.01)
epf_rate = st.sidebar.number_input("EPF Return Rate (Annual)", value=0.06, step=0.01)
rent_yield = st.sidebar.number_input("Rent Yield", value=0.04, step=0.005)
projection_years = st.sidebar.number_input("Projection Years", value=30, step=5)

# --------------------------
# 4. Project Base-case / Fair Comparison
# --------------------------
df_base = project_buy_rent(
    P=purchase_price,
    loan_amount=loan_amount,
    mortgage_rate=mortgage_rate,
    mortgage_term=mortgage_term,
    property_growth=property_growth,
    epf_rate=epf_rate,
    rent_yield=rent_yield,
    years=projection_years,
    down_payment=down_payment
)

break_even_year = next((row.Year for i,row in df_base.iterrows() if row["Buy Wealth (RM)"]>row["EPF Wealth (RM)"]), None)

# --------------------------
# 5. Tabs: Base-case / Charts / Summary / Sensitivity
# --------------------------
tab1, tab2, tab3 = st.tabs(["📈 Chart", "📊 Table", "📝 Summary"])

# --- Tab 1: Chart ---
with tab1:
    st.subheader("📈 Buy vs Rent+EPF Over Time")
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=df_base["Year"], y=df_base["Buy Wealth (RM)"], mode='lines+markers', name='🏡 Buy Property', line=dict(color='blue', width=3)))
    fig.add_trace(go.Scatter(x=df_base["Year"], y=df_base["EPF Wealth (RM)"], mode='lines+markers', name='💰 Rent+EPF', line=dict(color='green', width=3)))
    fig.add_trace(go.Scatter(x=df_base["Year"], y=df_base["Cumulative Rent"], mode='lines', name='💸 Cumulative Rent', line=dict(color='red', width=2, dash='dash')))
    
    if break_even_year:
        fig.add_vline(x=break_even_year, line=dict(color='orange', dash='dash', width=2))
        fig.add_annotation(x=break_even_year, y=max(df_base["Buy Wealth (RM)"].max(), df_base["EPF Wealth (RM)"].max()),
                           text=f"📍 Break-even: Year {break_even_year}", showarrow=False, yanchor="bottom", font=dict(color="orange", size=12))

    st.plotly_chart(fig, use_container_width=True)

# --- Tab 2: Table ---
with tab2:
    st.subheader("📊 Key Metrics")
    metrics = pd.DataFrame({
        "Scenario": ["🏡 Buy Property", "💰 Rent+EPF"],
        "Starting Wealth (RM)": [df_base["Buy Wealth (RM)"].iloc[0], df_base["EPF Wealth (RM)"].iloc[0]],
        "Final Value (RM)": [df_base["Buy Wealth (RM)"].iloc[-1], df_base["EPF Wealth (RM)"].iloc[-1]],
        "CAGR (%)": [df_base["Buy CAGR"].iloc[-1]*100, df_base["EPF CAGR"].iloc[-1]*100]
    })
    st.dataframe(metrics, use_container_width=True)

# --- Tab 3: Summary + Sensitivity ---
with tab3:
    st.subheader("📝 Summary")
    final_buy = df_base["Buy Wealth (RM)"].iloc[-1]
    final_epf = df_base["EPF Wealth (RM)"].iloc[-1]
    winner_value = "🏡 Buy Property" if final_buy>final_epf else "💰 Rent+EPF"
    st.write(f"Final Wealth Winner: {winner_value} (RM{final_buy:,.0f} vs RM{final_epf:,.0f})")
    st.write(f"Break-even Year: {break_even_year if break_even_year else 'No break-even'}")

    st.subheader("🧮 Interactive Sensitivity Analysis")
    mr_min, mr_max = st.slider("Mortgage Rate Range (%)", 2, 8, (3,7))
    ir_min, ir_max = st.slider("EPF Return Range (%)", 2, 12, (4,8))
    g_min, g_max = st.slider("Property Appreciation Range (%)", 0, 6, (2,4))
    ry_min, ry_max = st.slider("Rent Yield Range (%)", 2, 6, (3,5))
    
    mr_step = st.number_input("Mortgage Step (%)", value=1)
    ir_step = st.number_input("EPF Step (%)", value=1)
    g_step = st.number_input("Appreciation Step (%)", value=1)
    ry_step = st.number_input("Rent Yield Step (%)", value=1)

    mortgage_rates = np.arange(mr_min, mr_max+mr_step, mr_step)
    epf_returns = np.arange(ir_min, ir_max+ir_step, ir_step)
    appreciations = np.arange(g_min, g_max+g_step, g_step)
    rent_yields = np.arange(ry_min, ry_max+ry_step, ry_step)

    records = []
    for mr in mortgage_rates:
        for ir in epf_returns:
            for g in appreciations:
                for ry in rent_yields:
                    df_proj = project_buy_rent(
                        P=purchase_price,
                        loan_amount=loan_amount,
                        mortgage_rate=mr/100,
                        mortgage_term=mortgage_term,
                        property_growth=g/100,
                        epf_rate=ir/100,
                        rent_yield=ry/100,
                        years=projection_years,
                        down_payment=down_payment
                    )
                    records.append({
                        "MortgageRate": mr, "InvestReturn": ir, "Appreciation": g, "RentYield": ry,
                        "FinalBuyWealth": df_proj["Buy Wealth (RM)"].iloc[-1],
                        "FinalEPFWealth": df_proj["EPF Wealth (RM)"].iloc[-1],
                        "Difference": df_proj["Buy Wealth (RM)"].iloc[-1] - df_proj["EPF Wealth (RM)"].iloc[-1]
                    })
    df_sens = pd.DataFrame(records)

    # Heatmap
    param_x = st.selectbox("X-axis", ["MortgageRate","InvestReturn","Appreciation","RentYield"], index=0)
    param_y = st.selectbox("Y-axis", ["MortgageRate","InvestReturn","Appreciation","RentYield"], index=1)
    pivot = df_sens.pivot_table(index=param_y, columns=param_x, values="Difference", aggfunc="mean").fillna(0)
    fig_heatmap = px.imshow(pivot.values, x=pivot.columns, y=pivot.index, color_continuous_scale="RdBu_r", text_auto=True)
    fig_heatmap.update_layout(xaxis_title=param_x, yaxis_title=param_y, coloraxis_colorbar=dict(title="Buy - Rent (RM)"))
    st.plotly_chart(fig_heatmap, use_container_width=True)

    csv_sens = df_sens.to_csv(index=False).encode("utf-8")
    st.download_button("⬇️ Download Sensitivity Analysis CSV", data=csv_sens, file_name="buy_vs_rent_full_sensitivity.csv", mime="text/csv")
