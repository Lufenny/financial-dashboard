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
page = st.sidebar.radio("Go to:", ["Expected Outcomes", "📑 Analysis", "📊 EDA", "☁️ WordCloud", "⚙️ Data Process"])

# ----------------------------
# Page 1: Expected Outcomes
# ----------------------------
if page == "Expected Outcomes":
    st.title("🎯 Expected Outcomes")
    st.markdown("""
    - Compare **Rent vs Buy** scenarios  
    - Identify long-term financial implications  
    - Explore sensitivity to key assumptions  
    - Summarize results with clear visualizations  
    """)

# ----------------------------
# Page 2: Analysis
# ----------------------------
elif page == "📑 Analysis":
    st.title("📑 Scenario Comparison")
    st.markdown("Compare different financial scenarios side by side.")

    # Example scenario table
    scenarios = pd.DataFrame({
        "Scenario": ["Renting", "Buying (Loan)", "Buying (Cash)"],
        "Total Cost (RM)": [800000, 950000, 900000],
        "Net Worth (RM)": [500000, 1200000, 1100000]
    })
    st.dataframe(scenarios)

    st.markdown("This helps visualize trade-offs between renting and buying.")

# ----------------------------
# Page 3: EDA
# ----------------------------
elif page == "📊 EDA":
    st.title("📊 Exploratory Data Analysis")

    # Example dataset
    df = pd.DataFrame({
        "Year": np.arange(2025, 2035),
        "Rent Cost": np.linspace(20000, 35000, 10),
        "Buy Cost": np.linspace(25000, 40000, 10)
    })
    st.write("### Sample Dataset")
    st.dataframe(df)

    # Plotting
    fig, ax = plt.subplots()
    ax.plot(df["Year"], df["Rent Cost"], label="Rent Cost")
    ax.plot(df["Year"], df["Buy Cost"], label="Buy Cost")
    ax.set_xlabel("Year")
    ax.set_ylabel("Annual Cost (RM)")
    ax.legend()
    st.pyplot(fig)

# ----------------------------
# Page 4: WordCloud + Top Words
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

# ----------------------------
# Page 5: Data Process
# ----------------------------
elif page == "⚙️ Data Process":
    st.title("⚙️ Data Processing Steps")
    st.markdown("""
    - Clean raw financial datasets  
    - Handle missing values  
    - Merge rent and buy cost data  
    - Prepare for modeling & scenario analysis  
    """)
