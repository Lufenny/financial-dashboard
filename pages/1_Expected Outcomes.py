import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from matplotlib import rcParams

# --------------------------
# Global Font Setting
# --------------------------
plt.rcParams["font.family"] = "Times New Roman"

st.set_page_config(page_title="Expected Outcomes – Buy vs EPF", layout="wide")
st.title("📌 Expected Outcomes – Buy vs EPF Wealth")

# --------------------------
# Baseline Assumptions (Sidebar)
# --------------------------
st.sidebar.header("⚙️ Baseline Assumptions")

initial_property_price = st.sidebar.number_input("Initial Property Price (RM)", value=300000, step=10000)
property_growth_rate = st.sidebar.slider("Annual Property Growth Rate (%)", 0.0, 10.0, 5.0) / 100
mortgage_rate = st.sidebar.slider("Mortgage Interest Rate (%)", 0.0, 10.0, 4.0) / 100
loan_term_years = st.sidebar.number_input("Loan Term (Years)", value=20, step=1)
epf_rate = st.sidebar.slider("Annual EPF Dividend Rate (%)", 0.0, 10.0, 5.0) / 100
annual_epf_contribution = st.sidebar.number_input("Annual EPF Contribution (RM)", value=12000, step=1000)
years = st.sidebar.number_input("Projection Horizon (Years)", value=20, step=1)

# --------------------------
# Mortgage Calculation
# --------------------------
P = initial_property_price
r = mortgage_rate
n = loan_term_years
if r > 0:
    PMT = P * (r * (1 + r)**n) / ((1 + r)**n - 1)
else:
    PMT = P / n  # zero interest case

# --------------------------
# Projection Loop
# --------------------------
property_values = [P]
mortgage_balances = [P]
buy_wealth = [0]
epf_wealth = [0]

for t in range(1, years + 1):
    new_property_value = property_values[-1] * (1 + property_growth_rate)
    property_values.append(new_property_value)

    interest_payment = mortgage_balances[-1] * r
    principal_payment = PMT - interest_payment
    new_mortgage_balance = max(0, mortgage_balances[-1] - principal_payment)
    mortgage_balances.append(new_mortgage_balance)

    new_buy_wealth = new_property_value - new_mortgage_balance
    buy_wealth.append(new_buy_wealth)

    new_epf_wealth = epf_wealth[-1] * (1 + epf_rate) + annual_epf_contribution
    epf_wealth.append(new_epf_wealth)

# --------------------------
# DataFrame Results
# --------------------------
df = pd.DataFrame({
    "Year": np.arange(0, years + 1),
    "Property Value (RM)": property_values,
    "Mortgage Balance (RM)": mortgage_balances,
    "Buy Wealth (RM)": buy_wealth,
    "EPF Wealth (RM)": epf_wealth
})

df_fmt = df.copy()
for col in ["Property Value (RM)", "Mortgage Balance (RM)", "Buy Wealth (RM)", "EPF Wealth (RM)"]:
    df_fmt[col] = df_fmt[col].apply(lambda x: f"RM {x:,.0f}")

# --------------------------
# CAGR Calculation
# --------------------------
buy_cagr = (buy_wealth[-1] / buy_wealth[0])**(1/years) - 1 if buy_wealth[0] > 0 else (buy_wealth[-1] / 1e3)**(1/years) - 1
epf_cagr = (epf_wealth[-1] / epf_wealth[0])**(1/years) - 1 if epf_wealth[0] > 0 else (epf_wealth[-1] / 1e3)**(1/years) - 1

# --------------------------
# Plot
# --------------------------
fig, ax = plt.subplots(figsize=(10, 6))

line1, = ax.plot(df["Year"], df["Buy Wealth (RM)"], label="🏡 Buy Wealth (Property Equity)", linewidth=2, color="blue")
line2, = ax.plot(df["Year"], df["EPF Wealth (RM)"], label="💰 EPF Wealth", linewidth=2, color="green")

ax.set_xlabel("Year", fontsize=12)
ax.set_ylabel("Wealth (RM)", fontsize=12)
ax.set_title("Buy vs EPF Wealth Projection", fontsize=14, fontweight="bold")

# Legend without square boxes (use lines instead)
ax.legend(handles=[line1, line2], loc="upper left", frameon=False, fontsize=11)

# Grid formatting
ax.grid(True, linestyle="--", alpha=0.6)

# Annotate CAGR + Final Values
if buy_cagr > epf_cagr:
    ax.text(years, buy_wealth[-1],
            f"RM {buy_wealth[-1]:,.0f}\n({buy_cagr*100:.2f}% p.a.)",
            fontsize=12, color="white", weight="bold",
            ha="left", va="bottom",
            bbox=dict(facecolor="blue", alpha=0.7, edgecolor="none"))
    ax.text(years, epf_wealth[-1],
            f"RM {epf_wealth[-1]:,.0f}\n({epf_cagr*100:.2f}% p.a.)",
            fontsize=10, color="green", ha="left", va="bottom")
    subtitle = "👉 In this scenario, **Buying Property outperforms EPF**."
else:
    ax.text(years, epf_wealth[-1],
            f"RM {epf_wealth[-1]:,.0f}\n({epf_cagr*100:.2f}% p.a.)",
            fontsize=12, color="white", weight="bold",
            ha="left", va="bottom",
            bbox=dict(facecolor="green", alpha=0.7, edgecolor="none"))
    ax.text(years, buy_wealth[-1],
            f"RM {buy_wealth[-1]:,.0f}\n({buy_cagr*100:.2f}% p.a.)",
            fontsize=10, color="blue", ha="left", va="bottom")
    subtitle = "👉 In this scenario, **EPF outperforms Buying Property**."

# Subtitle under chart
plt.figtext(0.5, -0.05, subtitle, wrap=True, ha="center", fontsize=12, fontweight="bold", fontname="Times New Roman")

# --------------------------
# Streamlit Outputs
# --------------------------
st.pyplot(fig)

st.subheader("📊 Projection Table")
st.markdown(
    """
    <style>
    table td, table th {
        font-family: 'Times New Roman', serif;
        font-size: 14px;
    }
    </style>
    """, unsafe_allow_html=True
)
st.dataframe(df_fmt, use_container_width=True)

# Download CSV
csv = df.to_csv(index=False).encode("utf-8")
st.download_button(
    "⬇️ Download Results (CSV)",
    data=csv,
    file_name="expected_outcomes_buy_vs_epf.csv",
    mime="text/csv"
)
