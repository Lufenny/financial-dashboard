import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import os

st.set_page_config(page_title='Data Process', layout='wide')

# ---------------------------------------------
# Load Data (Uploader + GitHub fallback)
# ---------------------------------------------
@st.cache_data
def load_data(path="https://raw.githubusercontent.com/Lufenny/financial-dashboard/main/Data.csv"):
    return pd.read_csv(path)

st.title("⚙️ Data Processing Dashboard")

uploaded_file = st.file_uploader("Upload your dataset (CSV)", type=["csv"])
if uploaded_file is not None:
    df = pd.read_csv(uploaded_file)
elif os.path.exists("Data.csv"):
    df = pd.read_csv("Data.csv")
else:
    df = load_data()

# === Data Collection
st.header("✅ Data Collection")
years = sorted(df["Year"].dropna().unique())
st.write(f"**Total records:** {len(df)}")
st.write(f"**Years detected:** {years[0]} to {years[-1]}  \n(**{len(years)} years in total**)")

# === Data Cleansing
st.header("✅ Data Cleansing")
initial_rows = len(df)

# Track missing before cleaning
missing_summary = df.isnull().sum()
missing_cols = missing_summary[missing_summary > 0]

# Drop missing
df_clean = df.dropna().copy()

# Ensure Year is numeric
if "Year" in df_clean.columns:
    df_clean["Year"] = pd.to_numeric(df_clean["Year"], errors="coerce").astype("Int64")
    df_clean = df_clean.dropna(subset=["Year"]).copy()
    df_clean["Year"] = df_clean["Year"].astype(int)

dropped = initial_rows - len(df_clean)
if dropped == 0:
    st.write("No records were removed. The dataset is already clean.")
else:
    st.write(f"{dropped} record(s) removed due to missing values or invalid years.")
    if not missing_cols.empty:
        st.write("Columns with missing values before cleaning:")
        st.dataframe(missing_cols)

with st.expander("🔎 Preview Cleaned Data"):
    st.dataframe(df_clean, use_container_width=True)

# === Summary Statistics
st.header("📊 Summary Statistics")

st.subheader("Numeric Variables")
st.dataframe(df_clean.describe(include=[np.number]))

st.subheader("Categorical Variables")
cat_cols = df_clean.select_dtypes(include=["object"]).columns
if len(cat_cols) > 0:
    st.dataframe(df_clean[cat_cols].describe())
else:
    st.write("No categorical variables detected.")

# === Correlation Matrix (heatmap style, like EDA)
st.header("📈 Correlation Matrix")
corr = df_clean.corr(numeric_only=True)
if corr.empty:
    st.write("No numeric columns available to compute correlations.")
else:
    fig, ax = plt.subplots(figsize=(8, 6))
    im = ax.imshow(corr.values, cmap="Blues", vmin=-1, vmax=1)
    ax.set_xticks(np.arange(len(corr.columns)))
    ax.set_yticks(np.arange(len(corr.index)))
    ax.set_xticklabels(corr.columns, rotation=45, ha="right")
    ax.set_yticklabels(corr.index)

    # Annotate with contrast
    for i in range(len(corr.index)):
        for j in range(len(corr.columns)):
            val = corr.values[i, j]
            color = "white" if abs(val) > 0.5 else "black"
            ax.text(j, i, f"{val:.2f}", ha="center", va="center", fontsize=8, color=color)

    fig.colorbar(im, ax=ax, fraction=0.046, pad=0.04)
    ax.set_title("Correlation Matrix")
    plt.tight_layout()
    st.pyplot(fig)

# === Download full CSV
csv = df_clean.to_csv(index=False).encode("utf-8")
st.download_button(
    "⬇️ Download Cleaned CSV",
    data=csv,
    file_name="cleaned_data.csv",
    mime="text/csv"
)

# === Year Range Filter
st.header("📅 Year Range Filter")
min_year, max_year = st.slider(
    "Select Year Range:",
    min_value=int(years[0]),
    max_value=int(years[-1]),
    value=(int(years[0]), int(years[-1])),
    step=1
)
filtered_df = df_clean[(df_clean["Year"] >= min_year) & (df_clean["Year"] <= max_year)]

# === Trend Chart(s) with basic observations
st.header("📉 Trend Chart(s)")

chart_options = {
    "OPR_avg": "OPR (%)",
    "PriceGrowth": "Price Growth (%)",
    "RentYield": "Rental Yield (%)",
    "EPF": "EPF (%)"
}

selected_columns = st.multiselect(
    "Select variables to plot against Year:",
    options=list(chart_options.keys()),
    default=list(chart_options.keys()),
    format_func=lambda x: chart_options[x]
)

for col in selected_columns:
    if col in filtered_df.columns:
        fig, ax = plt.subplots()
        ax.plot(filtered_df["Year"], filtered_df[col], marker="o")
        ax.set_xlabel("Year")
        ax.set_ylabel(chart_options[col])
        ax.set_title(f"{chart_options[col]} vs Year")
        st.pyplot(fig)

        # Add observation (first vs last value)
        start_val, end_val = filtered_df[col].iloc[0], filtered_df[col].iloc[-1]
        st.write(f"**Observation:** {chart_options[col]} changed from {start_val:.2f} to {end_val:.2f} between {filtered_df['Year'].iloc[0]} and {filtered_df['Year'].iloc[-1]}.")
