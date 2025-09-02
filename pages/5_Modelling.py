"""
========================================
Buy vs Rent + EPF Modelling Script
========================================

Outputs:
- Yearly property value, mortgage balance, buy wealth, EPF wealth
- Annual rent and cumulative rent
- CAGR for buy and EPF
- Break-even year when Buy Wealth exceeds EPF Wealth
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


def project_buy_rent(
    P,
    loan_amount,
    mortgage_rate,
    mortgage_term,
    property_growth,
    epf_rate,
    rent_yield,
    years,
    down_payment=0,
    custom_rent=None
):
    """
    Projects Buy vs Rent + EPF wealth over time.
    
    Parameters:
    - P: Property purchase price
    - loan_amount: Mortgage principal
    - mortgage_rate: Annual mortgage interest rate
    - mortgage_term: Loan term in years
    - property_growth: Annual property appreciation rate
    - epf_rate: Annual EPF return rate
    - rent_yield: Annual rent as % of property value
    - years: Projection period in years
    - down_payment: Initial down payment
    - custom_rent: Optional fixed rent
    
    Returns:
    - DataFrame with yearly values: Buy Wealth, EPF Wealth, Property Value, Mortgage Balance, Rent, CAGR
    """
    
    monthly_PMT = calculate_monthly_mortgage(loan_amount, mortgage_rate, mortgage_term)
    
    # Initialize lists for projections
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

    # Yearly projection loop
    for t in range(1, years + 1):
        # Property value growth
        new_property_value = property_values[-1] * (1 + property_growth)
        property_values.append(new_property_value)

        # Mortgage balance update
        interest_payment = mortgage_balances[-1] * mortgage_rate
        principal_payment = monthly_PMT * 12 - interest_payment
        new_balance = max(0, mortgage_balances[-1] - principal_payment)
        mortgage_balances.append(new_balance)

        # Buy wealth (equity)
        buy_wealth.append(new_property_value - new_balance)

        # Rent & cumulative rent
        annual_rent = custom_rent if custom_rent is not None else new_property_value * rent_yield
        rents.append(annual_rent)
        cum_rent.append(cum_rent[-1] + annual_rent)

        # EPF investment from leftover cash (monthly compounding)
        investable = max(0, monthly_PMT*12 - annual_rent)
        epf_wealth.append(epf_wealth[-1] * (1 + epf_rate/12)**12 + investable)

    # CAGR calculation
    buy_cagr = [( (buy_wealth[i]/buy_wealth[0])**(1/i) - 1 if i>0 else 0) for i in range(len(buy_wealth))]
    epf_cagr = [( (epf_wealth[i]/epf_wealth[0])**(1/i) - 1 if i>0 else 0) for i in range(len(epf_wealth))]

    # Create DataFrame with results
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
    down_payment=down_payment
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

# Optional: view full projection table
print(df_results.head(10))  # First 10 years
