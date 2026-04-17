#!/usr/bin/env python3
"""Inspect a local Git repository for release-management preflight checks."""

from __future__ import annotations

import argparse
import json
import os
import re
import subprocess
import sys
from typing import Any


SKIP_DIRS = {
    ".git",
    ".hg",
    ".svn",
    ".venv",
    "venv",
    "__pycache__",
    "node_modules",
    "dist",
    "build",
    "coverage",
    "target",
    "out",
}

VERSION_CANDIDATES = {
    "package.json": "node",
    "pyproject.toml": "python",
    "setup.cfg": "python",
    "Cargo.toml": "rust",
    "pom.xml": "java-maven",
    "gradle.properties": "java-gradle",
    "Directory.Build.props": ".net",
    "VERSION": "generic",
}


def run_git(args: list[str], cwd: str) -> str:
    completed = subprocess.run(
        ["git", *args],
        cwd=cwd,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        check=False,
    )
    if completed.returncode != 0:
        raise RuntimeError(completed.stderr.strip() or "git command failed")
    return completed.stdout.strip()


def normalize_github_repo(raw: str | None) -> str | None:
    if not raw:
        return None

    value = raw.strip()
    patterns = [
        r"^git@github\.com:(?P<owner>[^/]+)/(?P<repo>[^/]+?)(?:\.git)?$",
        r"^https://github\.com/(?P<owner>[^/]+)/(?P<repo>[^/]+?)(?:\.git)?/?$",
        r"^ssh://git@github\.com/(?P<owner>[^/]+)/(?P<repo>[^/]+?)(?:\.git)?/?$",
        r"^(?P<owner>[^/]+)/(?P<repo>[^/]+?)$",
    ]

    for pattern in patterns:
        match = re.match(pattern, value)
        if match:
            return f"{match.group('owner')}/{match.group('repo')}"

    return None


def get_repo_root(cwd: str) -> str:
    return run_git(["rev-parse", "--show-toplevel"], cwd)


def get_branch_name(cwd: str) -> str | None:
    try:
        branch = run_git(["branch", "--show-current"], cwd)
    except RuntimeError:
        return None
    return branch or None


def get_head_sha(cwd: str) -> str:
    return run_git(["rev-parse", "HEAD"], cwd)


def get_remotes(cwd: str) -> dict[str, str]:
    lines = run_git(["remote", "-v"], cwd).splitlines()
    remotes: dict[str, str] = {}
    for line in lines:
        parts = line.split()
        if len(parts) >= 3 and parts[2] == "(fetch)" and parts[0] not in remotes:
            remotes[parts[0]] = parts[1]
    return remotes


def get_status_entries(cwd: str) -> list[dict[str, str]]:
    output = run_git(["status", "--short"], cwd)
    if not output:
        return []
    entries: list[dict[str, str]] = []
    for line in output.splitlines():
        if len(line) < 4:
            continue
        entries.append(
            {
                "index_status": line[0],
                "worktree_status": line[1],
                "path": line[3:].strip(),
            }
        )
    return entries


def summarize_status(entries: list[dict[str, str]]) -> dict[str, int]:
    summary = {
        "total": len(entries),
        "untracked": 0,
        "modified": 0,
        "deleted": 0,
        "renamed": 0,
        "copied": 0,
        "added": 0,
        "unknown": 0,
    }
    for entry in entries:
        code = f"{entry['index_status']}{entry['worktree_status']}"
        if "?" in code:
            summary["untracked"] += 1
        elif "D" in code:
            summary["deleted"] += 1
        elif "R" in code:
            summary["renamed"] += 1
        elif "C" in code:
            summary["copied"] += 1
        elif "A" in code:
            summary["added"] += 1
        elif "M" in code:
            summary["modified"] += 1
        else:
            summary["unknown"] += 1
    return summary


def extract_version(path: str) -> str | None:
    name = os.path.basename(path)
    try:
        with open(path, "r", encoding="utf-8") as handle:
            content = handle.read()
    except OSError:
        return None

    if name == "package.json":
        try:
            data = json.loads(content)
        except json.JSONDecodeError:
            return None
        value = data.get("version")
        return value if isinstance(value, str) else None

    patterns = {
        "pyproject.toml": r'(?m)^\s*version\s*=\s*"([^"]+)"',
        "setup.cfg": r"(?m)^\s*version\s*=\s*([^\s]+)",
        "Cargo.toml": r'(?m)^\s*version\s*=\s*"([^"]+)"',
        "pom.xml": r"<version>\s*([^<\s]+)\s*</version>",
        "gradle.properties": r"(?m)^\s*version\s*=\s*([^\s]+)",
        "Directory.Build.props": r"<Version>\s*([^<\s]+)\s*</Version>",
        "VERSION": r"^\s*([^\s]+)\s*$",
    }

    pattern = patterns.get(name)
    if not pattern:
        return None
    match = re.search(pattern, content)
    return match.group(1) if match else None


def find_version_files(repo_root: str) -> list[dict[str, Any]]:
    results: list[dict[str, Any]] = []
    for root, dirs, files in os.walk(repo_root):
        dirs[:] = [directory for directory in dirs if directory not in SKIP_DIRS]
        for filename in files:
            if filename not in VERSION_CANDIDATES:
                continue
            full_path = os.path.join(root, filename)
            rel_path = os.path.relpath(full_path, repo_root).replace("\\", "/")
            results.append(
                {
                    "path": rel_path,
                    "ecosystem": VERSION_CANDIDATES[filename],
                    "version": extract_version(full_path),
                }
            )
    results.sort(key=lambda item: item["path"])
    return results


def summarize_versions(version_files: list[dict[str, Any]]) -> dict[str, Any]:
    values = sorted(
        {item["version"] for item in version_files if isinstance(item["version"], str)}
    )
    conflicts = len(values) > 1
    return {
        "count": len(version_files),
        "detected_versions": values,
        "conflict": conflicts,
    }


def parse_changelog(repo_root: str) -> dict[str, Any]:
    path = os.path.join(repo_root, "CHANGELOG.md")
    if not os.path.exists(path):
        return {
            "present": False,
            "top_section": None,
            "latest_release_section": None,
            "has_unreleased": False,
            "sections": [],
        }

    try:
        with open(path, "r", encoding="utf-8") as handle:
            content = handle.read()
    except OSError:
        return {
            "present": True,
            "top_section": None,
            "latest_release_section": None,
            "has_unreleased": False,
            "sections": [],
        }

    sections = re.findall(r"(?m)^##\s+(.+)$", content)
    top_section = sections[0] if sections else None
    latest_release = None
    for section in sections:
        if "unreleased" not in section.lower():
            latest_release = section
            break
    return {
        "present": True,
        "top_section": top_section,
        "latest_release_section": latest_release,
        "has_unreleased": any("unreleased" in item.lower() for item in sections),
        "sections": sections[:8],
    }


def enforce_strict_checks(report: dict[str, Any]) -> tuple[bool, str | None]:
    if report["expected_repo_normalized"] and report["repo_match"] is False:
        return False, "expected repository does not match any configured remote"
    if report["detached_head"]:
        return False, "repository is in detached HEAD state"
    if not report["changelog"]["present"]:
        return False, "CHANGELOG.md is missing"
    if report["version_summary"]["conflict"]:
        return False, "multiple version values were detected"
    return True, None


def build_report(cwd: str, expected_repo: str | None) -> dict[str, Any]:
    repo_root = get_repo_root(cwd)
    branch = get_branch_name(repo_root)
    remotes = get_remotes(repo_root)
    normalized_remotes = {
        name: normalize_github_repo(url) for name, url in remotes.items()
    }
    expected_normalized = normalize_github_repo(expected_repo)
    matching_remotes = [
        name
        for name, normalized in normalized_remotes.items()
        if expected_normalized and normalized == expected_normalized
    ]
    status_entries = get_status_entries(repo_root)
    version_files = find_version_files(repo_root)
    changelog = parse_changelog(repo_root)

    report: dict[str, Any] = {
        "repo_root": repo_root.replace("\\", "/"),
        "branch": branch,
        "detached_head": branch is None,
        "head_sha": get_head_sha(repo_root),
        "remotes": remotes,
        "normalized_remotes": normalized_remotes,
        "expected_repo": expected_repo,
        "expected_repo_normalized": expected_normalized,
        "repo_match": bool(matching_remotes) if expected_normalized else None,
        "matching_remotes": matching_remotes,
        "status": status_entries,
        "status_summary": summarize_status(status_entries),
        "changelog": changelog,
        "version_files": version_files,
        "version_summary": summarize_versions(version_files),
    }
    return report


def print_text_report(report: dict[str, Any]) -> None:
    print(f"Repository root: {report['repo_root']}")
    print(f"Branch: {report['branch'] or '(detached HEAD)'}")
    print(f"Head SHA: {report['head_sha']}")
    if report["expected_repo_normalized"]:
        print(
            "Repository match: "
            + ("yes" if report["repo_match"] else "no")
            + f" ({report['expected_repo_normalized']})"
        )
    print("Remotes:")
    if report["remotes"]:
        for name, url in report["remotes"].items():
            normalized = report["normalized_remotes"].get(name) or "n/a"
            print(f"  - {name}: {url} [{normalized}]")
    else:
        print("  - none")

    print("Working tree:")
    if report["status"]:
        for entry in report["status"]:
            print(
                f"  - {entry['index_status']}{entry['worktree_status']} {entry['path']}"
            )
    else:
        print("  - clean")
    print(f"Status summary: {report['status_summary']}")

    changelog = report["changelog"]
    print(f"CHANGELOG.md present: {'yes' if changelog['present'] else 'no'}")
    if changelog["present"]:
        print(f"Top changelog section: {changelog['top_section'] or 'unknown'}")
        print(
            "Latest release section: "
            + (changelog["latest_release_section"] or "unknown")
        )

    print("Version files:")
    if report["version_files"]:
        for item in report["version_files"]:
            version = item["version"] or "unknown"
            print(f"  - {item['path']} ({item['ecosystem']}): {version}")
    else:
        print("  - none detected")
    print(f"Version summary: {report['version_summary']}")


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Inspect local Git repository state for release management."
    )
    parser.add_argument(
        "path",
        nargs="?",
        default=".",
        help="Path inside the target repository. Defaults to the current directory.",
    )
    parser.add_argument(
        "--expected-repo",
        dest="expected_repo",
        help="Expected GitHub repository in owner/name form or remote URL form.",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Emit the probe result as JSON.",
    )
    parser.add_argument(
        "--strict",
        action="store_true",
        help="Exit nonzero when repository match, changelog, branch, or version checks fail.",
    )
    return parser.parse_args(argv)


def main(argv: list[str]) -> int:
    args = parse_args(argv)
    try:
        report = build_report(os.path.abspath(args.path), args.expected_repo)
    except RuntimeError as exc:
        if args.json:
            print(json.dumps({"ok": False, "error": str(exc)}, indent=2, sort_keys=True))
        else:
            print(f"release_probe.py: {exc}", file=sys.stderr)
        return 1

    if args.strict:
        ok, reason = enforce_strict_checks(report)
        report["strict_ok"] = ok
        report["strict_reason"] = reason
        if not ok:
            if args.json:
                print(json.dumps(report, indent=2, sort_keys=True))
            else:
                print_text_report(report)
                print(f"Strict check failed: {reason}", file=sys.stderr)
            return 2

    if args.json:
        print(json.dumps(report, indent=2, sort_keys=True))
    else:
        print_text_report(report)
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
