import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib
import matplotlib.ticker as mticker
import plotly.graph_objects as go

# --------------------------
# 1. Global Settings
# --------------------------
st.set_page_config(page_title='Expected Outcomes – Fair Comparison', layout='wide')

# Times New Roman font for Streamlit
st.markdown(
    """
    <style>
    html, body, [class*="css"]  {
        font-family: 'Times New Roman', serif !important;
    }
    </style>
    """,
    unsafe_allow_html=True
)

# Times New Roman for matplotlib
matplotlib.rcParams['font.family'] = 'Times New Roman'

st.title("📌 Expected Outcomes – Buy Property vs Rent+EPF")

# --------------------------
# 2. Link Between EDA & Expected Outcomes
# --------------------------
st.subheader("🔗 Link to EDA Insights")

st.markdown(
    "The Expected Outcomes are directly shaped by insights from the **Exploratory Data Analysis (EDA)**, "
    "which provided the assumptions for property growth, EPF returns, and inflation trends."
)

with st.expander("📊 How EDA Informs Expected Outcomes"):
    st.markdown(
        """
        <ul>
            <li>🏠 <b>Property Price Growth:</b> Historical market appreciation rates were used as the assumption.</li>
            <li>💰 <b>EPF Returns:</b> Dividend trends informed the baseline and optimistic return scenarios.</li>
            <li>📈 <b>Inflation:</b> Past patterns guided the selection of realistic inflation ranges.</li>
        </ul>
        <p style="color: gray; font-size: 14px;">
        These EDA-driven assumptions serve as the foundation for comparing long-term 
        wealth accumulation between <b>buying property</b> and <b>saving in EPF</b>.
        </p>
        """,
        unsafe_allow_html=True
    )

# --------------------------
# 3. Baseline Assumptions Box
# --------------------------
st.subheader("📌 Baseline Assumptions")

st.markdown(
    """
    <style>
        table {border-collapse: collapse; width: 100%;}
        th {background-color: #4CAF50; color: white; padding: 8px; text-align: left; font-family: 'Times New Roman', serif;}
        td {border: 1px solid #ddd; padding: 8px; font-family: 'Times New Roman', serif;}
        tr:nth-child(even) {background-color: #f9f9f9;}
    </style>
    <table>
        <tr>
            <th>Parameter</th>
            <th>Baseline Value</th>
            <th>Justification / Source</th>
        </tr>
        <tr>
            <td>Initial Property Price</td>
            <td>RM 500,000</td>
            <td>Typical property price in target area</td>
        </tr>
        <tr>
            <td>Annual Property Growth Rate</td>
            <td>5%</td>
            <td>Based on historical market appreciation (past 10–20 years)</td>
        </tr>
        <tr>
            <td>Mortgage Rate</td>
            <td>4%</td>
            <td>Current average bank home loan rate</td>
        </tr>
        <tr>
            <td>Loan Term</td>
            <td>30 years</td>
            <td>Standard mortgage duration</td>
        </tr>
        <tr>
            <td>EPF Annual Growth Rate</td>
            <td>6%</td>
            <td>Historical EPF dividend trends</td>
        </tr>
        <tr>
            <td>Projection Years</td>
            <td>30</td>
            <td>Long-term wealth accumulation horizon</td>
        </tr>
    </table>
    """,
    unsafe_allow_html=True
)

# --------------------------
# 4. Helper Functions
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

def plot_outcomes(df, years):
    buy_final, epf_final = df["Buy Wealth (RM)"].iloc[-1], df["EPF Wealth (RM)"].iloc[-1]
    fig, ax = plt.subplots(figsize=(10,6))
    ax.plot(df["Year"], df["Buy Wealth (RM)"], label="Buy Property", color="blue", linewidth=2)
    ax.plot(df["Year"], df["EPF Wealth (RM)"], label="Rent+EPF", color="green", linewidth=2)
    ax.plot(df["Year"], df["Cumulative Rent (RM)"], label="Cumulative Rent", color="red", linestyle="--", linewidth=2)
    ax.set_xlabel("Year")
    ax.set_ylabel("Wealth / Rent (RM)")
    ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f"RM {x:,.0f}"))
    ax.legend()
    ax.grid(True, linestyle="--", alpha=0.6)
    return fig

def format_table(df):
    df_fmt = df.copy()
    for col in ["Property (RM)", "Mortgage (RM)", "Buy Wealth (RM)", "EPF Wealth (RM)", "Annual Rent (RM)", "Cumulative Rent (RM)"]:
        df_fmt[col] = df_fmt[col].apply(lambda x: f"RM {x:,.0f}")

    # Identify winner
    buy_final, epf_final = df["Buy Wealth (RM)"].iloc[-1], df["EPF Wealth (RM)"].iloc[-1]
    winner_col = "Buy Wealth (RM)" if buy_final > epf_final else "EPF Wealth (RM)"

    def highlight_winner(row):
        if row.name == df.index[-1]:
            return ['background-color: lightgreen' if col == winner_col else '' for col in df_fmt.columns]
        return ['' for _ in df_fmt.columns]

    styled_df = df_fmt.style.apply(highlight_winner, axis=1).set_properties(**{'font-family':'Times New Roman','font-size':'14px'})
    return styled_df

def calculate_cagr(initial, final, years):
    return (final / initial) ** (1 / years) - 1 if initial > 0 and years > 0 else 0

def generate_summary(df, years):
    buy_final = df["Buy Wealth (RM)"].iloc[-1]
    epf_final = df["EPF Wealth (RM)"].iloc[-1]
    rent_final = df["Cumulative Rent (RM)"].iloc[-1]
    buy_initial = next((x for x in df["Buy Wealth (RM)"] if x > 0), 1)
    epf_initial = next((x for x in df["EPF Wealth (RM)"] if x > 0), 1)
    buy_cagr = calculate_cagr(buy_initial, buy_final, years)
    epf_cagr = calculate_cagr(epf_initial, epf_final, years)
    winner = "Buy Property" if buy_final > epf_final else "Rent+EPF"
    ratio = buy_final / epf_final if epf_final > 0 else float('inf')
    break_even_year = next((year for year, buy, epf in zip(df["Year"], df["Buy Wealth (RM)"], df["EPF Wealth (RM)"]) if buy > epf), None)

    summary = f"""
    ### 📊 Expected Outcomes after {years} Years  
    - **Buy Property Wealth**: RM {buy_final:,.0f}  (CAGR: {buy_cagr*100:.2f}%)  
    - **Rent+EPF Wealth**: RM {epf_final:,.0f}  (CAGR: {epf_cagr*100:.2f}%)  
    - **Cumulative Rent Paid**: RM {rent_final:,.0f}  
    - **Wealth Ratio (Buy ÷ Rent+EPF)**: {ratio:.2f}x  
    """
    if break_even_year:
        summary += f"- **Break-even Year**: Year {break_even_year}\n"
    summary += f"\n🏆 **Winner: {winner}**"
    return summary

# --------------------------
# 2b. Plotly Animated Chart
# --------------------------
def plot_outcomes_animated(df):
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=df["Year"], y=df["Buy Wealth (RM)"], mode='lines+markers', name='Buy Property', line=dict(color='blue')))
    fig.add_trace(go.Scatter(x=df["Year"], y=df["EPF Wealth (RM)"], mode='lines+markers', name='Rent+EPF', line=dict(color='green')))
    fig.add_trace(go.Scatter(x=df["Year"], y=df["Cumulative Rent (RM)"], mode='lines+markers', name='Cumulative Rent', line=dict(color='red', dash='dash')))
    fig.update_layout(title="📈 Wealth Comparison Over Time", xaxis_title="Year", yaxis_title="RM", template="plotly_white")
    return fig

# --------------------------
# 5. Sidebar Inputs
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
# 6. Projection
# --------------------------
df = project_outcomes(initial_property_price, mortgage_rate, loan_term_years, property_growth, epf_rate, rent_yield, projection_years, custom_rent)

# --------------------------
# 7. Tabs
# --------------------------
tab1, tab2, tab3 = st.tabs(["📈 Chart","📊 Table","📝 Summary"])

with tab1:
    st.pyplot(plot_outcomes(df, projection_years))
    st.plotly_chart(plot_outcomes_animated(df), use_container_width=True)

with tab2:
    st.dataframe(format_table(df), use_container_width=True)

with tab3:
    break_even_year = next((year for year, buy, epf in zip(df["Year"], df["Buy Wealth (RM)"], df["EPF Wealth (RM)"]) if buy > epf), None)
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Buy Property Wealth", f"RM {df['Buy Wealth (RM)'].iloc[-1]:,.0f}")
    col2.metric("Rent+EPF Wealth", f"RM {df['EPF Wealth (RM)'].iloc[-1]:,.0f}")
    col3.metric("Cumulative Rent Paid", f"RM {df['Cumulative Rent (RM)'].iloc[-1]:,.0f}")
    col4.metric("Break-even Year", f"Year {break_even_year}" if break_even_year else "N/A")
    st.markdown(generate_summary(df, projection_years), unsafe_allow_html=True)

# --------------------------
# 8. Download CSV
# --------------------------
csv = df.to_csv(index=False).encode('utf-8')
st.download_button("📥 Download Projection Data (CSV)", csv, "projection.csv", "text/csv", key='download-csv')
