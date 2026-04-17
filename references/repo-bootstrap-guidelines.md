# Repository Bootstrap Guidelines

Use this reference when the release workflow is blocked because no GitHub repository exists yet.

## 1. Visibility heuristic

Use `private` by default when any of these are true:

- the repository contains proprietary business logic
- the project serves an internal team or a specific customer
- credentials, infrastructure details, or sensitive integration patterns are likely to appear
- the user has not said the project should be public

Use `public` when most of these are true:

- the project is intended for open-source reuse
- the code is safe to share externally
- the repository is expected to attract users, contributors, or community feedback
- the user explicitly wants visibility, discoverability, or distribution

When unsure:

- recommend `private`
- say it can be made public later after code, docs, and secrets are reviewed

## 2. Default branch heuristic

- Prefer `main` unless the user or organization already uses a different default branch convention.

## 3. Repository naming heuristic

Prefer lowercase hyphenated names. Keep them short, concrete, and domain-first.

### Service

Pattern:

- `<domain>-service`
- `<domain>-<capability>-service`

Examples:

- `billing-service`
- `identity-auth-service`
- `catalog-sync-service`

### API

Pattern:

- `<domain>-api`
- `<product>-public-api`

Examples:

- `payments-api`
- `customer-profile-api`
- `partner-public-api`

### CLI

Pattern:

- `<tool>-cli`
- `<domain>-cli`

Examples:

- `release-cli`
- `developer-tools-cli`
- `tenant-admin-cli`

### Frontend

Pattern:

- `<product>-web`
- `<product>-frontend`
- `<brand>-portal`

Examples:

- `billing-web`
- `ops-frontend`
- `partner-portal`

### Agent Skill

Pattern:

- `<capability>-skill`
- `<platform>-<capability>-skill`

Examples:

- `release-manager-skill`
- `github-release-manager-skill`
- `ci-triage-skill`

## 4. Description heuristic

Use one sentence.

Formula:

- `<Primary system> for <core domain or audience>, handling <2-3 major responsibilities>.`

Examples:

- `Billing service for subscription lifecycle, invoices, and payment event processing.`
- `Developer CLI for release preparation, changelog validation, and CI-safe deployment workflows.`
- `Frontend portal for partner onboarding, account management, and support operations.`
- `Agent Skill for GitHub release preparation, changelog gating, and post-push Actions monitoring.`

## 5. Starter topics heuristic

Pick 4-7 topics. Use the project type plus domain keywords.

### Service topics

- `backend`
- `service`
- `<domain>`
- `<integration>`
- `<language>`

Example:

- `backend, service, billing, payments, java`

### API topics

- `api`
- `rest-api`
- `<domain>`
- `<language>`
- `<framework>`

Example:

- `api, rest-api, identity, nodejs, express`

### CLI topics

- `cli`
- `developer-tools`
- `automation`
- `<domain>`
- `<language>`

Example:

- `cli, automation, release-management, python, developer-tools`

### Frontend topics

- `frontend`
- `web`
- `<domain>`
- `<framework>`
- `ui`

Example:

- `frontend, web, billing, react, ui`

### Agent Skill topics

- `agent-skill`
- `ai-agents`
- `automation`
- `<capability>`
- `<platform>`

Example:

- `agent-skill, ai-agents, automation, release-management, github`

## 6. Recommendation format

When the user needs a repository proposal, return:

- proposed name
- proposed visibility
- proposed description
- proposed starter topics
- suggested default branch
- one-sentence rationale for the visibility choice
