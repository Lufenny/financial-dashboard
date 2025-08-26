import streamlit as st

st.set_page_config(page_title='Deployment', layout='wide')
st.title("🚀 Deployment")

# ---------------------------------------------
# Deployment Plan Overview
# ---------------------------------------------
st.header("🌐 Model Deployment Plan")
st.write("""
This section outlines how the analytical framework is deployed for practical use.  
The system is published via **Streamlit Cloud**, with all source code hosted on GitHub:  
👉 [GitHub Repository](https://github.com/Lufenny/financial-dashboard)  
""")

# ---------------------------------------------
# Pipeline Flow (Text-based)
# ---------------------------------------------
st.subheader("🔄 Analytical Pipeline Overview")
st.markdown("""
**Flow:**

`Main.py` ➡️ `Modelling` ➡️ `Sensitivity Analysis` ➡️ `Results & Interpretation` ➡️ `Deployment`

**Explanation:**
- **Main.py**: Entry point of the app, loads data & sets navigation.  
- **Modelling**: Buy vs Rent calculations and sensitivity analysis.  
- **Sensitivity Analysis**: Explore scenarios with different mortgage, investment, property, and rent assumptions.  
- **Results & Interpretation**: Visualize outcomes, compare scenarios, and provide insights.  
- **Deployment**: Share and publish the app for users via Streamlit Cloud.
""")

# ---------------------------------------------
# Deployment Steps
# ---------------------------------------------
with st.expander("🔧 Deployment Steps", expanded=True):
    st.markdown("""
1. **Code Repository**  
   - All Streamlit scripts and supporting data are hosted on GitHub.  
   - `README.md` includes setup instructions and project overview.  

2. **Environment Setup**  
   - Ensure `requirements.txt` lists all dependencies (example below):  
     ```text
     streamlit>=1.29.0
     pandas>=2.0.3
     numpy>=1.26.0
     matplotlib>=3.8.0
     seaborn>=0.13.0
     scikit-learn>=1.3.0
     wordcloud>=1.9.2
     nltk>=3.8.1
     ```
   - Local run example:  
     ```bash
     pip install -r requirements.txt
     streamlit run Main.py
     ```
""")

# ---------------------------------------------
# Streamlit Cloud Deployment
# ---------------------------------------------
with st.expander("☁️ Streamlit Cloud Deployment"):
    st.markdown("""
- Connect your GitHub repository to **Streamlit Cloud**.  
- Choose `Main.py` as the main script.  
- Configure resource settings (CPU, memory) as needed.  
- Streamlit Cloud auto redeploys whenever you push new commits to GitHub.
""")

# ---------------------------------------------
# Future Improvements
# ---------------------------------------------
with st.expander("📌 Future Improvements"):
    st.markdown("""
- **Interactive Parameter Inputs** → allow users to adjust inflation, returns, and rent assumptions dynamically.  
- **Database Integration** → connect with live APIs (e.g., EPF rates, property index).  
- **Mobile-Friendly Interface** → responsive design for broader usability.  
- **Cloud Storage** → option to save user-uploaded scenarios or results.  
- **Visualization Enhancements** → add charts, heatmaps, or scenario comparison graphs.
""")

st.success("✅ Deployment ensures accessibility, scalability, and reproducibility of the research.")
