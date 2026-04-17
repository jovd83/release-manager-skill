# Release Workflow Reference

## 1. Safe default release model

1. Verify the repository identity.
2. Verify the branch and working-tree state.
3. Validate `CHANGELOG.md` against the actual release scope.
4. Determine the semantic version bump.
5. Update only release-facing files.
6. Stage only verified release files.
7. Create and push the release commit.
8. Monitor GitHub Actions for the pushed commit and correct safe in-scope failures.
9. Prepare the next development iteration.
10. Create and push the forward-prep commit.
11. Monitor GitHub Actions again for the forward-prep push.

## 2. Why this workflow uses two commits

1. The release commit preserves the exact releasable snapshot.
2. The forward-prep commit records the start of the next development cycle.
3. Two commits make review, rollback, and audit trails cleaner.
4. One mixed commit hides the boundary between released behavior and post-release scaffolding.

## 3. Repository identity checks

1. Normalize GitHub remotes before comparing them.
2. Treat these as equivalent after normalization:
   1. `git@github.com:owner/repo.git`
   2. `https://github.com/owner/repo.git`
   3. `https://github.com/owner/repo`
   4. `owner/repo`
3. Compare normalized remotes to `[[GITHUB_REPO]]` in `owner/repo` form.
4. Refuse to proceed if no remote matches the expected repository.
5. Prefer explicit failure over “best guess” matching.

## 4. Working-tree checks

1. Separate release files from unrelated local work.
2. Stop when unrelated work cannot be confidently excluded.
3. Prefer an explicit staging list over broad staging commands.
4. Re-check `git status --short` immediately before each commit.

## 5. Changelog gating rules

1. Treat `CHANGELOG.md` as the human-readable explanation of the release.
2. Validate it against:
   1. the current diff
   2. recent commit history
   3. the most recent release section or tag
3. Stop if meaningful behavior changes are missing.
4. Propose concise entries instead of silently inventing them inside the final commit.
5. Preserve the repository's existing changelog style when it differs slightly from Keep a Changelog.

## 6. Version-bump decision rules

1. `major`:
   1. breaking API or contract changes
   2. incompatible migrations
   3. removed supported behavior
2. `minor`:
   1. additive backward-compatible features
   2. new capabilities without breaking existing consumers
3. `patch`:
   1. bug fixes
   2. small operational improvements
   3. release maintenance without new features

## 7. Commit message alignment

1. Match the commit type to the chosen semantic version bump whenever the repository uses conventional commits.
2. Keep the commit title aligned with the changelog narrative.
3. Avoid vague commit titles such as `update files` or `release stuff`.
4. Prefer explicit release scope in the title when it improves clarity.

## 8. Push safety

1. Confirm the target branch before pushing.
2. Treat rejected pushes as a stop condition.
3. Classify the likely failure:
   1. authentication
   2. branch protection
   3. non-fast-forward
   4. remote mismatch
4. Never default to force-push.

## 9. Post-push GitHub Actions monitoring

1. After each successful push, inspect the workflow runs triggered by that commit.
2. Prefer repository-native GitHub tooling such as `gh run list` and `gh run view` when available.
3. Wait for relevant workflows to complete when the goal is release readiness.
4. If workflows pass, record that the push is CI-green.
5. If workflows fail:
   1. inspect the failed job and step
   2. classify the failure as infrastructure, flaky, or product regression
   3. correct safe in-scope regressions
   4. push the corrective change
   5. monitor the follow-up run again
6. Escalate instead of guessing when the failure is out of scope or external.

## 10. Forward-prep rules

1. Preserve the repository's versioning style.
2. If the project uses plain release numbers, prepare the next plain version section.
3. If the project uses suffixes such as `-SNAPSHOT`, `-dev`, or `-alpha.1`, preserve that pattern.
4. Keep the new top `Unreleased` section empty except for standard headings unless the user asks for seeded notes.
5. Keep the forward-prep commit separate from the release commit.

## 11. Stop conditions

1. Repository mismatch.
2. Detached `HEAD`.
3. Missing changelog in a repository that claims to maintain one.
4. Missing changelog coverage for meaningful changes.
5. Ambiguous version source.
6. Conflicting version definitions.
7. Push rejection.
8. Relevant GitHub Actions runs are failing and cannot be corrected safely in scope.

## 12. Final readiness checklist

1. The repository identity was verified.
2. The changelog matches the actual release scope.
3. The version bump is justified.
4. The release commit was created and pushed successfully.
5. Relevant GitHub Actions runs passed after the release push.
6. The forward-prep commit was created and pushed successfully when requested.
7. Relevant GitHub Actions runs passed after the forward-prep push when that push occurred.
8. The next development cycle is represented in `CHANGELOG.md`.
