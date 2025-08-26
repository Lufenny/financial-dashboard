import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from itertools import cycle

st.set_page_config(page_title='Modelling', layout='wide')
st.title('📊 Modelling')

# ---------------------------------------------
# Sensitivity Analysis - Interactive Controls
# ---------------------------------------------

st.markdown("### 📈 Sensitivity Analysis")
with st.expander("ℹ️ Description", expanded=False):
    st.write("""
    Explore how changes in monthly contributions, annual returns, and investment horizon
    affect your portfolio value over time.

    Use the sidebar to adjust parameters.  
    Toggle between **Scenario Comparison** and **Contribution vs. Growth Breakdown**.  
    You can also choose to see results **inflation-adjusted**.
    """)

# --- Sidebar User Inputs ---
st.sidebar.header("Adjust Parameters")

monthly_contribs = st.sidebar.multiselect(
    "Monthly Contribution (RM)",
    options=[100, 200, 400, 600, 800, 1000],
    default=[200, 400, 600]
)

annual_returns = st.sidebar.multiselect(
    "Annual Return Rate (%)",
    options=[3, 5, 7, 9, 11],
    default=[5, 7, 9]
)

start_year = st.sidebar.number_input("Start Year", min_value=2020, max_value=2030, value=2025, step=1)
end_year = st.sidebar.number_input("End Year", min_value=start_year+5, max_value=2050, value=2045, step=1)

# Inflation settings
st.sidebar.subheader("Inflation Adjustment")
adjust_inflation = st.sidebar.checkbox("Show Inflation-Adjusted Values", value=False)
inflation_rate = st.sidebar.slider("Annual Inflation Rate (%)", 0.0, 10.0, 2.0, step=0.5)

years = np.arange(start_year, end_year + 1)
n_months = len(years) * 12

# --- Sensitivity Calculation ---
results = []
for c in monthly_contribs:
    for r in annual_returns:
        r_decimal = r / 100
        monthly_rate = r_decimal / 12
        fv, contrib_only = [], []
        total_contrib = 0

        for i in range(1, n_months + 1):
            total_contrib += c
            contrib_only.append(total_contrib)
            fv.append(c * ((1 + monthly_rate)**i))

        yearly_values = [sum(fv[i*12:(i+1)*12]) for i in range(len(years))]
        yearly_contribs = [contrib_only[(i+1)*12 - 1] for i in range(len(years))]

        df = pd.DataFrame({
            "Year": years,
            "Contribution": c,
            "Return": r,
            "TotalValue": np.cumsum(yearly_values),
            "TotalContribution": yearly_contribs
        })

        # Inflation adjustment (convert to "real" value)
        if adjust_inflation:
            df["InflationFactor"] = [(1 + inflation_rate/100)**(y - start_year) for y in years]
            df["TotalValue"] = df["TotalValue"] / df["InflationFactor"]
            df["TotalContribution"] = df["TotalContribution"] / df["InflationFactor"]

        results.append(df)

df_sens = pd.concat(results)
df_sens.sort_values(["Contribution", "Return"], inplace=True)
df_sens["Growth"] = df_sens["TotalValue"] - df_sens["TotalContribution"]

# --- Tabs ---
tab1, tab2 = st.tabs(["📊 Scenario Comparison", "🧩 Contribution vs. Growth Breakdown"])

# --- Tab 1: Scenario Comparison ---
with tab1:
    fig1 = go.Figure()
    colors = cycle(['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', '#9467bd', '#8c564b'])
    line_styles = cycle(['solid', 'dash', 'dot', 'dashdot'])

    contrib_colors = {c: color for c, color in zip(sorted(monthly_contribs), colors)}

    for c in sorted(monthly_contribs):
        for r, ls in zip(sorted(annual_returns), line_styles):
            group = df_sens[(df_sens['Contribution']==c) & (df_sens['Return']==r)]
            fig1.add_trace(go.Scatter(
                x=group['Year'],
                y=group['TotalValue'],
                mode='lines+markers',
                name=f"RM{c}/m @ {r}%",
                line=dict(color=contrib_colors[c], dash=ls),
                hovertemplate='Year: %{x}<br>Total Value: RM%{y:,.0f}<extra></extra>'
            ))

    fig1.update_layout(
        title="Portfolio Value Sensitivity (Scenario Comparison)" + 
              (" – Inflation Adjusted" if adjust_inflation else " – Nominal"),
        xaxis_title="Year",
        yaxis_title="Portfolio Value (RM)",
        legend_title="Scenario",
        hovermode="x unified",
        template="plotly_white"
    )
    st.plotly_chart(fig1, use_container_width=True)

# --- Tab 2: Contribution vs. Growth Breakdown ---
with tab2:
    contrib_choice = st.selectbox("Select Contribution Level (RM)", sorted(monthly_contribs))
    return_choice = st.selectbox("Select Return Rate (%)", sorted(annual_returns))

    group = df_sens[(df_sens['Contribution']==contrib_choice) & (df_sens['Return']==return_choice)]

    fig2 = go.Figure()
    fig2.add_trace(go.Bar(
        x=group["Year"],
        y=group["TotalContribution"],
        name="Total Contribution",
        marker_color="#1f77b4",
        hovertemplate="Year: %{x}<br>Contribution: RM%{y:,.0f}<extra></extra>"
    ))
    fig2.add_trace(go.Bar(
        x=group["Year"],
        y=group["Growth"],
        name="Growth (Returns)",
        marker_color="#ff7f0e",
        hovertemplate="Year: %{x}<br>Growth: RM%{y:,.0f}<extra></extra>"
    ))

    fig2.update_layout(
        barmode="stack",
        title=f"Contribution vs. Growth Breakdown (RM{contrib_choice}/m @ {return_choice}%)" + 
              (" – Inflation Adjusted" if adjust_inflation else " – Nominal"),
        xaxis_title="Year",
        yaxis_title="Portfolio Value (RM)",
        hovermode="x unified",
        template="plotly_white"
    )
    st.plotly_chart(fig2, use_container_width=True)

# --- Download ---
csv = df_sens.to_csv(index=False).encode("utf-8")
st.download_button(
    "⬇️ Download Sensitivity Results (CSV)",
    data=csv,
    file_name="sensitivity_analysis.csv",
    mime="text/csv"
)
