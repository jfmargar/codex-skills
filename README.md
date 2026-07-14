# Codex Skills

Este repositorio agrupa skills personales de Codex para documentacion, automatizacion de flujos Android/iOS y utilidades de trabajo con assets.
Además, versiona una copia del `AGENTS.md` global de Codex para mantener trazabilidad de las reglas operativas.

Actualmente contiene estas skills:

- `android-docs`
- `android-simulator-autotest`
- `app-store-screenshot-pipeline`
- `app-store-screenshots`
- `close-android-release`
- `gitflow-issue-close`
- `imagegen`
- `kmp-docs-generator`
- `prepare-android-release`
- `update_project_docs` (carpeta `update-doc-skill`)

## Estructura del repositorio

```text
skills/
├── android-docs/
├── android-simulator-autotest/
├── app-store-screenshot-pipeline/
├── app-store-screenshots/
├── close-android-release/
├── gitflow-issue-close/
├── imagegen/
├── kmp-docs-generator/
├── prepare-android-release/
└── update-doc-skill/
```

## Reglas operativas versionadas

- El archivo raíz `AGENTS.md` refleja la configuración global de Codex que se está versionando en este repositorio.
- Sirve como referencia histórica y de colaboración para mantener consistencia entre sesiones y cambios de workflow.

## Resumen rápido

| Skill | Tipo | Enfoque | Resultado principal |
| --- | --- | --- | --- |
| `android-docs` | Agent-driven | Repositorios Android | Genera o refresca `README.md`, `docs/architecture.md` y `docs/navigation.md` |
| `android-simulator-autotest` | Validacion automatizada | Apps Android/KMP | Ejecuta smoke tests, chequeos de navegacion y auditoria basica sobre simulador |
| `app-store-screenshot-pipeline` | Pipeline guiado | Apps iOS | Captura y prepara screenshots comerciales para App Store |
| `app-store-screenshots` | Captura + composicion | Apps iOS | Genera lotes de screenshots listas para App Store Connect |
| `close-android-release` | Flujo de release | Apps Android | Cierra una release Android siguiendo el checklist definido por la skill |
| `gitflow-issue-close` | Flujo Git/GitHub | Repositorios con GitFlow | Implementa y cierra issues siguiendo rama, validacion y merge |
| `imagegen` | Utilidad de assets | Generacion/edicion de imagen | Usa Image API/CLI para crear o editar imagenes desde Codex |
| `kmp-docs-generator` | Agent-driven | Proyectos Kotlin Multiplatform Compose | Genera o refresca `README.md` y `docs/overview.md`, `docs/architecture.md`, `docs/navigation.md`, `docs/flows.md` |
| `prepare-android-release` | Flujo de release | Apps Android | Prepara una release Android antes del cierre y publicacion |
| `update_project_docs` | Script + preparacion | Proyectos KMP/Compose | Prepara `docs/structure.json` y prompts para que Codex genere documentacion despues |

## Skills

### `android-docs`

Ubicación: [skills/android-docs](./skills/android-docs)

Esta skill está pensada para analizar repositorios Android y producir documentación útil basada en el código real del proyecto, no en plantillas genéricas.

Qué hace:

- Inspecciona `AndroidManifest.xml`, Gradle, catálogos de versiones y puntos de entrada.
- Revisa la navegación real de la app, tanto en XML como en Compose si existe.
- Detecta capas, dependencias, DI, repositorios, casos de uso y estructura general.
- Genera o actualiza documentación orientada a arquitectura y navegación.

Archivos que genera o actualiza:

- `README.md`
- `docs/architecture.md`
- `docs/navigation.md`

Notas importantes:

- Su modo por defecto es agent-driven: la skill obliga a que el análisis principal lo haga el agente.
- Incluye plantillas en `assets/` y un helper opcional en `scripts/generate_docs.py`, pero ambos son apoyo y no fuente de verdad.
- Es la opción adecuada cuando el objetivo principal es documentar una app Android nativa o centrada en Android.

### `android-simulator-autotest`

Ubicacion: [skills/android-simulator-autotest](./skills/android-simulator-autotest)

Skill orientada a validacion casi end-to-end sobre simulador Android para proyectos Android o Kotlin Multiplatform.

Que hace:

- combina tests conectados, unit tests y smoke de arranque cuando aplica
- revisa logs y posibles crashes
- audita navegacion y recorridos principales apoyandose en scripts auxiliares

### `app-store-screenshot-pipeline`

Ubicacion: [skills/app-store-screenshot-pipeline](./skills/app-store-screenshot-pipeline)

Skill pensada para orquestar la captura y preparacion de screenshots comerciales para App Store.

Que hace:

- ayuda a seleccionar la historia visual del producto
- reutiliza sesiones de simulador cuando conviene
- prepara inventarios y flujo de trabajo de capturas y composicion

### `app-store-screenshots`

Ubicacion: [skills/app-store-screenshots](./skills/app-store-screenshots)

Skill para generar lotes de screenshots listas para App Store Connect a partir de pantallas reales de la app.

Que hace:

- selecciona pantallas clave
- genera composiciones promocionales
- adapta las imagenes a formatos y dimensiones de App Store

### `close-android-release`

Ubicacion: [skills/close-android-release](./skills/close-android-release)

Skill de workflow para cerrar una release Android siguiendo un proceso guiado.

### `gitflow-issue-close`

Ubicacion: [skills/gitflow-issue-close](./skills/gitflow-issue-close)

Skill para resolver y cerrar issues respetando una secuencia GitFlow completa: rama dedicada, validacion, commit, push y merge antes del cierre.

### `imagegen`

Ubicacion: [skills/imagegen](./skills/imagegen)

Skill de apoyo para generar o editar imagenes desde Codex usando la Image API mediante CLI.

Que hace:

- genera imagenes nuevas desde prompts
- edita assets existentes
- incluye referencias y ejemplos para prompting y uso de red/API

### `kmp-docs-generator`

Ubicación: [skills/kmp-docs-generator](./skills/kmp-docs-generator)

Esta skill está enfocada en proyectos Kotlin Multiplatform con Compose. Su alcance es más amplio que `android-docs`, porque no se limita a arquitectura y navegación: también cubre overview y flujos funcionales.

Qué hace:

- Analiza la configuración raíz del proyecto y la estructura de módulos KMP.
- Identifica entry points de Android, iOS y la parte compartida cuando existen.
- Inspecciona navegación, destinos, transiciones y reglas de back stack.
- Documenta arquitectura, módulos, dependencias y flujos principales.
- Reescribe la documentación completa para mantener consistencia entre archivos.

Archivos que genera o actualiza:

- `README.md`
- `docs/overview.md`
- `docs/architecture.md`
- `docs/navigation.md`
- `docs/flows.md`

Notas importantes:

- También es agent-driven por defecto.
- Está pensada para reconstruir la documentación completa de un proyecto KMP Compose a partir de la implementación real.
- No modifica `AGENTS.md`.

### `prepare-android-release`

Ubicacion: [skills/prepare-android-release](./skills/prepare-android-release)

Skill de workflow para preparar una release Android antes del cierre, centrada en pasos previos de versionado, checklist y coordinacion.

### `update_project_docs`

Ubicación: [skills/update-doc-skill](./skills/update-doc-skill)

Esta skill no genera directamente la documentación narrativa final. Su función es preparar el proyecto para que Codex pueda generar después documentación de flujos y estructura con mejor contexto.

Qué hace:

- Extrae la estructura del proyecto a `docs/structure.json`.
- Instala prompts auxiliares en `prompts/`.
- Deja preparado el contexto para una siguiente instrucción de generación documental.

Archivos o salidas esperadas:

- `docs/structure.json`
- `prompts/flow_prompt.md`
- `prompts/generate_flows.md`

Notas importantes:

- Su nombre interno es `update_project_docs`, aunque la carpeta del repo se llama `update-doc-skill`.
- Se ejecuta mediante `python3 run.py`.
- Acepta el parámetro opcional `lang` con valores como `en` o `es`.
- Es útil como paso previo cuando quieres preparar inputs estructurados antes de pedir a Codex que redacte `docs/flows.md`.

## Diferencias clave

- Usa `android-docs` cuando el repositorio es Android y necesitas documentacion centrada en arquitectura y navegacion.
- Usa `kmp-docs-generator` cuando el proyecto es Kotlin Multiplatform Compose y quieres una documentacion mas completa y coherente entre varios archivos.
- Usa `update_project_docs` cuando no quieres redactar aun toda la documentacion, sino preparar estructura y prompts para una generacion posterior.
- Usa `android-simulator-autotest` cuando el objetivo principal sea validar la app en simulador.
- Usa `app-store-screenshot-pipeline` o `app-store-screenshots` cuando necesites assets comerciales para App Store.
- Usa `prepare-android-release` y `close-android-release` para pasos guiados del ciclo de release Android.
- Usa `imagegen` para generacion o edicion de imagenes dentro de Codex.
- Usa `gitflow-issue-close` cuando debas cerrar trabajo siguiendo una rama y merge controlados.

## Observaciones sobre el contenido del repo

- `android-docs` incluye `assets/` con plantillas y `scripts/` con un generador auxiliar.
- `android-simulator-autotest`, `app-store-screenshot-pipeline`, `app-store-screenshots` e `imagegen` incluyen scripts o referencias de soporte para automatizar partes del flujo.
- `kmp-docs-generator` incluye scripts de soporte como `run.py` y `extract_structure.py`, ademas de assets de referencia.
- `update-doc-skill` esta mas orientada a preparacion automatizada mediante script y prompts localizados en `prompts/es` y `prompts/en`.
