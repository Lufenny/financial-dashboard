import streamlit as st
import pandas as pd
import numpy as np
import matplotlib
import plotly.graph_objects as go

# --------------------------
# 1. Global Settings
# --------------------------
st.set_page_config(page_title='Expected Outcomes – Fair Comparison', layout='wide')

st.markdown("""
<style>
html, body, [class*="css"] {
    font-family: 'Times New Roman', serif !important;
}
.streamlit-expanderContent, 
.css-1d391kg p, .css-1d391kg h1, .css-1d391kg h2, .css-1d391kg h3,
.css-1d391kg h4, .css-1d391kg h5, .css-1d391kg h6 {
    font-family: 'Times New Roman', serif;
}
</style>
""", unsafe_allow_html=True)

matplotlib.rcParams['font.family'] = 'Times New Roman'
st.title("📌 Expected Outcomes – Buy Property vs Rent+EPF")

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
        new_property_value = property_values[-1] * (1 + g)
        property_values.append(new_property_value)

        interest_payment = mortgage_balances[-1] * r
        principal_payment = PMT - interest_payment
        new_mortgage_balance = max(0, mortgage_balances[-1] - principal_payment)
        mortgage_balances.append(new_mortgage_balance)

        new_buy_wealth = new_property_value - new_mortgage_balance
        buy_wealth.append(new_buy_wealth)

        rent_payment = custom_rent if custom_rent is not None else new_property_value * rent_yield
        rents.append(rent_payment)
        cum_rent.append(cum_rent[-1] + rent_payment)

        investable = max(0, PMT - rent_payment)
        new_epf_wealth = epf_wealth[-1] * (1 + epf_rate) + investable
        epf_wealth.append(new_epf_wealth)

    return pd.DataFrame({
        "Year": np.arange(0, years + 1),
        "Property (RM)": property_values,
        "Mortgage (RM)": mortgage_balances,
        "Buy Wealth (RM)": buy_wealth,
        "EPF Wealth (RM)": epf_wealth,
        "Annual Rent (RM)": rents,
        "Cumulative Rent (RM)": cum_rent
    })

def calculate_cagr(initial, final, years):
    if years <=0 or final<=0 or initial<=0:
        return 0
    return (final/initial)**(1/years)-1
    
# --------------------------
# 3. Format Table with Highlights & CAGR Colors
# --------------------------
def format_table(df):
    df_fmt = df.copy()

    # Save numeric values before formatting
    buy_final, epf_final = df["Buy Wealth (RM)"].iloc[-1], df["EPF Wealth (RM)"].iloc[-1]
    buy_initial = next((x for x in df["Buy Wealth (RM)"] if x > 0), 1)
    epf_initial = next((x for x in df["EPF Wealth (RM)"] if x > 0), 1)
    years = df["Year"].iloc[-1]
    buy_cagr = calculate_cagr(buy_initial, buy_final, years)
    epf_cagr = calculate_cagr(epf_initial, epf_final, years)

    # Format with RM
    for col in ["Property (RM)", "Mortgage (RM)", "Buy Wealth (RM)", "EPF Wealth (RM)", "Annual Rent (RM)", "Cumulative Rent (RM)"]:
        df_fmt[col] = df_fmt[col].apply(lambda x: f"RM {x:,.0f}")

    winner_col = "Buy Wealth (RM)" if buy_final > epf_final else "EPF Wealth (RM)"
    break_even_year_idx = next((i for i, (b, e) in enumerate(zip(df["Buy Wealth (RM)"], df["EPF Wealth (RM)"])) if b > e), None)

    def highlight_rows(row):
        styles = ['' for _ in df_fmt.columns]
        if row.name == df.index[-1]:
            styles = ['background-color: lightgreen' if col == winner_col else '' for col in df_fmt.columns]
        if break_even_year_idx is not None and row.name == break_even_year_idx:
            styles = ['background-color: lightyellow' for _ in df_fmt.columns]
        return styles

    def color_cagr(val, column):
        if column == "Buy Wealth (RM)":
            return 'color: green;' if buy_cagr >= 0 else 'color: red;'
        elif column == "EPF Wealth (RM)":
            return 'color: green;' if epf_cagr >= 0 else 'color: red;'
        return ''

    styled = df_fmt.style.apply(highlight_rows, axis=1)\
                         .apply(lambda row: [color_cagr(v, col) for col, v in zip(row, df_fmt.columns)], axis=1)\
                         .set_properties(**{'font-family':'Times New Roman','font-size':'14px'})
    return styled

# --------------------------
# 4. Generate Summary with Emojis
# --------------------------
def generate_summary(df, years):
    buy_final = df["Buy Wealth (RM)"].iloc[-1]
    epf_final = df["EPF Wealth (RM)"].iloc[-1]
    rent_final = df["Cumulative Rent (RM)"].iloc[-1]

    buy_initial = next((x for x in df["Buy Wealth (RM)"] if x>0),1)
    epf_initial = next((x for x in df["EPF Wealth (RM)"] if x>0),1)

    buy_cagr = calculate_cagr(buy_initial, buy_final, years)
    epf_cagr = calculate_cagr(epf_initial, epf_final, years)

    winner = "🏆 Buy Property" if buy_final>epf_final else "🏆 Rent+EPF"
    ratio = buy_final/epf_final if epf_final>0 else float('inf')

    break_even_year = next((year for year, buy, epf in zip(df["Year"], df["Buy Wealth (RM)"], df["EPF Wealth (RM)"]) if buy>epf), None)

    summary = f"""
### 📊 Expected Outcomes after {years} Years  

- 💰 **Buy Property Wealth**: RM {buy_final:,.0f}  (CAGR: {buy_cagr*100:.2f}%)  
- 💰 **Rent+EPF Wealth**: RM {epf_final:,.0f}  (CAGR: {epf_cagr*100:.2f}%)  
- 💸 **Cumulative Rent Paid**: RM {rent_final:,.0f}  
- 📊 **Wealth Ratio (Buy ÷ Rent+EPF)**: {ratio:.2f}x  
"""
    if break_even_year is not None:
        summary += f"- 🟡 **Break-even Year**: Year {break_even_year} (Buy Property surpasses Rent+EPF)\n"

    summary += f"\n{winner}"
    return summary

# --------------------------
# 5. Plotly Chart with Emojis
# --------------------------
def plot_outcomes_interactive(df, years, PMT):
    buy_final, epf_final = df["Buy Wealth (RM)"].iloc[-1], df["EPF Wealth (RM)"].iloc[-1]
    winner_name = "🏆 Buy Property" if buy_final > epf_final else "🏆 Rent+EPF"

    fig = go.Figure()
    break_even_year = next((year for year, buy, epf in zip(df["Year"], df["Buy Wealth (RM)"], df["EPF Wealth (RM)"]) if buy>epf), None)

    hover_text = []
    for _, row in df.iterrows():
        be_icon = "🟡 " if row["Year"] == break_even_year else ""
        hover_text.append(
            f"<b>Year:</b> {row['Year']}<br>"
            f"{be_icon}<b>Buy Property:</b> 💰 RM {row['Buy Wealth (RM)']:,.0f}<br>"
            f"<b>Rent+EPF:</b> 💰 RM {row['EPF Wealth (RM)']:,.0f}<br>"
            f"<b>Cumulative Rent:</b> 💸 RM {row['Cumulative Rent (RM)']:,.0f}"
        )

    # Buy Property trace
    fig.add_trace(go.Scatter(
        x=df["Year"], y=df["Buy Wealth (RM)"], mode='lines',
        line=dict(color='blue', width=3), name='Buy Property',
        text=hover_text, hovertemplate='%{text}<extra></extra>'
    ))

    # Rent+EPF trace
    fig.add_trace(go.Scatter(
        x=df["Year"], y=df["EPF Wealth (RM)"], mode='lines',
        line=dict(color='green', width=3), name='Rent+EPF',
        text=hover_text, hovertemplate='%{text}<extra></extra>'
    ))

    # Cumulative Rent trace
    fig.add_trace(go.Scatter(
        x=df["Year"], y=df["Cumulative Rent (RM)"], mode='lines',
        line=dict(color='red', width=2, dash='dash'), name='Cumulative Rent',
        text=hover_text, hovertemplate='%{text}<extra></extra>'
    ))

    # Dynamic shaded area for leader
    fig.add_trace(go.Scatter(
        x=df["Year"].tolist() + df["Year"].tolist()[::-1],
        y=df[["Buy Wealth (RM)", "EPF Wealth (RM)"]].max(axis=1).tolist() +
          df[["Buy Wealth (RM)", "EPF Wealth (RM)"]].min(axis=1).tolist()[::-1],
        fill='toself',
        fillcolor='rgba(0,255,0,0.1)',
        line=dict(color='rgba(255,255,255,0)'),
        hoverinfo='skip',
        showlegend=False
    ))

    if break_even_year is not None:
        fig.add_vline(
            x=break_even_year,
            line=dict(color='orange', dash='dash', width=2),
    )
        fig.add_annotation(
            x=break_even_year,
            y=max(df["Buy Wealth (RM)"].max(), df["EPF Wealth (RM)"].max()),
            text=f"🟡 Break-even: Year {break_even_year}",
            showarrow=False,
            yanchor="bottom",
            font=dict(color="orange", size=12)
        )

    fig.update_layout(
        title=f"Comparison Over {years} Years – Winner: {winner_name}",
        xaxis_title="Year", yaxis_title="Wealth / Rent (RM)",
        template="plotly_white", legend=dict(x=0.01, y=0.99),
        hovermode='x unified'
    )

    return fig

# --------------------------
# 6. Sidebar Inputs
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
custom_rent = None
if use_custom_rent:
    custom_rent = st.sidebar.number_input("Custom Starting Annual Rent (RM)", value=20000, step=1000)

# --------------------------
# 7. Link EDA Insights
# --------------------------
st.subheader("🔗 Link to EDA Insights")
st.markdown("The Expected Outcomes are shaped by insights from the **EDA**, providing assumptions for property growth, EPF returns, and inflation trends.")
with st.expander("📊 How EDA Informs Expected Outcomes"):
    st.markdown("""
        - 🏠 **Property Price Growth:** Historical market appreciation rates.
        - 💰 **EPF Returns:** Dividend trends inform baseline and optimistic scenarios.
        - 📈 **Inflation:** Guides realistic inflation ranges.
    """)

# --------------------------
# 8. Baseline Assumptions Table
# --------------------------
st.subheader("📌 Baseline Assumptions")
st.markdown("""
| Parameter | Baseline Value | Justification / Source |
|-----------|----------------|----------------------|
| Initial Property Price | RM 500,000 | Typical property price in target area |
| Annual Property Growth Rate | 5% | Historical market appreciation (10–20 yrs) |
| Mortgage Rate | 4% | Current average bank home loan rate |
| Loan Term | 30 years | Standard mortgage duration |
| EPF Annual Growth Rate | 6% | Historical EPF dividend trends |
| Projection Years | 30 | Long-term wealth accumulation horizon |
""")

# --------------------------
# 9. Projection
# --------------------------
df = project_outcomes(initial_property_price, mortgage_rate, loan_term_years,
                      property_growth, epf_rate, rent_yield, projection_years, custom_rent)

# --------------------------
# 10. Tabs: Chart / Table / Summary
# --------------------------
tab1, tab2, tab3 = st.tabs(["📈 Chart","📊 Table","📝 Summary"])

with tab1:
    st.subheader("📈 Scenario Comparison – Buy vs Rent+EPF")

    fig = go.Figure()
    break_even_year = next((year for year, buy, epf in zip(df["Year"], df["Buy Wealth (RM)"], df["EPF Wealth (RM)"]) if buy>epf), None)

    # Hover text
    hover_text = []
    for _, row in df.iterrows():
        be_icon = "🟡 " if row["Year"] == break_even_year else ""
        hover_text.append(
            f"<b>Year:</b> {row['Year']}<br>"
            f"{be_icon}<b>Buy Wealth:</b> 💰 RM {row['Buy Wealth (RM)']:,.0f}<br>"
            f"<b>EPF Wealth:</b> 💰 RM {row['EPF Wealth (RM)']:,.0f}<br>"
            f"<b>Cumulative Rent:</b> 💸 RM {row['Cumulative Rent (RM)']:,.0f}"
        )

    # Buy Wealth trace
    fig.add_trace(go.Scatter(
        x=df["Year"], y=df["Buy Wealth (RM)"], mode='lines+markers',
        line=dict(color='blue', width=3), name='🏡 Buy Property',
        text=hover_text, hovertemplate='%{text}<extra></extra>'
    ))

    # EPF Wealth trace
    fig.add_trace(go.Scatter(
        x=df["Year"], y=df["EPF Wealth (RM)"], mode='lines+markers',
        line=dict(color='green', width=3), name='💰 Rent+EPF',
        text=hover_text, hovertemplate='%{text}<extra></extra>'
    ))

    # Cumulative Rent trace
    fig.add_trace(go.Scatter(
        x=df["Year"], y=df["Cumulative Rent (RM)"], mode='lines',
        line=dict(color='red', width=2, dash='dash'), name='💸 Cumulative Rent',
        text=hover_text, hovertemplate='%{text}<extra></extra>'
    ))

    # Shaded area between Buy and EPF
    fig.add_trace(go.Scatter(
        x=df["Year"].tolist() + df["Year"].tolist()[::-1],
        y=df[["Buy Wealth (RM)", "EPF Wealth (RM)"]].max(axis=1).tolist() +
          df[["Buy Wealth (RM)", "EPF Wealth (RM)"]].min(axis=1).tolist()[::-1],
        fill='toself',
        fillcolor='rgba(0,255,0,0.1)',
        line=dict(color='rgba(255,255,255,0)'),
        hoverinfo='skip',
        showlegend=False
    ))

    # Break-even vertical line
    if break_even_year is not None:
        fig.add_vline(
            x=break_even_year,
            line=dict(color='orange', dash='dash', width=2),
        )
        fig.add_annotation(
            x=break_even_year,
            y=max(df["Buy Wealth (RM)"].max(), df["EPF Wealth (RM)"].max()),
            text=f"🟡 Break-even: Year {break_even_year}",
            showarrow=False,
            yanchor="bottom",
            font=dict(color="orange", size=12)
        )

    fig.update_layout(
        title=f"Comparison Over {projection_years} Years",
        xaxis_title="Year",
        yaxis_title="Wealth / Rent (RM)",
        template="plotly_white",
        legend=dict(x=0.01, y=0.99),
        hovermode='x unified'
    )

    st.plotly_chart(fig, use_container_width=True)

with tab2:
    st.subheader("📊 Key Metrics Table")
    years = df["Year"].iloc[-1]
    property_cagr = calculate_cagr(next(x for x in df["Buy Wealth (RM)"] if x>0),
                                   df["Buy Wealth (RM)"].iloc[-1], years)
    investment_cagr = calculate_cagr(next(x for x in df["EPF Wealth (RM)"] if x>0),
                                     df["EPF Wealth (RM)"].iloc[-1], years)

    metrics = pd.DataFrame({
        "Scenario": ["🏡 Property", "💰 Investment"],
        "Final Value (RM)": [df["Buy Wealth (RM)"].iloc[-1], df["EPF Wealth (RM)"].iloc[-1]],
        "CAGR (%)": [property_cagr*100, investment_cagr*100]
    })

    metrics["Final Value (RM)"] = metrics["Final Value (RM)"].map("RM {:,.0f}".format)
    metrics["CAGR (%)"] = metrics["CAGR (%)"].round(2)

    style = (
        metrics.style
        .highlight_max(subset=["Final Value (RM)"], color="royalblue", props="color:white;")
        .highlight_max(subset=["CAGR (%)"], color="darkorange", props="color:white;")
    )
    st.dataframe(style, use_container_width=True)

with tab3:
    st.subheader("📝 Interpretation")
    final_property = df["Buy Wealth (RM)"].iloc[-1]
    final_investment = df["EPF Wealth (RM)"].iloc[-1]

    winner_value = "🏡 Property" if final_property > final_investment else "💰 Investment"
    winner_cagr = "🏡 Property" if property_cagr > investment_cagr else "💰 Investment"

    break_text = f"Break-even occurs at Year {int(break_even.iloc[0]['Year'])}" if not break_even.empty else "No break-even within horizon."

    st.markdown(f"""
- 🏦 **Final Wealth Winner**: {winner_value}  
- 📈 **CAGR Winner**: {winner_cagr}  
- 🟡 **Break-even**: {break_text}
""")

# --------------------------
# Sensitivity Analysis Mention with Link
# --------------------------
st.subheader("🧩 Sensitivity Analysis Note")
st.info(
    """
    Detailed sensitivity analysis is available in the [**Modelling**](./Modelling) page.  

    It examines how variations in key parameters affect wealth accumulation:

    - Mortgage Rates
    - Property Appreciation
    - Rental Yield
    - Investment Returns
    """
)

# --------------------------
# 11. Download CSV
# --------------------------
csv = df.to_csv(index=False).encode('utf-8')
st.download_button("📥 Download Projection Data (CSV)", csv, "projection.csv", "text/csv", key='download-csv')
