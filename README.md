# GhostQueue — The AI Tasks That Refuse to Die

[![GhostQueue reproducibility](https://github.com/hippoley/ghostqueue-week4/actions/workflows/ci.yml/badge.svg)](https://github.com/hippoley/ghostqueue-week4/actions/workflows/ci.yml)

**GhostQueue** is a local-first, open-source experiment in **advisory triage for interrupted AI jobs**. A job can vanish from a UI while retries, delayed acknowledgments, and uncertain execution states remain. GhostQueue classifies event descriptions into `retry`, `review`, `quarantine`, or `complete`, with deterministic safety overrides. **It never performs the suggested action.**

## Reproduce from a fresh clone

Requires Python 3.11+ and internet access **only to install the open-source training dependencies**. No inference API key or remote model endpoint is used.

```bash
git clone https://github.com/hippoley/ghostqueue-week4.git
cd ghostqueue-week4
python -m pip install -r requirements-train.txt
python train.py
python -m unittest discover -s tests -v
python evaluate.py
python -m ghostqueue examples/events.json
```

The training step creates `ghostqueue/weights.json` locally. This generated file is also available as an artifact from the [successful GitHub Actions run](https://github.com/hippoley/ghostqueue-week4/actions/runs/41021522073). After training, inference uses Python's standard library only.

## Interactive local Web demo

The browser UI calls the **real Python** `ghostqueue.core.triage()` through a localhost-only HTTP server; no outcomes are hardcoded in JavaScript.

After installing dependencies and generating weights with `python train.py`:

```bash
python web_demo.py
```

Open **http://127.0.0.1:8765**. Choose one of four example events, edit its description and flags, and click **Analyze event**. The response displays the model prediction, confidence, deterministic override reason, suggested state, and `executed_actions: 0`.

This is a **local demo**, not a publicly hosted URL or production task queue. The server binds to `127.0.0.1` only. It serves a fixed set of static assets, validates JSON input using the existing core logic, and does not execute suggested actions.

## Demo and evidence

- [Sample input events](examples/events.json)
- [Actual successful CI run](https://github.com/hippoley/ghostqueue-week4/actions/runs/41021522073)
- [CI workflow](.github/workflows/ci.yml) regenerates weights, runs tests, evaluates the synthetic holdout, exercises the CLI, and uploads artifacts
- [Demo instructions](DEMO.md)

The evaluation is deliberately small and synthetic: 32 author-created training examples and 24 separate synthetic holdout examples. The reported model result is **21/24 (87.5%)**, while the keyword baseline is **23/24 (95.83%)**; all **5/5 policy checks** pass. **The baseline wins.** These are not production metrics or a security certification. The holdout was authored for this prototype; it is not an independent benchmark.

## Safety boundaries

- `trusted: false` forces `quarantine` before any other policy.
- `external_side_effect: true` or `requires_approval: true` forces `review` unless the event is untrusted.
- Uncertain model predictions are routed to `review`.
- Inputs are validated: non-empty messages, strict boolean flags, valid nonblank IDs, and length limits.
- All outputs are **suggestions only**; `executed_actions` is always `0`.

No live queue integration, actual retries, real-world event data, or production guarantees are claimed.

## License and submission

MIT licensed. Created for the Hacktoberfest Open-Source AI Challenge Week 4: Ghost in the Machine. [Published DEV submission](https://dev.to/hippoley/this-is-a-submission-for-the-hacktoberfest-open-source-ai-challenge-week-4-ghost-in-the-machine-4h5n).
