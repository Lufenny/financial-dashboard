import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from wordcloud import WordCloud
from collections import Counter
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer
from nltk import ngrams
from nltk.tokenize import word_tokenize
import requests
from bs4 import BeautifulSoup
import re

# ----------------------------
# NLTK Setup
# ----------------------------
import nltk
nltk.download('punkt')
nltk.download('stopwords')
nltk.download('wordnet')

# ----------------------------
# Streamlit Page Config
# ----------------------------
st.set_page_config(page_title="EDA & Forum Scraper", layout="wide")
st.sidebar.title("🔍 Navigation")
page = st.sidebar.radio("Go to:", ["📊 EDA", "💬 Forum Scraper"])

# ----------------------------
# Load EDA Data
# ----------------------------
@st.cache_data
def load_data():
    url = "https://raw.githubusercontent.com/Lufenny/financial-dashboard/main/Data.csv"
    try:
        df = pd.read_csv(url)
        return df
    except Exception as e:
        st.error(f"Could not load Data.csv from GitHub. Error: {e}")
        return pd.DataFrame()

# ----------------------------
# EDA Page
# ----------------------------
if page == "📊 EDA":
    st.title("🔎 Exploratory Data Analysis (EDA)")
    df = load_data()
    
    if not df.empty:
        if "Year" in df.columns:
            df["Year"] = df["Year"].astype(int)
            df = df.reset_index(drop=True)
        
        # Data Preview
        st.subheader("📋 Data Preview")
        st.dataframe(df)

        # Summary Statistics
        st.subheader("📊 Summary Statistics")
        st.write(df.describe())

        # Chart Selector
        st.subheader("📈 Visual Analysis")
        chart_type = st.selectbox(
            "Select a chart to display:",
            ["OPR vs Year", "EPF vs Year", "Price Growth vs Year", "Rent Yield vs Year", "Correlation Heatmap"]
        )

        if chart_type == "OPR vs Year" and "OPR_avg" in df.columns:
            fig, ax = plt.subplots()
            ax.plot(df["Year"], df["OPR_avg"], marker="o", label="OPR (%)", color="blue")
            ax.set_xlabel("Year"); ax.set_ylabel("OPR (%)")
            ax.set_title("Trend of OPR vs Year")
            ax.legend(); st.pyplot(fig)

        elif chart_type == "EPF vs Year" and "EPF" in df.columns:
            fig, ax = plt.subplots()
            ax.plot(df["Year"], df["EPF"], marker="s", label="EPF (%)", color="orange")
            ax.set_xlabel("Year"); ax.set_ylabel("EPF (%)")
            ax.set_title("Trend of EPF vs Year")
            ax.legend(); st.pyplot(fig)

        elif chart_type == "Price Growth vs Year" and "PriceGrowth" in df.columns:
            fig, ax = plt.subplots()
            ax.plot(df["Year"], df["PriceGrowth"], marker="^", label="Price Growth (%)", color="green")
            ax.set_xlabel("Year"); ax.set_ylabel("Price Growth (%)")
            ax.set_title("Trend of Price Growth vs Year")
            ax.legend(); st.pyplot(fig)

        elif chart_type == "Rent Yield vs Year" and "RentYield" in df.columns:
            fig, ax = plt.subplots()
            ax.plot(df["Year"], df["RentYield"], marker="d", label="Rental Yield (%)", color="purple")
            ax.set_xlabel("Year"); ax.set_ylabel("Rental Yield (%)")
            ax.set_title("Trend of Rental Yield vs Year")
            ax.legend(); st.pyplot(fig)

        elif chart_type == "Correlation Heatmap":
            st.write("### Correlation Matrix")
            corr = df.corr(numeric_only=True)
            st.dataframe(corr.style.background_gradient(cmap="Blues"))

        # Download
        st.subheader("⬇️ Download Data")
        csv = df.to_csv(index=False).encode("utf-8")
        st.download_button("Download Dataset (CSV)", data=csv, file_name="EDA_data.csv", mime="text/csv")
    else:
        st.warning("EDA data is empty. Check GitHub CSV URL or network.")

# ----------------------------
# Forum Scraper Page (PropertyGuru Articles)
# ----------------------------
elif page == "💬 Forum Scraper":
    st.title("🏡 Rent vs Buy — PropertyGuru Articles (Malaysia)")
    st.write("Fetching latest property articles without API keys.")

    # ----------------------------
    # Scraper Function
    # ----------------------------
    def scrape_propertyguru(query="rent buy", limit=20):
        base_url = "https://www.propertyguru.com.my/property-news"
        headers = {"User-Agent": "Mozilla/5.0"}
        posts = []

        try:
            r = requests.get(base_url, headers=headers, timeout=10)
            if r.status_code != 200:
                return pd.DataFrame([{"error": f"Failed to fetch PropertyGuru data: {r.status_code}"}])

            soup = BeautifulSoup(r.text, "html.parser")
            articles = soup.find_all("article")[:limit]

            for a in articles:
                title_tag = a.find("h2")
                snippet_tag = a.find("p")
                url_tag = a.find("a", href=True)

                title = title_tag.text.strip() if title_tag else ""
                snippet = snippet_tag.text.strip() if snippet_tag else ""
                url = url_tag["href"] if url_tag else ""

                # Filter locally for query keywords
                if any(k in (title + " " + snippet).lower() for k in query.lower().split()):
                    posts.append({
                        "platform": "PropertyGuru",
                        "title": title,
                        "content": snippet,
                        "url": url
                    })

        except Exception as e:
            st.error(f"Scraping failed: {e}")

        return pd.DataFrame(posts)

    # ----------------------------
    # Text Processing Functions
    # ----------------------------
    def preprocess_text(text_series):
        lemmatizer = WordNetLemmatizer()
        stop_words = set(stopwords.words('english'))

        all_tokens = []
        for text in text_series.dropna().astype(str):
            tokens = word_tokenize(text.lower())
            tokens = [lemmatizer.lemmatize(t) for t in tokens if t.isalpha() and t not in stop_words]
            all_tokens.extend(tokens)
        return all_tokens

    def get_top_ngrams(tokens, n=1, top_k=10):
        if n == 1:
            c = Counter(tokens)
        else:
            c = Counter(ngrams(tokens, n))
        return c.most_common(top_k)

    # ----------------------------
    # Streamlit UI
    # ----------------------------
    query = st.text_input("Search query:", "rent buy")
    limit = st.slider("Number of articles", 5, 20, 10)
    ngram_option = st.radio("Show:", ["Unigrams", "Bigrams", "Trigrams"])

    if st.button("Scrape Articles"):
        with st.spinner("Fetching PropertyGuru articles..."):
            df = scrape_propertyguru(query, limit)

            if not df.empty:
                st.success(f"Fetched {len(df)} articles matching '{query}'")
                st.dataframe(df)

                # Download scraped articles
                st.subheader("⬇️ Download Articles")
                csv = df.to_csv(index=False).encode("utf-8")
                st.download_button("Download Articles (CSV)", data=csv, file_name="PropertyGuru_articles.csv", mime="text/csv")

                # Word Cloud & Top Words
                st.subheader("📊 Word Cloud & Top Words/Phrases")
                text_series = df["title"] + " " + df["content"]
                tokens = preprocess_text(text_series)

                if tokens:
                    n = 1 if ngram_option=="Unigrams" else 2 if ngram_option=="Bigrams" else 3
                    top_ngrams = get_top_ngrams(tokens, n=n, top_k=10)

                    col1, col2 = st.columns(2)

                    with col1:
                        st.write("### Word Cloud")
                        if n == 1:
                            wc_text = " ".join(tokens)
                            wc = WordCloud(width=800, height=400, background_color="white").generate(wc_text)
                            fig, ax = plt.subplots(figsize=(10,5))
                            ax.imshow(wc, interpolation="bilinear")
                            ax.axis("off")
                            st.pyplot(fig)
                        else:
                            st.info("Word Cloud only for unigrams. Showing Top Phrases instead.")

                    with col2:
                        st.write(f"### Top 10 {ngram_option}")
                        top_words = [" ".join(w) if isinstance(w, tuple) else w for w, count in top_ngrams]
                        counts = [count for w, count in top_ngrams]
                        st.table(pd.DataFrame({"Word/Phrase": top_words, "Count": counts}))

            else:
                st.warning(f"No articles found matching '{query}'. Try another keyword.")
