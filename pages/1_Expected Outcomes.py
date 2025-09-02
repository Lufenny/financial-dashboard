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
def calculate_monthly_mortgage(P, annual_rate, years):
    r = annual_rate / 12
    n = years * 12
    return P * (r * (1 + r)**n) / ((1 + r)**n - 1) if r > 0 else P / n

def project_outcomes(P, loan_amount, annual_mortgage_rate, loan_years, property_growth,
                     epf_rate, rent_yield, years, down_payment, custom_rent=None):
    monthly_PMT = calculate_monthly_mortgage(loan_amount, annual_mortgage_rate, loan_years)
    property_values = [P]
    mortgage_balances = [loan_amount]
    buy_wealth = [down_payment]  # Year 0
    epf_wealth = [down_payment]  # Year 0
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

        # Mortgage (annualized)
        interest_payment = mortgage_balances[-1] * annual_mortgage_rate
        principal_payment = monthly_PMT*12 - interest_payment
        new_mortgage_balance = max(0, mortgage_balances[-1] - principal_payment)
        mortgage_balances.append(new_mortgage_balance)

        # Buy wealth
        new_buy_wealth = new_property_value - new_mortgage_balance
        buy_wealth.append(new_buy_wealth)

        # Rent
        annual_rent = custom_rent if custom_rent is not None else new_property_value * rent_yield
        rents.append(annual_rent)
        cum_rent.append(cum_rent[-1] + annual_rent)

        # EPF wealth: leftover goes to EPF with monthly compounding
        investable = max(0, monthly_PMT*12 - annual_rent)
        new_epf_wealth = epf_wealth[-1]*(1 + epf_rate/12)**12 + investable
        epf_wealth.append(new_epf_wealth)

    # CAGR calculation
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
# 3. Sidebar Inputs with Sensitivity Sliders
# --------------------------
st.sidebar.header("⚙️ Baseline Assumptions & Sensitivity")
initial_property_price = st.sidebar.number_input("Initial Property Price (RM)", value=500_000, step=50_000)
down_payment = st.sidebar.number_input("Down Payment (RM)", value=100_000, step=10_000)
loan_amount = initial_property_price - down_payment

# Sensitivity sliders
mortgage_rate = st.sidebar.slider("Mortgage Rate (Annual)", 0.01, 0.08, 0.04, 0.005)
property_growth = st.sidebar.slider("Property Growth Rate (Annual)", 0.01, 0.10, 0.05, 0.005)
rent_yield = st.sidebar.slider("Rent Yield", 0.01, 0.10, 0.04, 0.005)
epf_rate = st.sidebar.slider("EPF Return Rate (Annual)", 0.01, 0.10, 0.06, 0.005)

loan_term_years = st.sidebar.number_input("Loan Term (Years)", value=30, step=5)
projection_years = st.sidebar.number_input("Projection Years", value=30, step=5)

# Optional custom rent
use_custom_rent = st.sidebar.checkbox("Use Custom Starting Rent?")
custom_rent = st.sidebar.number_input("Custom Starting Annual Rent (RM)", value=20000, step=1000) if use_custom_rent else None
if custom_rent and custom_rent > calculate_monthly_mortgage(loan_amount, mortgage_rate, loan_term_years)*12:
    st.warning("⚠️ Custom rent exceeds annual mortgage payment. EPF investable cash will be zero.")

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
st.markdown(f"""
| Parameter | Baseline Value | Source / Justification |
|-----------|----------------|----------------------|
| Initial Property Price | RM {initial_property_price:,.0f} | Typical local property |
| Down Payment | RM {down_payment:,.0f} | User-defined |
| Annual Property Growth | {property_growth*100:.1f}% | Historical appreciation |
| Mortgage Rate | {mortgage_rate*100:.1f}% | Current bank rates |
| Loan Term | {loan_term_years} yrs | Standard mortgage |
| EPF Annual Growth | {epf_rate*100:.1f}% | Historical dividend trends |
| Projection Years | {projection_years} | Long-term horizon |
| Rent Yield | {rent_yield*100:.1f}% | From EDA or user |
""")

# --------------------------
# 6. Projection
# --------------------------
df = project_outcomes(
    P=initial_property_price,
    loan_amount=loan_amount,
    annual_mortgage_rate=mortgage_rate,
    loan_years=loan_term_years,
    property_growth=property_growth,
    epf_rate=epf_rate,
    rent_yield=rent_yield,
    years=projection_years,
    down_payment=down_payment,
    custom_rent=custom_rent
)

# Break-even
break_even_year = next((row.Year for i,row in df.iterrows() if row["Buy Wealth (RM)"]>row["EPF Wealth (RM)"]), None)

# --------------------------
# 7. Tabs: Chart / Table / Summary
# --------------------------
tab1, tab2, tab3 = st.tabs(["📈 Chart", "📊 Table", "📝 Summary"])

# ----- Tab 1: Chart -----
with tab1:
    st.subheader("📈 Scenario Comparison")
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=df["Year"], y=df["Buy Wealth (RM)"], mode='lines+markers',
                             name='🏡 Buy Property', line=dict(color='blue', width=3)))
    fig.add_trace(go.Scatter(x=df["Year"], y=df["EPF Wealth (RM)"], mode='lines+markers',
                             name='💰 Rent+EPF', line=dict(color='green', width=3)))
    fig.add_trace(go.Scatter(x=df["Year"], y=df["Cumulative Rent"], mode='lines', 
                             name='💸 Cumulative Rent', line=dict(color='red', width=2, dash='dash')))
    if break_even_year:
        fig.add_vline(x=break_even_year, line=dict(color='orange', dash='dash', width=2))
        fig.add_annotation(x=break_even_year, y=max(df["Buy Wealth (RM)"].max(), df["EPF Wealth (RM)"].max()),
                           text=f"📍 Break-even: Year {break_even_year}", showarrow=False, yanchor="bottom",
                           font=dict(color="orange", size=12))
    # Year 0 annotation
    fig.add_annotation(x=0, y=df["Buy Wealth (RM)"].iloc[0], text=f"🏡 Start: RM {df['Buy Wealth (RM)'].iloc[0]:,.0f}", showarrow=True, arrowhead=2, ay=-40, font=dict(color="blue"))
    fig.add_annotation(x=0, y=df["EPF Wealth (RM)"].iloc[0], text=f"💰 Start: RM {df['EPF Wealth (RM)'].iloc[0]:,.0f}", showarrow=True, arrowhead=2, ay=-40, font=dict(color="green"))

    fig.update_layout(title=f"Comparison Over {projection_years} Years",
                      xaxis_title="Year", yaxis_title="Wealth / Rent (RM)",
                      template="simple_white", legend=dict(orientation="h", y=-0.2, x=0.5, xanchor="center"))
    st.plotly_chart(fig, use_container_width=True)

# ----- Tab 2: Table -----
with tab2:
    st.subheader("📊 Key Metrics Table (Fair Comparison)")
    metrics = pd.DataFrame({
        "Scenario": ["🏡 Buy Property", "💰 Rent+EPF"],
        "Starting Wealth (RM)": [df["Buy Wealth (RM)"].iloc[0], df["EPF Wealth (RM)"].iloc[0]],
        "Final Value (RM)": [df["Buy Wealth (RM)"].iloc[-1], df["EPF Wealth (RM)"].iloc[-1]],
        "CAGR (%)": [df["Buy CAGR"].iloc[-1]*100, df["EPF CAGR"].iloc[-1]*100]
    })
    metrics["Starting Wealth (RM)"] = metrics["Starting Wealth (RM)"].map("RM {:,.0f}".format)
    metrics["Final Value (RM)"] = metrics["Final Value (RM)"].map("RM {:,.0f}".format)
    metrics["CAGR (%)"] = metrics["CAGR (%)"].round(2)
    st.dataframe(metrics, use_container_width=True)

# ----- Tab 3: Summary -----
with tab3:
    st.subheader("📝 Interpretation – Fair Comparison")
    start_buy = df["Buy Wealth (RM)"].iloc[0]
    start_epf = df["EPF Wealth (RM)"].iloc[0]
    final_buy = df["Buy Wealth (RM)"].iloc[-1]
    final_epf = df["EPF Wealth (RM)"].iloc[-1]
    cagr_buy = df["Buy CAGR"].iloc[-1]*100
    cagr_epf = df["EPF CAGR"].iloc[-1]*100

    winner_value = "🏡 <span style='color:blue'>Buy Property</span>" if final_buy>final_epf else "💰 <span style='color:green'>Rent+EPF</span>"
    winner_cagr = "🏡 <span style='color:blue'>Buy Property</span>" if cagr_buy>cagr_epf else "💰 <span style='color:green'>Rent+EPF</span>"
    break_text = f"📍 Break-even occurs at **Year {break_even_year}**" if break_even_year else "📍 No break-even within projection horizon."

    st.markdown(f"""
### Key Insights  
- **Starting Wealth (Year 0):** 🏡 RM {start_buy:,.0f} vs 💰 RM {start_epf:,.0f}  
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
st.info("Adjust sliders in the sidebar to see real-time impact on wealth outcomes, break-even, and CAGR.")

# --------------------------
# 9. Download CSV
# --------------------------
csv_export = df.copy()
csv_export = csv_export[[
    "Year", "Buy Wealth (RM)", "EPF Wealth (RM)", "Buy CAGR", "EPF CAGR",
    "Annual Rent", "Cumulative Rent", "Property Value", "Mortgage Balance"
]]
csv_bytes = csv_export.to_csv(index=False).encode('utf-8')
st.download_button(
    label="📥 Download Projection Data (CSV)",
    data=csv_bytes,
    file_name="projection_fair_comparison.csv",
    mime="text/csv",
    key='download-csv'
)

# --------------------------
# Interactive Sensitivity Analysis
# --------------------------
st.subheader("🧩 Interactive Sensitivity Analysis")

# Sidebar: Sensitivity %
sensitivity_pct = st.sidebar.slider("Sensitivity Range (%)", min_value=1, max_value=50, value=10, step=1)

# --------------------------
# 1. Compute Sensitivity Table
# --------------------------
sens_df = pd.DataFrame({
    "Parameter": ["Mortgage Rate", "Property Growth", "EPF Rate", "Rent Yield"],
    "Base": [mortgage_rate, property_growth, epf_rate, rent_yield]
})

# Compute high/low scenarios
sens_df["Low"] = sens_df["Base"] * (1 - sensitivity_pct/100)
sens_df["High"] = sens_df["Base"] * (1 + sensitivity_pct/100)

# Placeholder lists for impacts
buy_low, buy_high, epf_low, epf_high = [], [], [], []

# Calculate projected outcomes for each parameter scenario
for idx, row in sens_df.iterrows():
    param = row["Parameter"]

    # Low scenario
    if param == "Mortgage Rate":
        df_low = project_outcomes(initial_property_price, loan_amount, row["Low"], loan_term_years,
                                  property_growth, epf_rate, rent_yield, projection_years, down_payment, custom_rent)
    elif param == "Property Growth":
        df_low = project_outcomes(initial_property_price, loan_amount, mortgage_rate, loan_term_years,
                                  row["Low"], epf_rate, rent_yield, projection_years, down_payment, custom_rent)
    elif param == "EPF Rate":
        df_low = project_outcomes(initial_property_price, loan_amount, mortgage_rate, loan_term_years,
                                  property_growth, row["Low"], rent_yield, projection_years, down_payment, custom_rent)
    elif param == "Rent Yield":
        df_low = project_outcomes(initial_property_price, loan_amount, mortgage_rate, loan_term_years,
                                  property_growth, epf_rate, row["Low"], projection_years, down_payment, custom_rent)
    buy_low.append(df_low["Buy Wealth (RM)"].iloc[-1])
    epf_low.append(df_low["EPF Wealth (RM)"].iloc[-1])

    # High scenario
    if param == "Mortgage Rate":
        df_high = project_outcomes(initial_property_price, loan_amount, row["High"], loan_term_years,
                                   property_growth, epf_rate, rent_yield, projection_years, down_payment, custom_rent)
    elif param == "Property Growth":
        df_high = project_outcomes(initial_property_price, loan_amount, mortgage_rate, loan_term_years,
                                   row["High"], epf_rate, rent_yield, projection_years, down_payment, custom_rent)
    elif param == "EPF Rate":
        df_high = project_outcomes(initial_property_price, loan_amount, mortgage_rate, loan_term_years,
                                   property_growth, row["High"], rent_yield, projection_years, down_payment, custom_rent)
    elif param == "Rent Yield":
        df_high = project_outcomes(initial_property_price, loan_amount, mortgage_rate, loan_term_years,
                                   property_growth, epf_rate, row["High"], projection_years, down_payment, custom_rent)
    buy_high.append(df_high["Buy Wealth (RM)"].iloc[-1])
    epf_high.append(df_high["EPF Wealth (RM)"].iloc[-1])

sens_df["Buy Low"] = buy_low
sens_df["Buy High"] = buy_high
sens_df["EPF Low"] = epf_low
sens_df["EPF High"] = epf_high

# Calculate impacts
sens_df["Buy Impact"] = sens_df["Buy High"] - sens_df["Buy Low"]
sens_df["EPF Impact"] = sens_df["EPF High"] - sens_df["EPF Low"]

# --------------------------
# 2. Tornado Chart with Highlights
# --------------------------
fig_tornado = go.Figure()
max_buy_idx = sens_df["Buy Impact"].idxmax()
max_epf_idx = sens_df["EPF Impact"].idxmax()

for i, row in sens_df.iterrows():
    buy_color = 'darkblue' if i == max_buy_idx else 'blue'
    epf_color = 'darkgreen' if i == max_epf_idx else 'green'

    fig_tornado.add_trace(go.Bar(
        y=[row["Parameter"]],
        x=[row["Buy High"] - row["Buy Low"]],
        base=row["Buy Low"],
        orientation='h',
        name='🏡 Buy Property' if i==0 else None,
        marker_color=buy_color,
        showlegend=i==0
    ))

    fig_tornado.add_trace(go.Bar(
        y=[row["Parameter"]],
        x=[row["EPF High"] - row["EPF Low"]],
        base=row["EPF Low"],
        orientation='h',
        name='💰 Rent+EPF' if i==0 else None,
        marker_color=epf_color,
        showlegend=i==0
    ))

# Add annotations for largest impacts
fig_tornado.add_annotation(
    x=sens_df.loc[max_buy_idx, "Buy High"],
    y=sens_df.loc[max_buy_idx, "Parameter"],
    text="🏡 Largest Impact",
    showarrow=True, arrowhead=2, ax=40, ay=0, font=dict(color="darkblue")
)
fig_tornado.add_annotation(
    x=sens_df.loc[max_epf_idx, "EPF High"],
    y=sens_df.loc[max_epf_idx, "Parameter"],
    text="💰 Largest Impact",
    showarrow=True, arrowhead=2, ax=40, ay=0, font=dict(color="darkgreen")
)

fig_tornado.update_layout(
    title=f"Tornado Chart with Highlighted Largest Impacts (±{sensitivity_pct}%)",
    barmode='overlay',
    xaxis_title="Final Wealth (RM)",
    yaxis_title="Parameter",
    template="simple_white",
    legend=dict(orientation="h", y=-0.2, x=0.5, xanchor="center")
)

st.plotly_chart(fig_tornado, use_container_width=True)

# --------------------------
# 3. Impact Table
# --------------------------
impact_table = sens_df.copy()
for col in ["Buy Low", "Buy High", "Buy Impact", "EPF Low", "EPF High", "EPF Impact"]:
    impact_table[col] = impact_table[col].map(lambda x: f"RM {x:,.0f}")

st.dataframe(
    impact_table[["Parameter", "Buy Low", "Buy High", "Buy Impact", "EPF Low", "EPF High", "EPF Impact"]],
    use_container_width=True
)

# --------------------------
# 4. Top Drivers Summary
# --------------------------
top_buy_drivers = sens_df.sort_values("Buy Impact", ascending=False).head(2)
top_epf_drivers = sens_df.sort_values("EPF Impact", ascending=False).head(2)

buy_text = ", ".join([f"{row['Parameter']} (RM {row['Buy Impact']:,.0f})" for _, row in top_buy_drivers.iterrows()])
epf_text = ", ".join([f"{row['Parameter']} (RM {row['EPF Impact']:,.0f})" for _, row in top_epf_drivers.iterrows()])

st.markdown(f"""
- 🏡 **Buy Property – Top Drivers:** {buy_text}  
- 💰 **Rent+EPF – Top Drivers:** {epf_text}  
""")

# --------------------------
# 5. Automated Recommendation
# --------------------------
st.subheader("💡 Sensitivity Recommendation")

# Identify the largest single driver per scenario
largest_buy = top_buy_drivers.iloc[0]
largest_epf = top_epf_drivers.iloc[0]

st.markdown(f"""
- 🏡 **Buy Property:** The most sensitive factor is **{largest_buy['Parameter']}**, with an impact of **RM {largest_buy['Buy Impact']:,.0f}**.  
  ⚠️ Recommendation: Monitor this parameter closely; small changes here can significantly affect your long-term wealth.

- 💰 **Rent+EPF:** The most sensitive factor is **{largest_epf['Parameter']}**, with an impact of **RM {largest_epf['EPF Impact']:,.0f}**.  
  ⚠️ Recommendation: This parameter largely drives your EPF wealth outcome; adjust contributions or strategy if necessary.
""")

