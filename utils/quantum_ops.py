import numpy as np

# ====================== Common helpers ======================
def kron(*ops):
    res = np.array([[1.0+0j]])
    for A in ops:
        res = np.kron(res, A)
    return res

def bloch_to_state(theta: float, phi: float) -> np.ndarray:
    a = np.cos(theta/2.0)
    b = np.exp(1j*phi) * np.sin(theta/2.0)
    return np.array([a, b], dtype=complex)

def density_matrix(state: np.ndarray) -> np.ndarray:
    return np.outer(state, np.conjugate(state))

def bloch_vector(rho1: np.ndarray):
    x = 2*np.real(rho1[0,1])
    y = -2*np.imag(rho1[0,1])
    z = np.real(rho1[0,0] - rho1[1,1])
    return float(x), float(y), float(z)

# ====================== Bell state / CHSH ======================
def bell_phi_plus():
    state = np.zeros(4, dtype=complex)
    state[0] = 1/np.sqrt(2)  # |00>
    state[3] = 1/np.sqrt(2)  # |11>
    return state

def projector_along_theta(theta: float, outcome: int):
    c = np.cos(theta/2.0)
    s = np.sin(theta/2.0)
    v = np.array([c, s], dtype=complex) if outcome == +1 else np.array([-s, c], dtype=complex)
    return np.outer(v, np.conjugate(v))

def joint_probabilities(theta_a: float, theta_b: float, state: np.ndarray = None):
    if state is None:
        state = bell_phi_plus()
    rho = np.outer(state, np.conjugate(state))
    probs = {}
    for r in (+1, -1):
        for s in (+1, -1):
            Pa = projector_along_theta(theta_a, r)
            Pb = projector_along_theta(theta_b, s)
            Pab = kron(Pa, Pb)
            probs[(r, s)] = float(np.real(np.trace(Pab @ rho)))
    Z = sum(probs.values())
    for k in probs:  # normalize and remove tiny negatives
        probs[k] = max(0.0, probs[k]/Z)
    return probs

def sample_outcomes(theta_a: float, theta_b: float, trials: int, rng=None):
    if rng is None:
        rng = np.random.default_rng()
    probs = joint_probabilities(theta_a, theta_b)
    keys = [(+1,+1),(+1,-1),(-1,+1),(-1,-1)]
    p = np.array([probs[k] for k in keys])
    idx = rng.choice(4, size=trials, p=p)
    mapping = {0:(+1,+1), 1:(+1,-1), 2:(-1,+1), 3:(-1,-1)}
    rs = np.array([mapping[i] for i in idx])
    r = rs[:,0]; s = rs[:,1]
    return r, s

def empirical_correlation(r, s):
    return float(np.mean(r * s))

def theoretical_correlation(theta_a: float, theta_b: float):
    return float(np.cos(theta_a - theta_b))

def sweep_correlation(theta_a: float, deltas: np.ndarray, trials_each: int = 2000, rng=None):
    if rng is None:
        rng = np.random.default_rng()
    emp, th = [], []
    for d in deltas:
        theta_b = theta_a + d
        r, s = sample_outcomes(theta_a, theta_b, trials_each, rng)
        emp.append(empirical_correlation(r, s))
        th.append(theoretical_correlation(theta_a, theta_b))
    return np.array(emp), np.array(th)

def chsh_value(theta_a, theta_ap, theta_b, theta_bp, trials=2000, rng=None):
    if rng is None:
        rng = np.random.default_rng()
    r1, s1 = sample_outcomes(theta_a, theta_b,  trials, rng)
    r2, s2 = sample_outcomes(theta_a, theta_bp, trials, rng)
    r3, s3 = sample_outcomes(theta_ap, theta_b,  trials, rng)
    r4, s4 = sample_outcomes(theta_ap, theta_bp, trials, rng)
    E1 = empirical_correlation(r1, s1)
    E2 = empirical_correlation(r2, s2)
    E3 = empirical_correlation(r3, s3)
    E4 = empirical_correlation(r4, s4)
    S_emp = E1 + E2 + E3 - E4
    S_th = (np.cos(theta_a - theta_b) + np.cos(theta_a - theta_bp)
            + np.cos(theta_ap - theta_b) - np.cos(theta_ap - theta_bp))
    return S_emp, S_th

# ====================== Teleportation ======================
I = np.eye(2, dtype=complex)
X = np.array([[0,1],[1,0]], dtype=complex)
Z = np.array([[1,0],[0,-1]], dtype=complex)
H = (1/np.sqrt(2)) * np.array([[1,1],[1,-1]], dtype=complex)

def single_qubit_state_from_bloch(theta: float, phi: float) -> np.ndarray:
    a = np.cos(theta/2.0); b = np.exp(1j*phi) * np.sin(theta/2.0)
    return np.array([a,b], dtype=complex)

def apply_single_qubit(state: np.ndarray, U: np.ndarray, target: int, n_qubits=3) -> np.ndarray:
    ops = [U if q==target else I for q in range(n_qubits)]
    U_full = ops[0]
    for k in range(1, n_qubits):
        U_full = np.kron(U_full, ops[k])
    return U_full @ state

def apply_cnot(state: np.ndarray, control: int, target: int, n_qubits=3) -> np.ndarray:
    dim = 2**n_qubits
    out = np.zeros_like(state)
    for basis in range(dim):
        bits = [(basis >> (n_qubits-1-q)) & 1 for q in range(n_qubits)]
        if bits[control] == 1:
            bits[target] ^= 1
            nb = 0
            for q in range(n_qubits):
                nb = (nb<<1) | bits[q]
            out[nb] += state[basis]
        else:
            out[basis] += state[basis]
    return out

def partial_trace_rho(rho: np.ndarray, keep: int, n_qubits=3) -> np.ndarray:
    """
    Reduced state of 'keep' by tracing out others (robust axis handling).
    rho: (2**n x 2**n)
    keep: 0,1,2 for which qubit to keep
    """
    rho = rho.reshape([2]*n_qubits*2)  # (2,2,2, 2,2,2) for 3 qubits
    left = list(range(n_qubits))
    right = [i+n_qubits for i in range(n_qubits)]
    for q in sorted([i for i in range(n_qubits) if i != keep], reverse=True):
        rho = np.trace(rho, axis1=q, axis2=right[q])
        left.pop(q); right.pop(q)
        right = [i-1 if i > q else i for i in right]
    return rho.reshape(2,2)

def teleportation_once(theta: float, phi: float, rng=None):
    if rng is None:
        rng = np.random.default_rng()
    psi = single_qubit_state_from_bloch(theta, phi)

    # |psi> ⊗ |0> ⊗ |0>
    state = np.kron(np.kron(psi, np.array([1,0], dtype=complex)), np.array([1,0], dtype=complex))
    # Create Bell pair q1-q2
    state = apply_single_qubit(state, H, target=1)
    state = apply_cnot(state, control=1, target=2)
    # Alice ops
    state = apply_cnot(state, control=0, target=1)
    state = apply_single_qubit(state, H, target=0)

    # Measure q0,q1 (Z basis)
    amps = state
    outcomes = [(0,0),(0,1),(1,0),(1,1)]
    probs = np.zeros(4)
    for i,(m0,m1) in enumerate(outcomes):
        p = 0.0
        for basis in range(8):
            b0 = (basis >> 2) & 1
            b1 = (basis >> 1) & 1
            if b0==m0 and b1==m1:
                p += np.abs(amps[basis])**2
        probs[i] = p
    probs = probs/np.sum(probs)
    idx = rng.choice(4, p=probs)
    m0, m1 = outcomes[idx]

    # collapse
    post = np.zeros_like(amps); norm=0.0
    for basis in range(8):
        b0 = (basis >> 2) & 1
        b1 = (basis >> 1) & 1
        if b0==m0 and b1==m1:
            post[basis] = amps[basis]
            norm += np.abs(amps[basis])**2
    post = post/np.sqrt(norm+1e-16)

    # Bob corrections on q2
    if m1==1: post = apply_single_qubit(post, X, target=2)
    if m0==1: post = apply_single_qubit(post, Z, target=2)

    rho = np.outer(post, np.conjugate(post))
    rho_bob = partial_trace_rho(rho, keep=2)
    fid = np.real(np.conjugate(psi) @ rho_bob @ psi)
    steps = {'probs_m0m1': {str(outcomes[i]): float(probs[i]) for i in range(4)},
             'm0': int(m0), 'm1': int(m1)}
    return m0, m1, float(fid), rho_bob, steps

def teleportation_batch(theta: float, phi: float, shots: int = 1000, rng=None):
    if rng is None:
        rng = np.random.default_rng()
    counts = {(0,0):0,(0,1):0,(1,0):0,(1,1):0}
    fids = []
    for _ in range(shots):
        m0, m1, fid, rho_bob, _ = teleportation_once(theta, phi, rng)
        counts[(m0,m1)] += 1
        fids.append(fid)
    return counts, float(np.mean(fids))

# ====================== Noise / Decoherence ======================
def apply_noise_channel(rho: np.ndarray, model: str, gamma: float) -> np.ndarray:
    gamma = float(np.clip(gamma, 0.0, 1.0))
    if model == "phase":
        E0 = np.array([[1,0],[0,np.sqrt(1-gamma)]], dtype=complex)
        E1 = np.array([[0,0],[0,np.sqrt(gamma)]], dtype=complex)
    elif model == "amplitude":
        E0 = np.array([[1,0],[0,np.sqrt(1-gamma)]], dtype=complex)
        E1 = np.array([[0,np.sqrt(gamma)],[0,0]], dtype=complex)
    else:
        raise ValueError("Unknown model: " + str(model))
    return E0 @ rho @ E0.conj().T + E1 @ rho @ E1.conj().T

def evolve_under_noise(theta: float, phi: float, gammas: np.ndarray, model: str):
    psi = single_qubit_state_from_bloch(theta, phi)
    rho0 = np.outer(psi, np.conjugate(psi))
    states, coherences, bloch = [], [], []
    for g in gammas:
        rho_g = apply_noise_channel(rho0, model, float(g))
        states.append(rho_g)
        coherences.append(np.abs(rho_g[0,1]))
        bloch.append(bloch_vector(rho_g))
    return states, np.array(coherences), np.array(bloch)
