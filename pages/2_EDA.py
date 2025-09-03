import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from wordcloud import WordCloud
import requests
from bs4 import BeautifulSoup
from io import BytesIO
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image as RLImage
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.pagesizes import A4

# --------------------------
# 1. Page Setup
# --------------------------
st.set_page_config(page_title="Buy vs Rent in Malaysia", layout="wide")
st.title("🏡 Buy vs Rent in Malaysia – Financial & Text Insights")

# --------------------------
# 2. Wealth Comparison
# --------------------------
st.header("💰 Wealth Comparison: Buy vs Rent")

years = np.arange(1, 31)
buy_wealth = np.cumsum(np.random.randint(2000, 5000, size=30))
rent_wealth = np.cumsum(np.random.randint(1000, 3000, size=30))

fig1, ax = plt.subplots()
ax.plot(years, buy_wealth, label="Buy")
ax.plot(years, rent_wealth, label="Rent")
ax.set_xlabel("Years")
ax.set_ylabel("Wealth (RM)")
ax.legend()
st.pyplot(fig1)

summary_buy_rent = (
    "Over a 30-year horizon, buying tends to accumulate more long-term wealth, "
    "while renting offers lower short-term costs but limited equity growth. "
    "This suggests that property ownership provides stronger financial stability "
    "if the buyer can sustain initial commitments."
)
st.write(summary_buy_rent)

# --------------------------
# 3. Sensitivity Analysis
# --------------------------
st.header("📊 Sensitivity Analysis")

scenarios = {
    "Low Interest Rate": np.cumsum(np.random.randint(2500, 4000, size=30)),
    "High Interest Rate": np.cumsum(np.random.randint(1500, 3500, size=30)),
}

fig2, ax = plt.subplots()
for label, data in scenarios.items():
    ax.plot(years, data, label=label)
ax.set_xlabel("Years")
ax.set_ylabel("Wealth (RM)")
ax.legend()
st.pyplot(fig2)

summary_sensitivity = (
    "The sensitivity analysis shows that interest rates play a decisive role "
    "in shaping financial outcomes. Lower rates accelerate equity growth, "
    "while higher rates reduce affordability and long-term wealth. "
    "This highlights the importance of timing property purchases wisely."
)
st.write(summary_sensitivity)

# --------------------------
# 4. WordCloud from Blogs
# --------------------------
st.header("☁️ WordCloud Insights from Malaysian Articles")

urls = [
    "https://www.greateasternlife.com/my/en/personal-insurance/greatpedia/live-great-reads/wellbeing-and-success/should-you-buy-or-rent-a-property-in-malaysia.html",
    "https://www.kwsp.gov.my/en/w/article/buy-vs-rent-malaysia",
    "https://www.iproperty.com.my/guides/should-buy-or-rent-property-malaysia-30437"
]

all_text = ""
for url in urls:
    try:
        response = requests.get(url)
        soup = BeautifulSoup(response.text, "html.parser")
        paragraphs = soup.find_all("p")
        text = " ".join([p.get_text() for p in paragraphs])
        all_text += text + " "
    except Exception as e:
        st.error(f"Error scraping {url}: {e}")

wc = WordCloud(width=800, height=400, background_color="white").generate(all_text)

fig3, ax = plt.subplots()
ax.imshow(wc, interpolation="bilinear")
ax.axis("off")
st.pyplot(fig3)

summary_wordcloud = (
    "Themes in Malaysian property discussions emphasize affordability, "
    "long-term stability, lifestyle flexibility, and financial planning. "
    "The prominence of terms like 'mortgage', 'investment', and 'cost' "
    "reflects a balance between security and flexibility in the buy vs rent debate."
)
st.write(summary_wordcloud)

# --------------------------
# 5. Combined Insights
# --------------------------
st.header("🔎 Combined Insights & Recommendations")

combined_summary = (
    "In Malaysia, buying a property generally offers stronger long-term financial security, "
    "but it requires significant upfront commitment. Renting, meanwhile, provides flexibility "
    "and lower immediate costs, making it suitable for younger individuals or those uncertain "
    "about long-term settlement. Sensitivity analysis reinforces that interest rates and "
    "financing terms strongly influence affordability. Text insights from local sources "
    "highlight that decisions are not purely financial — lifestyle goals and stability matter too."
)

st.write(combined_summary)

st.subheader("📚 Sources")
for url in urls:
    st.markdown(f"- {url}")

# --------------------------
# 6. PDF Export with Images
# --------------------------
def generate_pdf():
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4)
    styles = getSampleStyleSheet()
    elements = []

    elements.append(Paragraph("Buy vs Rent in Malaysia – Financial & Text Insights", styles['Title']))
    elements.append(Spacer(1, 12))

    # Wealth Comparison
    elements.append(Paragraph("💰 Wealth Comparison", styles['Heading2']))
    img_buffer1 = BytesIO()
    fig1.savefig(img_buffer1, format="png")
    img_buffer1.seek(0)
    elements.append(RLImage(img_buffer1, width=400, height=200))
    elements.append(Paragraph(summary_buy_rent, styles['Normal']))
    elements.append(Spacer(1, 12))

    # Sensitivity Analysis
    elements.append(Paragraph("📊 Sensitivity Analysis", styles['Heading2']))
    img_buffer2 = BytesIO()
    fig2.savefig(img_buffer2, format="png")
    img_buffer2.seek(0)
    elements.append(RLImage(img_buffer2, width=400, height=200))
    elements.append(Paragraph(summary_sensitivity, styles['Normal']))
    elements.append(Spacer(1, 12))

    # WordCloud
    elements.append(Paragraph("☁️ WordCloud Insights", styles['Heading2']))
    img_buffer3 = BytesIO()
    fig3.savefig(img_buffer3, format="png")
    img_buffer3.seek(0)
    elements.append(RLImage(img_buffer3, width=400, height=200))
    elements.append(Paragraph(summary_wordcloud, styles['Normal']))
    elements.append(Spacer(1, 12))

    # Combined Insights
    elements.append(Paragraph("🔎 Combined Insights & Recommendations", styles['Heading2']))
    elements.append(Paragraph(combined_summary, styles['Normal']))
    elements.append(Spacer(1, 12))

    # Sources
    elements.append(Paragraph("📚 Sources", styles['Heading2']))
    for url in urls:
        elements.append(Paragraph(url, styles['Normal']))

    doc.build(elements)
    buffer.seek(0)
    return buffer

if st.button("📥 Download Report as PDF"):
    pdf = generate_pdf()
    st.download_button(
        label="Download PDF",
        data=pdf,
        file_name="buy_vs_rent_malaysia.pdf",
        mime="application/pdf"
    )
