# Output Contract

Use this contract when the calling workflow needs a stricter, easier-to-parse release report.

## 1. Required section order

1. `Verification`
2. `Repository Setup`
3. `Changelog`
4. `Version Plan`
5. `Release Commit`
6. `GitHub Actions`
7. `Forward Prep`
8. `Final Readiness`

## 2. Section expectations

### Verification

Report:

- repository match status
- branch or detached state
- working-tree summary
- notable repository identity risks

### Repository Setup

Use this section when no GitHub repository exists yet.

Report:

- whether a GitHub repository or remote exists
- the required next step
- proposed repository name
- proposed visibility
- proposed short description
- proposed starter topics
- optional default branch recommendation

### Changelog

Report:

- whether `CHANGELOG.md` exists
- top working section and latest release section when visible
- whether the changelog appears complete for the release scope
- proposed entries when blocked

### Version Plan

Report:

- recommended bump type
- files that carry version information
- any version conflicts
- rationale for the bump

### Release Commit

Report:

- staged scope
- intended or completed commit message
- push status
- stop reason if blocked

### Forward Prep

Report:

- next development version or version style
- whether the next `Unreleased` section was added
- intended or completed forward-prep commit
- push status

### GitHub Actions

Report:

- relevant workflow runs for the pushed commit
- pass or fail status
- failure classification when red
- corrective change taken when applicable
- whether follow-up runs turned green

### Final Readiness

Report one of:

- `Ready for continued development`
- `Ready for local review only`
- `Blocked`

Then state the exact reason.

## 3. Tone rules

1. Prefer short, declarative bullets.
2. Keep facts and inference separate.
3. When blocked, say what is missing and what the safest next step is.
4. Do not imply success if any required push failed or was not attempted.
5. Do not imply success if relevant GitHub Actions runs are still failing.
6. Do not imply release execution can continue when a GitHub repository does not exist yet.
