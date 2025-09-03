import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import io
import re
from collections import Counter
from wordcloud import WordCloud
import nltk
from nltk.corpus import stopwords
import os
import requests
from bs4 import BeautifulSoup
import concurrent.futures
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image as RLImage
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.pagesizes import A4

# ----------------------------
# NLTK Setup
# ----------------------------
try:
    stopwords.words("english")
except LookupError:
    nltk.download("punkt")
    nltk.download("stopwords")

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
# Financial Data Function
# ----------------------------
@st.cache_data
def generate_financial_df(mortgage_rate, rent_escalation, investment_return, years=30,
                          mortgage_term=30, property_price=500000, monthly_rent=1500):
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

def get_wordcloud_image(wordcloud):
    fig_wc, ax_wc = plt.subplots(figsize=(10, 5))
    ax_wc.imshow(wordcloud, interpolation="bilinear")
    ax_wc.axis("off")
    buf = io.BytesIO()
    plt.savefig(buf, format="png")
    buf.seek(0)
    plt.close(fig_wc)
    return buf

# ----------------------------
# Malaysia Blog Scraping
# ----------------------------
def fetch_blog_text(url):
    headers = {"User-Agent": "Mozilla/5.0"}
    try:
        resp = requests.get(url, headers=headers, timeout=5)
        soup = BeautifulSoup(resp.text, "html.parser")
        paragraphs = [p.get_text() for p in soup.find_all("p")]
        return " ".join(paragraphs)
    except Exception:
        return ""

@st.cache_data
def fetch_malaysia_blogs(urls):
    text_data = ""
    with concurrent.futures.ThreadPoolExecutor() as executor:
        results = list(executor.map(fetch_blog_text, urls))
    for r in results:
        text_data += r + " "
    text_data = re.sub(r"\s+", " ", text_data)
    if not text_data.strip():
        text_data = "No text could be fetched from the web."
    return text_data

# ----------------------------
# PDF Export Function (ReportLab)
# ----------------------------
def save_combined_pdf(df_numeric, insights_text, sources, wordcloud=None, word_freq=None,
                      include_wealth=True, include_wordcloud=True, include_topwords=True):
    pdf_file = "Combined_Insights_Report.pdf"
    doc = SimpleDocTemplate(pdf_file, pagesize=A4)
    styles = getSampleStyleSheet()
    elements = []

    elements.append(Paragraph("Combined Insights Report", styles["Title"]))
    elements.append(Spacer(1, 12))

    if include_wealth:
        elements.append(Paragraph("Wealth Curve: Buy vs Rent + Invest", styles["Heading2"]))
        fig, ax = plt.subplots(figsize=(8, 4))
        ax.plot(df_numeric["Year"], df_numeric["Net_Wealth_Buy"], label="Buy", marker="o")
        ax.plot(df_numeric["Year"], df_numeric["Net_Wealth_Rent"], label="Rent + Invest", marker="o")
        ax.set_xlabel("Year")
        ax.set_ylabel("Net Wealth (RM)")
        ax.set_title("Net Wealth Over Time")
        ax.legend()
        wealth_file = "wealth_curve.png"
        plt.savefig(wealth_file)
        plt.close(fig)
        elements.append(RLImage(wealth_file, width=400, height=200))
        elements.append(Spacer(1, 12))

    if include_wordcloud and wordcloud:
        elements.append(Paragraph("WordCloud from Malaysia Blogs", styles["Heading2"]))
        wordcloud_file = "wordcloud.png"
        wordcloud.to_file(wordcloud_file)
        elements.append(RLImage(wordcloud_file, width=400, height=200))
        elements.append(Spacer(1, 12))

    if include_topwords and word_freq:
        elements.append(Paragraph("Top Words Frequency", styles["Heading2"]))
        words, counts = zip(*word_freq)
        fig_bar, ax_bar = plt.subplots(figsize=(6, 4))
        ax_bar.barh(words[::-1], counts[::-1], color="teal")
        ax_bar.set_xlabel("Count")
        ax_bar.set_ylabel("Word")
        bar_file = "top_words.png"
        plt.savefig(bar_file)
        plt.close(fig_bar)
        elements.append(RLImage(bar_file, width=300, height=200))
        elements.append(Spacer(1, 12))

    # Insights
    elements.append(Paragraph("Insights & Recommendations", styles["Heading2"]))
    elements.append(Paragraph(insights_text.replace("\n", "<br/>"), styles["Normal"]))
    elements.append(Spacer(1, 12))

    # Sources
    elements.append(Paragraph("Sources", styles["Heading2"]))
    for src in sources:
        elements.append(Paragraph(src, styles["Normal"]))
    elements.append(Spacer(1, 12))

    doc.build(elements)
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

elif page == "📈 Wealth Comparison":
    st.title("📊 Buy vs Rent + Invest Wealth")
    fig, ax = plt.subplots(figsize=(10, 6))
    ax.plot(df_numeric["Year"], df_numeric["Net_Wealth_Buy"], label="Buy", marker="o")
    ax.plot(df_numeric["Year"], df_numeric["Net_Wealth_Rent"], label="Rent + Invest", marker="o")
    ax.set_xlabel("Year")
    ax.set_ylabel("Net Wealth (RM)")
    ax.legend()
    st.pyplot(fig)

elif page == "☁️ WordCloud (Malaysia Blogs)":
    st.title("☁️ WordCloud from Malaysia Blogs")

    urls = [
        "https://www.greateasternlife.com/my/en/personal-insurance/greatpedia/live-great-reads/wellbeing-and-success/should-you-buy-or-rent-a-property-in-malaysia.html",
        "https://www.kwsp.gov.my/en/w/article/buy-vs-rent-malaysia",
        "https://www.iproperty.com.my/guides/should-buy-or-rent-property-malaysia-30437"
    ]
    text_data = fetch_malaysia_blogs(urls)

    extra_stopwords = {"akan", "dan", "atau", "yang", "untuk", "dengan", "jika"}
    stop_words = set(stopwords.words("english")) | extra_stopwords
    wordcloud, word_freq = generate_wordcloud(text_data, stop_words=stop_words)

    st.subheader("☁️ WordCloud")
    wc_buf = get_wordcloud_image(wordcloud)
    st.image(wc_buf)

    st.subheader("📊 Top Words Frequency")
    words, counts = zip(*word_freq) if word_freq else ([], [])
    fig_bar, ax_bar = plt.subplots(figsize=(8, 5))
    ax_bar.barh(words[::-1], counts[::-1], color="teal")
    st.pyplot(fig_bar)

elif page == "🔗 Combined Insights":
    st.title("🔗 Combined Insights")

    urls = [
        "https://www.greateasternlife.com/my/en/personal-insurance/greatpedia/live-great-reads/wellbeing-and-success/should-you-buy-or-rent-a-property-in-malaysia.html",
        "https://www.kwsp.gov.my/en/w/article/buy-vs-rent-malaysia",
        "https://www.iproperty.com.my/guides/should-buy-or-rent-property-malaysia-30437"
    ]
    text_data = fetch_malaysia_blogs(urls)
    extra_stopwords = {"akan", "dan", "atau", "yang", "untuk", "dengan", "jika"}
    stop_words = set(stopwords.words("english")) | extra_stopwords
    wordcloud, word_freq = generate_wordcloud(text_data, stop_words=stop_words)

    # Insights
    insights_text = """
    - Buying builds equity over time but requires higher upfront and recurring costs.
    - Renting provides flexibility and lower short-term costs, but no asset accumulation.
    - Investing rental savings can sometimes outperform home equity, depending on returns.
    """

    st.subheader("💡 Insights & Recommendations")
    st.info(insights_text)

    st.subheader("📚 Sources")
    for url in urls:
        st.write(f"- {url}")

    if st.button("⬇️ Download Combined PDF"):
        pdf_file = save_combined_pdf(df_numeric, insights_text, urls,
                                     wordcloud=wordcloud, word_freq=word_freq)
        with open(pdf_file, "rb") as f:
            st.download_button("Download PDF", f, file_name=pdf_file, mime="application/pdf")
