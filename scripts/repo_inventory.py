#!/usr/bin/env python3
"""Create a lightweight repository inventory for agent-assisted analysis.

This script intentionally avoids reading file contents. It lists likely high-signal
files and directories so an agent can decide what to inspect next.
"""

from __future__ import annotations

import argparse
from pathlib import Path

HIGH_SIGNAL_NAMES = {
    "readme.md",
    "pyproject.toml",
    "requirements.txt",
    "package.json",
    "dockerfile",
    "docker-compose.yml",
    "compose.yml",
    "go.mod",
    "cargo.toml",
    "pom.xml",
    "build.gradle",
}

KEYWORDS = (
    "agent",
    "tool",
    "prompt",
    "eval",
    "judge",
    "trace",
    "span",
    "telemetry",
    "session",
    "conversation",
    "memory",
    "router",
    "workflow",
)

SKIP_DIRS = {
    ".git",
    ".idea",
    ".vscode",
    "node_modules",
    "dist",
    "build",
    ".next",
    ".venv",
    "venv",
    "__pycache__",
}


def should_skip(path: Path) -> bool:
    return any(part in SKIP_DIRS for part in path.parts)


def score(path: Path) -> int:
    name = path.name.lower()
    value = 0
    if name in HIGH_SIGNAL_NAMES:
        value += 100
    for keyword in KEYWORDS:
        if keyword in str(path).lower():
            value += 10
    if path.suffix.lower() in {".py", ".ts", ".tsx", ".js", ".jsx", ".go", ".java", ".rs", ".yaml", ".yml", ".json", ".toml"}:
        value += 1
    return value


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("root", nargs="?", default=".")
    parser.add_argument("--limit", type=int, default=200)
    args = parser.parse_args()

    root = Path(args.root).resolve()
    files = [p for p in root.rglob("*") if p.is_file() and not should_skip(p.relative_to(root))]
    ranked = sorted(files, key=lambda p: (-score(p.relative_to(root)), str(p.relative_to(root))))

    print(f"Repository: {root}")
    print(f"Files discovered: {len(files)}")
    print("\nHigh-signal inventory:")
    for path in ranked[: args.limit]:
        rel = path.relative_to(root)
        print(f"{score(rel):>3}  {rel}")


if __name__ == "__main__":
    main()
