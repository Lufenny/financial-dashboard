import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib import rcParams

# --------------------------
# Page Config
# --------------------------
st.set_page_config(page_title="Expected Outcomes – Baseline", layout="wide")
st.title("📊 Expected Outcomes – Buy vs EPF Wealth")

# --------------------------
# Font Setup (Times New Roman)
# --------------------------
rcParams['font.family'] = 'Times New Roman'

# --------------------------
# Sidebar Inputs
# --------------------------
st.sidebar.header("⚙️ Baseline Assumptions")
initial_property_price = st.sidebar.number_input("Initial Property Price (RM)", value=300000, step=10000)
annual_property_growth = st.sidebar.number_input("Annual Property Growth (%)", value=3.0, step=0.1) / 100
epf_interest_rate = st.sidebar.number_input("EPF Annual Dividend (%)", value=5.0, step=0.1) / 100
years = st.sidebar.number_input("Investment Horizon (Years)", value=30, step=1)

# --------------------------
# Wealth Calculations
# --------------------------
buy_wealth = [initial_property_price * ((1 + annual_property_growth) ** i) for i in range(years + 1)]
epf_wealth = [initial_property_price * ((1 + epf_interest_rate) ** i) for i in range(years + 1)]
year_range = list(range(years + 1))

df = pd.DataFrame({
    "Year": year_range,
    "Buy Wealth (Property Equity)": buy_wealth,
    "EPF Wealth": epf_wealth
})

# Format values to RM without decimals
df["Buy Wealth (Property Equity)"] = df["Buy Wealth (Property Equity)"].apply(lambda x: f"RM {int(x):,}")
df["EPF Wealth"] = df["EPF Wealth"].apply(lambda x: f"RM {int(x):,}")

# --------------------------
# Show Table
# --------------------------
st.subheader("📑 Wealth Projection Table")
st.dataframe(df, use_container_width=True)

# --------------------------
# Plot Graph
# --------------------------
fig, ax = plt.subplots(figsize=(10, 6))

# Plot lines
ax.plot(year_range, [initial_property_price * ((1 + annual_property_growth) ** i) for i in year_range],
        label="Buy Wealth (Property Equity)", color="blue", linewidth=2)
ax.plot(year_range, [initial_property_price * ((1 + epf_interest_rate) ** i) for i in year_range],
        label="EPF Wealth", color="green", linewidth=2)

# Labels and Title
ax.set_title("Buy vs EPF Wealth Projection", fontsize=16, fontweight="bold")
ax.set_xlabel("Year", fontsize=14)
ax.set_ylabel("Wealth (RM)", fontsize=14)

# Format Y-axis with RM and no decimals
ax.get_yaxis().set_major_formatter(plt.FuncFormatter(lambda x, _: f"RM {int(x):,}"))

# Legend (no square box, only lines)
ax.legend(frameon=False, fontsize=12, prop={"family": "Times New Roman"})

# Grid
ax.grid(True, linestyle="--", alpha=0.6)

st.pyplot(fig)
