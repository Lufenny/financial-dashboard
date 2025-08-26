import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from itertools import cycle

st.set_page_config(page_title='Results & Interpretation', layout='wide')
st.title("📑 Results & Interpretation (Multi-Scenario)")

# --- Upload sensitivity CSV ---
st.sidebar.header("Upload Sensitivity Results")
uploaded_file = st.sidebar.file_uploader(
    "Upload 'sensitivity_analysis.csv' from Modelling page",
    type=["csv"]
)

if uploaded_file is not None:
    df_sens = pd.read_csv(uploaded_file)
else:
    st.warning("Please upload 'sensitivity_analysis.csv' from the Modelling page to proceed.")
    st.stop()

# --- Multi-Scenario Selection ---
st.sidebar.header("Select Scenarios to Compare")
contrib_options = sorted(df_sens["Contribution"].unique())
return_options = sorted(df_sens["Return"].unique())

selected_contribs = st.sidebar.multiselect(
    "Monthly Contribution (RM)", contrib_options, default=[contrib_options[0]]
)
selected_returns = st.sidebar.multiselect(
    "Annual Return (%)", return_options, default=[return_options[0]]
)

if not selected_contribs or not selected_returns:
    st.warning("Please select at least one contribution and one return rate.")
    st.stop()

# --- Filter Data ---
df_plot = df_sens[
    df_sens["Contribution"].isin(selected_contribs) &
    df_sens["Return"].isin(selected_returns)
].copy()

# --- Wealth definitions ---
# Rent & Invest wealth
df_plot["Rent & Invest (RM)"] = df_plot["TotalValue"]

# Buy wealth: use provided column if available, otherwise approximate with contributions + growth
if "TotalBuyWealth" in df_plot.columns:
    df_plot["Buy (RM)"] = df_plot["TotalBuyWealth"]
else:
    df_plot["Buy (RM)"] = df_plot["TotalContribution"] + df_plot["Growth"]

# --- Plot Multi-Scenario Curves ---
fig, ax = plt.subplots(figsize=(12, 6))
colors = cycle(["blue", "green", "orange", "red", "purple", "brown"])
line_styles = cycle(["solid", "dashed", "dotted", "dashdot"])

for c in selected_contribs:
    for r in selected_returns:
        scenario = df_plot[(df_plot["Contribution"] == c) & (df_plot["Return"] == r)]
        if scenario.empty:
            continue
        color = next(colors)
        ls = next(line_styles)
        ax.plot(
            scenario["Year"], 
            scenario["Rent & Invest (RM)"], 
            label=f"RM{c}/m @ {r}%", 
            color=color, 
            linestyle=ls, 
            marker="o"
        )
        # Plot Buy as dotted reference line
        ax.plot(
            scenario["Year"], 
            scenario["Buy (RM)"], 
            color=color, 
            linestyle="dotted",
            alpha=0.5
        )

ax.set_title("Multi-Scenario Wealth Comparison (Solid: Rent & Invest, Dotted: Buy)")
ax.set_xlabel("Year")
ax.set_ylabel("Value (RM)")
ax.grid(True, linestyle='--', alpha=0.5)
ax.legend()
st.pyplot(fig)

# --- Interpretation ---
st.header("📝 Interpretation")
st.write("""
- **Solid lines** = Rent & Invest strategy, **dotted lines** = Buy strategy.  
- **Crossing points** indicate the tipping year when investing surpasses owning (or vice versa).  
- Higher **monthly contributions** and **investment returns** accelerate Rent & Invest wealth.  
- Lower mortgage costs and stronger property appreciation improve Buy outcomes.  
- In the **short term (<10 years)**, renting often looks cheaper due to flexibility and lower upfront costs.  
- Over **long horizons (15–30 years)**, compounding from both property appreciation and investments become decisive.  

**Practical Implications**  
- 🏠 **Households**: Buying is stronger under low mortgage rates and steady appreciation. Renting can win when investment returns are high and rent remains affordable.  
- 💼 **Financial Advisors**: Scenario comparisons help clients see how small changes in rates or returns shift long-term outcomes.  
- 🏛️ **Policymakers**: Sensitivity results highlight how changes in interest rates, subsidies, or rental market conditions affect household wealth.  
""")

# --- Download Multi-Scenario Data ---
csv_bytes = df_plot[["Year", "Contribution", "Return", "Buy (RM)", "Rent & Invest (RM)"]].to_csv(index=False).encode("utf-8")
st.download_button(
    "⬇️ Download Multi-Scenario Results CSV",
    data=csv_bytes,
    file_name="results_interpretation_multiscenario.csv",
    mime="text/csv"
)
