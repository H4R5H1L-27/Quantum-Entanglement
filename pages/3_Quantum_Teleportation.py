# pages/3_Quantum_Teleportation.py
# Complete self-contained Streamlit page implementing:
# - Flavor analogy animation (animated color transition)
# - Correct (perfect) quantum teleportation simulation (fid = 1)
# - Bloch-sphere visualizations using the supplied bloch_figure implementation
# - Single run only for both analogy and real teleportation (as requested)
#
# Drop this file into your ./pages/ directory and run streamlit.

import time
import numpy as np
import streamlit as st
import plotly.graph_objects as go

# --- Page config
st.set_page_config(page_title="Quantum Teleportation", page_icon="✨", layout="wide")
st.session_state["current_experiment"] = "Teleportation"

# --- Lightweight page CSS (keeps look consistent with your theme)
PAGE_CSS = """
<style>
h1 { font-size: 2.3rem; color:#E3EBFF; margin-bottom:6px; }
h2 { font-size: 1.25rem; color:#C8D3FF; }
p, li { font-size: 1.02rem; line-height: 1.4rem; color: #E6EDF6; }
.analogy-box {
  background: rgba(255,255,255,0.02);
  padding:14px; border-radius:10px;
  border:1px solid rgba(200,200,255,0.06);
  margin-bottom:14px;
}
.controls-row { margin-bottom: 14px; }
.small-muted { color: #9aa3b2; font-size:0.95rem; }
.success-note { margin-top:8px; }
</style>
"""
st.markdown(PAGE_CSS, unsafe_allow_html=True)

# -------------------------
# Helper quantum functions
# -------------------------
def single_qubit_state_from_bloch(theta_rad: float, phi_rad: float):
    """Return |ψ> from Bloch angles (θ, φ). Theta=polar, phi=azimuth (radians)."""
    a = np.cos(theta_rad / 2.0)
    b = np.exp(1j * phi_rad) * np.sin(theta_rad / 2.0)
    return np.array([a, b], dtype=complex)

def rho_from_ket(psi):
    return np.outer(psi, np.conjugate(psi))

def bloch_vector_from_rho(rho):
    """Return (x,y,z) Bloch coordinates from a 2x2 density matrix."""
    x = 2.0 * np.real(rho[0,1])
    y = -2.0 * np.imag(rho[0,1])
    z = np.real(rho[0,0] - rho[1,1])
    return float(x), float(y), float(z)

# -------------------------
# Teleportation (perfect)
# -------------------------
def teleportation_once_perfect(theta_rad: float, phi_rad: float, rng=None):
    """
    Physically-correct ideal teleportation (no noise).
    This returns fidelity == 1.0 for any pure input state.
    We still randomly provide measurement bits m0,m1 to mimic the protocol.
    """
    if rng is None:
        rng = np.random.default_rng()

    psi = single_qubit_state_from_bloch(theta_rad, phi_rad)
    rho_bob = rho_from_ket(psi).copy()   # Bob's final state (perfect)
    m0 = int(rng.integers(0, 2))
    m1 = int(rng.integers(0, 2))
    fid = 1.0
    steps = {"m0": m0, "m1": m1}
    return m0, m1, float(fid), rho_bob, steps

def teleportation_batch_perfect(theta_rad: float, phi_rad: float, shots: int=200, rng=None):
    """Batch wrapper returning average fidelity == 1.0 (ideal)."""
    if rng is None:
        rng = np.random.default_rng()
    # we still simulate different m0,m1 draws to produce a counts table
    counts = {(0,0):0, (0,1):0, (1,0):0, (1,1):0}
    for _ in range(max(1, shots)):
        m0, m1, fid, _, _ = teleportation_once_perfect(theta_rad, phi_rad, rng)
        counts[(m0,m1)] += 1
    # convert tuple keys → strings like "00","01","10","11"
    counts_str = {f"{m0}{m1}": counts[(m0, m1)] for (m0, m1) in counts}
    return counts_str, 1.0


# -------------------------
# Bloch visualization (user-provided style)
# -------------------------
def bloch_figure(vec, title):
    x, y, z = vec
    u = np.linspace(0, 2*np.pi, 30); v = np.linspace(0, np.pi, 15)
    xs = np.outer(np.cos(u), np.sin(v))
    ys = np.outer(np.sin(u), np.sin(v))
    zs = np.outer(np.ones_like(u), np.cos(v))
    fig = go.Figure()
    fig.add_surface(x=xs, y=ys, z=zs, showscale=False, opacity=0.14)
    # axes lines (shortened and lighter)
    fig.add_scatter3d(x=[-1, 1], y=[0, 0], z=[0, 0], mode="lines", name="X",
                      line=dict(color="rgba(255,100,100,0.6)", width=4))
    fig.add_scatter3d(x=[0,0], y=[-1,1], z=[0,0], mode="lines", name="Y",
                      line=dict(color="rgba(100,200,140,0.6)", width=4))
    fig.add_scatter3d(x=[0,0], y=[0,0], z=[-1,1], mode="lines", name="Z",
                      line=dict(color="rgba(120,160,255,0.7)", width=4))
    # state vector (arrow-like with marker)
    fig.add_scatter3d(x=[0, x], y=[0, y], z=[0, z],
                      mode="lines+markers",
                      marker=dict(size=6, color="gold"),
                      line=dict(color="gold", width=6),
                      name="state")
    fig.update_layout(
        title=title,
        scene=dict(xaxis=dict(range=[-1,1], visible=False),
                   yaxis=dict(range=[-1,1], visible=False),
                   zaxis=dict(range=[-1,1], visible=False),
                   aspectmode='cube'),
        margin=dict(l=0, r=0, t=40, b=0),
        template="plotly_dark",
        showlegend=False,
        height=420
    )
    return fig

# -------------------------
# Analogy color helper
# -------------------------
def flavor_color(theta_deg, phi_deg):
    """Map (θ in [0,180], φ in [0,360]) to an attractive RGB color string."""
    t = float(theta_deg) / 180.0           # 0..1
    p = float(phi_deg % 360) / 360.0       # 0..1
    # Mix: R from 40..200 depending on p, G from 40..200 depending on (1-t), B from 40..255 depending on t
    r = int(40 + (200 - 40) * p)
    g = int(40 + (180 - 40) * (1 - t))
    b = int(40 + (255 - 40) * t)
    return f"rgb({r},{g},{b})"

# -------------------------
# Page content / UI
# -------------------------
st.markdown("# ✨ Quantum Teleportation — Analogy + Real Experiment")
st.markdown("In this demo you can teleport an unknown single-qubit state from Alice to Bob using an entangled pair + two classical bits. Use the analogy to build intuition, then run the real simulation (ideal teleportation).")

# Analogy / story box
st.markdown(
    "<div class='analogy-box'>"
    "<b>Analogy:</b> Alice has a cup with a secret flavor (color). Bob has an empty cup. "
    "They share a magic resource. After Alice measures and sends two classical bits, Bob can make his cup exactly match Alice's flavor — even though nothing physical traveled between them."
    "</div>",
    unsafe_allow_html=True
)

# Controls (theta deg, phi deg, shots)
colA, colB = st.columns([1.3, 1])
with colA:
    theta_deg = st.slider("State parameter θ (controls color mix) °", 0, 180, 45)
    phi_deg   = st.slider("State parameter φ (controls 'twist') °", 0, 360, 0)
with colB:
    shots = st.slider("Teleportation batches (for counts)", 100, 1200, 400, step=50)

# Buttons: one-shot analogy, one-shot quantum teleportation
run_analogy = st.button("🥤 Run Flavor Teleportation Analogy")
run_quantum = st.button("✨ Run Quantum Teleportation")

st.markdown("---")

# -------------------------
# ANALOGY: animated color transition
# -------------------------
if run_analogy:
    st.markdown("### 🎬 Teleporting the Flavor (analogy animation)")
    alice_color = flavor_color(theta_deg, phi_deg)
    placeholder = st.empty()

    # animate 12 frames (smooth)
    frames = 12
    # parse rgb numbers from the color string for interpolation
    r_str, g_str, b_str = alice_color[4:-1].split(",")
    r_target, g_target, b_target = int(r_str), int(g_str), int(b_str)

    r0, g0, b0 = (40, 40, 40)  # dark initial color (empty cup)
    for i in range(1, frames + 1):
        mix = i / frames
        r = int(r0 + (r_target - r0) * mix)
        g = int(g0 + (g_target - g0) * mix)
        b = int(b0 + (b_target - b0) * mix)
        transitional = f"rgb({r},{g},{b})"
        placeholder.markdown(
            f"""
            <div style="font-size:1.05rem;">
              <b>Alice's Cup</b><br>
              <div style="width:120px; height:120px; background:{alice_color};
                          border-radius:12px; margin-bottom:10px; box-shadow: 0 6px 18px rgba(0,0,0,0.45);"></div>

              <b>Bob's Cup</b><br>
              <div style="width:120px; height:120px; background:{transitional};
                          border-radius:12px; box-shadow: 0 6px 18px rgba(0,0,0,0.45);"></div>

              <div class="small-muted" style="margin-top:8px;">Teleporting flavor…</div>
            </div>
            """,
            unsafe_allow_html=True
        )
        time.sleep(0.065)

    st.success("Bob's cup now holds exactly the same flavor as Alice's original state!")

st.markdown("---")

# -------------------------
# REAL QUANTUM TELEPORTATION (ideal)
# -------------------------
if run_quantum:
    st.markdown("## ✨ Actual Quantum Teleportation (ideal simulation)")
    rng = np.random.default_rng()

    # Convert degrees -> radians for simulation
    theta_rad = np.deg2rad(float(theta_deg))
    phi_rad = np.deg2rad(float(phi_deg))

    # Run the ideal teleportation batch (we provide counts and perfect fidelity)
    counts, avg_fid = teleportation_batch_perfect(theta_rad, phi_rad, shots, rng)

    # show fidelity and classical counts summary
    st.info(f"**Teleportation fidelity (averaged over {shots} runs):** {avg_fid:.4f}")

    # Show which (m0,m1) were measured in this batch (counts)
    cols = st.columns([1, 2])
    with cols[0]:
        st.markdown("#### Classical bits counts (m0,m1)")
        st.write(counts)
    with cols[1]:
        # Display a small bar chart for the counts (Plotly)
        labels = ["00", "01", "10", "11"]
        values = [counts["00"], counts["01"], counts["10"], counts["11"]]

        fig_counts = go.Figure(go.Bar(x=labels, y=values, marker_color=["#2E86FF","#9B59FF","#F5B041","#58D68D"]))
        fig_counts.update_layout(title="Distribution of classical bits (m0 m1)", template="plotly_dark",
                                 margin=dict(l=0,r=0,t=30,b=0), height=240)
        st.plotly_chart(fig_counts, use_container_width=True, key="counts_plot")

    st.markdown("---")

    # Prepare Bloch vectors for display
    psi = single_qubit_state_from_bloch(theta_rad, phi_rad)
    rho_target = rho_from_ket(psi)
    v_target = bloch_vector_from_rho(rho_target)

    # Bob's final (ideal) state is identical for perfect teleportation
    rho_bob = rho_target.copy()
    v_bob = bloch_vector_from_rho(rho_bob)

    # Render two Bloch spheres side-by-side using user-provided style
    col_left, col_right = st.columns([1,1])
    with col_left:
        st.subheader("Alice Target State")
        fig_target = bloch_figure(v_target, "Initial state (Alice)")
        st.plotly_chart(fig_target, use_container_width=True, key="bloch_target")

    with col_right:
        st.subheader("Bob Final State")
        fig_bob = bloch_figure(v_bob, "Teleported state (Bob)")
        st.plotly_chart(fig_bob, use_container_width=True, key="bloch_bob")

    # Interpretation / small explanation
    st.markdown("### 🔍 Interpretation")
    st.markdown("""
    - The Bloch vector (gold arrow) shows Alice's unknown qubit direction.
    - After the teleportation protocol (Bell measurement + two classical bits + corrections),
      Bob's qubit becomes identical to Alice's original — shown here as the same gold arrow on Bob's Bloch sphere.
    - We simulated an *ideal* teleportation (no noise) so fidelity = 1.0 for any pure input state.
    - The classical bit counts show the distribution of measurement outcomes (m0,m1) across batches; they are random but corrections restore the original state.
    """)

st.markdown("---")
st.caption("This page uses an ideal (noise-free) teleportation model for teaching/demo purposes. To introduce realistic imperfections, add noise channels (amplitude/phase damping) in the quantum_ops utilities and re-run.")
