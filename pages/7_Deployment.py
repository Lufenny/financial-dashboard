import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
st.set_page_config(page_title='Deployment', layout='wide')

# ---------------------------------------------
# Deployment Content
# ---------------------------------------------
st.title("🚀 Deployment")

st.header("🌐 Model Deployment Plan")
st.write("""
This section outlines how the analytical framework can be deployed for practical use.  
The system will be published via **Streamlit Cloud** or **GitHub Pages**, enabling 
users to interactively explore different financial scenarios.  
""")

st.subheader("🔧 Deployment Steps")
st.markdown("""
1. **Code Repository**  
   - Upload all Streamlit scripts and data files to GitHub.  
   - Include a `README.md` with setup instructions.  

2. **Environment Setup**  
   - Ensure `requirements.txt` contains all dependencies.  

3. **Streamlit Cloud**  
   - Connect GitHub repo to Streamlit Cloud.  
   - Select the `Main.py` entry script.  
   - Configure resource settings.  

4. **Continuous Updates**  
   - Push new commits → app automatically redeploys.  
   - Supports version control & collaboration.  
""")

st.subheader("📌 Future Improvements")
st.write("""
- **Interactive Parameter Inputs** → allow users to adjust inflation, returns, 
  and rent assumptions dynamically.  
- **Database Integration** → link with APIs (e.g., EPF rates, property index).  
- **Mobile-Friendly Interface** → responsive design for broader usability.  
""")

st.success("✅ Deployment ensures accessibility, scalability, and reproducibility of the research.")
