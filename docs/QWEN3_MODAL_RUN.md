# Qwen3-8B real-model execution

Requested 4 November 2026 (Asia/Karachi). This run uses the user's explicitly
authorized Modal account. The earlier artifact-only provisioning restriction in
the imported package is superseded by that request. No OpenAI-hosted model or
OpenAI API credentials are used. `openai_compatible` names the HTTP wire format;
the endpoint is vLLM on `127.0.0.1` inside the Modal container.

## Frozen initial configuration

- Model: `Qwen/Qwen3-8B`.
- Hugging Face revision: `b968826d9c46dd6066d109eabc6255188de91218`, resolved from
  the model repository API before execution; tokenizer uses the same revision.
- vLLM image: `vllm/vllm-openai:v0.10.2`; exact installed environment and GPU
  description are recorded in each run. BF16 weights, no quantization.
- One A10G; CPU MuJoCo simulation; two isolated trial workers; no remote retries;
  two-hour function timeout. No always-on endpoint or minimum warm replicas.
- Non-thinking mode, temperature 0.7, top-p 0.8, top-k 20, output limit 300,
  JSON-object mode, explicit request seeds. These are Qwen's recommended
  non-thinking sampling settings. Seed control is requested, not a claim of
  bitwise determinism.
- E1: 60 intended development rollouts, seeds 100–109, exclusion/restricted,
  A–F, one later task per rollout. The 6,000-call cap is an upper bound.
- E2 is a separate invocation after development review, with seeds 1000–1009.
  No main/recovery/transfer grid is launched automatically.

## Execution and preservation

Authenticate with Modal's CLI or environment variables outside the repository.
Do not commit the token or place it in evidence folders. Launch from repo root:

```sh
modal run --detach scripts/modal_qwen3.py --stage development --version v1
```

The job first runs tests, physics preflight and the 72-rollout scripted recovery
suite. Those fixture outputs are separated from real-model output. Any gate
failure stops the run. It then freezes the real-model manifest, runs all cells,
validates, analyzes, produces the preselected paired replay and exports results.
Schema/HTTP failures remain failures; there is no fixture fallback.

Evidence Volume: `workin-memory-safety-evidence`.
Weight cache Volume: `workin-qwen3-hf-cache`.
Evidence path: `/qwen3_8b_development_v1/` (manifest/results under `plan/`).
The Volume is committed after each completed trial and each command. Full source,
environment, GPU details, server log and timestamped execution log are retained.
The result ZIP contains checksums and all plan attempts. Export the parent run
directory too, to retain infrastructure logs/source alongside the result ZIP.

```sh
modal volume get workin-memory-safety-evidence /qwen3_8b_development_v1 ./exports/development
```

Use a new version for code/configuration changes. This runner does not silently
reclaim interrupted workers, discard failed attempts, or alter frozen locks.
Model sampling changes require a new plan. No dollar cost is asserted without
charged provider usage; model tokens and measured elapsed time are retained.

## Imported package provenance

Original ZIP SHA-256:
`b9c021e4e65b9a06f6516ad75eb98d3dddbebdb2db1ec25f4d8e932b388ab115`.
All 902 entries in its `PACKAGE_CHECKSUMS.json` matched before modifications.
That file describes the original package, not the added Modal integration.
Original `archive/` and `artifacts/` are preserved unchanged. The reported
35 tests and 72 rollouts in `VERIFICATION.md` are historical software evidence.
Current real-model status belongs in the new run logs and result note.

Sources: [Qwen model card](https://huggingface.co/Qwen/Qwen3-8B),
[Modal vLLM example](https://modal.com/docs/examples/vllm_throughput).
