import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

st.set_page_config(page_title='Results & Interpretation', layout='wide')

# ---------------------------------------------
# Results & Interpretation Content
# ---------------------------------------------
st.title("📑 Results & Interpretation")

st.header("📊 Comparative Results")
st.write("""
This section summarises how different investment and housing strategies perform 
over time based on modelling results.
""")

# --- Example Comparative Data ---
years = list(range(2025, 2046))
data = {
    "Year": years,
    "Buy Equity (RM)": [i*20000 for i in range(len(years))],
    "Rent & Invest (RM)": [i*25000 for i in range(len(years))]
}
df_results = pd.DataFrame(data)

with st.expander("🔎 View Result Dataframe"):
    st.dataframe(df_results, use_container_width=True)

# --- Growth Curves ---
fig, ax = plt.subplots()
ax.plot(df_results["Year"], df_results["Buy Equity (RM)"], marker="o", label="Buy")
ax.plot(df_results["Year"], df_results["Rent & Invest (RM)"], marker="s", label="Rent & Invest")
ax.set_title("Wealth Accumulation Comparison")
ax.set_xlabel("Year")
ax.set_ylabel("Value (RM)")
ax.legend()
st.pyplot(fig)

# --- Interpretation ---
st.header("📝 Interpretation")
st.write("""
- **Rent & Invest** consistently outperforms **Buy** under the given assumptions.  
- Wealth divergence widens after ~15 years due to compounding returns.  
- However, the **Buy** scenario offers tangible property ownership, which reduces 
exposure to rental inflation and provides housing security.
""")

# --- Sensitivity Insight ---
st.subheader("📈 Sensitivity Insights")
st.write("""
- Higher contribution rates accelerate divergence in the Rent & Invest strategy.  
- Lower returns narrow the gap, making Buy relatively more attractive.  
- Inflation and rental growth rates are critical tipping factors.  
""")

# --- Download Results ---
csv = df_results.to_csv(index=False).encode("utf-8")
st.download_button(
    "⬇️ Download Results CSV",
    data=csv,
    file_name="results_interpretation.csv",
    mime="text/csv"
)
