# Codex Skills

Este repositorio agrupa varias skills de Codex orientadas a documentar proyectos Android y Kotlin Multiplatform.

Actualmente contiene tres skills:

- `android-docs`
- `kmp-docs-generator`
- `update_project_docs` (carpeta `update-doc-skill`)

## Estructura del repositorio

```text
skills/
├── android-docs/
├── kmp-docs-generator/
└── update-doc-skill/
```

## Resumen rápido

| Skill | Tipo | Enfoque | Resultado principal |
| --- | --- | --- | --- |
| `android-docs` | Agent-driven | Repositorios Android | Genera o refresca `README.md`, `docs/architecture.md` y `docs/navigation.md` |
| `kmp-docs-generator` | Agent-driven | Proyectos Kotlin Multiplatform Compose | Genera o refresca `README.md` y `docs/overview.md`, `docs/architecture.md`, `docs/navigation.md`, `docs/flows.md` |
| `update_project_docs` | Script + preparación | Proyectos KMP/Compose | Prepara `docs/structure.json` y prompts para que Codex genere documentación después |

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

- Usa `android-docs` cuando el repositorio es Android y necesitas documentación centrada en arquitectura y navegación.
- Usa `kmp-docs-generator` cuando el proyecto es Kotlin Multiplatform Compose y quieres una documentación más completa y coherente entre varios archivos.
- Usa `update_project_docs` cuando no quieres redactar aún toda la documentación, sino preparar estructura y prompts para una generación posterior.

## Observaciones sobre el contenido del repo

- `android-docs` incluye `assets/` con plantillas y `scripts/` con un generador auxiliar.
- `kmp-docs-generator` incluye scripts de soporte como `run.py` y `extract_structure.py`, además de assets de referencia.
- `update-doc-skill` está más orientada a preparación automatizada mediante script y prompts localizados en `prompts/es` y `prompts/en`.
