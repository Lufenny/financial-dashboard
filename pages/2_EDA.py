import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from fpdf import FPDF
import io
import re
from collections import Counter
from wordcloud import WordCloud
import nltk
from nltk.corpus import stopwords
import os

# ----------------------------
# Streamlit App Config
# ----------------------------
st.set_page_config(page_title="Buy vs Rent EDA Dashboard", layout="wide")
st.sidebar.title("🏡 Navigation")
page = st.sidebar.radio("Go to:", ["📊 EDA Overview", "📈 Wealth Comparison", "⚖️ Sensitivity Analysis", "☁️ WordCloud"])

# ----------------------------
# Base Financial Inputs
# ----------------------------
st.sidebar.header("💰 Financial Inputs")
mortgage_term = st.sidebar.number_input("Mortgage Term (years)", value=30, step=1)
property_price = st.sidebar.number_input("Property Price (RM)", value=500000, step=1000)
monthly_rent = st.sidebar.number_input("Monthly Rent (RM)", value=1500, step=100)
years = st.sidebar.number_input("Analysis Period (Years)", value=30, step=1)

# ----------------------------
# Generate Dataset Function
# ----------------------------
def generate_financial_df(mortgage_rate, rent_escalation, investment_return):
    df = pd.DataFrame({"Year": np.arange(1, years + 1)})
    r = mortgage_rate / 100 / 12
    n = mortgage_term * 12
    monthly_payment = property_price * r * (1 + r)**n / ((1 + r)**n - 1)
    df["Monthly_Mortgage"] = monthly_payment
    df["Cumulative_Mortgage_Paid"] = df["Monthly_Mortgage"].cumsum() * 12 / 12
    df["Home_Equity"] = property_price * (df["Year"] / mortgage_term).clip(upper=1)
    df["Annual_Rent"] = monthly_rent * 12 * (1 + rent_escalation/100)**(df["Year"]-1)
    df["Rent_Saved"] = df["Monthly_Mortgage"]*12 - df["Annual_Rent"]
    df["Rent_Saved"] = df["Rent_Saved"].clip(lower=0)
    df["Investment_Value"] = df["Rent_Saved"].cumsum() * ((1 + investment_return/100) ** (df["Year"]-1))
    df["Net_Wealth_Buy"] = df["Home_Equity"] - df["Cumulative_Mortgage_Paid"]
    df["Net_Wealth_Rent"] = df["Investment_Value"]
    return df

# ----------------------------
# EDA Overview Page
# ----------------------------
if page == "📊 EDA Overview":
    st.title("🔎 Dataset Preview & Stats")
    mortgage_rate = st.sidebar.number_input("Mortgage Rate (%)", value=4.0, step=0.1)
    rent_escalation = st.sidebar.number_input("Annual Rent Growth (%)", value=3.0, step=0.1)
    investment_return = st.sidebar.number_input("Annual Investment Return (%)", value=7.0, step=0.1)

    df = generate_financial_df(mortgage_rate, rent_escalation, investment_return)
    st.dataframe(df)

    st.subheader("📊 Numeric Descriptive Statistics")
    st.write(df.describe())

    st.subheader("❗ Missing Values")
    st.write(df.isna().sum())

    st.subheader("📈 Correlation Heatmap")
    fig, ax = plt.subplots(figsize=(8,6))
    cax = ax.matshow(df.corr(), cmap="coolwarm")
    plt.xticks(range(len(df.columns)), df.columns, rotation=45)
    plt.yticks(range(len(df.columns)), df.columns)
    fig.colorbar(cax)
    st.pyplot(fig)

# ----------------------------
# Wealth Comparison Page
# ----------------------------
elif page == "📈 Wealth Comparison":
    st.title("📊 Buy vs Rent + Invest Wealth Over Time")
    mortgage_rate = st.sidebar.number_input("Mortgage Rate (%)", value=4.0, step=0.1)
    rent_escalation = st.sidebar.number_input("Annual Rent Growth (%)", value=3.0, step=0.1)
    investment_return = st.sidebar.number_input("Annual Investment Return (%)", value=7.0, step=0.1)

    df = generate_financial_df(mortgage_rate, rent_escalation, investment_return)

    fig, ax = plt.subplots(figsize=(10,6))
    ax.plot(df["Year"], df["Net_Wealth_Buy"], label="Buy (Home Equity - Mortgage Paid)", marker='o')
    ax.plot(df["Year"], df["Net_Wealth_Rent"], label="Rent + Invest Savings", marker='o')
    ax.set_xlabel("Year")
    ax.set_ylabel("Net Wealth (RM)")
    ax.set_title("Net Wealth Comparison Over Time")
    ax.legend()
    st.pyplot(fig)

# ----------------------------
# Sensitivity Analysis Page
# ----------------------------
elif page == "⚖️ Sensitivity Analysis":
    st.title("⚖️ Sensitivity Analysis: Break-even Analysis")
    st.sidebar.header("Sensitivity Ranges")
    mortgage_range = st.sidebar.slider("Mortgage Rate (%)", 2.0, 8.0, (3.0, 6.0), 0.5)
    rent_range = st.sidebar.slider("Rent Escalation (%)", 0.0, 10.0, (2.0, 5.0), 0.5)
    invest_range = st.sidebar.slider("Investment Return (%)", 3.0, 12.0, (5.0, 9.0), 0.5)

    mortgage_vals = np.arange(mortgage_range[0], mortgage_range[1]+0.1, 0.5)
    rent_vals = np.arange(rent_range[0], rent_range[1]+0.1, 0.5)
    invest_vals = np.arange(invest_range[0], invest_range[1]+0.1, 0.5)

    fig, ax = plt.subplots(figsize=(10,6))
    break_even_records = []

    for m in mortgage_vals:
        for r in rent_vals:
            for i in invest_vals:
                df_scenario = generate_financial_df(m, r, i)
                ax.plot(df_scenario["Year"], df_scenario["Net_Wealth_Rent"], color='blue', alpha=0.05)
                ax.plot(df_scenario["Year"], df_scenario["Net_Wealth_Buy"], color='red', alpha=0.05)
                diff = df_scenario["Net_Wealth_Rent"] - df_scenario["Net_Wealth_Buy"]
                breakeven_year = df_scenario["Year"][diff > 0].min() if any(diff > 0) else np.nan
                break_even_records.append({
                    "Mortgage Rate (%)": m,
                    "Rent Escalation (%)": r,
                    "Investment Return (%)": i,
                    "Break-even Year": breakeven_year
                })

    ax.set_xlabel("Year")
    ax.set_ylabel("Net Wealth (RM)")
    ax.set_title("Sensitivity Analysis: Buy (red) vs Rent+Invest (blue)")
    st.pyplot(fig)

    df_break_even = pd.DataFrame(break_even_records)
    fastest_break_even = df_break_even["Break-even Year"].min()
    no_break_even_count = df_break_even["Break-even Year"].isna().sum()

    st.subheader("📋 Break-even Year Summary")
    st.write(f"✅ Fastest Break-even Year: {int(fastest_break_even)}")
    st.write(f"⚠️ Number of scenarios with NO break-even: {no_break_even_count}")
    st.dataframe(df_break_even.style.apply(
        lambda x: ['background-color: lightgreen' if x['Break-even Year']==fastest_break_even else '' for _ in x],
        axis=1
    ))

    csv = df_break_even.to_csv(index=False).encode('utf-8')
    st.download_button(
        label="⬇️ Download Break-even Table",
        data=csv,
        file_name="Break_even_Scenarios.csv",
        mime="text/csv"
    )

# ----------------------------
# WordCloud Page
# ----------------------------
elif page == "☁️ WordCloud":
    st.title("📝 Text Analysis & WordCloud")
    
    try:
        stopwords.words("english")
    except LookupError:
        nltk.download('punkt')
        nltk.download('stopwords')

    uploaded_file = st.file_uploader("Upload your CSV with 'Content' column", type=["csv"], key="wc")
    if uploaded_file is not None:
        df_text = pd.read_csv(uploaded_file)
    elif os.path.exists("Content.csv"):
        df_text = pd.read_csv("Content.csv")
    else:
        st.error("❌ No dataset found.")
        st.stop()

    if "Content" not in df_text.columns:
        st.error("CSV must have a 'Content' column")
    else:
        text_data = " ".join(df_text["Content"].dropna().astype(str))
        tokens = re.findall(r"\b[a-zA-Z]+\b", text_data.lower())
        stop_words = set(stopwords.words("english"))
        cleaned_tokens = [w for w in tokens if w not in stop_words]

        wordcloud = WordCloud(width=800, height=400, background_color="white").generate(" ".join(cleaned_tokens))
        word_freq = Counter(cleaned_tokens).most_common(15)
        words, counts = zip(*word_freq) if word_freq else ([], [])

        col1, col2 = st.columns(2)
        with col1:
            st.subheader("☁️ WordCloud")
            fig_wc, ax_wc = plt.subplots(figsize=(8,5))
            ax_wc.imshow(wordcloud, interpolation="bilinear")
            ax_wc.axis("off")
            st.pyplot(fig_wc)
        with col2:
            st.subheader("📊 Top Words Frequency")
            fig_bar, ax_bar = plt.subplots(figsize=(6,5))
            if words:
                ax_bar.barh(words[::-1], counts[::-1])
                ax_bar.set_xlabel("Count")
                ax_bar.set_ylabel("Word")
            else:
                ax_bar.text(0.5,0.5,"No words found",ha="center")
            st.pyplot(fig_bar)
