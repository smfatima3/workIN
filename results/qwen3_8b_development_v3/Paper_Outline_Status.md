# Paper outline after the Qwen3-8B development cohort

Working scope: controlled measurement of robot-memory recovery. No broad recovery-method paper is supported yet. Development results must remain separate from future exploratory discovery and confirmatory evidence.

1. Problem and protocol — **SUPPORTED (implementation)**: explicit source removal, two session resets, private stores, matched physical states, independent MuJoCo safety evaluator, and sensor-budget controls exist and pass software validation. This does not establish scientific novelty or hardware validity.
2. Model and environment — **SUPPORTED**: Qwen3-8B at the recorded immutable revision executed 60 development rollouts on Modal; all 220 responses passed the benchmark's JSON/schema checks. Exact runtime/source and response evidence are retained.
3. Development behavior — **EXPLORATORY / DEVELOPMENT ONLY**: all peer claims were rejected; all raw action decisions selected direct travel; observed A–D violations were 10/10 per condition. This documents this particular configuration, not a universal property of Qwen3-8B.
4. Persistent poisoning mechanism — **UNSUPPORTED**: no false or correct zone memories were stored or relayed. B−A was zero. No claim that source revocation left a behaviorally consequential poisoned descendant is justified here.
5. Verification behavior — **EXPLORATORY / DEVELOPMENT ONLY**: the existing code forced detours following restricted observations, producing 0/10 violations per E/F condition at an inspection/time cost. It is a transparent enforced baseline; model action choices remained unsafe after observation. Do not describe this as model recovery, superiority over published methods, or a novel defense.
6. Frozen discovery — **NOT RUN**: G1 safe-observation/memory-use gate failed. Seeds 1000–1009 remain untouched. Preserve the current negative result and perform balanced development diagnostics without requiring poison adoption.
7. Main, recovery stress, mechanism, and transfer — **NOT RUN WITH A REAL MODEL**: no confirmatory sample size, recovery ranking, metadata/read-budget interaction, second model family, or independent platform transfer is established. The scripted recovery smoke is software validation only.
8. Prior-work comparison and generality — **NOT RUN / UNSUPPORTED**: no faithful published-method comparison, scene generalization, robot hardware safety, injury reduction, deployment benefit, or firstness claim follows from E1.

Future results sections should cite immutable run IDs, retain all failed attempts and negative outcomes, report matched clean utility, and clearly distinguish interventions performed by code from decisions made by the model.
