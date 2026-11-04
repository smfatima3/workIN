# F1 clean rule comprehension

Qwen3-8B at revision `b968826d9c46dd6066d109eabc6255188de91218` completed 96 actual-model decisions: 72 screening probes plus 24 untouched-paraphrase checks. Each set crosses two safety rules, three observation states, and four wordings. No physical safety or generalization claim follows from this small engineering screen.

| Configuration | Legal actions | Belief/observation consistency | Unsupported permission on unknown | Gate |
|---|---:|---:|---:|---|
| Original interface, non-thinking | 8/24 | 17/24 | 7 | Fail |
| Explicit route semantics, non-thinking | 23/24 | 24/24 | 0 | Fail |
| Explicit route semantics, thinking | 24/24 | 24/24 | 0 | Pass |
| Selected thinking mode, fresh wording check | 24/24 | 24/24 | 0 | Pass |

The explicit non-thinking failure chose slow travel through a restricted exclusion zone. Thinking mode passed the frozen clean criteria and was selected without exposure to poisoning outcomes. Its final-answer parser separates the thinking segment and rejects truncated output. No malformed-response errors occurred in the completed probe set.

The check uses new wording, with the same route/rule parameters. This is a comprehension screen, not independent scene transfer. The original E1 failure remains preserved. F1 used an A10 GPU; subsequent stages use an H100 and record that hardware difference.

The server's default immutable input-prefix KV caching was active in this diagnostic; there was no shared conversational history or sampled-answer cache. It is explicitly disabled for subsequent revised runs.

Raw evidence: `F1_v1.zip`, including source, requests, raw responses, protocol, checksums and summary. This result establishes readiness to test useful memory; it does not establish that memory is used or that false claims propagate.
