import streamlit as st

st.set_page_config(page_title='Deployment', layout='wide')
st.title("🚀 Deployment")

# ---------------------------------------------
# Deployment Content
# ---------------------------------------------
st.header("🌐 Model Deployment Plan")
st.write("""
This section outlines how the analytical framework is deployed for practical use.  
The system is published via **Streamlit Cloud**, with all source code hosted on GitHub:  
👉 [GitHub Repository](https://github.com/Lufenny/financial-dashboard)  
""")

st.subheader("🔧 Deployment Steps")
st.markdown("""
1. **Code Repository**  
   - All Streamlit scripts and supporting data are hosted on GitHub.  
   - `README.md` includes setup instructions and project overview.  

2. **Environment Setup**  
   - Ensure `requirements.txt` lists all dependencies:  
     ```
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

3. **Streamlit Cloud Deployment**  
   - Connect the GitHub repo to Streamlit Cloud.  
   - Select `Main.py` as the entry point.  
   - Configure resource settings (CPU, memory) as needed.  

4. **Continuous Updates**  
   - New GitHub commits → auto redeployment on Streamlit Cloud.  
   - Supports version control, collaboration, and scalability.  
""")

st.subheader("📌 Future Improvements")
st.write("""
- **Interactive Parameter Inputs** → allow users to adjust inflation, returns, 
  and rent assumptions dynamically.  
- **Database Integration** → connect with live APIs (e.g., EPF rates, property index).  
- **Mobile-Friendly Interface** → responsive design for broader usability.  
- **Cloud Storage** → option to save user-uploaded scenarios or results.  
""")

st.success("✅ Deployment ensures accessibility, scalability, and reproducibility of the research.")
