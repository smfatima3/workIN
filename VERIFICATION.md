# Current real-model status — 4 November 2026

Qwen3-8B development completed: 60/60 real-model rollouts, validation PASS, 220
schema-valid responses, no failed trials. The Modal environment also reran all
35 tests and 72 recovery fixtures successfully. Semantic development checks did
not pass: no memory adoption and unsafe model actions under correct observations.
Discovery/main/recovery research remain unrun. See
[the complete result report](results/qwen3_8b_development_v3/Qwen3_8B_E1_Report.md).
The sections below are the preserved original package verification history.

# Revision 0.2.0 verification — 3 November 2026

**Software validation passed. Actual-model research experiments have not been run.**

- 35 automated tests passed on Python 3.12.14 and MuJoCo 3.17.0, including new tests for immutable memory snapshots, truth-independent metadata masking, missing-lineage repair without oracle access, shared sensing limits, sensor failure at the local shield, correct-record deletion, matched physical state, and research-stage fixture exclusion.
- Physics preflight passed.
- 72 scripted recovery rollouts completed: six stress variants × twelve conditions, three later tasks per rollout. This is software coverage with one seed, not statistical research evidence.
- All 72 passed integrity, reset, matched-initialization, observation-budget and prompt-label checks. Resume skipped all 72 after hash verification.
- Full analysis succeeded: six separate strata, all 72 condition summaries, paired risk comparisons and clean/poisoned utility/cost comparisons. No strata were pooled and no noninferiority claim was generated.
- A 24-second H.264 paired trajectory replay (1440 × 496, 12 fps) was generated from the first eligible matched block, watermarked as a scripted test. Its poster and an aggregate outcome plot were visually checked.
- Results were exported with checksums. The prior source ZIP and original raw fixture evidence are preserved separately.

The sensor-failure bug fix changes baseline behavior: old and new runs must not be pooled or resumed under a changed code hash. No actual LLM outcome, deployment advantage, novel-method superiority, external platform compatibility or AIM interest has been demonstrated.

## Prior-delivery verification, retained as history

# Delivery verification — 3 November 2026

**Status: software validation passed; scientific experiments not run.**

- 26 automated tests passed on Python 3.12.14 and MuJoCo 3.17.0.
- Tests cover physical footprint geometry, range-limited observations, executed speed/zone rules, independent local shielding, TTL, benign-state-preserving revocation, source removal, transient-state clearing, corrective claims, sensor failure, larger robot graphs, repeated tasks, missing-endpoint errors, and the HTTP JSON/usage/session contract.
- The CLI integration test exercises preparation, concurrent execution, hash validation, safe resume, and deliberate evidence-tampering detection.
- Twelve complete scripted-policy physics rollouts ran through the delivered preparation → execution → validation → analysis → video → result-export workflow. All twelve completed and validated.
- Resuming the completed plan skipped all twelve completed trials after verifying their raw-file hashes.
- Append/finalization behavior was hardened during integration: progress logs are separate from immutable completed event evidence. Truncated evidence is rejected rather than silently repaired or accepted.
- The actual-model HTTP path was tested against a local stub. This validates request/response plumbing only, not a real model's performance or provider compatibility.
- The paired video was verified as H.264, 1440 × 496, 288 frames, 24 seconds. A representative frame and aggregate figure were visually inspected. It is clearly labeled as a scripted software test.
- The algebraic operator example produced spectral radius zero and nonzero finite-horizon hazard weight, as expected for the explicitly supplied finite chain. It is not an empirical estimate.
- The example paired-design calculation returned 132 independent pairs under its stated assumptions. This does not establish an appropriate universal sample size; the actual protocol needs its own design/precision decision.

## Not verified

Real LLM scientific outcomes; model endpoint availability outside the local stub; released CPV/MAPLE/A-MemGuard integration; Isaac Sim/ROS 2/AIM compatibility; camera-based perception; humanoids or manipulation; hardware safety; injury modeling; empirical reproduction thresholds; novelty or venue acceptance.

The included software fixture is for reproducibility checks only. Its values must never be placed in a research abstract or described as actual-model results.
