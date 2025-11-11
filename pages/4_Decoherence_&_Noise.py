import numpy as np
import streamlit as st
import plotly.graph_objects as go

from utils.ui import inject_quantum_theme, page_header, param_help
from utils.quantum_ops import single_qubit_state_from_bloch, evolve_under_noise, bloch_vector

st.set_page_config(page_title="Decoherence & Noise", page_icon="☁️", layout="wide")
inject_quantum_theme()
page_header("☁️ Decoherence & Noise Models", "Watch quantum states lose coherence under the environment.")

st.markdown("""
### 🎯 Learning Goal
Visualize how **noise** causes quantum states to lose coherence — why superpositions vanish and classical behavior emerges.
""")

with st.expander("📘 Kraus operators (what the noise does)"):
    st.markdown(
r"""
**Phase damping** (dephasing): removes phase info (interference) but keeps energy.  
**Amplitude damping** (relaxation): energy leaks from \(|1⟩\) to \(|0⟩\).

Evolution: \(\rho' = \sum_i E_i \rho E_i^\dagger\).
""")
with st.expander("📘 Deep Explanation: Decoherence and the Quantum–Classical Transition"):
    st.markdown("""
    ### 🌫️ What is decoherence?
    Decoherence is how quantum systems lose their “quantumness.”  
    It’s what happens when a qubit interacts with its surroundings — the environment “measures” it and erases interference.

    ### ⚙️ Two kinds of noise
    - **Phase damping**: random phase shifts blur interference fringes.  
      The qubit loses its superposition phase (off-diagonal terms → 0) but keeps populations.
    - **Amplitude damping**: energy leaks out.  
      The qubit relaxes from |1⟩ (excited) to |0⟩ (ground), like an atom emitting a photon.

    ### 💡 The physics
    Mathematically, each process is a **Kraus channel** — a set of operators {E₀, E₁} that evolve the density matrix:
    \[
    \rho' = E_0 \rho E_0^\dagger + E_1 \rho E_1^\dagger
    \]
    As the noise parameter γ increases from 0 → 1:
    - Coherence |ρ₀₁| shrinks.
    - The Bloch vector moves inward → mixed state.
    - Eventually, only classical probabilities remain.

    ### 🧭 What to look for
    - In the Bloch sphere: the state’s arrow shortens toward the center.
    - In the graphs: off-diagonal |ρ₀₁| decays; populations drift toward equilibrium.

    ### 🌍 Why it matters
    Decoherence explains why macroscopic objects (like cats, planets, or humans) don’t show quantum weirdness — they constantly interact with billions of particles in the environment.

    It’s also the main challenge in building **quantum computers** — keeping qubits isolated and coherent long enough to compute.
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
    st.subheader("🎚️ Controls")
    model     = st.radio("Noise model", ["phase", "amplitude"], index=0)
    param_help("phase", "Destroys phase (off-diagonals). Populations remain.")
    param_help("amplitude", "Energy loss: |1⟩ → |0⟩ (populations change).")
    deg_theta = st.slider("Initial θ (deg)", 0, 180, 60); param_help("θ", "Polar angle on the Bloch sphere.")
    deg_phi   = st.slider("Initial φ (deg)", 0, 360, 90); param_help("φ", "Rotation around Z.")
    steps     = st.slider("Resolution (γ steps)", 5, 200, 40, step=5); param_help("γ steps", "Number of points from 0 → 1.")
    animate   = st.checkbox("Animate decoherence (0 → 1)")

    theta = np.deg2rad(deg_theta); phi = np.deg2rad(deg_phi)
    gammas = np.linspace(0, 1, steps)
    states, coherences, bloch = evolve_under_noise(theta, phi, gammas, model)
    v0 = bloch[0]; v1 = bloch[-1]

    if animate:
        frames = []
        for i, vec in enumerate(bloch):
            x,y,z = vec
            frames.append(go.Frame(
                data=[go.Scatter3d(x=[0,x], y=[0,y], z=[0,z], mode="lines+markers", name="state")],
                name=f"g={gammas[i]:.2f}"
            ))
        figA = bloch_figure(v0, f"Bloch vector under {model} damping")
        figA.frames = frames
        figA.update_layout(
            updatemenus=[dict(type="buttons",
                              buttons=[dict(label="Play", method="animate",
                                            args=[None, {"frame": {"duration": 120, "redraw": True}, "fromcurrent": True}]),
                                       dict(label="Pause", method="animate",
                                            args=[[None], {"mode": "immediate", "frame": {"duration": 0, "redraw": False}}])])],
            sliders=[dict(steps=[dict(method="animate",
                                      args=[[f'g={gammas[i]:.2f}'], {"mode":"immediate","frame":{"duration":0,"redraw":True}}],
                                      label=f"{gammas[i]:.2f}") for i in range(len(gammas))])]
        )
    else:
        figA = bloch_figure(v1, f"Final Bloch vector at γ=1.0 ({model})")

with colR:
    st.subheader("📉 Coherence and populations vs γ")
    gdeg = gammas * 100
    # coherence |rho01|
    fig1 = go.Figure()
    fig1.add_scatter(x=gdeg, y=coherences, mode="lines+markers", name="|ρ01|")
    fig1.update_layout(title="Coherence magnitude |ρ01| vs γ", xaxis_title="γ (%)", yaxis_title="|ρ01|")
    # populations ρ00 and ρ11
    p00 = [np.real(r[0,0]) for r in states]; p11 = [np.real(r[1,1]) for r in states]
    fig2 = go.Figure()
    fig2.add_scatter(x=gdeg, y=p00, mode="lines+markers", name="ρ00")
    fig2.add_scatter(x=gdeg, y=p11, mode="lines+markers", name="ρ11")
    fig2.update_layout(title="Populations vs γ", xaxis_title="γ (%)", yaxis_title="Probability", yaxis=dict(range=[0,1]))

    left, right = st.columns(2)
    with left:  st.plotly_chart(fig1, use_container_width=True)
    with right: st.plotly_chart(fig2, use_container_width=True)

st.subheader("🌐 Bloch visualization")
st.plotly_chart(figA, use_container_width=True)

st.markdown("---")
with st.expander("🌫️ Intuition"):
    st.markdown("""
- **Phase damping:** like two clocks slowly losing sync — X/Y information vanishes, Z stays.  
- **Amplitude damping:** an excited atom relaxes — probability flows toward **|0⟩**.
""")
st.success("**Takeaway:** Interaction with the environment erases quantum coherence → the classical world emerges.")
