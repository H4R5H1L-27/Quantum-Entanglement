import numpy as np
import streamlit as st
import plotly.graph_objects as go

from utils.ui import inject_quantum_theme, page_header, param_help
from utils.quantum_ops import (
    sample_outcomes, empirical_correlation, theoretical_correlation,
    sweep_correlation, joint_probabilities
)

st.set_page_config(page_title="Entanglement & Correlation", page_icon="🌀", layout="wide")
inject_quantum_theme()
page_header("🌀 Entanglement & Correlation (Bell Test)", "Correlated outcomes from a shared quantum state.")

st.markdown("""
### 🎯 Learning Goal
See how two entangled particles give **random individual results** yet **coordinated joint outcomes**, with correlation **E = cos(Δ)**.
""")

with st.expander("🎞️ Analogy — Two magic dice"):
    st.markdown("""
If both dice are rolled at the **same orientation**, they always **match**.  
Tilt one die, and the matching rate changes smoothly like a **cosine**.  
No signals at roll time — it’s baked into their **shared preparation**.
""")
with st.expander("📘 Deep Explanation: Entanglement and Correlated Outcomes"):
    st.markdown("""
    ### 🧠 What this experiment explores
    This is the **most fundamental quantum effect**: *entanglement* — when two particles share a single, inseparable quantum state.

    When you measure one particle, you instantly know something about the other, **no matter how far apart they are**.  
    Yet, no signal is sent faster than light — the correlations come from the *shared quantum state itself*.

    ### 🎲 The coin (or dice) analogy
    Imagine two "quantum coins" created together so that:
    - if both are flipped along the same orientation → they always land the **same** (HH or TT),
    - if one is tilted before flipping → they match only part of the time, following a **cosine pattern**.

    Each coin alone looks random — 50/50 heads or tails.  
    But the **relationship between their results** is not random — it depends on how the “flip directions” (angles) are aligned.

    ### ⚙️ What you’re adjusting
    - **θA, θB**: these are the measurement *angles* (directions) chosen by Alice and Bob.  
      Changing them changes the *orientation* of the measuring device (like rotating a polarizer in a photon experiment).
    - **Trials**: number of times the measurement is repeated — more trials = smoother data.
    - **Random seed**: fixes the pseudo-random outcomes for reproducibility.

    ### 💡 What to observe
    When you vary θA and θB:
    - Correlation E ≈ cos(θA − θB)
    - Perfect match (E=+1) when they align
    - Perfect opposite (E=−1) when they differ by 180°
    - Zero correlation when difference = 90°

    ### 🚀 What it signifies
    This pattern **cannot** be explained by “hidden classical rules.”  
    It shows that entangled systems have no independent reality until they’re measured — they act like *one* entity spread across space.
    """)

colL, colR = st.columns([1, 1.25])

with colL:
    st.subheader("🎚️ Parameters")
    degA = st.slider("Alice angle θ_A (degrees)", 0, 180, 0)
    param_help("θ_A", "Alice’s measurement axis in the X–Z plane (a detector dial).")
    degB = st.slider("Bob angle θ_B (degrees)", 0, 180, 45)
    param_help("θ_B", "Bob’s measurement axis in the X–Z plane.")
    trials = st.slider("Number of measurement pairs (trials)", 100, 200000, 5000, step=100)
    param_help("trials", "More trials → Monte Carlo average converges to theory.")
    seed = st.number_input("Random seed (optional, -1 = random)", value=42, step=1)
    run = st.button("▶ Run simulation")

    theta_a = np.deg2rad(degA)
    theta_b = np.deg2rad(degB)
    rng = np.random.default_rng(None if seed == -1 else int(seed))

    if run:
        r, s = sample_outcomes(theta_a, theta_b, trials, rng)
        E_emp = empirical_correlation(r, s)
        E_th = theoretical_correlation(theta_a, theta_b)

        st.info(f"Empirical E ≈ **{E_emp:.3f}**, Theory cos(Δ) = **{E_th:.3f}** (Δ = {abs(degA-degB)}°)")

        probs = joint_probabilities(theta_a, theta_b)
        labels = ["(+1,+1)","(+1,-1)","(-1,+1)","(-1,-1)"]
        values = [probs[(+1,+1)], probs[(+1,-1)], probs[(-1,+1)], probs[(-1,-1)]]
        fig_joint = go.Figure()
        fig_joint.add_bar(x=labels, y=values)
        fig_joint.update_layout(title="Joint outcome probabilities p(r,s)", yaxis_title="Probability", xaxis_title="(r, s)")
        st.plotly_chart(fig_joint, use_container_width=True)

        rs_prod = r * s
        roll = np.cumsum(rs_prod) / (np.arange(trials) + 1)
        fig_roll = go.Figure()
        fig_roll.add_scatter(y=roll, mode="lines", name="Running mean of r·s")
        fig_roll.add_hline(y=E_th, line_dash="dot", annotation_text="Theory", annotation_position="top right")
        fig_roll.update_layout(title="Convergence of correlation E = ⟨r·s⟩", xaxis_title="Trial", yaxis_title="Correlation")
        st.plotly_chart(fig_roll, use_container_width=True)

with colR:
    st.subheader("📈 Correlation vs angle difference (animated sweep)")
    sweep_trials = st.slider("Trials per point for sweep", 100, 10000, 1500, step=100)
    points = st.slider("Number of points in sweep", 10, 200, 80, step=5)
    deltas = np.linspace(0, np.pi, points)
    emp, th = sweep_correlation(np.deg2rad(degA), deltas, trials_each=sweep_trials, rng=rng)

    fig = go.Figure()
    fig.add_scatter(x=np.rad2deg(deltas), y=emp, mode="markers", name="Empirical (Monte Carlo)")
    fig.add_scatter(x=np.rad2deg(deltas), y=th, mode="lines", name="Theory cos(Δ)")
    fig.add_hline(y=1, line_dash="dot"); fig.add_hline(y=-1, line_dash="dot")
    fig.update_layout(
        title="E(Δ) for |Φ⁺⟩ in the X–Z plane",
        xaxis_title="Δ = θ_B - θ_A (degrees)",
        yaxis_title="Correlation E",
        yaxis=dict(range=[-1.05, 1.05])
    )
    st.plotly_chart(fig, use_container_width=True)

st.markdown("---")
with st.expander("🧠 Under the hood"):
    st.markdown(r"""
- State: **|Φ⁺⟩ = (|00⟩ + |11⟩)/√2**.  
- Measuring along angles θ_A, θ_B in the X–Z plane gives **E = cos(θ_A − θ_B)**.  
- Each local result is random, but **the pattern between them** is not.
""")
st.success("**Takeaway:** Quantum entanglement gives **structured randomness** — correlations stronger than any classical pre-agreement.")
