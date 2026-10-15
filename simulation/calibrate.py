"""Calibrate the procurement games to coded evidence from the contract documents.

Inputs (simulation/calibration/): hand-verified amendment histories, prices, SLA
caps and negotiated deviations, plus clause codes from extract_terms.py with
manual overrides. Outputs go to a new timestamped directory under outputs/.

Identification is deliberately limited. Amendment histories pin down how often
priced unplanned work occurs (lambda) and its share of lifecycle payments (s).
They do not separate incumbent cost from bargaining margin, so the vendor's
bargaining weight theta is reported as an identified set: every theta for which
a nonnegative incumbent cost reproduces the observed share.
"""
import argparse
import csv
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import statistics

from design import optimize
from models import DEFAULTS, solve

ROOT = Path(__file__).resolve().parent
CAL = ROOT / "calibration"
UNPLANNED = {"scope", "extension", "bridge"}


def read(name):
    with (CAL / name).open(newline="") as f:
        return list(csv.DictReader(f))


def number(x):
    return float(x) if x not in ("", None) else None


def amendment_moments(rows):
    """Per-family totals. Options are planned at award and excluded from unplanned work."""
    out = {}
    for r in rows:
        fam = out.setdefault(r["family_id"], dict(base=None, base_event="", unplanned=0., planned=0.,
                                                   events=0, priced_unplanned=0, by_kind={}, by_trigger={}))
        change = number(r["change"])
        if r["kind"] == "base":
            fam["base"], fam["base_event"] = number(r["value_after"]), r["event"]
            continue
        fam["events"] += 1
        if change is None:
            continue
        if r["kind"] in UNPLANNED:
            fam["unplanned"] += change
            fam["priced_unplanned"] += change > 0
            fam["by_trigger"][r["trigger"]] = fam["by_trigger"].get(r["trigger"], 0.)+change
        elif r["kind"] == "option":
            fam["planned"] += change
        fam["by_kind"][r["kind"]] = fam["by_kind"].get(r["kind"], 0.)+change
    for fam in out.values():
        if fam["base"]:
            fam["growth"] = fam["unplanned"]/fam["base"]
            fam["share"] = fam["unplanned"]/(fam["base"]+fam["unplanned"])
    return out


def coded_terms(terms, overrides):
    codes = {}
    for r in terms:
        codes.setdefault(r["family_id"], {})[r["indicator"]] = int(r["present"])
    for r in overrides:
        codes[r["family_id"]][r["indicator"]] = int(r["present"])
    return codes


def map_parameters(family, codes, negotiated, caps, rules):
    c = codes[family]
    cuts = lambda prefix: sum(r["family_id"] == family and r["parameter"].startswith(prefix)
                              and r["direction"] == "lower" for r in negotiated)
    pr = rules["portability_p"]
    p = sum(pr[k]*c[k] for k in ("data_ownership", "transition_assistance", "source_code_escrow"))
    p = max(pr["minimum"], p+pr["per_negotiated_reduction"]*cuts("p "))
    mr = rules["monitoring_m"]
    m = min(mr["maximum"], mr["base"]+mr["independent_testing"]*c["independent_testing"])
    fr = rules["penalty_F"]
    cap = next((float(r["cap_share"]) for r in caps if r["family_id"] == family), None)
    if cap is None:
        cap = fr["cap_share_if_uncapped_remedy"] if any(c[k] for k in fr["remedy_indicators"]) else 0.
    wr = rules["warranty_w"]
    w = wr["base"]+wr["defect_warranty"]*c["defect_warranty"]+wr["per_negotiated_reduction"]*cuts("w ")
    return dict(m=m, p=float(p), F=rules["base_units"]*cap, w=min(wr["maximum"], max(wr["minimum"], w)),
                penalty_cap_share=cap)


def calibrate_family(fam, mom, mapped, lam, rules):
    """Model 1 and Model 8 scenarios for one contract family across the theta grid.

    Money is normalized so the observed base contract equals `base_units` model units.
    The initial bid P0 = c0 + C(e) + K(k) + mF(1-q) - lambda*theta*Delta then pins the
    base-scope cost c0 (which does not affect choices), and the observed unplanned
    increase, conditional on additional work arriving, pins the amendment price
    A = cI + theta*(cR + S - cI). Hence cI = A - theta*(premium + S); a theta is
    inconsistent when the assumed switching costs alone exceed the observed amendment.
    """
    units, premium = rules["base_units"], rules["replacement_premium"]
    dollars = mom["base"]/units
    amendment = mom["growth"]*units
    rows = []
    for theta in rules["theta_grid"]:
        params = DEFAULTS["1"] | {"lam": lam, "theta": theta, "m": mapped["m"], "p": mapped["p"],
                                  "F": mapped["F"]}
        r = solve("1", params)  # choices do not depend on cI or c0
        ci = amendment-theta*(premium+r["switching_cost"])
        row = dict(family_id=fam, theta=theta, consistent=ci >= 0, observed_growth=mom["growth"],
                   dollars_per_model_unit=dollars, lam=lam, m=mapped["m"], p=mapped["p"], F=mapped["F"],
                   w=mapped["w"])
        if ci < 0:
            rows.append(row)
            continue
        params |= {"cI": ci, "cR": ci+premium}
        r = solve("1", params)
        base_scope = units-r["initial_price"]
        margin_share = 1-ci/r["amendment_price"]
        m8 = solve("8", DEFAULTS["8"] | {"lam": lam, "theta": theta, "p": mapped["p"], "w": mapped["w"],
                                         "cI": ci, "cR": ci+premium})
        row |= dict(incumbent_cost=ci, amendment_price=r["amendment_price"], base_scope_cost=base_scope,
                    base_scope_nonnegative=base_scope >= 0, amendment_margin_share=margin_share,
                    implied_margin_dollars=margin_share*mom["unplanned"],
                    effort=r["effort"], dependence=r["dependence"], burden=r["burden"],
                    implied_dependence_cost_dollars=params["ck"]*r["dependence"]**2/2*dollars,
                    m8_effort=m8["effort"], m8_dependence=m8["dependence"],
                    m8_defect_probability=m8["defect_probability"], m8_repair_margin=m8["repair_margin"],
                    m8_welfare_loss=m8["welfare_loss"], params=params)
        rows.append(row)
    return rows


def design_gap(fam, cal, max_F):
    """Model 1: the agency's optimal monitoring, portability and penalty exposure versus
    the coded terms, at theta=0.5 or the largest consistent theta below it. Penalty
    exposure is bounded by the highest SLA cap observed in the corpus."""
    rows = [r for r in cal if r["consistent"] and r["theta"] <= .5]
    if not rows:
        return None
    row = max(rows, key=lambda r: r["theta"])
    params = row["params"]
    current = solve(1, params)
    best = optimize(1, {"m": [0, 1], "p": [0, 5], "F": [0, max_F]}, "agency_value",
                    {k: v for k, v in params.items() if k not in ("m", "p", "F")})
    gain = best["value"]-current["agency_value"]
    return dict(family_id=fam, theta=row["theta"], coded_m=params["m"], coded_p=params["p"],
                coded_F=params["F"], optimal_F=best["instruments"]["F"],
                optimal_m=best["instruments"]["m"], optimal_p=best["instruments"]["p"],
                coded_effort=current["effort"], optimal_effort=best["outcome"]["effort"],
                coded_dependence=current["dependence"], optimal_dependence=best["outcome"]["dependence"],
                agency_value_gain_model_units=gain)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=ROOT / "outputs")
    args = parser.parse_args()
    rules = json.loads((CAL / "coding_rules.json").read_text())
    contracts = {r["family_id"]: r for r in read("contracts.csv")}
    amendments, prices, caps = read("amendments.csv"), read("prices.csv"), read("sla_caps.csv")
    negotiated = read("negotiated_terms.csv")
    codes = coded_terms(read("contract_terms.csv"), read("term_overrides.csv"))
    unknown = ({r["family_id"] for r in amendments+prices+caps+negotiated} | set(codes)) - set(contracts)
    if unknown:
        raise ValueError(f"Families missing from contracts.csv: {sorted(unknown)}")

    moments = amendment_moments(amendments)
    observed = {f for f, m in moments.items() if m["events"]}
    priced = {f for f in observed if moments[f]["priced_unplanned"]}
    lam = len(priced)/len(observed)
    histories = {f: m for f, m in moments.items() if m.get("share") is not None and m["unplanned"] > 0}
    mapped = {f: map_parameters(f, codes, negotiated, caps, rules) for f in codes}
    calibrated = []
    for fam, mom in histories.items():
        calibrated += calibrate_family(fam, mom, mapped[fam], lam, rules)
    max_F = rules["base_units"]*max(float(r["cap_share"]) for r in caps)
    gaps = [g for fam in histories
            if (g := design_gap(fam, [r for r in calibrated if r["family_id"] == fam], max_F))]

    state = [f for f, c in contracts.items() if c["role"] == "state_contract"]
    coop = [f for f, c in contracts.items() if c["role"] == "cooperative"]
    share_of = lambda fams, k: sum(codes[f][k] for f in fams)
    structure = dict(
        state_contracts=len(state),
        outcome_payment=share_of(state, "outcome_payment"),
        unit_pricing=share_of(state, "unit_pricing"),
        accuracy_standard=share_of(state, "accuracy_standard"),
        liquidated_damages=share_of(state, "liquidated_damages"),
        sla_fee_reduction=share_of(state, "sla_fee_reduction"),
        independent_testing=share_of(state, "independent_testing"),
        cooperative=len(coop), cooperative_local_testing=share_of(coop, "local_acceptance_testing"))
    # Structural restrictions implied by the coded payment terms for Models 3 and 4.
    restricted = dict(
        model_3_no_outcome_bonus=solve(3, {"R": 0}) | {"design_optimum": optimize(3, {"t": [0, 10], "R": [0, 40]}, "social_welfare")["value"]},
        model_4_no_false_flag_penalty=solve(4, {"f": 0}),
        model_5_local_validation=solve(5))

    stamp = datetime.now(timezone.utc).strftime("calibration_%Y%m%dT%H%M%S_%fZ")
    out = args.output.resolve() / stamp
    out.mkdir(parents=True)
    with (out / "calibrated_scenarios.csv").open("w", newline="") as f:
        fields = sorted({k for r in calibrated for k in r if k != "params"})
        writer = csv.DictWriter(f, fieldnames=fields)
        writer.writeheader()
        writer.writerows({k: v for k, v in r.items() if k != "params"} for r in calibrated)
    summary = dict(lambda_hat=lam, families_with_modifications=sorted(observed),
                   families_with_priced_unplanned_work=sorted(priced), moments=moments,
                   mapped_parameters=mapped, structure=structure, design_gaps=gaps,
                   restricted_scenarios=restricted, rules=rules, calibrated=calibrated,
                   input_sha256={p.name: hashlib.sha256(p.read_bytes()).hexdigest()
                                 for p in sorted(CAL.glob("*")) if p.suffix in (".csv", ".json")})
    (out / "calibration.json").write_text(json.dumps(summary, indent=2, allow_nan=False, default=str)+"\n")
    (out / "CALIBRATION.md").write_text(report(summary, contracts, codes, histories))
    print(f"Calibrated {len(histories)} contract families: {out}")


def money(x):
    return f"${x:,.0f}"


def report(s, contracts, codes, histories):
    L = ["# Calibration to the contract documents", "",
         "Moment-matched scenarios built from hand-verified contract records. They show what the models imply "
         "*if* these contracts are read through them; they are not estimates of vendor costs, profits, or intent.", "",
         "## 1. Amendment histories", "",
         "Unplanned work = scope changes, extensions, and bridge extensions with stated prices. Exercised options "
         "were priced at award and are excluded.", "",
         "| Family | Base | Base event | Unplanned increases | Planned options | Growth | Share of lifecycle | Unplanned by trigger |",
         "| --- | --- | --- | --- | --- | --- | --- | --- |"]
    for f, m in histories.items():
        trig = "; ".join(f"{k}: {money(v)}" for k, v in sorted(m["by_trigger"].items(), key=lambda x: -x[1]))
        L.append(f"| {f} | {money(m['base'])} | {m['base_event']} | {money(m['unplanned'])} | {money(m['planned'])} | "
                 f"{m['growth']:.3f} | {m['share']:.3f} | {trig} |")
    L += ["", f"**Frequency of priced unplanned work.** {len(s['families_with_priced_unplanned_work'])} of "
          f"{len(s['families_with_modifications'])} families with any observed post-award modification had priced "
          f"unplanned work, so λ̂ = {s['lambda_hat']:.3f}. FOIA productions and EPIC requests are not a random sample "
          "of contracts; this rate is descriptive of the corpus.", "",
          "Caveats: the MiDAS base is the contract value at change notice 3 (2017), not the 2011 award. Nevada's base "
          "is the value after Amendment 1. The Illinois PUA amendments followed pandemic claims volume (Amendment 4 cites "
          "a \"higher than anticipated number of claims\"), which the baseline treats as exogenous additional work.", "",
          "## 2. Coded contract terms and mapped parameters", "",
          "Clause indicators come from `calibration/extract_terms.py` (regular expressions with recorded snippets) "
          "and `term_overrides.csv` (manual corrections). Mapping rules are in `coding_rules.json`.", ""]
    keys = ["liquidated_damages", "sla_fee_reduction", "defect_warranty", "transition_assistance",
            "data_ownership", "source_code_escrow", "independent_testing", "unit_pricing", "outcome_payment",
            "accuracy_standard"]
    L += ["| Family | " + " | ".join(k.replace("_", " ") for k in keys) + " | m | p | F | w |",
          "| --- |" + " --- |"*(len(keys)+4)]
    for f in contracts:
        if contracts[f]["role"] != "state_contract":
            continue
        mp = s["mapped_parameters"][f]
        L.append(f"| {f} | " + " | ".join("✓" if codes[f][k] else "·" for k in keys) +
                 f" | {mp['m']:.2g} | {mp['p']:.2g} | {mp['F']:.2g} | {mp['w']:.2g} |")
    st = s["structure"]
    L += ["", f"Across {st['state_contracts']} state contract families: {st['outcome_payment']} pay for verified "
          f"outcomes, {st['accuracy_standard']} state an accuracy or false-positive standard, {st['unit_pricing']} "
          f"contain unit (per-profile, per-transaction or per-seat) pricing, {st['liquidated_damages']} contain performance "
          f"liquidated damages, and {st['sla_fee_reduction']} contain service-level fee reductions. "
          f"{st['cooperative_local_testing']} of {st['cooperative']} cooperative purchasing families contain local acceptance-testing language.", "",
          "Arizona's memorandum of negotiations records four accepted vendor deviations that each move a model parameter "
          "against the agency: source code excluded from deliverables, no state access to the escrow package (portability), "
          "defect classification changed from state determination to mutual determination (warranty enforcement), and the "
          "SLA at-risk cap reduced from 13% to 10% of the monthly charge (penalty exposure).", "",
          "## 3. Calibrated Models 1 and 8", "",
          f"Money is normalized so the observed base contract equals {s['rules']['base_units']} model units; penalty exposure "
          "F is the SLA cap times that base. The initial bid then determines the base-scope cost (which does not affect "
          "choices), and the observed unplanned increase, conditional on additional work arriving, determines the amendment "
          "price A. For each θ the incumbent cost is cI = A − θ(cR − cI + S). A θ is *inconsistent* when the assumed switching "
          "cost and replacement premium alone would exceed the observed amendment. Model 8 uses the same λ̂, θ, cI, portability "
          "and coded warranty enforcement w.", "",
          "| Family | θ | Consistent | cI | Margin share of amendment price | Implied margin in observed amendments | M1 effort | M1 dependence | M8 effort | M8 defect prob. | M8 excess social cost |",
          "| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |"]
    for r in s["calibrated"]:
        if not r["consistent"]:
            L.append(f"| {r['family_id']} | {r['theta']} | no | | | | | | | | |")
            continue
        L.append(f"| {r['family_id']} | {r['theta']} | yes | {r['incumbent_cost']:.3g} | {r['amendment_margin_share']:.1%} | "
                 f"{money(r['implied_margin_dollars'])} | {r['effort']:.3g} | {r['dependence']:.3g} | {r['m8_effort']:.3g} | "
                 f"{r['m8_defect_probability']:.3g} | {r['m8_welfare_loss']:.3g} |")
    L += ["", "Within a family, effort and dependence do not depend on the amendment data except through λ̂: the dollar "
          "records discipline the *accounting* (how much of observed amendment spending the model can attribute to "
          "bargaining margin), while the coded terms drive behavior. The margin share rises with θ by construction. "
          "The contracts cannot choose among consistent values; cost data, invoices, or competing bids for comparable "
          "work would be needed.", "",
          "## 4. Contract-design gap at the calibrated terms (Model 1)", "",
          "The agency re-optimizes monitoring m, portability p and penalty exposure F at θ = 0.5 (or the largest consistent "
          "θ below it). F is bounded by the highest SLA cap in the corpus (20% of the base contract).", "",
          "| Family | θ | Coded (m, p, F) | Optimal (m, p, F) | Effort (coded → optimal) | Dependence (coded → optimal) | Agency value gain (model units) |",
          "| --- | --- | --- | --- | --- | --- | --- |"]
    for g in s["design_gaps"]:
        L.append(f"| {g['family_id']} | {g['theta']} | ({g['coded_m']:.2g}, {g['coded_p']:.2g}, {g['coded_F']:.2g}) | "
                 f"({g['optimal_m']:.2g}, {g['optimal_p']:.2g}, {g['optimal_F']:.2g}) | "
                 f"{g['coded_effort']:.3g} → {g['optimal_effort']:.3g} | {g['coded_dependence']:.3g} → {g['optimal_dependence']:.3g} | "
                 f"{g['agency_value_gain_model_units']:.3g} |")
    rs = s["restricted_scenarios"]
    L += ["", "Two patterns follow from the model rather than the data. Monitoring has no value without an enforceable "
          "consequence (F = 0 makes effort zero at any m), so the binding term in most coded contracts is the remedy, not "
          "detection. And under fully competitive bidding amendment margins are offset in the initial bid, so portability "
          "pays only by reducing wasteful dependence investment; its optimal level depends on the illustrative portability "
          "cost and should not be read as evidence that coded portability is excessive. Gains are in model units because the "
          "value, burden and governance parameters are not calibrated.", "",
          "## 5. Structural restrictions for Models 3–5", "",
          f"- **Model 3.** No coded contract pays for verified outcomes, so R = 0. At default costs the usage-only contract "
          f"at the default usage price gives welfare {rs['model_3_no_outcome_bonus']['social_welfare']:.3g} versus "
          f"{rs['model_3_no_outcome_bonus']['design_optimum']:.3g} at the welfare-maximizing terms. A usage price alone can reach "
          "that optimum here only because costs and burdens are known; the design gap widens when they are not.",
          f"- **Model 4.** No coded contract states a false-positive standard, so the expected false-flag penalty is zero. "
          f"With a per-flag reward above cost the vendor's threshold is {rs['model_4_no_false_flag_penalty']['threshold']:.2g} "
          f"(flag everything), against a public threshold of {rs['model_4_no_false_flag_penalty']['public_threshold']:.3g}.",
          f"- **Model 5.** The NASPO cloud participating addenda contain no local acceptance-testing language, whereas the MMIS "
          "participating addendum does. With partial internalization (ω = 0.5) the default local-validation scenario omits a "
          f"socially valuable local test, costing {rs['model_5_local_validation']['local_welfare_loss']:.3g} across agencies.", "",
          "## Inputs", "", "SHA-256 hashes of every calibration input are in `calibration.json`.", ""]
    return "\n".join(L)


if __name__ == "__main__":
    main()
