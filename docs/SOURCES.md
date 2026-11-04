# Source audit and claim boundaries

Checked 3 November 2026. Primary sources below ground the positioning; this is a targeted novelty check, not an exhaustive systematic review. Preserve version/date when writing the manuscript. Numbers from these papers are not results for this package and are not used to calibrate its simulator.

| Source | Verified relevance | Consequence for this study |
|---|---|---|
| [AgentPoison](https://arxiv.org/abs/2407.12784) | Agent memory/RAG poisoning; includes embodied-driving relevance | Memory poisoning plus embodiment is insufficient novelty |
| [MemSecBench](https://arxiv.org/abs/2607.27080), [full text v1](https://arxiv.org/html/2607.27080v1) | Lifecycle evaluation spanning storage, later execution, and selective repair | Do not claim the first persistence-to-repair protocol |
| [MAPLE-Guard](https://arxiv.org/abs/2608.00426), [full text v2](https://arxiv.org/html/2608.00426v2) | Persistent private/shared memory, cross-agent reuse, lifecycle gates | Direct strong comparator for any proposed lifecycle method |
| [When Coordination Becomes a Threat](https://arxiv.org/abs/2608.06830), [full text v1](https://arxiv.org/html/2608.06830v1) | Multi-robot communication attacks and claim-provenance/verification gate | Propagation into robot actions and provenance checking already studied |
| [EgoSafetyBench](https://arxiv.org/abs/2607.00218) | Embodied runtime-safety judgments; both missed hazards and unnecessary interventions | Evaluate safe-task cost alongside protection |
| [A-MemGuard](https://arxiv.org/abs/2510.02373) | Memory validation and corrective experience/dual memory | Another relevant memory-defense comparator |
| [MemoryGraft](https://arxiv.org/abs/2512.16962) | Persistent behavior change via retrieved poisoned experiences | Session persistence is not a new attack class here |
| [Memory Poisoning Propagation and Repair Mechanism in Multi-Agent Collaborative Environments](https://doi.org/10.1145/3806262.3806294) | Evidence-graph and propagation-aware repair | Cross-agent repair is direct prior art; avoid a “first repair” claim |
| [Revoked but Still Authoritative](https://arxiv.org/abs/2609.08258) | Agent-memory retrieval can fail to enforce revocation; evaluated backend guard | A critical additional comparator: revocation failure alone is not new |
| [Governed Memory for Physical AI](https://spherity.github.io/spherity-research/governed-robot-memory-physical-ai.html) | Author's October 2026 overview describes retained-state revocation, operation gates, and physical recovery; robot behavioral evaluation remains prospective | Even robot-memory governance/revocation is not a new concept; focus on measured closed-loop consequences and cost |
| [MuJoCo Python documentation](https://mujoco.readthedocs.io/en/stable/python.html) | Official bindings, physics stepping, state copying, installation | Technical basis for the local implementation |
| [MuJoCo function reference](https://mujoco.readthedocs.io/en/stable/APIreference/APIfunctions.html) | Physics step and contact-force interfaces | Contact measurements are simulator quantities |

## Unverified or access-limited items

- [PhysHarm project page](https://physharm.vercel.app/) could not be opened in this check. AIM infrastructure/API/multi-robot support is not assumed.
- The earlier conversation's [When Prompts Control Robots](https://arxiv.org/abs/2608.00747) was found in search but full primary-page access failed during this check. Recheck before using precise methodological claims; the accessible multi-robot paper above already establishes close overlap.
- The earlier RoboMME/Astra and Gemini product claims were not needed for this implementation and are not used as dependencies. Verify actual versions, code, and provider availability before adopting them.
- No source establishes that this proposed study will be accepted by a venue or that AIM will collaborate.

## Current Paper 2 reference

Reviewed the existing execution-plan artifact titled `AGENTS.md` (Library file `libfile_dd749913b2488191b4ab29b8f72be414`, 1,250 lines). It specifies a memory reproduction model and an empirical validation plan; it is not a completed result report. This package does not modify it or claim its threshold has passed validation. Its lineage discussion is tightened here: ancestry must be combined with semantic falsehood/use evidence, because a corrective descendant is not contamination.

## Final novelty judgment

**Plausible empirical contribution; not established novelty.** A worthwhile result would quantify a physical post-incident recovery gap, characterize when contamination measures mispredict executed risk, or show a useful safety–task-cost tradeoff under an independent controller and realistic observations. Strong baseline comparison and external validation determine whether this becomes a full paper. “A retained false record can still matter” is insufficient.

## Recovery revision: company fit and additional prior-art checks

- [AIM's PASC announcement](https://www.aim-intelligence.com/blog/pasc-building-the-foundations-for-physical-ai-safety-1788434117231), published 7 September 2026, and [PASC](https://www.pasc-ai.com/), checked 3 November 2026. AIM convenes an open physical-AI safety consortium with recoverability, sufficiency and adversarial evaluation in its agenda. Technical alignment is an inference; commercial/collaboration interest is unconfirmed.
- [When Truth Is Distributed](https://arxiv.org/html/2608.03421v3): the deceiver-exit study retains testimony/conversation history; do not equate it with fresh future robot tasks after all transient context is cleared.
- [Containing Behavioral Cascades](https://arxiv.org/abs/2609.30523): the accessible primary abstract describes active Verify–Adapt–Hold and task-cost tradeoffs. It is close recovery prior art; full-method reproduction is not supplied here.
- [IJCAI 2026 robot-compromise paper](https://ijcai.org/proceedings/2026/71): single-entry robot compromise and communication-mediated unsafe actions are prior work, not a new contribution of this package.

The detailed method claims above retain the scope of the source access recorded in the previous assessment. The current revision rechecked AIM's official page, MAPLE-Guard and the author's Governed Memory overview. It makes no firstness or venue-acceptance claim.
