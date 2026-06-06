#!/usr/bin/env python3
"""CLI: emit generated/intract.yaml from intent.yaml (+ optional prompt.txt)."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT))

from generator.intract_manifest import write_intract_manifest  # noqa: E402


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("intent", type=Path)
    parser.add_argument("-o", "--output", type=Path, required=True)
    parser.add_argument("-p", "--prompt", type=Path, default=None)
    args = parser.parse_args()

    prompt = args.prompt.read_text(encoding="utf-8") if args.prompt and args.prompt.exists() else None
    path = write_intract_manifest(args.intent, args.output, prompt=prompt)
    print(path)


if __name__ == "__main__":
    main()
