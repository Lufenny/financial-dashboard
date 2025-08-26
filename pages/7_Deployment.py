import streamlit as st
import matplotlib.pyplot as plt
import networkx as nx

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
# Pipeline Diagram
# ---------------------------------------------
st.subheader("🔄 Analytical Pipeline Overview")

G = nx.DiGraph()
G.add_edges_from([
    ("Main.py", "Modelling"),
    ("Modelling", "Sensitivity Analysis"),
    ("Sensitivity Analysis", "Results & Interpretation"),
    ("Results & Interpretation", "Deployment")
])

plt.figure(figsize=(8,4))
pos = nx.spring_layout(G, seed=42)
nx.draw(G, pos, with_labels=True, node_size=4000, node_color="#A2D2FF", font_size=12, font_weight="bold", arrowsize=20)
st.pyplot(plt.gcf())

st.markdown("""
**Flow Explanation:**  
- **Main.py**: Entry point of the app, loads data & sets navigation.  
- **Modelling**: Buy vs Rent calculations and sensitivity analysis.  
- **Sensitivity Analysis**: Explore scenarios with different mortgage, investment, property, and rent assumptions.  
- **Results & Interpretation**: Visualize outcomes, compare scenarios, and provide insights.  
- **Deployment**: Share and publish the app for users via Streamlit Cloud.
""")

# ---------------------------------------------
# Deployment Steps (Collapsible)
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
    requirements_content = """streamlit>=1.29.0
pandas>=2.0.3
numpy>=1.26.0
matplotlib>=3.8.0
seaborn>=0.13.0
scikit-learn>=1.3.0
wordcloud>=1.9.2
nltk>=3.8.1
"""
    st.download_button(
        label="⬇️ Download requirements.txt",
        data=requirements_content,
        file_name="requirements.txt",
        mime="text/plain"
    )
    st.info("💡 Make sure `Main.py` is selected as the entry point when deploying on Streamlit Cloud.")

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
# Future Improvements (Collapsible)
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
