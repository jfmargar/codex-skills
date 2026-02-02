#!/usr/bin/env python3
import json
import os
import re
import sys
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
        return {}
    tree = ET.parse(manifest_path)
    root = tree.getroot()
    package_name = root.attrib.get("package", "")
    android_ns = "{http://schemas.android.com/apk/res/android}"
    application = root.find("application")
    application_name = ""
    launcher_activity = ""
    if application is not None:
        application_name = application.attrib.get(android_ns + "name", "")
        for activity in application.findall("activity"):
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


def fill_template(template, data):
    for key, value in data.items():
        template = template.replace("{{" + key + "}}", value)
    return template


def main():
    repo_root = os.getcwd()
    skill_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

    modules = detect_modules(repo_root)
    app_module = "app" if "app" in modules else (modules[0] if modules else "app")
    dabase_module = "dabase" if "dabase" in modules else "dabase"

    app_dir = find_dir(repo_root, app_module) or os.path.join(repo_root, app_module)
    dabase_dir = find_dir(repo_root, dabase_module) or os.path.join(repo_root, dabase_module)

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

    project_summary = (
        "Proyecto Android nativo (Kotlin/Java) con modulo base compartido (" + dabase_module + "). "
        "La app configura el entorno, la navegacion y la integracion con servicios externos."
    )

    project_overview = (
        "Este repositorio contiene una app Android (Kotlin/Java) y un modulo base compartido ("
        + dabase_module
        + "). La app configura el entorno, la navegacion y la integracion con Firebase, "
        "mientras que el modulo base aporta UI, DI, almacenamiento y servicios de red comunes."
    )

    modules_list = "- `:" + app_module + "`: aplicacion Android. Define entry points, navegacion y presenters.\n"
    modules_list += "- `:" + dabase_module + "`: libreria base con UI comun, utilidades, DI y clientes Retrofit."

    external_services = "- API backend (Retrofit + RxJava).\n"
    if firebase_enabled:
        external_services += "- Firebase (Crashlytics, Analytics, FCM).\n"
    if has_pdf_assets:
        external_services += "- PDF.js embebido en assets para visor PDF."

    startup_flow = (
        "1. `App` (Application) inicializa preferencias y guarda `baseUrl` y `loginUrl`.\n"
        "2. La actividad launcher arranca el flujo de la app.\n"
        "3. El presenter de splash decide el destino inicial segun token.\n"
        "4. La app aplica logica propia para decidir la pantalla inicial."
    )

    layers = (
        "- Presentacion: Activities/Views y Presenters en `"
        + app_module
        + "`.\n"
        "- Dominio: modelos en `"
        + app_module
        + "/src/main/java`.\n"
        "- Datos: servicios API y DTOs en `"
        + app_module
        + "/src/main/java`.\n"
        "- Utilidades: helpers en el modulo base."
    )

    navigation_summary = (
        "- `Navigate` gestiona navegacion base (login, acciones genericas).\n"
        "- `Router.kt` define rutas especificas de la app."
    )

    config_points = (
        "- Base URL: definida en `App` mediante preferencias.\n"
        "- Retrofit: configurado en `ApiModule` y maneja respuestas 401.\n"
        "- Entry points: Application y actividad launcher."
    )

    dabase_overview = (
        "El modulo `:"
        + dabase_module
        + "` es una libreria base para apps Android. Provee UI base, DI, red, utilidades y escenas comunes."
    )

    dabase_structure_notes = (
        "- `data/`: servicios Retrofit y DTOs comunes.\n"
        "- `domain/`: modelos base.\n"
        "- `injection/`: componentes y modulos Dagger.\n"
        "- `ui/`: base UI y escenas comunes.\n"
        "- `utils/`: utilidades de almacenamiento, formato y validacion."
    )

    base_ui_notes = (
        "- `BasePresenter` inyecta preferencias, navegacion y contexto.\n"
        "- `BaseActivity` gestiona DataBinding/ViewBinding y ciclo de vida comun."
    )

    di_notes = (
        "- Componente base usado por los presenters.\n"
        "- `RouterModule` configura la clase de login por defecto.\n"
        "- Modulos de red gestionan autenticacion y errores 401."
    )

    network_notes = (
        "- Servicios asegurados usan token y redirigen a login en 401.\n"
        "- Servicios no asegurados operan sin autenticacion.\n"
        "- Retrofit + RxJava con configuracion comun."
    )

    resource_notes = "- Layouts y estilos base en el modulo base."

    custom_overview = (
        "La app `:"
        + app_module
        + "` utiliza `:"
        + dabase_module
        + "` como base comun y extiende su comportamiento con configuraciones y modulos propios."
    )

    custom_injection_notes = (
        "- El injector de la app combina modulos base y el `ApiModule` especifico.\n"
        "- Los presenters de la app reciben `ApiServices` por DI."
    )

    custom_api_config = (
        "- `App` guarda `baseUrl` en preferencias.\n"
        "- `ApiModule` crea Retrofit y anade headers de autenticacion.\n"
        "- En `401`, se redirige al login con `Navigate`."
    )

    custom_navigation_notes = (
        "- `Router.kt` define rutas para noticias, documentos, filtros y pantallas auxiliares.\n"
        "- El splash puede redefinir el flujo inicial segun estado local."
    )

    custom_ui_notes = (
        "- Recursos propios en `app/src/main/res`.\n"
        + ("- PDF.js en `app/src/main/assets/pdfjs`." if has_pdf_assets else "")
    ).strip()

    custom_firebase_notes = (
        "- Crashlytics y FCM habilitados en Gradle." if firebase_enabled else "- Firebase no detectado en Gradle."
    )

    flows_overview = "Este documento resume los flujos clave entre la app y el modulo base."

    flow_startup_notes = (
        "- La actividad splash aplica la logica de entrada.\n"
        "- El presenter de splash controla el arranque y el login."
    )

    flow_di_notes = "- La app crea un injector especifico y registra sus modulos."

    flow_navigation_notes = "- Rutas definidas en `Router.kt` y gestionadas por `Navigate`."

    flow_data_notes = (
        "- Los presenters consumen `ApiServices` inyectado.\n"
        "- `PreferenceStorage` guarda token, baseUrl y estado local."
    )

    data = {
        "project_summary": project_summary,
        "project_overview": project_overview,
        "modules_list": modules_list,
        "external_services": external_services.strip(),
        "node_entry": sanitize_label("Android entry"),
        "node_app": sanitize_label("App module"),
        "node_app_init": sanitize_label("App init preferencias"),
        "node_presenters": sanitize_label("Presenters and Activities"),
        "node_api_module": sanitize_label("ApiModule Retrofit"),
        "node_router": sanitize_label("Router Navigate"),
        "node_base_ui": sanitize_label("Base UI presenters"),
        "node_api": sanitize_label("Backend API"),
        "node_firebase": sanitize_label("Firebase Crashlytics FCM" if firebase_enabled else "Firebase"),
        "node_assets": sanitize_label("PDF assets" if has_pdf_assets else "Assets"),
        "startup_flow": startup_flow,
        "layers": layers,
        "navigation_summary": navigation_summary,
        "config_points": config_points,
        "dabase_overview": dabase_overview,
        "dabase_node": sanitize_label(dabase_module),
        "dabase_root": sanitize_label("src main java"),
        "dabase_data": sanitize_label("data"),
        "dabase_domain": sanitize_label("domain"),
        "dabase_injection": sanitize_label("injection"),
        "dabase_ui": sanitize_label("ui"),
        "dabase_utils": sanitize_label("utils"),
        "dabase_structure_notes": dabase_structure_notes,
        "base_view": sanitize_label("BaseView"),
        "base_presenter": sanitize_label("BasePresenter"),
        "base_activity": sanitize_label("BaseActivity"),
        "base_scenes": sanitize_label("Scenes Login Splash"),
        "base_ui_notes": base_ui_notes,
        "di_component": sanitize_label("PresentInjector"),
        "di_context": sanitize_label("ContextModule"),
        "di_router": sanitize_label("RouterModule"),
        "di_secured": sanitize_label("SecuredApiModule"),
        "di_unsecured": sanitize_label("UnsecuredApiModule"),
        "di_notes": di_notes,
        "network_notes": network_notes,
        "resource_notes": resource_notes,
        "custom_overview": custom_overview,
        "custom_app_presenters": sanitize_label("App presenters"),
        "custom_injector": sanitize_label("DaggerAppPresentInjector"),
        "custom_context": sanitize_label("ContextModule"),
        "custom_api_module": sanitize_label("ApiModule app"),
        "custom_router": sanitize_label("RouterModule"),
        "custom_injection_notes": custom_injection_notes,
        "custom_api_config": custom_api_config,
        "custom_navigate": sanitize_label("Navigate"),
        "custom_router_node": sanitize_label("Router kt app"),
        "custom_corporates": sanitize_label("Corporates"),
        "custom_news": sanitize_label("News"),
        "custom_filter": sanitize_label("Filter"),
        "custom_documents": sanitize_label("Documents"),
        "custom_send": sanitize_label("SendNewsletter"),
        "custom_navigation_notes": custom_navigation_notes,
        "custom_ui_notes": custom_ui_notes,
        "custom_firebase_notes": custom_firebase_notes,
        "flows_overview": flows_overview,
        "flow_app": sanitize_label("App Application"),
        "flow_splash": sanitize_label("SplashExtension"),
        "flow_presenter": sanitize_label("SplashPresenter"),
        "flow_nav": sanitize_label("Navigate"),
        "flow_login": sanitize_label("LoginActivity"),
        "flow_news": sanitize_label("NewsActivity"),
        "flow_corp": sanitize_label("CorporatesActivity"),
        "flow_startup_notes": flow_startup_notes,
        "flow_injector_root": sanitize_label("AppModulePresenter"),
        "flow_injector": sanitize_label("DaggerAppPresentInjector"),
        "flow_context": sanitize_label("ContextModule"),
        "flow_api_module": sanitize_label("ApiModule app"),
        "flow_router": sanitize_label("RouterModule"),
        "flow_api_services": sanitize_label("Retrofit and ApiServices"),
        "flow_di_notes": flow_di_notes,
        "flow_corporates": sanitize_label("Corporates"),
        "flow_news_detail": sanitize_label("NewsDetail"),
        "flow_filter": sanitize_label("Filter"),
        "flow_documents": sanitize_label("Documents"),
        "flow_edit": sanitize_label("EditDocument"),
        "flow_send": sanitize_label("SendNewsletter"),
        "flow_generate": sanitize_label("GenerateDocument"),
        "flow_fullscreen": sanitize_label("FullScreen"),
        "flow_navigation_notes": flow_navigation_notes,
        "flow_ui": sanitize_label("Activity and Presenter"),
        "flow_api": sanitize_label("ApiServices"),
        "flow_net": sanitize_label("Retrofit OkHttp"),
        "flow_backend": sanitize_label("Backend API"),
        "flow_prefs": sanitize_label("PreferenceStorage"),
        "flow_data_notes": flow_data_notes,
    }

    readme_tpl = load_template(skill_root, "README.md.tpl")
    arquitectura_tpl = load_template(skill_root, "arquitectura.md.tpl")
    dabase_tpl = load_template(skill_root, "dabase-arquitectura.md.tpl")
    custom_tpl = load_template(skill_root, "customizacion-dabase.md.tpl")
    flows_tpl = load_template(skill_root, "flows.md.tpl")
    structure_tpl = load_template(skill_root, "structure.json.tpl")

    readme = fill_template(readme_tpl, data)
    arquitectura = fill_template(arquitectura_tpl, data)
    dabase_doc = fill_template(dabase_tpl, data)
    custom_doc = fill_template(custom_tpl, data)
    flows_doc = fill_template(flows_tpl, data)

    modules_json = json.dumps(modules or [app_module, dabase_module])
    structure_data = {
        "project_name": project_name,
        "modules_json": modules_json,
        "entry_application": app_path,
        "entry_launcher": launcher_path,
        "entry_login": dabase_login_activity,
        "app_description": "Aplicacion Android: navegacion, presenters y configuracion de API/Firebase.",
        "app_router": router_path,
        "app_api_module": api_module_path,
        "app_api_services": api_services_path,
        "app_domain": os.path.join(app_dir, "src/main/java"),
        "app_ui": os.path.join(app_dir, "src/main/java"),
        "app_assets": pdf_assets if has_pdf_assets else "",
        "dabase_description": "Libreria base: UI comun, DI, red y utilidades.",
        "dabase_present_injector": dabase_present_injector,
        "dabase_context_module": dabase_context_module,
        "dabase_router_module": dabase_router_module,
        "dabase_secured_module": dabase_secured_module,
        "dabase_unsecured_module": dabase_unsecured_module,
        "dabase_base_presenter": dabase_base_presenter,
        "dabase_navigate": dabase_navigate,
    }

    structure = fill_template(structure_tpl, structure_data)

    write_text(os.path.join(repo_root, "README.md"), readme)
    write_text(os.path.join(repo_root, "docs", "arquitectura.md"), arquitectura)
    write_text(os.path.join(repo_root, "docs", "dabase-arquitectura.md"), dabase_doc)
    write_text(os.path.join(repo_root, "docs", "customizacion-dabase.md"), custom_doc)
    write_text(os.path.join(repo_root, "docs", "flows.md"), flows_doc)
    write_text(os.path.join(repo_root, "docs", "structure.json"), structure)

    print("Docs generated.")


if __name__ == "__main__":
    main()
