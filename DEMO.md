# 30-second judge walkthrough

**The ghost:** a task can disappear from the interface while its underlying execution state is uncertain.

**The experiment:** GhostQueue reads four synthetic event descriptions and suggests `retry`, `review`, `quarantine`, or `complete`. A local TF-IDF + logistic-regression classifier proposes a label; deterministic rules override unsafe suggestions. It does not control a real queue or execute actions.

**Try it in a fresh clone:**

```bash
python -m pip install -r requirements-train.txt
python train.py
python -m ghostqueue examples/events.json
```

**Look for these two invariants in the JSONL output:**

- Event `job-102` has `external_side_effect: true` and must be recommended for **review**.
- Event `job-103` has `trusted: false` and must be recommended for **quarantine**.
- Every event must report `executed_actions: 0`.

**What actually ran?** [A successful GitHub Actions run](https://github.com/hippoley/ghostqueue-week4/actions/runs/41021522073) independently performed model training, unit tests, evaluation, and the CLI smoke test on GitHub-hosted infrastructure.

**What did we learn?** On 24 synthetic holdout examples, the AI classifier scored 21/24 (87.5%), while a keyword baseline scored 23/24 (95.83%). The baseline won. This is a small synthetic experiment, not a real-world performance claim.

---

# GhostQueue — reproducible demo

## Quick start

```bash
python -m pip install -r requirements-train.txt
python train.py
python -m unittest discover -s tests -v
python evaluate.py
python -m ghostqueue examples/events.json
```

Run the commands from the repository root. Training generates `ghostqueue/weights.json`; the CLI reads the local weights. No paid API or external model service is needed.

## What to watch for

The example events include an ordinary timeout, a payment-like event requiring human review, an untrusted instruction, and a completed job. Each output is JSON with a proposed state, a reason, model predictions, and `executed_actions: 0`. The second event has `external_side_effect: true` and must be reviewed. The third has `trusted: false` and must be quarantined regardless of the model prediction.

## Verified public execution

[GitHub Actions success, commit 752bc0c](https://github.com/hippoley/ghostqueue-week4/actions/runs/41021522073). Its workflow regenerates the model, runs unit tests, checks the 24-case synthetic evaluation against the documented 21/24 vs 23/24 figures, and executes the CLI example. The workflow uploads model weights and evaluation JSON as build artifacts.

This is an automated command-line demo, **not** a hosted web app or a video recording. For a DEV submission requiring a video or deployed URL, add an actual recording before publishing; do not describe this workflow as a video.

## Honest limitations

The project does not connect to a real queue or execute retries. The training and holdout data are small, synthetic, and author-created. The keyword baseline performs better than the learned model. Policy overrides are a guardrail for this toy experiment, not a proof of robust security.
