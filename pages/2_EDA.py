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
# Helper: PDF Generation
# ----------------------------
def create_eda_pdf(df, numeric_cols, categorical_cols, df_year=None, year_cols=None, df_wordcloud=None):
    pdf = FPDF()
    pdf.set_auto_page_break(auto=True, margin=15)
    
    # ---------------- Title ----------------
    pdf.add_page()
    pdf.set_font("Arial", 'B', 16)
    pdf.cell(0, 10, "Exploratory Data Analysis Report", ln=True, align="C")
    
    pdf.set_font("Arial", '', 12)
    pdf.ln(5)
    pdf.multi_cell(0, 8, f"Rows: {df.shape[0]}, Columns: {df.shape[1]}")
    
    # ---------------- Missing Values ----------------
    pdf.ln(5)
    pdf.set_font("Arial", 'B', 12)
    pdf.cell(0, 8, "Missing Values Summary", ln=True)
    pdf.set_font("Arial", '', 10)
    for col, count in df.isna().sum().items():
        pdf.cell(0, 6, f"{col}: {count}", ln=True)
    
    # ---------------- Numeric Descriptive Statistics ----------------
    pdf.add_page()
    pdf.set_font("Arial", 'B', 12)
    pdf.cell(0, 8, "Numeric Summary Statistics", ln=True)
    pdf.set_font("Arial", '', 10)
    summary = df[numeric_cols].describe()
    for i, row in summary.iterrows():
        pdf.cell(0, 6, f"{i}: {row.to_dict()}", ln=True)
    
    # ---------------- Numeric Histograms ----------------
    for col in numeric_cols:
        fig, ax = plt.subplots()
        ax.hist(df[col].dropna(), bins=15, color="skyblue", edgecolor="black")
        ax.set_title(f"Distribution of {col}")
        img_bytes = io.BytesIO()
        plt.savefig(img_bytes, format='png')
        plt.close(fig)
        img_bytes.seek(0)
        pdf.add_page()
        pdf.image(img_bytes, x=10, y=20, w=180)
    
    # ---------------- Boxplots ----------------
    for col in numeric_cols:
        fig, ax = plt.subplots()
        ax.boxplot(df[col].dropna(), vert=True)
        ax.set_title(f"Boxplot of {col}")
        img_bytes = io.BytesIO()
        plt.savefig(img_bytes, format='png')
        plt.close(fig)
        img_bytes.seek(0)
        pdf.add_page()
        pdf.image(img_bytes, x=10, y=20, w=180)
    
    # ---------------- Categorical Columns ----------------
    for col in categorical_cols:
        fig, ax = plt.subplots()
        df[col].value_counts().plot(kind="bar", ax=ax, color="lightgreen")
        ax.set_title(f"Counts of {col}")
        img_bytes = io.BytesIO()
        plt.savefig(img_bytes, format='png')
        plt.close(fig)
        img_bytes.seek(0)
        pdf.add_page()
        pdf.image(img_bytes, x=10, y=20, w=180)
    
    # ---------------- Yearly Trends ----------------
    if df_year is not None and year_cols:
        for col in year_cols:
            fig, ax = plt.subplots()
            ax.plot(df_year["Year"], df_year[col], marker="o", linewidth=1)
            ax.set_xlabel("Year")
            ax.set_ylabel(col)
            ax.set_title(f"Trend of {col} ({df_year['Year'].min()}-{df_year['Year'].max()})")
            ax.grid(alpha=0.2)
            img_bytes = io.BytesIO()
            plt.savefig(img_bytes, format='png')
            plt.close(fig)
            img_bytes.seek(0)
            pdf.add_page()
            pdf.image(img_bytes, x=10, y=20, w=180)
    
    # ---------------- Correlation Heatmap ----------------
    if numeric_cols:
        corr = df[numeric_cols].corr()
        fig, ax = plt.subplots(figsize=(8,6))
        cax = ax.matshow(corr, cmap="coolwarm")
        plt.xticks(range(len(numeric_cols)), numeric_cols, rotation=45)
        plt.yticks(range(len(numeric_cols)), numeric_cols)
        fig.colorbar(cax)
        img_bytes = io.BytesIO()
        plt.savefig(img_bytes, format='png')
        plt.close(fig)
        img_bytes.seek(0)
        pdf.add_page()
        pdf.image(img_bytes, x=10, y=20, w=180)
    
    # ---------------- WordCloud ----------------
    if df_wordcloud is not None:
        text_data = " ".join(df_wordcloud.dropna().astype(str))
        wordcloud = WordCloud(width=800, height=400, background_color="white").generate(text_data)
        fig, ax = plt.subplots(figsize=(8,5))
        ax.imshow(wordcloud, interpolation="bilinear")
        ax.axis("off")
        img_bytes = io.BytesIO()
        plt.savefig(img_bytes, format='png')
        plt.close(fig)
        img_bytes.seek(0)
        pdf.add_page()
        pdf.image(img_bytes, x=10, y=20, w=180)
    
    return pdf

# ----------------------------
# Page 1: EDA
# ----------------------------
if page == "📊 EDA":
    st.title("🔎 Exploratory Data Analysis (EDA)")
    uploaded_file = st.file_uploader("Upload your dataset (CSV)", type=["csv"])
    df = get_dataset(uploaded_file)
    
    if df is None:
        st.error("❌ No dataset found. Upload a CSV or place 'Data.csv' in working directory.")
        st.stop()
    
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
    
    # Trends over years
    df_year = None
    year_cols = []
    if "Year" in df.columns:
        st.subheader("📈 Trends Over Years")
        df["Year"] = pd.to_numeric(df["Year"], errors="coerce")
        df = df.dropna(subset=["Year"])
        df["Year"] = df["Year"].astype(int)
        year_min, year_max = int(df["Year"].min()), int(df["Year"].max())
        y0, y1 = st.slider("Select Year Range", year_min, year_max, (year_min, year_max))
        df_year = df[(df["Year"] >= y0) & (df["Year"] <= y1)]
        year_cols = st.multiselect("Select numeric columns to plot trends", numeric_cols, default=numeric_cols)
        for col in year_cols:
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
        fig, ax = plt.subplots(figsize=(8,6))
        cax = ax.matshow(corr, cmap="coolwarm")
        plt.xticks(range(len(numeric_cols)), numeric_cols, rotation=45)
        plt.yticks(range(len(numeric_cols)), numeric_cols)
        fig.colorbar(cax)
        st.pyplot(fig)
    
    # PDF download
    if st.button("📄 Download Full EDA PDF"):
        pdf = create_eda_pdf(df, numeric_cols, categorical_cols, df_year=df_year, year_cols=year_cols)
        pdf_bytes = pdf.output(dest='S').encode('latin1')
        st.download_button("Download EDA PDF", data=pdf_bytes, file_name="EDA_report.pdf", mime="application/pdf")

# ----------------------------
# Page 2: WordCloud
# ----------------------------
elif page == "☁️ WordCloud":
    st.title("📝 Text Analysis & WordCloud")
    uploaded_file = st.file_uploader("Upload blog CSV ('Content' column)", type=["csv"], key="wc")
    
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
        stop_words = set(stopwords.words("english")) | {"akan","dan","atau","yang","untuk","dengan","jika"}
        cleaned_tokens = [w for w in tokens if w not in stop_words]

        # WordCloud
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
        
        # PDF download with WordCloud
        if st.button("📄 Download Full EDA + WordCloud PDF"):
            pdf = create_eda_pdf(df=pd.DataFrame(), numeric_cols=[], categorical_cols=[], df_wordcloud=df_text["Content"])
            pdf_bytes = pdf.output(dest='S').encode('latin1')
            st.download_button("Download PDF", data=pdf_bytes, file_name="EDA_WordCloud.pdf", mime="application/pdf")
