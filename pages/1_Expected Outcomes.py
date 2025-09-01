import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib
import matplotlib.ticker as mticker

# --------------------------
# 1. Global Settings
# --------------------------
st.set_page_config(page_title='Expected Outcomes – Fair Comparison', layout='wide')

# Times New Roman font for Streamlit
st.markdown(
    """
    <style>
    html, body, [class*="css"]  {
        font-family: 'Times New Roman', serif !important;
    }
    </style>
    """,
    unsafe_allow_html=True
)

# Times New Roman for matplotlib
matplotlib.rcParams['font.family'] = 'Times New Roman'

st.title("📌 Expected Outcomes – Buy Property vs Rent+EPF")

# --------------------------
# 2. Helper Functions
# --------------------------
def calculate_mortgage_payment(P, r, n):
    """Annual mortgage payment for a fully-amortizing loan (n years)."""
    return P * (r * (1 + r)**n) / ((1 + r)**n - 1) if r > 0 else P / n

def calculate_cagr(final_value, initial_value, years):
    """Compound Annual Growth Rate with safe guards for non-positive initial value."""
    if years <= 0:
        return 0.0
    # Wealth starts at 0 in this model; use a tiny positive baseline to avoid /0
    base = initial_value if initial_value and initial_value > 0 else 1.0
    if final_value <= 0:
        return 0.0
    return (final_value / base) ** (1 / years) - 1

def project_outcomes(P, r, n, g, epf_rate, rent_yield, years):
    """
    - Property value grows at g.
    - Rent each year = property_value(t) * rent_yield (proxy via EDA)
    - EPF invests the 'mortgage payment - rent' if positive (opportunity cost framing).
    """
    PMT = calculate_mortgage_payment(P, r, n)

    # Year 0 (starting state)
    property_values      = [P]
    mortgage_balances    = [P]
    buy_wealth           = [0.0]
    epf_wealth           = [0.0]
    annual_rents         = [0.0]     # No rent "paid" at t=0 snapshot
    cumulative_rents     = [0.0]

    for t in range(1, years + 1):
        # Property growth
        new_property_value = property_values[-1] * (1 + g)
        property_values.append(new_property_value)

        # Mortgage repayment
        interest_payment     = mortgage_balances[-1] * r
        principal_payment    = PMT - interest_payment
        new_mortgage_balance = max(0.0, mortgage_balances[-1] - principal_payment)
        mortgage_balances.append(new_mortgage_balance)

        # Buy wealth = property value - mortgage
        new_buy_wealth = new_property_value - new_mortgage_balance
        buy_wealth.append(new_buy_wealth)

        # Rent grows with property value (proxy via rent_yield)
        rent_payment = new_property_value * rent_yield
        annual_rents.append(rent_payment)
        cumulative_rents.append(cumulative_rents[-1] + rent_payment)

        # EPF wealth = invest mortgage payment minus rent (if positive)
        investable = max(0.0, PMT - rent_payment)
        new_epf_wealth = epf_wealth[-1] * (1 + epf_rate) + investable
        epf_wealth.append(new_epf_wealth)

    return pd.DataFrame({
        "Year": np.arange(0, years + 1),
        "Property (RM)": property_values,
        "Mortgage (RM)": mortgage_balances,
        "Buy Wealth (RM)": buy_wealth,
        "EPF Wealth (RM)": epf_wealth,
        "Rent (RM)": annual_rents,
        "Cumulative Rent (RM)": cumulative_rents
    })

def plot_outcomes(df, years):
    buy_final = df["Buy Wealth (RM)"].iloc[-1]
    epf_final = df["EPF Wealth (RM)"].iloc[-1]
    rent_final = df["Cumulative Rent (RM)"].iloc[-1]
    winner_col = "Buy Wealth (RM)" if buy_final > epf_final else "EPF Wealth (RM)"
    winner_name = "Buy Property" if winner_col == "Buy Wealth (RM)" else "Rent+EPF"

    fig, ax = plt.subplots(figsize=(10, 6))
    ax.plot(df["Year"], df["Buy Wealth (RM)"], label="Buy Property", color="blue", linewidth=2)
    ax.plot(df["Year"], df["EPF Wealth (RM)"], label="Rent+EPF", color="green", linewidth=2)
    ax.plot(df["Year"], df["Cumulative Rent (RM)"], label="Cumulative Rent", color="red", linestyle="--", linewidth=2)

    # Highlight area
    if winner_name == "Buy Property":
        ax.fill_between(df["Year"], df["Buy Wealth (RM)"], df["EPF Wealth (RM)"], color="blue", alpha=0.1)
    else:
        ax.fill_between(df["Year"], df["EPF Wealth (RM)"], df["Buy Wealth (RM)"], color="green", alpha=0.1)

    # Annotate final values
    ax.text(years, buy_final,
            f"RM {buy_final:,.0f}",
            color="white" if winner_name == "Buy Property" else "blue",
            fontsize=12, weight="bold",
            bbox=dict(facecolor="blue" if winner_name == "Buy Property" else "none", alpha=0.7, edgecolor="none"),
            ha="left", va="bottom")

    ax.text(years, epf_final,
            f"RM {epf_final:,.0f}",
            color="white" if winner_name == "Rent+EPF" else "green",
            fontsize=12, weight="bold",
            bbox=dict(facecolor="green" if winner_name == "Rent+EPF" else "none", alpha=0.7, edgecolor="none"),
            ha="left", va="bottom")

    ax.text(years, rent_final,
            f"RM {rent_final:,.0f}",
            color="red", fontsize=11, weight="bold", ha="left", va="bottom")

    ax.set_title(f"Comparison Over {years} Years – Winner: {winner_name}", fontsize=14, weight="bold")
    ax.set_xlabel("Year")
    ax.set_ylabel("Wealth / Rent (RM)")
    ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f"RM {x:,.0f}"))
    ax.legend()
    ax.grid(True, linestyle="--", alpha=0.6)
    return fig

def format_table(df):
    df_fmt = df.copy()
    for col in ["Property (RM)", "Mortgage (RM)", "Buy Wealth (RM)", "EPF Wealth (RM)", "Rent (RM)", "Cumulative Rent (RM)"]:
        df_fmt[col] = df_fmt[col].apply(lambda x: f"RM {x:,.0f}")

    buy_final = df["Buy Wealth (RM)"].iloc[-1]
    epf_final = df["EPF Wealth (RM)"].iloc[-1]
    winner_col = "Buy Wealth (RM)" if buy_final > epf_final else "EPF Wealth (RM)"

    styled_df = df_fmt.style.set_properties(**{'font-family':'Times New Roman','font-size':'14px'})
    styled_df = styled_df.apply(
        lambda x: [
            'background-color: lightgreen' if x.name == df.index[-1] and col == winner_col else ''
            for col in df_fmt.columns
        ],
        axis=1
    )
    return styled_df

def generate_summary(df, years, initial_price):
    buy_final = df["Buy Wealth (RM)"].iloc[-1]
    epf_final = df["EPF Wealth (RM)"].iloc[-1]
    rent_final = df["Cumulative Rent (RM)"].iloc[-1]

    # CAGR: wealth starts at 0 in Year 0; use a tiny base to avoid divide-by-zero.
    buy_cagr = calculate_cagr(buy_final, 1.0, years)
    epf_cagr = calculate_cagr(epf_final, 1.0, years)

    winner = "Buy Property" if buy_final > epf_final else "Rent+EPF"

    summary = f"""
    ### 📊 Expected Outcomes after {years} Years

    - **Buy Property Wealth**: RM {buy_final:,.0f}  
      - CAGR: **{buy_cagr:.2%}** per year  

    - **Rent+EPF Wealth**: RM {epf_final:,.0f}  
      - CAGR: **{epf_cagr:.2%}** per year  

    - **Cumulative Rent Paid**: RM {rent_final:,.0f}

    🏆 **Winner: {winner}**
    """
    return summary

# --------------------------
# 3. Sidebar Inputs
# --------------------------
st.sidebar.header("⚙️ Baseline Assumptions")
initial_property_price = st.sidebar.number_input("Initial Property Price (RM)", value=500_000, step=50_000)
mortgage_rate        = st.sidebar.number_input("Mortgage Rate (Annual)", value=0.04, step=0.01, format="%.3f")
loan_term_years      = st.sidebar.number_input("Loan Term (Years)", value=30, step=5)
property_growth      = st.sidebar.number_input("Property Growth Rate (Annual)", value=0.05, step=0.01, format="%.3f")
epf_rate             = st.sidebar.number_input("EPF Return Rate (Annual)", value=0.06, step=0.01, format="%.3f")
rent_yield           = st.sidebar.number_input("Rent Yield (from EDA)", value=0.04, step=0.005, format="%.3f")
projection_years     = st.sidebar.number_input("Projection Years", value=30, step=5)

# --------------------------
# 4. Projection
# --------------------------
df = project_outcomes(
    initial_property_price, mortgage_rate, loan_term_years,
    property_growth, epf_rate, rent_yield, projection_years
)

# --------------------------
# 5. Tabs
# --------------------------
tab1, tab2, tab3 = st.tabs(["📈 Chart","📊 Table","📝 Summary"])

with tab1:
    st.pyplot(plot_outcomes(df, projection_years))

with tab2:
    st.dataframe(format_table(df), use_container_width=True)

with tab3:
    st.markdown(generate_summary(df, projection_years, initial_property_price), unsafe_allow_html=True)

# --------------------------
# 6. Download CSV
# --------------------------
csv = df.to_csv(index=False).encode('utf-8')
st.download_button("📥 Download Projection Data (CSV)", csv, "projection.csv", "text/csv", key='download-csv')
