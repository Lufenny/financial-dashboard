import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker

st.set_page_config(page_title='Modelling', layout='wide')
st.title('📊 Modelling')

# ---------------------------------------------
# Modelling Content
# ---------------------------------------------
st.title("📊 Modelling")

st.markdown("### 📈 Sensitivity Analysis")
with st.expander("ℹ️ Description", expanded=False):
    st.write("""
    Sensitivity analysis investigates how variations in key parameters—such as 
    contribution rates, return assumptions, and inflation—affect long-term 
    investment outcomes.
    """)

# --- Example Data ---
contrib_rates = [200, 400, 600]
returns = [0.05, 0.07, 0.09]
years = np.arange(2025, 2046)

results = []
for c in contrib_rates:
    for r in returns:
        values = np.cumsum([c * ((1 + r)**i) for i in range(len(years))])
        results.append(pd.DataFrame({
            "Year": years,
            "Contribution": c,
            "Return": r,
            "Value": values
        }))

df_sens = pd.concat(results)

# Ensure Year is integer
df_sens["Year"] = df_sens["Year"].astype(int)

# --- Chart ---
fig, ax = plt.subplots(figsize=(12,6))

# Sort the groupings by Contribution first, then Return
for (c, r), group in df_sens.groupby(["Contribution", "Return"], sort=True):
    ax.plot(group["Year"], group["Value"], label=f"RM{c}/m @ {int(r*100)}%")

ax.set_title("Sensitivity of Contributions & Returns")
ax.set_xlabel("Year")
ax.set_ylabel("Portfolio Value (RM)")

# Sort legend entries by Contribution and Return
handles, labels = ax.get_legend_handles_labels()
sorted_handles_labels = sorted(zip(handles, labels), key=lambda x: (
    int(x[1].split('/m')[0][2:]),  # Contribution RM value
    int(x[1].split('@')[1].replace('%',''))  # Return %
))
handles, labels = zip(*sorted_handles_labels)
ax.legend(handles, labels)

# Automatically set x-axis interval based on number of years
years_range = df_sens["Year"].max() - df_sens["Year"].min()
if years_range <= 10:
    interval = 1
elif years_range <= 20:
    interval = 2
else:
    interval = 5

ax.xaxis.set_major_locator(mticker.MultipleLocator(interval))
ax.xaxis.set_major_formatter(plt.FuncFormatter(lambda x, _: f'{int(x)}'))

# Format y-axis as RM with commas
ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f'RM{int(x):,}'))

# Add grid for better readability
ax.grid(True, linestyle='--', alpha=0.5)

st.pyplot(fig)

# --- Download ---
csv = df_sens.to_csv(index=False).encode("utf-8")
st.download_button(
    "⬇️ Download Sensitivity Results (CSV)",
    data=csv,
    file_name="sensitivity_analysis.csv",
    mime="text/csv"
)
