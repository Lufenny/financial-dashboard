import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

st.set_page_config(page_title='Expected Outcomes', layout='wide')
st.title("📌 Expected Outcomes – Baseline Comparison")

# --- Upload baseline dataset ---
st.sidebar.header("Upload Baseline Data")
uploaded_file = st.sidebar.file_uploader(
    "Upload 'baseline_outcomes.csv' (default modelling output)",
    type=["csv"]
)

if uploaded_file is not None:
    df = pd.read_csv(uploaded_file)
else:
    st.warning("Please upload 'baseline_outcomes.csv' to proceed.")
    st.stop()

# --- Show dataset preview ---
st.subheader("📊 Baseline Dataset")
st.dataframe(df.head())

# --- Wealth Comparison ---
st.subheader("💰 Buy vs Rent & Invest (Baseline)")

fig, ax = plt.subplots(figsize=(10, 5))
ax.plot(df["Year"], df["BuyWealth"], label="Buy (Property)", color="blue", marker="o")
ax.plot(df["Year"], df["RentWealth"], label="Rent & Invest", color="green", marker="o")
ax.set_xlabel("Year")
ax.set_ylabel("Value (RM)")
ax.set_title("Baseline Wealth Projection – Buy vs Rent & Invest")
ax.grid(True, linestyle="--", alpha=0.5)
ax.legend()
st.pyplot(fig)

# --- Key Insights ---
st.header("📝 Interpretation of Expected Outcomes")
st.write("""
- This chart shows the **baseline projection** using default assumptions (e.g., property appreciation ≈2%, EPF returns ≈5%).  
- The **blue line** represents wealth accumulation through homeownership, while the **green line** shows the rent-and-invest strategy.  
- At baseline, buying builds wealth primarily through equity appreciation, while renting relies on consistent investment returns.  
- This baseline view sets the stage for **scenario and sensitivity analyses** that explore how outcomes shift under alternative assumptions.
""")

# --- Download Data ---
csv_bytes = df.to_csv(index=False).encode("utf-8")
st.download_button(
    "⬇️ Download Baseline Outcomes CSV",
    data=csv_bytes,
    file_name="expected_outcomes_baseline.csv",
    mime="text/csv"
)
