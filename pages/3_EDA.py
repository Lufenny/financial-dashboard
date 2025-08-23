import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from wordcloud import WordCloud
from collections import Counter
import nltk
from nltk.corpus import stopwords
from nltk import word_tokenize, ngrams
from nltk.stem import WordNetLemmatizer

# ----------------------------
# NLTK Setup
# ----------------------------
nltk.download('punkt')
nltk.download('stopwords')
nltk.download('wordnet')

# ----------------------------
# Streamlit Page Config
# ----------------------------
st.set_page_config(page_title="EDA & Blog Insights", layout="wide")
st.sidebar.title("🔍 Navigation")
page = st.sidebar.radio("Go to:", ["📊 EDA", "💬 Blog Insights"])

# ----------------------------
# Load EDA Data
# ----------------------------
@st.cache_data
def load_eda_data():
    url = "https://raw.githubusercontent.com/Lufenny/financial-dashboard/main/Data.csv"
    try:
        df = pd.read_csv(url)
        return df
    except Exception as e:
        st.error(f"Could not load Data.csv from GitHub. Error: {e}")
        return pd.DataFrame()

# ----------------------------
# Load Blog Data
# ----------------------------
@st.cache_data
def load_blog_data():
    url = "https://raw.githubusercontent.com/Lufenny/financial-dashboard/main/Rent_vs_Buy_Blogs.csv"
    try:
        df = pd.read_csv(url)
        return df
    except Exception as e:
        st.error(f"Could not load blog CSV file. Error: {e}")
        return pd.DataFrame()

# ----------------------------
# Text Preprocessing
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
# EDA Page
# ----------------------------
if page == "📊 EDA":
    st.title("🔎 Exploratory Data Analysis (EDA)")
    df = load_eda_data()
    
    if not df.empty:
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
            ax.plot(df["Year"], df["OPR_avg"], marker="o", color="blue")
            ax.set_xlabel("Year"); ax.set_ylabel("OPR (%)"); ax.set_title("Trend of OPR vs Year")
            st.pyplot(fig)

        elif chart_type == "EPF vs Year" and "EPF" in df.columns:
            fig, ax = plt.subplots()
            ax.plot(df["Year"], df["EPF"], marker="s", color="orange")
            ax.set_xlabel("Year"); ax.set_ylabel("EPF (%)"); ax.set_title("Trend of EPF vs Year")
            st.pyplot(fig)

        elif chart_type == "Price Growth vs Year" and "PriceGrowth" in df.columns:
            fig, ax = plt.subplots()
            ax.plot(df["Year"], df["PriceGrowth"], marker="^", color="green")
            ax.set_xlabel("Year"); ax.set_ylabel("Price Growth (%)"); ax.set_title("Trend of Price Growth vs Year")
            st.pyplot(fig)

        elif chart_type == "Rent Yield vs Year" and "RentYield" in df.columns:
            fig, ax = plt.subplots()
            ax.plot(df["Year"], df["RentYield"], marker="d", color="purple")
            ax.set_xlabel("Year"); ax.set_ylabel("Rental Yield (%)"); ax.set_title("Trend of Rental Yield vs Year")
            st.pyplot(fig)

        elif chart_type == "Correlation Heatmap":
            st.write("### Correlation Matrix")
            corr = df.corr(numeric_only=True)
            st.dataframe(corr.style.background_gradient(cmap="Blues"))

        st.subheader("⬇️ Download Data")
        csv = df.to_csv(index=False).encode("utf-8")
        st.download_button("Download Dataset (CSV)", data=csv, file_name="EDA_data.csv", mime="text/csv")
    else:
        st.warning("EDA data is empty. Check GitHub CSV URL or network.")

# ----------------------------
# Blog Insights Page
# ----------------------------
elif page == "💬 Blog Insights":
    st.title("🏡 Rent vs Buy — Blog Discussions (Malaysia)")
    df_blog = load_blog_data()

    if not df_blog.empty:
        st.subheader("📋 Blog Data")
        st.dataframe(df_blog)

        # Optional: Filter by keyword
        keyword = st.text_input("Filter by keyword:", "rent buy")
        if keyword:
            df_blog = df_blog[df_blog["Content"].str.contains(keyword, case=False, na=False)]
            if df_blog.empty:
                st.warning(f"No blog posts found containing '{keyword}'.")

        st.subheader("📊 Word Cloud & Top Words")
        ngram_option = st.radio("Show:", ["Unigrams", "Bigrams", "Trigrams"])

        text_series = df_blog["Content"]
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
            st.warning("No text available for Word Cloud / n-gram analysis.")
    else:
        st.warning("Blog CSV file is empty or missing. Please check the GitHub link.")
