import numpy as np
import streamlit as st
import plotly.graph_objects as go

from utils.ui import inject_quantum_theme, page_header, param_help
from utils.quantum_ops import chsh_value

st.set_page_config(page_title="CHSH Inequality", page_icon="🌈", layout="wide")
inject_quantum_theme()
page_header("🌈 CHSH Inequality: Quantum vs Classical", "Build S and see the violation.")

st.markdown("""
### 🎯 Learning Goal
Learn how **Bell’s CHSH inequality** exposes the difference between classical realism and quantum entanglement.
""")

with st.expander("🧮 What is CHSH?"):
    st.markdown(r"""
We combine four correlations:
\[
S = E(a,b) + E(a,b') + E(a',b) - E(a',b')
\]
Classical bound: \(|S|\le 2\). Quantum (with |Φ⁺⟩): \(|S|\le 2\sqrt{2}\approx 2.828\).
""")
with st.expander("📘 Deep Explanation: CHSH and the Limits of Classical Reality"):
    st.markdown("""
    ### 🧩 The idea
    The **CHSH inequality** is an advanced version of Bell’s test.  
    It uses four measurement settings (a, a′ for Alice; b, b′ for Bob) to check if nature follows **local realism** — the idea that:
    > 1. Physical properties exist before measurement  
    > 2. Distant objects can’t instantly affect each other  

    ### ⚛️ Quantum surprise
    In classical physics, correlations between distant measurements obey the **CHSH bound**:  
    \[
    |S| = |E(a,b) + E(a,b′) + E(a′,b) − E(a′,b′)| ≤ 2
    \]
    But quantum mechanics predicts up to **2√2 ≈ 2.828** — and experiments confirm this.

    ### 👩‍🔬 Who are Alice and Bob?
    They are our traditional stand-ins for two physicists (or measurement devices) on opposite sides of the universe:
    - **Alice** chooses between two angles a or a′.  
    - **Bob** independently chooses between b or b′.
    - Each measures their particle and records ±1.  
    Their results are random individually — but correlated in a way that defies classical logic.

    ### ⚙️ What you control
    - **a, a′, b, b′**: angles representing each person’s measurement setting.  
      These determine which component of the spin/polarization is measured.
    - **Trials**: number of random experiments to simulate.
    - **Seed**: for reproducibility.

    ### 🔍 What you should see
    - For certain angle combinations, |S| > 2 — *the classical world breaks*.  
    - The **quantum curve** peaks at |S| = 2√2 — the **Tsirelson bound**.

    ### 💭 What this means
    Violating CHSH tells us:
    - There are no local “hidden” instructions.
    - Measurement outcomes depend on both local settings and the global entangled state.
    - Nature is inherently non-local in its correlations — but still doesn’t send faster-than-light messages.

    ### 🌐 Historical note
    This test was first performed by Alain Aspect (1980s) and more recently with loophole-free versions in 2015.  
    Each confirmed Einstein’s “spooky action” is *real*.
    """)

col1, col2 = st.columns([1, 1.25])
with col1:
    st.subheader("🎚️ Settings")
    deg_a  = st.slider("Alice angle a (°)", 0, 180, 0);   param_help("a", "Alice’s first measurement axis.")
    deg_ap = st.slider("Alice angle a′ (°)", 0, 180, 45); param_help("a′", "Alice’s second axis.")
    deg_b  = st.slider("Bob angle b (°)", 0, 180, 22);    param_help("b", "Bob’s first axis.")
    deg_bp = st.slider("Bob angle b′ (°)", 0, 180, 67);   param_help("b′", "Bob’s second axis.")
    trials = st.slider("Trials per pair", 100, 200000, 5000, step=100); param_help("trials", "Samples per correlation term.")
    seed   = st.number_input("Random seed (-1 = random)", value=42, step=1)
    run    = st.button("▶ Run CHSH")

    theta_a, theta_ap = np.deg2rad(deg_a), np.deg2rad(deg_ap)
    theta_b, theta_bp = np.deg2rad(deg_b), np.deg2rad(deg_bp)
    rng = np.random.default_rng(None if seed == -1 else int(seed))

    if run:
        S_emp, S_th = chsh_value(theta_a, theta_ap, theta_b, theta_bp, trials=trials, rng=rng)
        st.info(f"|S| Empirical = **{abs(S_emp):.3f}**, Theory = **{abs(S_th):.3f}**  (Classical bound 2)")

        bars = go.Figure()
        bars.add_hline(y=2, line_dash="dot", annotation_text="Classical limit (2)")
        bars.add_hline(y=2*np.sqrt(2), line_dash="dot", annotation_text="Quantum max (2√2)")
        bars.add_bar(x=["Empirical |S|", "Theoretical |S|"], y=[abs(S_emp), abs(S_th)], name="S values")
        bars.update_layout(title="CHSH S-value comparison", yaxis_title="|S|", yaxis=dict(range=[0,3]))
        st.plotly_chart(bars, use_container_width=True)

with col2:
    st.subheader("📈 Sweep b′ to see violation appear")
    st.caption("Hold a, a′, b fixed; vary b′.")
    sweep_points  = st.slider("Sweep points", 10, 180, 120, step=5)
    sweep_trials  = st.slider("Trials per sweep point", 500, 10000, 2000, step=500)
    sweep_range   = np.linspace(0, np.pi, sweep_points)
    S_emp_list, S_th_list = [], []
    for bp in sweep_range:
        emp, th = chsh_value(theta_a, theta_ap, theta_b, bp, trials=sweep_trials, rng=rng)
        S_emp_list.append(emp); S_th_list.append(th)

    fig = go.Figure()
    fig.add_scatter(x=np.rad2deg(sweep_range), y=np.abs(S_emp_list), mode="markers", name="Empirical |S|")
    fig.add_scatter(x=np.rad2deg(sweep_range), y=np.abs(S_th_list), mode="lines", name="Theory |S|")
    fig.add_hline(y=2, line_dash="dot", annotation_text="Classical bound")
    fig.add_hline(y=2*np.sqrt(2), line_dash="dot", annotation_text="Quantum limit 2√2")
    fig.update_layout(title="S-value vs Bob’s second angle b′", xaxis_title="b′ (degrees)", yaxis_title="|S|", yaxis=dict(range=[0,3]))
    st.plotly_chart(fig, use_container_width=True)

st.markdown("---")
with st.expander("🧠 Why violation matters"):
    st.markdown("""
If outcomes were **pre-decided** by hidden variables, we'd always have |S| ≤ 2.  
But quantum experiments — and your simulation — exceed 2, up to 2√2, proving **no local hidden-variable model** can explain reality.
""")
