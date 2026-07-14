#!/usr/bin/env python3

from __future__ import annotations

import argparse
import re
import xml.etree.ElementTree as ET
from pathlib import Path


ANDROID_NS = "{http://schemas.android.com/apk/res/android}"


def parse_settings_modules(root: Path) -> list[str]:
    settings_files = [root / "settings.gradle.kts", root / "settings.gradle"]
    includes: list[str] = []
    include_re = re.compile(r"include\((.+)\)")
    for settings in settings_files:
        if not settings.exists():
            continue
        for line in settings.read_text(encoding="utf-8").splitlines():
            m = include_re.search(line)
            if not m:
                continue
            body = m.group(1)
            for token in re.findall(r'"(:[^"]+)"|\'(:[^\']+)\'', body):
                mod = token[0] or token[1]
                if mod:
                    includes.append(mod)
    return includes


def module_path(root: Path, module: str) -> Path:
    return root / module.lstrip(":").replace(":", "/")


def read_text_if_exists(path: Path) -> str:
    return path.read_text(encoding="utf-8") if path.exists() else ""


def parse_application_id(module_dir: Path) -> str | None:
    candidates = [module_dir / "build.gradle.kts", module_dir / "build.gradle"]
    patterns = [
        re.compile(r'applicationId\s*=\s*"([^"]+)"'),
        re.compile(r'applicationId\s+"([^"]+)"'),
    ]
    for file in candidates:
        text = read_text_if_exists(file)
        if not text:
            continue
        for pattern in patterns:
            m = pattern.search(text)
            if m:
                return m.group(1).strip()
    return None


def parse_namespace(module_dir: Path) -> str | None:
    candidates = [module_dir / "build.gradle.kts", module_dir / "build.gradle"]
    patterns = [
        re.compile(r'namespace\s*=\s*"([^"]+)"'),
        re.compile(r'namespace\s+"([^"]+)"'),
    ]
    for file in candidates:
        text = read_text_if_exists(file)
        if not text:
            continue
        for pattern in patterns:
            m = pattern.search(text)
            if m:
                return m.group(1).strip()
    return None


def find_launcher_activity(manifest: Path) -> tuple[str | None, str | None]:
    try:
        tree = ET.parse(manifest)
        root = tree.getroot()
    except Exception:
        return (None, None)

    manifest_pkg = root.attrib.get("package")
    app = root.find("application")
    if app is None:
        return (manifest_pkg, None)

    for element in [*app.findall("activity"), *app.findall("activity-alias")]:
        has_main = False
        has_launcher = False
        for intent in element.findall("intent-filter"):
            for action in intent.findall("action"):
                if action.attrib.get(f"{ANDROID_NS}name") == "android.intent.action.MAIN":
                    has_main = True
            for category in intent.findall("category"):
                if category.attrib.get(f"{ANDROID_NS}name") == "android.intent.category.LAUNCHER":
                    has_launcher = True
        if has_main and has_launcher:
            raw_name = element.attrib.get(f"{ANDROID_NS}name")
            if not raw_name:
                return (manifest_pkg, None)
            if raw_name.startswith(".") and manifest_pkg:
                return (manifest_pkg, f"{manifest_pkg}{raw_name}")
            if "." not in raw_name and manifest_pkg:
                return (manifest_pkg, f"{manifest_pkg}.{raw_name}")
            return (manifest_pkg, raw_name)
    return (manifest_pkg, None)


def detect_android_module(root: Path, modules: list[str]) -> tuple[str, Path, Path] | None:
    manifests: list[tuple[str, Path, Path]] = []
    for module in modules:
        mod_dir = module_path(root, module)
        if not mod_dir.exists():
            continue
        for manifest in mod_dir.glob("src/**/AndroidManifest.xml"):
            manifests.append((module, mod_dir, manifest))
    # Prefer manifests with launcher activity.
    for module, mod_dir, manifest in manifests:
        _, activity = find_launcher_activity(manifest)
        if activity:
            return (module, mod_dir, manifest)
    return manifests[0] if manifests else None


def detect_tasks(module: str, module_dir: Path) -> tuple[str, str]:
    _ = module_dir
    module_prefix = module if module != ":" else ""
    if module_prefix:
        return (f"{module_prefix}:connectedDebugAndroidTest", f"{module_prefix}:test")
    return ("connectedDebugAndroidTest", "test")


def first_existing(candidates: list[Path]) -> Path | None:
    for path in candidates:
        if path.exists():
            return path
    return None


def detect_navigation_code(root: Path) -> tuple[Path | None, Path | None]:
    nav_candidates = sorted(root.glob("**/Navigation.kt"))
    destination_candidates = sorted(root.glob("**/AppDestination.kt"))

    nav_code = next((p for p in nav_candidates if "/src/commonMain/" in p.as_posix()), None)
    if nav_code is None and nav_candidates:
        nav_code = nav_candidates[0]

    destination_code = next(
        (p for p in destination_candidates if "/src/commonMain/" in p.as_posix()),
        None,
    )
    if destination_code is None and destination_candidates:
        destination_code = destination_candidates[0]

    return nav_code, destination_code


def detect_docs(root: Path) -> tuple[Path | None, Path | None]:
    nav_doc = first_existing(
        [
            root / "docs/navigation.md",
            root / "docs/navegacion.md",
            root / "docs/NAVIGATION.md",
        ]
    )
    flows_doc = first_existing(
        [
            root / "docs/flows.md",
            root / "docs/flujos.md",
            root / "docs/FLOWS.md",
        ]
    )
    return nav_doc, flows_doc


def print_kv(key: str, value: str | None) -> None:
    if value is None:
        return
    print(f"{key}={value}")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", required=True)
    args = parser.parse_args()

    root = Path(args.root).resolve()
    modules = parse_settings_modules(root)
    if not modules:
        modules = [":"]

    nav_doc, flows_doc = detect_docs(root)
    nav_code, destination_code = detect_navigation_code(root)

    detected = detect_android_module(root, modules)
    if not detected:
        print_kv("DETECTED_CONNECTED_TEST_TASK", "connectedCheck")
        print_kv("DETECTED_UNIT_TEST_TASK", "check")
        print_kv("DETECTED_NAV_DOC", str(nav_doc.resolve()) if nav_doc else None)
        print_kv("DETECTED_FLOWS_DOC", str(flows_doc.resolve()) if flows_doc else None)
        print_kv("DETECTED_NAV_CODE", str(nav_code.resolve()) if nav_code else None)
        print_kv("DETECTED_DESTINATION_CODE", str(destination_code.resolve()) if destination_code else None)
        return 0

    module, mod_dir, manifest = detected

    manifest_pkg, launcher_activity = find_launcher_activity(manifest)
    app_id = parse_application_id(mod_dir) or parse_namespace(mod_dir) or manifest_pkg
    connected_task, unit_task = detect_tasks(module, mod_dir)

    print_kv("DETECTED_MODULE", module)
    print_kv("DETECTED_MODULE_DIR", str(mod_dir.resolve()))
    print_kv("DETECTED_MANIFEST", str(manifest.resolve()))
    print_kv("DETECTED_CONNECTED_TEST_TASK", connected_task)
    print_kv("DETECTED_UNIT_TEST_TASK", unit_task)
    print_kv("DETECTED_APP_ID", app_id)
    print_kv("DETECTED_MAIN_ACTIVITY", launcher_activity)
    print_kv("DETECTED_NAV_DOC", str(nav_doc.resolve()) if nav_doc else None)
    print_kv("DETECTED_FLOWS_DOC", str(flows_doc.resolve()) if flows_doc else None)
    print_kv("DETECTED_NAV_CODE", str(nav_code.resolve()) if nav_code else None)
    print_kv("DETECTED_DESTINATION_CODE", str(destination_code.resolve()) if destination_code else None)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
