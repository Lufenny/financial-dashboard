import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from wordcloud import WordCloud
from collections import Counter
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer
from nltk import ngrams
import re
import nltk
import praw

# ----------------------------
# NLTK Setup
# ----------------------------
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
        return pd.read_csv(url)
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

# ----------------------------
# Forum Scraper Page (PRAW)
# ----------------------------
elif page == "💬 Forum Scraper":
    st.title("🏡 Rent vs Buy — Forum Discussions (Malaysia)")
    st.write("Fetching latest Reddit discussions via official API.")

    # Reddit API credentials from Streamlit secrets
    client_id = st.secrets["REDDIT_CLIENT_ID"]
    client_secret = st.secrets["REDDIT_CLIENT_SECRET"]
    user_agent = "streamlit_app_by_lufenny"

    reddit = praw.Reddit(
        client_id=client_id,
        client_secret=client_secret,
        user_agent=user_agent
    )

    query = st.text_input("Search query:", "rent vs buy")
    subreddit = st.selectbox("Choose subreddit:", ["MalaysianPF", "Malaysia", "personalfinance", "realestate"])
    limit = st.slider("Number of posts", 5, 50, 20)
    ngram_option = st.radio("Show:", ["Unigrams", "Bigrams", "Trigrams"])

    if st.button("Scrape Discussions"):
        with st.spinner("Fetching Reddit posts..."):
            posts = []
            for submission in reddit.subreddit(subreddit).search(query, limit=limit, sort="new"):
                posts.append({
                    "title": submission.title,
                    "content": submission.selftext[:300],
                    "url": submission.url
                })

            df = pd.DataFrame(posts)

            if df.empty:
                st.warning("No posts found. Try another query or subreddit.")
                st.stop()

            st.success(f"Fetched {len(df)} posts from r/{subreddit}")
            st.dataframe(df)

            # Combine title + content for analysis
            text_series = df["title"].fillna("") + " " + df["content"].fillna("")

            # Text Preprocessing
            lemmatizer = WordNetLemmatizer()
            stop_words = set(stopwords.words("english"))
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
                st.warning("No text available for Word Cloud / n-gram analysis.")
