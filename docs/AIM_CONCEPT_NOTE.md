# Collaboration concept: residual robot-safety risk after memory-source removal

**Researcher:** Maryam Fatima, independent AI/ML researcher.

**Working question:** When does removing or revoking a compromised information source fail to restore safe behavior in communicating robots, and which recovery policies reduce residual physical risk while preserving useful task performance under incomplete provenance and limited verification?

**Why this may matter:** An evaluation can appear clean once the attack input is gone, while earlier information remains in other agents' memories. For a robot team, the relevant recovery criterion is later physical behavior and useful mission performance. Measuring how much poison was deleted is an incomplete operational answer.

**Distinct scope:** Prior work already addresses memory persistence, multi-agent propagation, revocation enforcement, selective repair, and robotic communication attacks. The proposed study measures recovery in a physical control loop: source removal, retained descendants, later tasks, executed constraints, controller intervention, and repair cost. We would not claim that persistent memory attacks or provenance are new.

**Public evidence of fit (checked 3 November 2026):** AIM convenes PASC, whose published agenda includes recoverability, adversarial evaluation, evidence sufficiency and physical evaluation. [AIM PASC announcement](https://www.aim-intelligence.com/blog/pasc-building-the-foundations-for-physical-ai-safety-1788434117231), [PASC](https://www.pasc-ai.com/). This supports a plausible technical fit; it does not establish a purchase need, available infrastructure, or interest in this particular collaboration.

**Initial reusable experiment:** A frozen 60-rollout study with three simulated robot-associated agents, one physical scenario, ten matched seeds, and six conditions spanning clean/false information, persistent/transient zone memory, and use-time verification. The first research deliverable is an all-run figure, traceable memory-to-action events, and one paired trajectory replay. This evidence remains an exploratory part of the eventual paper.

**Recovery follow-up:** Matched blocking-only, full-reset, TTL, lineage-deletion, local-shield and use-verification policies under incomplete lineage and common sensing budgets; paired risk, task/retention cost, uncertainty, and a 24-second replay. The useful company-facing deliverable is a reproducible post-incident regression test and recovery comparison, contingent on actual-model validation.

**Current status:** Software package prepared and tested with a scripted policy and a local HTTP contract stub. No real-model scientific results are claimed. Actual model runs, strong published-method integration, and independent platform evaluation remain to be completed. No AIM platform access has been established.

**What Maryam can contribute:** Reproducible experiment implementation; per-agent memory/reset/repair instrumentation; paired statistical analysis; provenance and evidence audit; an evaluation package and clearly bounded manuscript.

**Proposed AIM contribution:** If scientifically useful to the team, co-design a physically meaningful scenario and scoring scheme, assess compatibility with its agent/robot environment, and guide a limited independent validation. These are discussion topics, not requested commitments to hardware, compute, or authorship.

**Potential company-facing deliverables, contingent on results:**

| Possible finding | Concrete demonstrator | Potential evaluation benefit |
|---|---|---|
| Residual risk survives source removal | Clean/poison/repaired matched runs with complete traces | Add a post-incident memory test to a safety evaluation workflow |
| Deleting poison fails to predict physical safety | Contamination and executed-risk comparison across controllers | Avoid treating memory cleanup as sufficient safety evidence |
| A low-cost repair dominates full reset | Safety–task–observation tradeoff report | Inform recovery policy choice while retaining useful state |
| Existing controllers contain the effect | Negative result with valid exposure/adoption and tight uncertainty | Identify protective design conditions and their limits |
| Scene/model transfer fails | Boundary cases and reproducible regression tests | Improve robustness evaluation scope |

These are hypotheses and proposed benefits. Do not pitch them as improvements to AIM's products until measured jointly. Their infrastructure, data access, commercial priorities, and collaboration terms remain unknown.

**First discussion request:** A short technical-fit discussion around the frozen protocol and any completed discovery evidence, followed by a small mutually agreed transfer experiment. Do not lead with a request to borrow a robot or with an unvalidated reproduction-threshold claim.

**After real discovery runs, fill this status paragraph directly from analysis outputs:**

“Across [completed/intended] frozen exploratory rollouts, the paired change in delayed executed violations was [estimate and interval]. The clean verification cost was [task/time/inspection change]. [Describe mechanism or null result]. This is a limited [scenario/model] study; the next question is whether it transfers to an independently implemented physical-safety scenario.”

Leave fields unfilled until the relevant data exist. Nothing in this package sends a message or application.
