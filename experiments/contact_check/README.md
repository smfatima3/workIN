# Reproduce the contact calibration

The supplied source and existing results are preserved in `results/contact_check/v1/supplied_package.zip`. The instrumented runner retains its geometry, timestep, motion and release rules. It adds per-trial XML, matched initial-state hashes, named contact events and trajectories. The audit compares all 24 outcomes and the placement trace to the supplied package and verifies its two historical event rows against the repository.

From the repository root, use Python 3.13 and run the following commands.

```sh
python -m pip install -r experiments/contact_check/requirements.txt
python experiments/contact_check/calibrate.py --out contact_check_run
```

Copy `contact_check/original_qwen_event_rows.csv` from the supplied ZIP into `contact_check_run`, preserving its bytes. Then generate all scenario videos and audit the run.

```sh
python experiments/contact_check/render.py --root contact_check_run
python experiments/contact_check/audit.py --root contact_check_run --supplied results/contact_check/v1/supplied_package.zip --qwen-csv results/foundation/F456_v1/all_runs.csv
```

[Recorded results and videos](../../results/contact_check/v1/run/REPORT.md)
