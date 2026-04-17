# Changelog

All notable changes to this skill will be documented in this file.

The format is based on Keep a Changelog and this project uses Semantic Versioning.

## [Unreleased]

### Added

- Added post-push GitHub Actions monitoring to the runtime skill contract, including corrective action guidance for failed workflow runs.
- Added a first-class no-repository path that stops early and proposes GitHub repository creation details.
- Added repository bootstrap heuristics for visibility, naming, descriptions, and starter topics.

### Changed

- Updated the README, workflow reference, output contract, and evaluation prompts so release success now requires relevant GitHub Actions checks to pass after push.
- Added top-level README badges for version, status, category, and license to match the packaging style used in other skill repositories.

### Fixed

### Removed

## [0.2.0] - 2026-04-17

### Added

- Added an explicit memory model and stronger execution and output contracts to `SKILL.md`.
- Added `references/output-contract.md` for stricter downstream reporting behavior.
- Added automated tests for `scripts/release_probe.py`.
- Added evaluation prompts in `evals/evals.json`.
- Added `.gitignore` for generated Python artifacts and local test noise.

### Changed

- Rewrote the README for clearer responsibilities, architecture boundaries, testing, and publishing guidance.
- Expanded `scripts/release_probe.py` with changelog parsing, status summaries, version conflict detection, and strict mode.
- Tightened the skill description, guardrails, examples, and troubleshooting guidance.

## [0.1.0] - 2026-04-17

### Added

- Initial release of `release-manager-skill`.
- Core workflow for GitHub release verification, changelog gating, selective staging, semantic versioning, and forward prep.
- Bundled references for release workflow, version file discovery, and failure handling.
- Bundled `release_probe.py` helper for deterministic repository inspection.
