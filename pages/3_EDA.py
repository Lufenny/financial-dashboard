import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from wordcloud import WordCloud
from collections import Counter
import nltk
from nltk.corpus import stopwords
import os

# ----------------------------
# NLTK Setup
# ----------------------------
nltk.download('punkt')
nltk.download('stopwords')

# ----------------------------
# Sidebar Navigation
# ----------------------------
st.set_page_config(page_title="EDA & WordCloud", layout="wide")
st.sidebar.title("🔍 Navigation")
page = st.sidebar.radio("Go to:", ["📊 EDA", "☁️ WordCloud"])

# ----------------------------
# Page 1: EDA
# ----------------------------
if page == "📊 EDA":
    st.title("🔎 Exploratory Data Analysis (EDA)")

    uploaded_file = st.file_uploader("Upload your dataset (CSV)", type=["csv"])
    if uploaded_file is not None:
        df = pd.read_csv(uploaded_file)
    elif os.path.exists("Data.csv"):  # fallback to default file
        df = pd.read_csv("Data.csv")
    else:
        st.error("❌ No dataset found. Please upload a CSV file to continue.")
        st.stop()

    # Ensure Year is integer if present
    if "Year" in df.columns:
        df["Year"] = df["Year"].astype(int, errors="ignore")
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
# Page 2: WordCloud + Top Words
# ----------------------------
elif page == "☁️ WordCloud":
    st.title("📝 Rent vs Buy — Blog Word Analysis")

    uploaded_file = st.file_uploader("Upload your blog dataset (CSV with 'Content' column)", type=["csv"])
    if uploaded_file is not None:
        df_text = pd.read_csv(uploaded_file)
    elif os.path.exists("Rent_vs_Buy_Blogs.csv"):  # fallback to default file
        df_text = pd.read_csv("Rent_vs_Buy_Blogs.csv")
    else:
        st.error("❌ No blog dataset found. Please upload a CSV file with a 'Content' column.")
        st.stop()

    if "Content" not in df_text.columns:
        st.error("CSV file must contain a 'Content' column with blog text.")
    else:
        # Combine all blog text
        text_data = " ".join(df_text["Content"].dropna().astype(str))

        # Tokenize & clean using regex
        import re
        tokens = re.findall(r"\b[a-zA-Z]+\b", text_data.lower())

        stop_words = set(stopwords.words("english"))
        cleaned_tokens = [word for word in tokens if word not in stop_words]

        # WordCloud
        wordcloud = WordCloud(width=800, height=400, background_color="white").generate(" ".join(cleaned_tokens))

        # Top words frequency
        word_freq = Counter(cleaned_tokens).most_common(15)
        words, counts = zip(*word_freq)

        # Layout side by side
        col1, col2 = st.columns(2)

        with col1:
            st.subheader("☁️ WordCloud")
            fig_wc, ax_wc = plt.subplots(figsize=(8, 5))
            ax_wc.imshow(wordcloud, interpolation="bilinear")
            ax_wc.axis("off")
            st.pyplot(fig_wc)

        with col2:
            st.subheader("📊 Top Words Frequency")
            fig_bar, ax_bar = plt.subplots(figsize=(6, 5))
            ax_bar.barh(words[::-1], counts[::-1])
            ax_bar.set_xlabel("Count")
            ax_bar.set_ylabel("Word")
            st.pyplot(fig_bar)
