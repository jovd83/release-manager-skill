# Changelog

All notable changes to this skill will be documented in this file.

The format is based on Keep a Changelog and this project uses Semantic Versioning.

## [0.3.0] - 2026-09-28

### Added
- Companion agents that run this workflow in an isolated context and stop before every push, tag or GitHub release: `agents/claude-code/release-manager.md` (Claude Code, preloads the skill) and `agents/codex/release-manager.toml` (Codex custom agent).

### Changed
- Invoke-only: `disable-model-invocation: true` for Claude Code and `allow_implicit_invocation: false` for Codex. The skill commits and pushes, so it runs when asked, through the agents or `/release-manager-skill`.
- `metadata` carries author and version. The README version badge is realigned (it said 0.2.0), and the optional-integrations list points at the agent's own memory instead of the retired shared-memory skill.

## [0.2.1] - 2026-04-30

### Changed
- Trim `SKILL.md` frontmatter to fit the 1000-character dispatcher limit (description trim, migrate non-dispatcher fields to body).

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
