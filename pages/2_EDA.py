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
import io
from fpdf import FPDF

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
# Load Dataset
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
# PDF Helper
# ----------------------------
def save_eda_pdf(df, numeric_cols, categorical_cols, year_col="Year"):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", "B", 16)
    pdf.cell(0, 10, "Exploratory Data Analysis Report", ln=True, align="C")
    
    # Dataset info
    pdf.set_font("Arial", "B", 14)
    pdf.ln(10)
    pdf.cell(0, 10, "Dataset Info", ln=True)
    pdf.set_font("Arial", "", 12)
    for col in df.columns:
        pdf.cell(0, 8, f"{col} ({str(df[col].dtype)})", ln=True)
    
    # Missing values
    pdf.ln(5)
    pdf.set_font("Arial", "B", 14)
    pdf.cell(0, 10, "Missing Values", ln=True)
    pdf.set_font("Arial", "", 12)
    for col, val in df.isna().sum().items():
        pdf.cell(0, 8, f"{col}: {val}", ln=True)
    
    # Numeric descriptive stats
    pdf.ln(5)
    pdf.set_font("Arial", "B", 14)
    pdf.cell(0, 10, "Numeric Descriptive Statistics", ln=True)
    pdf.set_font("Arial", "", 12)
    desc = df[numeric_cols].describe()
    for col in numeric_cols:
        pdf.cell(0, 8, f"{col}: mean={desc[col]['mean']:.2f}, std={desc[col]['std']:.2f}, min={desc[col]['min']}, max={desc[col]['max']}", ln=True)

    # Histograms
    pdf.add_page()
    pdf.set_font("Arial", "B", 14)
    pdf.cell(0, 10, "Numeric Column Histograms", ln=True)
    for col in numeric_cols:
        fig, ax = plt.subplots()
        ax.hist(df[col].dropna(), bins=15, color="skyblue", edgecolor="black")
        ax.set_title(f"Histogram of {col}")
        hist_file = f"{col}_hist.png"
        plt.savefig(hist_file)
        plt.close(fig)
        pdf.image(hist_file, w=180)
    
    # Boxplots
    pdf.add_page()
    pdf.set_font("Arial", "B", 14)
    pdf.cell(0, 10, "Numeric Column Boxplots", ln=True)
    for col in numeric_cols:
        fig, ax = plt.subplots()
        ax.boxplot(df[col].dropna())
        ax.set_title(f"Boxplot of {col}")
        box_file = f"{col}_box.png"
        plt.savefig(box_file)
        plt.close(fig)
        pdf.image(box_file, w=180)
    
    # Categorical charts
    if categorical_cols:
        pdf.add_page()
        pdf.set_font("Arial", "B", 14)
        pdf.cell(0, 10, "Categorical Columns", ln=True)
        for col in categorical_cols:
            fig, ax = plt.subplots()
            df[col].value_counts().plot(kind="bar", ax=ax, color="lightgreen")
            ax.set_title(f"Counts of {col}")
            cat_file = f"{col}_bar.png"
            plt.savefig(cat_file)
            plt.close(fig)
            pdf.image(cat_file, w=180)
    
    # Trends over years
    if year_col in df.columns:
        pdf.add_page()
        pdf.set_font("Arial", "B", 14)
        pdf.cell(0, 10, "Trends Over Years", ln=True)
        year_data = df.dropna(subset=[year_col])
        for col in numeric_cols:
            fig, ax = plt.subplots()
            ax.plot(year_data[year_col], year_data[col], marker="o", linewidth=1)
            ax.set_title(f"{col} Trend")
            trend_file = f"{col}_trend.png"
            plt.savefig(trend_file)
            plt.close(fig)
            pdf.image(trend_file, w=180)
    
    # Correlation heatmap
    if numeric_cols:
        pdf.add_page()
        pdf.set_font("Arial", "B", 14)
        pdf.cell(0, 10, "Correlation Heatmap", ln=True)
        fig, ax = plt.subplots(figsize=(8,6))
        cax = ax.matshow(df[numeric_cols].corr(), cmap="coolwarm")
        plt.xticks(range(len(numeric_cols)), numeric_cols, rotation=45)
        plt.yticks(range(len(numeric_cols)), numeric_cols)
        fig_file = "corr.png"
        plt.colorbar(cax)
        plt.savefig(fig_file)
        plt.close(fig)
        pdf.image(fig_file, w=180)

    pdf_file = "EDA_Full_Report.pdf"
    pdf.output(pdf_file)
    return pdf_file

# ----------------------------
# EDA Page
# ----------------------------
if page == "📊 EDA":
    st.title("🔎 Exploratory Data Analysis (EDA)")

    uploaded_file = st.file_uploader("Upload your dataset (CSV)", type=["csv"])
    df = get_dataset(uploaded_file)

    if df is None:
        st.error("❌ No dataset found.")
        st.stop()

    st.subheader("📋 Dataset Preview")
    st.dataframe(df)

    st.subheader("ℹ️ Dataset Info")
    buffer = io.StringIO()
    df.info(buf=buffer)
    st.text(buffer.getvalue())

    st.subheader("❗ Missing Values Summary")
    st.write(df.isna().sum())

    numeric_cols = df.select_dtypes(include=np.number).columns.tolist()
    categorical_cols = df.select_dtypes(exclude=np.number).columns.tolist()

    st.subheader("📊 Numeric Descriptive Statistics")
    st.write(df.describe(include=[np.number]))

    if st.button("Generate Full EDA PDF Report"):
        pdf_file = save_eda_pdf(df, numeric_cols, categorical_cols)
        with open(pdf_file, "rb") as f:
            st.download_button("⬇️ Download Full EDA PDF", f, file_name=pdf_file, mime="application/pdf")

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
        st.error("❌ No blog dataset found.")
        st.stop()

    if "Content" not in df_text.columns:
        st.error("CSV must have 'Content' column.")
    else:
        text_data = " ".join(df_text["Content"].dropna().astype(str))
        tokens = re.findall(r"\b[a-zA-Z]+\b", text_data.lower())
        stop_words = set(stopwords.words("english")) | {"akan","dan","atau","yang","untuk","dengan","jika"}
        cleaned_tokens = [w for w in tokens if w not in stop_words]

        wordcloud = WordCloud(width=800, height=400, background_color="white").generate(" ".join(cleaned_tokens))
        word_freq = Counter(cleaned_tokens).most_common(15)
        words, counts = zip(*word_freq) if word_freq else ([], [])

        col1, col2 = st.columns(2)
        with col1:
            st.subheader("☁️ WordCloud")
            fig_wc, ax_wc = plt.subplots(figsize=(8,5))
            ax_wc.imshow(wordcloud, interpolation="bilinear")
            ax_wc.axis("off")
            st.pyplot(fig_wc)
        with col2:
            st.subheader("📊 Top Words Frequency")
            fig_bar, ax_bar = plt.subplots(figsize=(6,5))
            if words:
                ax_bar.barh(words[::-1], counts[::-1])
                ax_bar.set_xlabel("Count")
                ax_bar.set_ylabel("Word")
            else:
                ax_bar.text(0.5,0.5,"No words found",ha="center")
            st.pyplot(fig_bar)
