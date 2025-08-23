import streamlit as st
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from wordcloud import WordCloud
from collections import Counter
import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize

# ----------------------------
# NLTK Setup
# ----------------------------
nltk.download('punkt')
nltk.download('stopwords')

# ----------------------------
# Sidebar Navigation
# ----------------------------
page = st.sidebar.radio("Go to:", ["EDA", "WordCloud"])

# ----------------------------
# Page 1: EDA
# ----------------------------
if page == "EDA":
    st.title("🎯 Expected Outcomes")
    st.markdown("""
    - Compare **Rent vs Buy** scenarios  
    - Identify long-term financial implications  
    - Explore sensitivity to key assumptions  
    - Summarize results with clear visualizations  
    """)


# ----------------------------
# Page 2: WordCloud + Top Words
# ----------------------------
elif page == "☁️ WordCloud":
    st.title("📝 Rent vs Buy — Blog Word Analysis")

    file_path = "Rent_vs_Buy_Blogs.csv"
    df_text = pd.read_csv(file_path)

    # Use correct column
    if "Content" not in df_text.columns:
        st.error("CSV file must contain a 'Content' column with blog text.")
    else:
        # Combine all blog text
        text_data = " ".join(df_text["Content"].dropna().astype(str))

        # Tokenize & clean using regex (safe for Streamlit Cloud)
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

