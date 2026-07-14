#!/usr/bin/env python3

from __future__ import annotations

import argparse
import dataclasses
import re
import subprocess
import time
import xml.etree.ElementTree as ET
from pathlib import Path


BOUNDS_RE = re.compile(r"\[(\d+),(\d+)\]\[(\d+),(\d+)\]")
ARROW_EXPR_RE = re.compile(r"`([^`]*->[^`]*)`")
ROUTE_RE = re.compile(r"\b(?:Splash|Main(?:\.[A-Za-z][A-Za-z0-9]*)?|Auth(?:\.[A-Za-z][A-Za-z0-9]*))\b")
MENU_LABELS = {
    "home",
    "events",
    "book",
    "contact",
    "connect",
    "inbox",
    "my account",
    "account",
    "profile",
}
DEFAULT_MAIN_ROUTES = ["Main.Home", "Main.Events", "Main.Book", "Main.Contact"]
LABEL_OVERRIDES = {
    "Home": ["Home", "Inicio"],
    "Events": ["Events", "Event", "Eventos"],
    "Book": ["Book", "Booking", "Reserva", "Reservar"],
    "Contact": ["Contact", "Contacto"],
    "Connect": ["Connect", "Connections", "Conexiones"],
    "Inbox": ["Inbox", "Messages", "Mensajes"],
    "MyAccount": ["My Account", "Account", "Profile", "Mi cuenta", "Perfil"],
    "PendingConnections": ["Pending Connections", "Pendientes", "Solicitudes"],
}


@dataclasses.dataclass
class Node:
    text: str
    desc: str
    clickable: bool
    enabled: bool
    bounds: tuple[int, int, int, int]

    @property
    def width(self) -> int:
        l, _, r, _ = self.bounds
        return max(0, r - l)

    @property
    def height(self) -> int:
        _, t, _, b = self.bounds
        return max(0, b - t)

    @property
    def center(self) -> tuple[int, int]:
        l, t, r, b = self.bounds
        return ((l + r) // 2, (t + b) // 2)

    @property
    def label(self) -> str:
        return (self.text or self.desc or "").strip()


@dataclasses.dataclass
class StepResult:
    name: str
    status: str
    detail: str


@dataclasses.dataclass
class JourneyPlan:
    routes: list[str]
    detail_sources: set[str]
    wants_profile_shortcut: bool
    source_docs: list[str]


class Adb:
    def __init__(self, adb_bin: str, device_id: str):
        self.adb_bin = adb_bin
        self.device_id = device_id

    def run(self, args: list[str], check: bool = True) -> subprocess.CompletedProcess[str]:
        cmd = [self.adb_bin, "-s", self.device_id] + args
        return subprocess.run(cmd, capture_output=True, text=True, check=check)

    def shell(self, cmd: str, check: bool = True) -> subprocess.CompletedProcess[str]:
        return self.run(["shell", cmd], check=check)

    def tap(self, x: int, y: int) -> None:
        self.shell(f"input tap {x} {y}")

    def swipe(self, x1: int, y1: int, x2: int, y2: int, duration_ms: int = 250) -> None:
        self.shell(f"input swipe {x1} {y1} {x2} {y2} {duration_ms}")

    def back(self) -> None:
        self.shell("input keyevent 4")

    def screen_size(self) -> tuple[int, int]:
        out = self.shell("wm size").stdout
        match = re.search(r"(\d+)x(\d+)", out)
        if not match:
            return (1080, 1920)
        return int(match.group(1)), int(match.group(2))

    def dump_nodes(self) -> list[Node]:
        self.shell("uiautomator dump /sdcard/window_dump.xml >/dev/null 2>&1", check=False)
        xml_text = self.shell("cat /sdcard/window_dump.xml", check=False).stdout
        if not xml_text.strip():
            return []
        try:
            root = ET.fromstring(xml_text)
        except ET.ParseError:
            return []

        nodes: list[Node] = []
        for el in root.iter("node"):
            bounds_raw = el.attrib.get("bounds", "")
            match = BOUNDS_RE.match(bounds_raw)
            if not match:
                continue
            bounds = tuple(int(match.group(i)) for i in range(1, 5))
            nodes.append(
                Node(
                    text=(el.attrib.get("text") or "").strip(),
                    desc=(el.attrib.get("content-desc") or "").strip(),
                    clickable=el.attrib.get("clickable") == "true",
                    enabled=el.attrib.get("enabled") == "true",
                    bounds=bounds,
                )
            )
        return nodes


def norm(value: str) -> str:
    return re.sub(r"\s+", " ", value.strip().lower())


def normalize_route(route: str) -> str | None:
    clean = route.strip().strip("`").strip()
    clean = re.sub(r"\(.*?\)", "", clean).strip()
    if not clean:
        return None
    if clean.startswith(("Main.", "Auth.")) or clean == "Splash":
        return clean
    return None


def is_detail_route(route: str) -> bool:
    token = route.split(".")[-1]
    return token.endswith("Detail") or "Detail" in token


def is_primary_main_route(route: str) -> bool:
    if not route.startswith("Main."):
        return False
    token = route.split(".")[-1]
    return not (is_detail_route(route) or token in {"Chat"})


def split_camel(token: str) -> str:
    return re.sub(r"(?<!^)([A-Z])", r" \1", token).strip()


def dedupe(values: list[str]) -> list[str]:
    seen: set[str] = set()
    ordered: list[str] = []
    for value in values:
        key = norm(value)
        if not key or key in seen:
            continue
        seen.add(key)
        ordered.append(value)
    return ordered


def labels_for_route(route: str) -> list[str]:
    token = route.split(".")[-1]
    token = re.sub(r"\(.*?\)", "", token)
    spaced = split_camel(token)
    compact = spaced.replace(" ", "")

    labels = LABEL_OVERRIDES.get(token, []).copy()
    labels.extend([spaced, compact])
    if spaced.startswith("My "):
        labels.append(spaced[3:])
    if " " in spaced:
        labels.append(spaced.split(" ")[0])
    return dedupe(labels)


def read_optional(path: str | None) -> tuple[str, str | None]:
    if not path:
        return "", None
    p = Path(path)
    if not p.exists():
        return "", None
    try:
        return p.read_text(encoding="utf-8"), str(p.resolve())
    except Exception:
        return "", None


def parse_routes_from_text(text: str) -> list[str]:
    routes = [normalize_route(r) for r in ROUTE_RE.findall(text)]
    return [route for route in routes if route]


def build_plan(navigation_doc: str | None, flows_doc: str | None) -> JourneyPlan:
    nav_text, nav_path = read_optional(navigation_doc)
    flows_text, flows_path = read_optional(flows_doc)

    combined = "\n".join([nav_text, flows_text]).strip()
    if not combined:
        return JourneyPlan(
            routes=DEFAULT_MAIN_ROUTES.copy(),
            detail_sources={"Main.Home", "Main.Events"},
            wants_profile_shortcut=True,
            source_docs=[],
        )

    docs_used = [path for path in [nav_path, flows_path] if path]
    routes_in_order: list[str] = []
    detail_sources: set[str] = set()
    wants_profile_shortcut = "TopBar(Profile)" in combined or "Main.MyAccount" in combined

    for expr in ARROW_EXPR_RE.findall(combined):
        raw_steps = [step.strip() for step in expr.split("->")]
        parsed_steps: list[list[str]] = []
        for step in raw_steps:
            if "TopBar(Profile" in step:
                wants_profile_shortcut = True
            routes = parse_routes_from_text(step)
            parsed_steps.append(routes)

        prev_main: str | None = None
        for routes in parsed_steps:
            if not routes:
                continue
            if prev_main and any(is_detail_route(route) for route in routes):
                detail_sources.add(prev_main)

            main_routes = [route for route in routes if route.startswith("Main.")]
            if main_routes:
                chosen = main_routes[0]
                if is_primary_main_route(chosen) and chosen not in routes_in_order:
                    routes_in_order.append(chosen)
                    prev_main = chosen

    for route in parse_routes_from_text(combined):
        if is_primary_main_route(route) and route not in routes_in_order:
            routes_in_order.append(route)

    if not routes_in_order:
        routes_in_order = DEFAULT_MAIN_ROUTES.copy()

    if not detail_sources:
        for default_source in ["Main.Home", "Main.Events"]:
            if default_source in routes_in_order:
                detail_sources.add(default_source)

    return JourneyPlan(
        routes=routes_in_order,
        detail_sources=detail_sources,
        wants_profile_shortcut=wants_profile_shortcut,
        source_docs=docs_used,
    )


def find_label_node(nodes: list[Node], labels: list[str], clickable_only: bool = True) -> Node | None:
    targets = {norm(label) for label in labels}
    exact: list[Node] = []
    contains: list[Node] = []
    for node in nodes:
        if clickable_only and not (node.clickable and node.enabled):
            continue
        values = [norm(node.text), norm(node.desc)]
        for value in values:
            if not value:
                continue
            if value in targets:
                exact.append(node)
            elif any(target in value for target in targets):
                contains.append(node)
    if exact:
        return exact[0]
    if contains:
        return contains[0]
    return None


def tap_label(adb: Adb, labels: list[str], timeout_s: float = 8.0) -> bool:
    end = time.time() + timeout_s
    while time.time() < end:
        node = find_label_node(adb.dump_nodes(), labels, clickable_only=False)
        if node:
            x, y = node.center
            adb.tap(x, y)
            return True
        time.sleep(0.4)
    return False


def wait_label(adb: Adb, labels: list[str], timeout_s: float = 8.0) -> bool:
    end = time.time() + timeout_s
    while time.time() < end:
        node = find_label_node(adb.dump_nodes(), labels, clickable_only=False)
        if node:
            return True
        time.sleep(0.4)
    return False


def tap_content_card(adb: Adb, width: int, height: int) -> bool:
    nodes = adb.dump_nodes()
    candidates: list[Node] = []
    for node in nodes:
        if not (node.clickable and node.enabled):
            continue
        label = norm(node.label)
        if label and label in MENU_LABELS:
            continue
        cx, cy = node.center
        if cy < int(height * 0.22) or cy > int(height * 0.82):
            continue
        if node.width < int(width * 0.45):
            continue
        if node.height < int(height * 0.06):
            continue
        candidates.append(node)
    if not candidates:
        return False
    candidates.sort(key=lambda node: node.center[1])
    x, y = candidates[0].center
    adb.tap(x, y)
    return True


def write_report(path: Path, steps: list[StepResult]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    ok_count = sum(1 for step in steps if step.status == "OK")
    fail_count = sum(1 for step in steps if step.status == "FAIL")
    warn_count = sum(1 for step in steps if step.status == "WARN")
    lines = [
        "# UI Journey Report",
        "",
        f"- OK: **{ok_count}**",
        f"- WARN: **{warn_count}**",
        f"- FAIL: **{fail_count}**",
        "",
        "## Steps",
    ]
    for step in steps:
        lines.append(f"- [{step.status}] {step.name}: {step.detail}")
    lines.append("")
    path.write_text("\n".join(lines), encoding="utf-8")


def route_step_name(route: str) -> str:
    return route.lower().replace(".", "-")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--adb", required=True)
    parser.add_argument("--device", required=True)
    parser.add_argument("--app-id", required=True)
    parser.add_argument("--main-activity", required=True)
    parser.add_argument("--output", required=True)
    parser.add_argument("--skip-launch", action="store_true")
    parser.add_argument("--navigation-doc")
    parser.add_argument("--flows-doc")
    args = parser.parse_args()

    plan = build_plan(args.navigation_doc, args.flows_doc)
    adb = Adb(args.adb, args.device)
    steps: list[StepResult] = []

    docs_label = ", ".join(plan.source_docs) if plan.source_docs else "fallback defaults"
    steps.append(
        StepResult(
            "journey-plan",
            "OK",
            f"routes={', '.join(plan.routes)} | detail_from={', '.join(sorted(plan.detail_sources)) or 'none'} | docs={docs_label}",
        )
    )

    try:
        width, height = adb.screen_size()
    except Exception as exc:  # pylint: disable=broad-except
        steps.append(StepResult("read-screen-size", "FAIL", str(exc)))
        write_report(Path(args.output), steps)
        return 2

    if not args.skip_launch:
        launch = adb.shell(f"am start -W -n {args.app_id}/{args.main_activity}", check=False)
        if launch.returncode != 0:
            steps.append(StepResult("launch-app", "FAIL", "am start failed"))
            write_report(Path(args.output), steps)
            return 3
        steps.append(StepResult("launch-app", "OK", "app launched"))
        time.sleep(1.5)
    else:
        steps.append(StepResult("launch-app", "OK", "skipped (already launched by caller)"))

    if tap_label(adb, ["Sign In", "Iniciar sesion"], timeout_s=3.0):
        steps.append(StepResult("welcome-sign-in", "OK", "auth entry tapped"))
        time.sleep(1.2)
    else:
        steps.append(StepResult("welcome-sign-in", "WARN", "auth entry not visible"))

    if tap_label(adb, ["Login", "Entrar", "Acceder"], timeout_s=3.0):
        steps.append(StepResult("login-submit", "OK", "login submit tapped"))
        time.sleep(2.0)
    else:
        steps.append(StepResult("login-submit", "WARN", "login submit not visible"))

    nav_probe_labels: list[str] = []
    for route in plan.routes[:6]:
        labels = labels_for_route(route)
        if labels:
            nav_probe_labels.append(labels[0])
    if not nav_probe_labels:
        nav_probe_labels = ["Home", "Events", "Book", "Contact"]

    if wait_label(adb, nav_probe_labels, timeout_s=12.0):
        steps.append(StepResult("main-navigation-visible", "OK", f"detected labels: {', '.join(nav_probe_labels)}"))
    else:
        steps.append(StepResult("main-navigation-visible", "WARN", "navigation labels not detected"))

    visited_routes = 0
    for route in plan.routes:
        labels = labels_for_route(route)
        step_name = route_step_name(route)
        if tap_label(adb, labels, timeout_s=4.0):
            visited_routes += 1
            steps.append(StepResult(step_name, "OK", f"opened via labels: {', '.join(labels[:3])}"))
            time.sleep(1.0)
            adb.swipe(width // 2, int(height * 0.78), width // 2, int(height * 0.35), 280)
            time.sleep(0.4)
            adb.swipe(width // 2, int(height * 0.42), width // 2, int(height * 0.80), 260)
            time.sleep(0.5)
            if route in plan.detail_sources:
                if tap_content_card(adb, width, height):
                    steps.append(StepResult(f"{step_name}-open-detail", "OK", "opened content card"))
                    time.sleep(1.2)
                    adb.back()
                    time.sleep(0.8)
                else:
                    steps.append(StepResult(f"{step_name}-open-detail", "WARN", "no tappable card found"))
        else:
            steps.append(StepResult(step_name, "WARN", f"could not open route by labels: {', '.join(labels[:3])}"))

    if plan.wants_profile_shortcut:
        account_labels = labels_for_route("Main.MyAccount")
        if tap_label(adb, account_labels, timeout_s=2.0):
            steps.append(StepResult("profile-shortcut", "OK", "opened account through visible label"))
            adb.back()
            time.sleep(0.8)
        else:
            adb.tap(int(width * 0.08), int(height * 0.08))
            time.sleep(1.0)
            if wait_label(adb, account_labels, timeout_s=2.0):
                steps.append(StepResult("profile-shortcut", "OK", "opened account through top-left tap"))
                adb.back()
            else:
                steps.append(StepResult("profile-shortcut", "WARN", "account screen not detected after shortcut tap"))

    write_report(Path(args.output), steps)

    if visited_routes >= 2:
        return 0
    return 10


if __name__ == "__main__":
    raise SystemExit(main())
