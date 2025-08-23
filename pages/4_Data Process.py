import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

st.set_page_config(page_title='Data Process', layout='wide')
st.title('⚙️ Data Processing')

# ---------------------------------------------
# Load Data
# ---------------------------------------------
@st.cache_data
def load_data(filepath="data.csv"):
    return pd.read_csv(filepath)

st.title("⚙️ Data Processing Dashboard")

# Load dataset
df = load_data()

# === Data Collection
st.header("✅ Data Collection")
years = sorted(df["Year"].unique())
st.write(f"**Total records:** {len(df)}")
st.write(f"**Years detected:** {years[0]} to {years[-1]}  \n(**{len(years)} years in total**)")

# === Data Cleansing
st.header("✅ Data Cleansing")
initial_rows = len(df)

# Drop missing
df_clean = df.dropna().copy()

# Ensure Year is numeric (same as in EDA)
if "Year" in df_clean.columns:
    df_clean["Year"] = pd.to_numeric(df_clean["Year"], errors="coerce").astype("Int64")
    df_clean = df_clean.dropna(subset=["Year"]).copy()
    df_clean["Year"] = df_clean["Year"].astype(int)

dropped = initial_rows - len(df_clean)
if dropped == 0:
    st.write("No records were removed. The dataset is already clean.")
else:
    st.write(f"{dropped} record(s) removed due to missing values or invalid years.")

with st.expander("🔎 Preview Cleaned Data"):
    st.dataframe(df_clean, use_container_width=True)

# === Summary Statistics
st.header("📊 Summary Statistics")
st.dataframe(df_clean.describe(include="all"))

# === Correlation Matrix
st.header("📈 Correlation Matrix")
corr = df_clean.corr(numeric_only=True)
st.dataframe(corr.style.background_gradient(cmap="Blues"), use_container_width=True)

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

# === Trend Chart(s)
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

# Plot each selected variable
for col in selected_columns:
    if col in filtered_df.columns:
        fig, ax = plt.subplots()
        ax.plot(filtered_df["Year"], filtered_df[col], marker="o")
        ax.set_xlabel("Year")
        ax.set_ylabel(chart_options[col])
        ax.set_title(f"{chart_options[col]} vs Year")
        st.pyplot(fig)

