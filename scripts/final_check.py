from __future__ import annotations

import subprocess
import sys
from pathlib import Path


REQUIRED_PATHS = [
    "README.md",
    "pyproject.toml",
    "src/launchlab",
    "tests",
    "scripts/build_research_report.py",
    "scripts/build_publication_outputs.py",
    "scripts/run_joint_surface.py",
    "docs/preregistration.md",
    "docs/assumptions.md",
    "docs/limitations.md",
]


def main() -> int:
    missing = [path for path in REQUIRED_PATHS if not Path(path).exists()]
    if missing:
        print("missing required paths:")
        for path in missing:
            print(f"  - {path}")
        return 1

    print("repository structure: OK")

    result = subprocess.run(
        [sys.executable, "-m", "pytest", "-q"],
        check=False,
    )
    if result.returncode:
        return result.returncode

    print("test suite: OK")
    print("portfolio readiness check: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
