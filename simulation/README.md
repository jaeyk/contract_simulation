# Procurement game simulations

Runnable implementations of [Model 1](../game_theory/README.md), [Models 2–7 and the combined Models 8–9](../game_theory/extensions.md), the agency's optimal contract-design problem, and a calibration to the contract documents in `../data`. The sweeps are deterministic equilibrium simulations with illustrative parameters. The calibration is a moment-matching exercise with explicit identified sets; nothing here establishes misconduct, causal effects, or actual vendor profits.

## Run

From the repository root:

```sh
cd simulation
uv sync --locked --cache-dir .cache/uv
.venv/bin/python -m unittest -v
.venv/bin/python run.py
.venv/bin/python calibrate.py
```

The project-local environment is `simulation/.venv`. Python 3.11 or newer is required. `pyproject.toml` declares Matplotlib for figures; `uv.lock` pins dependencies. The equilibrium solvers and tests use only Python's standard library. No input data or random seed is required.

Each execution creates a new timestamped directory under `outputs/` containing:

- `REPORT.md`: result ranges and links to figures and data.
- `model_1.csv` through `model_9.csv`: one row per parameter combination, including all input parameters and outcomes.
- `design.json`: optimal contract-design solutions (full runs only), summarized in `REPORT.md`.
- `model_1.png` / `model_1.svg`, etc.: three-panel figures for each model.
- `manifest.json`: fully resolved parameters, sweep values, row counts, Python/Matplotlib versions, and hashes of the solvers, runner, and dependency lockfile.

Earlier runs are preserved. Output directories are not ignored by Git so selected results can be versioned deliberately. Environment and cache directories are ignored.

An interactive in-conversation explorer can be generated from a completed full run:

```sh
.venv/bin/python build_visualization.py outputs/run_20261015T023107_949042Z
```

The explorer requires a run with all nine models. This writes `procurement-simulations.html` into that run directory using `visualization-template.html`. It embeds the saved CSV results without re-solving the models. Select a model, toggle scenario series, and inspect values along each chart. Hover values explicitly interpolate between sampled points; they are not newly solved equilibria, particularly at discrete regime boundaries. The fragment uses the conversation's theme and a pinned D3 CDN script; the existing PNG/SVG figures remain standalone exports.

Run a single model or use an alternative configuration/output parent:

```sh
.venv/bin/python run.py --model 6
.venv/bin/python run.py --config config.json --output outputs/experiment_a
```

## Configure experiments

Edit `config.json`. For each model, `parameters` overrides defaults in `models.py`; `sweep` defines one or two parameter lists. The runner takes their Cartesian product. The first sweep parameter is the horizontal plot axis; the second defines series. All configurations are checked before output is written. Unknown parameters and values outside the supported model domains raise errors.

For example, the default Model 6 experiment varies review cost `h` and high-effort cost `c`, holding error probabilities, harm, and penalties fixed. To vary penalties instead, replace the second sweep dimension with `"f": [0, 20, 40]`. Every value must remain below `L`.

The default run includes 241 parameter combinations:

| Model | Sweep | Main outcomes |
| --- | --- | --- |
| 1 | Monitoring `m` × portability `p` | Effort, dependence, bids, amendment price, lifecycle payments, profit |
| 2 | Warranty enforcement `w` × repair margin `mu` | Prevention, defects, repair revenue, social cost |
| 3 | Action payment `t` × outcome bonus `R` | Work intensity, success, burden, welfare gap |
| 4 | Flag reward `t` × enforcement `m` | Threshold, false flags, missed errors, welfare gap |
| 5 | Number of agencies `N` × testing cost `c` | Omitted/duplicated testing, expected tests, coordination benchmark, local-validation omission |
| 6 | Review cost `h` × effort cost `c` | Effort, review response, raw/final errors, public labor, social cost |
| 7 | Remedy credibility `rho` × harm `H` | Audit feasibility, agency audit policy, substitution, social cost |
| 8 | Portability `p` × warranty enforcement `w` | Prevention, dependence, repair margin, bids, social cost |
| 9 | Action payment `t` × uncorrected-error penalty `f` | Work, agency review and its cost, raw/final errors, social cost |

## Numerical method and equilibrium selection

Continuous concave problems use analytic boundary checks followed by 90 bisection iterations on the first-order condition. Prevention effort uses an adaptively bracketed root. Discrete games use backward induction or the closed-form mixed equilibrium. Figures connect sampled equilibria; they do not locate every threshold between grid points or imply smooth behavior at regime changes.

1. **Baseline:** Uses the portability-interaction specification, `S=s0+alpha*k/(1+p)`, and requires `cR+s0 >= cI`. This excludes cases where the vendor could invest to move from replacement into continuation. Initial bids are unrestricted: negative bids are reported and flagged, not silently floored. Fixed overhead is omitted. This is the only model with initial competitive bidding and total expected vendor profit. `agency_value` follows the baseline where the agency does not receive penalties; a separate net-payment column shows the alternative accounting if it does. The social-welfare column assumes penalties are transfers, while burden is fully weighted.
2. **Remediation:** A defect is always repaired; paid repair price is `r+mu`. Total defect social cost `H` already includes repair and harm, so do not add repair cost to it again. Fixed award payments are omitted. Penalties are transfers.
3. **Workflows:** Work is continuous, discretionary, and bounded by `cap`. Success follows `1-exp(-a*n)`. `t=R=0` represents fixed payment without marginal incentives. The output compares vendor work to the public optimum on the same interval. Mandatory checks are outside this choice.
4. **Flags:** Adds an explicit illustrative population assumption: calibrated scores are uniformly distributed on `[0,1]`, and the probability of true error conditional on score `z` is `z`. Thus error prevalence is 0.5. Integrated outcome masses are exact, not Monte Carlo estimates. `false_positive_mass` is erroneous flags per population case; `false_positive_rate` divides this by the non-error population share. When enforcement is zero and reward equals cost, the selected policy is no flags. Endpoint ties otherwise have zero population mass.
5. **Validation:** Selects the symmetric mixed equilibrium when `c<B`, and no testing when `c>=B`. At `c=B`, additional weak equilibria exist and the row is marked. The existence of a one-tester pure equilibrium is also reported. `coordinated_welfare=max(0,N*B-c)` is a planner benchmark, not a prediction that the symmetric equilibrium is inevitable. Local validation: each agency tests locally iff `omega*Lloc >= ell` (no spillovers); `local_welfare_loss=N*(Lloc-ell)` when a socially worthwhile test is omitted, and `total_welfare_loss` adds it to the shared-test loss.
6. **Review:** The agency receives penalties and skips review at exact indifference. The vendor selects low effort at exact indifference. The public benchmark compares all four effort/review combinations. Review is perfectly effective, and quality is observable to the agency at the review stage. `agency_review_cost` is a labor-resource cost, not a number of hours without calibration.
7. **Substitution:** The vendor retains quality at indifference; the agency tolerates substitution at policy indifference. `minimum_audit` is blank in CSV when available sanctions are zero, and may exceed one when deterrence is infeasible. Only feasible thresholds can become the selected audit probability. The agency does not retain sanctions. Its policy is compared to the best socially valued **feasible audit policy**, not to direct control of the vendor's technology. Real cost savings are subtracted from social harm, so negative social cost is possible and meaningful. Audit/termination resource costs beyond the stated audit cost are omitted.

8. **Lock-in and remediation:** The vendor's best response in dependence is exact given effort; effort maximizes the resulting profile by a 2,001-point global grid followed by bisection on the envelope-theorem slope (the profile need not be concave). Requires `cR+s0 >= cI` and `rR+s0 >= r`. Initial bids are unrestricted and zero-profit, as in Model 1. `H` includes repair cost and harm.
9. **Metered work and review:** The agency reviews at indifference (unlike Model 6), which makes the vendor's piecewise problem attained; vendor ties favor the reviewed region and planner ties favor no review. Review cost is `h + kappa*raw_error`. Penalties apply only to uncorrected errors and are transfers.

Models 2–6 report continuation profit or welfare excluding unspecified initial fixed payments where applicable. Model 5 has no strategic vendor payoff. Model 7 reports incremental vendor savings under the selected policy, not total revenue. Do not compare these quantities directly to Model 1's lifecycle profit.

## Optimal contract design

`design.py` solves the agency's commitment stage: `optimize(model, instruments, objective, fixed, costs)` searches instrument bounds on a 21-point grid per dimension with five zoom rounds, subtracting quadratic governance costs. The default problems in `PROBLEMS` run with every full `run.py` execution. Objectives other than Model 1's agency value are social cost or welfare, which equal the agency's objective under competitive zero-profit bidding with transfers netted. Grid search handles regime changes but reports one optimum when an interval is optimal; it is not a proof of global optimality for arbitrary new problems.

## Calibration to the contract documents

Inputs live in `calibration/`:

| File | Content |
| --- | --- |
| `contracts.csv` | Contract families: state, agency, vendor, system, and the `data/` file prefixes belonging to each |
| `amendments.csv` | Hand-verified base values and every observed modification, with kind (`scope`, `extension`, `bridge`, `option`, `admin`), trigger, amounts, and a source quote |
| `prices.csv` | Unit, hourly and fixed prices with quotes |
| `sla_caps.csv` | Service-level credit caps as a share of fees |
| `negotiated_terms.csv` | Accepted vendor deviations (Arizona memorandum of negotiations) |
| `extract_terms.py` → `contract_terms.csv` | Regular-expression clause codes with the first matching snippet for audit; needs Poppler's `pdftotext` and caches text in `.cache/` |
| `term_overrides.csv` | Manual corrections to automated codes, with reasons |
| `coding_rules.json` | Mapping from codes to parameters (`m`, `p`, `F`, `w`), base normalization, θ grid |

`calibrate.py` writes `outputs/calibration_<timestamp>/` with `CALIBRATION.md`, `calibration.json` (moments, mapped parameters, input hashes), and `calibrated_scenarios.csv`. It does not need `pdftotext`; rerun `extract_terms.py` only when documents or rules change.

What is identified: the frequency of priced unplanned work (λ̂, share of families with any observed modification that had one) and each family's amendment growth ratio. Money is normalized so the base contract equals 10 units; the observed growth then fixes the amendment price, and for each θ the incumbent cost is the residual. A θ is inconsistent when assumed switching costs alone exceed the observed amendment. What is not identified: the split of amendments into cost and margin, and all value, burden, and governance parameters, which keep illustrative defaults. Coded parameters follow transparent rules, not estimates. The document sample is a FOIA/EPIC corpus, not a random sample.

These implementations solve the stated continuation games and design problems over stated instruments. They do not estimate costs structurally, model partial review, vary score distributions, or simulate realized sample paths. Monetary and effort scales are illustrative and need empirical calibration before substantive magnitude comparisons across models.

## Verification and implementation record

`test_models.py` checks accounting identities, comparative statics, zero and capped choices, direct objective comparisons, mixed-strategy indifference, probability accounting, exhaustive review benchmarks, infeasible deterrence, beneficial substitution, local validation, brute-force joint optima for Models 8 and 9, analytic design benchmarks, and invalid inputs. `test_calibration.py` checks that every coded record references a known family and document, that amendment chains reconcile with stated totals (Illinois "Revised Total", MiDAS change notice 32), that overrides apply, and that calibrated scenarios reproduce the observed amendment and base.

The initial environment setup used `uv --version` and `uv sync --cache-dir .cache/uv`. The first sync hit a sandbox-related macOS system-configuration crash; the same sync completed with approved elevated execution. Subsequent runs use `.venv/bin/python` and need no network. Use the locked sync command above to reproduce dependency versions.
