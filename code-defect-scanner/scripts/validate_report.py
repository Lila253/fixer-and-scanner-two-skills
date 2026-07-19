#!/usr/bin/env python3
"""Validate the shared defect-report contract without third-party packages."""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path, PurePosixPath
from typing import Any


KINDS = {"defect", "risk", "suggestion"}
STATUSES = {"confirmed", "probable", "hypothesis"}
SEVERITIES = {"P0", "P1", "P2", "P3", None}
CONFIDENCES = {"high", "medium", "low"}
TOOL_STATUSES = {"passed", "failed", "skipped"}
FINDING_KEYS = {
    "id",
    "path",
    "start_line",
    "end_line",
    "symbol",
    "kind",
    "category",
    "status",
    "severity",
    "confidence",
    "description",
    "impact_assumption",
    "evidence",
    "suggested_action",
}


def add_error(errors: list[str], location: str, message: str) -> None:
    errors.append(f"{location}: {message}")


def is_safe_relative_path(value: Any) -> bool:
    if not isinstance(value, str) or not value.strip():
        return False
    normalized = value.replace("\\", "/")
    path = PurePosixPath(normalized)
    return not path.is_absolute() and ".." not in path.parts and not re.match(r"^[A-Za-z]:", normalized)


def validate_evidence_source(
    item: dict[str, Any], source_root: Path, location: str, errors: list[str]
) -> None:
    path_value = item.get("path")
    if path_value == "pasted-snippet" or not is_safe_relative_path(path_value):
        return
    source_path = (source_root / path_value).resolve()
    try:
        source_path.relative_to(source_root)
    except ValueError:
        add_error(errors, location, "evidence path escapes source root")
        return
    if not source_path.is_file():
        add_error(errors, location, f"source file does not exist: {path_value}")
        return
    try:
        lines = source_path.read_text(encoding="utf-8").splitlines()
    except UnicodeDecodeError:
        add_error(errors, location, f"source file is not UTF-8 text: {path_value}")
        return
    line_number = item.get("line")
    if not isinstance(line_number, int) or line_number < 1 or line_number > len(lines):
        add_error(errors, location, "evidence line is outside the source file")
        return
    code = item.get("code")
    if isinstance(code, str) and lines[line_number - 1].strip() != code.strip():
        add_error(errors, location, "evidence code does not match the current source line")


def validate_report(data: Any, source_root: Path | None) -> list[str]:
    errors: list[str] = []
    if not isinstance(data, dict):
        return ["report: expected a JSON object"]
    if set(data) != {"schema_version", "scan", "findings", "tool_results"}:
        add_error(errors, "report", "top-level fields must match the 1.0 contract")
    if data.get("schema_version") != "1.0":
        add_error(errors, "schema_version", "expected '1.0'")

    scan = data.get("scan")
    if not isinstance(scan, dict):
        add_error(errors, "scan", "expected an object")
    else:
        required_scan = {"scope", "files_scanned", "coverage", "skipped", "error_hint"}
        if set(scan) != required_scan:
            add_error(errors, "scan", "fields must match the 1.0 contract")
        if not isinstance(scan.get("scope"), str) or not scan.get("scope", "").strip():
            add_error(errors, "scan.scope", "expected a non-empty string")
        if not isinstance(scan.get("files_scanned"), int) or scan.get("files_scanned", -1) < 0:
            add_error(errors, "scan.files_scanned", "expected a non-negative integer")
        if scan.get("coverage") not in {"complete", "partial"}:
            add_error(errors, "scan.coverage", "expected complete or partial")
        skipped = scan.get("skipped")
        if not isinstance(skipped, list):
            add_error(errors, "scan.skipped", "expected an array")
        else:
            for index, item in enumerate(skipped):
                if not isinstance(item, dict) or set(item) != {"path", "reason"}:
                    add_error(errors, f"scan.skipped[{index}]", "expected path and reason")
        if scan.get("error_hint") is not None and not isinstance(scan.get("error_hint"), str):
            add_error(errors, "scan.error_hint", "expected a string or null")

    findings = data.get("findings")
    if not isinstance(findings, list):
        add_error(errors, "findings", "expected an array")
    else:
        for index, finding in enumerate(findings, start=1):
            location = f"findings[{index - 1}]"
            if not isinstance(finding, dict):
                add_error(errors, location, "expected an object")
                continue
            if set(finding) != FINDING_KEYS:
                add_error(errors, location, "fields must match the 1.0 contract")
            expected_id = f"DEF-{index:03d}"
            if finding.get("id") != expected_id:
                add_error(errors, f"{location}.id", f"expected {expected_id}")
            if not is_safe_relative_path(finding.get("path")):
                add_error(errors, f"{location}.path", "expected a safe relative path")
            start_line = finding.get("start_line")
            end_line = finding.get("end_line")
            if not isinstance(start_line, int) or start_line < 1:
                add_error(errors, f"{location}.start_line", "expected an integer >= 1")
            if not isinstance(end_line, int) or not isinstance(start_line, int) or end_line < start_line:
                add_error(errors, f"{location}.end_line", "must be >= start_line")
            if finding.get("symbol") is not None and not isinstance(finding.get("symbol"), str):
                add_error(errors, f"{location}.symbol", "expected a string or null")
            if finding.get("kind") not in KINDS:
                add_error(errors, f"{location}.kind", "invalid kind")
            if finding.get("status") not in STATUSES:
                add_error(errors, f"{location}.status", "invalid status")
            if finding.get("severity") not in SEVERITIES:
                add_error(errors, f"{location}.severity", "invalid severity")
            if finding.get("confidence") not in CONFIDENCES:
                add_error(errors, f"{location}.confidence", "invalid confidence")
            for field in ("category", "description", "suggested_action"):
                if not isinstance(finding.get(field), str) or not finding.get(field, "").strip():
                    add_error(errors, f"{location}.{field}", "expected a non-empty string")
            if not isinstance(finding.get("impact_assumption"), str):
                add_error(errors, f"{location}.impact_assumption", "expected a string")
            if finding.get("kind") in {"defect", "risk"} and finding.get("severity") is None:
                add_error(errors, f"{location}.severity", "defect and risk findings require severity")
            if finding.get("status") == "hypothesis" and finding.get("confidence") == "high":
                add_error(errors, f"{location}.confidence", "hypothesis cannot have high confidence")
            if finding.get("severity") == "P0" and (
                finding.get("status") == "hypothesis" or not finding.get("impact_assumption", "").strip()
            ):
                add_error(errors, location, "P0 requires non-hypothesis status and an impact assumption")
            evidence = finding.get("evidence")
            if not isinstance(evidence, list) or not evidence:
                add_error(errors, f"{location}.evidence", "expected at least one evidence item")
            else:
                for evidence_index, item in enumerate(evidence):
                    evidence_location = f"{location}.evidence[{evidence_index}]"
                    if not isinstance(item, dict) or set(item) != {"path", "line", "code"}:
                        add_error(errors, evidence_location, "expected path, line, and code")
                        continue
                    if not is_safe_relative_path(item.get("path")):
                        add_error(errors, f"{evidence_location}.path", "expected a safe relative path")
                    if not isinstance(item.get("line"), int) or item.get("line", 0) < 1:
                        add_error(errors, f"{evidence_location}.line", "expected an integer >= 1")
                    if not isinstance(item.get("code"), str) or not item.get("code", "").strip():
                        add_error(errors, f"{evidence_location}.code", "expected a non-empty string")
                    if source_root is not None:
                        validate_evidence_source(item, source_root, evidence_location, errors)

    tool_results = data.get("tool_results")
    if not isinstance(tool_results, list):
        add_error(errors, "tool_results", "expected an array")
    else:
        for index, item in enumerate(tool_results):
            location = f"tool_results[{index}]"
            if not isinstance(item, dict) or set(item) != {"command", "status", "summary"}:
                add_error(errors, location, "expected command, status, and summary")
                continue
            if item.get("status") not in TOOL_STATUSES:
                add_error(errors, f"{location}.status", "invalid status")
            for field in ("command", "summary"):
                if not isinstance(item.get(field), str) or not item.get(field, "").strip():
                    add_error(errors, f"{location}.{field}", "expected a non-empty string")
    return errors


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("report", type=Path)
    parser.add_argument("--source-root", type=Path)
    args = parser.parse_args()

    try:
        data = json.loads(args.report.read_text(encoding="utf-8"))
    except (OSError, UnicodeDecodeError, json.JSONDecodeError) as exc:
        print(f"invalid report: {exc}", file=sys.stderr)
        return 1

    source_root = args.source_root.resolve() if args.source_root else None
    errors = validate_report(data, source_root)
    if errors:
        for error in errors:
            print(f"ERROR: {error}", file=sys.stderr)
        return 1
    print(f"valid defect report: {args.report}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
