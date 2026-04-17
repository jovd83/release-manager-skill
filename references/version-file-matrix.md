# Version File Matrix

## 1. Common authoritative version files

1. JavaScript or TypeScript:
   1. `package.json`
   2. `package-lock.json` only when the repository intentionally mirrors the package version there
2. Python:
   1. `pyproject.toml`
   2. `setup.cfg`
   3. `setup.py` only when clearly authoritative
   4. `VERSION`
3. Rust:
   1. `Cargo.toml`
4. Java:
   1. `pom.xml`
   2. `gradle.properties`
5. .NET:
   1. `Directory.Build.props`
   2. `*.csproj`
6. Generic:
   1. `VERSION`
   2. repository-specific release metadata files

## 2. Monorepo caution

1. Do not assume the root version is authoritative in a monorepo.
2. Identify whether the release scope is:
   1. repository-wide
   2. package-specific
   3. service-specific
3. If the changelog is repository-wide but versions are package-local, stop and confirm the intended release boundary before editing files.

## 3. Selection rules

1. Prefer the file the build or packaging system actually uses.
2. Prefer repository evidence over generic assumptions.
3. If one file feeds generated mirrors, edit the source of truth first and update mirrors only when the repository expects them.
4. Stop when two files appear equally authoritative and disagree.

## 4. Extraction hints

1. `package.json`: read the `version` field.
2. `pyproject.toml`: inspect `[project] version` or tool-specific version fields.
3. `Cargo.toml`: read `package.version`.
4. `pom.xml`: inspect the project version, not dependency versions.
5. `gradle.properties`: inspect `version=`.
6. `VERSION`: use the file contents directly.

## 5. Semver bump rules

1. Patch:
   1. bug fixes
   2. security fixes without breaking API change
   3. release maintenance
2. Minor:
   1. new backward-compatible features
   2. additive API surface
3. Major:
   1. removed behavior
   2. incompatible API changes
   3. contract-breaking migrations

## 6. Development suffix rules

1. Preserve existing suffixes when the repository already uses them.
2. Common patterns:
   1. `1.4.3-SNAPSHOT`
   2. `1.4.3-dev`
   3. `1.4.3-alpha.1`
3. Do not introduce suffixes into a repository that does not already use them unless the user explicitly asks for that change.

## 7. Conflict handling

1. If multiple authoritative candidates disagree, stop and report:
   1. every file inspected
   2. the value found in each file
   3. the likely source of truth
2. Do not silently “fix” version drift without explaining the evidence.
