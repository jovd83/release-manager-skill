import json
import os
import subprocess
import tempfile
import unittest

from scripts import release_probe


def git_available() -> bool:
    try:
        completed = subprocess.run(
            ["git", "--version"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            check=False,
        )
    except OSError:
        return False
    return completed.returncode == 0


class NormalizeGithubRepoTests(unittest.TestCase):
    def test_normalizes_https(self) -> None:
        self.assertEqual(
            release_probe.normalize_github_repo("https://github.com/openai/skills.git"),
            "openai/skills",
        )

    def test_normalizes_ssh(self) -> None:
        self.assertEqual(
            release_probe.normalize_github_repo("git@github.com:openai/skills.git"),
            "openai/skills",
        )

    def test_normalizes_owner_repo(self) -> None:
        self.assertEqual(
            release_probe.normalize_github_repo("openai/skills"),
            "openai/skills",
        )


class VersionExtractionTests(unittest.TestCase):
    def test_extracts_package_json_version(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            path = os.path.join(tmpdir, "package.json")
            with open(path, "w", encoding="utf-8") as handle:
                json.dump({"name": "demo", "version": "1.2.3"}, handle)
            self.assertEqual(release_probe.extract_version(path), "1.2.3")

    def test_extracts_version_file(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            path = os.path.join(tmpdir, "VERSION")
            with open(path, "w", encoding="utf-8") as handle:
                handle.write("2.4.6\n")
            self.assertEqual(release_probe.extract_version(path), "2.4.6")

    def test_version_summary_detects_conflict(self) -> None:
        summary = release_probe.summarize_versions(
            [
                {"path": "package.json", "ecosystem": "node", "version": "1.0.0"},
                {"path": "pyproject.toml", "ecosystem": "python", "version": "2.0.0"},
            ]
        )
        self.assertTrue(summary["conflict"])


@unittest.skipUnless(git_available(), "git is required for repository probe tests")
class BuildReportTests(unittest.TestCase):
    def test_build_report_for_real_git_repo(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            subprocess.run(["git", "init", "-b", "main"], cwd=tmpdir, check=True)
            subprocess.run(
                ["git", "config", "user.name", "Test User"], cwd=tmpdir, check=True
            )
            subprocess.run(
                ["git", "config", "user.email", "test@example.com"],
                cwd=tmpdir,
                check=True,
            )
            subprocess.run(
                ["git", "remote", "add", "origin", "https://github.com/example/repo.git"],
                cwd=tmpdir,
                check=True,
            )

            with open(os.path.join(tmpdir, "CHANGELOG.md"), "w", encoding="utf-8") as handle:
                handle.write(
                    "# Changelog\n\n## [Unreleased]\n\n### Added\n\n## [1.0.0] - 2026-01-01\n"
                )
            with open(os.path.join(tmpdir, "package.json"), "w", encoding="utf-8") as handle:
                json.dump({"name": "demo", "version": "1.0.0"}, handle)
            with open(os.path.join(tmpdir, "README.md"), "w", encoding="utf-8") as handle:
                handle.write("demo\n")

            subprocess.run(["git", "add", "."], cwd=tmpdir, check=True)
            subprocess.run(["git", "commit", "-m", "init"], cwd=tmpdir, check=True)

            report = release_probe.build_report(tmpdir, "example/repo")
            self.assertEqual(report["branch"], "main")
            self.assertTrue(report["repo_match"])
            self.assertTrue(report["changelog"]["present"])
            self.assertTrue(report["changelog"]["has_unreleased"])
            self.assertEqual(report["version_summary"]["detected_versions"], ["1.0.0"])

    def test_strict_checks_fail_for_detached_head(self) -> None:
        report = {
            "expected_repo_normalized": "example/repo",
            "repo_match": True,
            "detached_head": True,
            "changelog": {"present": True},
            "version_summary": {"conflict": False},
        }
        ok, reason = release_probe.enforce_strict_checks(report)
        self.assertFalse(ok)
        self.assertIn("detached HEAD", reason)
