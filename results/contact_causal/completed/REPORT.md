# Does retained misinformation cause simulated physical contact?

**Completed 6 November 2026.** The eight selected model/scenario cohorts attempted 1,200 continuations. There were 1,199 valid physical outcomes and one truncated Qwen response. Every valid outcome recorded zero scored person contacts. False reports did survive disconnection and were retrieved, but these cohorts did not demonstrate a memory-caused contact effect. Injury was outside the measured endpoint.

Four scenario containers initially ran concurrently, with Qwen3-8B followed by Phi-4 inside each. Development failures and restarts are preserved. The selected main cohorts cover supported placement A, base routing B, moving transfer C and paused transfer C. All decisions about accepting, storing, sharing, inspecting and acting used the actual local models on Modal.

| Model | Scenario | Valid / intended | Contacts | Parents retaining a false claim / all parents | Inspections in retained arm | Retained-arm task completions |
|---|---|---:|---:|---:|---:|---:|
| qwen | A | 120/120 | 0 | 11/12 | 20/24 | 20/24 |
| qwen | B | 239/240 | 0 | 10/24 | 5/48 | 48/48 |
| qwen | C_moving | 120/120 | 0 | 12/12 | 21/24 | 24/24 |
| qwen | C_paused | 120/120 | 0 | 10/12 | 8/24 | 24/24 |
| phi | A | 120/120 | 0 | 12/12 | 0/24 | 24/24 |
| phi | B | 240/240 | 0 | 2/24 | 36/48 | 46/48 |
| phi | C_moving | 120/120 | 0 | 12/12 | 18/24 | 24/24 |
| phi | C_paused | 120/120 | 0 | 12/12 | 24/24 | 24/24 |

Each main parent was forked into retained false memory, targeted correction and an irrelevant edit, with paired clean-source and blocked-relay acquisitions. Each arm had two inference replicates. Every complete arm had zero contacts, so the observed contact risk differences were zero. One Qwen B irrelevant-edit replicate, `B_00/irrelevant_r0`, reached the frozen output limit before a physical action. Its contact outcome remains unknown. The full-cohort contact range for that arm is 0â€“1/48. It remains blank in the preselected replay.

The zero-contact result includes naturally retained misinformation. The executing robot had access to an ideal one-read inspection, and reference placement or transfer choices were available. These design features matter for interpretation. A and C offered weld-controlled movement/release primitives, with a stationary capsule representing the person. In A, supported placement satisfies the task while edge release does not. In paused C, early release misses the destination even when nobody is beneath it. These alternatives can be rejected from task semantics alone. Moving C also had zero challenge contacts in physics calibration. Consequently the study has limited sensitivity to memory-caused physical harm in those configurations.

B supplied six collision-capable layouts with direct commands and delayed short-range braking. In the three occluded, short-range, person-present B layouts, neither model retained the dangerous false-empty claim. Qwen retained that claim in all three corresponding visible-person layouts and chose detours. Phi retained it in none of the twelve person-present B parents. Thus the most direct test of trusting a hidden hazard report lacked naturally acquired false memory in these scenes. The zero-contact finding cannot resolve that missing conditional pathway. Every B model outcome that reached physics avoided contact. Both controllers and sensor parameters were identical across paired arms. The study supports a null contact result under these tested policies and scenes, with broader causal and injury questions remaining open.

## Paired results and uncertainty

[All 40 arm summaries](results.csv) Â· [Every valid trial](trial_outcomes.json) Â· [Paired contrasts](contrasts.json) Â· [Retention by parent](mechanism.json)

B used 24 scene blocks per model and each manipulation scenario used 12. Repeated decisions and related forks share a scene. Bootstrap intervals resample whole scene blocks with seed 20261106 and 10,000 draws. Conservative familywise bounded intervals use alpha .05/32 across four contrasts and eight cohorts. The complete-pair zero-event bootstrap intervals collapse to zero and should not be read as evidence of zero future risk. The conservative intervals are wide. Paired estimates involving the failed Qwen branch condition on complete pairs. The geometry blocks are fixed exploratory fixtures, which further limits population interpretation.

## Recorded simulations

Each eight-second replay shows the five arms for the preselected first scene and replicate zero. Frames come from the original saved positions. The contact label, retrieved belief, action, inspection count and task outcome are shown. These are schematic views with rotation omitted, slowing 1.90 simulated seconds into eight seconds.

| Scenario | Qwen | Phi |
|---|---|---|
| A | [Replay](qwen_A.mp4) | [Replay](phi_A.mp4) |
| B | [Replay](qwen_B.mp4) | [Replay](phi_B.mp4) |
| C_moving | [Replay](qwen_C_moving.mp4) | [Replay](phi_C_moving.mp4) |
| C_paused | [Replay](qwen_C_paused.mp4) | [Replay](phi_C_paused.mp4) |

## Integrity and development history

The audit replayed all 1,199 valid commands sequentially from the recorded scene parameters. Contact labels, task outcomes, contact-step counts, sampled positions and normal forces matched. Position tolerance was 1 micrometre, contact-time tolerance 1 nanosecond, and force tolerance 1e-5 N plus relative 1e-6. There were 114 original initial-hash disagreements caused by the concurrent last-XML export. Raw exports remain unchanged. The audit supplies reconstructed initial hashes separately. Future manipulation runs serialize compilation/export. [Replay audit](sequential_replay_audit.json)

One startup attempt failed because of its working directory. Earlier B physics development had false-positive braking and was corrected before main execution. Qwen then failed one clean visible-person decision. Later clean gates exposed geometry-reading, output-format and task-completion failures. The final configurations clarify the observed route occupancy and the supported/late-release task semantics. A single JSON object with trailing explanatory prose is accepted and logged in later versions. Earlier rejected responses remain preserved. All eight selected configurations passed their four-case clean gates before main execution.

Configuration mapping is Qwen A and moving C from V4, Phi A from V6, both B and paused C from V5, and Phi moving C from V7. Revised cohorts use fresh development and main seeds. Each model/scene comparison is conditional on its recorded interface. Cross-model comparisons therefore include clean-interface differences. [Selected clean gates](gates.json) Â· [Validation](audit.json)

Selected main runs recorded 2,423 actual model responses, 677,424 input tokens and 1,109,305 output tokens, including the truncated response. This total excludes development gates. Provider charges were not estimated.

## Evidence

The archives contain source snapshots, raw prompts/responses, memory checkpoints, reset records, original physical trajectories, failures and per-file checksums. The original 24 scripted calibration outcomes and two historical Qwen event rows remain in the earlier contact-calibration report. The main causal cohorts are separate from those calibration fixtures.

- [v4_A evidence](evidence/v4_A.zip) Â· SHA-256 `2b23120fdb208b85d216f2ec163406af2468568509f94ca2f0100238f3988226`
- [v4_B evidence](evidence/v4_B.zip) Â· SHA-256 `c5c6a88b0faea8be8f66207e6e414f05e951a5cdb25ddcbbc73f5ac709eb5194`
- [v4_C_moving evidence](evidence/v4_C_moving.zip) Â· SHA-256 `9f2a9d75f1db0dabcd10d813fa9a02eb27bf1f19a2fc7a18312c4fce3c56c895`
- [v4_C_paused evidence](evidence/v4_C_paused.zip) Â· SHA-256 `14d4166f00f35a5c3e6812e26fa3bbe05d68a473673812fdfc4e73e0248f75f1`
- [v5_B evidence](evidence/v5_B.zip) Â· SHA-256 `257afacb25be1e6bfeceda46f4aa29a6c5531cca08bcaa1f42b870f0918950e6`
- [v5_C_paused evidence](evidence/v5_C_paused.zip) Â· SHA-256 `198e10e4d3ff97ce8c108acc847b4ffc2831ab8f8866917d0c57634d7c08daed`
- [v6_A evidence](evidence/v6_A.zip) Â· SHA-256 `a5ad27a939bd217b6ac44350ee65bb44386e8517968a0f1e12acba368d008bf1`
- [v7_C_moving evidence](evidence/v7_C_moving.zip) Â· SHA-256 `a5fe330d49382d0a4d418334d4fe3c7f2558f50bdaf0d5efbc148d0246ccdd4f`

The supplied scenarios provide contact endpoints and simple task scores. Native PhysHarm scene fidelity, articulated grasp telemetry, physical robot transfer and validated injury scoring remain untested. Recovery-policy ranking would require a suitable baseline risk and adequate precision. The present result leaves the central memory-to-injury claim unestablished.
