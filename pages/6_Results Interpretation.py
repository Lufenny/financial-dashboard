import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from itertools import cycle

st.set_page_config(page_title='Results & Interpretation', layout='wide')
st.title("📑 Results & Interpretation (Multi-Scenario)")

# --- Upload sensitivity CSV ---
st.sidebar.header("Upload Sensitivity Results")
uploaded_file = st.sidebar.file_uploader(
    "Upload 'buy_vs_rent_sensitivity.csv' from Modelling page",
    type=["csv"]
)

if uploaded_file is not None:
    df_sens = pd.read_csv(uploaded_file)
else:
    st.warning("Please upload 'buy_vs_rent_sensitivity.csv' from the Modelling page to proceed.")
    st.stop()

# --- Multi-Scenario Selection ---
st.sidebar.header("Select Scenarios to Compare")

mortgage_options = sorted(df_sens["MortgageRate"].unique())
return_options = sorted(df_sens["InvestReturn"].unique())
appreciation_options = sorted(df_sens["Appreciation"].unique())
rent_yield_options = sorted(df_sens["RentYield"].unique())

selected_mortgages = st.sidebar.multiselect(
    "Mortgage Rate (%)", mortgage_options, default=[mortgage_options[0]]
)
selected_returns = st.sidebar.multiselect(
    "Investment Return (%)", return_options, default=[return_options[0]]
)
selected_app = st.sidebar.selectbox("Property Appreciation (%)", appreciation_options)
selected_ry = st.sidebar.selectbox("Rental Yield (%)", rent_yield_options)

if not selected_mortgages or not selected_returns:
    st.warning("Please select at least one mortgage rate and one return rate.")
    st.stop()

# --- Filter Data ---
df_plot = df_sens[
    (df_sens["MortgageRate"].isin(selected_mortgages)) &
    (df_sens["InvestReturn"].isin(selected_returns)) &
    (df_sens["Appreciation"] == selected_app) &
    (df_sens["RentYield"] == selected_ry)
].copy()

# --- Plot Multi-Scenario Curves ---
fig, ax = plt.subplots(figsize=(12, 6))
colors = cycle(["blue", "green", "orange", "red", "purple", "brown"])
line_styles = cycle(["solid", "dashed", "dotted", "dashdot"])

crossings_summary = []

for mr in selected_mortgages:
    for r in selected_returns:
        scenario = df_plot[(df_plot["MortgageRate"] == mr) & (df_plot["InvestReturn"] == r)]
        if scenario.empty:
            continue
        color = next(colors)
        ls = next(line_styles)

        # Plot Rent line
        ax.plot(
            scenario["Year"],
            scenario["RentPortfolio"],
            label=f"Rent @ {r}% | Mort {mr}%",
            color=color,
            linestyle=ls,
            marker="o"
        )
        # Plot Buy line
        ax.plot(
            scenario["Year"],
            scenario["BuyEquity"],
            color=color,
            linestyle="dotted",
            alpha=0.6
        )

        # --- Detect crossing point ---
        diff = scenario["RentPortfolio"].values - scenario["BuyEquity"].values
        cross_idx = None
        for i in range(1, len(diff)):
            if diff[i-1] * diff[i] < 0:  # sign change
                cross_idx = i
                break

        if cross_idx is not None:
            year_cross = scenario["Year"].iloc[cross_idx]
            rent_val = scenario["RentPortfolio"].iloc[cross_idx]
            buy_val = scenario["BuyEquity"].iloc[cross_idx]
            ax.scatter(year_cross, rent_val, color=color, s=80, edgecolor="black", zorder=5)
            ax.annotate(
                f"Cross @ {year_cross}",
                (year_cross, rent_val),
                textcoords="offset points",
                xytext=(0,10),
                ha="center",
                fontsize=8,
                color=color
            )
            crossings_summary.append(f"- Rent @ {r}% | Mort {mr}% → Tipping year ≈ {year_cross}")

ax.set_title("Multi-Scenario Wealth Comparison (Solid: Rent & Invest, Dotted: Buy)")
ax.set_xlabel("Year")
ax.set_ylabel("Value (RM)")
ax.grid(True, linestyle='--', alpha=0.5)
ax.legend()
st.pyplot(fig)

# --- Interpretation ---
st.header("📝 Interpretation")
st.write(f"""
- **Solid lines** = Rent & Invest strategy, **dotted lines** = Buy strategy.  
- **Crossing points** (marked on chart) indicate the tipping year when investing surpasses owning (or vice versa).  
- Higher **investment returns ({selected_returns})** accelerate Rent & Invest wealth.  
- Lower **mortgage rates ({selected_mortgages})** and steady **property appreciation ({selected_app}%)** strengthen Buy outcomes.  
- With **rental yields fixed at {selected_ry}%**, renting looks cheaper in the short term, but buying gains ground if appreciation persists.  
""")

if crossings_summary:
    st.subheader("🔎 Detected Tipping Years")
    for line in crossings_summary:
        st.write(line)
else:
    st.info("No crossing points detected in the selected scenarios (one strategy dominates throughout the horizon).")

# --- Download Multi-Scenario Data ---
csv_bytes = df_plot[["Year", "MortgageRate", "InvestReturn", "Appreciation", "RentYield", "BuyEquity", "RentPortfolio", "Difference"]].to_csv(index=False).encode("utf-8")
st.download_button(
    "⬇️ Download Multi-Scenario Results CSV",
    data=csv_bytes,
    file_name="results_interpretation_multiscenario.csv",
    mime="text/csv"
)
