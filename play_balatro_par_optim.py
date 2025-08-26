import math
from typing import List, Tuple, Dict

# ---------- helpers ----------
def sigmoid(z: float) -> float:
    return 1.0 / (1.0 + math.exp(-z))

def clamp_prob(p: float, eps: float = 1e-9) -> float:
    return min(max(p, eps), 1.0 - eps)

def logit(p: float) -> float:
    p = clamp_prob(p)
    return math.log(p / (1.0 - p))
# ---------- NLL + gradients ----------
def nll_and_grads(
    x_seqs: List[List[int]],
    y_seqs: List[List[float]],
    th: Dict[str, float],           # logits: th_q0, th_p00, th_p11, th_e0, th_e1
    learn_q0: bool = True
) -> Tuple[float, Dict[str, float]]:
    """
    Joint negative log-likelihood:
      - transitions: q0, p00, p11
      - emissions:   z0=P(r=1|action=0), z1=P(r=1|action=1) with r=1(y>0)
    """
    q0  = clamp_prob(sigmoid(th["th_q0"]))
    p00 = clamp_prob(sigmoid(th["th_p00"]))
    p11 = clamp_prob(sigmoid(th["th_p11"]))
    z0  = clamp_prob(sigmoid(th["th_e0"]))
    z1  = clamp_prob(sigmoid(th["th_e1"]))

    nll = 0.0
    g = {k: 0.0 for k in th.keys()}   # grads w.r.t. logits (thanks to logistic link)

    eps = 1e-12

    for x_seq, y_seq in zip(x_seqs, y_seqs):
        if not x_seq:
            continue
        assert len(x_seq) == len(y_seq), "x_seq and y_seq must have same length"

        # ----- initial action term -----
        x1 = x_seq[0]
        target = 1.0 if x1 == 0 else 0.0  # P(X1=0) = q0
        nll -= (target*math.log(q0+eps) + (1-target)*math.log(1-q0+eps))
        if learn_q0:
            # d/d(logit) = (p - target)
            g["th_q0"] += (q0 - target)

        # ----- transitions -----
        for t in range(len(x_seq)-1):
            prev, curr = x_seq[t], x_seq[t+1]
            if prev == 0:
                # target=1 if curr==0 else 0 ; p = p00
                target = 1.0 if curr == 0 else 0.0
                p = p00
                nll -= (target*math.log(p+eps) + (1-target)*math.log(1-p+eps))
                g["th_p00"] += (p - target)
            else:
                # target=1 if curr==1 else 0 ; p = p11
                target = 1.0 if curr == 1 else 0.0
                p = p11
                nll -= (target*math.log(p+eps) + (1-target)*math.log(1-p+eps))
                g["th_p11"] += (p - target)

        # ----- emissions (binary: r_t = 1 if y_t>0) -----
        for a, y in zip(x_seq, y_seq):
            r = 1.0 if y > 0 else 0.0
            if a == 0:
                p = z0
                nll -= (r*math.log(p+eps) + (1-r)*math.log(1-p+eps))
                g["th_e0"] += (p - r)
            else:
                p = z1
                nll -= (r*math.log(p+eps) + (1-r)*math.log(1-p+eps))
                g["th_e1"] += (p - r)

    return nll, g

# ---------- simple GD optimizer ----------
def fit_markov_with_emission(
    x_seqs: List[List[int]],
    y_seqs: List[List[float]],
    lr: float = 0.2,
    steps: int = 200,
    learn_q0: bool = True,
    seed: int = 0,
    init_params: Dict[str, float] = None,  # {"q0","p00","p11","z0","z1"} optional
    ):

    random = __import__("random")
    random.seed(seed)

    # init logits: from init_params if provided, else 0 (prob ~ 0.5)
    if init_params:
        th = {
            "th_q0":  logit(init_params.get("q0",  0.5)),
            "th_p00": logit(init_params.get("p00", 0.5)),
            "th_p11": logit(init_params.get("p11", 0.5)),
            "th_e0":  logit(init_params.get("z0",  0.5)),
            "th_e1":  logit(init_params.get("z1",  0.5)),
        }
    else:
        th = {
            "th_q0":  0.0,
            "th_p00": 0.0,
            "th_p11": 0.0,
            "th_e0":  0.0,
            "th_e1":  0.0,
        }

    for step in range(steps):
        nll, g = nll_and_grads(x_seqs, y_seqs, th, learn_q0=learn_q0)
        for k in th:
            th[k] -= lr * g[k]
        if (step+1) % 50 == 0:
            print(f"step {step+1:3d}: NLL={nll:.4f}")

    # map logits -> probabilities
    q0  = clamp_prob(sigmoid(th["th_q0"]))
    p00 = clamp_prob(sigmoid(th["th_p00"]))
    p11 = clamp_prob(sigmoid(th["th_p11"]))
    z0  = clamp_prob(sigmoid(th["th_e0"]))
    z1  = clamp_prob(sigmoid(th["th_e1"]))

    T = {
        "0": {"0": p00,        "1": 1.0 - p00},
        "1": {"0": 1.0 - p11,  "1": p11}
    }
    return {"q0": q0, "p00": p00, "p11": p11, "z0": z0, "z1": z1, "T": T}

def optimize_params(
    x_seq: List[int],
    y_seq: List[float],
    init_params: Dict[str, float] = None,
    lr: float = 0.3,
    steps: int = 150,
    learn_q0: bool = True,
    seed: int = 0
) -> Dict[str, float]:
    """
    Single-game optimizer: takes one x_seq and y_seq (same length), optional init_params,
    and returns {"q0","p00","p11","z0","z1","T"} where T is the transition matrix.
    """
    if not x_seq or not y_seq or len(x_seq) != len(y_seq):
        raise ValueError("optimize_params: x_seq and y_seq must be non-empty and of equal length")

    x_seqs = [list(map(int, x_seq))]
    y_seqs = [list(map(float, y_seq))]

    return fit_markov_with_emission(
        x_seqs, y_seqs,
        lr=lr, steps=steps, learn_q0=learn_q0, seed=seed,
        init_params=init_params
    )

'''
# ---------- demo with your mock single-game data ----------
x_seq = [1, 1, 0, 0, 0, 1, 1, 0]
y_seq = [0, 0, 48, 60, 16, 0, 0, 52]  # only used as (y>0) -> 1

# wrap as "list of games"
result = fit_markov_with_emission([x_seq], [y_seq], lr=0.3, steps=300, learn_q0=True)

print("\n==== Estimated parameters ====")
print(f"q0  = {result['q0']:.4f}")
print(f"p00 = {result['p00']:.4f}")
print(f"p11 = {result['p11']:.4f}")
print(f"z0  = {result['z0']:.4f}   # P(y>0 | action=0)")
print(f"z1  = {result['z1']:.4f}   # P(y>0 | action=1)")
print("Transition matrix:", result["T"])
print("Emission probs:", result["emissions"])
'''