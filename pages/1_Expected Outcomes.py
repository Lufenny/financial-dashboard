import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

# Page config
st.set_page_config(page_title="Expected Outcomes – Baseline", layout="wide")
st.title("📌 Expected Outcomes – Baseline Comparison")

# --------------------------
# Link Between EDA & Expected Outcomes
# --------------------------
st.subheader("🔗 Link to EDA Insights")

# Short visible summary
st.write(
    "The Expected Outcomes are directly shaped by insights from the Exploratory Data Analysis (EDA), "
    "which provided the assumptions for property growth, EPF returns, and inflation trends."
)

# Expander for more detail
with st.expander("See how EDA informs Expected Outcomes"):
    st.markdown(
        "- **Property Price Growth**: Historical market appreciation rates were used as the assumption.  \n"
        "- **EPF Returns**: Dividend trends informed the baseline and optimistic return scenarios.  \n"
        "- **Inflation**: Past patterns guided the selection of realistic inflation ranges.  \n\n"
        "These EDA-driven assumptions serve as the foundation for comparing long-term "
        "wealth accumulation between **buying property** and **saving in EPF**."
    )

# --------------------------
# Sidebar Inputs
# --------------------------
st.sidebar.header("⚙️ Baseline Assumptions")

initial_property_price = st.sidebar.number_input("Initial Property Price (RM)", value=500000, step=10000)
property_growth_rate = st.sidebar.number_input("Annual Property Growth Rate (%)", value=5.0, step=0.1) / 100
mortgage_rate = st.sidebar.number_input("Mortgage Interest Rate (%)", value=4.0, step=0.1) / 100
loan_term_years = st.sidebar.number_input("Loan Term (Years)", value=20, step=1)
annual_epf_contribution = st.sidebar.number_input("Annual EPF Contribution (RM)", value=20000, step=1000)
epf_rate = st.sidebar.number_input("EPF Annual Growth Rate (%)", value=5.0, step=0.1) / 100
years = st.sidebar.number_input("Projection Horizon (Years)", value=20, step=1)

# --------------------------
# Mortgage Calculation
# --------------------------
P = initial_property_price
r = mortgage_rate
n = loan_term_years

if r > 0:
    PMT = P * (r * (1 + r)**n) / ((1 + r)**n - 1)  # Annual repayment
else:
    PMT = P / n

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

    # Mortgage repayment
    interest_payment = mortgage_balances[-1] * r
    principal_payment = PMT - interest_payment
    new_mortgage_balance = max(0, mortgage_balances[-1] - principal_payment)
    mortgage_balances.append(new_mortgage_balance)

    # Wealth
    new_buy_wealth = new_property_value - new_mortgage_balance
    buy_wealth.append(new_buy_wealth)

    new_epf_wealth = epf_wealth[-1] * (1 + epf_rate) + annual_epf_contribution
    epf_wealth.append(new_epf_wealth)

# --------------------------
# CAGR
# --------------------------
buy_cagr = (buy_wealth[-1] / buy_wealth[0])**(1/years) - 1 if buy_wealth[0] > 0 else (buy_wealth[-1] / 1e3)**(1/years) - 1
epf_cagr = (epf_wealth[-1] / epf_wealth[0])**(1/years) - 1 if epf_wealth[0] > 0 else (epf_wealth[-1] / 1e3)**(1/years) - 1

# --------------------------
# Chart
# --------------------------
fig, ax = plt.subplots(figsize=(10, 6))
ax.plot(range(years + 1), buy_wealth, label="Buy Property", color="blue")
ax.plot(range(years + 1), epf_wealth, label="EPF Savings", color="green")

ax.set_xlabel("Year")
ax.set_ylabel("Wealth (RM)")
ax.set_title("Expected Outcomes: Buy Property vs EPF")
ax.legend()

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
    subtitle = " In this scenario, Buying Property outperforms EPF."
else:
    ax.text(years, epf_wealth[-1],
            f"RM {epf_wealth[-1]:,.0f}\n({epf_cagr*100:.2f}% p.a.)",
            fontsize=12, color="white", weight="bold",
            ha="left", va="bottom",
            bbox=dict(facecolor="green", alpha=0.7, edgecolor="none"))
    ax.text(years, buy_wealth[-1],
            f"RM {buy_wealth[-1]:,.0f}\n({buy_cagr*100:.2f}% p.a.)",
            fontsize=10, color="blue", ha="left", va="bottom")
    subtitle = " In this scenario, EPF outperforms Buying Property."

plt.figtext(0.5, -0.05, subtitle, wrap=True, ha="center", fontsize=12, fontweight="bold", fontname="Times New Roman")

st.pyplot(fig)

# --------------------------
# DataFrame Results
# --------------------------
df = pd.DataFrame({
    "Year": np.arange(0, years + 1),
    "Property (RM)": property_values,
    "Mortgage (RM)": mortgage_balances,
    "Buy Wealth (RM)": buy_wealth,
    "EPF Wealth (RM)": epf_wealth
})

# Format copy for table
df_fmt = df.copy()
for col in ["Property (RM)", "Mortgage (RM)", "Buy Wealth (RM)", "EPF Wealth (RM)"]:
    df_fmt[col] = df_fmt[col].apply(lambda x: f"RM {x:,.0f}")

st.subheader("📊 Projection Table")
st.dataframe(df_fmt, use_container_width=True)

# --------------------------
# Download CSV
# --------------------------
csv = df.to_csv(index=False).encode("utf-8")
st.download_button(
    "⬇️ Download Projection Results (CSV)",
    data=csv,
    file_name="expected_outcomes.csv",
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
