# Calibration to the contract documents

Moment-matched scenarios built from hand-verified contract records. They show what the models imply *if* these contracts are read through them; they are not estimates of vendor costs, profits, or intent.

## 1. Amendment histories

Unplanned work = scope changes, extensions, and bridge extensions with stated prices. Exercised options were priced at award and are excluded.

| Family | Base | Base event | Unplanned increases | Planned options | Growth | Share of lifecycle | Unplanned by trigger |
| --- | --- | --- | --- | --- | --- | --- | --- |
| IL-IDES-DELOITTE-PUA | $9,490,000 | award | $24,344,194 | $0 | 2.565 | 0.720 | unspecified: $17,967,194; demand: $6,377,000 |
| MI-DTMB-FAST-MIDAS | $47,026,150 | CN3-value | $32,613,466 | $9,310,170 | 0.694 | 0.410 | continuity: $26,729,168; policy: $4,552,298; unspecified: $1,332,000 |
| NV-DWSS-PONDERA | $1,497,261 | A1-value | $389,280 | $0 | 0.260 | 0.206 | unspecified: $389,280 |
| IN-FSSA-FRAUDCASTER | $744,000 | award | $43,000 | $0 | 0.058 | 0.055 | migration: $43,000 |

**Frequency of priced unplanned work.** 5 of 12 families with any observed post-award modification had priced unplanned work, so λ̂ = 0.417. FOIA productions and EPIC requests are not a random sample of contracts; this rate is descriptive of the corpus.

Caveats: the MiDAS base is the contract value at change notice 3 (2017), not the 2011 award. Nevada's base is the value after Amendment 1. The Illinois PUA amendments followed pandemic claims volume (Amendment 4 cites a "higher than anticipated number of claims"), which the baseline treats as exogenous additional work.

## 2. Coded contract terms and mapped parameters

Clause indicators come from `calibration/extract_terms.py` (regular expressions with recorded snippets) and `term_overrides.csv` (manual corrections). Mapping rules are in `coding_rules.json`.

| Family | liquidated damages | sla fee reduction | defect warranty | transition assistance | data ownership | source code escrow | independent testing | unit pricing | outcome payment | accuracy standard | m | p | F | w |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| IL-IDES-DELOITTE-PUA | · | · | ✓ | ✓ | ✓ | · | · | · | · | · | 0.5 | 2 | 0 | 0.5 |
| MI-DTMB-FAST-MIDAS | · | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | · | · | 1 | 3 | 0.5 | 0.5 |
| NV-DWSS-PONDERA | · | · | · | · | · | · | · | ✓ | · | · | 0.5 | 0 | 0 | 0.1 |
| IN-FSSA-FRAUDCASTER | · | · | · | · | ✓ | · | · | ✓ | · | · | 0.5 | 1 | 0 | 0.1 |
| IN-DWD-PONDERA | · | · | ✓ | · | ✓ | · | · | ✓ | · | · | 0.5 | 1 | 0 | 0.5 |
| IL-IDES-PONDERA | · | · | · | · | · | · | · | · | · | · | 0.5 | 0 | 0 | 0.1 |
| DC-DHS-PONDERA | · | · | · | ✓ | · | ✓ | · | ✓ | · | · | 0.5 | 2 | 0 | 0.1 |
| WI-DOC-NORTHPOINTE | · | · | ✓ | · | · | · | · | · | · | · | 0.5 | 0 | 0 | 0.5 |
| NE-DCS-VANT4GE | · | · | · | · | · | · | · | · | · | · | 0.5 | 0 | 0 | 0.1 |
| MI-DTMB-DELOITTE-UI | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | · | ✓ | · | · | 0.5 | 3 | 2 | 0.5 |
| VA-VITA-DELOITTE | · | · | ✓ | ✓ | · | · | · | ✓ | · | · | 0.5 | 1 | 0 | 0.5 |
| AZ-DES-GEOSOL-UI | · | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | · | · | · | 1 | 1 | 1 | 0.3 |
| AZ-AHCCCS-ACCENTURE-HEAPLUS | · | · | · | ✓ | ✓ | · | · | · | · | · | 0.5 | 2 | 0 | 0.1 |
| OH-DAS-DELOITTE-SACWIS | · | · | · | · | · | · | · | · | · | · | 0.5 | 0 | 0 | 0.1 |
| IA-IDPH-PONDERA | · | · | · | · | ✓ | · | · | · | · | · | 0.5 | 1 | 0 | 0.1 |
| ND-DOH-PROUDCROWD | · | · | · | · | · | · | · | · | · | · | 0.5 | 0 | 0 | 0.1 |
| TX-TWC-ONPOINT | · | · | · | · | · | · | · | · | · | · | 0.5 | 0 | 0 | 0.1 |
| KS-DOA-PONDERA | · | · | · | ✓ | · | · | · | · | · | · | 0.5 | 1 | 0 | 0.1 |
| DC-DCHA-RENTGROW | · | · | · | · | · | · | · | · | · | · | 0.5 | 0 | 0 | 0.1 |

Across 19 state contract families: 0 pay for verified outcomes, 0 state an accuracy or false-positive standard, 7 contain unit (per-profile, per-transaction or per-seat) pricing, 1 contain performance liquidated damages, and 3 contain service-level fee reductions. 2 of 7 cooperative purchasing families contain local acceptance-testing language.

Arizona's memorandum of negotiations records four accepted vendor deviations that each move a model parameter against the agency: source code excluded from deliverables, no state access to the escrow package (portability), defect classification changed from state determination to mutual determination (warranty enforcement), and the SLA at-risk cap reduced from 13% to 10% of the monthly charge (penalty exposure).

## 3. Calibrated Models 1 and 8

Money is normalized so the observed base contract equals 10 model units; penalty exposure F is the SLA cap times that base. The initial bid then determines the base-scope cost (which does not affect choices), and the observed unplanned increase, conditional on additional work arriving, determines the amendment price A. For each θ the incumbent cost is cI = A − θ(cR − cI + S). A θ is *inconsistent* when the assumed switching cost and replacement premium alone would exceed the observed amendment. Model 8 uses the same λ̂, θ, cI, portability and coded warranty enforcement w.

| Family | θ | Consistent | cI | Margin share of amendment price | Implied margin in observed amendments | M1 effort | M1 dependence | M8 effort | M8 defect prob. | M8 excess social cost |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| IL-IDES-DELOITTE-PUA | 0.1 | yes | 25.5 | 0.8% | $191,557 | 0 | 0.0278 | 0.938 | 0.391 | 1.08 |
| IL-IDES-DELOITTE-PUA | 0.25 | yes | 25.1 | 2.0% | $485,484 | 0 | 0.0694 | 0.906 | 0.404 | 1.19 |
| IL-IDES-DELOITTE-PUA | 0.5 | yes | 24.6 | 4.1% | $992,935 | 0 | 0.139 | 0.844 | 0.43 | 1.41 |
| IL-IDES-DELOITTE-PUA | 0.75 | yes | 24 | 6.3% | $1,522,354 | 0 | 0.208 | 0.772 | 0.462 | 1.7 |
| IL-IDES-DELOITTE-PUA | 0.9 | yes | 23.7 | 7.6% | $1,850,550 | 0 | 0.25 | 0.721 | 0.486 | 1.93 |
| MI-DTMB-FAST-MIDAS | 0.1 | yes | 6.73 | 2.9% | $945,422 | 0.352 | 0.0208 | 0.939 | 0.391 | 1.08 |
| MI-DTMB-FAST-MIDAS | 0.25 | yes | 6.43 | 7.3% | $2,381,923 | 0.352 | 0.0521 | 0.907 | 0.404 | 1.18 |
| MI-DTMB-FAST-MIDAS | 0.5 | yes | 5.91 | 14.8% | $4,825,079 | 0.352 | 0.104 | 0.848 | 0.428 | 1.39 |
| MI-DTMB-FAST-MIDAS | 0.75 | yes | 5.38 | 22.5% | $7,329,466 | 0.352 | 0.156 | 0.781 | 0.458 | 1.65 |
| MI-DTMB-FAST-MIDAS | 0.9 | yes | 5.05 | 27.2% | $8,861,490 | 0.352 | 0.188 | 0.735 | 0.479 | 1.84 |
| NV-DWSS-PONDERA | 0.1 | yes | 2.38 | 8.3% | $32,441 | 0 | 0.0833 | 0.223 | 0.8 | 4.78 |
| NV-DWSS-PONDERA | 0.25 | yes | 2 | 23.2% | $90,460 | 0 | 0.208 | 0 | 1 | 6.95 |
| NV-DWSS-PONDERA | 0.5 | yes | 1.18 | 54.5% | $212,112 | 0 | 0.417 | 0 | 1 | 7.6 |
| NV-DWSS-PONDERA | 0.75 | yes | 0.162 | 93.8% | $364,957 | 0 | 0.625 | 0 | 1 | 8.68 |
| NV-DWSS-PONDERA | 0.9 | no | | | | | | | | |
| IN-FSSA-FRAUDCASTER | 0.1 | yes | 0.374 | 35.3% | $15,190 | 0 | 0.0417 | 0.243 | 0.784 | 4.61 |
| IN-FSSA-FRAUDCASTER | 0.25 | yes | 0.0519 | 91.0% | $39,138 | 0 | 0.104 | 0 | 1 | 6.79 |
| IN-FSSA-FRAUDCASTER | 0.5 | no | | | | | | | | |
| IN-FSSA-FRAUDCASTER | 0.75 | no | | | | | | | | |
| IN-FSSA-FRAUDCASTER | 0.9 | no | | | | | | | | |

Within a family, effort and dependence do not depend on the amendment data except through λ̂: the dollar records discipline the *accounting* (how much of observed amendment spending the model can attribute to bargaining margin), while the coded terms drive behavior. The margin share rises with θ by construction. The contracts cannot choose among consistent values; cost data, invoices, or competing bids for comparable work would be needed.

## 4. Contract-design gap at the calibrated terms (Model 1)

The agency re-optimizes monitoring m, portability p and penalty exposure F at θ = 0.5 (or the largest consistent θ below it). F is bounded by the highest SLA cap in the corpus (20% of the base contract).

| Family | θ | Coded (m, p, F) | Optimal (m, p, F) | Effort (coded → optimal) | Dependence (coded → optimal) | Agency value gain (model units) |
| --- | --- | --- | --- | --- | --- | --- |
| IL-IDES-DELOITTE-PUA | 0.5 | (0.5, 2, 0) | (1, 0.35, 2) | 0 → 0.853 | 0.139 → 0.308 | 13.1 |
| MI-DTMB-FAST-MIDAS | 0.5 | (1, 3, 0.5) | (1, 0.35, 2) | 0.352 → 0.853 | 0.104 → 0.308 | 6.97 |
| NV-DWSS-PONDERA | 0.5 | (0.5, 0, 0) | (1, 0.35, 2) | 0 → 0.853 | 0.417 → 0.308 | 12.8 |
| IN-FSSA-FRAUDCASTER | 0.25 | (0.5, 1, 0) | (1, 0.14, 2) | 0 → 0.853 | 0.104 → 0.182 | 12.8 |

Two patterns follow from the model rather than the data. Monitoring has no value without an enforceable consequence (F = 0 makes effort zero at any m), so the binding term in most coded contracts is the remedy, not detection. And under fully competitive bidding amendment margins are offset in the initial bid, so portability pays only by reducing wasteful dependence investment; its optimal level depends on the illustrative portability cost and should not be read as evidence that coded portability is excessive. Gains are in model units because the value, burden and governance parameters are not calibrated.

## 5. Structural restrictions for Models 3–5

- **Model 3.** No coded contract pays for verified outcomes, so R = 0. At default costs the usage-only contract at the default usage price gives welfare 6.64 versus 6.66 at the welfare-maximizing terms. A usage price alone can reach that optimum here only because costs and burdens are known; the design gap widens when they are not.
- **Model 4.** No coded contract states a false-positive standard, so the expected false-flag penalty is zero. With a per-flag reward above cost the vendor's threshold is 0 (flag everything), against a public threshold of 0.314.
- **Model 5.** The NASPO cloud participating addenda contain no local acceptance-testing language, whereas the MMIS participating addendum does. With partial internalization (ω = 0.5) the default local-validation scenario omits a socially valuable local test, costing 2 across agencies.

## Inputs

SHA-256 hashes of every calibration input are in `calibration.json`.
