import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from wordcloud import WordCloud
import nltk
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords

# Download nltk resources
nltk.download("punkt", quiet=True)
nltk.download("stopwords", quiet=True)

st.title("📊 Exploratory Data Analysis (EDA)")

# ========================
# SECTION A: Rent vs Buy EDA
# ========================
st.header("🏡 Rent vs Buy Dataset")

@st.cache_data
def load_main_data():
    file_path = "Buy_vs_Rent_KL_FullModel.xlsx"   # adjust if needed
    return pd.read_excel(file_path, sheet_name="Annual_Summary")

try:
    df_main = load_main_data()
    st.success("✅ Main Rent vs Buy dataset loaded!")
    st.dataframe(df_main.head())
except Exception as e:
    st.error(f"⚠️ Could not load main dataset.\n\n{e}")
    st.stop()

# ---- Summary Statistics ----
st.subheader("📈 Summary Statistics")
st.write(df_main.describe())

# ---- Rent vs Buy Cumulative Chart ----
st.subheader("📊 Cumulative Rent vs Buy Costs")
if "Cumulative Rent" in df_main.columns and "Cumulative Buy" in df_main.columns:
    st.line_chart(df_main[["Cumulative Rent", "Cumulative Buy"]])

# ---- Scenario Comparison ----
st.subheader("⚖️ Scenario Comparison")
if "Scenario" in df_main.columns:
    scenario_summary = df_main.groupby("Scenario")[["Cumulative Rent", "Cumulative Buy"]].last()
    st.bar_chart(scenario_summary)

# ---- Sensitivity Analysis ----
st.subheader("🧪 Sensitivity Analysis")
if "Monthly Contribution" in df_main.columns and "Final Wealth" in df_main.columns:
    sensitivity = df_main.groupby("Monthly Contribution")["Final Wealth"].mean()
    st.line_chart(sensitivity)

# ========================
# SECTION B: Blog Insights
# ========================
st.header("📰 Blog Insights: Rent vs Buy in Malaysia")

@st.cache_data
def load_blog_data():
    url = "https://raw.githubusercontent.com/Lufenny/financial-dashboard/main/Rent_vs_Buy_Blogs.csv"
    return pd.read_csv(url)

try:
    df_blog = load_blog_data()
    st.success("✅ Blog CSV loaded!")
    st.dataframe(df_blog)
except Exception as e:
    st.error(f"⚠️ Could not load blog CSV.\n\n{e}")
    st.stop()

# ---- Preprocess Blog Text ----
def preprocess_text(series):
    text = " ".join(series.dropna().astype(str))
    tokens = word_tokenize(text.lower())
    stop_words = set(stopwords.words("english"))
    tokens = [w for w in tokens if w.isalpha() and w not in stop_words]
    return " ".join(tokens)

# ---- Word Cloud ----
st.subheader("☁️ Word Cloud from Blogs")
all_text = preprocess_text(df_blog["Content"])
if all_text.strip():
    wc = WordCloud(width=800, height=400, background_color="white").generate(all_text)
    fig, ax = plt.subplots(figsize=(10, 5))
    ax.imshow(wc, interpolation="bilinear")
    ax.axis("off")
    st.pyplot(fig)

# ---- Blog Category Counts ----
st.subheader("📊 Blog Category Distribution")
if "Category" in df_blog.columns:
    st.bar_chart(df_blog["Category"].value_counts())
