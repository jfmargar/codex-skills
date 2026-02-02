#!/usr/bin/env python3
import os
import re
import xml.etree.ElementTree as ET
from pathlib import Path


def read_text(path):
    try:
        return Path(path).read_text(encoding="utf-8")
    except Exception:
        return ""


def write_text(path, content):
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    Path(path).write_text(content, encoding="utf-8")


def find_file(root, filename):
    for dirpath, _, filenames in os.walk(root):
        if filename in filenames:
            return os.path.join(dirpath, filename)
    return None


def find_dir(root, dirname):
    candidate = os.path.join(root, dirname)
    return candidate if os.path.isdir(candidate) else None


def sanitize_label(value):
    if not value:
        return "Unknown"
    value = re.sub(r"[^A-Za-z0-9 ]+", " ", value)
    value = re.sub(r"\s+", " ", value).strip()
    return value or "Unknown"


def resolve_class_to_path(class_name, package_name, module_dir):
    if not class_name:
        return ""
    if class_name.startswith("."):
        full = package_name + class_name
    elif "." in class_name:
        full = class_name
    else:
        full = package_name + "." + class_name
    rel = full.replace(".", "/")
    kotlin_path = os.path.join(module_dir, "src/main/java", rel + ".kt")
    java_path = os.path.join(module_dir, "src/main/java", rel + ".java")
    if os.path.exists(kotlin_path):
        return kotlin_path
    if os.path.exists(java_path):
        return java_path
    return ""


def parse_manifest(manifest_path):
    if not manifest_path or not os.path.exists(manifest_path):
        return {"package": "", "application": "", "launcher": "", "activities": []}
    tree = ET.parse(manifest_path)
    root = tree.getroot()
    package_name = root.attrib.get("package", "")
    android_ns = "{http://schemas.android.com/apk/res/android}"
    application = root.find("application")
    application_name = ""
    launcher_activity = ""
    activities = []
    if application is not None:
        application_name = application.attrib.get(android_ns + "name", "")
        for activity in application.findall("activity"):
            name = activity.attrib.get(android_ns + "name", "")
            if name:
                activities.append(name)
            intent_filters = activity.findall("intent-filter")
            for intent in intent_filters:
                has_main = any(
                    act.attrib.get(android_ns + "name") == "android.intent.action.MAIN"
                    for act in intent.findall("action")
                )
                has_launcher = any(
                    cat.attrib.get(android_ns + "name") == "android.intent.category.LAUNCHER"
                    for cat in intent.findall("category")
                )
                if has_main and has_launcher:
                    launcher_activity = activity.attrib.get(android_ns + "name", "")
                    break
            if launcher_activity:
                break
    return {
        "package": package_name,
        "application": application_name,
        "launcher": launcher_activity,
        "activities": activities,
    }


def detect_modules(root):
    modules = []
    for name in ["app", "dabase"]:
        if os.path.isdir(os.path.join(root, name)):
            modules.append(name)
    if not modules:
        for entry in os.listdir(root):
            path = os.path.join(root, entry)
            if os.path.isdir(path) and (
                os.path.exists(os.path.join(path, "build.gradle"))
                or os.path.exists(os.path.join(path, "build.gradle.kts"))
            ):
                modules.append(entry)
    return modules


def has_firebase(build_gradle_path):
    text = read_text(build_gradle_path)
    return "firebase" in text.lower()


def load_template(skill_root, name):
    path = os.path.join(skill_root, "assets", name)
    return read_text(path)


def load_template_with_fallback(skill_root, name, fallback):
    template = load_template(skill_root, name)
    return template if template.strip() else fallback


def fill_template(template, data):
    for key, value in data.items():
        template = template.replace("{{" + key + "}}", value)
    return template


def relative_path(path, root):
    if not path:
        return ""
    try:
        return os.path.relpath(path, root)
    except Exception:
        return path


def collect_source_files(module_dir):
    src_root = os.path.join(module_dir, "src", "main", "java")
    if not os.path.isdir(src_root):
        return []
    matches = []
    for dirpath, _, filenames in os.walk(src_root):
        for filename in filenames:
            if filename.endswith(".kt") or filename.endswith(".java"):
                matches.append(os.path.join(dirpath, filename))
    return matches


def extract_class_names(paths, suffixes):
    found = set()
    pattern = re.compile(r"\bclass\s+([A-Za-z0-9_]+)")
    for path in paths:
        text = read_text(path)
        for match in pattern.findall(text):
            if any(match.endswith(suffix) for suffix in suffixes):
                found.add(match)
    return sorted(found)


def extract_route_functions(paths):
    found = set()
    pattern = re.compile(r"\bfun\s+([A-Za-z0-9_]+)\s*\(")
    for path in paths:
        text = read_text(path)
        for match in pattern.findall(text):
            if match.startswith(("goTo", "open", "navigate", "show")):
                found.add(match)
    return sorted(found)


def extract_gradle_dependencies(text):
    deps = []
    pattern = re.compile(r"^\s*(implementation|api|kapt|ksp)\s+([\"'])(.+?)\2", re.MULTILINE)
    for match in pattern.findall(text):
        deps.append(match[2])
    return deps


def classify_dependencies(deps):
    buckets = {
        "di": [],
        "network": [],
        "db": [],
        "async": [],
        "firebase": [],
        "testing": [],
        "other": [],
    }
    for dep in deps:
        lowered = dep.lower()
        if "hilt" in lowered or "dagger" in lowered or "koin" in lowered:
            buckets["di"].append(dep)
        elif "retrofit" in lowered or "okhttp" in lowered or "moshi" in lowered:
            buckets["network"].append(dep)
        elif "room" in lowered or "sqlite" in lowered or "datastore" in lowered:
            buckets["db"].append(dep)
        elif "coroutines" in lowered or "rxjava" in lowered:
            buckets["async"].append(dep)
        elif "firebase" in lowered:
            buckets["firebase"].append(dep)
        elif "junit" in lowered or "espresso" in lowered or "mockito" in lowered:
            buckets["testing"].append(dep)
        else:
            buckets["other"].append(dep)
    return buckets


def parse_nav_graphs(nav_dir):
    graphs = []
    if not os.path.isdir(nav_dir):
        return graphs
    for filename in sorted(os.listdir(nav_dir)):
        if not filename.endswith(".xml"):
            continue
        path = os.path.join(nav_dir, filename)
        try:
            tree = ET.parse(path)
            root = tree.getroot()
        except Exception:
            graphs.append({"file": path, "destinations": [], "actions": []})
            continue
        destinations = []
        actions = []
        for node in root.iter():
            tag = node.tag.split("}")[-1]
            if tag in ["fragment", "activity", "dialog", "navigation"]:
                dest_id = node.attrib.get("{http://schemas.android.com/apk/res/android}id", "")
                dest_name = node.attrib.get("{http://schemas.android.com/apk/res/android}name", "")
                if dest_id or dest_name:
                    destinations.append("{} {}".format(dest_id, dest_name).strip())
            if tag == "action":
                action_id = node.attrib.get("{http://schemas.android.com/apk/res/android}id", "")
                to_dest = node.attrib.get("{http://schemas.android.com/apk/res/android}destination", "")
                if action_id or to_dest:
                    actions.append("{} {}".format(action_id, to_dest).strip())
        graphs.append({"file": path, "destinations": destinations, "actions": actions})
    return graphs


def find_package_layers(src_root):
    layers = {}
    for layer in ["ui", "domain", "data", "injection", "di"]:
        layer_path = os.path.join(src_root, layer)
        if os.path.isdir(layer_path):
            layers[layer] = layer_path
    return layers


def extract_feature_components(paths):
    features = {}
    pattern = re.compile(r"\bclass\s+([A-Za-z0-9_]+)")
    for path in paths:
        normalized = path.replace("\\", "/")
        marker = "/ui/scenes/"
        if marker not in normalized:
            continue
        feature = normalized.split(marker, 1)[1].split("/", 1)[0]
        if not feature:
            continue
        text = read_text(path)
        for match in pattern.findall(text):
            if match.endswith("Activity"):
                features.setdefault(feature, {"activities": set(), "fragments": set()})["activities"].add(match)
            elif match.endswith("Fragment"):
                features.setdefault(feature, {"activities": set(), "fragments": set()})["fragments"].add(match)
    return features


def main():
    repo_root = os.getcwd()
    skill_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    docs_root = os.path.join(repo_root, "docs")
    Path(docs_root).mkdir(parents=True, exist_ok=True)

    modules = detect_modules(repo_root)
    if not modules and (
        os.path.exists(os.path.join(repo_root, "build.gradle"))
        or os.path.exists(os.path.join(repo_root, "build.gradle.kts"))
    ):
        modules = ["app"]
    app_module = "app" if "app" in modules else (modules[0] if modules else "app")
    dabase_module = "dabase" if "dabase" in modules else "dabase"

    app_dir = find_dir(repo_root, app_module) or os.path.join(repo_root, app_module)
    dabase_dir = find_dir(repo_root, dabase_module) or os.path.join(repo_root, dabase_module)

    if not os.path.isdir(app_dir) and os.path.exists(os.path.join(repo_root, "src", "main", "AndroidManifest.xml")):
        app_dir = repo_root

    manifest_path = os.path.join(app_dir, "src/main/AndroidManifest.xml")
    manifest = parse_manifest(manifest_path)

    app_path = resolve_class_to_path(manifest.get("application", ""), manifest.get("package", ""), app_dir)
    launcher_path = resolve_class_to_path(manifest.get("launcher", ""), manifest.get("package", ""), app_dir)

    router_path = find_file(app_dir, "Router.kt") or ""
    api_module_path = find_file(app_dir, "ApiModule.kt") or ""
    api_services_path = find_file(app_dir, "ApiServices.kt") or ""

    dabase_present_injector = find_file(dabase_dir, "PresentInjector.kt") or ""
    dabase_context_module = find_file(dabase_dir, "ContextModule.kt") or ""
    dabase_router_module = find_file(dabase_dir, "RouterModule.kt") or ""
    dabase_secured_module = find_file(dabase_dir, "SecuredApiModule.kt") or ""
    dabase_unsecured_module = find_file(dabase_dir, "UnsecuredApiModule.kt") or ""
    dabase_base_presenter = find_file(dabase_dir, "BasePresenter.kt") or ""
    dabase_navigate = find_file(dabase_dir, "Navigate.kt") or ""
    dabase_login_activity = find_file(dabase_dir, "LoginActivity.kt") or ""

    pdf_assets = os.path.join(app_dir, "src/main/assets/pdfjs")
    has_pdf_assets = os.path.isdir(pdf_assets)

    firebase_enabled = has_firebase(os.path.join(app_dir, "build.gradle")) or has_firebase(
        os.path.join(app_dir, "build.gradle.kts")
    )

    project_name = os.path.basename(repo_root)

    source_files = collect_source_files(app_dir)
    activity_classes = extract_class_names(source_files, ["Activity"])
    fragment_classes = extract_class_names(source_files, ["Fragment"])
    feature_components = extract_feature_components(source_files)

    manifest_activities = [
        act.lstrip(".") if act.startswith(".") else act for act in manifest.get("activities", [])
    ]
    if manifest.get("package"):
        manifest_activities = [
            (manifest.get("package") + act if act and not "." in act else act) for act in manifest_activities
        ]

    router_files = [p for p in [router_path, dabase_navigate] if p]
    route_functions = extract_route_functions(router_files)

    nav_res_dir = os.path.join(app_dir, "src", "main", "res", "navigation")
    has_nav_graph = os.path.isdir(nav_res_dir) and any(
        name.endswith(".xml") for name in os.listdir(nav_res_dir)
    )
    nav_graphs = parse_nav_graphs(nav_res_dir)

    gradle_files = []
    for name in ["build.gradle", "build.gradle.kts"]:
        path = os.path.join(repo_root, name)
        if os.path.exists(path):
            gradle_files.append(path)
    for name in ["build.gradle", "build.gradle.kts"]:
        path = os.path.join(app_dir, name)
        if os.path.exists(path):
            gradle_files.append(path)

    deps = []
    for path in gradle_files:
        deps.extend(extract_gradle_dependencies(read_text(path)))
    deps = sorted(set(deps))
    deps_buckets = classify_dependencies(deps)

    src_root = os.path.join(app_dir, "src", "main", "java")
    package_layers = find_package_layers(src_root)

    modules_list = []
    for module in modules or [app_module]:
        if module == dabase_module:
            modules_list.append("- `:{}` (base compartida)".format(module))
        else:
            modules_list.append("- `:{}`".format(module))
    modules_block = "\n".join(modules_list) if modules_list else "- No se detectaron modulos."

    entry_points = []
    if manifest.get("application"):
        entry_points.append("- Application: `{}`".format(manifest.get("application")))
    if manifest.get("launcher"):
        entry_points.append("- Launcher: `{}`".format(manifest.get("launcher")))
    if dabase_login_activity:
        entry_points.append("- Login base: `{}`".format(relative_path(dabase_login_activity, repo_root)))
    entry_points_block = "\n".join(entry_points) if entry_points else "- No se detectaron entry points."

    key_components = []
    if app_path:
        key_components.append("- Application class: `{}`".format(relative_path(app_path, repo_root)))
    if router_path:
        key_components.append("- Router: `{}`".format(relative_path(router_path, repo_root)))
    if api_module_path:
        key_components.append("- API module: `{}`".format(relative_path(api_module_path, repo_root)))
    if api_services_path:
        key_components.append("- API services: `{}`".format(relative_path(api_services_path, repo_root)))
    if dabase_present_injector:
        key_components.append("- Base injector: `{}`".format(relative_path(dabase_present_injector, repo_root)))
    if dabase_base_presenter:
        key_components.append("- Base presenter: `{}`".format(relative_path(dabase_base_presenter, repo_root)))
    if has_pdf_assets:
        key_components.append("- PDF assets: `{}`".format(relative_path(pdf_assets, repo_root)))
    if firebase_enabled:
        key_components.append("- Firebase: detectado en Gradle")
    key_components_block = "\n".join(key_components) if key_components else "- No se detectaron componentes clave."

    architecture_diagram = ""
    if modules_list:
        nodes = []
        links = []
        for index, module in enumerate(modules_list):
            node_id = chr(ord("B") + index)
            label = module.replace("- `:", "").replace("`", "").strip()
            nodes.append("{}[{}]".format(node_id, sanitize_label(label)))
            links.append("A --> {}".format(node_id))
        architecture_diagram = "## Diagrama de alto nivel\n\n```mermaid\ngraph TD;\n"
        for node in nodes:
            architecture_diagram += node + ";\n"
        for link in links:
            architecture_diagram += link + ";\n"
        architecture_diagram += "```\n"

    navigation_summary = []
    if router_path:
        navigation_summary.append("- Router detectado: `{}`".format(relative_path(router_path, repo_root)))
    if dabase_navigate:
        navigation_summary.append("- Navigate base: `{}`".format(relative_path(dabase_navigate, repo_root)))
    if has_nav_graph:
        navigation_summary.append("- Navigation graphs en `app/src/main/res/navigation`.")
    navigation_summary_block = "\n".join(navigation_summary) if navigation_summary else "- No se detecto router/navigate."

    navigation_entry = []
    if manifest.get("launcher"):
        navigation_entry.append("- Launcher: `{}`".format(manifest.get("launcher")))
    if manifest.get("application"):
        navigation_entry.append("- Application: `{}`".format(manifest.get("application")))
    navigation_entry_block = "\n".join(navigation_entry) if navigation_entry else "- No se detectaron puntos de inicio."

    routes_block = []
    if route_functions:
        routes_block.append("Funciones de navegacion:")
        routes_block.extend(["- `{}`".format(fn) for fn in route_functions[:20]])
        if len(route_functions) > 20:
            routes_block.append("- (mas funciones omitidas)")
    if manifest_activities:
        routes_block.append("Activities en manifest:")
        routes_block.extend(["- `{}`".format(act) for act in manifest_activities[:20]])
        if len(manifest_activities) > 20:
            routes_block.append("- (mas activities omitidas)")
    if activity_classes:
        routes_block.append("Activities en codigo:")
        routes_block.extend(["- `{}`".format(act) for act in activity_classes[:20]])
        if len(activity_classes) > 20:
            routes_block.append("- (mas activities omitidas)")
    if fragment_classes:
        routes_block.append("Fragments en codigo:")
        routes_block.extend(["- `{}`".format(fr) for fr in fragment_classes[:20]])
        if len(fragment_classes) > 20:
            routes_block.append("- (mas fragments omitidos)")
    navigation_routes_block = "\n".join(routes_block) if routes_block else "- No se detectaron rutas."

    nav_graph_block = []
    if nav_graphs:
        for graph in nav_graphs:
            nav_graph_block.append("- `{}`".format(relative_path(graph["file"], repo_root)))
            for dest in graph["destinations"][:8]:
                nav_graph_block.append("  - Destino: `{}`".format(dest))
            if len(graph["destinations"]) > 8:
                nav_graph_block.append("  - (mas destinos omitidos)")
            for action in graph["actions"][:6]:
                nav_graph_block.append("  - Accion: `{}`".format(action))
            if len(graph["actions"]) > 6:
                nav_graph_block.append("  - (mas acciones omitidas)")
    nav_graphs_block = "\n".join(nav_graph_block) if nav_graph_block else "- No se detectaron NavGraphs."

    layers_block = []
    if package_layers:
        for layer, path in package_layers.items():
            layers_block.append("- `{}`: `{}`".format(layer, relative_path(path, repo_root)))
    layers_block = "\n".join(layers_block) if layers_block else "- No se detectaron capas por paquete."

    deps_block = []
    for key, label in [
        ("di", "DI"),
        ("network", "Networking"),
        ("db", "Persistencia"),
        ("async", "Async"),
        ("firebase", "Firebase"),
        ("testing", "Testing"),
        ("other", "Otros"),
    ]:
        if deps_buckets[key]:
            deps_block.append("- {}:".format(label))
            deps_block.extend(["  - `{}`".format(dep) for dep in deps_buckets[key][:8]])
            if len(deps_buckets[key]) > 8:
                deps_block.append("  - (mas dependencias omitidas)")
    deps_block = "\n".join(deps_block) if deps_block else "- No se detectaron dependencias declaradas."

    navigation_diagram = ""
    if manifest.get("launcher") and feature_components:
        launcher_label = sanitize_label(manifest.get("launcher"))
        navigation_diagram = "## Diagrama de navegacion\n\n```mermaid\ngraph LR;\n"
        navigation_diagram += "A[{}];\n".format(launcher_label)
        node_counter = 1
        for feature in sorted(feature_components.keys()):
            feature_node = "F{}".format(node_counter)
            node_counter += 1
            navigation_diagram += "{}[{}];\n".format(feature_node, sanitize_label(feature))
            navigation_diagram += "A --> {};\n".format(feature_node)

            classes = sorted(
                feature_components[feature]["activities"] | feature_components[feature]["fragments"]
            )
            for class_name in classes[:4]:
                class_node = "C{}".format(node_counter)
                node_counter += 1
                navigation_diagram += "{}[{}];\n".format(class_node, sanitize_label(class_name))
                navigation_diagram += "{} --> {};\n".format(feature_node, class_node)
        navigation_diagram += "```\n"

    project_summary = (
        "Proyecto Android (Kotlin/Java) con modulos detectados: "
        + (", ".join(modules) if modules else app_module)
        + "."
    )

    docs_index = "- [docs/arquitectura.md](docs/arquitectura.md): arquitectura y componentes clave.\n"
    docs_index += "- [docs/navegacion.md](docs/navegacion.md): mapa de navegacion y rutas detectadas."

    commands = "- `./gradlew clean`\n- `./gradlew assembleDebug`\n- `./gradlew assembleRelease`\n- `./gradlew lint`"

    notes = []
    if firebase_enabled:
        notes.append("- Firebase detectado en Gradle.")
    if has_pdf_assets:
        notes.append("- PDF.js embebido en `app/src/main/assets/pdfjs`.")
    notes_block = "\n".join(notes) if notes else "- Sin notas adicionales."

    data = {
        "project_name": project_name,
        "project_summary": project_summary,
        "docs_index": docs_index,
        "commands": commands,
        "notes": notes_block,
        "architecture_summary": "Resumen de la estructura y responsabilidades principales del proyecto.",
        "modules_list": modules_block,
        "entry_points": entry_points_block,
        "key_components": key_components_block,
        "architecture_diagram": architecture_diagram,
        "layers": layers_block,
        "dependencies": deps_block,
        "navigation_summary": navigation_summary_block,
        "navigation_entry": navigation_entry_block,
        "navigation_routes": navigation_routes_block,
        "navigation_graphs": nav_graphs_block,
        "navigation_diagram": navigation_diagram,
    }

    default_readme_tpl = (
        "# {{project_name}}\n\n"
        "{{project_summary}}\n\n"
        "## Indice\n\n"
        "{{docs_index}}\n\n"
        "## Comandos\n\n"
        "{{commands}}\n\n"
        "## Notas\n\n"
        "{{notes}}\n"
    )
    default_arquitectura_tpl = (
        "# Arquitectura del proyecto\n\n"
        "[Volver al README](../README.md)\n\n"
        "{{architecture_summary}}\n\n"
        "## Modulos\n\n"
        "{{modules_list}}\n\n"
        "## Puntos de entrada\n\n"
        "{{entry_points}}\n\n"
        "## Componentes clave\n\n"
        "{{key_components}}\n\n"
        "## Capas y paquetes\n\n"
        "{{layers}}\n\n"
        "## Dependencias relevantes\n\n"
        "{{dependencies}}\n\n"
        "{{architecture_diagram}}"
    )
    default_navegacion_tpl = (
        "# Navegacion\n\n"
        "[Volver al README](../README.md)\n\n"
        "{{navigation_summary}}\n\n"
        "## Puntos de inicio\n\n"
        "{{navigation_entry}}\n\n"
        "## NavGraphs\n\n"
        "{{navigation_graphs}}\n\n"
        "## Rutas y pantallas\n\n"
        "{{navigation_routes}}\n\n"
        "{{navigation_diagram}}"
    )

    readme_tpl = load_template_with_fallback(skill_root, "README.md.tpl", default_readme_tpl)
    arquitectura_tpl = load_template_with_fallback(
        skill_root, "arquitectura.md.tpl", default_arquitectura_tpl
    )
    navegacion_tpl = load_template_with_fallback(
        skill_root, "navegacion.md.tpl", default_navegacion_tpl
    )

    readme = fill_template(readme_tpl, data)
    arquitectura = fill_template(arquitectura_tpl, data)
    navegacion = fill_template(navegacion_tpl, data)

    write_text(os.path.join(repo_root, "README.md"), readme)
    write_text(os.path.join(docs_root, "arquitectura.md"), arquitectura)
    write_text(os.path.join(docs_root, "navegacion.md"), navegacion)

    print("Docs generated.")


if __name__ == "__main__":
    main()
