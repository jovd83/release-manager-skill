---
name: release-manager-skill
description: Use when validating, documenting, or preparing a GitHub-hosted repository for release in a project that follows semantic versioning and maintains a human-readable CHANGELOG.md. Verifies the expected repository and branch, handles the case where no GitHub repository exists yet by asking the user to create one and proposing repository setup details, audits changelog completeness against the actual change scope, selects the correct semver bump, stages only release-safe files, creates and pushes the release commit, monitors GitHub Actions after push, corrects failed workflow runs when possible, and prepares the next Unreleased development cycle.
license: MIT
compatibility: Requires git and local shell access. Works best with Python 3 when running scripts/release_probe.py. Network access is only required for push verification.
metadata:
  author: OpenAI Codex
  version: "0.2.0"
  maturity: stable-beta
  dispatcher-category: release-management
  dispatcher-capabilities: repo-verification, changelog-validation, semantic-versioning, selective-staging, release-commit-prep, forward-release-prep, github-repo-bootstrap, actions-monitoring, ci-remediation
  dispatcher-accepted-intents: prepare_release, validate_changelog, create_release_commit, bump_version, ready_repo_for_next_iteration, bootstrap_github_repo, monitor_actions_after_push, correct_ci_failure
  dispatcher-input-artifacts: repo_path, git_state, changelog, version_files, release_scope
  dispatcher-output-artifacts: release_summary, changelog_patch, version_bump_plan, release_readiness_report, repo_bootstrap_plan, ci_status_report
  dispatcher-stack-tags: git, github, release, semver, changelog, keep-a-changelog
  dispatcher-risk: medium
  dispatcher-writes-files: true
  dispatcher-layer: execution
  dispatcher-lifecycle: active
---

# Release Manager Skill


## Telemetry & Logging
> [!IMPORTANT]
> All usage of this skill must be logged via the Skill Dispatcher (using `./log-dispatch.cmd` or `python scripts/dispatch_logger.py`) to ensure audit logs and wallboard analytics are accurate:
> `./log-dispatch.cmd --skill release-manager-skill --intent <intent> --reason <reason>`



## 1. Mission

1. Keep GitHub repositories release-ready without smuggling unclear changes into history.
2. Treat `CHANGELOG.md` as a release gate, not as an afterthought.
3. Prefer auditable, reversible steps over clever shortcuts.
4. Stop when repository identity, version state, or changelog coverage is ambiguous.

## 2. Use this skill for

1. Validating whether a repository is ready for a release commit.
2. Reconciling `CHANGELOG.md` with the actual code and configuration changes.
3. Selecting the correct semantic version bump.
4. Preparing a clean release commit and a separate forward-prep commit.
5. Monitoring GitHub Actions after push and addressing failed runs before declaring success.
6. Leaving the repository ready for continued development after the release push and workflow validation.
7. Stopping early when no GitHub repository exists yet and proposing a sensible repository bootstrap package.

## 3. Do not use this skill for

1. Publishing GitHub Releases, tags, or release notes unless the user explicitly asks for that extra step.
2. Performing broad feature work, refactors, or unrelated cleanup.
3. Resolving merge conflicts or branch strategy disputes as the main task.
4. Rewriting Git history, force-pushing, or undoing shared commits unless explicitly requested.
5. Managing cross-repository release coordination or organization-wide release trains.

## 4. Required inputs

1. The expected GitHub repository identifier as `[[GITHUB_REPO]]` in `owner/name` form.
2. Access to the local checkout that is supposed to match that repository.
3. A repository that already follows semantic versioning and already maintains a human-readable `CHANGELOG.md`.
4. A clear release scope or enough repository evidence to infer one safely.
5. If no GitHub repository exists yet, enough project context to propose a repository name, visibility, description, and starter topics.

## 5. Memory model

1. Runtime memory:
   1. Keep the active repository state, changelog findings, version candidates, and commit plan in working memory for the current release task only.
   2. Discard runtime findings when the task ends unless the user asks for a saved artifact.
2. Project or skill memory:
   1. Persist release checklists, local release notes drafts, or validation artifacts only when the repository benefits from them as local files.
   2. Keep project-local artifacts scoped to this repository and this release workflow.
3. Shared memory:
   1. Treat organization-wide release conventions or cross-agent operational policy as external shared infrastructure.
   2. Do not silently promote runtime findings or project-local artifacts into shared memory.
4. Promotion rule:
   1. Promote information only when it is stable, valuable, and correctly scoped.

## 6. Establish the release contract

1. Treat `[[GITHUB_REPO]]` as the canonical remote repository identifier.
2. Treat the current branch as provisional until verified.
3. Treat the latest changelog state as provisional until checked against the real diff.
4. Treat every version-bearing file as a candidate until a source of truth is established.

## 7. Gather evidence first

1. Run a repository probe before editing anything.
2. Prefer `python scripts/release_probe.py --expected-repo [[GITHUB_REPO]] --json` when Python is available.
3. Otherwise run equivalent Git checks manually.
4. Collect these facts before proceeding:
   1. repository root
   2. current branch or detached state
   3. configured remotes
   4. whether the local remote matches `[[GITHUB_REPO]]`
   5. tracked modifications and untracked files
   6. changelog presence and top sections
   7. likely version-bearing files
   8. obvious version conflicts
5. Stop immediately if the local repository does not match `[[GITHUB_REPO]]`.
6. Stop immediately if the current branch is detached and the user did not explicitly ask to release from a detached state.
7. Stop immediately if the repository claims to use a changelog but `CHANGELOG.md` is missing.
8. If no GitHub repository or remote exists yet:
   1. stop the release workflow before commit or push steps
   2. tell the user a GitHub repository must be created first
   3. propose:
      1. repository name
      2. visibility
      3. short description
      4. starter topics
      5. optional default branch suggestion
   4. read [references/repo-bootstrap-guidelines.md](references/repo-bootstrap-guidelines.md) when the project type, naming pattern, or visibility choice is not obvious
   5. do not pretend release operations can continue without a repository target

## 8. Validate the changelog before staging

1. Open `CHANGELOG.md`.
2. Identify:
   1. the top working section
   2. the latest released section
   3. whether `Unreleased` already exists
3. Compare the changelog narrative against:
   1. the current diff
   2. the files changed since the last release marker or tag
   3. the apparent scope of the requested release
4. Confirm that meaningful changes are documented.
5. Treat these as meaningful changes unless the repository clearly says otherwise:
   1. user-facing features
   2. bug fixes
   3. breaking changes
   4. migration steps
   5. behavior-affecting configuration changes
6. Do not block on noise-only changes such as formatting, comments, or internal churn unless the repository normally documents them.
7. Stop and report missing changelog coverage when any meaningful change is absent.
8. When stopping, provide:
   1. the missing area
   2. the evidence that it changed
   3. one or more concise proposed changelog entries
9. Do not proceed to commit creation until changelog coverage and release scope agree.
10. Use [assets/changelog-entry-template.md](assets/changelog-entry-template.md) for concise wording when needed.

## 9. Decide the semantic version bump

1. Infer the bump only after changelog validation.
2. Use `major` for breaking changes.
3. Use `minor` for backward-compatible features.
4. Use `patch` for fixes, maintenance releases, or documentation-aligned release prep without new features.
5. Read [references/version-file-matrix.md](references/version-file-matrix.md) when version locations are unclear.
6. If multiple authoritative version files exist, update all of them consistently.
7. If multiple version files disagree, stop and reconcile before release.
8. Keep prerelease, development, or snapshot suffixes only when the repository already uses them.
9. State the chosen bump and the reason before editing version files.

## 10. Prepare the release commit

1. Stage only files that belong to the release-ready change set.
2. Do not use blanket staging such as `git add .` or `git add -A` unless the repository is already clean apart from the intended release files and you have verified every path.
3. Ensure the staged set matches the changelog narrative.
4. Craft a conventional commit message that matches the release scope.
5. Prefer these commit prefixes:
   1. `fix:` for patch releases
   2. `feat:` for minor releases
   3. `feat!:` or `breaking:` style project convention for major releases
   4. `chore(release):` only when the repository uses release-prep commits as a convention
6. Re-check `git status --short` before committing.
7. Commit locally only after the staged set is correct.
8. Keep the release commit focused on the releasable snapshot only.

## 11. Push the release commit safely

1. Push to the intended branch on the intended remote.
2. Confirm that the push succeeded.
3. Stop if the push is rejected.
4. Report the rejection cause.
5. Suggest the smallest safe next step.
6. Do not force-push unless the user explicitly asks for it.
7. Do not claim success just because the local commit exists.

## 12. Monitor GitHub Actions after each push

1. After each successful push, inspect the GitHub Actions runs triggered by that commit.
2. Prefer repository-native tooling such as `gh run list`, `gh run view`, or equivalent GitHub integrations when available.
3. Wait for the relevant workflow runs to complete or reach a clearly terminal state when the user expects release-readiness, not just local push completion.
4. If all relevant runs pass, record that the push is CI-green.
5. If any relevant run fails:
   1. inspect the failed workflow, job, and step
   2. summarize the failure clearly
   3. distinguish infrastructure flakiness from product or test regressions
   4. correct the failure when it is safe and in scope
   5. push the corrective change
   6. monitor the new GitHub Actions runs again
6. Stop only when:
   1. the relevant workflows pass
   2. the failure is external or out of scope and must be escalated
   3. the user explicitly asked for observation only without remediation
7. Do not declare the repository release-ready while relevant GitHub Actions runs are failing.

## 13. Perform forward prep for continued development

1. After the release commit is pushed, bump the repository to the next development version when the project convention requires it.
2. Add a new empty top section to `CHANGELOG.md` for the next iteration.
3. Use [assets/unreleased-section-template.md](assets/unreleased-section-template.md) as the default scaffold.
4. Include:
   1. the next version number
   2. `Unreleased` as the date placeholder
   3. `Added`
   4. `Changed`
   5. `Fixed`
   6. `Removed`
5. Keep the section empty except for headings unless the user explicitly asks to seed entries.
6. Commit the forward-prep changes as a second commit.
7. Push the forward-prep commit.
8. Treat the repository as fully ready for continued development only after this second push succeeds.
9. Do not merge the release commit and forward-prep commit into a single commit unless the repository already uses that convention and the user explicitly wants it.

## 14. Use this execution order

1. Verify repository identity and working state.
2. If no GitHub repository exists yet, stop and propose repository creation details.
3. Validate `CHANGELOG.md`.
4. Stop and propose missing changelog entries if coverage is incomplete.
5. Decide the semantic version bump.
6. Update release-facing files.
7. Stage only relevant files.
8. Create and push the release commit.
9. Monitor GitHub Actions for the release push and correct failures when safe and in scope.
10. Bump to the next development version if the repository convention requires it.
11. Add the new `Unreleased` changelog section.
12. Create and push the forward-prep commit.
13. Monitor GitHub Actions for the forward-prep push and correct failures when safe and in scope.
14. Return the final readiness summary.

## 15. Output contract

1. Use step-by-step execution output.
2. Use these sections in this order:
   1. `Verification`
   2. `Repository Setup`
   3. `Changelog`
   4. `Version Plan`
   5. `Release Commit`
   6. `GitHub Actions`
   7. `Forward Prep`
   8. `Final Readiness`
3. Distinguish:
   1. observed facts
   2. inferred conclusions
   3. blocked conditions
4. Put Git commands in fenced code blocks.
5. Add a concise summary after each major phase.
6. When blocked, say exactly what is missing and what the safest next action is.
7. Read [references/output-contract.md](references/output-contract.md) when you need a stricter response shape.

## 16. Run these command patterns

1. Use these repository verification commands when shell access is available:

```bash
git rev-parse --show-toplevel
git branch --show-current
git remote -v
git status --short
```

2. Use these changelog and history commands when needed:

```bash
git log --oneline --decorate -n 20
git diff --stat
git diff -- CHANGELOG.md
```

3. Use selective staging commands such as:

```bash
git add CHANGELOG.md package.json pyproject.toml
git status --short
```

4. Use a conventional release commit pattern such as:

```bash
git commit -m "fix: release 1.4.3"
git push origin main
```

5. Use a forward-prep commit pattern such as:

```bash
git commit -m "chore: prepare next development iteration"
git push origin main
```

6. Use GitHub Actions inspection commands such as:

```bash
gh run list --limit 10
gh run view <run-id> --log-failed
```

## 17. Guardrails

1. Do not assume the branch is `main` or `develop`.
2. Do not assume `origin` points at the correct repository.
3. Do not assume the latest changelog section is accurate.
4. Do not assume a single source of truth for the version number.
5. Do not commit unrelated local work.
6. Do not rewrite history unless the user explicitly asks for it.
7. Do not create tags or GitHub releases unless the user explicitly asks for them.
8. Do not invent missing release notes silently.
9. Do not claim success until both required pushes succeed.
10. Do not bury blockers inside optimistic language.
11. Do not broaden scope from release preparation into general repository maintenance.
12. Do not treat a successful push as final success when relevant GitHub Actions runs are red.
13. Do not retry or rerun failed workflows blindly before understanding the failure class.
14. Do not continue into release execution when no GitHub repository exists yet.

## 18. Bundled resources

1. Read [references/release-workflow.md](references/release-workflow.md) when you need the full safe-release sequence and stop conditions.
2. Read [references/version-file-matrix.md](references/version-file-matrix.md) when the project has multiple or unclear version files.
3. Read [references/failure-modes.md](references/failure-modes.md) when the workflow is blocked or repository state is unusual.
4. Read [references/repo-bootstrap-guidelines.md](references/repo-bootstrap-guidelines.md) when you need concrete heuristics for repository naming, visibility, descriptions, or starter topics.
5. Read [references/output-contract.md](references/output-contract.md) when you need a stronger reporting structure for downstream automation or handoff.
6. Use [assets/changelog-entry-template.md](assets/changelog-entry-template.md) when drafting concise changelog entries.
7. Use `scripts/release_probe.py` for deterministic repository inspection.
8. Use `tests/test_release_probe.py` and `evals/evals.json` when validating changes to the skill.

## 19. Examples

1. Example input:

```text
Use release-manager-skill for owner/service-api. Verify the repo, ensure CHANGELOG.md covers the current fixes, commit the release changes, push them, then prepare the next Unreleased section.
```

2. Expected output shape:

```text
## Verification
- Repository matches owner/service-api
- Branch: main
- Working tree: 3 modified files, 0 untracked

## Changelog
- Latest release notes are missing one fix entry
- Proposed entry: Fixed: Correct token refresh handling for expired sessions.
- Workflow paused until CHANGELOG.md is updated
```

3. Example input:

```text
Use release-manager-skill for owner/webapp. The changelog is already correct. Finish the release commit and prepare the next development section.
```

4. Expected output shape:

```text
## Verification
- Repository matches owner/webapp
- Branch: develop
- Working tree: release files only

## Release Commit
- Version bump: minor
- Commit: feat: release 2.3.0
- Push: success

## GitHub Actions
- Release workflow run: passed
- Smoke tests: passed

## Forward Prep
- Next version section added: 2.4.0 - Unreleased
- Commit: chore: prepare next development iteration
- Push: success
- Forward-prep workflow run: passed

## Final Readiness
- Repository is ready for continued development
```

5. Example input:

```text
Use release-manager-skill for owner/library. Validate whether the current checkout is safe to release, but do not push anything yet.
```

6. Expected output shape:

```text
## Verification
- Repository matches owner/library
- Branch: release/1.8.x
- Working tree: clean

## Changelog
- Coverage appears complete for the current diff

## Version Plan
- Recommended bump: patch
- Reason: bug-fix-only scope, no breaking change evidence

## Final Readiness
- Release candidate is locally ready
- Push not attempted because the user requested validation only
```

7. Example input:

```text
Use release-manager-skill for owner/service. Push the release commit, monitor GitHub Actions, and if a workflow fails because of a test regression, correct it and re-run the release flow until CI is green.
```

8. Expected output shape:

```text
## Release Commit
- Commit: fix: release 3.1.4
- Push: success

## GitHub Actions
- Workflow run: failed
- Failure: integration test expected outdated version metadata
- Correction: updated version assertion and pushed fix
- Follow-up workflow run: passed

## Final Readiness
- Repository is ready for continued development
```

9. Example input:

```text
Use release-manager-skill for a local project that is not on GitHub yet. Tell me what repository I should create so the release workflow can proceed cleanly later.
```

10. Expected output shape:

```text
## Verification
- No GitHub repository or remote is configured yet

## Repository Setup
- Required next step: create a GitHub repository before release operations
- Proposed name: acme-billing-service
- Proposed visibility: private
- Proposed description: Billing service for subscription lifecycle, invoices, and payment event processing.
- Proposed topics: billing, payments, subscriptions, backend, api
- Suggested default branch: main

## Final Readiness
- Blocked
- Reason: release workflow cannot continue until the repository exists on GitHub
```

## 20. Troubleshooting

1. Error: local repository does not match `[[GITHUB_REPO]]`.
   Fix: stop, show the detected remote, and ask the user to switch directories or correct the target repository.
2. Error: detached `HEAD`.
   Fix: stop and require an explicit branch target before committing.
3. Error: unrelated modified or untracked files are present.
   Fix: stop, list the unrelated paths, and stage only the verified release files after separating scope.
4. Error: `CHANGELOG.md` is missing.
   Fix: stop and ask whether the repository truly maintains a changelog; do not fabricate a new process silently.
5. Error: meaningful code changes are missing from `CHANGELOG.md`.
   Fix: stop and propose concise entries using [assets/changelog-entry-template.md](assets/changelog-entry-template.md).
6. Error: no version file can be identified.
   Fix: inspect repository conventions, read [references/version-file-matrix.md](references/version-file-matrix.md), and ask for the canonical version source if it remains ambiguous.
7. Error: multiple version files disagree.
   Fix: stop, report every conflicting file, identify the most likely source of truth, and require reconciliation before release.
8. Error: push is rejected.
   Fix: report whether the issue is authentication, branch protection, or non-fast-forward, then suggest the smallest safe follow-up.
9. Error: repository uses tags, release branches, or prerelease suffixes not covered here.
   Fix: preserve the repository convention, state the detected pattern, and extend the workflow only as far as the evidence supports.
10. Error: GitHub Actions fails after push.
    Fix: inspect the failed workflow run, identify whether the failure is flaky infrastructure or a real regression, correct safe in-scope issues, push the fix, and monitor the next run before declaring success.
11. Error: no GitHub repository exists yet.
    Fix: stop immediately, ask the user to create one, and propose a repository name, visibility, description, and starter topics instead of attempting release actions.
