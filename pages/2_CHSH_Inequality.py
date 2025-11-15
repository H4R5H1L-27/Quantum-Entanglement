import streamlit as st
import numpy as np
import plotly.graph_objects as go
from utils.quantum_ops import sample_outcomes, empirical_correlation, theoretical_correlation, chsh_value

# ============================
# PAGE SETTINGS
# ============================
st.set_page_config(page_title="CHSH Inequality", page_icon="🌈", layout="wide")
st.markdown("# 🌈 CHSH Inequality — Quantum vs Classical Limits")
st.markdown("---")

# ============================
# ANALOGY + EXPLANATION
# ============================
st.markdown("""
## 🎮 Game Analogy: Alice & Bob’s Impossible Game

Imagine a game show.

- Alice and Bob are in **separate sealed rooms**  
- Alice can press **A1** or **A2**  
- Bob can press **B1** or **B2**  
- Each press outputs either:  
  - 🟣 **+1**  
  - 🟡 **–1**  
- They **cannot communicate**  
- They try to win points based on how well their outputs match a secret scoring rule  

### Classical World:
No matter how clever their strategy is,  
they cannot beat **S ≤ 2**.

### Quantum World:
If Alice & Bob share entangled particles,  
they can beat the classical limit and reach **S ≈ 2.828**.

This is the CHSH inequality — your experiment will demonstrate it.
""")

st.markdown("---")

# ============================
# SLIDERS (simple, no session state hacks)
# ============================
col1, col2, col3 = st.columns([1, 1, 0.7])

with col1:
    a_deg = st.slider("Alice angle a (°)", 0, 360, 0)
    ap_deg = st.slider("Alice angle a′ (°)", 0, 360, 90)

with col2:
    b_deg = st.slider("Bob angle b (°)", 0, 360, 45)
    bp_deg = st.slider("Bob angle b′ (°)", 0, 360, 315)

with col3:
    trials = st.slider("Trials per correlation", 200, 20000, 2000, step=100)
    seed = st.number_input("Seed (−1 = random)", value=-1, step=1)

colA, colB = st.columns([1, 1])
run_classical = colA.button("🎮 Run Game Analogy Simulation")
run_quantum = colB.button("🌈 Run Quantum CHSH Experiment")

st.markdown("---")

# ============================
# SIMPLE CLASSICAL GAME ANALOGY (clean version)
# ============================
if run_classical:

    rng = np.random.default_rng(None if seed == -1 else int(seed))

    st.markdown("## 🎬 Classical Game Analogy (Simple Version)")
    st.write("This simulation mimics the *classical limit* of the CHSH game. No quantum effects here.")

    # Deterministic classical strategy (cannot exceed S ≤ 2)
    # Alice: A1 → +1, A2 → –1
    # Bob:   B1 → +1, B2 → +1   (a simple LHV model)
    mapping_alice = {1: +1, 2: -1}
    mapping_bob = {1: +1, 2: +1}

    # One simulated round (just for visual effect)
    a_choice = rng.choice([1, 2])
    b_choice = rng.choice([1, 2])

    A = mapping_alice[a_choice]
    B = mapping_bob[b_choice]

    # A batch to compute matching %
    rounds = 1000
    matches = 0
    for _ in range(rounds):
        ac = rng.choice([1, 2])
        bc = rng.choice([1, 2])
        if mapping_alice[ac] == mapping_bob[bc]:
            matches += 1

    match_pct = matches / rounds * 100

    # ====== Visual Output (clean boxes) ======
    colA, colB = st.columns(2)

    def render_box(label, value):
        color = "#FFD86B" if value == +1 else "#9CC0FF"
        sign = "+" if value == +1 else "−"
        return f"""
        <div style='
            display:flex;
            flex-direction:column;
            justify-content:center;
            align-items:center;
            padding:20px;
            border-radius:12px;
            background-color:{color};
            width:140px;
            height:140px;
            font-size:48px;
            font-weight:700;
            color:black;
            margin:auto;
        '>{sign}<div style='font-size:18px;margin-top:10px;'>{label}</div></div>
        """

    with colA:
        st.markdown(render_box(f"Alice (A{a_choice})", A), unsafe_allow_html=True)

    with colB:
        st.markdown(render_box(f"Bob (B{b_choice})", B), unsafe_allow_html=True)

    # Matching % box
    st.markdown(
        f"""
        <div style='
            margin-top:20px;
            padding:18px;
            border-radius:10px;
            background-color:#123d24;
            color:#d5ffe0;
            font-size:20px;
        '>
            Classical matching ≈ <strong>{match_pct:.1f}%</strong> over {rounds} rounds.
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.info("Classical models cannot exceed S = 2 — no matter how clever the strategy.")


# ============================
# QUANTUM CHSH EXPERIMENT
# ============================
if run_quantum:

    rng = np.random.default_rng(None if seed == -1 else int(seed))

    # compute S using helper from utils
    S_emp, S_th = chsh_value(
        np.deg2rad(a_deg), np.deg2rad(ap_deg),
        np.deg2rad(b_deg), np.deg2rad(bp_deg),
        trials=trials, rng=rng
    )

    st.markdown("## 🌈 Actual Quantum CHSH Experiment")

    st.info(
        f"**Empirical S:** {S_emp:.3f}\n\n"
        f"**Quantum Theory S:** {S_th:.3f}\n\n"
        f"**Classical Limit:** 2"
    )

    # Angle differences display
    st.markdown("### 📐 Angle Differences")
    st.markdown(
        f"- Δ(a, b) = **{abs(a_deg - b_deg):.1f}°**  \n"
        f"- Δ(a, b′) = **{abs(a_deg - bp_deg):.1f}°**  \n"
        f"- Δ(a′, b) = **{abs(ap_deg - b_deg):.1f}°**  \n"
        f"- Δ(a′, b′) = **{abs(ap_deg - bp_deg):.1f}°**  \n"
    )

    # BAR PLOT
    fig = go.Figure()
    fig.add_bar(x=["Classical Limit"], y=[2], marker_color="gray")
    fig.add_bar(x=["Empirical |S|"], y=[abs(S_emp)], marker_color="orange")
    fig.add_bar(x=["Quantum Theory"], y=[abs(S_th)], marker_color="purple")
    fig.update_layout(
        title="CHSH S-Value Comparison",
        template="plotly_dark",
        yaxis_title="|S|",
        yaxis=dict(range=[0, 3])
    )
    st.plotly_chart(fig, use_container_width=True)

    # Interpretation
    st.markdown("## 🔍 Interpretation")

    if abs(S_emp) <= 2:
        st.warning("**No violation:** S ≤ 2 → The results can be explained by classical physics.")
    elif 2 < abs(S_emp) < 2.7:
        st.success(f"**Quantum violation detected!** S = {S_emp:.3f} → Nonlocal correlations exist.")
    else:
        st.success(f"**Strong quantum violation!** S = {S_emp:.3f} ≈ Tsirelson bound (2.828).")

# ============================
# VIOLATION HEATMAP
# ============================
st.markdown("---")
st.markdown("## 🔥 Where Do Violations Happen? (Heatmap)")

# Classic CHSH strategy: a' = a + 90°, b' = b + 45°
grid = 80
A = np.linspace(0, np.pi, grid)
B = np.linspace(0, np.pi, grid)
S_map = np.zeros((grid, grid))

for i, a0 in enumerate(A):
    for j, b0 in enumerate(B):
        a_p = a0 + np.pi / 2
        b_p = b0 + np.pi / 4
        S_map[i, j] = (
            np.cos(a0 - b0)
            + np.cos(a0 - b_p)
            + np.cos(a_p - b0)
            - np.cos(a_p - b_p)
        )

heat = go.Figure(
    data=go.Heatmap(
        z=S_map,
        x=np.rad2deg(B),
        y=np.rad2deg(A),
        colorscale="RdBu",
        colorbar=dict(title="S"),
    )
)
heat.update_layout(
    title="CHSH Violation Regions (Red = Higher S)",
    xaxis_title="Bob angle (°)",
    yaxis_title="Alice angle (°)",
)
st.plotly_chart(heat, use_container_width=True)
