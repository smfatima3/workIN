# Transfer and strong-baseline integration

## Why two layers

The included MuJoCo benchmark is a self-contained mechanistic measurement environment. It lets the first 60 real-model rollouts generate reusable evidence without waiting for an external simulator or collaboration. It does not establish humanoid safety, manipulation safety, or AIM platform compatibility.

An external embodiment should reuse:

- Per-agent memory lifecycle and source/descendant IDs.
- Source removal, session/queue reset, repair notice semantics, and paired seeds.
- Action-request versus executed-action distinction.
- Frozen condition/metric names and trial IDs.
- Raw sensor/trajectory/video logs and integrity checks.

It must **replace** the physical world, robot observation/action adapter, and scenario-specific safety evaluator with validated platform implementations.

## Candidate transfer options

| Option | Suitable evidence | Integration status |
|---|---|---|
| Isaac Sim + ROS 2/Nav2 | Multi-robot navigation under realistic sensing, namespaces, obstacles | Not implemented or validated in this bundle |
| AIM/PhysHarm-compatible scenario | Physical-safety evaluation chosen jointly with their team | Access/capabilities unknown; no assumed permission or API |
| RoboMME/other manipulation benchmark | Persistent false object/procedure claim affecting manipulation | Separate environment/control interface; not interchangeable with navigation |
| Real robots | Sim-to-real limits under supervised bounded tests | Not authorized or provided here; simulation results do not establish hardware safety |

Do not translate MuJoCo coordinates into arbitrary ROS topics and call the integration complete. For ROS, verify robot names, frames, time source, navigation action API, world-reset state, localization, costmaps, sensor observations, controller cancellation, and data timestamps. For Isaac, freeze exact simulator version and compatible GPU/driver/scene assets from official documentation. The named Gemini/Astra model availability and IDs from earlier conversation must be rechecked with the provider; no dependencies here rely on those claims.

## Adapter acceptance contract

Before transferring a scientific cohort, implement and test these operations in a dedicated module:

1. `reset(scene_seed, task_seed, robot_states)`: resets simulator, controller queues, clocks, maps and caches; returns reproducible state IDs.
2. `observe(robot_id)`: returns only physically available, timestamped sensing; no evaluator oracle fields.
3. `inspect_claim(robot_id, claim)`: executes a feasible sensing action; reports cost, unavailable observations, and uncertainty.
4. `execute(robot_id, command)`: records request, controller acceptance/rejection, actual trajectory and contacts; preserves independent safety limits.
5. `evaluate_episode()`: uses separate privileged evaluator state to compute predefined physical metrics.
6. `record_video()`: produces timestamped actual simulator-camera frames with identifiers matched to event logs.
7. `reset_agent_sessions()`: terminates transient contexts, messages, hidden tool state, and replay buffers while preserving declared memories.

Acceptance tests: clean success, deliberately constructed rule breach, safe blocked command, stale sensor, reset independence, concurrent robot isolation, deterministic seed scope, and no privileged-state leakage. A mock passing these tests cannot be reported as platform transfer.

## Baseline fidelity and scientific claim limits

| Baseline | Included implementation | Allowed name |
|---|---|---|
| No defense / no zone memory | Yes | Exact benchmark control |
| TTL / full reset / source-only deletion | Yes | Exact benchmark control, not a learned defense |
| Ancestry-based revocation | Yes, uses available ancestry; E5b includes missing metadata; source alert assumed | Transparent descendant-revocation control |
| Write-time / use-time verification | Yes, local posted-rule sensor | Custom verification baseline |
| Local rule shield | Yes, local sensor-triggered detour/speed cap | Simple rule controller; no formal guarantee |
| Published CPV Gate | No faithful implementation | “Related to CPV” in discussion only |
| MAPLE-Guard | Not integrated | Required strong lifecycle comparator candidate |
| A-MemGuard | Not integrated | Additional memory-defense candidate |
| Revocation-enforcement guard (2609.08258) | Not integrated | Direct related recovery comparator candidate |

An ancestry-deletion baseline, even under missing metadata, is not automatically a novel algorithm. E5b probes a failure boundary; independent support and derived state still need implementation. To claim improvement over CPV/MAPLE or another published method:

- Read the actual paper and released code; pin the exact revision and inspect the license.
- Reproduce at least one upstream setting or document unavailable code and a faithful paper-based reimplementation.
- Match access to memory, source alerts, observations, controller rules, model context, and budgets.
- Keep any adaptation in a separate registered adapter with a deviation table.
- Evaluate clean utility and all attack arms; never silently replace a method with a keyword filter.

The current artifacts are sufficient to run the controlled study. Completion of a strong published comparator and independent scene/platform validation is still needed for broad superiority/generalization claims.
