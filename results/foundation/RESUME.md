# Paused at user request — 4 November 2026

All Modal experiment containers were stopped and verified absent. No overnight
experiment or automatic restart is scheduled. Credentials remain outside the repo.

## Completed evidence

- F1: 96 real-model probes. Explicit thinking Qwen3-8B passed screening and the
  fresh 24-probe check. Non-thinking configurations did not pass the clean gate.
- F2/F3 v1: all 72 continuations completed, validation passed, all safely completed.
  F2 useful-memory gate failed (19/24 correct claims stored; 3/12 beneficial pairs).
  F3 clean gate passed; no controlled false-memory violation occurred.
- F2/F3 v2: interrupted on user request. The local capture contains 16 completed
  continuations out of 72 and 16 acquired parents out of 24. Completed-record hashes
  were checked. No complete-cohort gate result is available. The interrupted run is
  preserved in `F23_v2_interrupted.zip` with a local capture manifest. The remote
  wrapper did not finish its ordinary whole-run archive on cancellation.
- F4–F6: NOT STARTED.

## Resume sequence

1. Inspect the interrupted v2 artifacts and implement safe continuation from the
   frozen manifest, checkpoints and exact source snapshot. Preserve all partial
   attempts and completed branches; do not overwrite them or silently replace seeds.
   Finish and validate the full 72-cell cohort before interpreting the gates.
2. If F2 remains unsuccessful, diagnose on new development cases while preserving
   earlier outcomes. Do not force storage, peer acceptance or a positive attack.
3. Once clean gates pass, freeze and run F4–F6: 240 acquisitions, 1,200
   continuations, including all clean counterparts, paired rescue replicates,
   blocked-relay controls, and physical/free dock-cost modes. The replay selection
   was declared before outcomes in `docs/FOUNDATION_PROTOCOL.md`.
4. Independent replication requested by the user: a different model family,
   genuinely different scenes/tasks, and a faithful published defense baseline.
   Select the model and upstream baseline after checking official sources and
   implementation suitability; pin versions and preserve the baseline's actual
   semantics. A renamed home-built verifier is not a faithful baseline.
   Different jitter or paraphrases alone are not different scenes/tasks. Run clean
   competence and memory-use checks for the new model before replication.

The existing evidence has not demonstrated the full naturally retained
misinformation-to-physical-failure pathway. Replication must test whether the
observed outcome or protective boundary extends, without presupposing a failure.
No hardware, AIM integration or external collaboration is claimed or scheduled.

Repository branch: `codex/foundation-f1-f6` in `smfatima3/workIN`.
Modal interrupted app: `ap-Pkuci3yMcUj97BXMB3VuOy` (stopped).
Persistent volume path: `workin-memory-safety-evidence:/foundation_f23_v2`.
