# --- Upload sensitivity CSV ---
uploaded_file = st.sidebar.file_uploader(
    "Upload 'buy_vs_rent_sensitivity.csv' from Modelling page",
    type=["csv"]
)

if uploaded_file is not None:
    df_sens = pd.read_csv(uploaded_file)
else:
    st.warning("Please upload 'buy_vs_rent_sensitivity.csv' from the Modelling page to proceed.")
    st.stop()

# --- Multi-Scenario Selection ---
mortgage_options = sorted(df_sens["MortgageRate"].unique())
return_options = sorted(df_sens["InvestReturn"].unique())

selected_mortgages = st.sidebar.multiselect("Mortgage Rate (%)", mortgage_options, default=[mortgage_options[0]])
selected_returns = st.sidebar.multiselect("Investment Return (%)", return_options, default=[return_options[0]])

if not selected_mortgages or not selected_returns:
    st.warning("Please select at least one mortgage rate and one return rate.")
    st.stop()

# --- Filter Data ---
df_plot = df_sens[
    df_sens["MortgageRate"].isin(selected_mortgages) &
    df_sens["InvestReturn"].isin(selected_returns)
]

# --- Plot Multi-Scenario Curves ---
fig, ax = plt.subplots(figsize=(12, 6))
for mr in selected_mortgages:
    for r in selected_returns:
        scenario = df_plot[(df_plot["MortgageRate"]==mr) & (df_plot["InvestReturn"]==r)]
        if scenario.empty: continue
        ax.plot(scenario["Year"], scenario["RentPortfolio"], label=f"Rent @ {r}% | Mort {mr}%", linestyle="solid")
        ax.plot(scenario["Year"], scenario["BuyEquity"], linestyle="dotted", alpha=0.7, color=ax.lines[-1].get_color())
