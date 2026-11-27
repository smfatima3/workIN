# Robot memory after the reporting source disconnects

The same robot begins a new task from the same simulated physical state. Retained memory preserves an observation that has become stale. Targeted correction supplies the current value. A matched sham edit changes metadata and preserves the stale value. A separately acquired accurate report serves as the clean comparison.

**All planned simulation experiments are complete.** The conveyor includes 64 layouts for each of three frozen local Ollama checkpoints, 192 model–layout runs, 768 arm outcomes and 1,098 distinct recorded responses. The repeated branches reuse identical requests within the same scene when appropriate. There are no missing conveyor outcomes.

| Simulated outcome | Planner | Eligible pairs | Retained | Corrected | Retained-only / corrected-only | Difference, pp (95% paired CI) |
| --- | --- | ---: | ---: | ---: | ---: | --- |
| Glass spill | Qwen3-14B | 48 | 34 | 9 | 25 / 0 | +52.1 (26.6 to 68.5) |
| Conveyor floor contact | Qwen3-14B | 64 | 22 | 0 | 22 / 0 | +34.4 (14.9 to 49.1) |
| Conveyor floor contact | Qwen3-8B | 64 | 23 | 2 | 22 / 1 | +32.8 (12.0 to 49.0) |
| Moving-tray overload | Qwen3-14B | 48 | 16 | 34 | 1 / 19 | −37.5 (−56.7 to −11.5) |

The table shows selected matched comparisons. The [complete primary table](../../project/evidence/paired_primary.csv) includes every planner and the null results. The interval is for the percentage-point difference between retained and corrected arms, conditional on naturally storing the stale reading.

On the conveyor, Qwen3-14B also dropped 25/64 parcels under the sham edit. Phi-4 skipped all 64 old-speed reports, inspected the actual speed and completed all 64 deliveries in each arm. Its natural-retainer contrast is unestimable. On the glass task Phi-4 had stored all 48 position reports. Differences here are between tested checkpoints and tasks. The experiments do not isolate parameter count or establish real-world injury.

## Materials

- [Project page with nine replays](https://smfatima3.github.io/workIN/) and [video provenance manifest](../../project/media/manifest.json).
- [Review report (PDF)](../../project/evidence/Review_Report.pdf), [editable results summary](../../project/evidence/Results_for_manuscript.md) and [experiment inventory](../../project/evidence/study_inventory.csv).
- [Full results archive](https://github.com/smfatima3/workIN/releases/download/robot-memory-safety-2026-11-27/Robot_Memory_Safety_All_Results.zip), including the intact final study archive, historical results, source decisions, protocols, incomplete historical attempts and simulation videos. The ZIP includes a SHA-256 inventory.
- [Standalone Colab notebook](https://github.com/smfatima3/workIN/releases/download/robot-memory-safety-2026-11-27/RSS_Robot_Memory_Review.ipynb) and [release checksums](https://github.com/smfatima3/workIN/releases/download/robot-memory-safety-2026-11-27/SHA256SUMS.txt).

The glass and bath tasks are PhysHarm-inspired adaptations using idealized liquid models. The trays use Godot and the conveyor uses MuJoCo. Floor contact, escaped liquid and exceeding a tray rating are separate measured outcomes. The earlier Scenario B pedestrian audit observed zero contacts in 479 valid runs. The archive labels scripted calibrations, simulations with live model decisions and modeled network timing separately.
