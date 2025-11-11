import streamlit as st

QUANTUM_CSS = """
<style>
/* subtle starfield + grid */
body {
  background-image:
    radial-gradient(ellipse at center, rgba(138,127,255,0.05) 0%, rgba(14,15,26,0) 60%),
    linear-gradient(rgba(255,255,255,0.03) 1px, transparent 1px),
    linear-gradient(90deg, rgba(255,255,255,0.03) 1px, transparent 1px);
  background-size: cover, 40px 40px, 40px 40px;
  background-repeat: no-repeat, repeat, repeat;
  background-position: center center, 0 0, 0 0;
}
.block-container { padding-top: 1.1rem; }

/* gradient headers + soft glow */
h1, h2, .quantum-title {
  background: linear-gradient(90deg,#9B8FFF,#64E1FF 60%,#7DF3C5);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
}
div.stAlert, div.stSuccess, div.stInfo, div.stWarning {
  box-shadow: 0 0 18px rgba(138,127,255,.15);
  border-radius: 16px !important;
}

/* parameter pills */
.param-label {
  display:inline-block; padding:.2rem .55rem; margin:.2rem .45rem .2rem 0;
  border-radius:999px; background:#1d2140; color:#CDD5FF; font-size:.82rem;
  border:1px solid rgba(138,127,255,.25);
}

/* small caption */
.q-cap { color:#A9B1D6; font-size:.95rem; }
</style>
"""

def inject_quantum_theme():
    st.markdown(QUANTUM_CSS, unsafe_allow_html=True)

def page_header(title: str, subtitle: str = ""):
    st.markdown(f"<h1 class='quantum-title'>{title}</h1>", unsafe_allow_html=True)
    if subtitle:
        st.markdown(f"<p class='q-cap'>{subtitle}</p>", unsafe_allow_html=True)

def param_help(label: str, text: str):
    st.markdown(f"<span class='param-label'>{label}</span> {text}", unsafe_allow_html=True)
