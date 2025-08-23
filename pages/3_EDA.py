import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from wordcloud import WordCloud
import nltk
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords

# --- Ensure NLTK dependencies ---
nltk.download("punkt", quiet=True)
nltk.download("stopwords", quiet=True)

# --- Page Title ---
st.title("📑 Blog Insights: Rent vs Buy in Malaysia")

# --- Load CSV from GitHub ---
@st.cache_data
def load_data():
    url = "https://raw.githubusercontent.com/Lufenny/financial-dashboard/main/Rent_vs_Buy_Blogs.csv"
    return pd.read_csv(url)

try:
    df = load_data()
    st.success("✅ Blog CSV loaded successfully!")
except Exception as e:
    st.error(f"⚠️ Could not load blog CSV file.\n\n{e}")
    st.stop()

# --- Show raw dataset ---
st.subheader("🔍 Blog Data Preview")
st.dataframe(df)

# --- Preprocess text ---
def preprocess_text(series):
    text = " ".join(series.dropna().astype(str))
    tokens = word_tokenize(text.lower())
    stop_words = set(stopwords.words("english"))
    tokens = [w for w in tokens if w.isalpha() and w not in stop_words]
    return " ".join(tokens)

# --- Generate Word Cloud ---
st.subheader("☁️ Word Cloud of Blog Content")
all_text = preprocess_text(df["Content"])
if all_text.strip():
    wc = WordCloud(width=800, height=400, background_color="white").generate(all_text)
    fig, ax = plt.subplots(figsize=(10, 5))
    ax.imshow(wc, interpolation="bilinear")
    ax.axis("off")
    st.pyplot(fig)
else:
    st.warning("⚠️ No text found for Word Cloud.")

# --- Category Distribution ---
st.subheader("📊 Category Distribution")
if "Category" in df.columns:
    category_counts = df["Category"].value_counts()
    st.bar_chart(category_counts)
else:
    st.warning("⚠️ 'Category' column missing in dataset.")
