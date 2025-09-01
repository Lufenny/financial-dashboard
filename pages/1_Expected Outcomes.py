import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib

# --------------------------
# 1. Global Settings
# --------------------------
st.set_page_config(page_title='Expected Outcomes – Baseline', layout='wide')

# ✅ Apply Times New Roman everywhere
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

# ✅ Ensure matplotlib uses Times New Roman too
matplotlib.rcParams['font.family'] = 'Times New Roman'

st.title("📌 Expected Outcomes – Baseline Comparison")


# --------------------------
# 2. Helper Functions
# --------------------------
def calculate_mortgage_payment(P, r, n):
    """Annual mortgage payment (PMT) based on property price, rate, and term."""
    return P * (r * (1 + r)**n) / ((1 + r)**n - 1) if r > 0 else P / n


def project_outcomes(P, r, n, g, epf_rate, years):
    """Generate yearly projection of Buy vs EPF wealth."""
    PMT = calculate_mortgage_payment(P, r, n)
    property_value, mortgage_balance, buy_wealth, epf_wealth = P, P, 0, 0

    data = []
    for t in range(1, years + 1):
        property_value *= (1 + g)                # Property appreciation
        mortgage_balance = mortgage_balance * (1 + r) - PMT if t <= n else 0
        buy_wealth = property_value - mortgage_balance
        epf_wealth = epf_wealth * (1 + epf_rate) + PMT
        data.append([t, property_value, mortgage_balance, buy_wealth, epf_wealth])

    return pd.DataFrame(data, columns=["Year", "Property (RM)", "Mortgage (RM)", "Buy Wealth (RM)", "EPF Wealth (RM)"])


def plot_outcomes(df, years, buy_wealth, epf_wealth):
    """Line chart comparing Buy vs EPF outcomes."""
    fig, ax = plt.subplots(figsize=(8, 5))
    ax.plot(df["Year"], df["Buy Wealth (RM)"], label="Buy Property", linewidth=2)
    ax.plot(df["Year"], df["EPF Wealth (RM)"], label="EPF Savings", linewidth=2)

    # Highlight final outcomes
    winner = "Buy Property" if buy_wealth > epf_wealth else "EPF Savings"
    ax.set_title(f"Comparison Over {years} Years – Winner: {winner}", fontsize=14, weight="bold")
    ax.set_xlabel("Year")
    ax.set_ylabel("Wealth (RM)")
    ax.legend()
    ax.grid(True, linestyle="--", alpha=0.6)

    return fig


def format_table(df):
    """Format RM values with commas and Times New Roman styling."""
    df_fmt = df.copy()
    for col in ["Property (RM)", "Mortgage (RM)", "Buy Wealth (RM)", "EPF Wealth (RM)"]:
        df_fmt[col] = df_fmt[col].apply(lambda x: f"RM {x:,.0f}")

    styled_df = df_fmt.style.set_properties(**{
        'font-family': 'Times New Roman',
        'font-size': '14px'
    })
    return styled_df


def generate_summary(buy_wealth, epf_wealth, years):
    """Textual explanation for examiner / reader."""
    if buy_wealth > epf_wealth:
        return f"📈 After {years} years, **Buying Property** leads with RM {buy_wealth:,.0f}, outperforming EPF (RM {epf_wealth:,.0f})."
    elif epf_wealth > buy_wealth:
        return f"💰 After {years} years, **EPF Savings** leads with RM {epf_wealth:,.0f}, outperforming Buying Property (RM {buy_wealth:,.0f})."
    else:
        return f"⚖️ After {years} years, both strategies result in the same outcome of RM {buy_wealth:,.0f}."


# --------------------------
# 3. Sidebar Inputs
# --------------------------
st.sidebar.header("⚙️ Baseline Assumptions")

initial_property_price = st.sidebar.number_input("Initial Property Price (RM)", value=500_000, step=50_000)
mortgage_rate = st.sidebar.number_input("Mortgage Rate (Annual)", value=0.04, step=0.01)
loan_term_years = st.sidebar.number_input("Loan Term (Years)", value=30, step=5)
property_growth = st.sidebar.number_input("Property Growth Rate (Annual)", value=0.05, step=0.01)
epf_rate = st.sidebar.number_input("EPF Return Rate (Annual)", value=0.06, step=0.01)
projection_years = st.sidebar.number_input("Projection Years", value=30, step=5)


# --------------------------
# 4. Main Outputs with Tabs
# --------------------------
df = project_outcomes(initial_property_price, mortgage_rate, loan_term_years, property_growth, epf_rate, projection_years)
buy_wealth, epf_wealth = df["Buy Wealth (RM)"].iloc[-1], df["EPF Wealth (RM)"].iloc[-1]

tab1, tab2, tab3 = st.tabs(["📈 Chart", "📊 Table", "📝 Summary"])

with tab1:
    st.pyplot(plot_outcomes(df, projection_years, buy_wealth, epf_wealth))

with tab2:
    st.dataframe(format_table(df), use_container_width=True)

with tab3:
    st.write(generate_summary(buy_wealth, epf_wealth, projection_years))


# --------------------------
# 5. Download Option
# --------------------------
csv = df.to_csv(index=False).encode('utf-8')
st.download_button("📥 Download Projection Data (CSV)", csv, "projection.csv", "text/csv", key='download-csv')
