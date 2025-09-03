import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from fpdf import FPDF
import io

# ----------------------------
# Streamlit App Config
# ----------------------------
st.set_page_config(page_title="Buy vs Rent EDA Dashboard", layout="wide")
st.sidebar.title("🏡 Assumptions & Navigation")
page = st.sidebar.radio("Go to:", ["📊 EDA Overview", "📈 Wealth Comparison", "⚖️ Sensitivity Analysis"])

# ----------------------------
# Base Financial Inputs
# ----------------------------
st.sidebar.header("💰 Base Financial Inputs")
mortgage_term = st.sidebar.number_input("Mortgage Term (years)", value=30, step=1)
property_price = st.sidebar.number_input("Property Price (RM)", value=500000, step=1000)
monthly_rent = st.sidebar.number_input("Monthly Rent (RM)", value=1500, step=100)
years = st.sidebar.number_input("Analysis Period (Years)", value=30, step=1)

# ----------------------------
# Generate Dataset Function
# ----------------------------
def generate_financial_df(mortgage_rate, rent_escalation, investment_return):
    df = pd.DataFrame({"Year": np.arange(1, years + 1)})
    # Mortgage monthly payment
    r = mortgage_rate / 100 / 12
    n = mortgage_term * 12
    monthly_payment = property_price * r * (1 + r)**n / ((1 + r)**n - 1)
    df["Monthly_Mortgage"] = monthly_payment
    df["Cumulative_Mortgage_Paid"] = df["Monthly_Mortgage"].cumsum() * 12 / 12
    # Home equity (simplified)
    df["Home_Equity"] = property_price * (df["Year"] / mortgage_term).clip(upper=1)
    # Rent scenario
    df["Annual_Rent"] = monthly_rent * 12 * (1 + rent_escalation/100)**(df["Year"]-1)
    df["Rent_Saved"] = df["Monthly_Mortgage"]*12 - df["Annual_Rent"]
    df["Rent_Saved"] = df["Rent_Saved"].clip(lower=0)
    # Investment growth
    df["Investment_Value"] = df["Rent_Saved"].cumsum() * ((1 + investment_return/100) ** (df["Year"]-1))
    # Net wealth
    df["Net_Wealth_Buy"] = df["Home_Equity"] - df["Cumulative_Mortgage_Paid"]
    df["Net_Wealth_Rent"] = df["Investment_Value"]
    return df

# ----------------------------
# EDA Overview Page
# ----------------------------
if page == "📊 EDA Overview":
    st.title("🔎 Dataset Preview & Stats")
    mortgage_rate = st.sidebar.number_input("Mortgage Rate (%)", value=4.0, step=0.1)
    rent_escalation = st.sidebar.number_input("Annual Rent Growth (%)", value=3.0, step=0.1)
    investment_return = st.sidebar.number_input("Annual Investment Return (%)", value=7.0, step=0.1)

    df = generate_financial_df(mortgage_rate, rent_escalation, investment_return)
    st.dataframe(df)

    st.subheader("📊 Numeric Descriptive Statistics")
    st.write(df.describe())

    st.subheader("❗ Missing Values")
    st.write(df.isna().sum())

    st.subheader("📈 Correlation Heatmap")
    fig, ax = plt.subplots(figsize=(8,6))
    cax = ax.matshow(df.corr(), cmap="coolwarm")
    plt.xticks(range(len(df.columns)), df.columns, rotation=45)
    plt.yticks(range(len(df.columns)), df.columns)
    fig.colorbar(cax)
    st.pyplot(fig)

# ----------------------------
# Wealth Comparison Page
# ----------------------------
elif page == "📈 Wealth Comparison":
    st.title("📊 Buy vs Rent + Invest Wealth Over Time")
    mortgage_rate = st.sidebar.number_input("Mortgage Rate (%)", value=4.0, step=0.1)
    rent_escalation = st.sidebar.number_input("Annual Rent Growth (%)", value=3.0, step=0.1)
    investment_return = st.sidebar.number_input("Annual Investment Return (%)", value=7.0, step=0.1)

    df = generate_financial_df(mortgage_rate, rent_escalation, investment_return)

    fig, ax = plt.subplots(figsize=(10,6))
    ax.plot(df["Year"], df["Net_Wealth_Buy"], label="Buy (Home Equity - Mortgage Paid)", marker='o')
    ax.plot(df["Year"], df["Net_Wealth_Rent"], label="Rent + Invest Savings", marker='o')
    ax.set_xlabel("Year")
    ax.set_ylabel("Net Wealth (RM)")
    ax.set_title("Net Wealth Comparison Over Time")
    ax.legend()
    st.pyplot(fig)

# ----------------------------
# Sensitivity Analysis Page
# ----------------------------
elif page == "⚖️ Sensitivity Analysis":
    st.title("⚖️ Sensitivity Analysis: Break-even Analysis")

    # Sliders for scenario ranges
    st.sidebar.header("Sensitivity Ranges")
    mortgage_range = st.sidebar.slider("Mortgage Rate (%)", 2.0, 8.0, (3.0, 6.0), 0.5)
    rent_range = st.sidebar.slider("Rent Escalation (%)", 0.0, 10.0, (2.0, 5.0), 0.5)
    invest_range = st.sidebar.slider("Investment Return (%)", 3.0, 12.0, (5.0, 9.0), 0.5)

    years_array = np.arange(1, years+1)
    # Create grid of scenarios
    mortgage_vals = np.arange(mortgage_range[0], mortgage_range[1]+0.1, 0.5)
    rent_vals = np.arange(rent_range[0], rent_range[1]+0.1, 0.5)
    invest_vals = np.arange(invest_range[0], invest_range[1]+0.1, 0.5)

    st.write("### 🧮 Sensitivity Analysis: Net Wealth Over Time for Different Scenarios")
    fig, ax = plt.subplots(figsize=(10,6))

    # Store break-even results
    break_even_records = []

    for m in mortgage_vals:
        for r in rent_vals:
            for i in invest_vals:
                df_scenario = generate_financial_df(m, r, i)
                ax.plot(df_scenario["Year"], df_scenario["Net_Wealth_Rent"], color='blue', alpha=0.05)
                ax.plot(df_scenario["Year"], df_scenario["Net_Wealth_Buy"], color='red', alpha=0.05)
                
                # Find break-even year (first year Rent+Invest > Buy)
                diff = df_scenario["Net_Wealth_Rent"] - df_scenario["Net_Wealth_Buy"]
                breakeven_year = df_scenario["Year"][diff > 0].min() if any(diff > 0) else np.nan
                break_even_records.append({
                    "Mortgage Rate (%)": m,
                    "Rent Escalation (%)": r,
                    "Investment Return (%)": i,
                    "Break-even Year": breakeven_year
                })

    ax.set_xlabel("Year")
    ax.set_ylabel("Net Wealth (RM)")
    ax.set_title("Sensitivity Analysis: Buy (red) vs Rent+Invest (blue)")
    st.pyplot(fig)

    st.info("💡 Interpretation: Red lines = Buy, Blue lines = Rent+Invest. Transparency shows range of outcomes. Break-even occurs when blue surpasses red.")

    # Display Break-even Summary Table
    st.subheader("📋 Break-even Year Summary")
    df_break_even = pd.DataFrame(break_even_records)
    st.dataframe(df_break_even)

    # Optional: Export break-even table as CSV
    csv = df_break_even.to_csv(index=False).encode('utf-8')
    st.download_button(
        label="⬇️ Download Break-even Table",
        data=csv,
        file_name="Break_even_Scenarios.csv",
        mime="text/csv"
    )

    st.info("💡 Interpretation: Lines show how net wealth changes with different mortgage rates, rent growth, and investment returns. Overlap indicates break-even points where renting+investing may surpass buying.")
