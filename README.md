# PQC Experiment

Hands-on post-quantum measurement: benchmarks, key and signature size comparisons, known-answer tests, and runnable experiments on constrained hardware.

A pack source for `modular-ai-core`. Source id: `pqc-experiment`. Pack id:
`pqc_experiment`. Namespaced by the core as `pqc-experiment__pqc_experiment`.

## Layout

```
registry/index.json
packs/pqc_experiment/pack.json
packs/pqc_experiment/prompt.md
packs/pqc_experiment/examples.md
packs/pqc_experiment/knowledge/*.md
packs/pqc_experiment/vectors.json
build_vectors.py
```

## Adding this source to the core

In `~/modular-ai-core/sources.json`:

```json
{"id": "pqc-experiment", "repo": "yatakitumbi2025-del/pqc-experiment@main",
  "enabled": true, "allow_tools": false}
```

This pack's experiments are meant to be executed, so the core may grant it `code_runner` by setting `allow_tools: true` for this source. That is a deliberate, per-source decision made in the core's `sources.json` — this repo does not and cannot grant it.

## Rebuilding vectors after editing knowledge

```bash
cd ~/pqc-experiment
python build_vectors.py
git add . && git commit -m "Update knowledge" && git push
cd ~/modular-ai-core && rm -f routing_cache.json && python core.py --refresh
```

## Editing the router description

`routing.description_for_router` in `pack.json` must stay **task-shaped** — a
list of real questions, not abstract prose. This pack shares vocabulary with the
other two PQC packs, so any edit risks stealing or losing traffic. Score before
you commit:

```bash
cd ~ && python score_pqc.py
```

## Trust

The core decides which sources may use tools. A pack in this repo declares
`"tools": []` and always will. If a future edit adds a tool name to `pack.json`,
the core should ignore it.
