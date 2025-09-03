# app.py
import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from wordcloud import WordCloud
import requests
from bs4 import BeautifulSoup
import concurrent.futures
import re
import io
import datetime

# reportlab for PDF
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image as RLImage
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import inch
from reportlab.lib import colors

# nltk stopwords
import nltk
from nltk.corpus import stopwords
try:
    stopwords.words("english")
except LookupError:
    nltk.download("punkt")
    nltk.download("stopwords")

# ----------------------------
# App config
# ----------------------------
st.set_page_config(page_title="Buy vs Rent Dashboard", layout="wide")
st.sidebar.title("🏡 Navigation")
page = st.sidebar.radio("Go to:", [
    "📊 EDA Overview",
    "📈 Wealth Comparison",
    "⚖️ Sensitivity Analysis",
    "☁️ WordCloud (Malaysia Blogs)",
    "🔗 Combined Insights"
])

# ----------------------------
# Constants / Blog URLs
# ----------------------------
BLOG_URLS = [
    "https://www.greateasternlife.com/my/en/personal-insurance/greatpedia/live-great-reads/wellbeing-and-success/should-you-buy-or-rent-a-property-in-malaysia.html",
    "https://www.kwsp.gov.my/en/w/article/buy-vs-rent-malaysia",
    "https://www.iproperty.com.my/guides/should-buy-or-rent-property-malaysia-30437"
]

EXTRA_STOPWORDS = {"akan", "dan", "atau", "yang", "untuk", "dengan", "jika"}

# ----------------------------
# Utility: fetch one URL text
# ----------------------------
def fetch_blog_text_single(url):
    headers = {"User-Agent": "Mozilla/5.0 (compatible)"}
    try:
        r = requests.get(url, headers=headers, timeout=8)
        r.raise_for_status()
        soup = BeautifulSoup(r.text, "html.parser")
        paragraphs = [p.get_text(separator=" ", strip=True) for p in soup.find_all("p")]
        return " ".join(paragraphs)
    except Exception as e:
        print(f"Failed to fetch {url}: {e}")
        return ""

# ----------------------------
# Cached: fetch malaysia blogs (parallel) - cached daily
# ----------------------------
@st.cache_data(ttl=24 * 60 * 60)
def fetch_malaysia_blogs(urls):
    text_chunks = []
    with concurrent.futures.ThreadPoolExecutor() as ex:
        results = list(ex.map(fetch_blog_text_single, urls))
    for t in results:
        if t:
            text_chunks.append(t)
    all_text = " ".join(text_chunks)
    all_text = re.sub(r"\s+", " ", all_text).strip()
    if not all_text:
        all_text = "No text could be fetched from the web. Check connection or sources."
    return all_text

# ----------------------------
# Cached: generate wordcloud and top words
# ----------------------------
@st.cache_data
def make_wordcloud_and_freq(text, n_top=20):
    stop_words = set(stopwords.words("english")) | EXTRA_STOPWORDS
    tokens = re.findall(r"\b[a-zA-Z]{2,}\b", text.lower())
    cleaned = [t for t in tokens if t not in stop_words]
    if not cleaned:
        wc = WordCloud(width=800, height=400, background_color="white").generate("no content")
        freq = []
    else:
        wc = WordCloud(width=800, height=400, background_color="white").generate(" ".join(cleaned))
        freq = pd.Series(cleaned).value_counts().head(n_top).reset_index().values.tolist()  # list of [word, freq]
    return wc, freq

# ----------------------------
# Financial model (deterministic/simple)
# ----------------------------
@st.cache_data
def generate_financial_df(mortgage_rate_pct, rent_escalation_pct, investment_return_pct,
                          years=30, mortgage_term=30, property_price=500000, monthly_rent=1500):
    mortgage_rate = mortgage_rate_pct / 100.0
    rent_escalation = rent_escalation_pct / 100.0
    investment_return = investment_return_pct / 100.0

    df = pd.DataFrame({"Year": np.arange(1, years + 1)})

    # monthly mortgage payment (fixed-rate annuity)
    r = mortgage_rate / 12.0
    n = mortgage_term * 12
    if r == 0:
        monthly_payment = property_price / n
    else:
        monthly_payment = property_price * r * (1 + r) ** n / ((1 + r) ** n - 1)

    df["Monthly_Mortgage"] = monthly_payment
    df["Annual_Mortgage_Paid"] = monthly_payment * 12
    df["Cumulative_Mortgage_Paid"] = df["Annual_Mortgage_Paid"].cumsum()

    # Simple equity approx (linear principal build; you can refine to full amortization later)
    df["Home_Equity"] = property_price * (df["Year"] / mortgage_term).clip(upper=1)

    # Annual rent with escalation
    df["Annual_Rent"] = monthly_rent * 12 * (1 + rent_escalation) ** (df["Year"] - 1)

    # Rent saved each year (mortgage - rent)
    df["Rent_Saved"] = (df["Annual_Mortgage_Paid"] - df["Annual_Rent"]).clip(lower=0)

    # Investment value accumulation
    invest_values = []
    total = 0.0
    for saved in df["Rent_Saved"]:
        total = (total + saved) * (1 + investment_return)
        invest_values.append(total)
    df["Investment_Value"] = invest_values

    df["Net_Wealth_Buy"] = df["Home_Equity"] - df["Cumulative_Mortgage_Paid"]
    df["Net_Wealth_Rent"] = df["Investment_Value"]

    return df

# ----------------------------
# Helper: convert Matplotlib fig to BytesIO (for reportlab embedding)
# ----------------------------
def fig_to_bytes(fig, fmt="png", dpi=150):
    buf = io.BytesIO()
    fig.savefig(buf, format=fmt, dpi=dpi, bbox_inches="tight")
    buf.seek(0)
    plt.close(fig)
    return buf

# ----------------------------
# Create report PDF with ReportLab
# ----------------------------
def create_report_pdf(df_numeric, wc_buf, wc_freq, wealth_buf, sens_buf, blog_sources_list, recommendation_text, out_buf):
    doc = SimpleDocTemplate(out_buf, pagesize=A4)
    styles = getSampleStyleSheet()
    story = []

    # Title
    story.append(Paragraph("Buy vs Rent – Combined Insights Report (Malaysia)", styles["Title"]))
    story.append(Spacer(1, 8))

    # Generated datetime
    story.append(Paragraph(f"Generated: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", styles["Normal"]))
    story.append(Spacer(1, 8))

    # Sources (bullet list)
    story.append(Paragraph("Sources (scraped):", styles["Heading2"]))
    for url in blog_sources_list:
        story.append(Paragraph(f"- {url}", styles["Normal"]))
    story.append(Spacer(1, 8))

    # Summary paragraph (short)
    story.append(Paragraph("Summary:", styles["Heading2"]))
    summary_paragraph = (
        "This report compares the trade-off between buying a property and renting while "
        "investing the difference. It includes a wealth-accumulation model (buy vs rent+invest), "
        "a sensitivity analysis across investment return scenarios, and textual insights synthesized "
        "from Malaysian property articles."
    )
    story.append(Paragraph(summary_paragraph, styles["Normal"]))
    story.append(Spacer(1, 8))

    # WordCloud image
    story.append(Paragraph("WordCloud (Malaysia articles)", styles["Heading2"]))
    if wc_buf is not None:
        story.append(RLImage(wc_buf, width=450, height=225))
    story.append(Spacer(1, 8))

    # Top words table
    story.append(Paragraph("Top words (from the articles)", styles["Heading3"]))
    if wc_freq:
        table_data = [["Word", "Frequency"]] + [[str(w), int(f)] for w, f in wc_freq]
        tbl = Table(table_data, colWidths=[250, 80])
        tbl.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#2F4F4F")),
            ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
            ("ALIGN", (0, 0), (-1, -1), "CENTER"),
            ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
            ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ]))
        story.append(tbl)
    else:
        story.append(Paragraph("No top words available.", styles["Normal"]))
    story.append(Spacer(1, 12))

    # Wealth Chart
    story.append(Paragraph("Wealth Accumulation: Buy vs Rent + Invest", styles["Heading2"]))
    if wealth_buf is not None:
        story.append(RLImage(wealth_buf, width=450, height=250))
    story.append(Spacer(1, 8))

    # Sensitivity Chart
    story.append(Paragraph("Sensitivity Analysis (varied investment returns)", styles["Heading2"]))
    if sens_buf is not None:
        story.append(RLImage(sens_buf, width=450, height=250))
    story.append(Spacer(1, 8))

    # Final-year numbers summary
    if not df_numeric.empty:
        last = df_numeric.iloc[-1]
        table_data = [["Measure", "Value"],
                      ["Final Net Wealth (Buy)", f"RM {last['Net_Wealth_Buy']:,.2f}"],
                      ["Final Net Wealth (Rent + Invest)", f"RM {last['Net_Wealth_Rent']:,.2f}"]]
        tbl2 = Table(table_data, colWidths=[260, 150])
        tbl2.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#2F4F4F")),
            ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
            ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
        ]))
        story.append(tbl2)
    story.append(Spacer(1, 12))

    # Insights & Recommendation (shaded paragraph)
    story.append(Paragraph("Insights & Recommendation", styles["Heading2"]))
    # we embed recommendation_text as a multi-line paragraph (string)
    rec_par = Paragraph(recommendation_text.replace("\n", "<br/>"), styles["Normal"])
    # put in a light shaded box by using a Table with background color
    rec_table = Table([[rec_par]], colWidths=[450])
    rec_table.setStyle(TableStyle([
        ("BACKGROUND", (0,0), (-1,-1), colors.HexColor("#F3F9F1")),  # light green
        ("BOX", (0,0), (-1,-1), 1, colors.grey),
        ("LEFTPADDING", (0,0), (-1,-1), 8),
        ("RIGHTPADDING", (0,0), (-1,-1), 8),
        ("VALIGN", (0,0), (-1,-1), "TOP"),
    ]))
    story.append(rec_table)
    story.append(Spacer(1, 12))

    # Build PDF into out_buf
    doc.build(story)

# ----------------------------
# UI: Sidebar inputs for finance
# ----------------------------
st.sidebar.header("💰 Financial Inputs")
mortgage_rate = st.sidebar.slider("Mortgage Rate (%)", 1.0, 10.0, 4.0, 0.1)
rent_escalation = st.sidebar.slider("Annual Rent Growth (%)", 0.0, 10.0, 3.0, 0.1)
investment_return = st.sidebar.slider("Investment Return (%)", 1.0, 15.0, 7.0, 0.1)
years = st.sidebar.number_input("Analysis Period (Years)", value=30, step=1)
property_price = st.sidebar.number_input("Property Price (RM)", value=500000, step=50000)
monthly_rent = st.sidebar.number_input("Monthly Rent (RM)", value=1500, step=100)
mortgage_term = st.sidebar.number_input("Mortgage Term (years)", value=30, step=1)

# ----------------------------
# Prepare data and visuals (fetch blogs)
# ----------------------------
with st.spinner("Fetching Malaysia articles (cached daily)..."):
    scraped_text = fetch_malaysia_blogs(BLOG_URLS)

# WordCloud + frequency
wc, wc_freq = make_wordcloud_and_freq(scraped_text, n_top=20)

# Build word_freq DataFrame for display
word_freq_df = pd.DataFrame(wc_freq, columns=["Word", "Frequency"]) if wc_freq else pd.DataFrame(columns=["Word","Frequency"])

# Financial df
df_numeric = generate_financial_df(mortgage_rate, rent_escalation, investment_return,
                                   years=years, mortgage_term=mortgage_term,
                                   property_price=property_price, monthly_rent=monthly_rent)

# ----------------------------
# Pages Implementation
# ----------------------------
if page == "📊 EDA Overview":
    st.title("🔎 EDA Overview")
    st.subheader("Dataset (yearly rows)")
    st.dataframe(df_numeric)
    st.subheader("Descriptive statistics")
    st.write(df_numeric.describe())
    st.subheader("Missing values")
    st.write(df_numeric.isna().sum())

    st.subheader("Correlation heatmap")
    fig, ax = plt.subplots(figsize=(7,6))
    cax = ax.matshow(df_numeric.select_dtypes(include=[np.number]).corr(), cmap="coolwarm")
    plt.xticks(range(len(df_numeric.select_dtypes(include=[np.number]).columns)),
               df_numeric.select_dtypes(include=[np.number]).columns, rotation=45)
    plt.yticks(range(len(df_numeric.select_dtypes(include=[np.number]).columns)),
               df_numeric.select_dtypes(include=[np.number]).columns)
    fig.colorbar(cax)
    st.pyplot(fig)

elif page == "📈 Wealth Comparison":
    st.title("📈 Wealth Comparison")
    st.subheader("Buy vs Rent + Invest Over Time")
    fig_w, ax = plt.subplots(figsize=(9,5))
    ax.plot(df_numeric["Year"], df_numeric["Net_Wealth_Buy"], label="Buy (Net Wealth)", marker="o")
    ax.plot(df_numeric["Year"], df_numeric["Net_Wealth_Rent"], label="Rent + Invest (Net Wealth)", marker="o")
    ax.set_xlabel("Year"); ax.set_ylabel("Net Wealth (RM)")
    ax.set_title("Net Wealth Comparison")
    ax.legend(); ax.grid(True)
    st.pyplot(fig_w)

    # save for PDF
    wealth_buf = fig_to_bytes(fig_w)

elif page == "⚖️ Sensitivity Analysis":
    st.title("⚖️ Sensitivity Analysis")
    st.info("Overlayed scenarios for mortgage, rent growth, and investment return.")
    mortgage_range = st.sidebar.slider("Mortgage Rate Range (%)", 2.0, 8.0, (3.0, 6.0), 0.5)
    rent_range = st.sidebar.slider("Rent Escalation Range (%)", 0.0, 10.0, (1.0, 4.0), 0.5)
    invest_range = st.sidebar.slider("Investment Return Range (%)", 3.0, 12.0, (5.0, 9.0), 0.5)
    steps = st.sidebar.number_input("Steps per parameter", min_value=2, max_value=6, value=3)

    fig_sens, ax_sens = plt.subplots(figsize=(9,5))
    scenarios = []
    for m in np.linspace(mortgage_range[0], mortgage_range[1], steps):
        for re_ in np.linspace(rent_range[0], rent_range[1], steps):
            for ir in np.linspace(invest_range[0], invest_range[1], steps):
                df_test = generate_financial_df(m, re_, ir, years=years,
                                               mortgage_term=mortgage_term,
                                               property_price=property_price,
                                               monthly_rent=monthly_rent)
                ax_sens.plot(df_test["Year"], df_test["Net_Wealth_Rent"], color="green", alpha=0.12)
                ax_sens.plot(df_test["Year"], df_test["Net_Wealth_Buy"], color="blue", alpha=0.12)
                scenarios.append((m, re_, ir, df_test.iloc[-1]["Net_Wealth_Rent"]))
    ax_sens.set_title("Sensitivity Analysis (many scenarios overlayed)")
    ax_sens.set_xlabel("Year"); ax_sens.set_ylabel("Net Wealth (RM)")
    ax_sens.grid(True)
    st.pyplot(fig_sens)

    sens_buf = fig_to_bytes(fig_sens)

    if scenarios:
        sens_df = pd.DataFrame(scenarios, columns=["MortgageRate", "RentEscalation", "InvestReturn", "FinalRentWealth"])
        st.subheader("Sample sensitivity results (final-year rent wealth)")
        st.dataframe(sens_df.sort_values("FinalRentWealth", ascending=False).head(10))
    else:
        st.info("No scenarios generated.")

elif page == "☁️ WordCloud (Malaysia Blogs)":
    st.title("☁️ WordCloud (Malaysia Blogs)")
    st.subheader("WordCloud from scraped Malaysia articles")
    fig_wc, ax_wc = plt.subplots(figsize=(10,4.5))
    ax_wc.imshow(wc, interpolation="bilinear")
    ax_wc.axis("off")
    st.pyplot(fig_wc)

    st.subheader("Top words (20)")
    if not word_freq_df.empty:
        st.dataframe(word_freq_df)
    else:
        st.info("No words available.")

    wc_buf = fig_to_bytes(fig_wc)

elif page == "🔗 Combined Insights":
    st.title("🔗 Combined Financial & Text Insights")

    # Wealth plot
    st.subheader("Wealth Accumulation")
    fig_w2, ax_w2 = plt.subplots(figsize=(6,4))
    ax_w2.plot(df_numeric["Year"], df_numeric["Net_Wealth_Buy"], label="Buy", marker="o")
    ax_w2.plot(df_numeric["Year"], df_numeric["Net_Wealth_Rent"], label="Rent + Invest", marker="o")
    ax_w2.set_xlabel("Year"); ax_w2.set_ylabel("Net Wealth (RM)")
    ax_w2.legend(); ax_w2.grid(True)
    st.pyplot(fig_w2)
    wealth_buf = fig_to_bytes(fig_w2)

    # Sensitivity example
    st.subheader("Sensitivity (example overlay)")
    fig_sens2, ax_sens2 = plt.subplots(figsize=(6,4))
    invest_rates = [0.03, 0.05, 0.07]
    sens_results = []
    for r in invest_rates:
        df_tmp = generate_financial_df(mortgage_rate, rent_escalation, r*100, years=years,
                                       mortgage_term=mortgage_term, property_price=property_price,
                                       monthly_rent=monthly_rent)
        ax_sens2.plot(df_tmp["Year"], df_tmp["Net_Wealth_Rent"], label=f"Invest {int(r*100)}%")
        sens_results.append((f"Invest {int(r*100)}%", df_tmp.iloc[-1]["Net_Wealth_Rent"]))
    ax_sens2.plot(df_numeric["Year"], df_numeric["Net_Wealth_Buy"], label="Buy (Net)", color="black", linewidth=2)
    ax_sens2.set_xlabel("Year"); ax_sens2.set_ylabel("Net Wealth (RM)")
    ax_sens2.legend(); ax_sens2.grid(True)
    st.pyplot(fig_sens2)
    sens_buf = fig_to_bytes(fig_sens2)

    # WordCloud
    st.subheader("WordCloud (from Malaysia articles)")
    fig_wc2, ax_wc2 = plt.subplots(figsize=(10,4.5))
    ax_wc2.imshow(wc, interpolation="bilinear")
    ax_wc2.axis("off")
    st.pyplot(fig_wc2)
    wc_buf = fig_to_bytes(fig_wc2)

    st.subheader("Top 20 words")
    if not word_freq_df.empty:
        st.dataframe(word_freq_df)
    else:
        st.info("No words available.")

    # Summary paragraph
    st.subheader("Summary")
    st.write(
        "This analysis compares buying a property vs renting and investing the difference. "
        "It models yearly wealth accumulation over the selected period, shows sensitivity "
        "to investment returns, and synthesizes themes from Malaysia-focused articles."
    )

    # Recommendation & insights
    final_buy = df_numeric.iloc[-1]["Net_Wealth_Buy"]
    final_rent = df_numeric.iloc[-1]["Net_Wealth_Rent"]
    if final_buy > final_rent:
        recommendation_text = (
            "Based on the input assumptions, BUYING yields higher final net wealth. "
            "Buying gives equity stability but requires upfront & running costs.\n\n"
            "Insights:\n"
            "- Buying builds long-term equity and suits those seeking stability.\n"
            "- Renting+Investing could still be preferable if you can consistently invest savings and achieve higher returns."
        )
        rec_colour = "#DFF0D8"  # light green
        rec_text_display = "✅ Based on these assumptions, BUYING looks better."
    else:
        recommendation_text = (
            "Based on the input assumptions, RENTING + INVESTING yields higher final net wealth. "
            "Renting + disciplined investing may outperform if investments beat mortgage costs.\n\n"
            "Insights:\n"
            "- Renting and investing is attractive if you value flexibility and can invest savings reliably.\n"
            "- Ensure discipline: savings must actually be invested, not spent."
        )
        rec_colour = "#FFF3CD"  # light orange
        rec_text_display = "🔔 Based on these assumptions, RENTING + INVESTING looks better."

    # Collapsible insights & recommendation
    with st.expander("💡 Insights & Recommendation", expanded=False):
        st.markdown(f"<div style='padding:12px;border-radius:8px;background:{rec_colour}'>{rec_text_display}</div>", unsafe_allow_html=True)
        st.write(recommendation_text)

    # Sources (collapsible)
    with st.expander("📚 Sources", expanded=False):
        for url in BLOG_URLS:
            st.markdown(f"- [{url}]({url})")

    # Prepare PDF on demand
    if st.button("📥 Download Combined PDF Report"):
        out_buffer = io.BytesIO()
        # create PDF with wordcloud (wc_buf), wealth chart (wealth_buf) and sensitivity chart (sens_buf)
        # pass word frequency as list of (word, freq)
        create_report_pdf(df_numeric, wc_buf, wc_freq, wealth_buf, sens_buf, BLOG_URLS, recommendation_text, out_buffer)
        out_buffer.seek(0)
        st.download_button("Download PDF", data=out_buffer, file_name="combined_insights_report.pdf", mime="application/pdf")

# end of file
