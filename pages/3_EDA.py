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

st.markdown("### 🔄 Scenario Comparison")
with st.expander("ℹ️ Description", expanded=False):
    st.write("""
    Scenario analysis evaluates how investment outcomes change under 
    alternative future states, such as optimistic, baseline, and 
    pessimistic conditions. This technique supports robust planning by 
    illustrating potential deviations from the central forecast.
    """)

# --- Define Scenarios ---
years = np.arange(2025, 2046)
baseline = np.cumprod([1.05]*len(years)) * 100
optimistic = np.cumprod([1.08]*len(years)) * 100
pessimistic = np.cumprod([1.03]*len(years)) * 100

df_scen = pd.DataFrame({
    "Year": years.astype(int),
    "Baseline (5%)": baseline,
    "Optimistic (8%)": optimistic,
    "Pessimistic (3%)": pessimistic
})

# --- Chart ---
fig, ax = plt.subplots()
ax.plot(df_scen["Year"], df_scen["Baseline (5%)"], label="Baseline (5%)", color="blue")
ax.plot(df_scen["Year"], df_scen["Optimistic (8%)"], label="Optimistic (8%)", color="green")
ax.plot(df_scen["Year"], df_scen["Pessimistic (3%)"], label="Pessimistic (3%)", color="red")
ax.set_xlabel("Year")
ax.set_ylabel("Index Value (Relative Growth)")
ax.set_title("Scenario Comparison")
ax.legend()
st.pyplot(fig)

# --- Download ---
csv = df_scen.to_csv(index=False).encode("utf-8")
st.download_button(
    "⬇️ Download Scenario Results (CSV)",
    data=csv,
    file_name="scenario_analysis.csv",
    mime="text/csv"
)



# ----------------------------
# Page setup
# ----------------------------
st.set_page_config(page_title="EDA & Forum Scraper", layout="wide")

# ----------------------------
# Download required NLTK data
# ----------------------------
nltk.download("punkt", quiet=True)
nltk.download("stopwords", quiet=True)
nltk.download("wordnet", quiet=True)

# ----------------------------
# Load EDA Data
# ----------------------------
@st.cache_data
def load_data(path: str = "data.csv"):
    if not os.path.exists(path):
        return None, f"File not found: {path}"
    try:
        df = pd.read_csv(path)
        return df, None
    except Exception as e:
        return None, f"Error reading {path}: {e}"

# ----------------------------
# Text Preprocessing
# ----------------------------
def preprocess_text(text_series: pd.Series):
    lemmatizer = WordNetLemmatizer()
    stop_words = set(stopwords.words("english"))
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
# Reddit Scraper (PRAW)
# ----------------------------
@st.cache_data(show_spinner=False)
def scrape_reddit_praw(query, subreddit_name, limit, client_id, client_secret, user_agent):
    reddit = praw.Reddit(
        client_id=client_id,
        client_secret=client_secret,
        user_agent=user_agent
    )
    subreddit = reddit.subreddit(subreddit_name)
    posts = []
    for submission in subreddit.search(query, limit=limit):
        posts.append({
            "platform": "Reddit",
            "subreddit": subreddit_name,
            "title": submission.title,
            "url": submission.url,
            "content": submission.selftext[:300]
        })
    return pd.DataFrame(posts)

# ----------------------------
# Streamlit Layout
# ----------------------------
st.sidebar.title("🔍 Navigation")
page = st.sidebar.radio("Go to:", ["📊 EDA", "💬 Forum Scraper"])

if page == "💬 Forum Scraper":
    st.title("🏡 Rent vs Buy — Forum Discussions (Malaysia)")
    st.write("Fetching latest Reddit discussions using Reddit API.")

    query = st.text_input("Search query:", "rent vs buy")
    subreddit = st.selectbox("Choose subreddit:", ["MalaysianPF", "Malaysia", "personalfinance", "realestate"])
    limit = st.slider("Number of posts", 5, 50, 20)

    # PRAW credentials input
    st.sidebar.subheader("🔑 Reddit API Credentials")
    client_id = st.sidebar.text_input("Client ID", type="password")
    client_secret = st.sidebar.text_input("Client Secret", type="password")
    user_agent = st.sidebar.text_input("User Agent", "streamlit-app")

    if st.button("Scrape Discussions"):
        if not (client_id and client_secret and user_agent):
            st.warning("Please enter all Reddit API credentials in the sidebar!")
        else:
            with st.spinner("Scraping Reddit..."):
                df_posts = scrape_reddit_praw(query, subreddit, limit, client_id, client_secret, user_agent)

                if df_posts.empty:
                    st.warning("No posts found.")
                else:
                    st.success(f"Fetched {len(df_posts)} posts from r/{subreddit}")
                    st.dataframe(df_posts, use_container_width=True)

                    # Word Cloud & Top Words Side-by-Side
                    st.subheader("📊 Word Cloud & Top Words/Phrases")
                    tokens = preprocess_text(df_posts["title"])
                    if tokens:
                        ngram_option = st.radio("Show:", ["Unigrams", "Bigrams", "Trigrams"])
                        n = 1 if ngram_option == "Unigrams" else 2 if ngram_option == "Bigrams" else 3
                        top_ngrams = get_top_ngrams(tokens, n=n, top_k=10)

                        col1, col2 = st.columns(2)
                        with col1:
                            st.write("### Word Cloud")
                            if n == 1:
                                wc_text = " ".join(tokens)
                                wc = WordCloud(width=800, height=400, background_color="white").generate(wc_text)
                                fig, ax = plt.subplots(figsize=(10, 5))
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
                        st.warning("No text available for analysis.")
