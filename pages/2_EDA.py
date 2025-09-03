import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from fpdf import FPDF
import re
from functools import lru_cache
from collections import Counter
from wordcloud import WordCloud
import nltk
from nltk.corpus import stopwords
import os
import requests
from bs4 import BeautifulSoup
import time
from concurrent.futures import ThreadPoolExecutor

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
    "☁️ WordCloud (Malaysia Blogs)",
    "🔗 Combined Insights"
])

# ----------------------------
# Financial Model Function
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
# WordCloud Function
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
# Blog Scraping (Malaysia Sources)
# ----------------------------
blog_sources = [
    "https://www.greateasternlife.com/my/en/personal-insurance/greatpedia/live-great-reads/wellbeing-and-success/should-you-buy-or-rent-a-property-in-malaysia.html",
    "https://www.kwsp.gov.my/en/w/article/buy-vs-rent-malaysia",
    "https://www.iproperty.com.my/guides/should-buy-or-rent-property-malaysia-30437"
]

@st.cache_data
def fetch_malaysia_blogs(sources=blog_sources, delay=1):
    headers = {"User-Agent": "Mozilla/5.0"}
    all_text = ""

    def fetch(url):
        try:
            resp = requests.get(url, headers=headers, timeout=10)
            soup = BeautifulSoup(resp.text, "html.parser")
            paragraphs = [p.get_text() for p in soup.find_all("p")]
            return " ".join(paragraphs)
        except:
            return ""

    with ThreadPoolExecutor() as executor:
        texts = list(executor.map(fetch, sources))
    all_text = " ".join(texts)
    all_text = re.sub(r'\s+', ' ', all_text)
    return all_text if all_text.strip() else "No text could be fetched."

# ----------------------------
# PDF Export
# ----------------------------
def save_combined_pdf(df_numeric, wordcloud=None, word_freq=None, include_wealth=True, include_wordcloud=True, include_topwords=True, blog_sources=None):
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
        pdf.cell(0, 10, "WordCloud of Malaysia Blogs", ln=True)
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

    # Recommendation Box
    pdf.add_page()
    pdf.set_font("Arial", "B", 14)
    pdf.set_fill_color(220, 240, 220)
    pdf.multi_cell(0, 10, "💡 Recommendation:\n\nIf Buy wealth > Rent wealth, buying provides better long-term accumulation.\nIf Rent wealth > Buy wealth, renting and investing savings may yield better results.", fill=True)

    # Sources
    if blog_sources:
        pdf.ln(10)
        pdf.set_font("Arial", "", 12)
        pdf.cell(0, 10, "Sources:", ln=True)
        for src in blog_sources:
            pdf.multi_cell(0, 8, src)

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
# Pages
# ----------------------------
if page == "📊 EDA Overview":
    st.title("🔎 Dataset Preview & Stats")
    st.dataframe(df_numeric)
    st.subheader("📊 Descriptive Statistics")
    st.write(df_numeric.describe())
    st.subheader("📈 Correlation Heatmap")
    fig, ax = plt.subplots(figsize=(8,6))
    cax = ax.matshow(df_numeric.corr(), cmap="coolwarm")
    plt.xticks(range(len(df_numeric.columns)), df_numeric.columns, rotation=45)
    plt.yticks(range(len(df_numeric.columns)), df_numeric.columns)
    fig.colorbar(cax)
    st.pyplot(fig)

elif page == "📈 Wealth Comparison":
    st.title("📊 Buy vs Rent + Invest Wealth Over Time")
    fig, ax = plt.subplots(figsize=(10,6))
    ax.plot(df_numeric["Year"], df_numeric["Net_Wealth_Buy"], label="Buy", marker='o')
    ax.plot(df_numeric["Year"], df_numeric["Net_Wealth_Rent"], label="Rent + Invest", marker='o')
    ax.set_xlabel("Year")
    ax.set_ylabel("Net Wealth (RM)")
    ax.legend()
    st.pyplot(fig)

elif page == "⚖️ Sensitivity Analysis":
    st.title("⚖️ Sensitivity Analysis")
    mortgage_range = st.sidebar.slider("Mortgage Rate Range (%)", 2.0, 8.0, (3.0, 6.0), 0.5)
    rent_range = st.sidebar.slider("Rent Escalation Range (%)", 0.0, 10.0, (2.0, 5.0), 0.5)
    invest_range = st.sidebar.slider("Investment Return Range (%)", 3.0, 12.0, (5.0, 9.0), 0.5)

    fig, ax = plt.subplots(figsize=(10,6))
    for mr in np.linspace(mortgage_range[0], mortgage_range[1], 3):
        for rr in np.linspace(rent_range[0], rent_range[1], 2):
            for ir in np.linspace(invest_range[0], invest_range[1], 2):
                df_test = generate_financial_df(mr, rr, ir, years=years)
                ax.plot(df_test["Year"], df_test["Net_Wealth_Buy"], alpha=0.4, color="blue")
                ax.plot(df_test["Year"], df_test["Net_Wealth_Rent"], alpha=0.4, color="green")
    ax.set_title("Sensitivity Analysis: Wealth Outcomes")
    st.pyplot(fig)

elif page == "☁️ WordCloud (Malaysia Blogs)":
    st.title("☁️ WordCloud from Malaysia Property Blogs")
    text_data = fetch_malaysia_blogs()
    if text_data.strip():
        extra_stopwords = {"akan","dan","atau","yang","untuk","dengan","jika"}
        stop_words = set(stopwords.words("english")) | extra_stopwords
        wordcloud, word_freq = generate_wordcloud(text_data, stop_words=stop_words)

        st.subheader("☁️ WordCloud")
        st.image(wordcloud.to_array(), use_column_width=True)

        words, counts = zip(*word_freq) if word_freq else ([], [])
        st.subheader("📊 Top Words Frequency")
        fig_bar, ax_bar = plt.subplots(figsize=(8,5))
        if words:
            ax_bar.barh(words[::-1], counts[::-1], color="teal")
            ax_bar.set_xlabel("Count")
            ax_bar.set_ylabel("Word")
            st.pyplot(fig_bar)
    else:
        st.warning("⚠️ Could not fetch blog content.")

elif page == "🔗 Combined Insights":
    st.title("🔗 Combined Financial & Text Insights")
    include_wealth = st.checkbox("Include Wealth Curve", value=True)
    include_wordcloud = st.checkbox("Include WordCloud", value=True)
    include_topwords = st.checkbox("Include Top Words Bar Chart", value=True)

    if st.button("⬇️ Download Combined PDF"):
        text_data = fetch_malaysia_blogs()
        extra_stopwords = {"akan","dan","atau","yang","untuk","dengan","jika"}
        stop_words = set(stopwords.words("english")) | extra_stopwords
        wordcloud, word_freq = generate_wordcloud(text_data, stop_words=stop_words)

        pdf_file = save_combined_pdf(
            df_numeric,
            wordcloud if include_wordcloud else None,
            word_freq if include_topwords else None,
            include_wealth,
            include_wordcloud,
            include_topwords,
            blog_sources=blog_sources
        )
        with open(pdf_file, "rb") as f:
            st.download_button("Download PDF", f, file_name=pdf_file, mime="application/pdf")
