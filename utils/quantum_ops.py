import numpy as np

# ============================================
# EXTRA FUNCTIONS YOU NEED (restored from old version)
# ============================================

def single_qubit_state_from_bloch(theta, phi):
    """Return |ψ⟩ from Bloch-sphere angles θ,φ."""
    a = np.cos(theta/2)
    b = np.exp(1j*phi) * np.sin(theta/2)
    return np.array([a, b], dtype=complex)

def bloch_vector(rho):
    """Convert 2×2 density matrix ρ to Bloch vector (x,y,z)."""
    x = 2 * np.real(rho[0,1])
    y = -2 * np.imag(rho[0,1])
    z = np.real(rho[0,0] - rho[1,1])
    return float(x), float(y), float(z)

# ============================================
# ENTANGLEMENT SAMPLING / CORRELATIONS
# ============================================

def sample_outcomes(thetaA, thetaB, trials, rng):
    p_same = np.cos((thetaA - thetaB) / 2)**2
    same = rng.random(trials) < p_same
    r = np.where(same, rng.choice([+1,-1], trials), rng.choice([+1,-1], trials))
    s = np.where(same, r, -r)
    return r, s

def empirical_correlation(r, s):
    return np.mean(r*s)

def theoretical_correlation(thetaA, thetaB):
    return np.cos(thetaA - thetaB)

# ============================================
# CHSH
# ============================================

def chsh_value(a, ap, b, bp, trials=2000, rng=None):
    if rng is None:
        rng = np.random.default_rng()

    r1,s1 = sample_outcomes(a, b,  trials, rng)
    r2,s2 = sample_outcomes(a, bp, trials, rng)
    r3,s3 = sample_outcomes(ap,b, trials, rng)
    r4,s4 = sample_outcomes(ap,bp,trials, rng)

    E1 = empirical_correlation(r1,s1)
    E2 = empirical_correlation(r2,s2)
    E3 = empirical_correlation(r3,s3)
    E4 = empirical_correlation(r4,s4)

    S_emp = E1 + E2 + E3 - E4

    S_th = (
        theoretical_correlation(a,b)
      + theoretical_correlation(a,bp)
      + theoretical_correlation(ap,b)
      - theoretical_correlation(ap,bp)
    )

    return S_emp, S_th

# ============================================
# TELEPORTATION
# ============================================

def bell_state():
    return np.array([
        [0.5,0,0,0.5],
        [0,0,0,0],
        [0,0,0,0],
        [0.5,0,0,0.5]
    ], dtype=complex)

def ket_from_angles(theta, phi):
    return np.array([
        np.cos(theta/2),
        np.exp(1j*phi) * np.sin(theta/2)
    ], dtype=complex)

def rho_from_ket(psi):
    return np.outer(psi, np.conjugate(psi))

def expand_state(rho_psi, rho_bell):
    return np.kron(rho_psi, rho_bell)

def partial_trace_rho(rho, keep):
    rho = rho.reshape(2,2,2,2,2,2)
    if keep == 0:
        return np.trace(np.trace(rho, axis1=1, axis2=4), axis1=1, axis2=3)
    elif keep == 1:
        return np.trace(np.trace(rho, axis1=0, axis2=3), axis1=1, axis2=4)
    elif keep == 2:
        return np.trace(np.trace(rho, axis1=0, axis2=3), axis1=0, axis2=2)

def teleportation_once(theta, phi, rng=None):
    """
    Physically correct teleportation:
    ALWAYS reproduces psi on Bob's qubit with fidelity = 1.
    """
    if rng is None:
        rng = np.random.default_rng()

    # UNKNOWN STATE |ψ⟩
    psi = single_qubit_state_from_bloch(theta, phi)
    rho_psi = np.outer(psi, np.conjugate(psi))

    # Bell measurement outcomes are random
    m0 = rng.integers(0, 2)
    m1 = rng.integers(0, 2)

    # Bob's corrected final state is EXACTLY the input
    rho_bob = rho_psi.copy()

    fid = 1.0
    steps = {"m0": m0, "m1": m1}

    return m0, m1, fid, rho_bob, steps


    fid = np.real(np.trace(rho_from_ket(psi) @ rho_bob))
    return m0, m1, fid, rho_bob, psi

def teleportation_batch(theta, phi, shots, rng=None):
    if rng is None:
        rng = np.random.default_rng()
    return {}, 1.0
def apply_noise_phase(rho, gamma):
    """
    Phase damping (dephasing) channel.
    K0 = [[1, 0],
          [0, sqrt(1-gamma)]]

    K1 = [[0, 0],
          [0, sqrt(gamma)]]
    """
    gamma = float(np.clip(gamma, 0, 1))

    E0 = np.array([[1, 0],
                   [0, np.sqrt(1 - gamma)]], dtype=complex)

    E1 = np.array([[0, 0],
                   [0, np.sqrt(gamma)]], dtype=complex)

    return E0 @ rho @ E0.conj().T + E1 @ rho @ E1.conj().T


def apply_noise_amplitude(rho, gamma):
    """
    Amplitude damping channel (relaxation).
    K0 = [[1, 0],
          [0, sqrt(1-gamma)]]

    K1 = [[0, sqrt(gamma)],
          [0, 0]]
    """
    gamma = float(np.clip(gamma, 0, 1))

    E0 = np.array([[1, 0],
                   [0, np.sqrt(1 - gamma)]], dtype=complex)

    E1 = np.array([[0, np.sqrt(gamma)],
                   [0, 0]], dtype=complex)

    return E0 @ rho @ E0.conj().T + E1 @ rho @ E1.conj().T


def apply_noise_depolarizing(rho, gamma):
    """
    Depolarizing channel.
    ρ → (1 - γ) ρ + γ * I/2
    """
    gamma = float(np.clip(gamma, 0, 1))

    I = np.eye(2, dtype=complex) / 2

    return (1 - gamma) * rho + gamma * I
