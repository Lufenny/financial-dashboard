import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from wordcloud import WordCloud
import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize

# Make sure nltk punkt + stopwords are available
nltk.download("punkt", quiet=True)
nltk.download("stopwords", quiet=True)

st.title("📑 Rent vs Buy — Blog Insights (Malaysia)")

# --- Load CSV from GitHub ---
@st.cache_data
def load_blog_data():
    url = "https://raw.githubusercontent.com/Lufenny/financial-dashboard/main/financial-dashboard/Rent_vs_Buy_Blogs.csv"
    try:
        df = pd.read_csv(url)
        return df
    except Exception as e:
        st.error(f"Could not load blog CSV file. Error: {e}")
        return pd.DataFrame()

df = load_blog_data()

if df.empty:
    st.warning("⚠️ Blog CSV file is empty or missing. Please check the GitHub link.")
else:
    st.success("✅ Blog CSV loaded successfully!")
    st.dataframe(df)

    # --- Show category distribution ---
    st.subheader("📊 Category Distribution")
    category_counts = df["Category"].value_counts()
    st.bar_chart(category_counts)

    # --- Word Cloud from blog contents ---
    st.subheader("☁️ Word Cloud from Blog Content")

    text_series = df["Content"].dropna().astype(str)
    stop_words = set(stopwords.words("english"))

    def preprocess_text(text_series):
        tokens = []
        for text in text_series:
            words = word_tokenize(text.lower())
            words = [w for w in words if w.isalpha() and w not in stop_words]
            tokens.extend(words)
        return tokens

    tokens = preprocess_text(text_series)

    if tokens:
        wordcloud = WordCloud(width=800, height=400, background_color="white").generate(" ".join(tokens))
        fig, ax = plt.subplots(figsize=(10, 5))
        ax.imshow(wordcloud, interpolation="bilinear")
        ax.axis("off")
        st.pyplot(fig)
    else:
        st.warning("⚠️ No tokens available for word cloud.")

    # --- Top keywords ---
    st.subheader("🔑 Top Keywords in Blog Content")
    freq = pd.Series(tokens).value_counts().head(15)
    st.bar_chart(freq)
