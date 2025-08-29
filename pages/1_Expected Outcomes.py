import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.ticker as mtick

# --------------------------
# Streamlit Config
# --------------------------
st.set_page_config(page_title="Expected Outcomes – Baseline", layout="wide")
st.title("📌 Expected Outcomes – Baseline Comparison")

# --------------------------
# Baseline Assumptions (Sidebar)
# --------------------------
st.sidebar.header("⚙️ Baseline Assumptions")
initial_property_price = st.sidebar.number_input("Initial Property Price (RM)", value=500000, step=10000)
annual_property_growth = st.sidebar.number_input("Annual Property Growth (%)", value=3.0, step=0.5) / 100
mortgage_rate = st.sidebar.number_input("Mortgage Rate (%)", value=5.0, step=0.1) / 100
loan_term = st.sidebar.number_input("Loan Term (years)", value=30, step=5)
annual_rent = st.sidebar.number_input("Annual Rent (RM)", value=20000, step=1000)
annual_investment_return = st.sidebar.number_input("Investment Return (%)", value=6.0, step=0.5) / 100
years = st.sidebar.number_input("Projection Years", value=20, step=5)

# --------------------------
# Mortgage Calculation
# --------------------------
loan_amount = initial_property_price
monthly_rate = mortgage_rate / 12
n_payments = loan_term * 12
monthly_mortgage = loan_amount * monthly_rate / (1 - (1 + monthly_rate) ** (-n_payments))

# --------------------------
# Initialize Values
# --------------------------
loan_balance = loan_amount
invest_value = 0
records = []

# --------------------------
# Projection Loop
# --------------------------
for i in range(1, years + 1):
    # Property value growth
    value = initial_property_price * ((1 + annual_property_growth) ** i)
    
    # Loan balance amortization
    loan_balance = loan_balance * (1 + mortgage_rate) - monthly_mortgage * 12
    loan_balance = max(loan_balance, 0)
    
    # Buy scenario: equity = property value - loan balance
    buy_equity = value - loan_balance
    
    # Rent scenario: invest instead of mortgage, minus rent
    invest_value = invest_value * (1 + annual_investment_return)
    invest_value += monthly_mortgage * 12
    invest_value -= annual_rent
    
    records.append([2025 + i, value, loan_balance, buy_equity, invest_value])

# --------------------------
# Convert to DataFrame
# --------------------------
df_baseline = pd.DataFrame(records, columns=["Year", "PropertyValue", "MortgageBalance", "BuyWealth", "RentWealth"])

# --------------------------
# Format Table with RM
# --------------------------
df_display = df_baseline.copy()
df_display["PropertyValue"] = df_display["PropertyValue"].apply(lambda x: f"RM {x:,.0f}")
df_display["MortgageBalance"] = df_display["MortgageBalance"].apply(lambda x: f"RM {x:,.0f}")
df_display["BuyWealth"] = df_display["BuyWealth"].apply(lambda x: f"RM {x:,.0f}")
df_display["RentWealth"] = df_display["RentWealth"].apply(lambda x: f"RM {x:,.0f}")

st.subheader("📊 Model Baseline Outcomes (Illustrative)")
st.dataframe(df_display)

# --------------------------
# Plot Chart
# --------------------------
fig, ax = plt.subplots(figsize=(12, 5))

ax.plot(df_baseline["Year"], df_baseline["BuyWealth"], label="Buy (Property Equity)", color="blue", marker="o")
ax.plot(df_baseline["Year"], df_baseline["RentWealth"], label="Rent & Invest", color="green", marker="o")

ax.set_xlabel("Year")
ax.set_ylabel("Wealth (RM)")
ax.set_title("Expected Outcomes: Buy vs Rent")
ax.legend()

# Format Y-axis with RM
ax.yaxis.set_major_formatter(mtick.StrMethodFormatter("RM {x:,.0f}"))

st.pyplot(fig)
