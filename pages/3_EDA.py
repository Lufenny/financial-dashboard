import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from wordcloud import WordCloud
from collections import Counter
import nltk
from nltk.corpus import stopwords
import os
import re
import numpy as np

# ----------------------------
# NLTK Setup (download if missing)
# ----------------------------
try:
    stopwords.words("english")
except Exception:
    with st.spinner("Downloading NLTK data..."):
        nltk.download('punkt')
        nltk.download('stopwords')

# ----------------------------
# App config + Sidebar Navigation
# ----------------------------
st.set_page_config(page_title="EDA & WordCloud", layout="wide")
st.sidebar.title("🔍 Navigation")
page = st.sidebar.radio("Go to:", ["📊 EDA", "☁️ WordCloud"])

# ----------------------------
# Helper: load dataset (from upload or fallback file)
# ----------------------------
@st.cache_data
def load_csv_from_path(path):
    return pd.read_csv(path)

def load_dataset(uploaded_file=None, fallback_path="Data.csv"):
    if uploaded_file is not None:
        df = pd.read_csv(uploaded_file)
    elif os.path.exists(fallback_path):
        df = load_csv_from_path(fallback_path)
    else:
        return None
    return df

# ----------------------------
# Page 1: EDA
# ----------------------------
if page == "📊 EDA":
    st.title("🔎 Exploratory Data Analysis (EDA) — Full dataset period support")

    uploaded_file = st.file_uploader("Upload your dataset (CSV)", type=["csv"])
    df = load_dataset(uploaded_file, fallback_path="Data.csv")

    if df is None:
        st.error("❌ No dataset found. Please upload a CSV file (or place Data.csv in the working directory).")
        st.stop()

    # Ensure Year column is numeric integer if present
    if "Year" in df.columns:
        df["Year"] = pd.to_numeric(df["Year"], errors="coerce")
        df = df.dropna(subset=["Year"]).copy()
        df["Year"] = df["Year"].astype(int)
    else:
        st.warning("Dataset has no 'Year' column — charts by year will be disabled. You can continue with the wordcloud page.")
    
    # Show dataset span info (full period)
    if "Year" in df.columns and len(df) > 0:
        year_min = int(df["Year"].min())
        year_max = int(df["Year"].max())
        span_years = year_max - year_min + 1
        st.markdown(f"**Dataset period:** {year_min} — {year_max}  (_{span_years} years total_)")
        # short validation message to replace the old 2010–2014 wording
        st.info(f"The EDA below now uses the full available period ({year_min}—{year_max}). If your earlier draft referenced 2010–2014 only, this interactive analysis will show the full-span behaviour for OPR, EPF, price growth and rent yields.")
    else:
        year_min = year_max = None

    # Data Preview
    st.subheader("📋 Data Preview")
    st.dataframe(df.reset_index(drop=True))

    # Summary Statistics
    st.subheader("📊 Summary Statistics (numeric columns)")
    st.write(df.describe(include=[np.number]))

    # If Year exists, let user select subset of years to visualize
    if year_min is not None:
        st.subheader("📈 Visual Analysis (select year range)")
        y0, y1 = st.slider("Select Year Range", min_value=year_min, max_value=year_max, value=(year_min, year_max), step=1)
        df_plot = df[(df["Year"] >= y0) & (df["Year"] <= y1)].copy()
    else:
        st.subheader("📈 Visual Analysis")
        df_plot = df.copy()

    # Chart Selector
    chart_type = st.selectbox(
        "Select a chart to display:",
        ["OPR vs Year", "EPF vs Year", "Price Growth vs Year", "Rent Yield vs Year", "Correlation Heatmap"]
    )

    # Utility to plot a simple line if column exists
    def plot_line(year_col, value_col, ylabel, title):
        if year_col not in df_plot.columns or value_col not in df_plot.columns:
            st.warning(f"Missing column: '{value_col}'. Available columns: {', '.join(df_plot.columns)}")
            return
        fig, ax = plt.subplots()
        ax.plot(df_plot[year_col], df_plot[value_col], marker="o", linewidth=1)
        ax.set_xlabel("Year")
        ax.set_ylabel(ylabel)
        ax.set_title(title)
        ax.grid(alpha=0.2)
        st.pyplot(fig)

    if chart_type == "OPR vs Year":
        plot_line("Year", "OPR_avg", "OPR (%)", f"Trend of OPR ({y0}–{y1})" if year_min else "Trend of OPR")
        # add a short automated observation (basic)
        if "OPR_avg" in df_plot.columns and "Year" in df_plot.columns:
            start, end = float(df_plot["OPR_avg"].iloc[0]), float(df_plot["OPR_avg"].iloc[-1])
            st.write(f"**Observation:** OPR changed from {start:.2f}% to {end:.2f}% between {df_plot['Year'].iloc[0]} and {df_plot['Year'].iloc[-1]} (selected range).")

    elif chart_type == "EPF vs Year":
        plot_line("Year", "EPF", "EPF Dividend (%)", f"Trend of EPF Dividend ({y0}–{y1})" if year_min else "Trend of EPF Dividend")

    elif chart_type == "Price Growth vs Year":
        plot_line("Year", "PriceGrowth", "Price Growth (%)", f"Trend of Property Price Growth ({y0}–{y1})" if year_min else "Trend of Property Price Growth")

    elif chart_type == "Rent Yield vs Year":
        plot_line("Year", "RentYield", "Rental Yield (%)", f"Trend of Rental Yield ({y0}–{y1})" if year_min else "Trend of Rental Yield")

    elif chart_type == "Correlation Heatmap":
        st.write("### Correlation Matrix (numeric columns)")
        corr = df_plot.corr(numeric_only=True)
        if corr.empty:
            st.write("No numeric columns available to compute correlations.")
        else:
            fig, ax = plt.subplots(figsize=(8, 6))
            im = ax.imshow(corr.values, cmap="Blues", vmin=-1, vmax=1)
            ax.set_xticks(np.arange(len(corr.columns)))
            ax.set_yticks(np.arange(len(corr.index)))
            ax.set_xticklabels(corr.columns, rotation=45, ha="right")
            ax.set_yticklabels(corr.index)
            # annotate
            for i in range(len(corr.index)):
                for j in range(len(corr.columns)):
                    val = corr.values[i, j]
                    ax.text(j, i, f"{val:.2f}", ha="center", va="center", fontsize=8, color="black")
            fig.colorbar(im, ax=ax, fraction=0.046, pad=0.04)
            ax.set_title(f"Correlation matrix ({y0}–{y1})" if year_min else "Correlation matrix")
            plt.tight_layout()
            st.pyplot(fig)

    # Download filtered/exported data
    st.subheader("⬇️ Download Data")
    csv_bytes = df_plot.to_csv(index=False).encode("utf-8")
    st.download_button("Download Filtered Dataset (CSV)", data=csv_bytes, file_name="EDA_data_filtered.csv", mime="text/csv")

# ----------------------------
# Page 2: WordCloud + Top Words
# ----------------------------
elif page == "☁️ WordCloud":
    st.title("📝 Rent vs Buy — Blog Word Analysis")

    uploaded_file = st.file_uploader("Upload your blog dataset (CSV with 'Content' column)", type=["csv"], key="wc")
    if uploaded_file is not None:
        df_text = pd.read_csv(uploaded_file)
    elif os.path.exists("Rent_vs_Buy_Blogs.csv"):
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
        tokens = re.findall(r"\b[a-zA-Z]+\b", text_data.lower())

        stop_words = set(stopwords.words("english"))
        cleaned_tokens = [word for word in tokens if word not in stop_words]

        # WordCloud
        wordcloud = WordCloud(width=800, height=400, background_color="white").generate(" ".join(cleaned_tokens))

        # Top words frequency
        word_freq = Counter(cleaned_tokens).most_common(15)
        if len(word_freq) > 0:
            words, counts = zip(*word_freq)
        else:
            words, counts = [], []

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
            if words:
                ax_bar.barh(words[::-1], counts[::-1])
                ax_bar.set_xlabel("Count")
                ax_bar.set_ylabel("Word")
            else:
                ax_bar.text(0.5, 0.5, "No words found", ha="center")
            st.pyplot(fig_bar)
