# GhostQueue publication and verification gate — 2026-10-30

## Verified locally

- [x] Original source recovered from the local Git Bundle.
- [x] Hardened `ghostqueue/core.py` event validation: object, required nonempty message, 10,000-character limit, strict booleans, string/integer event ID.
- [x] CLI now returns exit code 2 on invalid event data instead of producing misleading predictions.
- [x] 15/15 local unit tests pass (6 original + 9 validation tests).
- [x] New complete-history Git Bundle created at local commit `ccbff8a`.

## Required before publishing the DEV entry

- [ ] Push the hardened local Git history and **all** original source/weights/evaluation files to this public repository.
- [ ] Reconcile this repository's pre-existing documentation commits; do **not** force-push over them without reviewing.
- [ ] Verify CI passes on the resulting public `main` commit.
- [ ] Run a clean-clone CLI demo and include a public demo or video.
- [ ] Publish the English DEV entry with the required competition tags.
- [ ] Verify the public DEV submission URL.

**This public repository is still an incomplete mirror.** The 15/15 test result is from the local source bundle, not from GitHub Actions. Do not imply a complete public release or successful contest submission until verified.
