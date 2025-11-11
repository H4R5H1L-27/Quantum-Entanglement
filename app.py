import streamlit as st
from utils.ui import inject_quantum_theme, page_header

st.set_page_config(page_title="Quantum Playground", page_icon="🧪", layout="wide")
inject_quantum_theme()

page_header("🧪 Quantum Playground", "An interactive lab to *see* and *feel* quantum mechanics.")
st.markdown("---")

col1, col2 = st.columns(2)
with col1:
    st.markdown("### 🌀 Entanglement & Correlation (Bell Test)")
    st.write("Explore *spooky* correlations. Adjust angles and watch correlations follow **cos(Δ)**.")
    st.link_button("Open module", "1_Entanglement_&_Correlation_(Bell_Test)")

    st.markdown("### 🌈 CHSH Inequality: Quantum vs Classical")
    st.write("Build **S = E(a,b)+E(a,b′)+E(a′,b)−E(a′,b′)** and **see** the violation of the classical bound 2.")
    st.link_button("Open module", "2_CHSH_Inequality")

with col2:
    st.markdown("### ✨ Quantum Teleportation Protocol")
    st.write("Step through how |ψ⟩ moves from Alice to Bob using **entanglement + 2 classical bits**.")
    st.link_button("Open module", "3_Quantum_Teleportation")

    st.markdown("### ☁️ Decoherence & Noise Models")
    st.write("Watch superpositions fade under **phase** and **amplitude** damping with a Bloch-sphere animation.")
    st.link_button("Open module", "4_Decoherence_&_Noise")

st.markdown("---")
st.subheader("🧭 Your Quantum Journey")
st.markdown("""
1. **Entanglement** — What does it mean to share a fate?  
2. **CHSH** — How do we *prove* nature isn't classical?  
3. **Teleportation** — How can information move without particles moving?  
4. **Decoherence** — Why everyday life looks classical.  
""")
st.caption("Quantum Playground · Built with ❤️ using Streamlit · NumPy · Plotly")
