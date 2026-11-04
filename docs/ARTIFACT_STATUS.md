# Artifact status

Prepared 3 November 2026 for Maryam Fatima's robotics extension of Paper 2.

## Included and executable

- Python package and ten ordered CLI scripts.
- MuJoCo planar robot simulator and two safety-rule families.
- Structured memory/communication, controlled exposure, fresh-session resets, recovery controls.
- Configurable actual-model HTTP client with usage/latency records and explicit failure handling.
- Immutable manifests, code hashes, raw traces, resumption, sharding, progress checkpoints.
- Analysis, figures, paired video, result packaging, and design-sensitivity utilities.
- Strict `AGENTS.md`, full run instructions, paper/research rationale, experiment ordering, metrics, baseline/transfer contracts, and collaboration concept note.

## Not a completed scientific result

Bundled artifacts use the scripted fixture. No real model experiment, empirical propagation threshold, safety guarantee, comparison with released prior-work code, Isaac/ROS integration, or hardware/AIM evaluation is claimed.

The handoff deliberately prevents scripted fixtures from running under scientific stage names. Real-model endpoint and model revision must be supplied before research execution. Defaults for large grids are examples subject to power/precision and budget review.

## Implementation assumptions worth reviewing before main runs

- Source exposure is guaranteed and structured; no external attack feasibility is measured.
- Two downstream agents can independently adopt/reject/write/share; the source is an initial record holder rather than a fully evaluated planning policy.
- Private memory is a small exact store. No vector retrieval, free-text summary laundering, competing claims, or learned retrieval is evaluated.
- Recovery now masks ancestry with fixed probabilities 1/0.5/0; actual missingness is logged. This is not semantic compression or forged lineage. Source alert detection and authenticity remain assumed.
- Sign sensing has range constraints, but no image recognition, occlusion, or probabilistic measurement noise; failure stress returns unknown.
- Local collision avoidance is simple and identical across arms. Contact values are not injury estimates.
- Future tasks repeat a scene with seeded state changes; logical age is not a natural distractor-task sequence.
- Full-reset docking cost is configurable, defaults to a modeled 4-second delay, and needs a zero-cost sensitivity. It is not a measured industrial workflow cost.
- The paired replay is rendered from measured simulator states, not video from real robots.

See `VERIFICATION.md` for the actual software validation performed on delivery.

Revision 0.2.0 adds shared observation budgets, sensor-failure enforcement for shields, physical-initialization hash validation, and paired clean/poison utility for all recovery methods. Mixed-support records, alert/command latency, natural-language summaries, published-method fidelity, and external platform transfer remain future gates.
