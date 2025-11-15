import streamlit as st
import numpy as np
import plotly.graph_objects as go
import time
import base64

from utils.quantum_ops import (
    apply_noise_phase, 
    apply_noise_amplitude, 
    apply_noise_depolarizing
)
def load_base64_image(path):
    with open(path, "rb") as f:
        data = f.read()
    return "data:image/png;base64," + base64.b64encode(data).decode()
EMBED_IMAGE = (
"data:image/png;base64,"
"iVBORw0KGgoAAAANSUhEUgAAAMgAAADICAMAAACahl6sAAAAMFBMVEX////w8PDFxcW7u7uGhobv7+/"
"r6+vT09OYmJjo6OihobHc3Ny3t7eioqKdnZ3U1NTEw8S4AAACMElEQVR4nO3bS07DMAwFUDkGooy2/"
"79pQpVJVpazlRtWLpmjHtkobaN6D+PfYZ7RUTpujISiFDUFxIr05oig3NbS1RyCBjIhF6kKIhxCB3s"
"RDaYJxCF3sIV+igBxCB3sQDaYJxCF3sQTaYJxCF3sQTaYJxCF3sQTaYJxCF3sQTaYJxCF3sQTaYJxC"
"F3sQTaYJxCF3sQTaYJxCF3sQTaYJxCF3sQTaYJxCF3sQTaYJxCF3sQTaYJxCF3sQTaYJxCF3sQTaYJ"
"xCF3sQTaYJxCF3sQTZojtDQdzPEwQX5XAbAVYSEuxsjjXNMTvEihQ/HUkHf8cQmiVjCwXTlzAIXazh"
"JzStO2Qd6hw2yY7jYdo8+E9RbMh8j+x0dFbB+1oGf4bm/FvGV8eK3vp4eGztqKq7aj3Hy+XapnwXCf"
"DIeEJD7BqXc9E+u6KD//Am8ZI1sC3yRyvE4s46HoPazTA/gkGEXUXMaLLfi5yRvCNrI6VsgGAaHo9d"
"IO4D4ew3Efr2E1VlzDqgW8sELpAo7P5NdQ4KJc4D+Xe/Q4KJc4D+Xe/Q4KJc4D+Xe/Q4KJc4D+Xe/Q"
"4KJc4D+Xe/Q4KJc4D+Xe/Q4KJc4D+Xe/Q4KJc4D+Xe/Q4KJc4D+Xe/Q4KJc4D+Xe/Q4KJc4D+Xe/Q4"
"KJc4D+Xe/Q4KJc4D+Xe/Q4KJc4D+Xe/Q4KJc4D+Xe/Q4OJeoHGIcQgdxoAAAAASUVORK5CYII="
)


# =========================
# PAGE SETUP
# =========================
st.set_page_config(page_title="Decoherence & Noise", page_icon="☁️", layout="wide")
st.session_state["current_experiment"] = "Decoherence"

PAGE_CSS = """
<style>
h1 { font-size: 2.3rem; color:#E3EBFF; }
h2 { font-size: 1.25rem; color:#C8D3FF; }
p, li { font-size: 1.05rem; line-height: 1.55rem; }
.analogy-box {
  background: rgba(255,255,255,0.03); 
  padding:15px; border-radius:12px;
  border:1px solid rgba(200,200,255,0.10);
  margin-bottom:18px;
}
.blur-box {
    width:150px; height:150px;
    border-radius: 12px;
    border:1px solid rgba(200,200,255,0.10);
    margin-bottom:10px;
}
.big-graph {
  background:rgba(255,255,255,0.03);
  padding:18px; border-radius:15px;
  margin-top:20px;
}
</style>
"""
st.markdown(PAGE_CSS, unsafe_allow_html=True)

# =========================
# PAGE TITLE
# =========================
st.markdown("# ☁️ Decoherence & Noise")
st.markdown("### How quantum states slowly lose their 'quantumness'")

# =========================
# Analogy
# =========================
st.markdown("## 🎨 Analogy: A Picture Slowly Blurring")

st.markdown(
"""
<div class='analogy-box'>
Imagine a crisp, bright photograph.<br><br>

As the **environment interferes** (air, heat, vibrations),
the picture becomes:

- less sharp  
- less colorful  
- eventually just **gray**  
<br>
This is exactly what **decoherence** does to a quantum state:
it smears the delicate quantum information until nothing remains.
</div>
""",
unsafe_allow_html=True
)

# =========================
# Controls
# =========================
colA, colB = st.columns([1.2, 1])

with colA:
    noise_type = st.selectbox(
        "Choose noise model",
        ["Phase Damping", "Amplitude Damping", "Depolarizing Noise"]
    )

with colB:
    strength = st.slider("Noise strength γ (0 → none, 1 → max)", 0.0, 1.0, 0.3, step=0.05)

run_analogy = st.button("🎨 Run Blurring Analogy")
run_quantum = st.button("☁️ Apply Noise to Bloch Sphere")

st.markdown("---")

# =========================
# ANALOGY — Visual Blur
# =========================
def blur_radius(gamma):
    """Simple linear mapping to blur intensity."""
    return gamma * 10
def blur_intensity(gamma: float):
    """Map noise strength to CSS blur radius."""
    return gamma * 8   # scale the blur effect

if run_analogy:
    st.markdown("### 🎬 Visualizing Decoherence…")

    placeholder = st.empty()

    for i in range(12):
        g = (i / 11) * strength
        blur = g * 8  # blur in px

        html = f"""
<div style='font-size:1.2rem; color:#E3EBFF;'>

<b>Original Image:</b><br>
<img src="{EMBED_IMAGE}"
     style="width:150px; height:150px; border-radius:12px;
            border:1px solid rgba(200,200,255,0.10); margin-bottom:15px;
            filter:blur(0px);">

<b>After Noise (γ = {g:.2f}):</b><br>
<img src="{EMBED_IMAGE}"
     style="width:150px; height:150px; border-radius:12px;
            border:1px solid rgba(200,200,255,0.10); margin-bottom:15px;
            filter:blur({blur}px);">

</div>
"""

        placeholder.markdown(html, unsafe_allow_html=True)

        time.sleep(0.08)

    st.success("The increasing blur represents decoherence — loss of quantum coherence.")




st.markdown("---")

# =========================
# BLOCH SPHERE — Quantum Decoherence
# =========================
def bloch_from_rho(rho):
    """Convert density matrix → Bloch coords."""
    x = 2 * np.real(rho[0,1])
    y = -2 * np.imag(rho[0,1])
    z = np.real(rho[0,0] - rho[1,1])
    return x, y, z

# Your preferred Bloch renderer
def bloch_figure(vec, title):
    x,y,z = vec
    u = np.linspace(0, 2*np.pi, 30)
    v = np.linspace(0, np.pi, 15)
    xs = np.outer(np.cos(u), np.sin(v))
    ys = np.outer(np.sin(u), np.sin(v))
    zs = np.outer(np.ones_like(u), np.cos(v))

    fig = go.Figure()
    fig.add_surface(x=xs, y=ys, z=zs, showscale=False, opacity=0.15)

    # Axes
    fig.add_scatter3d(x=[-1,1], y=[0,0], z=[0,0], mode="lines", name="X")
    fig.add_scatter3d(x=[0,0], y=[-1,1], z=[0,0], mode="lines", name="Y")
    fig.add_scatter3d(x=[0,0], y=[0,0], z=[-1,1], mode="lines", name="Z")

    # State vector
    fig.add_scatter3d(
        x=[0, x], y=[0, y], z=[0, z],
        mode="lines+markers",
        name="state",
        marker=dict(size=4, color="#7CFC00")
    )

    fig.update_layout(
        title=title,
        scene=dict(xaxis=dict(range=[-1,1]),
                   yaxis=dict(range=[-1,1]),
                   zaxis=dict(range=[-1,1])),
        margin=dict(l=0,r=0,t=50,b=0),
        height=450
    )
    return fig

# =========================
# Apply Noise
# =========================
if run_quantum:
    st.markdown("## ☁️ Bloch Sphere Under Decoherence")

    # Starting state = |+>
    rho0 = np.array([[0.5, 0.5],
                     [0.5, 0.5]], dtype=complex)

    # Apply chosen noise model
    if noise_type == "Phase Damping":
        rho = apply_noise_phase(rho0, strength)
    elif noise_type == "Amplitude Damping":
        rho = apply_noise_amplitude(rho0, strength)
    else:
        rho = apply_noise_depolarizing(rho0, strength)

    # Extract vectors
    vec0 = bloch_from_rho(rho0)
    vec1 = bloch_from_rho(rho)

    # Compute coherence loss
    r0 = np.linalg.norm(vec0)
    r1 = np.linalg.norm(vec1)

    st.info(f"**Bloch radius before:** {r0:.3f} → **after noise:** {r1:.3f}")

    # Layout
    col1, col2 = st.columns(2)

    with col1:
        st.write("### Initial State (|+⟩)")
        st.plotly_chart(bloch_figure(vec0, "Initial State"), use_container_width=True)

    with col2:
        st.write(f"### After Noise ({noise_type})")
        st.plotly_chart(bloch_figure(vec1, "After Noise"), use_container_width=True)

    st.markdown("### 🔍 Interpretation")
    st.markdown(f"""
- The Bloch vector starts long and well-defined (**coherent**).
- Noise causes the vector to **shrink**, representing information loss.
- Stronger γ → stronger shrink → state becomes mixed.
- Different noise models destroy coherence differently.
""")
