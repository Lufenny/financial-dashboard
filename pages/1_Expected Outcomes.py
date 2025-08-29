import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.ticker import FuncFormatter

# --------------------------
# Global Font Style
# --------------------------
plt.rcParams["font.family"] = "Times New Roman"  # Apply to matplotlib plots

st.set_page_config(page_title="Expected Outcomes – Buy vs EPF", layout="wide")

# Apply CSS styling for Times New Roman in Streamlit text & tables
st.markdown(
    """
    <style>
    * {
        font-family: 'Times New Roman', serif !important;
    }
    </style>
    """,
    unsafe_allow_html=True
)

# --------------------------
# Page Title & Intro
# --------------------------
st.title("📌 Expected Outcomes – Buy vs EPF Wealth")

st.write(
    "This section compares the long-term outcomes of **buying a house** versus saving in "
    "**EPF (Employees Provident Fund)**. The projection shows how your property equity "
    "(Buy Wealth) and EPF savings could grow over time based on the assumptions you set."
)

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
    PMT = P * (r * (1 + r)**n) / ((1 + r)**n - 1)  # standard annuity formula
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
    # Property growth
    new_property_value = property_values[-1] * (1 + property_growth_rate)
    property_values.append(new_property_value)

    # Mortgage balance update
    interest_payment = mortgage_balances[-1] * r
    principal_payment = PMT - interest_payment
    new_mortgage_balance = max(0, mortgage_balances[-1] - principal_payment)
    mortgage_balances.append(new_mortgage_balance)

    # Buy Wealth = Property Value - Mortgage Balance
    new_buy_wealth = new_property_value - new_mortgage_balance
    buy_wealth.append(new_buy_wealth)

    # EPF Wealth = previous * (1+rate) + contribution
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

# Format numbers with commas and RM
df_fmt = df.copy()
for col in ["Property Value (RM)", "Mortgage Balance (RM)", "Buy Wealth (RM)", "EPF Wealth (RM)"]:
    df_fmt[col] = df_fmt[col].apply(lambda x: f"RM {x:,.0f}")

# --------------------------
# Plot
# --------------------------
fig, ax = plt.subplots(figsize=(10, 6))

# Plot with thicker lines
ax.plot(df["Year"], df["Buy Wealth (RM)"], label="🏡 Buy Wealth (Property Equity)", linewidth=2.5, color="#2E86C1")
ax.plot(df["Year"], df["EPF Wealth (RM)"], label="💰 EPF Wealth (Savings Growth)", linewidth=2.5, color="#27AE60")

# Styling
ax.set_xlabel("Year", fontsize=12)
ax.set_ylabel("Wealth (RM)", fontsize=12)
ax.set_title("Comparison of Buy vs EPF Wealth Projection", fontsize=14, weight="bold")
ax.grid(True, linestyle="--", alpha=0.6)

# Remove decimals on x-axis
ax.xaxis.set_major_locator(plt.MaxNLocator(integer=True))

# Format y-axis with RM and commas
ax.yaxis.set_major_formatter(FuncFormatter(lambda x, _: f"RM {x:,.0f}"))

# Improved legend
legend = ax.legend(
    fontsize=11,
    frameon=True,
    fancybox=True,
    shadow=True,
    loc="upper left"
)
legend.get_frame().set_facecolor("white")
legend.get_frame().set_edgecolor("black")

# --------------------------
# Annotate final wealth
# --------------------------
ax.annotate(
    f"RM {buy_wealth[-1]:,.0f}",
    xy=(years, buy_wealth[-1]),
    xytext=(5, 0),
    textcoords="offset points",
    fontsize=11,
    color="#2E86C1",
    weight="bold"
)

ax.annotate(
    f"RM {epf_wealth[-1]:,.0f}",
    xy=(years, epf_wealth[-1]),
    xytext=(5, -15),
    textcoords="offset points",
    fontsize=11,
    color="#27AE60",
    weight="bold"
)

# --------------------------
# Streamlit Outputs
# --------------------------
st.pyplot(fig)
st.subheader("📊 Projection Table")
st.dataframe(df_fmt, use_container_width=True)

# Download CSV
csv = df.to_csv(index=False).encode("utf-8")
st.download_button(
    "⬇️ Download Results (CSV)",
    data=csv,
    file_name="expected_outcomes_buy_vs_epf.csv",
    mime="text/csv"
)

# --------------------------
# Summary Box
# --------------------------
final_buy = buy_wealth[-1]
final_epf = epf_wealth[-1]

st.subheader("📌 Summary")
if final_buy > final_epf:
    st.success(
        f"After **{years} years**, buying a house results in higher wealth:\n\n"
        f"- 🏡 Buy Wealth: **RM {final_buy:,.0f}**\n"
        f"- 💰 EPF Wealth: **RM {final_epf:,.0f}**"
    )
elif final_epf > final_buy:
    st.info(
        f"After **{years} years**, saving in EPF results in higher wealth:\n\n"
        f"- 💰 EPF Wealth: **RM {final_epf:,.0f}**\n"
        f"- 🏡 Buy Wealth: **RM {final_buy:,.0f}**"
    )
else:
    st.warning(
        f"After **{years} years**, both strategies result in about the same wealth:\n\n"
        f"- 🏡 Buy Wealth: **RM {final_buy:,.0f}**\n"
        f"- 💰 EPF Wealth: **RM {final_epf:,.0f}**"
    )
