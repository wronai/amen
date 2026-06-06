#!/usr/bin/env python3
"""CLI: emit generated/service.testql.toon.yaml from intent.yaml."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT))

from generator.testql_scenario import write_testql_scenario  # noqa: E402


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("intent", type=Path)
    parser.add_argument("-o", "--output", type=Path, required=True)
    args = parser.parse_args()
    path = write_testql_scenario(args.intent, args.output)
    print(path)


if __name__ == "__main__":
    main()
