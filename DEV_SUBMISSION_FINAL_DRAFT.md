*This is a submission for the [Hacktoberfest Open-Source AI Challenge Week 4: Ghost in the Machine](https://dev.to/challenges/hacktoberfest-week4-2026-10-26).*

## What I Built

**What if an AI job disappears from your screen but never actually stops?**

GhostQueue is a local-first, open-source experiment in triaging interrupted or ambiguous AI tasks. A cancellation can look complete while a retry, delayed acknowledgment, or uncertain execution state remains. That is my interpretation of the ghost in the machine: unfinished work haunting a supposedly quiet interface.

Given an event description, GhostQueue proposes one of four states: **retry, review, quarantine, or complete**. The ML prediction is advisory. Deterministic rules force untrusted input into quarantine and external side effects or approval-dependent actions into review. The prototype never actually retries or executes anything.

## Demo

**Reproducible CLI demo:** [instructions and scenarios](https://github.com/hippoley/ghostqueue-week4/blob/main/DEMO.md)

**Successful public CI execution:** [GitHub Actions run](https://github.com/hippoley/ghostqueue-week4/actions/runs/41021522073)

The public workflow trains the model, runs the tests, evaluates the 24-case synthetic holdout, and invokes the CLI with example events. This is an automated CLI demonstration, not a deployed website or video.

## Code

**GitHub repository:** https://github.com/hippoley/ghostqueue-week4

Clone and reproduce:

```bash
git clone https://github.com/hippoley/ghostqueue-week4.git
cd ghostqueue-week4
python -m pip install -r requirements-train.txt
python train.py
python -m unittest discover -s tests -v
python evaluate.py
python -m ghostqueue examples/events.json
```

## How I Built It

I used an open-source, local TF-IDF plus logistic regression classifier trained with scikit-learn on 32 synthetic event descriptions. The training script exports the learned parameters to JSON. Inference uses only the Python standard library; it needs no hosted model endpoint or proprietary API.

The classifier has four possible labels, but it does not have permission to perform the corresponding actions. Input validation rejects malformed event objects, invalid boolean flags, blank IDs, and oversized messages. Policy overrides protect the decision boundary: untrusted events are quarantined, and events with external side effects or approval requirements are sent for review.

The evaluation is intentionally transparent. On 24 separate, author-created synthetic holdout cases, the ML model scored **21/24 (87.5%)**. A simple keyword baseline scored **23/24 (95.83%)**. All five policy checks passed in the verified CI run.

**The baseline beat the AI model.** I am reporting that result because the point of an open experiment is to discover where AI helps—and where it does not.

## Why Does Open Innovation Matter?

A closed API could produce a label, but it would not make this particular experiment as easy to inspect, rerun, or challenge. The training examples, training code, evaluation logic, policy checks, and inference path are public. Anyone can regenerate the local model and test the same scenarios without an inference service or API key.

Open development also makes an uncomfortable result visible: on this small synthetic dataset, the simpler baseline wins. That finding is a useful design constraint, not a marketing problem. When a system may eventually control real tools, probabilistic interpretation should not silently become authority to act.

This prototype does not establish production reliability, real-world accuracy, or robust prompt-injection defense. It is a reproducible starting point for examining those questions.

## The Spirit of It

The scariest software ghost is not a jump scare. It is the task that looks cancelled but might still be doing something.

GhostQueue asks what should happen before such a task is allowed to return from the dead. Its answer is modest: make the state visible, compare the model against simple rules, and keep the final decision behind an explicit boundary.

That is the kind of ghost I want an open-source community to investigate together.

---

**Submission note:** This file is a draft, not proof of DEV publication. Confirm any challenge-required tags and add a video or deployed demo if required by the challenge page before publishing.
