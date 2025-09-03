import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from wordcloud import WordCloud
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image as RLImage
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import inch

# --------------------------
# 1. Global Settings
# --------------------------
st.set_page_config(page_title="📊 Combined Financial & Text Insights", layout="wide")

# --------------------------
# 2. Simulated Financial Data
# --------------------------
years = np.arange(2024, 2034)
buy_wealth = np.cumsum(np.random.randint(20, 80, size=len(years))) * 1000
rent_invest_wealth = np.cumsum(np.random.randint(25, 70, size=len(years))) * 1000

df_numeric = pd.DataFrame({
    "Year": years,
    "Net_Wealth_Buy": buy_wealth,
    "Net_Wealth_Rent": rent_invest_wealth
})

# --------------------------
# 3. Simulated Text Data
# --------------------------
sample_text = """
buying a house can be rewarding but renting offers flexibility.
investment in property is long-term but rent allows liquidity.
financial planning is crucial when deciding to buy or rent.
"""
wordcloud = WordCloud(width=800, height=400, background_color="white").generate(sample_text)

words = sample_text.split()
word_freq = pd.Series(words).value_counts().head(10).reset_index()
word_freq.columns = ["Word", "Count"]

# --------------------------
# 4. Streamlit Display
# --------------------------
st.title("📊 Combined Financial & Text Insights")

# Financial Chart
st.subheader("📈 Buy vs Rent + Invest Wealth Curve")
fig, ax = plt.subplots(figsize=(7, 4))
ax.plot(df_numeric["Year"], df_numeric["Net_Wealth_Buy"], label="Buy", marker="o")
ax.plot(df_numeric["Year"], df_numeric["Net_Wealth_Rent"], label="Rent + Invest", marker="o")
ax.set_xlabel("Year")
ax.set_ylabel("Net Wealth (RM)")
ax.set_title("Net Wealth Over Time")
ax.legend()
st.pyplot(fig)

# WordCloud
st.subheader("☁️ WordCloud of Text Data")
fig_wc, ax_wc = plt.subplots(figsize=(7, 4))
ax_wc.imshow(wordcloud, interpolation="bilinear")
ax_wc.axis("off")
st.pyplot(fig_wc)

# Top Words
st.subheader("🔝 Top 10 Words Frequency")
fig_bar, ax_bar = plt.subplots(figsize=(7, 4))
ax_bar.barh(word_freq["Word"][::-1], word_freq["Count"][::-1], color="teal")
ax_bar.set_xlabel("Count")
ax_bar.set_ylabel("Word")
st.pyplot(fig_bar)

# Insights
st.subheader("💡 Insights & Recommendations")
insights = [
    "1. Buying builds equity long-term, but short-term costs are higher.",
    "2. Renting with disciplined investment can outperform buying in certain cases.",
    "3. Results are sensitive to interest rates, rent growth, and investment returns.",
    "4. Decision depends on personal goals, risk tolerance, and financial discipline."
]
for ins in insights:
    st.write(f"- {ins}")

# Sources
st.subheader("📚 Sources")
sources = [
    "https://www.greateasternlife.com/my/en/personal-insurance/greatpedia/live-great-reads/wellbeing-and-success/should-you-buy-or-rent-a-property-in-malaysia.html",
    "https://www.kwsp.gov.my/en/w/article/buy-vs-rent-malaysia",
    "https://www.iproperty.com.my/guides/should-buy-or-rent-property-malaysia-30437"
]
for url in sources:
    st.markdown(f"- [{url}]({url})")

# --------------------------
# 5. PDF Export Function
# --------------------------
def save_combined_pdf(df_numeric, wordcloud, word_freq, insights, sources,
                      include_wealth=True, include_wordcloud=True,
                      include_topwords=True, include_insights=True,
                      include_sources=True):

    pdf_file = "Combined_Insights_Report.pdf"
    doc = SimpleDocTemplate(pdf_file, pagesize=A4)
    story = []
    styles = getSampleStyleSheet()

    # Title
    story.append(Paragraph("<b>Combined Insights Report</b>", styles["Title"]))
    story.append(Spacer(1, 0.2 * inch))

    # Wealth Curve
    if include_wealth:
        fig, ax = plt.subplots(figsize=(7, 4))
        ax.plot(df_numeric["Year"], df_numeric["Net_Wealth_Buy"], label="Buy", marker="o")
        ax.plot(df_numeric["Year"], df_numeric["Net_Wealth_Rent"], label="Rent + Invest", marker="o")
        ax.set_xlabel("Year")
        ax.set_ylabel("Net Wealth (RM)")
        ax.set_title("Net Wealth Over Time")
        ax.legend()
        wealth_file = "wealth_curve.png"
        plt.savefig(wealth_file)
        plt.close(fig)
        story.append(Paragraph("<b>Buy vs Rent + Invest Wealth</b>", styles["Heading2"]))
        story.append(RLImage(wealth_file, width=6*inch, height=3*inch))
        story.append(Spacer(1, 0.3 * inch))

    # WordCloud
    if include_wordcloud:
        wordcloud_file = "wordcloud.png"
        wordcloud.to_file(wordcloud_file)
        story.append(Paragraph("<b>WordCloud of Text Data</b>", styles["Heading2"]))
        story.append(RLImage(wordcloud_file, width=6*inch, height=3*inch))
        story.append(Spacer(1, 0.3 * inch))

    # Top Words
    if include_topwords:
        fig_bar, ax_bar = plt.subplots(figsize=(7, 4))
        ax_bar.barh(word_freq["Word"][::-1], word_freq["Count"][::-1], color="teal")
        ax_bar.set_xlabel("Count")
        ax_bar.set_ylabel("Word")
        bar_file = "top_words.png"
        plt.savefig(bar_file)
        plt.close(fig_bar)
        story.append(Paragraph("<b>Top Words Frequency</b>", styles["Heading2"]))
        story.append(RLImage(bar_file, width=6*inch, height=3*inch))
        story.append(Spacer(1, 0.3 * inch))

    # Insights
    if include_insights:
        story.append(Paragraph("<b>Insights & Recommendations</b>", styles["Heading2"]))
        for ins in insights:
            story.append(Paragraph(ins, styles["Normal"]))
            story.append(Spacer(1, 0.05 * inch))

    # Sources
    if include_sources:
        story.append(Paragraph("<b>Sources</b>", styles["Heading2"]))
        for url in sources:
            story.append(Paragraph(f"- {url}", styles["Normal"]))
            story.append(Spacer(1, 0.05 * inch))

    doc.build(story)
    return pdf_file

# --------------------------
# 6. Streamlit PDF Export Button
# --------------------------
if st.button("📄 Export Combined PDF Report"):
    pdf_path = save_combined_pdf(df_numeric, wordcloud, word_freq, insights, sources)
    with open(pdf_path, "rb") as f:
        st.download_button("⬇️ Download PDF", f, file_name="Combined_Insights_Report.pdf")
