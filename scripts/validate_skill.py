#!/usr/bin/env python3
"""
Validator for the GitHub Release Manager Agent Skill.
Checks for mandatory files, SKILL.md structure, and metadata consistency.
"""

import os
import sys
import re
from pathlib import Path

class Validator:
    def __init__(self, root_dir):
        self.root = Path(root_dir).resolve()
        self.errors = []
        self.warnings = []

    def error(self, msg):
        self.errors.append(msg)
        print(f"ERROR: {msg}")

    def warn(self, msg):
        self.warnings.append(msg)
        print(f"WARN:  {msg}")

    def info(self, msg):
        print(f"INFO:  {msg}")

    def check_mandatory_files(self):
        mandatory = [
            "SKILL.md",
            "README.md",
            "CHANGELOG.md",
            "LICENSE",
            "scripts/release_probe.py",
            "tests/test_release_probe.py",
            "evals/evals.json",
            "agents/openai.yaml"
        ]
        for rel_path in mandatory:
            path = self.root / rel_path
            if not path.exists():
                self.error(f"Missing mandatory file: {rel_path}")
            else:
                self.info(f"Found {rel_path}")

    def check_skill_md(self):
        skill_md_path = self.root / "SKILL.md"
        if not skill_md_path.exists():
            return

        content = skill_md_path.read_text(encoding="utf-8")
        
        # Check Frontmatter
        if not content.startswith("---"):
            self.error("SKILL.md missing YAML frontmatter start (---)")
        
        # Check mandatory headers
        headers = [
            "## 1. Mission",
            "## 2. Use this skill for",
            "## 3. Do not use this skill for",
            "## 14. Use this execution order",
            "## 15. Output contract",
            "## 17. Guardrails"
        ]
        for header in headers:
            if header not in content:
                self.error(f"SKILL.md missing mandatory header: {header}")
            else:
                self.info(f"SKILL.md contains {header}")

        # Extract version from frontmatter
        version_match = re.search(r'version:\s*"([^"]+)"', content)
        if version_match:
            version = version_match.group(1)
            self.info(f"SKILL.md version: {version}")
        else:
            self.error("SKILL.md frontmatter missing version")

    def check_readme_badges(self):
        readme_path = self.root / "README.md"
        if not readme_path.exists():
            return

        content = readme_path.read_text(encoding="utf-8")
        if "[![Validate Skill]" not in content:
            self.warn("README.md missing Validate Skill badge")

    def run(self):
        self.info(f"Validating skill in {self.root}")
        self.check_mandatory_files()
        self.check_skill_md()
        self.check_readme_badges()
        
        if self.errors:
            print(f"\nValidation FAILED with {len(self.errors)} errors and {len(self.warnings)} warnings.")
            return False
        else:
            print(f"\nValidation PASSED with {len(self.warnings)} warnings.")
            return True

if __name__ == "__main__":
    repo_root = sys.argv[1] if len(sys.argv) > 1 else "."
    validator = Validator(repo_root)
    if not validator.run():
        sys.exit(1)
    sys.exit(0)
