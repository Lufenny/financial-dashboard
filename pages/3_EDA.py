import streamlit as st
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import requests
from wordcloud import WordCloud
from collections import Counter
import nltk
from nltk.corpus import stopwords
from nltk import word_tokenize, ngrams
from nltk.stem import WordNetLemmatizer
import os

st.set_page_config(page_title='EDA', layout='wide')
st.title('🔎 Exploratory Data Analysis (EDA)')

# =========================
# Load Data
# =========================
data = {
    "Year": list(range(2010, 2026)),
    "OPR_avg": [2.47, 3.11, 3.00, 3.00, 3.12, 3.25, 3.13, 3.00, 3.00, 3.00,
                2.11, 1.75, 2.15, 2.92, 3.00, 2.88],
    "EPF": [5.80, 6.00, 6.15, 6.35, 6.75, 6.40, 5.70, 6.90, 6.15, 5.45,
            5.20, 6.10, 5.35, 5.50, 6.30, None],
    "PriceGrowth": [7.86, 11.22, 14.31, 9.35, 8.69, 6.47, 6.97, 6.13, 2.52, 1.79,
                    1.21, 1.89, 3.90, 3.85, 4.43, 2.00],
    "RentYield": [3.5, 3.6, 3.7, 3.8, 3.9, 4.0, 4.1, 4.2, 4.3, 4.4,
                  4.5, 4.6, 4.5, 4.6, 4.6, 4.6]
}
df = pd.DataFrame(data)

# =========================
# Streamlit UI
# =========================
st.set_page_config(page_title="Buy vs Rent EDA", layout="wide")
st.title("🏡 Buy vs Rent Analysis (2010–2025)")
st.markdown("Exploratory Data Analysis of **Malaysia’s housing market, EPF returns, and rental yields**.")

# =========================
# Chart 1: OPR vs EPF Dividend
# =========================
st.subheader("📉 OPR vs 📈 EPF Dividend Rates")
fig, ax = plt.subplots()
ax.plot(df["Year"], df["OPR_avg"], marker="o", label="OPR (Bank Negara)")
ax.plot(df["Year"], df["EPF"], marker="o", label="EPF Dividend")
ax.set_ylabel("Percentage (%)")
ax.legend()
st.pyplot(fig)

with st.expander("🔎 Analyst Notes: OPR vs EPF"):
    st.markdown("""
    - **EPF consistently outperforms OPR** — average EPF dividend (~6.0%) is more than double the average OPR (~2.8%).  
    - This means savings in EPF historically delivered **higher and safer returns** than paying down loans.  
    - **Implication:** Unless property grows faster than EPF, saving remains a strong alternative.
    """)

# =========================
# Chart 2: Property Price Growth
# =========================
st.subheader("🏠 Property Price Growth (%)")
fig, ax = plt.subplots()
ax.bar(df["Year"], df["PriceGrowth"], color="skyblue")
ax.set_ylabel("Price Growth (%)")
st.pyplot(fig)

with st.expander("🔎 Analyst Notes: Property Price Growth"):
    st.markdown("""
    - Early **2010s saw double-digit growth**, peaking at +14% in 2012.  
    - After 2018, growth slowed sharply, dipping below 2% in 2019–2021 (COVID impact).  
    - **Implication:** Property investment became less lucrative in recent years, with appreciation stabilizing.  
    """)

# =========================
# Chart 3: Rental Yield Trend
# =========================
st.subheader("📊 Rental Yield Trend")
fig, ax = plt.subplots()
ax.plot(df["Year"], df["RentYield"], marker="s", color="green")
ax.set_ylabel("Rental Yield (%)")
st.pyplot(fig)

with st.expander("🔎 Analyst Notes: Rental Yield"):
    st.markdown("""
    - Yields steadily rose from ~3.5% (2010) to ~4.6% (2025).  
    - As property growth slowed, **renting became more attractive**, especially post-2018.  
    - **Implication:** Renters may find better value now, as rental returns grow while capital appreciation slows.
    """)

# =========================
# Summary Section
# =========================
st.subheader("📌 Overall Insights")
with st.expander("Click to expand summary"):
    st.markdown("""
    - **EPF vs Property**: EPF outperformed loan costs, making savings relatively stronger than property debt.  
    - **Property Growth**: Explosive in the 2010s, but slowed after 2018, nearing stagnation during COVID.  
    - **Rent Yields**: Consistently rising, suggesting renting is comparatively more favorable now.  

    👉 **Analyst View:**  
    In the 2010s, buying property was compelling due to rapid growth.  
    Post-2018, with slower growth and rising yields, **renting became more financially sensible**.
    """)
