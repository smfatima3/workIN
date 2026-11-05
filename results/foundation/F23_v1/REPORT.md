# F2/F3 v1: completed development evidence

Qwen3-8B, pinned revision `b968826d9c46dd6066d109eabc6255188de91218`, BF16,
thinking mode, vLLM 0.10.2 on one Modal H100. No OpenAI-hosted model calls.

All 24 acquisition parents and 72 intended continuations completed. Hash,
checkpoint, session and fixture checks passed. All continuations safely completed
their simulated delivery; no executed zone violations occurred.

F2 failed the prospective useful-memory gate. The model correctly stored 19/24
locally observed claims (threshold 20), and retaining memory reduced inspection
count or mission time in only 3/12 paired parents (threshold 6). Retained and deleted
branches each used 22 sign reads in total. Equal totals do not exclude differences
within particular pairs. Five known observations were correctly classified but the
model voluntarily declined storage.

F3's 12 correct-memory branches safely completed. None of the 48 controlled
correct/false/absent/irrelevant continuations violated the zone rule. This is a
negative controlled diagnostic, not evidence that naturally acquired misinformation
is harmless. There are only three independent blocks per rule/context stratum;
the conservative familywise violation-difference intervals span [-1, 1].

There were 24 acquisition calls and 275 continuation calls. Continuations used
124,275 input and 203,145 output tokens. Actual billed cost is not estimated.

The retrieval interface removed the origin of local observations, leaving them
indistinguishable from uncertain notes. Development v2 preserves truthful evidence
type and unchanged rule epoch, and clarifies continuity equally across all branches.
It uses fresh seeds 21100–21111 and 22100–22111. Storage, sharing, reliance and
inspection remain model choices. v1 is retained separately and is never pooled
with v2. v1 used four workers and default immutable prefix caching; v2 uses sixteen
workers and disables prefix caching. Hardware/software details and exact source
are included in each evidence archive.

Evidence: `F23_v1.zip`, including raw requests/responses, trajectories, manifests,
protocol lock, memory interventions, source, environment and checksum manifest.
This planar MuJoCo experiment establishes neither hardware safety nor injury risk.
