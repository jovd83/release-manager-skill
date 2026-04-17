# GitHub Release Manager Agent Skill

[![version](https://img.shields.io/badge/version-0.2.0-blue)](CHANGELOG.md)
[![status](https://img.shields.io/badge/status-stable--beta-f0ad4e)](SKILL.md)
[![category](https://img.shields.io/badge/category-release--management-0a7ea4)](SKILL.md)
[![license](https://img.shields.io/badge/license-MIT-green)](LICENSE)
[![Buy Me a Coffee](https://img.shields.io/badge/Buy%20Me%20a%20Coffee-ffdd00?style=flat&logo=buy-me-a-coffee&logoColor=black)](https://buymeacoffee.com/jovd83)
[![Validate Skill](https://github.com/jovd83/release-manager-skill/actions/workflows/validate.yml/badge.svg)](https://github.com/jovd83/release-manager-skill/actions/workflows/validate.yml)

`release-manager-skill` is an Agent Skills-compatible package for disciplined GitHub release preparation in repositories that use semantic versioning and a human-maintained `CHANGELOG.md`.

The skill is designed for agents that need to validate release readiness, keep changelog coverage honest, choose the correct semver bump, and leave the repository ready for the next development cycle without mixing unrelated work into history.

## Responsibilities

The skill is responsible for:

- verifying that the local checkout matches an expected GitHub repository
- stopping early when no GitHub repository exists yet and proposing how to create one
- checking branch and working-tree safety before release operations
- treating `CHANGELOG.md` as a release gate
- helping identify the correct semantic version bump
- monitoring GitHub Actions after push and driving failed runs to resolution when safe and in scope
- guiding a clean two-commit release pattern:
  - release commit
  - forward-prep commit for the next `Unreleased` cycle

The skill is not responsible for:

- publishing GitHub Releases or tags by default
- performing broad feature work or refactoring
- managing cross-repository release trains
- embedding shared-memory infrastructure inside the skill package

## Why it exists

Release workflows fail in subtle, expensive ways:

- the wrong repository or remote is used
- a detached `HEAD` is overlooked
- meaningful changes are not reflected in the changelog
- version files drift out of sync
- release commits and forward-prep changes get mixed together

This repository turns that fragile flow into a repeatable, auditable skill that another agent can pick up and use reliably.

It also handles the earlier bootstrap case cleanly: if the project is not on GitHub yet, the skill should stop and help the user define the repository they need before any release process begins.

For that bootstrap path, the skill now includes concrete heuristics for:

- choosing `private` vs `public`
- naming repositories by project type such as service, API, CLI, frontend, or agent skill
- drafting a concise repository description
- selecting sensible starter topics

## Quick invoke

```text
Use $release-manager-skill for owner/repo. Verify that this checkout matches the target GitHub repository, confirm CHANGELOG.md fully covers the pending release, create and push the release commit, then prepare the next Unreleased section.
```

## How the skill works

1. Verify repository identity and working state.
2. If no GitHub repository exists yet, stop and propose repository creation details.
3. Validate `CHANGELOG.md` against the actual change scope.
4. Stop and propose missing changelog entries when coverage is incomplete.
5. Determine the correct semantic version bump.
6. Create and push the release commit.
7. Monitor GitHub Actions for the pushed commit and correct failures when safe and in scope.
8. Prepare the next development iteration with a separate forward-prep commit.
9. Monitor GitHub Actions again after the forward-prep push.

## Repository layout

```text
.
|-- SKILL.md
|-- agents/
|   `-- openai.yaml
|-- assets/
|-- evals/
|-- references/
|-- scripts/
|-- tests/
|-- .gitignore
|-- CHANGELOG.md
|-- LICENSE
`-- README.md
```

## Core files

- `SKILL.md`
  Runtime instructions, guardrails, contracts, and examples.
- `agents/openai.yaml`
  UI metadata for compatible runtimes.
- `scripts/release_probe.py`
  Deterministic helper for repository inspection and machine-readable preflight data.
- `references/`
  Supporting guidance for workflow details, repo bootstrap heuristics, output contract, version-file selection, and failure handling.
- `assets/`
  Reusable changelog scaffolding.
- `tests/test_release_probe.py`
  Automated tests for the probe helper.
- `evals/evals.json`
  Forward-test prompts and expected behaviors for manual or harness-driven evaluation.

## Memory architecture

This skill uses a deliberate, bounded memory model:

- Runtime memory:
  Ephemeral release findings for the current task only.
- Project-local memory:
  Optional release artifacts saved inside the target repository when explicitly useful.
- Shared memory:
  Out of scope for this package. Cross-agent conventions should live in external shared-memory infrastructure, not inside this skill repo.

The skill does not automatically promote runtime findings into persistent memory.

## Optional integrations

These can improve the workflow but are not required:

- `gh` CLI for GitHub-specific checks or follow-up release work
- CI pipelines that run the probe helper or tests
- a separate shared-memory skill for organization-wide release policy

These integrations are optional and are not embedded as hard dependencies in the current implementation.

## Running the helper

Basic usage:

```bash
python scripts/release_probe.py --expected-repo owner/name --json
```

Strict preflight mode:

```bash
python scripts/release_probe.py --expected-repo owner/name --strict --json
```

The probe reports:

- repository root
- branch or detached state
- remote normalization and expected-repo match
- working-tree entries and summary counts
- changelog presence and top sections
- version-bearing files and obvious version conflicts

GitHub Actions monitoring is part of the runtime skill behavior rather than the probe helper. The skill should inspect workflow runs after each push and avoid declaring success while relevant Actions runs are failing.

## Testing

Run the automated tests with:

```bash
python -m unittest discover -s tests -v
```

Use the forward-test prompts in `evals/evals.json` when changing the skill instructions, assets, or probe behavior.

## Publishing notes

- The package name must remain `release-manager-skill` while this directory name stays unchanged.
- A stronger GitHub repository name is recommended for publication; see the suggestion in the final summary.
- The repository is aligned with the Agent Skills structure: `SKILL.md` plus optional `agents/`, `references/`, `scripts/`, `assets/`, tests, and eval artifacts.

## Contribution guidance

When improving this skill:

- keep `SKILL.md` focused on runtime behavior, not maintainer chatter
- move bulky details into `references/`
- add tests when changing `scripts/release_probe.py`
- update `CHANGELOG.md` when behavior or contracts change
- preserve the separation between runtime execution, project-local persistence, and shared infrastructure

## License

MIT. See [LICENSE](LICENSE).
