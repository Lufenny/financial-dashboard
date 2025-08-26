import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from itertools import cycle

st.set_page_config(page_title='Results & Interpretation', layout='wide')
st.title("📑 Results & Interpretation (Multi-Scenario)")

# --------------------------
# Upload Sensitivity CSV
# --------------------------
st.sidebar.header("Upload Sensitivity Results")
uploaded_file = st.sidebar.file_uploader(
    "Upload 'buy_vs_rent_sensitivity.csv' from Modelling page",
    type=["csv"]
)

if uploaded_file is not None:
    df_sens = pd.read_csv(uploaded_file)
    df_sens.columns = df_sens.columns.str.strip()
    
    required_cols = ["Year","MortgageRate","InvestReturn","Appreciation","RentYield",
                     "BuyEquity","RentPortfolio","Difference"]
    missing = [c for c in required_cols if c not in df_sens.columns]
    if missing:
        st.error(f"CSV is missing required columns: {missing}")
        st.stop()
else:
    st.warning("Please upload 'buy_vs_rent_sensitivity.csv' from the Modelling page to proceed.")
    st.stop()

# --------------------------
# Multi-Scenario Selection
# --------------------------
st.sidebar.header("Select Scenarios to Compare")

mortgage_options = sorted(df_sens["MortgageRate"].unique())
return_options = sorted(df_sens["InvestReturn"].unique())
appreciation_options = sorted(df_sens["Appreciation"].unique())
rent_yield_options = sorted(df_sens["RentYield"].unique())

selected_mortgages = st.sidebar.multiselect(
    "Mortgage Rate (%)", mortgage_options, default=[mortgage_options[0]]
)
selected_returns = st.sidebar.multiselect(
    "Investment Return (%)", return_options, default=[return_options[0]]
)
selected_app = st.sidebar.selectbox("Property Appreciation (%)", appreciation_options)
selected_ry = st.sidebar.selectbox("Rental Yield (%)", rent_yield_options)

if not selected_mortgages or not selected_returns:
    st.warning("Please select at least one mortgage rate and one return rate.")
    st.stop()

# --------------------------
# Filter Data
# --------------------------
df_plot = df_sens[
    (df_sens["MortgageRate"].isin(selected_mortgages)) &
    (df_sens["InvestReturn"].isin(selected_returns)) &
    (df_sens["Appreciation"] == selected_app) &
    (df_sens["RentYield"] == selected_ry)
]

if df_plot.empty:
    st.warning("No matching scenarios found for the selected filters.")
    st.stop()

# --------------------------
# Plotting Multi-Year Trajectories with Consistent Colors
# --------------------------
st.subheader("📊 Multi-Scenario Wealth Trajectories Over Time")

scenario_colors = plt.cm.tab10.colors  # Use tab10 colormap
color_cycle = cycle(scenario_colors)

fig, ax = plt.subplots(figsize=(10,6))

# Group by scenario: MortgageRate + InvestReturn
grouped = df_plot.groupby(['MortgageRate','InvestReturn'])
for (mr, ir), group in grouped:
    group_sorted = group.sort_values('Year')
    color = next(color_cycle)
    
    # Labels for legend
    label_buy = f"MR:{mr}%, IR:{ir}% Buy"
    label_rent = f"MR:{mr}%, IR:{ir}% Rent"
    
    ax.plot(group_sorted['Year'], group_sorted['BuyEquity'], marker='o', linestyle='-', color=color, label=label_buy)
    ax.plot(group_sorted['Year'], group_sorted['RentPortfolio'], marker='x', linestyle='--', color=color, label=label_rent)

ax.set_xlabel("Year")
ax.set_ylabel("Wealth (RM)")
ax.set_title(f"Wealth Accumulation Over Time | Appreciation {selected_app}%, Rent Yield {selected_ry}%")
ax.legend(fontsize=8, loc='upper left', bbox_to_anchor=(1,1))
plt.tight_layout()
st.pyplot(fig)

# --------------------------
# Show Final Values Table
# --------------------------
st.subheader("📋 Final Wealth Values (Last Year)")

final_df = df_plot[df_plot['Year']==df_plot['Year'].max()][
    ['MortgageRate','InvestReturn','BuyEquity','RentPortfolio','Difference']
].copy()

# Format values for readability
final_df['BuyEquity'] = final_df['BuyEquity'].map('{:,.0f}'.format)
final_df['RentPortfolio'] = final_df['RentPortfolio'].map('{:,.0f}'.format)
final_df['Difference'] = final_df['Difference'].map('{:,.0f}'.format)

st.dataframe(final_df.reset_index(drop=True))
