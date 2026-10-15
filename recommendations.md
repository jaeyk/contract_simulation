# Designing contracts that hedge against vendor strategies

Recommendations for public agencies drawn from the procurement models (Models 1–9), the contract-design optimization, and the calibration to state contracts in this repository. See the [README](README.md) for the full workflow and results, and [game_theory/](game_theory/README.md) for the models.

## The core principle

Make vendors pay for what the agency values: verified, correct outcomes and the full cost of achieving them, backed by remedies the agency can actually enforce. Contracts that pay for activity, flags, or nominal completion, or that rely on monitoring without consequences, invite the strategies below.

## Vendor strategies and contract countermeasures

| Vendor strategy | What the models show | Contract countermeasure |
| --- | --- | --- |
| **Bid low, earn on amendments** (Model 1) | Competition pushes expected amendment margins into lower initial bids, so the award price understates lifecycle cost. Dependence still wastes resources. | Evaluate bids on **expected lifecycle cost**: base price plus priced change-order rates. Lock in hourly rates and an annual change-order budget at award, as Illinois did in its PUA contract's 7th amendment ($150–200/hr). |
| **Build lock-in** (Models 1, 8) | Dependence raises the bargained price of every later amendment and repair. | **Portability as a package:** state ownership of data *and* code, source-code escrow the agency can test and have released, transition assistance, and documentation. Open-source licensing of custom code is one way to secure the code part, not a substitute for the rest: open code can still be locked in through undocumented configuration, vendor-controlled hosting, or know-how held only by the incumbent. Arizona's UI modernization vendor won the exclusion of source code and blocked state access to the escrow package during negotiation; those are the clauses to protect. |
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

## Limits of contractual safeguards

Contracts can align incentives on outcomes that are **observable and verifiable**, but only while the agency can still exit. Beyond that, safeguards hit predictable limits.

### Limits that come from the models

| Limit | Why it happens | Where it shows up |
| --- | --- | --- |
| **Safeguards aren't free** | With competitive bidding, vendors price risk into their bids, so the agency pays for every penalty and warranty. Penalties above the real harm cause over-investment and may thin the bidder pool. | Model 1 bid offset; Model 2 overinvestment |
| **A remedy is only as good as the evidence behind it** | Effort responds to *chance of detection × penalty*. If errors are hard to observe or their classification is disputed, nominal clauses do nothing. | Model 1 (m·F); Model 2 (w is enforced coverage, not contract wording) |
| **Lock-in undermines enforcement** | Termination and re-procurement threats are credible only if the agency can actually leave. The more dependent it is, the weaker every exit-based remedy. | Model 7: with larger cost savings or weaker detection, even auditing every time cannot deter substitution |
| **Contracts get renegotiated** | Amendments are bargained under lock-in, so protections can be traded away mid-contract or before signature. | Model 1 bargaining |
| **The agency can't bind its own future behavior** | Once bad output arrives, fixing it is the agency's best move. The vendor anticipates this, so remedies that apply only after the agency fails to fix things are neutralized. | Models 6 and 9: the vendor holds work at the review cutoff |
| **Every measurable target can be gamed** | Pay for flags and you get flags; penalize only errors that reach applicants and the vendor manages around review. | Models 4 and 9 |
| **One term alone often does nothing** | Safeguards work in pairs: warranty with portability, penalty with detection, reward with false-flag enforcement. | Model 8; Model 4 (the optimal per-flag reward falls from 8.9 to 2.7 when false flags are rarely caught) |
| **Unforeseen change can't be priced in advance** | Pandemic programs, new federal guidance, and caseload spikes create genuinely new work. Contracts can only set *how* it is priced, through rate cards and change-order budgets. | Illinois PUA amendments; MiDAS CARES Act changes |
| **One buyer can't fix a collective problem** | No single agency's contract funds testing whose benefits are shared across buyers. | Model 5 |

### What the contract data add

- **Remedies are rare and capped.** 3 of 19 state contracts have service-level fee reductions, capped at 5–20% of fees. Only 1 has performance liquidated damages. None pays for outcomes or states an accuracy standard.
- **Protections erode in negotiation.** Arizona accepted four vendor deviations, each weakening a safeguard.
- **Continuity overrides competition.** MiDAS ran through 13 monthly bridge extensions "while negotiations continue". The exit threat that safeguards rely on wasn't available.
- **The counterparty can change.** Pondera contracts were reassigned to West Publishing (Thomson Reuters) mid-term after an acquisition, and Kansas bought through a reseller (SHI). Both blur who is responsible for remedies.
- **Burden falls outside the contract.** Errors that hit applicants appear in no contract metric unless the agency writes them in.

Safeguards therefore need non-contractual supports:

- in-house technical capacity;
- independent testing;
- re-procurement planning that starts early;
- representative audits of outcomes for applicants.

## Does the optimal design differ for AI?

### What the data can and cannot say

The corpus is mostly **predictive risk scoring and legacy systems**, not generative or agentic AI:

- **Predictive scoring:** Pondera, FraudCaster, COMPAS, Vant4ge, and OnPoint.
- **Large, mostly rules-based builds:** MiDAS, the Deloitte UI systems, and HEAplus.

The data therefore cannot compare AI with non-AI contracts, and they say nothing about generative or agentic systems. They do support one comparison: predictive-analytics subscriptions versus system builds.

| Coded safeguard | Predictive analytics (11) | System builds (7) |
| --- | --- | --- |
| Any performance remedy (liquidated damages or service-level penalties) | **0** | 3 |
| Transition assistance | 2 | 6 |
| Source-code escrow | 1 | 3 |
| Independent verification and validation | 0 | 2 |
| Unit pricing | 4 | 3 |
| Accuracy or false-positive standard | 0 | 0 |

The scoring products, the most AI-like contracts in the corpus, carry the *fewest* safeguards. The comparison is confounded: they are small vendor-standard subscriptions, while the builds are custom projects worth $50 million or more.

### What the theory says

The core principle doesn't change: pay for verified outcomes, back them with enforceable remedies, and keep a credible exit. What changes is the parameters, so the binding term and its required strength shift.

The table below re-runs the design optimizer under parameter shifts that plausibly distinguish the technologies. The shifts are illustrative, not estimated.

| Technology | What plausibly differs | What the models say to emphasize |
| --- | --- | --- |
| **Legacy builds** | Lock-in and defect-driven amendments dominate; errors are relatively testable | Warranty enforcement, portability, and rate cards (Models 1, 2, 8). Optimal portability rises with dependence leverage, from 0.19 to 0.82 as leverage goes from 1 to 4. |
| **Predictive scoring** | Payment tied to flags; false positives are hard to observe and harm applicants | Pay for validated findings, and set the reward together with false-flag enforcement. When false flags are rarely caught, the optimal per-flag reward falls by about two-thirds (Model 4). |
| **Generative AI** | Output errors are pervasive, verifying them is costly, and providers swap models often | Remedies on raw error rates, measured staff review, and change notification (Models 6, 7, 9). Raising the vendor's savings from a cheaper model from 4 to 8, or cutting detection from 0.5 to 0.2, makes deterrence impossible even with certain auditing. Notification that raises detection to 0.8, plus a larger sanction, restores it. |
| **Agentic AI** | The vendor's orchestration controls how much billable work happens, and actions can cause harm | Avoid usage pricing, cap and log actions, attach liability to actions, and require recovery duties. The optimum stays at no per-action price, but a bad price becomes far costlier when the vendor controls more of the workflow: at the same price, welfare loss rises from 7.4 to 19.3 (Model 9). |

### Where theory is ambiguous: does AI raise or lower lock-in?

- **Raises it:** dependence on retrieval systems, prompts, evaluation sets, and workflow state.
- **Lowers it:** interchangeable foundation models and cheaper development.

The models cannot settle this, and it determines whether portability terms matter more or less for AI. It is the main empirical question for a follow-up.

### What a real comparison would need

Generative and agentic contracts with their amendments, usage invoices, evaluation reports, and permission settings, classified by actual capability and deployment date rather than by signing year.

## Caveats

- **Magnitudes are illustrative.** Figures such as "a 20% cap raises effort to 0.85" depend on uncalibrated value, cost, and burden parameters. The direction of each recommendation is robust within the models; the levels are not.
- **Stronger terms have costs.** Vendors price risk into bids, and penalties above the true social loss produce overinvestment (Model 2). Very demanding terms may also reduce the number of bidders, which these models do not capture.
- **Evidence gaps.** The contract records cannot separate amendment costs from bargaining margins, and the corpus is a FOIA/EPIC sample rather than a random one. Testing these recommendations would require cost data, invoices or competing bids for comparable work, and records of how often agencies actually enforce remedies.
