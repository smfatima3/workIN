# Reproduce the handoff

Extract each main evidence ZIP into a directory named contact_VERSION_SCENARIO beneath a common raw root. For example, v5_B.zip extracts into raw/contact_v5_B. Use V4 for Qwen A and moving C, V5 for both B and paused C, V6 for Phi A and V7 for Phi moving C. The script selects these recorded configurations and audits all valid physical commands.

From the repository root run the following command with the environment dependencies recorded in each evidence archive.

```sh
python scripts/contact_causal_handoff.py --raw-root raw --out handoff
```

This sends no model requests. It validates checkpoints, checks recorded contacts, sequentially replays physics and creates the numerical summaries and fixed paired videos. Existing videos in the output folder are reused. Use a fresh output folder when regenerating media. The narrative report explains the development failures and statistical limits.

Raw data remain immutable. MuJoCo last-XML export raced in some earlier threaded manipulation runs. The separate sequential replay audit retains those original mismatches and provides reconstructed hashes. Frames match within 1 micrometre, contact times within 1 nanosecond, and normal forces within 1e-5 N plus relative 1e-6.
