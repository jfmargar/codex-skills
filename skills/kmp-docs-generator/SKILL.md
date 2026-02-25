---
name: kmp-docs-generator
description: Analyze Kotlin Multiplatform Compose repositories and generate or update README.md plus docs/overview.md, docs/architecture.md, docs/navigation.md, and docs/flows.md from real repo inspection. Use when project docs must be created if missing or fully refreshed if present.
---

# kmp-docs-generator

Agent-first skill to generate project documentation from direct repository inspection.

## Scope

This skill always targets the current working directory and manages only:

- `README.md` (project summary + documentation index)
- `docs/overview.md`
- `docs/architecture.md`
- `docs/navigation.md`
- `docs/flows.md`

It does not generate or modify `AGENTS.md`.

## Create/Update behavior

- If `README.md` or `docs/*` files do not exist, create them.
- If they already exist, update them with full-file rewrites to keep consistency.

## Required workflow (always)

1. Inspect repository structure before writing anything.
2. Detect modules from `settings.gradle(.kts)` and root folders.
3. Detect entry points (Android, iOS, `App()`).
4. Inspect navigation from real code paths, especially:
   - `AppDestination`
   - `Navigation.kt`
   - real `navigate(...)` calls and registered routes
5. Identify key composable screens and architecture layers (`domain`, `data`, `ui`, plus legacy `dabase`).
6. Cross-check consistency between `README.md` and all files in `docs/`.
7. Write/update outputs in Spanish by default.

## Output structure

- `README.md`: concise project summary and index linking to all docs files.
- `docs/overview.md`: high-level project view with valid cross-references.
- `docs/architecture.md`: modules, layers, and relevant dependencies.
- `docs/navigation.md`: destinations, transitions, and navigation notes from code.
- `docs/flows.md`: operational happy paths and Mermaid flow aligned with navigation.

## Quality rules

- Do not invent facts: if something is not confirmed in code, do not document it as implemented.
- Keep `docs/navigation.md` and `docs/flows.md` aligned (same navigation reality; same Mermaid graph when applicable).
- Prefer precision over boilerplate text.
