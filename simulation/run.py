"""Run reproducible, deterministic parameter sweeps for procurement games."""
import argparse
import csv
import hashlib
import itertools
import json
import os
from pathlib import Path
import platform

from design import solve_problems
from models import DEFAULTS, solve

ROOT = Path(__file__).resolve().parent
TITLES = {
    "1": "Dependence and amendment bargaining", "2": "Paid remediation",
    "3": "Metered workflows", "4": "Rewarded flags", "5": "Shared validation",
    "6": "Human review", "7": "Post-award substitution",
    "8": "Lock-in and paid remediation (Models 1+2)",
    "9": "Metered workflows and agency review (Models 3+6)",
}
PANELS = {
    "1": [("effort", "Quality effort"), ("dependence", "Proprietary dependence"),
          ("agency_gross_payment", "Gross lifecycle payments")],
    "2": [("effort", "Prevention effort"), ("defect_probability", "Defect probability"),
          ("welfare_loss", "Excess social cost")],
    "3": [("work", "Workflow intensity"), ("success", "Verified success probability"),
          ("welfare_loss", "Welfare loss")],
    "4": [("threshold", "Flagging threshold"), ("false_positive_mass", "False flags per case"),
          ("welfare_loss", "Welfare loss")],
    "5": [("no_test_probability", "Probability of no test"),
          ("expected_tests", "Expected number of tests"),
          ("total_welfare_loss", "Welfare loss (shared + local tests)")],
    "6": [("high_effort", "High effort (1=yes)"), ("agency_review_cost", "Agency review labor cost"),
          ("welfare_loss", "Excess social cost")],
    "7": [("selected_audit", "Selected audit probability"), ("substitutes", "Substitution (1=yes)"),
          ("policy_welfare_loss", "Loss vs best feasible audit policy")],
    "8": [("effort", "Prevention effort"), ("dependence", "Proprietary dependence"),
          ("welfare_loss", "Excess social cost")],
    "9": [("work", "Workflow intensity"), ("agency_review_cost", "Agency review cost"),
          ("welfare_loss", "Excess social cost")],
}


def expand(model, spec):
    if set(spec) - {"parameters", "sweep"}:
        raise ValueError(f"Model {model}: unrecognized configuration keys")
    parameters = DEFAULTS[model] | spec.get("parameters", {})
    solve(model, parameters)
    sweep = spec.get("sweep", {})
    if not 1 <= len(sweep) <= 2:
        raise ValueError("Each model requires one or two sweep dimensions")
    for key, values in sweep.items():
        if key not in parameters or not isinstance(values, list) or not values:
            raise ValueError(f"Invalid sweep: {key}")
        if len(set(values)) != len(values):
            raise ValueError(f"Duplicate sweep values: {key}")
    rows = []
    for values in itertools.product(*sweep.values()):
        p = parameters | dict(zip(sweep, values))
        rows.append(p | solve(model, p))
    return rows, {"parameters": parameters, "sweep": sweep}


def plot(model, rows, sweep, destination, plt):
    axes_names = list(sweep)
    x = axes_names[0]
    group = axes_names[1] if len(axes_names) == 2 else None
    fig, axes = plt.subplots(1, 3, figsize=(13, 4.4), layout="constrained")
    for ax, (metric, label) in zip(axes, PANELS[model]):
        for value in sorted(sweep[group]) if group else [None]:
            subset = sorted((r for r in rows if group is None or r[group] == value), key=lambda r: r[x])
            ax.plot([r[x] for r in subset], [r[metric] for r in subset],
                    marker="o", markersize=3, label=f"{group}={value}" if group else "Equilibrium",
                    drawstyle="steps-post" if (model, metric) == ("6", "high_effort") else "default")
        ax.set(xlabel=x, ylabel=label)
        ax.grid(alpha=.2)
        ax.spines[["top", "right"]].set_visible(False)
    axes[0].legend(fontsize=8)
    fig.suptitle(f"Model {model}: {TITLES[model]}\nIllustrative parameters; lines connect sampled equilibria", fontsize=12)
    fig.savefig(destination / f"model_{model}.png", dpi=180)
    fig.savefig(destination / f"model_{model}.svg")
    plt.close(fig)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", type=Path, default=ROOT / "config.json")
    parser.add_argument("--output", type=Path, default=ROOT / "outputs")
    parser.add_argument("--model", choices=list(DEFAULTS), help="Run only one model")
    args = parser.parse_args()
    config = json.loads(args.config.read_text())
    if set(config) - set(DEFAULTS) or not config:
        parser.error("Configuration requires model keys from 1 through 9")
    if args.model and args.model not in config:
        parser.error("Selected model is absent from configuration")
    selected = [args.model] if args.model else list(config)
    # Validate all configurations before writing any output.
    runs = {m: expand(m, config[m]) for m in selected}
    out = args.output.resolve()
    # Each execution has its own directory: preserve earlier runs and avoid stale files.
    out.mkdir(parents=True, exist_ok=True)
    from datetime import datetime, timezone
    run_dir = out / datetime.now(timezone.utc).strftime("run_%Y%m%dT%H%M%S_%fZ")
    run_dir.mkdir()
    os.environ.setdefault("MPLCONFIGDIR", str(ROOT / ".cache" / "matplotlib"))
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    manifest = {
        "python": platform.python_version(), "matplotlib": matplotlib.__version__,
        "method": "Deterministic equilibrium sweeps; no random draws or empirical calibration",
        "source_sha256": {name: hashlib.sha256((ROOT/name).read_bytes()).hexdigest()
                          for name in ["models.py", "design.py", "run.py", "uv.lock"]},
        "models": {},
    }
    report = ["# Simulation results", "", "Illustrative deterministic equilibria, not empirical estimates.",
              "", "Full resolved parameters and source hashes are in `manifest.json`.", ""]
    for m, (rows, resolved) in runs.items():
        with (run_dir / f"model_{m}.csv").open("w", newline="") as file:
            writer = csv.DictWriter(file, fieldnames=list(rows[0]))
            writer.writeheader()
            writer.writerows(rows)
        plot(m, rows, resolved["sweep"], run_dir, plt)
        manifest["models"][m] = resolved | {"rows": len(rows)}
        report += [f"## Model {m}: {TITLES[m]}", "", f"{len(rows)} parameter combinations. [Data](model_{m}.csv).", ""]
        for key, label in PANELS[m]:
            values = [float(r[key]) for r in rows]
            report.append(f"- {label}: {min(values):.4g} to {max(values):.4g}.")
        if m == "1":
            count = sum(r["negative_initial_bid"] for r in rows)
            report += [f"- {count} scenarios require negative initial bids; these use unrestricted-bid theory, not a bid floor."]
        report += ["", f"![Model {m}](model_{m}.png)", ""]
    if not args.model:
        designs = solve_problems()
        (run_dir / "design.json").write_text(json.dumps(designs, indent=2, allow_nan=False)+"\n")
        manifest["design_problems"] = len(designs)
        report += ["## Optimal contract design", "",
                   "The agency commits to instruments before the continuation game. Values are the stated objective "
                   "net of quadratic governance costs; full outcomes are in [design.json](design.json). Where an "
                   "interval of instrument values is optimal (discrete regimes), one optimum is reported.", "",
                   "| Problem | Objective | Optimal instruments | Optimal value | Value at default terms |",
                   "| --- | --- | --- | --- | --- |"]
        for d in designs:
            chosen = ", ".join(f"{k}={v:.3g}" for k, v in d["instruments"].items())
            report.append(f"| {d['label']} | {d['objective']} | {chosen} | {d['value']:.4g} | {d['default_value']:.4g} |")
        report.append("")
    (run_dir / "manifest.json").write_text(json.dumps(manifest, indent=2, allow_nan=False)+"\n")
    (run_dir / "REPORT.md").write_text("\n".join(report))
    print(f"Completed {sum(len(rows) for rows, _ in runs.values())} scenarios: {run_dir}")


if __name__ == "__main__":
    main()
