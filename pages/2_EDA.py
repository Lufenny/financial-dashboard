import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from wordcloud import WordCloud
import requests
from bs4 import BeautifulSoup
from fpdf import FPDF
import io

# --------------------------
# Streamlit Page Config
# --------------------------
st.set_page_config(page_title="🏡 Buy vs Rent Malaysia", layout="wide")
st.title("🏡 Buy vs Rent Analysis (Malaysia)")

# --------------------------
# Scraping Malaysian Blogs
# --------------------------
blog_sources = [
    "https://www.greateasternlife.com/my/en/personal-insurance/greatpedia/live-great-reads/wellbeing-and-success/should-you-buy-or-rent-a-property-in-malaysia.html",
    "https://www.kwsp.gov.my/en/w/article/buy-vs-rent-malaysia",
    "https://www.iproperty.com.my/guides/should-buy-or-rent-property-malaysia-30437"
]

@st.cache_data
def fetch_blog_text(url):
    try:
        res = requests.get(url, timeout=10)
        soup = BeautifulSoup(res.text, "html.parser")
        return " ".join([p.get_text() for p in soup.find_all("p")])
    except Exception as e:
        return f"Error fetching {url}: {e}"

all_text = " ".join([fetch_blog_text(url) for url in blog_sources])

# --------------------------
# Generate WordCloud & Word Frequency
# --------------------------
@st.cache_data
def generate_wordcloud(text):
    wc = WordCloud(width=800, height=400, background_color="white").generate(text)
    return wc

if all_text.strip():
    wordcloud = generate_wordcloud(all_text)
    wordcloud_img = wordcloud.to_image()

    words = pd.Series(all_text.lower().split())
    word_freq = words.value_counts().head(20)
else:
    wordcloud, wordcloud_img, word_freq = None, None, None

# --------------------------
# Financial Model Functions
# --------------------------
def simulate_wealth(purchase_price, down_payment, mortgage_rate, rent, investment_return, years=30):
    loan_amount = purchase_price - down_payment
    monthly_rate = mortgage_rate / 12
    n_months = years * 12
    mortgage_payment = loan_amount * (monthly_rate * (1 + monthly_rate)**n_months) / ((1 + monthly_rate)**n_months - 1)

    wealth_buy, wealth_rent = [], []
    invest_value = down_payment
    rent_invest = down_payment

    for year in range(1, years + 1):
        # Buy: property grows at 3% annually
        invest_value = (invest_value + 0) * (1 + investment_return)
        property_value = purchase_price * ((1 + 0.03) ** year)
        equity = property_value - loan_amount * ((1 + monthly_rate) ** (year * 12) - (1 + monthly_rate) ** (year * 12 - 12)) / ((1 + monthly_rate) ** (year * 12) - 1)
        wealth_buy.append(equity + invest_value)

        # Rent & invest: save difference between rent & mortgage
        savings = (mortgage_payment - rent * 12) if mortgage_payment > rent * 12 else 0
        rent_invest = (rent_invest + savings) * (1 + investment_return)
        wealth_rent.append(rent_invest)

    return wealth_buy, wealth_rent

def plot_wealth(purchase_price, down_payment, mortgage_rate, rent, investment_return, years=30):
    wealth_buy, wealth_rent = simulate_wealth(purchase_price, down_payment, mortgage_rate, rent, investment_return, years)
    fig, ax = plt.subplots(figsize=(6,4))
    ax.plot(range(1, years+1), wealth_buy, label="Buy (Equity + Investment)")
    ax.plot(range(1, years+1), wealth_rent, label="Rent & Invest")
    ax.set_xlabel("Years")
    ax.set_ylabel("Wealth (RM)")
    ax.legend()
    ax.grid(True)
    return fig

def plot_sensitivity(purchase_price, down_payment, mortgage_rate, rent, investment_return, years=30):
    fig, ax = plt.subplots(figsize=(6,4))
    rates = [0.02, 0.04, 0.06, 0.08]
    for r in rates:
        _, wealth_rent = simulate_wealth(purchase_price, down_payment, mortgage_rate, rent, r, years)
        ax.plot(range(1, years+1), wealth_rent, label=f"Invest Return {int(r*100)}%")
    ax.set_xlabel("Years")
    ax.set_ylabel("Wealth (RM)")
    ax.legend()
    ax.grid(True)
    return fig

# --------------------------
# Sidebar Inputs
# --------------------------
st.sidebar.header("📌 Assumptions")
purchase_price = st.sidebar.number_input("Property Price (RM)", 300000, 2000000, 500000, 50000)
down_payment = st.sidebar.number_input("Down Payment (RM)", 10000, 500000, 100000, 10000)
mortgage_rate = st.sidebar.slider("Mortgage Rate (%)", 1.0, 10.0, 4.0) / 100
rent = st.sidebar.number_input("Annual Rent (RM)", 6000, 60000, 18000, 1000)
investment_return = st.sidebar.slider("Investment Return (%)", 2.0, 12.0, 6.0) / 100
years = st.sidebar.slider("Years", 10, 40, 30)

# --------------------------
# Combined Insights in Streamlit
# --------------------------
st.header("📊 Combined Financial & Text Insights")

col1, col2 = st.columns(2)

with col1:
    st.subheader("Wealth Accumulation")
    fig = plot_wealth(purchase_price, down_payment, mortgage_rate, rent, investment_return, years)
    st.pyplot(fig)

with col2:
    st.subheader("Sensitivity Analysis")
    fig_sens = plot_sensitivity(purchase_price, down_payment, mortgage_rate, rent, investment_return, years)
    st.pyplot(fig_sens)

st.subheader("WordCloud from Malaysian Blogs")
if wordcloud_img:
    st.image(wordcloud_img, use_column_width=True)

st.subheader("Top Words from Articles")
if word_freq is not None:
    st.dataframe(word_freq.reset_index().rename(columns={"index": "Word", 0: "Frequency"}))

st.markdown("### 💡 Recommendation")
st.info("""
- **Buy** if you prioritize long-term stability and property appreciation.  
- **Rent** if flexibility and liquidity are more important.  
- Blogs suggest: weigh your savings, career mobility, and family plans.
""")

# --------------------------
# Export to PDF
# --------------------------
def export_pdf():
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    pdf.cell(200, 10, "Buy vs Rent Analysis Report", ln=True, align="C")

    pdf.multi_cell(0, 10, "This report combines financial modelling and Malaysian property blog insights.\n\n")

    # Recommendation Box
    pdf.set_fill_color(230, 230, 250)
    pdf.multi_cell(0, 10, "Recommendation:\nBuy for stability & appreciation.\nRent for flexibility & liquidity.\n", fill=True)

    return pdf

if st.button("📥 Download PDF Report"):
    pdf_file = export_pdf()
    pdf_bytes = pdf_file.output(dest="S").encode("latin-1")
    st.download_button("Download PDF", data=pdf_bytes, file_name="buy_vs_rent_report.pdf", mime="application/pdf")
