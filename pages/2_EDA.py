import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from wordcloud import WordCloud
from collections import Counter
import nltk
from nltk.corpus import stopwords
import os
import re
from fpdf import FPDF
import io

# ----------------------------
# NLTK Setup
# ----------------------------
try:
    stopwords.words("english")
except LookupError:
    nltk.download('punkt')
    nltk.download('stopwords')

# ----------------------------
# Streamlit App Config
# ----------------------------
st.set_page_config(page_title="Full EDA Dashboard", layout="wide")
st.sidebar.title("🔍 Navigation")
page = st.sidebar.radio("Go to:", ["📊 EDA", "☁️ WordCloud"])

# ----------------------------
# Load dataset
# ----------------------------
@st.cache_data
def load_csv(path):
    return pd.read_csv(path)

def get_dataset(uploaded_file=None, fallback_path="Data.csv"):
    if uploaded_file is not None:
        df = pd.read_csv(uploaded_file)
    elif os.path.exists(fallback_path):
        df = load_csv(fallback_path)
    else:
        return None
    return df

# ----------------------------
# PDF Generation
# ----------------------------
def generate_pdf(df, title="EDA Report"):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", 'B', 16)
    pdf.cell(0, 10, title, ln=True, align="C")
    pdf.set_font("Arial", '', 12)
    pdf.ln(10)

    pdf.cell(0, 10, "Dataset Preview (first 10 rows):", ln=True)
    pdf.ln(5)
    for i, row in df.head(10).iterrows():
        pdf.multi_cell(0, 8, str(row.to_dict()))
        pdf.ln(2)

    pdf.ln(5)
    pdf.cell(0, 10, "Descriptive Statistics (numeric columns):", ln=True)
    pdf.ln(5)
    pdf.multi_cell(0, 8, str(df.describe(include=[np.number])))

    return pdf.output(dest="S").encode("latin1")

# ----------------------------
# EDA Page
# ----------------------------
if page == "📊 EDA":
    st.title("🔎 Exploratory Data Analysis (EDA)")

    uploaded_file = st.file_uploader("Upload your dataset (CSV)", type=["csv"])
    df = get_dataset(uploaded_file)

    if df is None:
        st.error("❌ No dataset found. Please upload a CSV file or place 'Data.csv' in working directory.")
        st.stop()

    # Dataset preview
    st.subheader("📋 Dataset Preview")
    st.dataframe(df.head(10))

    st.subheader("ℹ️ Dataset Info")
    buffer = io.StringIO()
    df.info(buf=buffer)
    st.text(buffer.getvalue())

    st.subheader("❗ Missing Values Summary")
    st.write(df.isna().sum())

    st.subheader("📊 Numeric Descriptive Statistics")
    st.write(df.describe(include=[np.number]))

    numeric_cols = df.select_dtypes(include=np.number).columns.tolist()
    categorical_cols = df.select_dtypes(exclude=np.number).columns.tolist()

    # Numeric distributions
    st.subheader("📈 Numeric Distributions")
    for col in numeric_cols:
        fig, ax = plt.subplots()
        ax.hist(df[col].dropna(), bins=15, color="skyblue", edgecolor="black")
        ax.set_title(f"Distribution of {col}")
        st.pyplot(fig)

    # Boxplots
    st.subheader("📦 Boxplots (Outliers)")
    for col in numeric_cols:
        fig, ax = plt.subplots()
        ax.boxplot(df[col].dropna(), vert=True)
        ax.set_title(f"Boxplot of {col}")
        st.pyplot(fig)

    # Categorical analysis
    if categorical_cols:
        st.subheader("📊 Categorical Columns Analysis")
        for col in categorical_cols:
            fig, ax = plt.subplots()
            df[col].value_counts().plot(kind="bar", ax=ax, color="lightgreen")
            ax.set_title(f"Counts of {col}")
            st.pyplot(fig)

    # Trends over Year
    if "Year" in df.columns:
        st.subheader("📈 Trends Over Years")
        df["Year"] = pd.to_numeric(df["Year"], errors="coerce")
        df = df.dropna(subset=["Year"])
        df["Year"] = df["Year"].astype(int)

        year_min, year_max = int(df["Year"].min()), int(df["Year"].max())
        y0, y1 = st.slider("Select Year Range", year_min, year_max, (year_min, year_max))

        df_year = df[(df["Year"] >= y0) & (df["Year"] <= y1)]
        chart_cols = st.multiselect("Select numeric columns to plot trends", numeric_cols, default=numeric_cols)
        for col in chart_cols:
            fig, ax = plt.subplots()
            ax.plot(df_year["Year"], df_year[col], marker="o", linewidth=1)
            ax.set_xlabel("Year")
            ax.set_ylabel(col)
            ax.set_title(f"Trend of {col} ({y0}-{y1})")
            ax.grid(alpha=0.2)
            st.pyplot(fig)

    # Correlation heatmap
    if numeric_cols:
        st.subheader("🧩 Correlation Matrix")
        corr = df[numeric_cols].corr()
        fig, ax = plt.subplots(figsize=(8, 6))
        cax = ax.matshow(corr, cmap="coolwarm")
        plt.xticks(range(len(numeric_cols)), numeric_cols, rotation=45)
        plt.yticks(range(len(numeric_cols)), numeric_cols)
        fig.colorbar(cax)
        st.pyplot(fig)

    # PDF download
    st.subheader("⬇️ Download EDA Report as PDF")
    pdf_bytes = generate_pdf(df)
    st.download_button("Download PDF", data=pdf_bytes, file_name="EDA_Report.pdf", mime="application/pdf")

# ----------------------------
# WordCloud Page
# ----------------------------
elif page == "☁️ WordCloud":
    st.title("📝 Text Analysis & WordCloud")

    uploaded_file = st.file_uploader("Upload your blog dataset (CSV with 'Content' column)", type=["csv"], key="wc")
    if uploaded_file is not None:
        df_text = pd.read_csv(uploaded_file)
    elif os.path.exists("Rent_vs_Buy_Blogs.csv"):
        df_text = pd.read_csv("Rent_vs_Buy_Blogs.csv")
    else:
        st.error("❌ No blog dataset found. Upload CSV with 'Content' column.")
        st.stop()

    if "Content" not in df_text.columns:
        st.error("CSV must have a 'Content' column with text.")
    else:
        text_data = " ".join(df_text["Content"].dropna().astype(str))
        tokens = re.findall(r"\b[a-zA-Z]+\b", text_data.lower())
        stop_words = set(stopwords.words("english")) | {"akan", "dan", "atau", "yang", "untuk", "dengan", "jika"}
        cleaned_tokens = [w for w in tokens if w not in stop_words]

        wordcloud = WordCloud(width=800, height=400, background_color="white").generate(" ".join(cleaned_tokens))
        word_freq = Counter(cleaned_tokens).most_common(15)
        words, counts = zip(*word_freq) if word_freq else ([], [])

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
            if words:
                ax_bar.barh(words[::-1], counts[::-1])
                ax_bar.set_xlabel("Count")
                ax_bar.set_ylabel("Word")
            else:
                ax_bar.text(0.5, 0.5, "No words found", ha="center")
            st.pyplot(fig_bar)
