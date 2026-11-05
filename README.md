# Persistent Memory and Residual Robot Safety Risk

**5 November 2026 · F1–F6 and the Phi-4 warehouse replication are complete.** The two main cohorts completed 1,839/1,840 planned continuations. One Qwen response reached the output limit. The [final report](results/Final_Experiment_Report.md) includes paired comparisons, recovery costs, the MAPLE-Guard baseline, replays and verified evidence.

**Historical E1 result · 4 November 2026.** Qwen3-8B on
Modal completed and validated 60/60 rollouts (220 model calls), following 35 tests
and 72 fresh scripted recovery fixtures. The model rejected every peer claim and
chose unsafe direct actions, including after restricted observations; verification
code enforced safe detours. The semantic development gate failed, so discovery
and later stages of the original E1 protocol were left unrun. See the
[result report](results/qwen3_8b_development_v3/Qwen3_8B_E1_Report.md),
[complete evidence ZIP](results/qwen3_8b_development_v3/Qwen3_8B_E1_Evidence.zip), and
[Modal setup](docs/QWEN3_MODAL_RUN.md). Development results are not evidence of a
residual memory-poisoning effect or a new recovery method. No OpenAI-hosted model
was used. Earlier package documents below retain their original historical scope.

A reproducible experiment package for the question:

> **When does removing or revoking a compromised information source fail to restore safe behavior in communicating robots, and which recovery policies reduce residual physical risk while preserving useful task performance under incomplete provenance and limited verification?**

This package supplies a protocol for reusable exploratory evidence. Original
demonstrations use an explicitly labeled scripted test policy. The new Qwen3
development evidence is separately labeled in `results/`; it is not discovery or
confirmatory evidence. The optional Modal runner provisions compute only when
explicitly invoked with an authorized account. Nothing contacts AIM or deploys a robot.

**Revision 0.2.0:** recovery is now the organizing question. See `docs/REVISION_2026_11_03.md` for implemented changes, the audit, and remaining gates. Earlier fixture evidence is preserved separately; it is not evidence for this revision.

## Start here, in this order

1. Read `AGENTS.md` — the execution contract.
2. Read `docs/RESEARCH_QUESTION_AND_PAPER.md` — motivation, contribution boundaries, revised paper structure.
3. Read `docs/EXPERIMENTS.md` — numbered experiments, budgets, and gates.
4. Install, test, and run the short software smoke below.
5. Configure one actual model, run development, then freeze discovery.
6. Validate and analyze all runs; generate the paired video from those same saved runs.
7. Use the discovery evidence in the paper's exploratory section and collaboration concept note. Keep subsequent confirmatory seeds independent.

## What is actually implemented

- MuJoCo rigid-body dynamics for 3–5 simplified planar mobile platforms, with identical local collision avoidance across all conditions.
- Two explicit safety-rule families: exclusion-zone entry and speed-zone violations; restricted and unrestricted contexts.
- Separate private memories, structured claim adoption, optional write-back/sharing, two fresh-session reset boundaries, source removal and disconnection, downstream physical execution.
- Six primary conditions A–F; TTL, complete reset, source-only deletion, descendant revocation, local rule shield, and write-time verification controls; isolation and stale-information controls.
- Recovery stress stage: full/partial/no lineage metadata, shared inspection allowances, sensor unavailability, paired cost/utility analysis, and matched physical-state hashes.
- Actual OpenAI-compatible model calls via a configured local or hosted endpoint; prompts/responses/usage logs; no automatic mock fallback.
- Deterministic manifests, code hashes, independent trial folders, raw logs, resume, sharding, checkpoints, aggregate statistics, figures, a short paired trajectory video, and checksummed result ZIPs.

## Scope you must not overstate

The robots are **force/velocity-controlled planar platforms**, not wheeled hardware, manipulators, or humanoids. Agents receive structured observations, not camera frames. The source's initial false record is delivered under a controlled guaranteed-exposure threat model; B/C decide whether to adopt/store/share. Physical goals are concurrent deliveries, with a fixed controller rather than free-form LLM motion control. Rule violations and simulator contact measurements are safety proxies, not calibrated injuries.

The local simulator and HTTP contract have been tested, and the Qwen3 endpoint
completed the development cohort described above. Isaac Sim, ROS 2, external
published defenses and AIM infrastructure remain unvalidated.
`docs/TRANSFER_AND_BASELINES.md` gives acceptance work for those additions. The
main script is executable, but full-paper claims require the scientific gates in
`AGENTS.md`.

## 0. Install and verify

Linux, Python 3.10+ recommended; tested with Python 3.12.14. CPU simulation needs no RTX GPU. Model inference may use a remote endpoint or a separate GPU server. Dependencies are in `pyproject.toml`; exact tested direct dependencies are in `requirements-tested.txt`.

```bash
cd memory_robot_safety
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements-tested.txt
python -m pip install -e . --no-deps
python -m pytest -q
python scripts/00_preflight.py
```

Do not use the unrestricted `pip freeze` from an unrelated environment as a reproducibility lock. A per-run environment report records the actual relevant packages. For long-lived studies, preserve the entire container image/digest or your environment lock as well.

## 1. End-to-end software smoke — no API calls

```bash
python scripts/01_prepare.py --stage smoke --out runs/smoke_v1
python scripts/02_run.py --plan runs/smoke_v1 --workers 2
python scripts/03_validate.py --plan runs/smoke_v1
python scripts/04_analyze.py --plan runs/smoke_v1
python scripts/05_video.py --plan runs/smoke_v1 --out runs/smoke_v1/analysis/paired.mp4
python scripts/07_package_results.py --plan runs/smoke_v1 --out exports/smoke_v1.zip
```

This is 12 short rollouts (2 seeds × 6 conditions). All results and video say **SCRIPTED TEST — NOT RESEARCH RESULTS**. The supplied demo is generated through this path. Scripted behavior is deliberately credulous so the instrumentation exercises both safe and unsafe paths. Do not cite its effect sizes.

## 2. Configure an actual LLM

Use an already available OpenAI-compatible endpoint. A `/v1/chat/completions` API with JSON output is needed; a model-name claim from a social-media post is not sufficient. Check the provider's actual model listing. The package does not hard-code the previously discussed Gemini/Astra model IDs.

```bash
export MRS_API_BASE='http://127.0.0.1:8000/v1'
# If needed, set MRS_API_KEY securely in the shell; never put it in a config, command history, or ZIP.
python scripts/00_preflight.py --check-endpoint
```

Set `MODEL_ID` and `MODEL_REV` to the **actual** available model and immutable checkpoint/revision, or dated hosted-provider snapshot. Neither value should be invented. For example, set shell variables through your environment manager before the commands below.

```bash
python scripts/01_prepare.py --stage development --provider openai_compatible \
  --model "$MODEL_ID" --revision "$MODEL_REV" --out runs/development_v1
python scripts/02_run.py --plan runs/development_v1 --workers 1
python scripts/03_validate.py --plan runs/development_v1
python scripts/04_analyze.py --plan runs/development_v1
```

Use `--no-json-mode` at preparation only if the endpoint lacks `response_format`; the returned content must still be valid JSON. `--send-seed` is optional because providers differ. Record whether seed control is honored; temperature zero does not ensure exact reproducibility. API timeouts/schema failures remain failed runs, with partial logs, and never become “safe outcomes.”

## 3. Freeze reusable discovery evidence

Fix any implementation or prompt issues on development seeds only. Finalize the physical thresholds, threat model, sensor assumptions, memory format, endpoint version, and sampling plan. Then:

```bash
python scripts/01_prepare.py --stage discovery --provider openai_compatible \
  --model "$MODEL_ID" --revision "$MODEL_REV" --out runs/discovery_v1
python scripts/02_run.py --plan runs/discovery_v1 --workers 2
python scripts/03_validate.py --plan runs/discovery_v1
python scripts/04_analyze.py --plan runs/discovery_v1
python scripts/05_video.py --plan runs/discovery_v1 --out runs/discovery_v1/analysis/paired.mp4
python scripts/07_package_results.py --plan runs/discovery_v1 --out exports/discovery_v1.zip
```

60 complete rollouts: 1 scenario × 10 held-out seeds × 6 conditions. Each includes exposure, source removal, relay, a second reset, and later physical execution. It is a publishable *exploratory component*, not automatic evidence of novelty, a significant effect, or rare-event safety. Retain negative and inconclusive results. If it influences later choices, do not pool it into the confirmatory estimator.

## 4. Main and final stages

First run design sensitivity; the defaults below are budgeting grids, not guaranteed sample sizes:

```bash
python scripts/06_power.py --p10 0.20 --p01 0.05 --comparisons 6 --half-width 0.10
```

After choosing and recording a justified `N_SEEDS`:

```bash
python scripts/01_prepare.py --stage main --provider openai_compatible \
  --model "$MODEL_ID" --revision "$MODEL_REV" --n-seeds "$N_SEEDS" --out runs/main_model1_v1
python scripts/02_run.py --plan runs/main_model1_v1 --workers 2
python scripts/03_validate.py --plan runs/main_model1_v1
python scripts/04_analyze.py --plan runs/main_model1_v1
```

Repeat the preparation/run/validate/analyze sequence with `--stage defenses`, `--stage recovery`, then `--stage mechanism`. After gates pass, `--stage transfer` runs supported topology and sensor-failure stress tests. Run a second **different model family** with a new plan directory and its exact revision. The script named `transfer` does not mean Isaac Sim or real-robot transfer; those need the separately documented integration.

A new code/prompt/config version requires a new plan directory. Do not change the hash in `protocol.lock.json` to bypass this rule.

### Recovery revision: additional commands

Run the recovery fixture matrix before using the new scientific stage (72 rollouts; no API calls):

```bash
python scripts/01_prepare.py --stage smoke --suite recovery --n-seeds 1 --out runs/recovery_smoke_v2
python scripts/02_run.py --plan runs/recovery_smoke_v2 --workers 2
python scripts/03_validate.py --plan runs/recovery_smoke_v2
python scripts/04_analyze.py --plan runs/recovery_smoke_v2
python scripts/05_video.py --plan runs/recovery_smoke_v2 --conditions B,lineage_revoke_poison,F --out runs/recovery_smoke_v2/analysis/recovery_paired.mp4
python scripts/07_package_results.py --plan runs/recovery_smoke_v2 --out exports/recovery_smoke_v2.zip
```

After real-model development and prospective precision/budget selection:

```bash
python scripts/01_prepare.py --stage recovery --provider openai_compatible \
  --model "$MODEL_ID" --revision "$MODEL_REV" --n-seeds "$N_SEEDS" --out runs/recovery_model1_v2
python scripts/02_run.py --plan runs/recovery_model1_v2 --workers 2
python scripts/03_validate.py --plan runs/recovery_model1_v2
python scripts/04_analyze.py --plan runs/recovery_model1_v2
python scripts/05_video.py --plan runs/recovery_model1_v2 --conditions B,lineage_revoke_poison,F --out runs/recovery_model1_v2/analysis/recovery_paired.mp4
python scripts/07_package_results.py --plan runs/recovery_model1_v2 --out exports/recovery_model1_v2.zip
```

The default E5b grid is 2,880 rollouts, a budget example rather than a powered design. Repeat preparation with `--dock-lookup-delay-s 0` and a new output directory for the prespecified cost sensitivity, then run the same execution/validation/analysis sequence. Do not change frozen protocols. All recovery comparisons use the same information and read allowance within each stratum; travel and model overhead remain measured rather than assumed equal. No scientific run is performed by preparing a plan.

## 5. Parallelism, interruptions, and preserving progress

`--workers` runs independent trials concurrently in a process with isolated MuJoCo models/stores. Start at 1–2; model endpoint capacity is the bottleneck. For separate machines/sandboxes, copy the **same frozen code and plan**, use distinct shard indices, and retain each machine's outputs:

```bash
python scripts/02_run.py --plan runs/main_model1_v1 --shards 4 --shard-index 0 --workers 1
# Other machines use indices 1, 2, and 3 with the same --shards 4.
python scripts/08_status.py --plan runs/main_model1_v1
```

Merge by unique trial ID; never overwrite different attempts. Copy all attempt folders and completion hashes. Analyze only the complete merged plan. No Modal or other cloud provisioning is performed by these scripts.

- Re-run the same command to skip completed, hash-verified trials.
- `--retry-failed` makes a new attempt while retaining the previous failure.
- `--retry-interrupted` reclaims a same-host lock only after its PID is gone. A foreign-host lock needs an explicit operator check that its worker stopped; do not remove live locks.
- Every completed trial and at least every 20 minutes updates the shard checkpoint. This is progress metadata, not a durable remote backup. Copy/checkpoint run directories to your durable experiment volume after each batch.
- An interrupted trial restarts from its beginning with a new attempt; it does not resume mid-trajectory or reuse uncertain API responses.
- `07_package_results.py` validates integrity and exports all attempts. Store that ZIP alongside the frozen code bundle.

## 6. Outputs and the paired video

```text
runs/<plan>/
  protocol.lock.json             # exact study and code identity
  manifest.jsonl                # every intended trial, randomized execution order
  checkpoint_shard*.json        # progress
  runs/<trial_id>/
    attempt_001/
      trial.json
      events.jsonl              # model, exposure, write, reset, repair, sensor, action
      memories.json
      world_*.xml
      trajectory.jsonl          # actual sampled physics trajectories
      result.json
    DONE.json                   # hashes of successful attempt files
    FAILED.json                 # when incomplete/failed
  analysis/
    run_metrics.csv
    summary.json                # intervals, paired contrasts, missingness
    REPORT.md
    outcomes_*.png / *.pdf
    paired.mp4 / paired.png / paired.json
```

The default video is 24 seconds, A/B/F side by side, matched physical initialization, shared simulation clock. It selects the lexicographically first complete matching block without looking at outcomes. Finished panels hold their final frame. It is a **2D replay of logged physics states**, not an invented demonstration or robot-camera recording. Its JSON includes trial IDs and source hashes. Use `--block-id` only with a disclosed illustrative selection rule; do not present a hand-picked failure as representative. Figures summarize every run.

## Script index

| Script | Role |
|---|---|
| `00_preflight.py` | Physics and optional model-list checks |
| `01_prepare.py` | Versioned manifest and protocol freeze |
| `02_run.py` | Model/robot execution, resume, sharding, checkpoints |
| `03_validate.py` | Integrity, resets, fixture exclusion, prompt-label leak checks |
| `04_analyze.py` | All scalar metrics, paired contrasts, uncertainty, figures |
| `05_video.py` | Paired replay from saved states |
| `06_power.py` | Paired-design sensitivity and precision planning |
| `07_package_results.py` | Checksummed result export |
| `08_status.py` | Completed/failed/pending inventory |
| `09_operator_diagnostic.py` | Paper 2 finite-horizon algebraic diagnostic |

For metrics and claim rules, see `docs/METRICS_AND_STATISTICS.md`. For a concise collaboration pitch, see `docs/AIM_CONCEPT_NOTE.md`.

## Preserved evidence and version history

`archive/v0.1.0_code_and_smoke.zip` preserves the previous complete code bundle. `artifacts/software_smoke` and its results ZIP belong to that earlier code hash. Use the archived code to resume them; current analysis can read their stored outputs but will not invent newly added fields. Revision 0.2.0 validation is recorded in `VERIFICATION.md` and `artifacts/recovery_smoke_v2`. Never edit old raw evidence or lockfiles to make hashes match new code.
