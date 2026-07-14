#!/usr/bin/env python3
"""Audit documented navigation/flows against code-registered routes.

Outputs a Markdown report. Returns non-zero only on runtime/parsing errors,
unless --fail-on-drift is enabled.
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path


SECTION_RE = re.compile(r"^##\s+(.+?)\s*$", re.MULTILINE)
ARROW_RE = re.compile(r"`([^`]*->[^`]*)`")
COMPOSABLE_RE = re.compile(r"composable<AppDestination\.([A-Za-z0-9_.]+)")
NAVIGATE_RE = re.compile(r"navigate\(AppDestination\.([A-Za-z0-9_.]+)")


def normalize_route(raw: str) -> str | None:
    value = raw.strip().strip("`").strip()
    value = value.replace("AppDestination.", "")
    value = re.sub(r"\(.*?\)", "", value).strip()
    value = value.rstrip(",.")
    if not value:
        return None
    if value.startswith(("Splash", "Auth.", "Main.")) or value == "Main":
        return value
    return None


def extract_section(md: str, title: str) -> str:
    matches = list(SECTION_RE.finditer(md))
    for i, match in enumerate(matches):
        if match.group(1).strip().lower() == title.strip().lower():
            start = match.end()
            end = matches[i + 1].start() if i + 1 < len(matches) else len(md)
            return md[start:end]
    return ""


def extract_bullet_values(section_text: str) -> list[str]:
    values: list[str] = []
    for line in section_text.splitlines():
        m = re.match(r"^\s*-\s+(.*)$", line)
        if m:
            values.append(m.group(1).strip())
    return values


def routes_from_path_expression(expr: str) -> set[str]:
    routes: set[str] = set()
    steps = [s.strip() for s in expr.split("->")]
    for step in steps:
        for variant in step.split("|"):
            route = normalize_route(variant)
            if route:
                routes.add(route)
    return routes


def build_report(
    nav_doc: Path,
    flows_doc: Path,
    nav_code: Path,
    destination_code: Path,
) -> tuple[str, dict[str, set[str]]]:
    nav_md = nav_doc.read_text(encoding="utf-8")
    flows_md = flows_doc.read_text(encoding="utf-8")
    nav_kt = nav_code.read_text(encoding="utf-8")

    doc_dest_section = extract_section(nav_md, "Destinos registrados")
    doc_destinations = {
        route
        for item in extract_bullet_values(doc_dest_section)
        for route in [normalize_route(item)]
        if route
    }

    flow_section = extract_section(flows_md, "Flujos operativos principales")
    flow_paths = ARROW_RE.findall(flow_section)
    flow_routes = set()
    for path_expr in flow_paths:
        flow_routes.update(routes_from_path_expression(path_expr))

    transitions_section = extract_section(nav_md, "Transiciones observadas en codigo")
    transition_bullets = extract_bullet_values(transitions_section)
    transition_paths = [
        item.replace("`", "").strip()
        for item in transition_bullets
        if "->" in item
    ]
    transition_targets = set()
    for path_expr in transition_paths:
        parts = [s.strip() for s in path_expr.split("->")]
        if len(parts) >= 2:
            target = normalize_route(parts[-1])
            if target:
                transition_targets.add(target)

    code_destinations = set(COMPOSABLE_RE.findall(nav_kt))
    code_destinations = {normalize_route(r) for r in code_destinations}
    code_destinations = {r for r in code_destinations if r}

    navigate_targets = set(NAVIGATE_RE.findall(nav_kt))
    navigate_targets = {normalize_route(r) for r in navigate_targets}
    navigate_targets = {r for r in navigate_targets if r}

    docs_only = doc_destinations - code_destinations
    code_only = code_destinations - doc_destinations
    flow_missing_in_code = flow_routes - code_destinations
    transition_target_without_navigate = transition_targets - navigate_targets

    report = []
    report.append("# Navigation And Flow Audit")
    report.append("")
    report.append("## Inputs")
    report.append(f"- Navigation docs: `{nav_doc}`")
    report.append(f"- Flows docs: `{flows_doc}`")
    report.append(f"- Navigation code: `{nav_code}`")
    report.append(f"- Destination code: `{destination_code}`")
    report.append("")
    report.append("## Summary")
    report.append(f"- Documented destinations: **{len(doc_destinations)}**")
    report.append(f"- Code registered destinations (`composable`): **{len(code_destinations)}**")
    report.append(f"- Flow steps (operational flows): **{len(flow_routes)}**")
    report.append(f"- `navigate(...)` targets in code: **{len(navigate_targets)}**")
    report.append("")

    def emit_list(title: str, values: set[str]) -> None:
        report.append(f"## {title}")
        if not values:
            report.append("- None")
        else:
            for value in sorted(values):
                report.append(f"- `{value}`")
        report.append("")

    emit_list("Docs Destinations Missing In Code", docs_only)
    emit_list("Code Destinations Missing In Docs", code_only)
    emit_list("Flow Steps Missing In Code", flow_missing_in_code)
    emit_list("Transition Targets Without navigate() Evidence", transition_target_without_navigate)

    findings = {
        "docs_only": docs_only,
        "code_only": code_only,
        "flow_missing_in_code": flow_missing_in_code,
        "transition_target_without_navigate": transition_target_without_navigate,
    }
    return "\n".join(report).rstrip() + "\n", findings


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--navigation-doc", required=True)
    parser.add_argument("--flows-doc", required=True)
    parser.add_argument("--navigation-code", required=True)
    parser.add_argument("--destination-code", required=True)
    parser.add_argument("--output", required=True)
    parser.add_argument("--fail-on-drift", action="store_true")
    args = parser.parse_args()

    nav_doc = Path(args.navigation_doc)
    flows_doc = Path(args.flows_doc)
    nav_code = Path(args.navigation_code)
    destination_code = Path(args.destination_code)
    output = Path(args.output)

    required = [nav_doc, flows_doc, nav_code, destination_code]
    missing = [str(p) for p in required if not p.exists()]
    if missing:
        print(f"ERROR: Missing required files: {', '.join(missing)}", file=sys.stderr)
        return 2

    try:
        report, findings = build_report(nav_doc, flows_doc, nav_code, destination_code)
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(report, encoding="utf-8")
    except Exception as exc:  # pylint: disable=broad-except
        print(f"ERROR: audit failed: {exc}", file=sys.stderr)
        return 3

    has_drift = any(findings.values())
    if args.fail_on_drift and has_drift:
        return 10
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
