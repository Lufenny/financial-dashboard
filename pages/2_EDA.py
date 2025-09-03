import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from wordcloud import WordCloud
import requests
from bs4 import BeautifulSoup
from collections import Counter
from io import BytesIO
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.pagesizes import A4

# --------------------------
# Page Config
# --------------------------
st.set_page_config(page_title="Buy vs Rent – Malaysia EDA", layout="wide")

st.title("🏡 Buy vs Rent in Malaysia – Exploratory Data Analysis")

# --------------------------
# Scraping Blogs
# --------------------------
blog_sources = {
    "Great Eastern": "https://www.greateasternlife.com/my/en/personal-insurance/greatpedia/live-great-reads/wellbeing-and-success/should-you-buy-or-rent-a-property-in-malaysia.html",
    "KWSP": "https://www.kwsp.gov.my/en/w/article/buy-vs-rent-malaysia",
    "iProperty": "https://www.iproperty.com.my/guides/should-buy-or-rent-property-malaysia-30437"
}

def scrape_text(url):
    try:
        r = requests.get(url, timeout=10)
        soup = BeautifulSoup(r.text, "html.parser")
        text = " ".join([p.get_text() for p in soup.find_all("p")])
        return text
    except:
        return ""

all_text = " ".join([scrape_text(url) for url in blog_sources.values()])

# --------------------------
# WordCloud & Top Words
# --------------------------
wc = WordCloud(width=800, height=400, background_color="white").generate(all_text)

st.subheader("☁️ WordCloud from Malaysia Articles")
st.image(wc.to_array(), use_container_width=True)

# Save wordcloud image
wc_img = BytesIO()
wc.to_image().save(wc_img, format="PNG")
wc_img.seek(0)

words = all_text.lower().split()
common_words = Counter(words).most_common(20)
df_words = pd.DataFrame(common_words, columns=["Word", "Frequency"])

st.subheader("📊 Top 20 Words")
st.dataframe(df_words)

# --------------------------
# Wealth Accumulation Model
# --------------------------
st.subheader("💰 Wealth Accumulation: Buy vs Rent & Invest")

years = 30
property_price = 500000
annual_rent = 20000
mortgage_rate = 0.04
investment_return = 0.05

# Buy Scenario
mortgage_payment = (property_price * (1 + mortgage_rate) ** years) / years
buy_wealth = np.cumsum([-mortgage_payment] * years) + property_price

# Rent + Invest Scenario
invest_wealth = np.cumsum([(property_price/years) + (annual_rent * -1)] * years) * (1 + investment_return)

plt.figure(figsize=(10,5))
plt.plot(range(years), buy_wealth, label="Buy (Equity in Property)")
plt.plot(range(years), invest_wealth, label="Rent + Invest")
plt.xlabel("Years")
plt.ylabel("Wealth (RM)")
plt.legend()
st.pyplot(plt)

# Save chart
wealth_img = BytesIO()
plt.savefig(wealth_img, format="PNG", bbox_inches="tight")
wealth_img.seek(0)

# --------------------------
# Sensitivity Analysis
# --------------------------
st.subheader("📈 Sensitivity Analysis – Rent vs Buy")

scenarios = [
    {"mortgage_rate": 0.03, "investment_return": 0.04, "label": "Low Risk"},
    {"mortgage_rate": 0.04, "investment_return": 0.05, "label": "Base Case"},
    {"mortgage_rate": 0.05, "investment_return": 0.07, "label": "High Return"}
]

plt.figure(figsize=(10,5))
for s in scenarios:
    invest_wealth = np.cumsum([(property_price/years) + (annual_rent * -1)] * years) * (1 + s["investment_return"])
    plt.plot(range(years), invest_wealth, label=f"Rent+Invest – {s['label']}")

plt.plot(range(years), buy_wealth, label="Buy (Fixed)")
plt.xlabel("Years")
plt.ylabel("Wealth (RM)")
plt.legend()
st.pyplot(plt)

# Save sensitivity chart
sensitivity_img = BytesIO()
plt.savefig(sensitivity_img, format="PNG", bbox_inches="tight")
sensitivity_img.seek(0)

# --------------------------
# PDF Export
# --------------------------
def create_pdf():
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4)
    styles = getSampleStyleSheet()
    story = []
    
    story.append(Paragraph("🏡 Buy vs Rent in Malaysia – Report", styles["Title"]))
    story.append(Spacer(1, 12))
    story.append(Paragraph("This report analyses wealth accumulation trade-offs between buying a home vs renting and investing in Malaysia.", styles["Normal"]))
    story.append(Spacer(1, 12))
    
    story.append(Paragraph("Sources:", styles["Heading2"]))
    for name, url in blog_sources.items():
        story.append(Paragraph(f"- {name}: {url}", styles["Normal"]))
    story.append(Spacer(1, 12))
    
    story.append(Paragraph("WordCloud from Malaysia Articles:", styles["Heading2"]))
    story.append(Image(wc_img, width=400, height=200))
    story.append(Spacer(1, 12))
    
    story.append(Paragraph("Wealth Accumulation (Buy vs Rent):", styles["Heading2"]))
    story.append(Image(wealth_img, width=400, height=200))
    story.append(Spacer(1, 12))
    
    story.append(Paragraph("Sensitivity Analysis Scenarios:", styles["Heading2"]))
    story.append(Image(sensitivity_img, width=400, height=200))
    story.append(Spacer(1, 12))
    
    doc.build(story)
    buffer.seek(0)
    return buffer

if st.button("📥 Download Full PDF Report"):
    pdf = create_pdf()
    st.download_button("Download PDF", pdf, file_name="buy_vs_rent_report.pdf")
