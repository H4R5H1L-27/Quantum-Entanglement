import streamlit as st

st.set_page_config(
    page_title="Quantum Playground",
    page_icon="⚛️",
    layout="wide"
)

# Load global theme (light/dark)
try:
    with open("styles/theme_light.css") as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)
except:
    pass

# ====== PAGE LAYOUT ======

# Center content
st.markdown("""
<style>
.main-container {
    max-width: 900px;
    margin-left: auto;
    margin-right: auto;
    padding-top: 40px;
}
.big-title {
    font-size: 3rem;
    font-weight: 700;
    text-align:center;
    margin-bottom: 0.2rem;
}
.subtitle {
    text-align:center;
    font-size: 1.2rem;
    margin-bottom: 2.2rem;
    color: #888;
}
.section-title {
    font-size: 1.6rem;
    font-weight:600;
    margin-top: 2.5rem;
}
.exp-card {
    background: rgba(255,255,255,0.03);
    border-radius: 12px;
    padding: 18px;
    border: 1px solid rgba(200,200,255,0.15);
    margin-bottom: 20px;
}
.exp-button {
    background:#2B6CB0 !important;
    color:white !important;
    padding:0.65rem 1.2rem !important;
    border-radius:8px !important;
    font-size:1rem !important;
}
.exp-button:hover {
    background:#2C5282 !important;
}
</style>
<div class="main-container">
""", unsafe_allow_html=True)

# ===== TITLE =====
st.markdown("<div class='big-title'>Quantum Playground</div>", unsafe_allow_html=True)
st.markdown("<div class='subtitle'>Interactive quantum concepts explained visually through analogies.</div>", unsafe_allow_html=True)


# ===== QUICK INTRO =====
st.markdown("## What you’ll explore")
st.markdown("""
This playground covers **four core quantum experiments**, each explained using
a **simple analogy**, a **clean visual**, and a **short scientific explanation**:

1. **Entanglement & Correlation**  
   How two particles behave like perfectly coordinated random coins.

2. **CHSH Inequality**  
   A test proving quantum correlations exceed all classical models.

3. **Quantum Teleportation**  
   Transferring a quantum state using entanglement + two classical bits.

4. **Decoherence & Noise**  
   How quantum states lose their structure when interacting with the environment.
""")


# ===== EXPERIMENT BUTTONS =====

st.markdown("## Choose an Experiment")

col1, col2 = st.columns(2)

with col1:
    st.markdown("### ⚛️ Entanglement & Correlation")
    st.markdown("Two entangled particles produce coordinated outcomes stronger than any classical system.")

    if st.button("Open Entanglement Demo"):
        st.switch_page("pages/1_Entanglement_&_Correlation_(Bell_Test).py")

    st.markdown("---")

    st.markdown("### 🌈 CHSH Inequality")
    st.markdown("Show that quantum predictions violate classical realism using four measurement settings.")

    if st.button("Open CHSH Experiment"):
        st.switch_page("pages/2_CHSH_Inequality.py")

with col2:
    st.markdown("### ✨ Quantum Teleportation")
    st.markdown("Watch how a secret quantum state is transferred using shared entanglement.")

    if st.button("Open Teleportation Demo"):
        st.switch_page("pages/3_Quantum_Teleportation.py")

    st.markdown("---")

    st.markdown("### ☁️ Decoherence & Noise")
    st.markdown("See how quantum states fade when exposed to the environment.")

    if st.button("Open Noise Simulator"):
        st.switch_page("pages/4_Decoherence_&_Noise.py")


# Closing wrapper
st.markdown("</div>", unsafe_allow_html=True)
