import numpy as np
import streamlit as st
import plotly.graph_objects as go

from utils.ui import inject_quantum_theme, page_header, param_help
from utils.quantum_ops import (
    single_qubit_state_from_bloch, teleportation_once, teleportation_batch, bloch_vector
)

st.set_page_config(page_title="Quantum Teleportation", page_icon="✨", layout="wide")
inject_quantum_theme()
page_header("✨ Quantum Teleportation", "Move a quantum **state** using entanglement + 2 classical bits.")

st.markdown("""
### 🎯 Learning Goal
See how an **unknown quantum state** can be perfectly transferred from Alice to Bob using one entangled pair and two classical bits.
""")

with st.expander("📖 Story version"):
    st.markdown("""
**Charlie** prepares a secret qubit (the mystery arrow) and gives it to **Alice**.  
Alice and **Bob** share an entangled pair.  
Alice performs gates and measures → two bits **(m0,m1)**.  
She sends those bits to Bob; Bob applies **Z^m0 X^m1**.  
Bob’s qubit **becomes the original**. The *state* moved — not the particle.
""")
with st.expander("📘 Deep Explanation: Quantum Teleportation"):
    st.markdown("""
    ### 🧠 What teleportation really means
    In science fiction, teleportation means “moving an object.”  
    In **quantum physics**, it means **transferring the state** of one particle to another — perfectly, but without moving matter itself.

    ### 👩‍🔬 The characters
    - **Charlie**: prepares an unknown quantum state |ψ⟩ — something only he knows.
    - **Alice**: receives that state and shares an entangled pair with Bob.
    - **Bob**: wants to get a perfect copy of |ψ⟩, but Alice can only send him *two classical bits*.

    ### ⚙️ What happens
    1. Alice performs a **Bell-state measurement** on her two qubits (the one from Charlie and her half of the entangled pair).  
    2. That collapses her system and produces two classical bits (m0, m1).
    3. She sends those two bits to Bob.
    4. Bob applies a correction — **Z^m0 X^m1** — to his qubit.
    5. Instantly, his qubit becomes **identical** to Charlie’s original.

    ### 💡 Key insight
    - No quantum information travels directly — it’s reconstructed through **entanglement + classical bits**.  
    - The original state is destroyed in the process (it’s not cloning).  
    - This preserves the **no-cloning theorem** and the **speed limit of information**.

    ### 🎛️ What you’re changing
    - **θ, φ**: define the unknown qubit’s position on the Bloch sphere (like latitude/longitude on a globe).  
      Changing them changes the *color and direction* of the quantum arrow.
    - **shots**: repeat teleportation many times to see the fidelity converge.
    - **seed**: for repeatable randomness.

    ### 🚀 What to observe
    - Bob’s final Bloch vector matches Charlie’s.  
    - The **fidelity** tells you how close they are (1 = perfect).
    - Different (m0,m1) pairs show different correction patterns.

    ### 🌠 What it signifies
    This process demonstrates **quantum information transfer** — the foundation of **quantum networks** and **quantum internet**.
    """)

def bloch_figure(vec, title):
    x,y,z = vec
    u = np.linspace(0, 2*np.pi, 30); v = np.linspace(0, np.pi, 15)
    xs = np.outer(np.cos(u), np.sin(v))
    ys = np.outer(np.sin(u), np.sin(v))
    zs = np.outer(np.ones_like(u), np.cos(v))
    fig = go.Figure()
    fig.add_surface(x=xs, y=ys, z=zs, showscale=False, opacity=0.15)
    fig.add_scatter3d(x=[-1,1], y=[0,0], z=[0,0], mode="lines", name="X")
    fig.add_scatter3d(x=[0,0], y=[-1,1], z=[0,0], mode="lines", name="Y")
    fig.add_scatter3d(x=[0,0], y=[0,0], z=[-1,1], mode="lines", name="Z")
    fig.add_scatter3d(x=[0,x], y=[0,y], z=[0,z], mode="lines+markers", name="state")
    fig.update_layout(title=title, scene=dict(xaxis=dict(range=[-1,1]), yaxis=dict(range=[-1,1]), zaxis=dict(range=[-1,1])))
    return fig

colL, colR = st.columns([1, 1.35])
with colL:
    st.subheader("🎚️ Choose the unknown state |ψ⟩")
    deg_theta = st.slider("θ (polar, degrees)", 0, 180, 60); param_help("θ", "Polar angle on the Bloch sphere.")
    deg_phi   = st.slider("φ (azimuthal, degrees)", 0, 360, 90); param_help("φ", "Rotation around the Z-axis.")
    shots     = st.slider("Batch shots", 10, 10000, 1000, step=10); param_help("shots", "Repeat teleportation to gather statistics.")
    seed      = st.number_input("Random seed (-1 = random)", value=123, step=1)
    run_one   = st.button("▶ Run ONE teleportation")
    run_many  = st.button("▶ Run MANY teleportations")

    theta = np.deg2rad(deg_theta); phi = np.deg2rad(deg_phi)
    rng = np.random.default_rng(None if seed==-1 else int(seed))
    psi = single_qubit_state_from_bloch(theta, phi)

with colR:
    st.subheader("🎯 Target vs. Bob’s final state (Bloch vectors)")

    if run_one:
        m0, m1, fid, rho_bob, steps = teleportation_once(theta, phi, rng)
        st.info(f"Measurement bits: m0={m0}, m1={m1}  |  Fidelity with target: **{fid:.4f}**")

        rho_target = np.outer(psi, np.conjugate(psi))
        v_target = bloch_vector(rho_target)
        v_bob    = bloch_vector(rho_bob)

        left, right = st.columns(2)
        with left:  st.plotly_chart(bloch_figure(v_target, "Target (Charlie’s |ψ⟩)"), use_container_width=True)
        with right: st.plotly_chart(bloch_figure(v_bob, "Bob’s state after corrections"), use_container_width=True)

        with st.expander("🔎 Step probabilities & classical channel"):
            st.write("Outcome probabilities for (m0,m1):", steps['probs_m0m1'])

    if run_many:
        counts, avg_fid = teleportation_batch(theta, phi, shots, rng)
        st.markdown(f"**Average fidelity over {shots} runs:** **{avg_fid:.4f}**")
        labels = ["00","01","10","11"]
        values = [counts[(0,0)], counts[(0,1)], counts[(1,0)], counts[(1,1)]]
        fig = go.Figure()
        fig.add_bar(x=labels, y=values, name="Counts of (m0 m1)")
        fig.update_layout(title="Distribution of classical bits from Alice", xaxis_title="(m0 m1)", yaxis_title="Counts")
        st.plotly_chart(fig, use_container_width=True)

st.markdown("---")
with st.expander("🧠 Math summary"):
    st.markdown(r"""
Start with \(|ψ⟩_{q0} \otimes |Φ^+⟩_{q1,q2}\).  
Alice applies **CNOT(q0→q1)** and **H(q0)**, measures q0,q1 → bits \((m0,m1)\).  
Bob applies \(Z^{m0} X^{m1}\). Reduced state on Bob becomes **exactly** \(|ψ⟩⟨ψ|\).
""")
st.success("**Takeaway:** Quantum information can move without particles moving — but needs **two classical bits**.")
