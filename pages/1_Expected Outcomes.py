import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import matplotlib

# --------------------------
# 1. Global Settings
# --------------------------
st.set_page_config(page_title='Expected Outcomes – Buy vs Rent+EPF', layout='wide')

st.markdown("""
<style>
html, body, [class*="css"] {
    font-family: 'Times New Roman', serif !important;
}
</style>
""", unsafe_allow_html=True)
matplotlib.rcParams['font.family'] = 'Times New Roman'

st.title("📌 Expected Outcomes – Buy Property vs Rent+EPF (Fair Comparison)")

# --------------------------
# 2. Helper Functions
# --------------------------
def calculate_mortgage_payment(P, r, n):
    return P * (r * (1 + r)**n) / ((1 + r)**n - 1) if r > 0 else P / n

def project_outcomes(P, r, n, g, epf_rate, rent_yield, years, custom_rent=None):
    PMT = calculate_mortgage_payment(P, r, n)
    property_values, mortgage_balances = [P], [P]
    buy_wealth, epf_wealth, rents, cum_rent = [0], [0], [], []

    initial_rent = custom_rent if custom_rent is not None else P * rent_yield
    rents.append(initial_rent)
    cum_rent.append(initial_rent)

    for t in range(1, years + 1):
        # Property and mortgage
        new_property_value = property_values[-1] * (1 + g)
        property_values.append(new_property_value)

        interest_payment = mortgage_balances[-1] * r
        principal_payment = PMT - interest_payment
        new_mortgage_balance = max(0, mortgage_balances[-1] - principal_payment)
        mortgage_balances.append(new_mortgage_balance)

        new_buy_wealth = new_property_value - new_mortgage_balance
        buy_wealth.append(new_buy_wealth)

        # Rent and EPF
        rent_payment = custom_rent if custom_rent is not None else new_property_value * rent_yield
        rents.append(rent_payment)
        cum_rent.append(cum_rent[-1] + rent_payment)

        investable = max(0, PMT - rent_payment)
        new_epf_wealth = epf_wealth[-1] * (1 + epf_rate) + investable
        epf_wealth.append(new_epf_wealth)

    # Compute CAGR
    buy_cagr = [( (buy_wealth[i]/buy_wealth[1])**(1/i)-1 if i>0 else 0) for i in range(len(buy_wealth))]
    epf_cagr = [( (epf_wealth[i]/epf_wealth[1])**(1/i)-1 if i>0 else 0) for i in range(len(epf_wealth))]

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
st.sidebar.header("⚙️ Baseline Assumptions")
initial_property_price = st.sidebar.number_input("Initial Property Price (RM)", value=500_000, step=50_000)
mortgage_rate = st.sidebar.number_input("Mortgage Rate (Annual)", value=0.04, step=0.01)
loan_term_years = st.sidebar.number_input("Loan Term (Years)", value=30, step=5)
property_growth = st.sidebar.number_input("Property Growth Rate (Annual)", value=0.05, step=0.01)
epf_rate = st.sidebar.number_input("EPF Return Rate (Annual)", value=0.06, step=0.01)
rent_yield = st.sidebar.number_input("Rent Yield (from EDA)", value=0.04, step=0.005)
projection_years = st.sidebar.number_input("Projection Years", value=30, step=5)
use_custom_rent = st.sidebar.checkbox("Use Custom Starting Rent?")
custom_rent = st.sidebar.number_input("Custom Starting Annual Rent (RM)", value=20000, step=1000) if use_custom_rent else None

# --------------------------
# 4. Link to EDA Insights
# --------------------------
st.subheader("🔗 Link to EDA Insights")
st.markdown("Expected outcomes are informed by **EDA insights** on property growth, EPF returns, and rent trends.")
with st.expander("📊 How EDA Informs Expected Outcomes"):
    st.markdown("""
        - 🏠 Property Growth: Historical market appreciation  
        - 💰 EPF Returns: Dividend trends  
        - 📈 Inflation: Realistic ranges for long-term projection
    """)

# --------------------------
# 5. Baseline Assumptions Table
# --------------------------
st.subheader("📌 Baseline Assumptions")
st.markdown("""
| Parameter | Baseline Value | Source / Justification |
|-----------|----------------|----------------------|
| Initial Property Price | RM 500,000 | Typical local property |
| Annual Property Growth | 5% | Historical appreciation |
| Mortgage Rate | 4% | Current bank rates |
| Loan Term | 30 yrs | Standard mortgage |
| EPF Annual Growth | 6% | Historical dividend trends |
| Projection Years | 30 | Long-term horizon |
""")

# --------------------------
# 6. Projection
# --------------------------
df = project_outcomes(initial_property_price, mortgage_rate, loan_term_years,
                      property_growth, epf_rate, rent_yield, projection_years, custom_rent)

# Break-even year
break_even_year = next((row.Year for i,row in df.iterrows() if row["Buy Wealth (RM)"]>row["EPF Wealth (RM)"]), None)

# --------------------------
# 7. Tabs: Chart / Table / Summary
# --------------------------
tab1, tab2, tab3 = st.tabs(["📈 Chart", "📊 Table", "📝 Summary"])

# ----- Tab 1: Chart -----
with tab1:
    st.subheader("📈 Scenario Comparison")
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=df["Year"], y=df["Buy Wealth (RM)"], mode='lines+markers',
        name='🏡 Buy Property', line=dict(color='blue', width=3)
    ))
    fig.add_trace(go.Scatter(
        x=df["Year"], y=df["EPF Wealth (RM)"], mode='lines+markers',
        name='💰 Rent+EPF', line=dict(color='green', width=3)
    ))
    fig.add_trace(go.Scatter(
        x=df["Year"], y=df["Cumulative Rent"], mode='lines', 
        name='💸 Cumulative Rent', line=dict(color='red', width=2, dash='dash')
    ))

    # Break-even line
    if break_even_year:
        fig.add_vline(x=break_even_year, line=dict(color='orange', dash='dash', width=2))
        fig.add_annotation(
            x=break_even_year, y=max(df["Buy Wealth (RM)"].max(), df["EPF Wealth (RM)"].max()),
            text=f"📍 Break-even: Year {break_even_year}", showarrow=False, yanchor="bottom",
            font=dict(color="orange", size=12)
        )

    fig.update_layout(
        title=f"Comparison Over {projection_years} Years",
        xaxis_title="Year", yaxis_title="Wealth / Rent (RM)",
        template="simple_white", legend=dict(orientation="h", y=-0.2, x=0.5, xanchor="center")
    )
    st.plotly_chart(fig, use_container_width=True)

# ----- Tab 2: Table -----
with tab2:
    st.subheader("📊 Key Metrics Table")
    metrics = pd.DataFrame({
        "Scenario": ["🏡 Buy Property", "💰 Rent+EPF"],
        "Final Value (RM)": [df["Buy Wealth (RM)"].iloc[-1], df["EPF Wealth (RM)"].iloc[-1]],
        "CAGR (%)": [df["Buy CAGR"].iloc[-1]*100, df["EPF CAGR"].iloc[-1]*100]
    })
    metrics["Final Value (RM)"] = metrics["Final Value (RM)"].map("RM {:,.0f}".format)
    metrics["CAGR (%)"] = metrics["CAGR (%)"].round(2)

    st.dataframe(metrics, use_container_width=True)

# ----- Tab 3: Summary -----
with tab3:
    st.subheader("📝 Interpretation")

    final_buy = df["Buy Wealth (RM)"].iloc[-1]
    final_epf = df["EPF Wealth (RM)"].iloc[-1]
    cagr_buy = df["Buy CAGR"].iloc[-1]*100
    cagr_epf = df["EPF CAGR"].iloc[-1]*100

    winner_value = "🏡 <span style='color:blue'>Buy Property</span>" if final_buy>final_epf else "💰 <span style='color:green'>Rent+EPF</span>"
    winner_cagr = "🏡 <span style='color:blue'>Buy Property</span>" if cagr_buy>cagr_epf else "💰 <span style='color:green'>Rent+EPF</span>"
    break_text = f"📍 Break-even occurs at **Year {break_even_year}**" if break_even_year else "📍 No break-even within projection horizon."

    st.markdown(f"""
### Key Insights  
- **Final Wealth Winner:** {winner_value} (RM {final_buy:,.0f} vs RM {final_epf:,.0f})  
- **CAGR Winner:** {winner_cagr} ({cagr_buy:.2f}% vs {cagr_epf:.2f}%)  
- {break_text}

### Color & Icon Reference
- 🏡 Blue — Buy Property  
- 💰 Green — Rent+EPF  
- 📍 Orange Dashed Line — Break-even
""", unsafe_allow_html=True)

    st.markdown("""
### Recommendation  
- Prioritize **long-term wealth**: choose the final value winner.  
- Prioritize **growth efficiency (CAGR)**: choose the CAGR winner.  
- Consider personal factors: risk tolerance, liquidity, housing preference.
""", unsafe_allow_html=True)

# --------------------------
# 8. Sensitivity Analysis Note
# --------------------------
st.subheader("🧩 Sensitivity Analysis Note")
st.info("""
Detailed sensitivity analysis is available on the Modelling page.  
It examines how variations in mortgage rates, property growth, rental yield, and EPF returns affect long-term outcomes.
""")

# --------------------------
# 9. Download CSV
# --------------------------
csv = df.to_csv(index=False).encode('utf-8')
st.download_button("📥 Download Projection Data (CSV)", csv, "projection.csv", "text/csv", key='download-csv')
