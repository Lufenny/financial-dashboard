import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib
import matplotlib.ticker as mticker

# --------------------------
# 1. Global Settings
# --------------------------
st.set_page_config(page_title='Expected Outcomes – Baseline', layout='wide')

# Apply Times New Roman to all Streamlit text
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

# Apply Times New Roman to matplotlib charts
matplotlib.rcParams['font.family'] = 'Times New Roman'

st.title("📌 Expected Outcomes")

# --------------------------
# 2. Helper Functions
# --------------------------
def calculate_mortgage_payment(P, r, n):
    return P * (r * (1 + r)**n) / ((1 + r)**n - 1) if r > 0 else P / n

def project_outcomes(P, r, n, g, epf_rate, years):
    PMT = calculate_mortgage_payment(P, r, n)
    property_value, mortgage_balance, buy_wealth, epf_wealth = P, P, 0, 0
    data = []
    for t in range(1, years + 1):
        property_value *= (1 + g)
        mortgage_balance = mortgage_balance * (1 + r) - PMT if t <= n else 0
        buy_wealth = property_value - mortgage_balance
        epf_wealth = epf_wealth * (1 + epf_rate) + PMT
        data.append([t, property_value, mortgage_balance, buy_wealth, epf_wealth])
    return pd.DataFrame(data, columns=["Year", "Property (RM)", "Mortgage (RM)", "Buy Wealth (RM)", "EPF Wealth (RM)"])

def plot_outcomes(df, years):
    buy_final, epf_final = df["Buy Wealth (RM)"].iloc[-1], df["EPF Wealth (RM)"].iloc[-1]
    if buy_final > epf_final:
        winner_color, loser_color = "blue", "green"
        winner, loser = "Buy Property", "EPF Savings"
    else:
        winner_color, loser_color = "green", "blue"
        winner, loser = "EPF Savings", "Buy Property"

    fig, ax = plt.subplots(figsize=(10, 6))
    ax.plot(df["Year"], df["Buy Wealth (RM)"], label="Buy Property", color="blue", linewidth=2)
    ax.plot(df["Year"], df["EPF Wealth (RM)"], label="EPF Savings", color="green", linewidth=2)

    # Highlight winning strategy area
    if winner == "Buy Property":
        ax.fill_between(df["Year"], df["Buy Wealth (RM)"], df["EPF Wealth (RM)"], color="blue", alpha=0.1)
    else:
        ax.fill_between(df["Year"], df["EPF Wealth (RM)"], df["Buy Wealth (RM)"], color="green", alpha=0.1)

    # Annotate final values
    ax.text(years, df["Buy Wealth (RM)"].iloc[-1],
            f"RM {df['Buy Wealth (RM)'].iloc[-1]:,.0f}",
            color="white" if winner=="Buy Property" else "blue",
            fontsize=12, weight="bold",
            bbox=dict(facecolor="blue" if winner=="Buy Property" else "none", alpha=0.7, edgecolor="none"),
            ha="left", va="bottom")
    ax.text(years, df["EPF Wealth (RM)"].iloc[-1],
            f"RM {df['EPF Wealth (RM)'].iloc[-1]:,.0f}",
            color="white" if winner=="EPF Savings" else "green",
            fontsize=12, weight="bold",
            bbox=dict(facecolor="green" if winner=="EPF Savings" else "none", alpha=0.7, edgecolor="none"),
            ha="left", va="bottom")

    ax.set_title(f"Comparison Over {years} Years – Winner: {winner}", fontsize=14, weight="bold")
    ax.set_xlabel("Year")
    ax.set_ylabel("Wealth (RM)")
    ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f"RM {x:,.0f}"))
    ax.legend()
    ax.grid(True, linestyle="--", alpha=0.6)
    return fig

def format_table(df):
    df_fmt = df.copy()
    for col in ["Property (RM)", "Mortgage (RM)", "Buy Wealth (RM)", "EPF Wealth (RM)"]:
        df_fmt[col] = df_fmt[col].apply(lambda x: f"RM {x:,.0f}")

    # Determine winner column based on final year
    buy_final, epf_final = df["Buy Wealth (RM)"].iloc[-1], df["EPF Wealth (RM)"].iloc[-1]
    winner_col = "Buy Wealth (RM)" if buy_final > epf_final else "EPF Wealth (RM)"

    # Highlight only the last row of the winning column
    styled_df = df_fmt.style.set_properties(**{'font-family': 'Times New Roman', 'font-size': '14px'})
    styled_df = styled_df.apply(
        lambda x: ['background-color: lightgreen' if x.name == df.index[-1] and col == winner_col else '' for col in df_fmt.columns],
        axis=1
    )
    return styled_df

def generate_summary(df, years):
    buy_final, epf_final = df["Buy Wealth (RM)"].iloc[-1], df["EPF Wealth (RM)"].iloc[-1]
    if buy_final > epf_final:
        summary_text = f"📈 After {years} years, **Buying Property** leads with RM {buy_final:,.0f}, outperforming EPF (RM {epf_final:,.0f})."
    elif epf_final > buy_final:
        summary_text = f"💰 After {years} years, **EPF Savings** leads with RM {epf_final:,.0f}, outperforming Buying Property (RM {buy_final:,.0f})."
    else:
        summary_text = f"⚖️ After {years} years, both strategies result in the same outcome of RM {buy_final:,.0f}."
    return summary_text

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
# 4. Baseline Assumptions Box
# --------------------------
st.subheader("📌 Baseline Assumptions")
st.markdown("""
| Parameter | Baseline Value | Justification / Source |
|-----------|---------------|----------------------|
| Initial Property Price | RM 500,000 | Typical property price in target area |
| Annual Property Growth Rate | 5% | Based on historical market appreciation |
| Mortgage Rate | 4% | Current average bank home loan rate |
| Loan Term | 30 years | Standard mortgage duration |
| EPF Annual Growth Rate | 6% | Historical EPF dividend trends |
| Projection Years | 30 | Long-term wealth accumulation horizon |
""")

# --------------------------
# 5. Main Outputs with Tabs
# --------------------------
df = project_outcomes(initial_property_price, mortgage_rate, loan_term_years, property_growth, epf_rate, projection_years)

tab1, tab2, tab3 = st.tabs(["📈 Chart", "📊 Table", "📝 Summary"])

with tab1:
    st.pyplot(plot_outcomes(df, projection_years))

with tab2:
    st.dataframe(format_table(df), use_container_width=True)

    # Result Box below Table
    buy_final, epf_final = df["Buy Wealth (RM)"].iloc[-1], df["EPF Wealth (RM)"].iloc[-1]
    if buy_final > epf_final:
        winner, loser = "Buy Property", "EPF Savings"
        diff = buy_final - epf_final
    elif epf_final > buy_final:
        winner, loser = "EPF Savings", "Buy Property"
        diff = epf_final - buy_final
    else:
        winner, loser, diff = "Tie", "Tie", 0

    st.markdown(
        f"""
        <div style="padding:15px; border-radius:10px; background-color:#f0f9f0; border:1px solid #b6e2b6;">
            <h4 style="margin:0; font-family:'Times New Roman';">🏆 Result Summary</h4>
            <p style="margin:5px 0; font-family:'Times New Roman'; font-size:16px;">
                <b>Winner:</b> {winner}<br>
                <b>Loser:</b> {loser}<br>
                <b>Difference:</b> RM {diff:,.0f}
            </p>
        </div>
        """,
        unsafe_allow_html=True
    )

with tab3:
    st.markdown(generate_summary(df, projection_years), unsafe_allow_html=True)

    # Result Box under Summary
    st.markdown(
        f"""
        <div style="padding:15px; border-radius:10px; background-color:#f0f9f0; border:1px solid #b6e2b6;">
            <h4 style="margin:0; font-family:'Times New Roman';">🏆 Result Summary</h4>
            <p style="margin:5px 0; font-family:'Times New Roman'; font-size:16px;">
                <b>Winner:</b> {winner}<br>
                <b>Loser:</b> {loser}<br>
                <b>Difference:</b> RM {diff:,.0f}
            </p>
        </div>
        """,
        unsafe_allow_html=True
    )

# --------------------------
# 6. Download Option
# --------------------------
csv = df.to_csv(index=False).encode('utf-8')
st.download_button("📥 Download Projection Data (CSV)", csv, "projection.csv", "text/csv", key='download-csv')
