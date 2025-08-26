import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

st.set_page_config(page_title='Scenario Analysis', layout='wide')
st.title('🔄 Scenario Analysis')

# ---- Page Content ----
with st.expander("ℹ️ Description", expanded=False):
    st.write("""
    This scenario analysis extends the historical insights from the EDA (2010–2025) 
    into a forward-looking projection (2025–2045). The growth rates chosen are 
    informed by historical patterns:
    - Baseline (5%): consistent with Malaysia’s long-run EPF average.
    - Optimistic (8%): reflects strong market years where EPF exceeded 7%.
    - Pessimistic (3%): aligned with slower property price growth observed recently.
    
    This highlights how even small differences in annual growth, when compounded, 
    create wide divergences in long-term wealth outcomes.
    """)

# --- Define Scenarios ---
years = np.arange(2025, 2046)
baseline = np.cumprod([1.05]*len(years)) * 100
optimistic = np.cumprod([1.08]*len(years)) * 100
pessimistic = np.cumprod([1.03]*len(years)) * 100

df_scen = pd.DataFrame({
    "Year": years.astype(int),
    "Baseline (5%)": baseline,
    "Optimistic (8%)": optimistic,
    "Pessimistic (3%)": pessimistic
})

# --- Chart ---
fig, ax = plt.subplots()
ax.plot(df_scen["Year"], df_scen["Baseline (5%)"], label="Baseline (5%)", color="blue")
ax.plot(df_scen["Year"], df_scen["Optimistic (8%)"], label="Optimistic (8%)", color="green")
ax.plot(df_scen["Year"], df_scen["Pessimistic (3%)"], label="Pessimistic (3%)", color="red")
ax.set_xlabel("Year")
ax.set_ylabel("Wealth Index (Relative Growth, base=100 in 2025)")
ax.set_title("Scenario Comparison (2025–2045)")
ax.legend()

# Force integer ticks on x-axis
ax.xaxis.set_major_locator(plt.MaxNLocator(integer=True))
ax.yaxis.set_major_formatter('{:.0f}'.format)

st.pyplot(fig)

# --- Download CSV ---
csv = df_scen.to_csv(index=False).encode("utf-8")
st.download_button(
    "⬇️ Download Scenario Results (CSV)",
    data=csv,
    file_name="scenario_analysis.csv",
    mime="text/csv"
)
