# Changelog Entry Templates

Write entries in user-visible language. Prefer one sentence per bullet. Describe the observable outcome, not the implementation detail.

## Fix

- Fixed: <observable bug fix in one concise sentence>.
- Example: Fixed: prevent stale refresh tokens from causing silent session expiry loops.

## Feature

- Added: <new backward-compatible capability in one concise sentence>.
- Example: Added: allow release validation to report obvious version-file conflicts before commit preparation.

## Breaking change

- Changed: <breaking behavior change in one concise sentence>.
- Removed: <deprecated behavior or interface that no longer exists>.
- Example: Changed: require the expected GitHub repository identifier before release execution.
- Example: Removed: implicit release execution against whichever remote happened to be configured.

## Maintenance

- Changed: <release-relevant operational or configuration change in one concise sentence>.
- Example: Changed: standardize forward-prep commits so the next Unreleased section is always created as a separate step.
