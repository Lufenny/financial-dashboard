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
    affect your portfolio value over time. Hover over lines to see exact values.
    """)

# --- User Inputs ---
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

years = np.arange(start_year, end_year + 1)
n_months = len(years) * 12

# --- Sensitivity Calculation ---
results = []
for c in monthly_contribs:
    for r in annual_returns:
        r_decimal = r / 100
        monthly_rate = r_decimal / 12
        fv = []
        for i in range(1, n_months + 1):
            fv.append(c * ((1 + monthly_rate)**i))
        yearly_values = [sum(fv[i*12:(i+1)*12]) for i in range(len(years))]
        results.append(pd.DataFrame({
            "Year": years,
            "Contribution": c,
            "Return": r,
            "Value": np.cumsum(yearly_values)
        }))

df_sens = pd.concat(results)
df_sens.sort_values(["Contribution", "Return"], inplace=True)

# --- Plotly Interactive Plot ---
fig = go.Figure()

colors = cycle(['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', '#9467bd', '#8c564b'])
line_styles = cycle(['solid', 'dash', 'dot', 'dashdot'])

contrib_colors = {c: color for c, color in zip(sorted(monthly_contribs), colors)}

for c in sorted(monthly_contribs):
    for r, ls in zip(sorted(annual_returns), line_styles):
        group = df_sens[(df_sens['Contribution']==c) & (df_sens['Return']==r)]
        fig.add_trace(go.Scatter(
            x=group['Year'],
            y=group['Value'],
            mode='lines+markers',
            name=f"RM{c}/m @ {r}%",
            line=dict(color=contrib_colors[c], dash=ls),
            hovertemplate='Year: %{x}<br>Value: RM%{y:,.0f}<extra></extra>'
        ))

fig.update_layout(
    title="Portfolio Value Sensitivity",
    xaxis_title="Year",
    yaxis_title="Portfolio Value (RM)",
    legend_title="Scenario",
    hovermode="x unified",
    template="plotly_white"
)

st.plotly_chart(fig, use_container_width=True)

# --- Download ---
csv = df_sens.to_csv(index=False).encode("utf-8")
st.download_button(
    "⬇️ Download Sensitivity Results (CSV)",
    data=csv,
    file_name="sensitivity_analysis.csv",
    mime="text/csv"
)
