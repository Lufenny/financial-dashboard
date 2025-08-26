import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

st.set_page_config(page_title='Results & Interpretation', layout='wide')
st.title("📑 Results & Interpretation (Dynamic)")

# --- Load sensitivity results from Modelling ---
# In production, you can pass df_sens directly via session_state
try:
    df_sens = st.session_state["df_sens"]
except KeyError:
    st.error("❌ Sensitivity results not found. Run Modelling page first.")
    st.stop()

# --- Select scenario to visualize ---
st.sidebar.header("Select Scenario")
contrib_options = sorted(df_sens["Contribution"].unique())
return_options = sorted(df_sens["Return"].unique())

selected_contrib = st.sidebar.selectbox("Monthly Contribution (RM)", contrib_options)
selected_return = st.sidebar.selectbox("Annual Return (%)", return_options)

df_scenario = df_sens[
    (df_sens["Contribution"] == selected_contrib) &
    (df_sens["Return"] == selected_return)
].copy()

if df_scenario.empty:
    st.warning("No data found for this scenario.")
    st.stop()

# --- Prepare Data ---
df_scenario["Buy (RM)"] = df_scenario["TotalContribution"]
df_scenario["Rent & Invest (RM)"] = df_scenario["TotalValue"]

# --- Dynamic Crossover Year ---
crossover = df_scenario[df_scenario["Rent & Invest (RM)"] > df_scenario["Buy (RM)"]]
crossover_year = crossover["Year"].iloc[0] if not crossover.empty else None

# --- Show Data ---
with st.expander("🔎 View Scenario Dataframe"):
    st.dataframe(df_scenario[["Year", "Buy (RM)", "Rent & Invest (RM)"]], use_container_width=True)

# --- Plot ---
fig, ax = plt.subplots(figsize=(10, 5))
ax.plot(df_scenario["Year"], df_scenario["Buy (RM)"], marker="o", label="Buy", color="blue")
ax.plot(df_scenario["Year"], df_scenario["Rent & Invest (RM)"], marker="s", label="Rent & Invest", color="green")
ax.set_title(f"Wealth Comparison (RM{selected_contrib}/m @ {selected_return}%)")
ax.set_xlabel("Year")
ax.set_ylabel("Value (RM)")
ax.grid(True, linestyle='--', alpha=0.5)
ax.legend()
st.pyplot(fig)

# --- Interpretation ---
st.header("📝 Interpretation")
st.write(f"""
- **Rent & Invest** consistently outperforms **Buy** under the selected scenario.  
- Wealth divergence increases over time due to compounding returns.  
- Rent & Invest overtakes Buy around **{crossover_year}**.  
- The **Buy** scenario offers tangible property ownership and housing security.
""")

# --- Download ---
csv_bytes = df_scenario[["Year", "Buy (RM)", "Rent & Invest (RM)"]].to_csv(index=False).encode("utf-8")
st.download_button(
    "⬇️ Download Results CSV",
    data=csv_bytes,
    file_name=f"results_interpretation_RM{selected_contrib}_{selected_return}.csv",
    mime="text/csv"
)
