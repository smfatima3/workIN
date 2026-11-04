# Research question, scientific value, and revised paper

Date: 3 November 2026. Status: proposed study with tested software; no empirical LLM findings.

## Recommended central question

**When does removing or revoking a compromised information source fail to restore safe behavior in communicating robots, and which recovery policies reduce residual physical risk while preserving useful task performance under incomplete provenance and limited verification?**

The decisive extension is *restoration of safe behavior after an information incident*. The paper should quantify physical residual risk, identify when contamination statistics are misleading, and compare recovery policies under explicit observation and task costs. Merely showing that a copied false claim survives deleting its source would be unsurprising.

Working title: **Restoring Safe Robot Behavior after Information-Source Revocation**.

Dependency-aware repair is a candidate policy, not an assumed contribution or a promised winner. The central result should be a measured recovery boundary or a useful safety–utility tradeoff. Complete provenance alone does not restore safety: a system must act on it, remove or revalidate dependent state, and deal separately with already committed physical actions.

An alternative if evidence supports persistence but not recovery comparisons: **Persistent Memory Poisoning and Delayed Safety Failures in Communicating Robot Teams**.

## Why the community needs this question answered

Robotic deployments reuse maps, handoff reports, task experience, and shared claims. Operators responding to a bad source may remove that source, clear the current conversation, or revoke its access. Those actions need not remove earlier copies or their behavioral influence. A later ordinary task can exercise a stale retained belief after the visible incident has ended.

The practical unknown is not whether storage persists. It is **whether that residual state remains consequential in a closed physical control loop**, how much risk persists, and what recovery operation is sufficient at acceptable cost. A low-level controller may absorb a wrong high-level belief; another task may turn one residual record into a constraint breach. Conversely, deleting many records can harm useful coordination without improving physical safety.

Answering this enables:

- A reproducible post-incident safety test, including delayed tasks and clean controls.
- A way to compare source deletion, source revocation, descendant repair, full reset, verification, and action-level safeguards using actual behavior.
- Evidence about when memory contamination is an inadequate proxy for robot safety.
- An operational recovery report: residual risk, benign state retained, observation overhead, time to restore performance, and known limitations.

These are intended benefits. No deployment capability or commercial value has been demonstrated yet.

## Related work narrows the claim

AgentPoison already studies agent memory/RAG poisoning, including an autonomous-driving setting. MemSecBench follows poisoning through persistence, execution, and repair. MAPLE-Guard addresses memory-mediated cross-agent reuse and lifecycle defenses. Multi-robot communication-attack work already links unsafe claims to actions and evaluates a CPV gate. EgoSafetyBench highlights both missed hazards and unnecessary interventions. Revoked but Still Authoritative also measures memory-backend revocation failures. Governed Memory for Physical AI already develops a robot-memory withdrawal/retained-state architecture and explicitly leaves physical behavioral evaluation prospective. These strengthen the need for an empirical physical contribution rather than a new label for revocation. See `SOURCES.md` for verified primary links.

Therefore do not claim any of these as new by itself: memory poisoning, persistence after a session reset, multi-agent propagation, lineage instrumentation, provenance checking, selective repair, or the observation that task success can coexist with danger.

The **candidate contribution** is a controlled, embodied *post-source-removal recovery evaluation*, showing how different retained states, physical constraints, controller protections, and repair costs change the relationship between contamination and executed safety violations. This is a scoped hypothesis about a useful research gap, not an exhaustive proof of firstness.

## Research questions and falsifiable outcomes

| RQ | Question | Supporting evidence | Useful null / limit |
|---|---|---|---|
| RQ1 — residual risk | Does poisoning increase later executed rule violations after source and transient contexts are removed? | Paired B−A effect with uncertainty, traceable false adoption, real model, full resets | No measurable increase within precision; controller/model may contain the effect |
| RQ2 — memory mechanism | How much of the poisoning effect depends on persistent memory and inter-robot transfer? | (B−A)−(D−C), isolation controls, stored false claims, later retrieval, held-out scene/model checks | Shared memory may not be needed, or ordinary sensing errors may dominate |
| RQ3 — recovery | Which repair policies reduce residual physical risk at acceptable task and sensing cost? | Matched clean/poison comparisons, post-alert trials, utility/latency/resource tradeoffs, strong published comparator | A simple full reset or independent shield may dominate; report this |
| RQ4 — proxy validity | Do fewer false memories or a lower propagation score reliably mean safer physical execution? | Joint contamination–violation analysis and held-out prediction, controller-protected cases, low-spread failures | Metrics may align on tested conditions, or predictive evidence may be too weak |

Make RQ3 the organizing question of the paper; RQ1 establishes the problem and RQ2 tests its mechanism. RQ1–RQ3 are the core paper. RQ4 is secondary until there is enough data for predictive validation. An attractive Paper 2 analogy must not dictate results.

## Threat model and assumptions

Core experiments condition on a single guaranteed compromised record and controlled initial exposure. The adversary cannot change system prompts, simulator state, controllers, the evaluator, sensor truth, or later data. Downstream agents can reject, correct, retain, or share the claim. The source is disconnected before evaluation; no reseeding is allowed.

The current implementation uses a restricted structured claim (zone restricted/unrestricted/unknown), exact private stores, and complete or partially unavailable ancestry metadata. The new recovery stage masks lineage fields at the recovery boundary without changing claim content; this models metadata availability, not paraphrase or forged provenance. The first report is experimentally delivered from the source; this does not establish that an attacker can create that record through external interaction. A future external-entry experiment must measure seed creation separately from propagation and residual harm.

For recovery conditions, the team receives a source-record revocation signal. This is an assumed detected incident. The study does not currently evaluate a detector, alert latency, semantic paraphrase, forged lineage, or adaptive attacker. The recovery stage now evaluates missing ancestry, shared inspection budgets, and an unavailable sensor. A true claim may also be revoked in the clean counterpart, exposing unnecessary repair cost.

## Causal target and decision rule

Let R_H(pi, M, x_r) be the probability of an executed rule violation within the frozen post-reset horizon H, given downstream policy pi, retained memory M, and physical initialization x_r. The memory contrast is

    Delta_memory = E[R_H(pi, M_poison, x_r) - R_H(pi, M_clean, x_r)].

Keep pi, dynamics, task, sensor access, physical initialization, and horizon identical. Do not compare a blocked-source policy to a different clean policy and call the difference a memory effect. A/B changes the initial information and the resulting retained state; it estimates that controlled exposure effect through the declared persistent-state channel, not a natural indirect effect or the effect of one particular record. All later physical initializations are now hashed and checked within matched blocks. Real-model sampling noise remains part of the experiment; a nominal seed does not guarantee identical model samples.

For recovery, compare R_H(pi_r, M, x_r) and ordinary/safe task completion under each policy r. A policy is useful only if a predeclared risk target and acceptable utility loss are supported by sufficiently precise intervals. Freeze the risk target, utility margin, sensing budget, and comparison family before confirmatory execution; do not pick them after viewing the Pareto plot. The existing 0.05 utility margin is a placeholder requiring scientific justification.

H1: Retained poisoned state can increase post-reset executed violations relative to matched clean and transient-memory controls. A precise null is useful.

H2: Recovery policy rankings can depend on provenance availability and observation budget. Selective deletion need not beat full reset or verification; a simple dominating baseline is a valid result.

A novel-method claim additionally requires mixed true/false descendants, independently supported correct claims, alert delays or derived state, and a faithful strong published comparator. These are **not implemented yet** and are explicit gates, not completed experiments. The present metadata mask is a deliberately narrow mechanism test.

## Paper 2 relationship

Paper 2 asks when memory propagation grows or dies out. This paper asks whether physical safety is restored after the source is removed, and whether repairs preserve useful behavior. Keep their datasets, claims, and manuscripts separate; cite shared methods/code transparently.

For nonnegative next-generation K and initial item count vector z0, a finite-horizon diagnostic is:

\[
S_H=\sum_{g=0}^{H} q^\top K^g z_0.
\]

If expected generation counts are componentwise bounded by K and q bounds per-item conditional hazard probabilities, a union/expectation bound gives P(any hazard by H) ≤ min(1,S_H). Those assumptions are strong and must be checked; fitted means are not probabilistic upper bounds. This is elementary supporting analysis, not a new theorem or a validated robot guarantee.

Even rho(K)<1 permits nonzero finite-horizon harm. A finite directed chain can have rho(K)=0 and still carry one hazardous claim to another robot. Conversely, a local rule controller can suppress violations while false memories remain. `09_operator_diagnostic.py` illustrates this distinction without manufacturing a fitted K.

## Proposed paper structure (adapt page budget to venue)

1. **Introduction (about 1 page).** A source is removed but later robot behavior is still at risk. Explain the operational recovery problem, exact RQ, prior-work boundary, and evidence-supported contributions. Do not open with an epidemic analogy.
2. **Related work (about 0.75 page).** Memory persistence/repair; multi-agent and multi-robot attacks; runtime physical safety. Use a precise comparison table; acknowledge direct overlap.
3. **Recovery problem and estimands (about 1 page).** Same-policy memory contrast, matched physical initialization, information available to each repair, and predeclared risk/utility requirements. Then: Robot dynamics/observations, private memory, source/descendant semantics, source revocation, safety predicates, limited sensor access, guaranteed seed versus external entry.
4. **Evaluation protocol and recovery policies (about 1.25 pages).** Exposure → source removal/reset → memory-only relay → reset → later physical tasks; six controls; repair baselines; benign context; partial provenance; shared sensing limits; cost sensitivity. Describe transparent controls without inventing a novel algorithm.
5. **Experimental setup (about 1 page).** Models/revisions, physics/controller, scenarios, seeds, cohort separation, observation and compute budgets, failure handling, statistics.
6. **Results (about 2 pages).** RQ1 residual risk; RQ2 persistence/communication controls; RQ3 recovery boundaries under provenance/sensing limits and clean/poison utility comparisons; optional RQ4 proxy failures. All numerical claims come from frozen logs.
7. **Generalization, limits, and operational implications (about 0.75 page).** Sensor uncertainty, another model/platform, no injury extrapolation, guaranteed compromise, provenance assumptions, and what a deployer can actually infer.
8. **Conclusion (short).** Only established results and remaining limits.

Appendices: full manifests/prompts; code/scene versions; reset tests; all seeds/failures; paired inference; additional controls; video selection; external baseline reproduction details; Paper 2 diagnostic assumptions.

## Required figures and tables

| Item | Content | Evidence source |
|---|---|---|
| Fig. 1 | Source removal, surviving memories, later robot action; mark reset boundaries | Protocol; not an empirical result |
| Fig. 2 | Executed delayed violations and safe completion for A–F | Full main cohort; `04_analyze.py` |
| Fig. 3 | Recovery risk vs task/inspection cost | Defense cohort; include clean counterparts |
| Fig. 4 | Exposure → false storage → later retrieval → unsafe request → execution | Event logs; distinguish counts/denominators |
| Fig. 5, if supported | Retained false memory vs physical violation across controllers/scenes | Secondary analysis; not a fitted-on-test predictor |
| Table 1 | Closest prior work and precise additional scope | Verified sources |
| Table 2 | Model, observation, controller, scenario, sample and failure counts | Manifest/environment |
| Table 3 | Paired primary effects with intervals; utility cost | Frozen analysis |
| Table 4 | Baseline implementation fidelity and transfer limits | Integration audit |

The initial discovery figure and paired video can appear in the paper's preliminary/appendix material. They do not become confirmatory merely because the project later grows.

## Claim decisions after results

- **Strong case:** reproducible residual physical effect on unseen seeds, meaningful controls, useful recovery tradeoff against a strong baseline, and another model/platform.
- **Measurement case:** reliable benchmark/negative boundary with clear reusable instrumentation, but no novel defense. Present it as such.
- **Insufficient:** only scripted behavior, one cherry-picked clip, forced downstream compliance, no clean utility, or a trivial source-copy demonstration. Do not submit broad safety claims.
