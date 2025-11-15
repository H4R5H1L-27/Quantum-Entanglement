import streamlit as st
import numpy as np
import plotly.graph_objects as go

from utils.quantum_ops import sample_outcomes, empirical_correlation, theoretical_correlation

# -------------------------
# Page config
# -------------------------
st.set_page_config(page_title="Entanglement & Correlation", page_icon="🌀", layout="wide")

# -------------------------
# Header CSS (animation)
# -------------------------
HEADER_CSS = """
<style>
.ent-banner {
    display:flex;
    justify-content:center;
    align-items:center;
    margin-top:10px;
    margin-bottom:36px;
}
.coin-hdr {
    width:55px; height:55px;
    border-radius:50%;
    background: radial-gradient(circle at 30% 30%, #FFE8A4, #E9B44C);
    display:flex; justify-content:center; align-items:center;
    font-weight:700; font-size:1.4rem;
    animation: pulse 1.8s infinite;
}
.link {
    width:70px;
    height:4px;
    background:linear-gradient(90deg, #7f5af0, #00c8ff);
    animation: glow 1.8s infinite;
    border-radius:4px;
    margin:0 18px;
}
@keyframes pulse { 0%{transform:scale(1);} 50%{transform:scale(1.12);} 100%{transform:scale(1);} }
@keyframes glow  { 0%{opacity:0.35;} 50%{opacity:1;} 100%{opacity:0.35;} }
</style>
"""
st.markdown(HEADER_CSS, unsafe_allow_html=True)
st.markdown("<div class='ent-banner'><div class='coin-hdr'>A</div><div class='link'></div><div class='coin-hdr'>B</div></div>", unsafe_allow_html=True)

# -------------------------
# Title and intro
# -------------------------
st.markdown("# 🌀 Entanglement & Correlation (Bell Test)")
st.markdown("### Coordinated randomness beyond classical physics.\n")

# -------------------------
# Analogy description
# -------------------------
st.markdown(
    """
### 🪙 Magical Coin Analogy

Imagine Alice and Bob each have a magical coin:

- Each flip is random (Heads or Tails).
- If they tilt their coins to **the same angle**, the coins **always match** — even across planets.
- As their angles differ, the chance of matching drops smoothly (cosine curve).

This behaviour mimics **quantum entanglement**.
"""
)

# -------------------------
# Controls
# -------------------------
st.markdown("## 🕹️ Adjust Coin Angles & Options")

col1, col2, col3, col4 = st.columns([1, 1, 1, 0.6])
with col1:
    degA = st.slider("Alice’s angle (°)", 0, 180, 45)
with col2:
    degB = st.slider("Bob’s angle (°)", 0, 180, 90)
with col3:
    trials = st.slider("Trials", 200, 20000, 2000, step=100)
with col4:
    seed_in = st.number_input("Seed (−1 = random)", value=-1, step=1)

run = st.button("🪙 Run Magical Coin Simulation")
st.markdown("---")

# -------------------------
# Simulation + visuals
# -------------------------
if run:
    # RNG
    rng = np.random.default_rng(None if seed_in == -1 else int(seed_in))

    thetaA = np.deg2rad(degA)
    thetaB = np.deg2rad(degB)

    # sample outcomes (arrays of +1/-1)
    r, s = sample_outcomes(thetaA, thetaB, trials, rng)

    # correlations
    E_emp = empirical_correlation(r, s)
    E_th = theoretical_correlation(thetaA, thetaB)

    # match probability for ring visual
    match_prob = (1 + E_emp) / 2 * 100

    # pick last outcomes for display
    A = "H" if r[-1] == +1 else "T"
    B = "H" if s[-1] == +1 else "T"

    # -------------------------
    # Coin visual (render HTML correctly)
    # -------------------------
    coin_html = f"""
    <style>
    .coin-row {{
        display:flex; justify-content:center; align-items:center;
        gap:70px; margin-top:18px; margin-bottom:20px;
    }}
    .circle {{
        width:74px; height:74px; border-radius:50%;
        background:#FFE8A4; border:4px solid #E3B34C;
        display:flex; justify-content:center; align-items:center;
        font-size:2.1rem; font-weight:800; color:#000000; text-shadow:none;
    }}
    .ring {{
        width:180px; height:180px; border-radius:50%;
        background:conic-gradient(#7f5af0 {match_prob}%, #ccc {match_prob}%);
        display:flex; justify-content:center; align-items:center;
        font-size:1.2rem; font-weight:700; color:#000000; text-shadow:none;
    }}
    .label-small {{ text-align:center; margin-top:6px; font-weight:600; }}
    </style>

    <div class="coin-row">
      <div>
        <div class="circle">{A}</div>
        <div class="label-small">Alice</div>
      </div>

      <div class="ring">{match_prob:.1f}% match</div>

      <div>
        <div class="circle">{B}</div>
        <div class="label-small">Bob</div>
      </div>
    </div>
    """
    st.markdown("## 🎬 Magical Coins in Action")
    st.markdown(coin_html, unsafe_allow_html=True)

    st.success(f"Matching chance ≈ **{match_prob:.1f}%** based on {trials} flips.")

    # -------------------------
    # Animated convergence plot
    # -------------------------
    st.markdown("## ⏳ How Correlation Stabilizes (Animated)")

    placeholder = st.empty()

    running_E = []
    update_every = max(1, trials // 80)  # controls animation frames

    # build progressively but avoid per-step redraw for large trials
    for i in range(1, trials + 1):
        running_E.append(empirical_correlation(r[:i], s[:i]))

        if i % update_every == 0 or i == trials:
            fig2 = go.Figure()
            fig2.add_trace(go.Scatter(
                x=list(range(1, len(running_E) + 1)),
                y=running_E,
                mode="lines",
                line=dict(color="#00c8ff", width=3),
                name="Running E"
            ))
            # add horizontal line for theoretical value
            fig2.add_hline(y=E_th, line_dash="dash", line_color="#7f5af0", annotation_text="Theory", annotation_position="top right")

            fig2.update_layout(
                height=320,
                template="plotly_dark",
                xaxis_title="Trials",
                yaxis_title="Empirical Correlation E",
                yaxis=dict(range=[-1.05, 1.05]),
                showlegend=False,
                margin=dict(t=30, b=30, l=40, r=40)
            )
            placeholder.plotly_chart(fig2, use_container_width=True)

    # -------------------------
    # Quantum curve + markers (final)
    # -------------------------
    st.markdown("## 📈 Quantum Prediction vs Coin Model (Final)")

    dtheta = abs(degA - degB)

    xs = np.linspace(0, np.pi, 240)
    fig = go.Figure()

    # theory curve
    fig.add_trace(go.Scatter(
        x=np.rad2deg(xs),
        y=np.cos(xs),
        mode="lines",
        line=dict(width=3, color="#7f5af0"),
        name="Quantum E(Δθ)"
    ))

    # empirical marker
    fig.add_trace(go.Scatter(
        x=[dtheta],
        y=[E_emp],
        mode="markers",
        marker=dict(size=14, color="#ffdd00"),
        name="Empirical (your run)",
        hovertemplate="Δθ=%{x:.1f}°<br>E_emp=%{y:.3f}<extra></extra>"
    ))

    # theoretical marker at same x
    fig.add_trace(go.Scatter(
        x=[dtheta],
        y=[E_th],
        mode="markers",
        marker=dict(size=12, color="rgba(127,90,240,0.2)", line=dict(color="#7f5af0", width=2)),
        name="Theoretical (cos Δθ)",
        hovertemplate="Δθ=%{x:.1f}°<br>E_th=%{y:.3f}<extra></extra>"
    ))

    fig.update_layout(
        height=420,
        xaxis_title="Angle difference (°)",
        yaxis_title="Correlation E",
        template="plotly_dark",
        yaxis=dict(range=[-1.05, 1.05]),
        legend=dict(orientation="v", x=0.98, xanchor="right")
    )
    st.plotly_chart(fig, use_container_width=True)

    # -------------------------
    # Physical meaning
    # -------------------------
    st.markdown("## 🧠 What This Means Physically")
    st.markdown(
        f"""
- Empirical correlation (E_emp) = **{E_emp:.3f}**  
- Theoretical correlation (cos Δθ) = **{E_th:.3f}**  
- Angle difference Δθ = **{dtheta:.1f}°**  

The purple curve is the ideal quantum prediction; the yellow dot is your simulated result.
With more trials the empirical point moves closer to theory. Increase **Trials** to reduce sampling noise.
"""
    )
