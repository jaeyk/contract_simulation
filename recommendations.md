# Designing contracts that hedge against vendor strategies

Recommendations for public agencies drawn from the procurement models (Models 1–9), the contract-design optimization, and the calibration to state contracts in this repository. See the [README](README.md) for the full workflow and results, and [game_theory/](game_theory/README.md) for the models.

## The core principle

Make vendors pay for what the agency values: verified, correct outcomes and the full cost of achieving them, backed by remedies the agency can actually enforce. Contracts that pay for activity, flags, or nominal completion, or that rely on monitoring without consequences, invite the strategies below.

## Vendor strategies and contract countermeasures

| Vendor strategy | What the models show | Contract countermeasure |
| --- | --- | --- |
| **Bid low, earn on amendments** (Model 1) | Competition pushes expected amendment margins into lower initial bids, so the award price understates lifecycle cost. Dependence still wastes resources. | Evaluate bids on **expected lifecycle cost**: base price plus priced change-order rates. Lock in hourly rates and an annual change-order budget at award, as Illinois did in its PUA contract's 7th amendment ($150–200/hr). |
| **Build lock-in** (Models 1, 8) | Dependence raises the bargained price of every later amendment and repair. | **Portability as a package:** state ownership of data *and* code, source-code escrow the agency can test and have released, transition assistance, and documentation. Arizona's UI modernization vendor won the exclusion of source code and blocked state access to the escrow package during negotiation; those are the clauses to protect. |
| **Under-prevent defects, then bill for repairs** (Models 2, 8) | Prevention collapses when uncovered defects become paid work. Weak portability makes this worse, because repairs are priced under lock-in. | **Agency-controlled defect classification**: the state decides what counts as a defect versus new scope. Make covered repairs non-billable, or **cap repair prices**. In Model 2 a price cap cut social cost from 6.33 to 4.77 and reduced the enforcement needed. Do not accept "mutually determine" language. |
| **Shirk where monitoring has no consequence** (Model 1, calibration) | With no enforceable penalty, quality effort is zero at any monitoring level. Three of the four calibrated contracts were in this position. | **Remedies first, monitoring second.** Service-level fee reductions with meaningful caps: the corpus shows 5–20% of fees, and a 20% cap raised modeled effort from 0 to 0.85. Then fund independent verification and validation (IV&V) so failures are detected. |
| **Inflate billable activity** (Models 3, 9) | Per-action pay rewards extra checks, retries, and tool calls, especially when staff correct the errors anyway. | Pay for **verified correct completion**. If you use usage pricing, set the rate knowing costs and burdens, and track **cost per correct case**, not call counts. |
| **Let agency staff absorb errors** (Models 6, 9) | A penalty only on errors that reach applicants is neutralized by the agency's own review. Vendors can hold quality just low enough that staff keep correcting. | Tie remedies to **raw error rates** measured before agency correction, or **charge the vendor for correction labor**. Record staff review time as a contract cost. |
| **Over-flag to hit a proxy** (Model 4) | A per-flag reward with no false-positive penalty means flag everything. None of the 19 coded state contracts states an accuracy or false-positive standard. | Pay for **validated** findings, include an enforceable false-positive standard, and measure appeal-adjusted outcomes on representative samples, not just flag counts. |
| **Swap in a cheaper configuration after acceptance** (Model 7) | Deterrence requires audit probability × sanction ≥ the vendor's savings. Termination threats count only if credible. | **Change-notification and revalidation duties**, audit rights with evidence access, and remedies that do not depend on termination, since lock-in makes termination non-credible. |
| **Free-ride on a cooperative award** (Model 5) | Shared tests are underprovided, and local tests are skipped when agencies discount local harms. The NASPO cloud participating addenda contain no local testing language. | **Assign and fund** common validation explicitly, and require **local acceptance testing** in participating addenda. Treat purchasing eligibility as distinct from validated deployment. |

## Design principles

1. **Instruments interact, so design them together.** Warranty enforcement and portability are complements (Model 8): portability raises prevention, and enforcement is weaker without it. Penalties and review interact (Model 9). Strengthening one term while its partner stays weak can accomplish nothing.
2. **Remedies bind before detection.** Spending on monitoring is wasted without an enforceable, adequately capped consequence.
3. **Measure the right outcome.** Use raw correctness, verified completion, cost per correct case, and appeal-adjusted accuracy, not activity, flags, or errors that survive review.
4. **Protect key terms during negotiation.** Arizona's memorandum of negotiations shows value leaking through four accepted vendor deviations: source code excluded, escrow access blocked, defect classification shared, and the SLA at-risk cap cut from 13% to 10%. Treat such terms as non-negotiable, or price them explicitly.
5. **Keep a credible exit.** Portability, transition plans, and competitive re-procurement timelines prevent extension chains like MiDAS's 13 monthly bridge extensions in 2021–22.

## Contract checklist

### At solicitation and award

- [ ] Bids are scored on expected lifecycle cost, including priced change-order rates and an annual change-order budget.
- [ ] The state owns data, deliverables, and custom code; escrow is testable and has defined release events.
- [ ] Transition assistance, documentation, and knowledge transfer are deliverables with acceptance criteria.

### Quality and remedies

- [ ] The agency alone classifies defects versus new scope; covered repairs are non-billable or price-capped.
- [ ] Service-level fee reductions have meaningful caps and are actually assessed.
- [ ] Remedies attach to raw error rates, not only errors that reach applicants.
- [ ] Accuracy and false-positive standards are stated and measured on representative samples.
- [ ] IV&V or equivalent independent testing is funded.

### Payment structure

- [ ] Payment is tied to verified correct completion, not activity volume or flag counts.
- [ ] Agency correction and review labor is measured, and charged back where attributable.

### After award

- [ ] Material changes to models, data sources, or subcontractors require notification and revalidation.
- [ ] Audit rights include access to logs and evidence.
- [ ] Remedies exist that do not depend on termination.
- [ ] Re-procurement starts early enough to avoid bridge extensions.

### Cooperative purchasing

- [ ] Common validation is assigned and funded.
- [ ] Participating addenda require local acceptance testing before deployment.

## Caveats

- **Magnitudes are illustrative.** Figures such as "a 20% cap raises effort to 0.85" depend on uncalibrated value, cost, and burden parameters. The direction of each recommendation is robust within the models; the levels are not.
- **Stronger terms have costs.** Vendors price risk into bids, and penalties above the true social loss produce overinvestment (Model 2). Very demanding terms may also reduce the number of bidders, which these models do not capture.
- **Evidence gaps.** The contract records cannot separate amendment costs from bargaining margins, and the corpus is a FOIA/EPIC sample rather than a random one. Testing these recommendations would require cost data, invoices or competing bids for comparable work, and records of how often agencies actually enforce remedies.
