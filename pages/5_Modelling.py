import streamlit as st
import numpy as np
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px

st.set_page_config(page_title="Buy vs Rent – Fair Comparison", layout="wide")
st.title("🏡 Buy vs Rent – Modelling & Sensitivity Analysis (Fair Comparison)")

# --------------------------
# 1. Helper Functions
# --------------------------
def calculate_monthly_mortgage(P, annual_rate, years):
    r = annual_rate / 12
    n = years * 12
    return P * (r * (1 + r)**n) / ((1 + r)**n - 1) if r > 0 else P / n

def project_buy_rent(P, loan_amount, mortgage_rate, mortgage_term, property_growth,
                     epf_rate, rent_yield, years, custom_rent=None):
    monthly_PMT = calculate_monthly_mortgage(loan_amount, mortgage_rate, mortgage_term)
    property_values = [P]
    mortgage_balances = [loan_amount]
    buy_wealth = [P - loan_amount]  # down payment as Year 0
    epf_wealth = [P - loan_amount]
    rents = []
    cum_rent = []

    # Initial rent
    annual_rent = custom_rent if custom_rent is not None else P * rent_yield
    rents.append(annual_rent)
    cum_rent.append(annual_rent)

    for t in range(1, years + 1):
        # Property growth
        new_property_value = property_values[-1] * (1 + property_growth)
        property_values.append(new_property_value)

        # Mortgage
        interest_payment = mortgage_balances[-1] * mortgage_rate
        principal_payment = monthly_PMT*12 - interest_payment
        new_mortgage_balance = max(0, mortgage_balances[-1] - principal_payment)
        mortgage_balances.append(new_mortgage_balance)

        # Buy wealth
        new_buy_wealth = new_property_value - new_mortgage_balance
        buy_wealth.append(new_buy_wealth)

        # Rent & EPF
        annual_rent = custom_rent if custom_rent is not None else new_property_value * rent_yield
        rents.append(annual_rent)
        cum_rent.append(cum_rent[-1] + annual_rent)
        investable = max(0, monthly_PMT*12 - annual_rent)
        new_epf_wealth = epf_wealth[-1]*(1 + epf_rate/12)**12 + investable
        epf_wealth.append(new_epf_wealth)

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
# 2. Sidebar Inputs
# --------------------------
st.sidebar.header("📌 Baseline Assumptions")
purchase_price = st.sidebar.number_input("Property Price (RM)", value=500_000, step=50_000)
down_payment = st.sidebar.number_input("Down Payment (RM)", value=100_000, step=10_000)
loan_amount = purchase_price - down_payment

mortgage_rate = st.sidebar.number_input("Mortgage Rate (Annual %)", value=4.0, step=0.5)/100
loan_term_years = st.sidebar.number_input("Loan Term (Years)", value=30, step=5)
property_growth = st.sidebar.number_input("Property Growth Rate (Annual %)", value=5.0, step=0.5)/100
epf_rate = st.sidebar.number_input("EPF Return Rate (Annual %)", value=6.0, step=0.5)/100
rent_yield = st.sidebar.number_input("Rent Yield (%)", value=4.0, step=0.5)/100
projection_years = st.sidebar.number_input("Projection Years", value=30, step=5)
use_custom_rent = st.sidebar.checkbox("Use Custom Starting Rent?")
custom_rent = st.sidebar.number_input("Custom Starting Annual Rent (RM)", value=20000, step=1000) if use_custom_rent else None

# --------------------------
# 3. Tabs: Base-case / Fair Comparison / Sensitivity
# --------------------------
tab1, tab2, tab3 = st.tabs(["📊 Base-case", "📈 Fair Comparison", "🧮 Sensitivity Analysis"])

# ----- Tab 1: Base-case -----
with tab1:
    st.subheader("📊 Base-case Wealth Accumulation")
    df_base = project_buy_rent(purchase_price, loan_amount, mortgage_rate, loan_term_years,
                               property_growth, epf_rate, rent_yield, projection_years, custom_rent)

    # Plot
    fig_base = go.Figure()
    fig_base.add_trace(go.Scatter(x=df_base["Year"], y=df_base["Buy Wealth (RM)"], mode='lines+markers', name='🏡 Buy Property'))
    fig_base.add_trace(go.Scatter(x=df_base["Year"], y=df_base["EPF Wealth (RM)"], mode='lines+markers', name='💰 Rent+EPF'))
    st.plotly_chart(fig_base, use_container_width=True)

    st.write(f"Final Buy Wealth: RM {df_base['Buy Wealth (RM)'].iloc[-1]:,.0f}")
    st.write(f"Final Rent+EPF Wealth: RM {df_base['EPF Wealth (RM)'].iloc[-1]:,.0f}")

# ----- Tab 2: Fair Comparison -----
with tab2:
    st.subheader("📈 Fair Comparison – Year 0 Starting Wealth Included")
    df_fair = df_base.copy()  # already includes down payment as Year 0
    # Add break-even year
    break_even_year = next((row.Year for i,row in df_fair.iterrows() if row["Buy Wealth (RM)"]>row["EPF Wealth (RM)"]), None)
    
    fig_fair = go.Figure()
    fig_fair.add_trace(go.Scatter(x=df_fair["Year"], y=df_fair["Buy Wealth (RM)"], mode='lines+markers', name='🏡 Buy Property'))
    fig_fair.add_trace(go.Scatter(x=df_fair["Year"], y=df_fair["EPF Wealth (RM)"], mode='lines+markers', name='💰 Rent+EPF'))
    
    if break_even_year:
        fig_fair.add_vline(x=break_even_year, line=dict(color='orange', dash='dash', width=2))
    
    st.plotly_chart(fig_fair, use_container_width=True)
    st.write(f"Break-even Year: {break_even_year if break_even_year else 'No break-even within horizon'}")

# ----- Tab 3: Sensitivity Analysis -----
with tab3:
    st.subheader("🧮 Sensitivity Analysis – Multiple Scenarios")
    # Parameter ranges
    mortgage_rates = [3, 4, 5, 6, 7]
    epf_returns = [4, 5, 6, 7, 8]
    appreciations = [2, 3, 4]
    rent_yields = [3, 4, 5]

    records = []
    for mr in mortgage_rates:
        for ir in epf_returns:
            for g in appreciations:
                for ry in rent_yields:
                    df_proj = project_buy_rent(
                        P=purchase_price,
                        loan_amount=loan_amount,
                        mortgage_rate=mr/100,
                        mortgage_term=loan_term_years,
                        property_growth=g/100,
                        epf_rate=ir/100,
                        rent_yield=ry/100,
                        years=projection_years
                    )
                    final_buy = df_proj["Buy Wealth (RM)"].iloc[-1]
                    final_epf = df_proj["EPF Wealth (RM)"].iloc[-1]
                    records.append({
                        "MortgageRate": mr, "InvestReturn": ir,
                        "Appreciation": g, "RentYield": ry,
                        "FinalBuyWealth": final_buy, "FinalEPFWealth": final_epf,
                        "Difference": final_buy - final_epf
                    })
    df_sens = pd.DataFrame(records)
    st.write(f"Total scenarios evaluated: {len(df_sens)}")

    # Interactive heatmap
    param_x = st.selectbox("X-axis parameter", ["MortgageRate","InvestReturn","Appreciation","RentYield"], index=0)
    param_y = st.selectbox("Y-axis parameter", ["MortgageRate","InvestReturn","Appreciation","RentYield"], index=1)

    pivot_heatmap = df_sens.pivot_table(index=param_y, columns=param_x, values="Difference", aggfunc="mean").fillna(0)

    fig_heatmap = px.imshow(pivot_heatmap.values, x=pivot_heatmap.columns, y=pivot_heatmap.index,
                            color_continuous_scale='RdBu_r', text_auto=True, aspect="auto")
    fig_heatmap.update_layout(xaxis_title=param_x, yaxis_title=param_y, coloraxis_colorbar=dict(title="Buy - Rent (RM)"))
    st.plotly_chart(fig_heatmap, use_container_width=True)

    # CSV download
    csv_sens = df_sens.to_csv(index=False).encode("utf-8")
    st.download_button("⬇️ Download Sensitivity Analysis (CSV)", data=csv_sens, file_name="buy_vs_rent_sensitivity_fair.csv", mime="text/csv")
