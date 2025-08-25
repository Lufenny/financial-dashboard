import streamlit as st
st.set_page_config(page_title='Capstone Project Report', page_icon='📊', layout='wide')

st.title("Capstone Project Report")

# Initialize session state
if "step" not in st.session_state:
    st.session_state.step = 1

# Function to go to next step
def next_step():
    st.session_state.step += 1

# Function to go back
def prev_step():
    st.session_state.step -= 1


# --- Step 1: Hypotheses ---
if st.session_state.step == 1:
    st.header("🧩 Hypotheses / Expected Outcome")
    st.markdown("""
    - Hypotheses about financial growth and risk.  
    - Expected outcomes under baseline, optimistic, and pessimistic assumptions.  
    """)
    st.button("Next →", on_click=next_step)


# --- Step 2: Data Sources ---
elif st.session_state.step == 2:
    st.header("📂 Data Sources")
    st.markdown("""
    - Input assumptions provided by user (contributions, returns, duration).  
    - Historical benchmarks for validation.  
    """)
    col1, col2 = st.columns(2)
    col1.button("← Back", on_click=prev_step)
    col2.button("Next →", on_click=next_step)


# --- Step 3: EDA ---
elif st.session_state.step == 3:
    st.header("🔍 Exploratory Data Analysis")
    st.markdown("""
    - Word clouds, summary stats, and visuals.  
    - Patterns and anomalies before modelling.  
    """)
    col1, col2 = st.columns(2)
    col1.button("← Back", on_click=prev_step)
    col2.button("Next →", on_click=next_step)


# --- Step 4: Data Process ---
elif st.session_state.step == 4:
    st.header("⚙️ Data Process")
    st.markdown("""
    - Data cleaning, transformation, and feature engineering.  
    """)
    col1, col2 = st.columns(2)
    col1.button("← Back", on_click=prev_step)
    col2.button("Next →", on_click=next_step)


# --- Step 5: Modelling ---
elif st.session_state.step == 5:
    st.header("🤖 Modelling")
    st.markdown("""
    - Scenario analysis (baseline / optimistic / pessimistic).  
    - Sensitivity analysis of contributions and returns.  
    """)
    col1, col2 = st.columns(2)
    col1.button("← Back", on_click=prev_step)
    col2.button("Next →", on_click=next_step)


# --- Step 6: Results ---
elif st.session_state.step == 6:
    st.header("📈 Results & Interpretation")
    st.markdown("""
    - Growth projections (2025–2045).  
    - Comparison between different strategies.  
    """)
    col1, col2 = st.columns(2)
    col1.button("← Back", on_click=prev_step)
    col2.button("Next →", on_click=next_step)


# --- Step 7: Deployment ---
elif st.session_state.step == 7:
    st.header("🚀 Deployment Details")
    st.markdown("""
    The analytical framework has been operationalised through an interactive **Streamlit application**, 
    ensuring accessibility and reproducibility of the findings.  

    All dependencies—including *pandas*, *numpy*, *matplotlib*, and *streamlit*—are specified in 
    a `requirements.txt` file. The app is hosted on **Streamlit Cloud**, making it accessible 
    from any browser without local installation.  

    ### 🧭 User Guide
    1. Navigate step by step using the **Next → buttons**.  
    2. Explore **Scenario Analysis** (baseline, optimistic, pessimistic).  
    3. Use **Sensitivity Analysis** to adjust contributions & returns.  
    4. Expect quarterly updates with latest macroeconomic data.  

    ---
    ℹ️ **Disclaimer:**  
    This tool is for educational purposes only and does **not** constitute financial advice.  
    """)
    st.button("← Back", on_click=prev_step)

