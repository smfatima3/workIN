# AGENTS.md — strict Codex execution contract

## Objective and scientific scope

Build evidence for **residual physical safety risk after source removal/revocation in robot-agent memory networks** and the risk–utility tradeoff of repair. This is a new robotics measurement study related to Paper 2, not a claim that its reproduction threshold has been validated. The existing Paper 2 files are read-only reference material; do not overwrite or replace that paper.

Read in order: README.md; docs/RESEARCH_QUESTION_AND_PAPER.md; docs/EXPERIMENTS.md; docs/METRICS_AND_STATISTICS.md; docs/TRANSFER_AND_BASELINES.md; docs/SOURCES.md. Record progress in a new `EXECUTION_LOG.md` under the active run directory, with UTC timestamps and the user's local date if presenting schedules.

## Non-negotiable evidence rules

1. Never fabricate results, citations, seeds, model revisions, costs, simulator capabilities, or physical-harm estimates.
2. `scripted` is software validation only. It must never enter discovery/main/transfer tables or scientific videos. Never silently fall back to it when an API fails.
3. Run the actual model for every scientific agent decision. Use separate private memory stores and stateless API sessions. No shared hidden conversation or cross-trial cache.
4. A source-removal reset must erase the seed, disconnect the source, clear all transient context/queues, and preserve only allowed memory state. Validate both boundaries and keep snapshots.
5. Adoption, sharing, write-back, and actions must be chosen by the downstream policy. The controlled initial record exposure is an explicit assumed compromise, not demonstrated external exploit success.
6. Provenance is exposure/derivation evidence, not proof of semantic contamination. Corrective memories and quoted/rejected claims are not “infected.” The current restricted structured-claim vocabulary makes semantic scoring deterministic; do not extend it to free text without an adjudication protocol.
7. Evaluator truth, condition names, poison labels, and future outcomes must never enter agent prompts or defense decisions. Sensor access must obey physical range and declared failure settings. A revocation notice can identify a source record but must not reveal which descendants are false.
8. Always keep ordinary local obstacle/robot avoidance active. Distinguish unsafe requests, controller-blocked requests, executed rule violations, physical contacts, and injury. Do not infer injury from a rule breach or contact impulse.
9. Every defense needs matched clean and poisoned conditions with identical task/controller/sensor settings. Include benign-memory retention, task performance, inspection burden, time, and model cost. A stop-everything policy is not a useful safety result.
10. Do not rename a home-built verifier “CPV,” “MAPLE-Guard,” or “A-MemGuard.” Exact named baselines require faithful integration, source version, license review, and an upstream reproduction/audit. Current baselines are transparent adaptations, clearly labeled.
11. Current plane-constrained platforms, structured sensor observations, complete or deliberately unavailable provenance, static sign truth, and modeled docking lookup cost must remain explicit limitations. The timing sweep changes logical memory age, not a simulated week or a sequence of autonomous distractor missions.
12. No fabricated theory: rho(K)<1 does not imply physical safety. The operator utility is illustrative unless independently estimated with validated assumptions and uncertainty. Three robots cannot establish an epidemic phase transition.

## Execution order and mandatory gates

**G0 — artifact/physics.** Install; run all tests and preflight; inspect safe/unsafe trajectory cases; confirm physical dimensions/rules; verify hash/integrity checks and API schema handling. Stop scientific runs on failure.

**G1 — actual-model development.** Use development seeds only. Check clean task completion, no oracle leakage, meaningful memory use, actual schema failure rates, a reproducible false-claim lifecycle, and safe behavior under correct local observations. Diagnose near-zero clean success or high invalid-response rates before evaluating attacks. Do not require a positive poisoning result as a pass criterion.

**G2 — frozen discovery.** Freeze prompts, model, code, metrics, parameters, and all 60 intended rollouts before seeing held-out outcomes. Execute/validate/analyze every condition, including null results. Generate one paired replay with predeclared selection. Label exploratory evidence. No post-outcome attack tuning on discovery seeds.

**G3 — paper viability and prior art.** Compare the observed result against MemSecBench, MAPLE-Guard, AgentPoison, multi-robot CPV work, Revoked but Still Authoritative, and Governed Memory for Physical AI. A copied false claim surviving deletion is insufficient novelty. Continue only if the research question yields a useful measurement, failure boundary, or recovery tradeoff. A null result can be scientifically useful; do not invent an effect to pass. Complete a faithful strong prior-work comparator or explicitly limit claims to a controlled benchmark study.

**G4 — confirmatory design.** Run design sensitivity; choose independent sample size and primary family before execution. Defaults are budgeting examples only. Main seeds must be disjoint from development/discovery; model/scene choice must not be selected on main outcomes. Do not make precision or noninferiority claims from n=10.

**G5 — main evidence.** At least two safety mechanisms, restricted/unrestricted controls, actual model, and all primary cells. Keep interrupted/API-error cases visible; resume/retry same intended seeds. Explain nonrandom missingness. Do not rank methods on incomparable subsets.

**G6 — recovery/mechanism.** Run matched repair policies, E5b provenance/read-budget stress, isolation/stale controls, retention/topology sweeps, source-only versus descendant removal, and sensor failure. Validate identical physical-initialization hashes. Every sensor consumer, including shields, must obey the same declared failure setting and shared allowance. Report clean and poisoned utility for every repair and a zero-docking-cost sensitivity. Report expected-by-construction differences separately from new findings. Compare fixed sensing budgets and code/prompt interfaces; report additional verification resources.

**G7 — external validity.** Another model family and unseen scenes; for broad embodied claims, independent simulator/platform transfer. Current `transfer` script only covers topology/sensor stress. An AIM/Isaac/ROS/hardware result must not be claimed until that integration and scenario contract pass validation. Reuse the logging/evaluator contract, not invented physics data.

**G8 — paper assembly.** Tables/figures come from raw logs and scripts, with exact versions, complete manifests, failures, uncertainty, and limits. Final claims must map to completed experiment IDs. Include artifact checksums and provenance.

## Reuse without contaminating the final paper

- Software fixtures: never scientific evidence.
- Development: troubleshooting/tuning only; not main results.
- Discovery: retained, citable exploratory panel/appendix with clear status. If it affects design, do not pool it into the confirmatory estimate.
- Main: independently frozen confirmatory cohort; no peeking-driven stopping or seed replacement.
- If all scientific settings were genuinely frozen prospectively and a pooling rule was preregistered, an aggregate can be secondary; otherwise present cohorts separately.
- Editing a plan's lockfile or deleting an unfavorable rollout is forbidden. Correct errors by new versioned runs and record why.

## Statistical and runtime contract

The independent unit is a complete rollout, not a message, robot, frame, or repeated task. Use matched blocks. Report primary risk difference, memory interaction, and defense effect; adjust the predefined primary family. Report uncertainty even with zero events. Utility noninferiority needs a predeclared acceptable margin and a sufficiently narrow appropriate interval, not a non-significant p-value. Do not interpret the exploratory interaction sign-flip diagnostic as exact factorial inference.

Keep raw model responses, prompts, sensor decisions, memory snapshots, reset traces, physical states, API usage/latency, seeds, model revisions, environment, code hash, and all failed attempts. Actual monetary costs require provider prices dated to the run and charged usage; otherwise report tokens and time only.

Use isolated trials for parallel execution; never share mutable simulator/agent state. Preserve checkpoints after each trial and at least every 20 minutes. A checkpoint is not a durable backup: retain the run folder on a persistent volume and export checksummed ZIPs. Do not provision cloud compute or reuse credentials found in prior conversations. The user requested an artifact; paid experiment execution needs a separately authorized budget/environment.

## Stop/report behavior

On infrastructure failure, finish independent safe work, preserve logs, and report the exact blocker. Do not substitute synthetic evidence. On null or weak scientific results, report the outcome with limits and revise the framing transparently on new development data. Ask the user only for genuinely missing model/budget/platform choices that tools cannot resolve; do not repeatedly ask permission for local fixes already within scope.

## Required final handoff

A validated execution log; complete manifest and protocol lock; all raw results/failures; metrics CSV; summary JSON with intervals; outcome figures; paired MP4 + source manifest; results ZIP + checksum; a one-page result/contribution note; and a paper outline with every claim tagged `SUPPORTED`, `EXPLORATORY`, `UNSUPPORTED`, or `NOT RUN`.

## Revision 0.2.0 requirements

- Use the revised method-neutral RQ. Do not assume dependency-aware deletion is novel or superior.
- Complete provenance is not sufficient for safety without enforcement and treatment of dependent state; independent sensors are not infallible or free.
- Never let recovery read evaluator-only pre-mask lineage or claim truth. Report actual metadata availability and observation denials.
- Partial lineage currently means unavailable entire record ancestry, not semantic compression or forgery. State this exact scope.
- Before a broad recovery-method claim, implement mixed true/false descendants, independently supported correct records, delayed/derived-state cases, and a faithful published comparator, or explicitly narrow the claim.
- Preserve the v0.1.0 archive and all old raw evidence. New code requires new manifests; legacy fixtures do not validate changed behavior.
