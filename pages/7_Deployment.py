import streamlit as st

st.set_page_config(page_title='Deployment', layout='wide')
st.title("🚀 Deployment")

# --------------------------
# GitHub Repository Link
# --------------------------
st.markdown(
    "This section outlines how the analytical framework is deployed for practical use.  \n"
    "The system is published via **Streamlit Cloud**, with all source code hosted on GitHub:  \n"
    "[![GitHub Repository](https://img.shields.io/badge/GitHub-Repository-blue?logo=github)]"
    "(https://github.com/Lufenny/financial-dashboard)"
)

# --------------------------
# Deployment Steps
# --------------------------
with st.expander("🔧 Deployment Steps"):
    st.subheader("1️⃣ Code Repository")
    st.write("""
    - All Streamlit scripts and supporting data are hosted on GitHub.  
    - `README.md` includes setup instructions and project overview.
    """)

    st.subheader("2️⃣ Environment Setup")
    st.write("Ensure `requirements.txt` lists all dependencies:")
    st.code("""
streamlit>=1.29.0
pandas>=2.0.3
numpy>=1.26.0
matplotlib>=3.8.0
seaborn>=0.13.0
scikit-learn>=1.3.0
wordcloud>=1.9.2
nltk>=3.8.1
    """, language='bash')

    st.write("Local run example:")
    st.code("pip install -r requirements.txt\nstreamlit run Main.py", language='bash')

    st.subheader("3️⃣ Streamlit Cloud Deployment")
    st.write("""
    - Connect the GitHub repo to Streamlit Cloud.  
    - Select `Main.py` as the entry point.  
    - Configure resource settings (CPU, memory) as needed.
    """)

    st.subheader("4️⃣ Continuous Updates")
    st.write("""
    - New GitHub commits → auto redeployment on Streamlit Cloud.  
    - Supports version control, collaboration, and scalability.
    """)

# --------------------------
# Future Improvements
# --------------------------
with st.expander("📌 Future Improvements"):
    st.write("""
    - **Interactive Parameter Inputs** → allow users to adjust inflation, returns, and rent assumptions dynamically.  
    - **Database Integration** → connect with live APIs (e.g., EPF rates, property index).  
    - **Mobile-Friendly Interface** → responsive design for broader usability.  
    - **Cloud Storage** → option to save user-uploaded scenarios or results.
    """)

st.success("✅ Deployment ensures accessibility, scalability, and reproducibility of the research.")
