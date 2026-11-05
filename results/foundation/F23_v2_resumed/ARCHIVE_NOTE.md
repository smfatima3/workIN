# Export correction

The scientific cohort completed all 72 continuations and analysis passed. The
remote ZIP export then failed because the copied resume harness had a pre-1980
timestamp. The original `evidence.zip` is retained as the partial export, not the
complete handoff. The full persistent directory was downloaded and all 675 entries
in its checksum manifest matched. `evidence_repacked.zip` is the complete local
repack, including that original manifest. No model calls were rerun for this fix.
The wrapper now accepts old timestamps during ZIP export.
