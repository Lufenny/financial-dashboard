import streamlit as st

# ---------------------------------------------
# Page setup
# ---------------------------------------------
st.set_page_config(
    page_title='Capstone Project Report',
    page_icon='📊',
    layout='wide'
)

# ---------------------------------------------
# Title and Project Header
# ---------------------------------------------
st.title("Capstone Project Report")

st.markdown("## Wealth Accumulation through Homeownership versus Renting and Investing: Evidence from Kuala Lumpur")

# Horizontal separator
st.markdown("---")

# ---------------------------------------------
# Author / Course Info (centered with background)
# ---------------------------------------------
st.markdown(
    """
    <div style="
        text-align: center;
        line-height: 1.6;
        padding: 20px;
        margin: 20px 0;
        background-color: #f0f4f8;
        border-radius: 10px;
        box-shadow: 2px 2px 8px rgba(0,0,0,0.1);
    ">
        <strong>Prepared by:</strong> Lufenny<br>
        <strong>Course:</strong> Data Analyst Course<br>
        <strong>School:</strong> Forward School<br>
        <strong>Year:</strong> 2025
    </div>
    """,
    unsafe_allow_html=True
)
