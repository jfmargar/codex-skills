#!/usr/bin/env python3
import re
from pathlib import Path
from typing import Dict, Iterable, List

from extract_structure import collect_structure, iter_kotlin_files

ANDROID_ACTIVITY_RE = re.compile(r"\bclass\s+(\w*MainActivity)\b")
IOS_VIEW_CONTROLLER_RE = re.compile(r"\bclass\s+(\w*MainViewController)\b")
COMPOSE_CONTROLLER_RE = re.compile(r"\bComposeUIViewController\s*\{")
APP_FUNCTION_RE = re.compile(r"\bfun\s+App\s*\(")
NAV_GRAPH_RE = re.compile(r"\b(\w+NavGraph)\b")
UISTATE_RE = re.compile(r"\b(\w+UiState)\b")
BOTTOM_SHEET_RE = re.compile(r"\b(\w+BottomSheet)\b")
MODAL_BOTTOM_SHEET_RE = re.compile(r"\bModalBottomSheet\b")
VIEWMODEL_RE = re.compile(r"\bclass\s+(\w+ViewModel)\b")
COMPOSABLE_ROUTE_RE = re.compile(r'\bcomposable\s*\(\s*["\']([^"\']+)["\']')
COMPOSABLE_ROUTE_NAMED_RE = re.compile(r'\bcomposable\s*\(\s*route\s*=\s*["\']([^"\']+)["\']')

CODE_BLOCK_RE = re.compile(r"^```")
HEADING_RE = re.compile(r"^(#+)\s+(.*)$")
PLACEHOLDER_RE = re.compile(r"{{\w+}}")

MAX_LIST_ITEMS = 12


def read_text(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except OSError:
        return ""


def rel_path(path: Path, root: Path) -> str:
    try:
        return str(path.relative_to(root))
    except ValueError:
        return str(path)


def template_has_placeholders(text: str) -> bool:
    return bool(PLACEHOLDER_RE.search(text))


def fill_template(template: str, data: Dict[str, str]) -> str:
    for key, value in data.items():
        template = template.replace("{{" + key + "}}", value)
    return template


def load_template_with_fallback(path: Path, fallback: str) -> str:
    template = read_text(path)
    if template.strip() and template_has_placeholders(template):
        return template
    return fallback


def find_entry_points(kotlin_files: Iterable[Path], project_root: Path) -> Dict[str, List[str]]:
    entries = {"android": [], "ios": [], "app": []}
    for file_path in kotlin_files:
        text = read_text(file_path)
        if "androidMain" in file_path.parts:
            for match in ANDROID_ACTIVITY_RE.findall(text):
                entries["android"].append(f"{match} ({rel_path(file_path, project_root)})")
        if "iosMain" in file_path.parts:
            for match in IOS_VIEW_CONTROLLER_RE.findall(text):
                entries["ios"].append(f"{match} ({rel_path(file_path, project_root)})")
            if COMPOSE_CONTROLLER_RE.search(text):
                entries["ios"].append(f"ComposeUIViewController ({rel_path(file_path, project_root)})")
        if APP_FUNCTION_RE.search(text):
            entries["app"].append(f"App() ({rel_path(file_path, project_root)})")
    for key in entries:
        entries[key] = sorted(set(entries[key]))
    return entries


def collect_named_symbols(kotlin_files: Iterable[Path], pattern: re.Pattern) -> List[str]:
    symbols = set()
    for file_path in kotlin_files:
        text = read_text(file_path)
        for match in pattern.findall(text):
            symbols.add(match)
    return sorted(symbols)


def collect_files_with_patterns(
    kotlin_files: Iterable[Path],
    project_root: Path,
    patterns: Dict[str, re.Pattern],
) -> Dict[str, List[str]]:
    results = {label: [] for label in patterns}
    for file_path in kotlin_files:
        text = read_text(file_path)
        for label, pattern in patterns.items():
            if pattern.search(text):
                results[label].append(rel_path(file_path, project_root))
    for label in results:
        results[label] = sorted(set(results[label]))[:MAX_LIST_ITEMS]
    return results


def summarize_flows(text: str, max_items: int = 6) -> List[str]:
    lines = text.splitlines()
    in_code_block = False
    current_heading = None
    current_paragraph: List[str] = []
    summaries = []

    def flush():
        nonlocal current_heading, current_paragraph
        if not current_heading or not current_paragraph:
            current_heading = None
            current_paragraph = []
            return
        summary = " ".join(current_paragraph).strip()
        if summary:
            summary = summary[:200].rstrip()
            summaries.append(f"- {current_heading}: {summary}")
        current_heading = None
        current_paragraph = []

    for line in lines:
        if CODE_BLOCK_RE.match(line.strip()):
            in_code_block = not in_code_block
            continue
        if in_code_block:
            continue
        heading_match = HEADING_RE.match(line.strip())
        if heading_match:
            flush()
            current_heading = heading_match.group(2).strip()
            continue
        if current_heading and line.strip():
            if line.strip().startswith("!"):
                continue
            current_paragraph.append(line.strip())
        if len(summaries) >= max_items:
            break
    if len(summaries) < max_items:
        flush()
    return summaries[:max_items]


def detect_modules(project_root: Path) -> List[str]:
    candidates = ["composeApp", "shared", "androidApp", "iosApp"]
    modules = [name for name in candidates if (project_root / name).is_dir()]
    settings_gradle = project_root / "settings.gradle.kts"
    if not settings_gradle.exists():
        settings_gradle = project_root / "settings.gradle"
    if settings_gradle.exists():
        text = read_text(settings_gradle)
        for match in re.findall(r"include\(([^)]+)\)", text):
            for raw in match.split(","):
                name = raw.strip().strip('"').strip("'").strip(":")
                if name:
                    modules.append(name)
    return sorted(set(modules))


def find_common_main(project_root: Path, modules: List[str]) -> List[str]:
    common_paths = []
    for module in modules:
        path = project_root / module / "src" / "commonMain"
        if path.is_dir():
            common_paths.append(str(path.relative_to(project_root)))
    return common_paths


def find_layer_paths(project_root: Path, common_main_paths: List[str]) -> Dict[str, List[str]]:
    layers = {"domain": [], "data": [], "ui": []}
    for common_path in common_main_paths:
        root = project_root / common_path
        for layer in layers:
            for path in root.rglob(layer):
                if path.is_dir():
                    layers[layer].append(str(path.relative_to(project_root)))
    for layer in layers:
        layers[layer] = sorted(set(layers[layer]))[:MAX_LIST_ITEMS]
    return layers


def extract_gradle_dependencies(text: str) -> List[str]:
    deps = []
    pattern = re.compile(r"^\s*(implementation|api|kapt|ksp)\s*\(?\s*[\"'](.+?)[\"']\s*\)?", re.MULTILINE)
    for match in pattern.findall(text):
        deps.append(match[1])
    return deps


def classify_dependencies(deps: List[str]) -> Dict[str, List[str]]:
    buckets = {
        "di": [],
        "network": [],
        "db": [],
        "serialization": [],
        "async": [],
        "navigation": [],
        "logging": [],
        "analytics": [],
        "testing": [],
        "other": [],
    }
    for dep in deps:
        lowered = dep.lower()
        if "koin" in lowered or "dagger" in lowered or "hilt" in lowered:
            buckets["di"].append(dep)
        elif "ktor" in lowered or "retrofit" in lowered or "okhttp" in lowered:
            buckets["network"].append(dep)
        elif "room" in lowered or "sqldelight" in lowered or "datastore" in lowered:
            buckets["db"].append(dep)
        elif "serialization" in lowered or "moshi" in lowered or "gson" in lowered:
            buckets["serialization"].append(dep)
        elif "coroutines" in lowered or "rxjava" in lowered:
            buckets["async"].append(dep)
        elif "navigation" in lowered:
            buckets["navigation"].append(dep)
        elif "timber" in lowered or "logger" in lowered:
            buckets["logging"].append(dep)
        elif "firebase" in lowered or "analytics" in lowered or "crashlytics" in lowered:
            buckets["analytics"].append(dep)
        elif "junit" in lowered or "kotest" in lowered or "mock" in lowered or "espresso" in lowered:
            buckets["testing"].append(dep)
        else:
            buckets["other"].append(dep)
    return buckets


def collect_compose_routes(kotlin_files: Iterable[Path]) -> List[str]:
    routes = set()
    for file_path in kotlin_files:
        text = read_text(file_path)
        for match in COMPOSABLE_ROUTE_RE.findall(text):
            routes.add(match)
        for match in COMPOSABLE_ROUTE_NAMED_RE.findall(text):
            routes.add(match)
    return sorted(routes)


def build_navigation_doc(
    project_root: Path,
    structure: Dict[str, List[dict]],
    flows_summary: List[str],
    flows_exists: bool,
    entry_points: Dict[str, List[str]],
    kotlin_files: List[Path],
    routes: List[str],
) -> str:
    sheets = collect_named_symbols(kotlin_files, BOTTOM_SHEET_RE)
    if any(MODAL_BOTTOM_SHEET_RE.search(read_text(path)) for path in kotlin_files):
        sheets.append("ModalBottomSheet")
        sheets = sorted(set(sheets))

    files_with = collect_files_with_patterns(
        kotlin_files,
        project_root,
        {
            "NavGraph": NAV_GRAPH_RE,
            "UiState": UISTATE_RE,
            "BottomSheet": BOTTOM_SHEET_RE,
        },
    )

    lines = [
        "# Navegacion y pantallas",
        "",
        "Referencias relacionadas:",
        "- Overview: [docs/overview.md](overview.md)",
        "- Flujos: [docs/flows.md](flows.md)",
        "",
        "## Puntos de entrada",
    ]

    if entry_points["android"]:
        lines.append("- Android: " + ", ".join(entry_points["android"]))
    if entry_points["ios"]:
        lines.append("- iOS: " + ", ".join(entry_points["ios"]))
    if entry_points["app"]:
        lines.append("- App root: " + ", ".join(entry_points["app"]))
    if not any(entry_points.values()):
        lines.append("- No se detectaron puntos de entrada.")

    lines += ["", "## Resumen de flows.md"]
    if flows_exists and flows_summary:
        lines.extend(flows_summary)
    elif flows_exists:
        lines.append("- Ver docs/flows.md para el resumen completo.")
    else:
        lines.append("- docs/flows.md no existe en el proyecto.")

    lines += ["", "## Estructura detectada"]
    if structure.get("screens"):
        lines.append("- Pantallas: " + ", ".join(structure["screens"][:MAX_LIST_ITEMS]))
    else:
        lines.append("- Pantallas: no detectadas.")

    if structure.get("uiStates"):
        lines.append("- UiStates: " + ", ".join(structure["uiStates"][:MAX_LIST_ITEMS]))
    else:
        lines.append("- UiStates: no detectados.")

    nav_graphs = [name for name in structure.get("screens", []) if name.endswith("NavGraph")]
    if nav_graphs:
        lines.append("- NavGraphs: " + ", ".join(nav_graphs[:MAX_LIST_ITEMS]))
    else:
        lines.append("- NavGraphs: no detectados.")

    if sheets:
        lines.append("- BottomSheets: " + ", ".join(sheets[:MAX_LIST_ITEMS]))
    else:
        lines.append("- BottomSheets: no detectados.")

    if routes:
        lines.append("- Rutas composable: " + ", ".join(routes[:MAX_LIST_ITEMS]))
    else:
        lines.append("- Rutas composable: no detectadas.")

    if structure.get("navigation"):
        lines += ["", "## Navegacion inferida (sheets)"]
        for item in structure["navigation"][:MAX_LIST_ITEMS]:
            lines.append(f"- {item['from']} -> {item['to']} ({item['event']})")

    lines += ["", "## Archivos relevantes"]
    any_files = False
    for label, paths in files_with.items():
        if paths:
            any_files = True
            lines.append(f"- {label}: " + ", ".join(paths))
    if not any_files:
        lines.append("- No se detectaron archivos relevantes.")

    return "\n".join(lines).rstrip() + "\n"


def build_overview_doc(
    project_root: Path,
    structure: Dict[str, List[dict]],
    flows_exists: bool,
    entry_points: Dict[str, List[str]],
    modules: List[str],
    common_main_paths: List[str],
    layer_paths: Dict[str, List[str]],
) -> str:
    lines = [
        "# Overview",
        "",
        "## Referencias",
        "- Arquitectura: [docs/architecture.md](architecture.md)",
        "- Navegacion y sheets: [docs/navigation.md](navigation.md)",
    ]
    if flows_exists:
        lines.append("- Flujos resumidos: [docs/flows.md](flows.md)")
    else:
        lines.append("- Flujos resumidos: docs/flows.md no existe")

    lines += ["", "## Arranque y estructura base"]
    if modules:
        lines.append("- Modulos detectados: " + ", ".join(modules))
    else:
        lines.append("- Modulos detectados: no se detectaron.")

    if entry_points["android"]:
        lines.append("- Android entry: " + ", ".join(entry_points["android"]))
    if entry_points["ios"]:
        lines.append("- iOS entry: " + ", ".join(entry_points["ios"]))
    if entry_points["app"]:
        lines.append("- UI raiz: " + ", ".join(entry_points["app"]))

    lines += ["", "## Codigo compartido"]
    if common_main_paths:
        lines.append("- commonMain: " + ", ".join(common_main_paths))
    else:
        lines.append("- commonMain: no detectado.")

    lines += ["", "## Arquitectura (resumen)"]
    layer_lines = []
    for layer, paths in layer_paths.items():
        if paths:
            layer_lines.append(f"{layer}: " + ", ".join(paths))
    if layer_lines:
        for item in layer_lines:
            lines.append(f"- {item}")
    else:
        lines.append("- Capas no detectadas en commonMain.")

    lines += ["", "## Navegacion y flujos"]
    screen_count = len(structure.get("screens", []))
    ui_state_count = len(structure.get("uiStates", []))
    lines.append(f"- Pantallas detectadas: {screen_count}")
    lines.append(f"- UiStates detectados: {ui_state_count}")

    return "\n".join(lines).rstrip() + "\n"


def build_architecture_doc(data: Dict[str, str]) -> str:
    default_template = (
        "# Arquitectura\n\n"
        "## Modulos\n\n"
        "{{modules}}\n\n"
        "## Puntos de entrada\n\n"
        "{{entry_points}}\n\n"
        "## Codigo compartido\n\n"
        "{{common_main}}\n\n"
        "## Capas y paquetes\n\n"
        "{{layers}}\n\n"
        "## Componentes clave\n\n"
        "{{key_components}}\n\n"
        "## Dependencias relevantes\n\n"
        "{{dependencies}}\n\n"
        "{{architecture_diagram}}"
    )
    return fill_template(default_template, data).rstrip() + "\n"


def main() -> int:
    project_root = Path.cwd().resolve()
    docs_dir = project_root / "docs"
    docs_dir.mkdir(exist_ok=True)

    skill_root = Path(__file__).parent.resolve()
    architecture_source = skill_root / "assets" / "architecture.md"
    agents_source = skill_root / "assets" / "AGENTS.md"

    kotlin_files = [Path(path) for path in iter_kotlin_files(str(project_root))]
    structure = collect_structure(str(project_root))

    entry_points = find_entry_points(kotlin_files, project_root)
    modules = detect_modules(project_root)
    common_main_paths = find_common_main(project_root, modules)
    layer_paths = find_layer_paths(project_root, common_main_paths)
    viewmodels = collect_named_symbols(kotlin_files, VIEWMODEL_RE)

    gradle_files = []
    for name in ["build.gradle.kts", "build.gradle"]:
        root_path = project_root / name
        if root_path.exists():
            gradle_files.append(root_path)
    for module in modules:
        for name in ["build.gradle.kts", "build.gradle"]:
            module_path = project_root / module / name
            if module_path.exists():
                gradle_files.append(module_path)

    deps = []
    for path in gradle_files:
        deps.extend(extract_gradle_dependencies(read_text(path)))
    deps = sorted(set(deps))
    deps_bucket = classify_dependencies(deps)

    flows_path = docs_dir / "flows.md"
    flows_exists = flows_path.exists()
    flows_text = read_text(flows_path) if flows_exists else ""
    flows_summary = summarize_flows(flows_text)

    routes = collect_compose_routes(kotlin_files)

    entry_points_block = []
    if entry_points["android"]:
        entry_points_block.append("- Android: " + ", ".join(entry_points["android"]))
    if entry_points["ios"]:
        entry_points_block.append("- iOS: " + ", ".join(entry_points["ios"]))
    if entry_points["app"]:
        entry_points_block.append("- App root: " + ", ".join(entry_points["app"]))
    if not entry_points_block:
        entry_points_block.append("- No se detectaron puntos de entrada.")

    common_block = "- " + "\n- ".join(common_main_paths) if common_main_paths else "- commonMain no detectado."

    layer_lines = []
    for layer, paths in layer_paths.items():
        if paths:
            layer_lines.append("- {}: {}".format(layer, ", ".join(paths)))
    layers_block = "\n".join(layer_lines) if layer_lines else "- Capas no detectadas en commonMain."

    components = []
    if viewmodels:
        components.append("- ViewModels: " + ", ".join(viewmodels[:MAX_LIST_ITEMS]))
    if routes:
        components.append("- Rutas composable: " + ", ".join(routes[:MAX_LIST_ITEMS]))
    components_block = "\n".join(components) if components else "- No se detectaron componentes clave."

    deps_lines = []
    for key, label in [
        ("di", "DI"),
        ("network", "Networking"),
        ("db", "Persistencia"),
        ("serialization", "Serializacion"),
        ("async", "Async"),
        ("navigation", "Navigation"),
        ("logging", "Logging"),
        ("analytics", "Analytics"),
        ("testing", "Testing"),
        ("other", "Otros"),
    ]:
        if deps_bucket[key]:
            deps_lines.append("- {}:".format(label))
            deps_lines.extend(["  - `{}`".format(dep) for dep in deps_bucket[key][:MAX_LIST_ITEMS]])
            if len(deps_bucket[key]) > MAX_LIST_ITEMS:
                deps_lines.append("  - (mas dependencias omitidas)")
    deps_block = "\n".join(deps_lines) if deps_lines else "- No se detectaron dependencias."

    diagram = ""
    if modules:
        diagram = "## Diagrama de modulos\n\n```mermaid\ngraph TD;\n"
        for module in modules:
            node = module.replace("-", "_")
            diagram += f"A[Repositorio] --> {node}[{module}];\n"
        diagram += "```\n"

    architecture_data = {
        "modules": "- " + "\n- ".join(modules) if modules else "- No se detectaron modulos.",
        "entry_points": "\n".join(entry_points_block),
        "common_main": common_block,
        "layers": layers_block,
        "key_components": components_block,
        "dependencies": deps_block,
        "architecture_diagram": diagram,
    }

    navigation_doc = build_navigation_doc(
        project_root,
        structure,
        flows_summary,
        flows_exists,
        entry_points,
        kotlin_files,
        routes,
    )
    overview_doc = build_overview_doc(
        project_root,
        structure,
        flows_exists,
        entry_points,
        modules,
        common_main_paths,
        layer_paths,
    )

    architecture_template = load_template_with_fallback(
        architecture_source,
        (
            "# Arquitectura\n\n"
            "{{modules}}\n\n"
            "{{entry_points}}\n\n"
            "{{common_main}}\n\n"
            "{{layers}}\n\n"
            "{{key_components}}\n\n"
            "{{dependencies}}\n\n"
            "{{architecture_diagram}}"
        ),
    )
    architecture_doc = fill_template(architecture_template, architecture_data)

    agents_template = load_template_with_fallback(
        agents_source,
        (
            "# Repository Guidelines\n\n"
            "## Project Structure & Module Organization\n\n"
            "{{modules}}\n\n"
            "## Build, Test, and Development Commands\n\n"
            "- `./gradlew build`\n\n"
            "## Coding Style & Naming Conventions\n\n"
            "- Kotlin style, 4-space indentation.\n\n"
            "## Testing Guidelines\n\n"
            "- Shared tests in commonTest.\n"
        ),
    )
    agents_doc = fill_template(agents_template, {"modules": architecture_data["modules"]})

    (docs_dir / "architecture.md").write_text(architecture_doc.rstrip() + "\n", encoding="utf-8")
    (docs_dir / "navigation.md").write_text(navigation_doc, encoding="utf-8")
    (docs_dir / "overview.md").write_text(overview_doc, encoding="utf-8")
    (project_root / "AGENTS.md").write_text(agents_doc.rstrip() + "\n", encoding="utf-8")

    print("Documentation generation completed successfully.")
    print(f"Project (cwd): {project_root}")
    print("Generated / overwritten:")
    print(" - AGENTS.md")
    print(" - docs/architecture.md")
    print(" - docs/navigation.md")
    print(" - docs/overview.md")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
