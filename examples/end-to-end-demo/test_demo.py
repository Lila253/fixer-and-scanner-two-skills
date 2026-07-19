#!/usr/bin/env python3
"""Run dependency-free behavior checks for the fixed demo code."""

from __future__ import annotations

import contextlib
import io
import runpy
from pathlib import Path


def main() -> int:
    demo_dir = Path(__file__).resolve().parent
    module = runpy.run_path(str(demo_dir / "fixed-code.py"))

    missing_repo = type("MissingRepo", (), {"find": lambda self, _user_id: None})
    found_repo = type(
        "FoundRepo", (), {"find": lambda self, _user_id: {"name": "Alice"}}
    )

    assert module["find_name"](missing_repo(), "missing") is None
    assert module["find_name"](found_repo(), "found") == "Alice"
    assert module["safe_find_name"](missing_repo(), "missing") is None

    output = io.StringIO()
    with contextlib.redirect_stdout(output):
        module["print_items"]([])
        module["print_items"]([1, 2])
    assert output.getvalue().splitlines() == ["1", "2"]

    print("DefectLoop end-to-end demo: all behavior checks passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
