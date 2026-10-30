# GhostQueue — Ghost in the Machine

Offline, open-weight AI prototype for **advisory** triage of interrupted jobs. It never executes retries or other external actions.

**Publication status:** This GitHub repository is being populated from the verified local GhostQueue Git Bundle. Until the original source, trained weights, and evaluation artifacts are all uploaded and checked, **this is not a complete reproducible release**.

The verified local prototype uses a 4-class TF-IDF + logistic regression classifier, with dependency-free Python inference and hard-coded policy overrides. On 24 author-created synthetic holdout examples, it scored **21/24 (87.5%)**, below a keyword baseline at **23/24 (95.8%)**. These figures are local evidence, not yet independently reproducible from this remote repository.

**Safety design:** untrusted input => quarantine; any external side effect or required approval => review; model output is advice only. No real queue connector, external actions, production performance, or validated security guarantee.

This is a Hacktoberfest Week 4 candidate, **not yet a DEV submission**. See the original local Git Bundle for complete code and history.

MIT license in the source bundle; original project started during Oct 26–31, 2026.
