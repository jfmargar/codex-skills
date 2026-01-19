#!/usr/bin/env python3
import json
import os
import re
import sys
from typing import Dict, Iterable, List, Set

SKIP_DIRS = {
    ".git",
    ".gradle",
    ".idea",
    "build",
    "dist",
    "out",
}

NAV_GRAPH_RE = re.compile(r"\b(\w+NavGraph)\b")
COMPOSABLE_SCREEN_RE = re.compile(r"@Composable\s+fun\s+(\w+Screen)\s*\(")
SEALED_UISTATE_CLASS_RE = re.compile(r"\bsealed\s+class\s+(\w+UiState)\b")
SEALED_UISTATE_INTERFACE_RE = re.compile(r"\bsealed\s+interface\s+(\w+UiState)\b")
BOTTOM_SHEET_RE = re.compile(r"\b(\w+BottomSheet)\b")
MODAL_BOTTOM_SHEET_RE = re.compile(r"\bModalBottomSheet\b")

BLOCK_COMMENT_RE = re.compile(r"/\*.*?\*/", re.DOTALL)
LINE_COMMENT_RE = re.compile(r"//.*?$", re.MULTILINE)


def iter_kotlin_files(root: str) -> Iterable[str]:
    for dirpath, dirnames, filenames in os.walk(root):
        dirnames[:] = [d for d in dirnames if d not in SKIP_DIRS]
        for filename in sorted(filenames):
            if filename.endswith(".kt"):
                yield os.path.join(dirpath, filename)


def strip_comments(text: str) -> str:
    text = BLOCK_COMMENT_RE.sub("", text)
    text = LINE_COMMENT_RE.sub("", text)
    return text


def find_ui_states(text: str) -> Set[str]:
    states = set()
    for match in SEALED_UISTATE_CLASS_RE.finditer(text):
        states.add(match.group(1))
    for match in SEALED_UISTATE_INTERFACE_RE.finditer(text):
        states.add(match.group(1))
    return states


def find_ui_state_refs(text: str, ui_states: Set[str]) -> Set[str]:
    refs = set()
    for state in ui_states:
        if re.search(r"\b" + re.escape(state) + r"\b", text):
            refs.add(state)
    return refs


def find_bottom_sheets(text: str) -> Set[str]:
    sheets = set()
    for match in BOTTOM_SHEET_RE.finditer(text):
        sheets.add(match.group(1))
    if MODAL_BOTTOM_SHEET_RE.search(text):
        sheets.add("ModalBottomSheet")
    return sheets


def collect_structure(root: str) -> Dict[str, List[dict]]:
    screens = set()
    nav_graphs = set()
    ui_states = set()

    files = list(iter_kotlin_files(root))
    contents: Dict[str, str] = {}
    for path in files:
        try:
            with open(path, "r", encoding="utf-8") as f:
                contents[path] = strip_comments(f.read())
        except OSError:
            continue

    for text in contents.values():
        for match in NAV_GRAPH_RE.finditer(text):
            nav_graphs.add(match.group(1))
        for match in COMPOSABLE_SCREEN_RE.finditer(text):
            screens.add(match.group(1))
        ui_states.update(find_ui_states(text))

    navigation = []
    for text in contents.values():
        screen_names = set(match.group(1) for match in COMPOSABLE_SCREEN_RE.finditer(text))
        if not screen_names:
            continue

        ui_state_refs = find_ui_state_refs(text, ui_states)
        if not ui_state_refs:
            continue

        sheets = find_bottom_sheets(text)
        if not sheets:
            continue

        for screen in sorted(screen_names):
            for sheet in sorted(sheets):
                navigation.append(
                    {
                        "from": screen,
                        "to": sheet,
                        "event": "state_driven_sheet",
                    }
                )

    all_screens = sorted(screens.union(nav_graphs))
    navigation.sort(key=lambda item: (item["from"], item["to"], item["event"]))

    return {
        "screens": all_screens,
        "navigation": navigation,
        "uiStates": sorted(ui_states),
    }


def resolve_project_root(argv: List[str]) -> str:
    if len(argv) < 2:
        raise ValueError("Missing project path argument.")
    root = os.path.abspath(argv[1])
    if not os.path.isdir(root):
        raise ValueError(f"Project path is not a directory: {root}")
    return root


def main() -> int:
    try:
        project_root = resolve_project_root(sys.argv)
    except ValueError as exc:
        print(f"Error: {exc}")
        return 1

    output_path = os.path.join(project_root, "docs", "structure.json")
    structure = collect_structure(project_root)
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(structure, f, indent=2)
        f.write("\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
