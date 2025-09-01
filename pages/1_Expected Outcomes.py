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

# Times New Roman for Streamlit text
st.markdown("""
<style>
html, body, [class*="css"]  {
    font-family: 'Times New Roman', serif !important;
}
</style>
""", unsafe_allow_html=True)

# Times New Roman for Matplotlib
matplotlib.rcParams['font.family'] = 'Times New Roman'

st.title("📌 Expected Outcomes – Buy Property vs Rent+EPF")

# --------------------------
# 2. Helper Functions
# --------------------------
def calculate_mortgage_payment(P, r, n):
    return P * (r * (1 + r)**n) / ((1 + r)**n - 1) if r > 0 else P / n

def project_outcomes(P, r, n, g, epf_rate, years):
    PMT = calculate_mortgage_payment(P, r, n)
    property_values, mortgage_balances = [P], [P]
    buy_wealth, epf_wealth = [0], [0]

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

        # EPF wealth = invest PMT (opportunity cost)
        new_epf_wealth = epf_wealth[-1] * (1 + epf_rate) + PMT
        epf_wealth.append(new_epf_wealth)

    df = pd.DataFrame({
        "Year": np.arange(0, years + 1),
        "Property (RM)": property_values,
        "Mortgage (RM)": mortgage_balances,
        "Buy Wealth (RM)": buy_wealth,
        "EPF Wealth (RM)": epf_wealth
    })
    return df

def compute_cagr(df, years):
    buy_cagr = (df["Buy Wealth (RM)"].iloc[-1] / df["Buy Wealth (RM)"].iloc[0])**(1/years) - 1
    epf_cagr = (df["EPF Wealth (RM)"].iloc[-1] / df["EPF Wealth (RM)"].iloc[0])**(1/years) - 1
    return buy_cagr, epf_cagr

def compute_cagr_over_time(df):
    years = df["Year"].values
    buy_cagr = ((df["Buy Wealth (RM)"].values / df["Buy Wealth (RM)"].iloc[0])**(1/years) - 1)
    epf_cagr = ((df["EPF Wealth (RM)"].values / df["EPF Wealth (RM)"].iloc[0])**(1/years) - 1)
    buy_cagr[0], epf_cagr[0] = 0, 0  # handle year 0
    return years, buy_cagr, epf_cagr

def plot_outcomes(df, years):
    buy_cagr, epf_cagr = compute_cagr(df, years)
    buy_final, epf_final = df["Buy Wealth (RM)"].iloc[-1], df["EPF Wealth (RM)"].iloc[-1]
    winner_name = "Buy Property" if buy_final > epf_final else "Rent+EPF"

    fig, ax = plt.subplots(figsize=(10,6))
    ax.plot(df["Year"], df["Buy Wealth (RM)"], label="Buy Property", color="blue", linewidth=2)
    ax.plot(df["Year"], df["EPF Wealth (RM)"], label="Rent+EPF", color="green", linewidth=2)

    # Highlight final values with CAGR
    ax.text(years, buy_final, f"RM {buy_final:,.0f}\n({buy_cagr*100:.2f}% p.a.)",
            color="white" if winner_name=="Buy Property" else "blue",
            fontsize=12, weight="bold",
            bbox=dict(facecolor="blue" if winner_name=="Buy Property" else "none", alpha=0.7, edgecolor="none"),
            ha="left", va="bottom")
    ax.text(years, epf_final, f"RM {epf_final:,.0f}\n({epf_cagr*100:.2f}% p.a.)",
            color="white" if winner_name=="Rent+EPF" else "green",
            fontsize=12, weight="bold",
            bbox=dict(facecolor="green" if winner_name=="Rent+EPF" else "none", alpha=0.7, edgecolor="none"),
            ha="left", va="bottom")

    ax.set_xlabel("Year")
    ax.set_ylabel("Wealth (RM)")
    ax.set_title(f"Comparison Over {years} Years – Winner: {winner_name}", fontsize=14, weight="bold")
    ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f"RM {x:,.0f}"))
    ax.legend()
    ax.grid(True, linestyle="--", alpha=0.6)
    return fig

def plot_cagr_chart(df):
    years, buy_cagr, epf_cagr = compute_cagr_over_time(df)
    fig, ax = plt.subplots(figsize=(10,6))
    ax.plot(years, buy_cagr*100, label="Buy Property CAGR", color="blue", linewidth=2)
    ax.plot(years, epf_cagr*100, label="Rent+EPF CAGR", color="green", linewidth=2)
    ax.set_title("CAGR Over Time", fontsize=14, weight="bold")
    ax.set_xlabel("Year")
    ax.set_ylabel("CAGR (% p.a.)")
    ax.legend()
    ax.grid(True, linestyle="--", alpha=0.6)
    return fig

def format_table(df):
    df_fmt = df.copy()
    for col in ["Property (RM)", "Mortgage (RM)", "Buy Wealth (RM)", "EPF Wealth (RM)"]:
        df_fmt[col] = df_fmt[col].apply(lambda x: f"RM {x:,.0f}")

    buy_final, epf_final = df["Buy Wealth (RM)"].iloc[-1], df["EPF Wealth (RM)"].iloc[-1]
    winner_col = "Buy Wealth (RM)" if buy_final > epf_final else "EPF Wealth (RM)"

    styled_df = df_fmt.style.set_properties(**{'font-family':'Times New Roman','font-size':'14px'})
    styled_df = styled_df.apply(
        lambda x: ['background-color: lightgreen' if x.name==df.index[-1] and col==winner_col else '' for col in df_fmt.columns],
        axis=1
    )
    return styled_df

def generate_summary(df, years):
    buy_final, epf_final = df["Buy Wealth (RM)"].iloc[-1], df["EPF Wealth (RM)"].iloc[-1]
    buy_cagr, epf_cagr = compute_cagr(df, years)

    if buy_final > epf_final:
        return f"📈 After {years} years, **Buying Property** leads with RM {buy_final:,.0f} ({buy_cagr*100:.2f}% p.a.), outperforming Rent+EPF (RM {epf_final:,.0f}, {epf_cagr*100:.2f}% p.a.)."
    elif epf_final > buy_final:
        return f"💰 After {years} years, **Rent+EPF** leads with RM {epf_final:,.0f} ({epf_cagr*100:.2f}% p.a.), outperforming Buying Property (RM {buy_final:,.0f}, {buy_cagr*100:.2f}% p.a.)."
    else:
        return f"⚖️ After {years} years, both strategies result in the same outcome of RM {buy_final:,.0f} ({buy_cagr*100:.2f}% p.a.)."

# --------------------------
# 3. Sidebar Inputs
# --------------------------
st.sidebar.header("⚙️ Baseline Assumptions")
initial_property_price = st.sidebar.number_input("Initial Property Price (RM)", value=500_000, step=50_000)
mortgage_rate = st.sidebar.number_input("Mortgage Rate (Annual, e.g., 0.04)", value=0.04, step=0.01)
loan_term_years = st.sidebar.number_input("Loan Term (Years)", value=30, step=5)
property_growth = st.sidebar.number_input("Property Growth Rate (Annual, e.g., 0.05)", value=0.05, step=0.01)
epf_rate = st.sidebar.number_input("EPF Return Rate (Annual, e.g., 0.06)", value=0.06, step=0.01)
projection_years = st.sidebar.number_input("Projection Years", value=30, step=5)

# --------------------------
# 4. Projection
# --------------------------
df = project_outcomes(initial_property_price, mortgage_rate, loan_term_years, property_growth, epf_rate, projection_years)

# --------------------------
# 5. Tabs
# --------------------------
tab1, tab2, tab3, tab4 = st.tabs(["📈 Wealth Chart","📊 Projection Table","📝 Summary","📊 CAGR Chart"])

with tab1:
    st.pyplot(plot_outcomes(df, projection_years))

with tab2:
    st.dataframe(format_table(df), use_container_width=True)

with tab3:
    st.markdown(generate_summary(df, projection_years), unsafe_allow_html=True)

with tab4:
    st.pyplot(plot_cagr_chart(df))

# --------------------------
# 6. Download CSV
# --------------------------
csv = df.to_csv(index=False).encode('utf-8')
st.download_button("📥 Download Projection Data (CSV)", csv, "projection.csv", "text/csv", key='download-csv')
