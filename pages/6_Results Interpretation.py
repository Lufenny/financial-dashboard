import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from itertools import cycle

st.set_page_config(page_title='Results & Interpretation', layout='wide')
st.title("📑 Results & Interpretation (Multi-Scenario)")

# --- Upload sensitivity CSV ---
st.sidebar.header("Upload Sensitivity Results")
uploaded_file = st.sidebar.file_uploader(
    "Upload 'buy_vs_rent_sensitivity.csv' from Modelling page",
    type=["csv"]
)

if uploaded_file is not None:
    df_sens = pd.read_csv(uploaded_file)
    # Strip spaces and ensure columns exist
    df_sens.columns = df_sens.columns.str.strip()
    required_cols = ["Year","MortgageRate","InvestReturn","Appreciation","RentYield","BuyEquity","RentPortfolio","Difference"]
    missing = [c for c in required_cols if c not in df_sens.columns]
    if missing:
        st.error(f"CSV is missing required columns: {missing}")
        st.stop()
else:
    st.warning("Please upload 'buy_vs_rent_sensitivity.csv' from the Modelling page to proceed.")
    st.stop()

# --- Multi-Scenario Selection ---
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

# --- Filter Data ---
df_plot = df_sens[
    (df_sens["MortgageRate"].isin(selected_mortgages)) &
    (df_sens["InvestReturn"].isin(selected_returns)) &
    (df_sens["Appreciation"] == selected_app) &
    (df_sens["RentYield"] == select_
