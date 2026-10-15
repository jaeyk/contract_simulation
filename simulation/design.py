"""Optimal contract design: the agency chooses instruments before the continuation game.

Each problem fixes a model, the instruments the agency controls (with bounds), an
objective outcome, and optional quadratic governance costs g*x^2/2 per instrument.
The search is a deterministic grid with successive zooming, so it handles the
discrete regime changes in Models 6, 7 and 9 that defeat derivative-based methods.
"""
import itertools

from models import DEFAULTS, solve

# Objectives that are costs are minimized; all others are maximized.
COSTS = {"social_cost", "welfare_loss", "agency_net_cost_excluding_fixed", "agency_cost"}


def score(model, params, objective, costs):
    outcome = solve(model, params)
    governance = sum(g*params[k]**2/2 for k, g in costs.items())
    value = outcome[objective]+(governance if objective in COSTS else -governance)
    return value, outcome, governance


def optimize(model, instruments, objective, fixed=None, costs=None, grid=21, rounds=5):
    """Return the best instrument values within the bounds, with outcomes and governance cost."""
    model, fixed, costs = str(model), fixed or {}, costs or {}
    unknown = (set(instruments) | set(fixed) | set(costs)) - set(DEFAULTS[model])
    if unknown:
        raise ValueError(f"Model {model}: unknown parameters {sorted(unknown)}")
    if set(costs) - set(instruments):
        raise ValueError("Governance costs apply only to instruments")
    sign = 1 if objective in COSTS else -1
    bounds = {k: tuple(map(float, b)) for k, b in instruments.items()}
    best = None
    for _ in range(rounds):
        axes = [[lo+(hi-lo)*i/(grid-1) for i in range(grid)] for lo, hi in bounds.values()]
        for values in itertools.product(*axes):
            params = DEFAULTS[model] | fixed | dict(zip(bounds, values))
            try:
                value, outcome, governance = score(model, params, objective, costs)
            except ValueError:  # e.g. a penalty grid point at the model's f < L boundary
                continue
            # Ties keep the earliest grid point (lowest instrument values).
            if best is None or sign*value < sign*best[0]-1e-12:
                best = (value, dict(zip(bounds, values)), outcome, governance)
        if best is None:
            raise ValueError("No feasible design in the stated bounds")
        span = {k: (hi-lo)/(grid-1) for k, (lo, hi) in bounds.items()}
        lo0 = {k: float(b[0]) for k, b in instruments.items()}
        hi0 = {k: float(b[1]) for k, b in instruments.items()}
        bounds = {k: (max(lo0[k], best[1][k]-2*span[k]), min(hi0[k], best[1][k]+2*span[k]))
                  for k in bounds}
    value, choice, outcome, governance = best
    return dict(model=model, objective=objective, value=value, instruments=choice,
                governance_cost=governance, fixed=fixed, outcome=outcome)


# Default design problems. Under fully informed competitive bidding (zero expected
# vendor profit) the agency pays real costs plus expected penalties, so with
# transfers netted and burden fully weighted its objective equals social cost.
# Model 1 keeps the agency's own objective so the burden weight omega can matter.
PROBLEMS = [
    dict(name="1a", label="Model 1, agency chooses monitoring and portability (omega=0)", model="1",
         instruments={"m": [0, 1], "p": [0, 5]}, objective="agency_value", fixed={"omega": 0}),
    dict(name="1b", label="Model 1, agency chooses monitoring and portability (omega=1)", model="1",
         instruments={"m": [0, 1], "p": [0, 5]}, objective="agency_value", fixed={"omega": 1}),
    dict(name="1c", label="Model 1, agency chooses monitoring and portability (omega=3)", model="1",
         instruments={"m": [0, 1], "p": [0, 5]}, objective="agency_value", fixed={"omega": 3}),
    dict(name="1s", label="Model 1, social optimum over monitoring and portability", model="1",
         instruments={"m": [0, 1], "p": [0, 5]}, objective="social_welfare_if_penalty_transfer"),
    dict(name="2a", label="Model 2, warranty enforcement with enforcement cost", model="2",
         instruments={"w": [0, 1]}, objective="social_cost", costs={"w": 4}),
    dict(name="2b", label="Model 2, warranty enforcement and repair-price cap", model="2",
         instruments={"w": [0, 1], "mu": [0, 8]}, objective="social_cost", costs={"w": 4}),
    dict(name="3u", label="Model 3, usage price only", model="3",
         instruments={"t": [0, 10]}, objective="social_welfare", fixed={"R": 0}),
    dict(name="3o", label="Model 3, outcome bonus only", model="3",
         instruments={"R": [0, 40]}, objective="social_welfare", fixed={"t": 0}),
    dict(name="3m", label="Model 3, usage price and outcome bonus", model="3",
         instruments={"t": [0, 10], "R": [0, 40]}, objective="social_welfare"),
    dict(name="4a", label="Model 4, per-flag reward", model="4",
         instruments={"t": [0, 15]}, objective="social_welfare"),
    dict(name="4b", label="Model 4, per-flag reward and costly false-flag enforcement", model="4",
         instruments={"t": [0, 15], "m": [0, 1]}, objective="social_welfare", costs={"m": 4}),
    dict(name="6a", label="Model 6, penalty on uncorrected errors", model="6",
         instruments={"f": [0, 99.9]}, objective="social_cost"),
    dict(name="8a", label="Model 8, warranty enforcement and portability (costly)", model="8",
         instruments={"w": [0, 1], "p": [0, 5]}, objective="social_cost", costs={"w": 4, "p": .2}),
    dict(name="9a", label="Model 9, usage price and uncorrected-error penalty", model="9",
         instruments={"t": [0, 10], "f": [0, 19.9]}, objective="social_cost"),
    dict(name="9b", label="Model 9, add verified-correctness bonus", model="9",
         instruments={"t": [0, 10], "R": [0, 30], "f": [0, 19.9]}, objective="social_cost"),
]


def solve_problems(problems=PROBLEMS):
    results = []
    for spec in problems:
        r = optimize(spec["model"], spec["instruments"], spec["objective"],
                     spec.get("fixed"), spec.get("costs"))
        default = DEFAULTS[spec["model"]] | spec.get("fixed", {})
        base_value, _, _ = score(spec["model"], default, spec["objective"], spec.get("costs", {}))
        results.append(r | {"name": spec["name"], "label": spec["label"],
                            "default_instruments": {k: default[k] for k in spec["instruments"]},
                            "default_value": base_value})
    return results
