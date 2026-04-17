# Failure Modes

## 1. Repository mismatch

1. Symptom: remote normalization does not match `[[GITHUB_REPO]]`.
2. Response: stop immediately.
3. Report:
   1. expected repository
   2. detected remote URLs
   3. normalized mismatch
4. Safe next step: switch to the correct checkout or correct the target repo value.

## 1a. No GitHub repository exists yet

1. Symptom: there is no GitHub remote, or no GitHub repository has been created for the project.
2. Response: stop immediately.
3. Report:
   1. that release execution cannot proceed yet
   2. that the user needs to create a GitHub repository first
   3. a proposed repository package including:
      1. name
      2. visibility
      3. short description
      4. starter topics
      5. optional default branch suggestion
4. Safe next step: create the repository on GitHub, then re-run the release workflow against the new remote.

## 2. Detached HEAD

1. Symptom: no current branch name is available.
2. Response: stop.
3. Report:
   1. current commit SHA
   2. lack of branch target
   3. need for explicit branch selection
4. Safe next step: check out the intended release branch before continuing.

## 3. Dirty tree with unrelated changes

1. Symptom: modified or untracked files exceed the intended release scope.
2. Response: stop or stage only the verified release files.
3. Report the unrelated paths explicitly.
4. Safe next step: separate release files from unrelated work before commit creation.

## 4. Missing changelog coverage

1. Symptom: code changes exist without meaningful release notes.
2. Response: stop and propose concise entries.
3. Do not continue to commit creation until the changelog is reconciled.
4. Safe next step: update `CHANGELOG.md` with precise, user-visible bullets.

## 5. Missing or conflicting version sources

1. Symptom: no authoritative version file is found, or multiple files disagree.
2. Response: stop.
3. Report every candidate file and the value discovered in each.
4. Safe next step: confirm the canonical source of truth before editing version files.

## 6. Push rejection

1. Symptom: `git push` fails.
2. Response: stop.
3. Classify the most likely reason:
   1. auth failure
   2. protected branch
   3. non-fast-forward
   4. incorrect remote
4. Suggest the smallest safe follow-up action.

## 7. Unusual release conventions

1. Symptom: repository uses tags, release branches, prerelease suffixes, or custom changelog headings.
2. Response: preserve the convention.
3. Extend the workflow only as far as the repository evidence supports.
4. Safe next step: state the detected convention and limit automation to the verified parts.
