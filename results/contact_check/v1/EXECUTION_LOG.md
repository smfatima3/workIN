# Execution log

- 2026-11-05. Local date in Asia/Karachi. Inspected the supplied ZIP and its 24 calibration cells. Preserved the original archive before execution.
- Executed the supplied calibration script independently and the instrumented runner with the same geometry, motion, release timings and timestep. Both reproduced all 24 existing outcomes.
- Added contact-step records and per-trial initial states, scene XML and trajectories. Confirmed 12 identical physical initialization and geometry pairs.
- Generated four eight-second paired videos, each covering all three supplied offsets. Inspected all four previews. Verified 96 frames at 12 fps and decoded the final frames.
- 2026-11-05T16:54:15Z. During post-run validation, clock read confirmed the local date as 5 November, 21:54 Asia/Karachi. The executable audit passed and verified both historical Qwen event rows verbatim. Exact execution start/end times were not captured.
- All 24 trials are scripted calibration. Model calls 0. GPU usage 0. Original model results are preserved. The paused C sensitivity remains separate from the moving C miss.
- This run uses positive normal force for the specified moving/person pair. Contacts with the floor and desk are excluded. Task completion, near misses and injury remain unscored.
