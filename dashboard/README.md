# Procurement Incentives Lab

A standalone, responsive dashboard for all nine [procurement models](../game_theory/README.md), including the combined Models 8–9. It recomputes equilibria in the browser as contract parameters change; it does not interpolate the earlier saved simulation grid.

## Features

- Nine model pages with two primary controls and an editor for every parameter.
- Three outcomes, sensitivity curves, selected-scenario markers, and all-outcome comparisons.
- Pin current terms as a comparison, then vary either primary parameter.
- Export current/comparison scenarios as JSON and fully parameterized sensitivity sweeps as CSV.
- Browser-local scenario persistence, responsive layouts, keyboard-accessible controls, model assumptions, and boundary warnings.

The dashboard uses the same mathematical specifications as `simulation/models.py`. `dist/models.js` is a browser port validated against Python-generated fixtures. No external JavaScript libraries or build dependencies are required. The site is prepared for private Sites hosting; `dist/` is the complete static application.

## Local use and verification

From the repository root:

```sh
simulation/.venv/bin/python dashboard/generate_fixtures.py
node --test dashboard/tests.mjs
simulation/.venv/bin/python -m http.server 8765 --directory dashboard/dist --bind 127.0.0.1
```

Open `http://127.0.0.1:8765`. Serve via HTTP because browser ES modules may be blocked when opened directly from `file://`.

The parity check covers every output across the 241 sweep scenarios in `simulation/config.json` and 15 additional boundary cases. Invalid inputs are rejected before solving. For numerical stability and browser responsiveness the UI accepts finite, nonnegative parameters up to 1,000,000, with the stricter theoretical constraints applied by each model.

Sensitivity charts solve approximately 81 points for each scenario (integer points for agency count), adding selected values and known review boundaries. Hover/tap details report the nearest **solved** point. Connecting lines are visual guides; they do not imply continuous outcomes at discrete thresholds. The selected outcome cards compare each scenario at its own parameter values; sensitivity lines vary the chosen axis over a shared range while holding each scenario's other parameters fixed.

Illustrative parameters are not empirically calibrated. Fixed payments and welfare conventions differ across models; raw magnitudes should not be compared across models. Negative initial bids, multiple validation equilibria, review tie-breaking, and substitution feasibility follow the theory notes and are described on the relevant model page.
