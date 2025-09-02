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
    return P * (r * (1 + r)**n) / ((1 + r)**n - 1) if r > 0 else P / n

def project_outcomes(P, r, n, g, epf_rate, rent_yield, years, custom_rent=None):
    PMT = calculate_mortgage_payment(P, r, n)
    property_values, mortgage_balances = [P], [P]
    buy_wealth, epf_wealth, rents, cum_rent = [0], [0], [], []

    # Initial rent setup
    initial_rent = custom_rent if custom_rent is not None else P * rent_yield
    rents.append(initial_rent)
    cum_rent.append(initial_rent)

    for t in range(1, years + 1):
        # Property growth
        new_property_value = property_values[-1] * (1 + g)
        property_values.append(new_property_value)

        # Mortgage repayment
        interest_payment = mortgage_balances[-1] * r
        principal_payment = PMT - interest_payment
        new_mortgage_balance = max(0, mortgage_balances[-1] - principal_payment)
        mortgage_balances.append(new_mortgage_balance)

        # Buy wealth = property value - mortgage
        new_buy_wealth = new_property_value - new_mortgage_balance
        buy_wealth.append(new_buy_wealth)

        # Rent grows with property value
        rent_payment = (custom_rent if custom_rent is not None else new_property_value * rent_yield)
        rents.append(rent_payment)
        cum_rent.append(cum_rent[-1] + rent_payment)

        # EPF wealth = invest mortgage payment - rent
        investable = max(0, PMT - rent_payment)
        new_epf_wealth = epf_wealth[-1] * (1 + epf_rate) + investable
        epf_wealth.append(new_epf_wealth)

    return pd.DataFrame({
        "Year": np.arange(0, years + 1),
        "Property (RM)": property_values,
        "Mortgage (RM)": mortgage_balances,
        "Buy Wealth (RM)": buy_wealth,
        "EPF Wealth (RM)": epf_wealth,
        "Annual Rent (RM)": rents,
        "Cumulative Rent (RM)": cum_rent
    })

def plot_outcomes(df, years):
    buy_final, epf_final = df["Buy Wealth (RM)"].iloc[-1], df["EPF Wealth (RM)"].iloc[-1]
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

    # Annotate final values with slight x-shift
    offset = 0.3
    ax.text(years + offset, buy_final, f"RM {buy_final:,.0f}",
            color="white" if winner_name == "Buy Property" else "blue",
            fontsize=12, weight="bold",
            bbox=dict(facecolor="blue" if winner_name == "Buy Property" else "none", alpha=0.7, edgecolor="none"),
            ha="left", va="bottom")

    ax.text(years + offset, epf_final, f"RM {epf_final:,.0f}",
            color="white" if winner_name == "Rent+EPF" else "green",
            fontsize=12, weight="bold",
            bbox=dict(facecolor="green" if winner_name == "Rent+EPF" else "none", alpha=0.7, edgecolor="none"),
            ha="left", va="bottom")

    ax.text(years + offset, rent_final, f"RM {rent_final:,.0f}",
            color="red", fontsize=11, weight="bold", ha="left", va="bottom")

    ax.set_title(f"Comparison Over {years} Years – Winner: {winner_name}", fontsize=14, weight="bold")
    ax.set_xlabel("Year")
    ax.set_ylabel("Wealth / Rent (RM)")
    ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f"RM {x:,.0f}"))
    ax.legend()
    ax.grid(True, linestyle="--", alpha=0.6)
    ax.set_axisbelow(True)
    return fig

def format_table(df):
    df_fmt = df.copy()
    for col in ["Property (RM)", "Mortgage (RM)", "Buy Wealth (RM)", "EPF Wealth (RM)", "Annual Rent (RM)", "Cumulative Rent (RM)"]:
        df_fmt[col] = df_fmt[col].apply(lambda x: f"RM {x:,.0f}")

    buy_final, epf_final = df["Buy Wealth (RM)"].iloc[-1], df["EPF Wealth (RM)"].iloc[-1]
    winner_col = "Buy Wealth (RM)" if buy_final > epf_final else "EPF Wealth (RM)"

    def highlight_winner(row):
        if row.name == df.index[-1]:
            color = 'lightgreen' if row[winner_col] == f"RM {max(buy_final, epf_final):,.0f}" else ''
            return [f'background-color: {color}' for _ in row]
        return ['' for _ in row]

    styled_df = df_fmt.style.set_properties(**{'font-family':'Times New Roman','font-size':'14px'})
    styled_df = styled_df.apply(highlight_winner, axis=1)
    return styled_df

def calculate_cagr(initial, final, years):
    if years <= 0 or final <= 0:
        return 0
    if initial <= 0:
        return 0
    return (final / initial) ** (1 / years) - 1

def generate_summary(df, years):
    buy_final = df["Buy Wealth (RM)"].iloc[-1]
    epf_final = df["EPF Wealth (RM)"].iloc[-1]
    rent_final = df["Cumulative Rent (RM)"].iloc[-1]

    # Use first positive year for CAGR (not hardcoded index 1)
    buy_initial = next((x for x in df["Buy Wealth (RM)"] if x > 0), 1)
    epf_initial = next((x for x in df["EPF Wealth (RM)"] if x > 0), 1)

    buy_cagr = calculate_cagr(buy_initial, buy_final, years)
    epf_cagr = calculate_cagr(epf_initial, epf_final, years)

    winner = "Buy Property" if buy_final > epf_final else "Rent+EPF"
    ratio = buy_final / epf_final if epf_final > 0 else float('inf')

    summary = f"""
    ### 📊 Expected Outcomes after {years} Years  

    - **Buy Property Wealth**: RM {buy_final:,.0f}  (CAGR: {buy_cagr*100:.2f}%)  
    - **Rent+EPF Wealth**: RM {epf_final:,.0f}  (CAGR: {epf_cagr*100:.2f}%)  
    - **Cumulative Rent Paid**: RM {rent_final:,.0f}  
    - **Wealth Ratio (Buy ÷ Rent+EPF)**: {ratio:.2f}x  

    🏆 **Winner: {winner}**
    """
    return summary


# --------------------------
# 3. Sidebar Inputs
# --------------------------
st.sidebar.header("⚙️ Baseline Assumptions")
initial_property_price = st.sidebar.number_input("Initial Property Price (RM)", value=500_000, step=50_000)
mortgage_rate = st.sidebar.number_input("Mortgage Rate (Annual)", value=0.04, step=0.01)
loan_term_years = st.sidebar.number_input("Loan Term (Years)", value=30, step=5)
property_growth = st.sidebar.number_input("Property Growth Rate (Annual)", value=0.05, step=0.01)
epf_rate = st.sidebar.number_input("EPF Return Rate (Annual)", value=0.06, step=0.01)
rent_yield = st.sidebar.number_input("Rent Yield (from EDA)", value=0.04, step=0.005)
projection_years = st.sidebar.number_input("Projection Years", value=30, step=5)

use_custom_rent = st.sidebar.checkbox("Use Custom Starting Rent?")
custom_rent = None
if use_custom_rent:
    custom_rent = st.sidebar.number_input("Custom Starting Annual Rent (RM)", value=20000, step=1000)

# --------------------------
# 4. Projection
# --------------------------
df = project_outcomes(initial_property_price, mortgage_rate, loan_term_years, property_growth, epf_rate, rent_yield, projection_years, custom_rent)

# --------------------------
# 5. Tabs
# --------------------------
tab1, tab2, tab3 = st.tabs(["📈 Chart","📊 Table","📝 Summary"])

with tab1:
    st.pyplot(plot_outcomes(df, projection_years))

with tab2:
    st.dataframe(format_table(df), use_container_width=True)

with tab3:
    col1, col2, col3 = st.columns(3)
    col1.metric("Buy Property Wealth", f"RM {df['Buy Wealth (RM)'].iloc[-1]:,.0f}")
    col2.metric("Rent+EPF Wealth", f"RM {df['EPF Wealth (RM)'].iloc[-1]:,.0f}")
    col3.metric("Cumulative Rent Paid", f"RM {df['Cumulative Rent (RM)'].iloc[-1]:,.0f}")
    st.markdown(generate_summary(df, projection_years), unsafe_allow_html=True)

# --------------------------
# 6. Download CSV
# --------------------------
csv = df.to_csv(index=False).encode('utf-8')
st.download_button("📥 Download Projection Data (CSV)", csv, "projection.csv", "text/csv", key='download-csv')
