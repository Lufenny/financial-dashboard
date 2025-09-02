"""
========================================
Buy vs Rent + EPF Modelling Script (Clean Version)
========================================

Outputs:
- Yearly property value, mortgage balance, buy wealth, EPF wealth
- Annual rent and cumulative rent
- CAGR for buy and EPF
- Break-even year when Buy Wealth exceeds EPF Wealth
- Sensitivity analysis for key parameters
"""

# --------------------------
# 1. Import Libraries
# --------------------------
import pandas as pd
import numpy as np

# --------------------------
# 2. Helper Functions
# --------------------------
def calculate_monthly_mortgage(loan_amount, annual_rate, years):
    """
    Calculate monthly mortgage payment using standard annuity formula.
    """
    r = annual_rate / 12
    n = years * 12
    return loan_amount * (r * (1 + r)**n) / ((1 + r)**n - 1) if r > 0 else loan_amount / n


def project_buy_rent(P, loan_amount, mortgage_rate, mortgage_term,
                     property_growth, epf_rate, rent_yield, years,
                     down_payment=0, custom_rent=None):
    """
    Projects Buy vs Rent + EPF wealth over time.
    Returns a DataFrame with yearly values.
    """
    monthly_PMT = calculate_monthly_mortgage(loan_amount, mortgage_rate, mortgage_term)
    
    property_values = [P]
    mortgage_balances = [loan_amount]
    buy_wealth = [down_payment]
    epf_wealth = [down_payment]
    rents = []
    cum_rent = []

    # Initial rent
    annual_rent = custom_rent if custom_rent is not None else P * rent_yield
    rents.append(annual_rent)
    cum_rent.append(annual_rent)

    # Yearly projection
    for t in range(1, years + 1):
        # Property growth
        new_property_value = property_values[-1] * (1 + property_growth)
        property_values.append(new_property_value)

        # Mortgage balance
        interest_payment = mortgage_balances[-1] * mortgage_rate
        principal_payment = monthly_PMT * 12 - interest_payment
        new_balance = max(0, mortgage_balances[-1] - principal_payment)
        mortgage_balances.append(new_balance)

        # Buy wealth
        buy_wealth.append(new_property_value - new_balance)

        # Rent
        annual_rent = custom_rent if custom_rent is not None else new_property_value * rent_yield
        rents.append(annual_rent)
        cum_rent.append(cum_rent[-1] + annual_rent)

        # EPF wealth from leftover cash
        investable = max(0, monthly_PMT*12 - annual_rent)
        epf_wealth.append(epf_wealth[-1] * (1 + epf_rate/12)**12 + investable)

    # CAGR
    buy_cagr = [( (buy_wealth[i]/buy_wealth[0])**(1/i) - 1 if i>0 else 0) for i in range(len(buy_wealth))]
    epf_cagr = [( (epf_wealth[i]/epf_wealth[0])**(1/i) - 1 if i>0 else 0) for i in range(len(epf_wealth))]

    df = pd.DataFrame({
        "Year": np.arange(0, years + 1),
        "Property Value": property_values,
        "Mortgage Balance": mortgage_balances,
        "Buy Wealth (RM)": buy_wealth,
        "EPF Wealth (RM)": epf_wealth,
        "Annual Rent": rents,
        "Cumulative Rent": cum_rent,
        "Buy CAGR": buy_cagr,
        "EPF CAGR": epf_cagr
    })
    return df


# --------------------------
# 3. Baseline Assumptions
# --------------------------
purchase_price = 500_000
down_payment = 100_000
loan_amount = purchase_price - down_payment
mortgage_rate = 0.04
mortgage_term = 30
property_growth = 0.05
epf_rate = 0.06
rent_yield = 0.04
projection_years = 30
custom_rent = None  # Optional, e.g., 20000

# --------------------------
# 4. Run Projection
# --------------------------
df_results = project_buy_rent(
    P=purchase_price,
    loan_amount=loan_amount,
    mortgage_rate=mortgage_rate,
    mortgage_term=mortgage_term,
    property_growth=property_growth,
    epf_rate=epf_rate,
    rent_yield=rent_yield,
    years=projection_years,
    down_payment=down_payment,
    custom_rent=custom_rent
)

# --------------------------
# 5. Break-even Analysis
# --------------------------
break_even_year = next((row.Year for i,row in df_results.iterrows() if row["Buy Wealth (RM)"] > row["EPF Wealth (RM)"]), None)

# --------------------------
# 6. Summary Output
# --------------------------
final_buy = df_results["Buy Wealth (RM)"].iloc[-1]
final_epf = df_results["EPF Wealth (RM)"].iloc[-1]

print("=== Buy vs Rent + EPF Modelling Results ===")
print(f"Projection Years: {projection_years}")
print(f"Final Buy Wealth (RM): {final_buy:,.0f}")
print(f"Final EPF Wealth (RM): {final_epf:,.0f}")
print(f"Break-even Year: {break_even_year if break_even_year else 'No break-even'}")

# Optional: first 10 years
print(df_results.head(10))

# --------------------------
# 7. Sensitivity Analysis
# --------------------------
sensitivity_pct = 0.10  # ±10%
params = {
    "Mortgage Rate": mortgage_rate,
    "Property Growth": property_growth,
    "EPF Rate": epf_rate,
    "Rent Yield": rent_yield
}

sensitivity_results = []

for param_name, base_value in params.items():
    low = base_value * (1 - sensitivity_pct)
    high = base_value * (1 + sensitivity_pct)

    # Build kwargs for low/high scenario
    kwargs_base = dict(
        P=purchase_price,
        loan_amount=loan_amount,
        mortgage_rate=mortgage_rate,
        mortgage_term=mortgage_term,
        property_growth=property_growth,
        epf_rate=epf_rate,
        rent_yield=rent_yield,
        years=projection_years,
        down_payment=down_payment,
        custom_rent=custom_rent
    )

    # Low scenario
    kwargs_low = kwargs_base.copy()
    kwargs_low[param_name.replace(" ", "_").lower()] = low
    df_low = project_buy_rent(**kwargs_low)
    final_buy_low = df_low["Buy Wealth (RM)"].iloc[-1]
    final_epf_low = df_low["EPF Wealth (RM)"].iloc[-1]

    # High scenario
    kwargs_high = kwargs_base.copy()
    kwargs_high[param_name.replace(" ", "_").lower()] = high
    df_high = project_buy_rent(**kwargs_high)
    final_buy_high = df_high["Buy Wealth (RM)"].iloc[-1]
    final_epf_high = df_high["EPF Wealth (RM)"].iloc[-1]

    # Store results
    sensitivity_results.append({
        "Parameter": param_name,
        "Buy Low": final_buy_low,
        "Buy High": final_buy_high,
        "Buy Impact": final_buy_high - final_buy_low,
        "EPF Low": final_epf_low,
        "EPF High": final_epf_high,
        "EPF Impact": final_epf_high - final_epf_low
    })

df_sensitivity = pd.DataFrame(sensitivity_results)

# Identify most sensitive parameters
most_sensitive_buy = df_sensitivity.loc[df_sensitivity["Buy Impact"].idxmax()]
most_sensitive_epf = df_sensitivity.loc[df_sensitivity["EPF Impact"].idxmax()]

print("\n=== Sensitivity Analysis (±10%) ===")
print(df_sensitivity)
print(f"\nMost sensitive factor for Buy Wealth: {most_sensitive_buy['Parameter']} "
      f"(Impact: RM {most_sensitive_buy['Buy Impact']:,.0f})")
print(f"Most sensitive factor for EPF Wealth: {most_sensitive_epf['Parameter']} "
      f"(Impact: RM {most_sensitive_epf['EPF Impact']:,.0f})")
