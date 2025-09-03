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
import requests
from bs4 import BeautifulSoup
import time

# ----------------------------
# NLTK Setup
# ----------------------------
try:
    stopwords.words("english")
except LookupError:
    nltk.download('punkt')
    nltk.download('stopwords')

# ----------------------------
# Streamlit Config
# ----------------------------
st.set_page_config(page_title="Buy vs Rent Dashboard", layout="wide")
st.sidebar.title("🏡 Navigation")
page = st.sidebar.radio("Go to:", [
    "📊 EDA Overview", 
    "📈 Wealth Comparison", 
    "⚖️ Sensitivity Analysis", 
    "☁️ WordCloud",
    "🔗 Combined Insights"
])

# ----------------------------
# Cached Financial Data Function
# ----------------------------
@st.cache_data
def generate_financial_df(mortgage_rate, rent_escalation, investment_return, years=30, mortgage_term=30, property_price=500000, monthly_rent=1500):
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
# Cached WordCloud Function
# ----------------------------
@st.cache_data
def generate_wordcloud(text, stop_words=None, width=800, height=400):
    if stop_words is None:
        stop_words = set(stopwords.words("english"))
    tokens = re.findall(r"\b[a-zA-Z]+\b", text.lower())
    cleaned_tokens = [w for w in tokens if w not in stop_words]
    wc = WordCloud(width=width, height=height, background_color="white").generate(" ".join(cleaned_tokens))
    word_freq = Counter(cleaned_tokens).most_common(20)
    return wc, word_freq

# ----------------------------
# Google Search Web Scraping Function
# ----------------------------
@st.cache_data(show_spinner=True)
def fetch_google_articles_safe(query="Rent vs Buy", max_articles=5, delay=1):
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}
    search_url = f"https://www.google.com/search?q={query.replace(' ','+')}&num={max_articles}"
    all_text = ""
    try:
        response = requests.get(search_url, headers=headers, timeout=5)
        soup = BeautifulSoup(response.text, "html.parser")
        links = []
        for g in soup.find_all('a'):
            href = g.get('href')
            if href and href.startswith("/url?q="):
                url = href.split("/url?q=")[1].split("&")[0]
                if "webcache" not in url:
                    links.append(url)
        links = links[:max_articles]

        for url in links:
            try:
                resp = requests.get(url, headers=headers, timeout=5)
                page_soup = BeautifulSoup(resp.text, "html.parser")
                paragraphs = [p.get_text() for p in page_soup.find_all("p")]
                all_text += " ".join(paragraphs)
                time.sleep(delay)
            except Exception as e:
                print(f"Skipping URL {url} due to error: {e}")
    except Exception as e:
        print(f"Google search failed: {e}")

    all_text = re.sub(r'\s+', ' ', all_text)
    if not all_text.strip():
        all_text = "No text could be fetched from the web. Try another source or check your internet connection."
    return all_text

# ----------------------------
# PDF Export Function
# ----------------------------
def save_combined_pdf(df_numeric, wordcloud=None, word_freq=None, include_wealth=True, include_wordcloud=True, include_topwords=True):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", "B", 16)
    pdf.cell(0, 10, "Combined Insights Report", ln=True, align="C")
    temp_files = []

    if include_wealth:
        pdf.set_font("Arial", "B", 14)
        pdf.ln(10)
        pdf.cell(0, 10, "Buy vs Rent + Invest Wealth", ln=True)
        fig, ax = plt.subplots(figsize=(10,6))
        ax.plot(df_numeric["Year"], df_numeric["Net_Wealth_Buy"], label="Buy", marker='o')
        ax.plot(df_numeric["Year"], df_numeric["Net_Wealth_Rent"], label="Rent + Invest", marker='o')
        ax.set_xlabel("Year")
        ax.set_ylabel("Net Wealth (RM)")
        ax.set_title("Net Wealth Over Time")
        ax.legend()
        wealth_file = "wealth_curve.png"
        plt.savefig(wealth_file)
        plt.close(fig)
        pdf.image(wealth_file, w=180)
        temp_files.append(wealth_file)

    if include_wordcloud and wordcloud:
        pdf.add_page()
        pdf.set_font("Arial", "B", 14)
        pdf.cell(0, 10, "WordCloud of Text Data", ln=True)
        wordcloud_file = "wordcloud.png"
        wordcloud.to_file(wordcloud_file)
        pdf.image(wordcloud_file, w=180)
        temp_files.append(wordcloud_file)

    if include_topwords and word_freq:
        pdf.ln(10)
        pdf.set_font("Arial", "B", 14)
        pdf.cell(0, 10, "Top Words Frequency", ln=True)
        words, counts = zip(*word_freq)
        fig_bar, ax_bar = plt.subplots(figsize=(8,5))
        ax_bar.barh(words[::-1], counts[::-1], color="teal")
        ax_bar.set_xlabel("Count")
        ax_bar.set_ylabel("Word")
        bar_file = "top_words.png"
        plt.savefig(bar_file)
        plt.close(fig_bar)
        pdf.image(bar_file, w=180)
        temp_files.append(bar_file)

    pdf_file = "Combined_Insights_Report.pdf"
    pdf.output(pdf_file)
    for file in temp_files:
        if os.path.exists(file):
            os.remove(file)
    return pdf_file

# ----------------------------
# Sidebar Inputs
# ----------------------------
st.sidebar.header("💰 Financial Inputs")
mortgage_rate = st.sidebar.slider("Mortgage Rate (%)", 1.0, 10.0, 4.0, 0.1)
rent_escalation = st.sidebar.slider("Annual Rent Growth (%)", 0.0, 10.0, 3.0, 0.1)
investment_return = st.sidebar.slider("Investment Return (%)", 1.0, 15.0, 7.0, 0.1)
years = st.sidebar.number_input("Analysis Period (Years)", value=30, step=1)

df_numeric = generate_financial_df(mortgage_rate, rent_escalation, investment_return, years=years)

# ----------------------------
# Pages Implementation
# ----------------------------
# EDA Overview
if page == "📊 EDA Overview":
    st.title("🔎 Dataset Preview & Stats")
    st.dataframe(df_numeric)
    st.subheader("📊 Numeric Descriptive Statistics")
    st.write(df_numeric.describe())
    st.subheader("❗ Missing Values")
    st.write(df_numeric.isna().sum())
    st.subheader("📈 Correlation Heatmap")
    fig, ax = plt.subplots(figsize=(8,6))
    cax = ax.matshow(df_numeric.corr(), cmap="coolwarm")
    plt.xticks(range(len(df_numeric.columns)), df_numeric.columns, rotation=45)
    plt.yticks(range(len(df_numeric.columns)), df_numeric.columns)
    fig.colorbar(cax)
    st.pyplot(fig)

# Wealth Comparison
elif page == "📈 Wealth Comparison":
    st.title("📊 Buy vs Rent + Invest Wealth Over Time")
    fig, ax = plt.subplots(figsize=(10,6))
    ax.plot(df_numeric["Year"], df_numeric["Net_Wealth_Buy"], label="Buy", marker='o')
    ax.plot(df_numeric["Year"], df_numeric["Net_Wealth_Rent"], label="Rent + Invest", marker='o')
    ax.set_xlabel("Year")
    ax.set_ylabel("Net Wealth (RM)")
    ax.set_title("Net Wealth Comparison")
    ax.legend()
    st.pyplot(fig)

# Sensitivity Analysis
elif page == "⚖️ Sensitivity Analysis":
    st.title("⚖️ Sensitivity Analysis")
    st.info("Sensitivity Analysis chart will show multiple scenarios overlayed (Buy vs Rent+Invest).")
    st.write("Adjust sliders in sidebar to see impact of ranges.")

# WordCloud
elif page == "☁️ WordCloud":
    st.title("☁️ WordCloud Generator")
    source_option = st.radio("Select text source:", ["Text Input", "CSV Upload", "Google Search"])
    text_data = ""

    if source_option == "Text Input":
        user_text = st.text_area("Paste your text here:", height=200)
        if user_text.strip():
            text_data = user_text

    elif source_option == "CSV Upload":
        uploaded_file = st.file_uploader("Upload CSV with 'Content' column", type=["csv"])
        if uploaded_file:
            df_text = pd.read_csv(uploaded_file)
            if "Content" in df_text.columns:
                text_data = " ".join(df_text["Content"].dropna().astype(str))
            else:
                st.error("CSV must have a 'Content' column.")

    elif source_option == "Google Search":
        st.info("Fetching latest articles from Google...")
        text_data = fetch_google_articles_safe(query="Rent vs Buy", max_articles=5)

    if text_data.strip():
        extra_stopwords = {"akan","dan","atau","yang","untuk","dengan","jika"}
        stop_words = set(stopwords.words("english")) | extra_stopwords
        wordcloud, word_freq = generate_wordcloud(text_data, stop_words=stop_words)

        st.subheader("☁️ WordCloud")
        fig_wc, ax_wc = plt.subplots(figsize=(10,5))
        ax_wc.imshow(wordcloud, interpolation="bilinear")
        ax_wc.axis("off")
        st.pyplot(fig_wc)

        words, counts = zip(*word_freq) if word_freq else ([], [])
        st.subheader("📊 Top Words Frequency")
        fig_bar, ax_bar = plt.subplots(figsize=(8,5))
        if words:
            ax_bar.barh(words[::-1], counts[::-1], color="teal")
            ax_bar.set_xlabel("Count")
            ax_bar.set_ylabel("Word")
        else:
            ax_bar.text(0.5,0.5,"No words found", ha="center")
        st.pyplot(fig_bar)
    else:
        st.info("⚠️ No text available from the selected source.")

# Combined Insights PDF
elif page == "🔗 Combined Insights":
    st.title("🔗 Combined Financial & Text Insights")
    include_wealth = st.checkbox("Include Wealth Curve", value=True)
    include_wordcloud = st.checkbox("Include WordCloud", value=True)
    include_topwords = st.checkbox("Include Top Words Bar Chart", value=True)

    if 'wordcloud' not in locals() or 'word_freq' not in locals():
        st.info("Fetching latest articles for WordCloud...")
        text_data = fetch_google_articles_safe(query="Rent vs Buy", max_articles=5)
        if text_data.strip():
            extra_stopwords = {"akan","dan","atau","yang","untuk","dengan","jika"}
            stop_words = set(stopwords.words("english")) | extra_stopwords
            wordcloud, word_freq = generate_wordcloud(text_data, stop_words=stop_words)

    if st.button("⬇️ Download Combined PDF"):
        pdf_file = save_combined_pdf(
            df_numeric,
            wordcloud if include_wordcloud and 'wordcloud' in locals() else None,
            word_freq if include_topwords and 'word_freq' in locals() else None,
            include_wealth,
            include_wordcloud,
            include_topwords
        )
        with open(pdf_file, "rb") as f:
            st.download_button("Download PDF", f, file_name=pdf_file, mime="application/pdf")
