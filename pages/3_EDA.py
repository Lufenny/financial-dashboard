import streamlit as st

# ----------------------------
# Global Page Config
# ----------------------------
st.set_page_config(page_title='EDA & Forum Scraper', layout='wide')
st.title('🔎 Exploratory Data Analysis (EDA) & Forum Scraper')

# ----------------------------
# Imports
# ----------------------------
import pandas as pd
import matplotlib.pyplot as plt
import requests
import re
from wordcloud import WordCloud
from collections import Counter
import nltk
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer
from nltk import ngrams

# ----------------------------
# NLTK Downloads (Cloud-safe)
# ----------------------------
nltk.download('stopwords', quiet=True)
nltk.download('wordnet', quiet=True)

# ----------------------------
# Load EDA Data
# ----------------------------
@st.cache_data
def load_data():
    url = "https://raw.githubusercontent.com/Lufenny/financial-dashboard/main/Data.csv"
    try:
        return pd.read_csv(url)
    except Exception as e:
        st.error(f"Could not load Data.csv from GitHub. Error: {e}")
        return pd.DataFrame()

# ----------------------------
# Reddit Scraper
# ----------------------------
def scrape_reddit_no_api(query="rent vs buy", subreddit="MalaysianPF", limit=20):
    url = f"https://www.reddit.com/r/{subreddit}/search.json?q={query}&restrict_sr=1&limit={limit}&sort=new"
    headers = {"User-Agent": "Mozilla/5.0"}
    r = requests.get(url, headers=headers)
    if r.status_code != 200:
        return pd.DataFrame([{"error": f"Failed to fetch Reddit data: {r.status_code}"}])

    data = r.json()
    posts = []
    for post in data.get("data", {}).get("children", []):
        p = post["data"]
        posts.append({
            "platform": "Reddit",
            "subreddit": subreddit,
            "title": p.get("title", ""),
            "url": "https://reddit.com" + p.get("permalink", ""),
            "content": p.get("selftext", "")[:300]
        })
    return pd.DataFrame(posts)

# ----------------------------
# Sidebar Navigation
# ----------------------------
st.sidebar.title("🔍 Navigation")
page = st.sidebar.radio("Go to:", ["📊 EDA", "💬 Forum Scraper"])

# ----------------------------
# Page 1: EDA
# ----------------------------
if page == "📊 EDA":
    st.header("🔎 Exploratory Data Analysis (EDA)")
    df = load_data()

    if df.empty:
        st.warning("No data available for EDA.")
        st.stop()

    if "Year" in df.columns:
        df["Year"] = df["Year"].astype(int)
        df = df.reset_index(drop=True)

    st.subheader("📋 Data Preview")
    st.dataframe(df)

    st.subheader("📊 Summary Statistics")
    st.write(df.describe())

    st.subheader("📈 Visual Analysis")
    chart_type = st.selectbox(
        "Select a chart to display:",
        ["OPR vs Year", "EPF vs Year", "Price Growth vs Year", "Rent Yield vs Year", "Correlation Heatmap"]
    )

    if chart_type == "OPR vs Year" and "OPR_avg" in df.columns:
        fig, ax = plt.subplots()
        ax.plot(df["Year"], df["OPR_avg"], marker="o", color="blue", label="OPR (%)")
        ax.set_xlabel("Year"); ax.set_ylabel("OPR (%)"); ax.set_title("Trend of OPR vs Year"); ax.legend()
        st.pyplot(fig)
    elif chart_type == "EPF vs Year" and "EPF" in df.columns:
        fig, ax = plt.subplots()
        ax.plot(df["Year"], df["EPF"], marker="s", color="orange", label="EPF (%)")
        ax.set_xlabel("Year"); ax.set_ylabel("EPF (%)"); ax.set_title("Trend of EPF vs Year"); ax.legend()
        st.pyplot(fig)
    elif chart_type == "Price Growth vs Year" and "PriceGrowth" in df.columns:
        fig, ax = plt.subplots()
        ax.plot(df["Year"], df["PriceGrowth"], marker="^", color="green", label="Price Growth (%)")
        ax.set_xlabel("Year"); ax.set_ylabel("Price Growth (%)"); ax.set_title("Trend of Price Growth vs Year"); ax.legend()
        st.pyplot(fig)
    elif chart_type == "Rent Yield vs Year" and "RentYield" in df.columns:
        fig, ax = plt.subplots()
        ax.plot(df["Year"], df["RentYield"], marker="d", color="purple", label="Rental Yield (%)")
        ax.set_xlabel("Year"); ax.set_ylabel("Rental Yield (%)"); ax.set_title("Trend of Rental Yield vs Year"); ax.legend()
        st.pyplot(fig)
    elif chart_type == "Correlation Heatmap":
        st.write("### Correlation Matrix")
        corr = df.corr(numeric_only=True)
        st.dataframe(corr.style.background_gradient(cmap="Blues"))

    st.subheader("⬇️ Download Data")
    csv = df.to_csv(index=False).encode("utf-8")
    st.download_button("Download Dataset (CSV)", data=csv, file_name="EDA_data.csv", mime="text/csv")

# ----------------------------
# Page 2: Forum Scraper
# ----------------------------
elif page == "💬 Forum Scraper":
    st.header("🏡 Rent vs Buy — Forum Discussions (Malaysia)")
    st.write("Fetching latest Reddit discussions without API keys.")

    query = st.text_input("Search query:", "rent vs buy")
    subreddit = st.selectbox("Choose subreddit:", ["MalaysianPF", "Malaysia", "personalfinance", "realestate"])
    limit = st.slider("Number of posts", 5, 50, 20)
    ngram_option = st.radio("Show:", ["Unigrams", "Bigrams", "Trigrams"])

    if st.button("Scrape Discussions"):
        with st.spinner("Scraping Reddit..."):
            df = scrape_reddit_no_api(query, subreddit, limit)

            if df.empty:
                st.warning("No posts found. Try another query or subreddit.")
                st.stop()

            for col in ["title", "content"]:
                if col not in df.columns:
                    df[col] = ""

            st.success(f"Fetched {len(df)} posts from r/{subreddit}")
            st.dataframe(df)

            text_series = df["title"].fillna("") + " " + df["content"].fillna("")

            lemmatizer = WordNetLemmatizer()
            stop_words = set(stopwords.words('english'))
            all_tokens = []

            for text in text_series.astype(str):
                tokens = re.findall(r'\b[a-zA-Z]+\b', text.lower())
                tokens = [lemmatizer.lemmatize(t) for t in tokens if t not in stop_words]
                all_tokens.extend(tokens)

            tokens = all_tokens

            if tokens:
                n = 1 if ngram_option == "Unigrams" else 2 if ngram_option == "Bigrams" else 3
                if n == 1:
                    top_ngrams = Counter(tokens).most_common(10)
                else:
                    top_ngrams = Counter(ngrams(tokens, n)).most_common(10)

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
                st.warning("No text available for Word Cloud / n-gram analysis, but posts are displayed above.")
