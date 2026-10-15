"""Explanatory figures for the README, solved directly from models.py and calibrate.py.

Writes PNGs to docs/figures/. Illustrative parameters (model defaults unless noted).
"""
import csv
import os
from pathlib import Path

from models import solve

ROOT = Path(__file__).resolve().parent
OUT = ROOT.parent / "docs" / "figures"
os.environ.setdefault("MPLCONFIGDIR", str(ROOT / ".cache" / "matplotlib"))
import matplotlib  # noqa: E402
matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402

SURFACE, INK, INK2, MUTED, GRID = "#fcfcfb", "#0b0b0b", "#52514e", "#8a8984", "#e6e5e1"
SERIES = ["#2a78d6", "#eb6834", "#1baf7a", "#eda100"]  # validated categorical slots 1-4 (light)
plt.rcParams.update({
    "figure.facecolor": SURFACE, "axes.facecolor": SURFACE, "savefig.facecolor": SURFACE,
    "axes.edgecolor": MUTED, "axes.labelcolor": INK2, "xtick.color": INK2, "ytick.color": INK2,
    "text.color": INK, "font.size": 10.5, "axes.titlesize": 12, "axes.titleweight": "bold",
    "axes.titlelocation": "left", "axes.spines.top": False, "axes.spines.right": False,
    "axes.grid": True, "grid.color": GRID, "grid.linewidth": .8, "lines.linewidth": 2,
    "legend.frameon": False, "legend.fontsize": 9.5,
})


def grid(lo, hi, n=401):
    return [lo+(hi-lo)*i/(n-1) for i in range(n)]


def label_end(ax, xs, ys, text, color_index, dy=0, x=None):
    """Direct label in ink, next to the line's end (identity is carried by the swatch line)."""
    i = len(xs)-1 if x is None else min(range(len(xs)), key=lambda j: abs(xs[j]-x))
    ax.annotate(text, (xs[i], ys[i]), xytext=(6, dy), textcoords="offset points",
                va="center", fontsize=9.5, color=INK2)


def finish(fig, name, note):
    fig.text(0.01, -0.02, note, fontsize=8.5, color=MUTED, ha="left", va="top", wrap=True)
    fig.savefig(OUT / name, dpi=200, bbox_inches="tight", pad_inches=.15)
    plt.close(fig)


def fig_bid_offset():
    thetas = grid(0, 1, 201)
    rows = [solve(1, {"theta": t}) for t in thetas]
    initial = [r["initial_price"] for r in rows]
    amend = [.5*r["amendment_price"] for r in rows]
    life = [r["agency_gross_payment"] for r in rows]
    fig, ax = plt.subplots(figsize=(7.2, 4.2))
    for ys, text, i in [(life, "Lifecycle payments", 0), (amend, "Expected amendment payments", 1),
                        (initial, "Competitive initial bid", 2)]:
        ax.plot(thetas, ys, color=SERIES[i], label=text)
        label_end(ax, thetas, ys, text, i)
    ax.axhline(0, color=MUTED, lw=1)
    ax.set(xlim=(0, 1), xlabel="Vendor bargaining weight over amendments (θ)", ylabel="Cost units",
           title="1. Competition moves lock-in rents into a lower first bid")
    ax.legend(loc="lower left")
    ax.margins(x=0)
    fig.subplots_adjust(right=.72)
    finish(fig, "01_bid_offset.png", "Model 1, default parameters. Lifecycle rises only by the cost of building dependence; "
           "amendment margins are offset in the bid.")


def fig_remedy_binds():
    ms = grid(0, 1, 101)
    fig, ax = plt.subplots(figsize=(7.2, 4.2))
    for i, (F, text) in enumerate([(10, "Penalty F = 10"), (2, "Penalty F = 2 (20% cap)"), (0, "No enforceable penalty")]):
        ys = [solve(1, {"m": m, "F": F})["effort"] for m in ms]
        ax.plot(ms, ys, color=SERIES[i], label=text)
        label_end(ax, ms, ys, text, i)
    ax.set(xlim=(0, 1), xlabel="Monitoring: probability a failure is detected and enforced (m)",
           ylabel="Vendor quality effort", title="2. Monitoring is worthless without a consequence")
    ax.legend(loc="upper left")
    fig.subplots_adjust(right=.72)
    finish(fig, "02_remedy_binds.png", "Model 1. Effort solves c·e = m·F·exp(−e): with F = 0 it is zero at every m. "
           "Three of four calibrated contracts had no enforceable penalty.")


def fig_lockin():
    ps = grid(0, 5, 201)
    fig, axes = plt.subplots(1, 2, figsize=(10, 4.2))
    for i, w in enumerate([.75, .5, .25]):
        rows = [solve(8, {"p": p, "w": w}) for p in ps]
        for ax, key in zip(axes, ["effort", "welfare_loss"]):
            ys = [r[key] for r in rows]
            ax.plot(ps, ys, color=SERIES[i], label=f"Warranty enforcement w = {w}")
            label_end(ax, ps, ys, f"w = {w}", i)
    fig.suptitle("3. When repairs are paid, portability raises prevention and cuts waste", x=.06, ha="left",
                 fontsize=12, fontweight="bold", y=1.0)
    axes[0].set(xlabel="Portability requirements (p)", ylabel="Prevention effort")
    axes[1].set(xlabel="Portability requirements (p)", ylabel="Excess social cost")
    axes[0].legend(loc="center right", bbox_to_anchor=(1, .58))
    for ax in axes:
        ax.set_xlim(0, 5)
    fig.subplots_adjust(wspace=.35, right=.93)
    finish(fig, "03_lockin_remediation.png", "Model 8 (Models 1 + 2). Dependence raises the bargained margin on uncovered "
           "repairs, weakening prevention; portability breaks the loop.")


def fig_bunching():
    ts = grid(0, 8, 401)
    fig, ax = plt.subplots(figsize=(7.2, 4.2))
    cut = solve(9, {"f": 12})["review_cutoff_work"]
    ax.axhspan(0, cut, color=GRID, alpha=.6, lw=0)
    ax.text(.15, cut/2, "Agency reviews and corrects\n(vendor owes no penalty)", fontsize=9, color=INK2, va="center")
    for i, (f, text) in enumerate([(0, "No penalty"), (12, "Penalty on uncorrected errors, f = 12")]):
        ys = [solve(9, {"t": t, "f": f})["work"] for t in ts]
        ax.plot(ts, ys, color=SERIES[i], label=text)
        label_end(ax, ts, ys, f"f = {f}", i, dy=-8 if f == 0 else 8)
    ax.annotate("Vendor holds work at the\nreview cutoff to keep staff\ncorrecting its errors", (3.6, cut),
                xytext=(4.6, .35), fontsize=9, color=INK2, arrowprops=dict(arrowstyle="->", color=MUTED))
    ax.set(xlim=(0, 8), ylim=(0, 7.5), xlabel="Payment per discretionary action (t)",
           ylabel="Vendor work (actions)", title="4. A penalty only on errors that reach applicants can be gamed")
    ax.legend(loc="upper left")
    finish(fig, "04_review_bunching.png", "Model 9 (Models 3 + 6), review cutoff for f = 12 shaded. "
           "Remedies tied to raw errors avoid this.")


def fig_review_regimes():
    hs = grid(0.5, 60, 1200)
    rows = [solve(6, {"h": h}) for h in hs]
    fig, ax = plt.subplots(figsize=(7.2, 4.2))
    for lo, hi, text in [(0, 8, "Always\nreviews"), (8, 40, "Reviews only after\nlow effort"), (40, 60, "Never reviews")]:
        ax.axvspan(lo, hi, color=GRID if text.startswith("Reviews only") else SURFACE, alpha=.7, lw=0)
        ax.text((lo+hi)/2, 47, text, ha="center", fontsize=9, color=INK2)
    for i, (key, text) in enumerate([("social_cost", "Equilibrium"), ("public_social_cost", "Planner")]):
        ys = [r[key] for r in rows]
        ax.plot(hs, ys, color=SERIES[i], label=text, drawstyle="steps-post")
    ax.text(26, 33, "Equilibrium", fontsize=9.5, color=INK2, ha="right")
    ax.text(50, 12, "Planner", fontsize=9.5, color=INK2, ha="center")
    ax.set(xlim=(0, 60), ylim=(0, 52), xlabel="Agency cost of reviewing output (h)", ylabel="Total social cost",
           title="5. Because the agency will fix errors, the vendor stops preventing them")
    ax.legend(loc="lower right")
    finish(fig, "05_review_regimes.png", "Model 6. In the middle regime the agency reviews only after low effort, so "
           "the vendor chooses low effort; staff labor replaces prevention.")


def fig_flags():
    ts = grid(0, 15, 301)
    fig, ax = plt.subplots(figsize=(7.2, 4.2))
    public = solve(4)["public_threshold"]
    ax.axhline(public, color=INK2, lw=1.2, ls=(0, (4, 3)))
    ax.text(15, public+.03, "Public-value threshold", ha="right", fontsize=9, color=INK2)
    for i, (m, text) in enumerate([(1, "False flags always penalized"), (.5, "Penalized half the time"),
                                   (0, "Never penalized")]):
        ys = [solve(4, {"t": t, "m": m})["threshold"] for t in ts]
        ax.plot(ts, ys, color=SERIES[i], label=text)
        x, y = {1: (10.2, .22), .5: (6.5, .14), 0: (2.25, .55)}[m]
        ax.text(x, y, f"m = {m}", fontsize=9.5, color=INK2)
    ax.set(xlim=(0, 15), ylim=(-.03, 1.05), xlabel="Reward per flagged case (t)",
           ylabel="Vendor flags cases with error probability above",
           title="6. Paying per flag lowers the bar for flagging")
    ax.legend(loc="upper right")
    finish(fig, "06_flag_threshold.png", "Model 4. Below the dashed line the vendor over-flags. No coded contract "
           "states a false-positive standard.")


def fig_identified_sets():
    runs = sorted((ROOT / "outputs").glob("calibration_*/calibrated_scenarios.csv"))
    rows = list(csv.DictReader(runs[-1].open()))
    names = {"IL-IDES-DELOITTE-PUA": "Illinois PUA (Deloitte)", "MI-DTMB-FAST-MIDAS": "Michigan MiDAS (FAST)",
             "NV-DWSS-PONDERA": "Nevada SNAP (Pondera)", "IN-FSSA-FRAUDCASTER": "Indiana FraudCaster"}
    fig, ax = plt.subplots(figsize=(7.2, 4.2))
    for i, (fam, text) in enumerate(names.items()):
        pts = [(float(r["theta"]), 100*float(r["amendment_margin_share"])) for r in rows
               if r["family_id"] == fam and r["consistent"] == "True"]
        xs, ys = zip(*pts)
        ax.plot(xs, ys, color=SERIES[i], marker="o", markersize=6, markeredgecolor=SURFACE, label=text)
        label_end(ax, xs, ys, text, i)
    ax.set(xlim=(0, 1), ylim=(0, 100), xlabel="Vendor bargaining weight (θ)",
           ylabel="Share of amendment price that is margin (%)",
           title="7. The contracts bound, but cannot pin down, bargaining power")
    ax.legend(loc="center left", bbox_to_anchor=(1.0, .55))
    fig.subplots_adjust(right=.7)
    finish(fig, "07_identified_sets.png", "Calibration. Lines end where θ becomes inconsistent with the observed "
           "amendment. Large amendments are mostly cost at any θ.")


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    for f in [fig_bid_offset, fig_remedy_binds, fig_lockin, fig_bunching, fig_review_regimes, fig_flags,
              fig_identified_sets]:
        f()
    print(f"Wrote figures to {OUT}")


if __name__ == "__main__":
    main()
