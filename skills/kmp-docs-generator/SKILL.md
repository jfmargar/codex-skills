---
name: kmp-docs-generator
description: Analyze Kotlin Multiplatform Compose repositories and generate or update README.md plus docs/overview.md, docs/architecture.md, docs/navigation.md, and docs/flows.md from real repo inspection. Use when project docs must be created if missing or fully refreshed if present.
---

# kmp-docs-generator

Use this skill to generate or refresh documentation for Kotlin Multiplatform Compose repositories.
The agent must analyze the repo directly and produce docs from verified findings.

## Default mode (required)

This skill is **agent-driven by default**.

- The agent must inspect code and configuration directly.
- The agent must prioritize repository evidence over assumptions.
- Documentation must reflect the current implementation, not ideal/target architecture.

## Scope

This skill always targets the current working directory and manages only:

- `README.md` (project summary + docs index)
- `docs/overview.md`
- `docs/architecture.md`
- `docs/navigation.md`
- `docs/flows.md`

It does not generate or modify `AGENTS.md`.

## Create/Update behavior

- If outputs do not exist, create them.
- If outputs exist, rewrite fully to maintain consistency between files.

## Required repository analysis

Read and extract facts from:
- Root config: `settings.gradle(.kts)`, `build.gradle(.kts)`, `gradle/libs.versions.toml`
- KMP module setup (`android`, `ios`, `wasm/js`, shared/common modules when present)
- Entry points (Android `Application`/`Activity`, iOS app entry, shared `App()` composable)
- Navigation implementation:
  - destination models (`AppDestination`, `Screen`, sealed routes, etc.)
  - route registration (`NavHost`, `navigation`, `composable`)
  - transition calls (`navigate(...)`, pop/back-stack rules)
- Project structure and layers (`ui`, `domain`, `data`, plus legacy/shared variants)
- DI and service wiring (Koin/Hilt/manual DI)

## Execution workflow (agent)

1. Inspect repository structure and module graph.
2. Identify platform entry points and shared app entry.
3. Inspect navigation code and route definitions.
4. Map screens/features to flows and transitions.
5. Inspect architecture and dependencies per layer.
6. Write/update `README.md` + all files under `docs/`.
7. Validate consistency with quality gate before finishing.

## Output expectations

- `README.md`: concise summary and links to `docs/*`.
- `docs/overview.md`: functional overview and module responsibilities.
- `docs/architecture.md`: layers, DI, data flow, relevant dependencies.
- `docs/navigation.md`: route inventory, transitions, back-stack/pop rules.
- `docs/flows.md`: main operational flows aligned with navigation.

Write in Spanish by default unless user asks otherwise.

## Diagrams

Use Mermaid compatible with GitLab:
- `graph TD/LR`
- `sequenceDiagram`

Keep labels simple; avoid special characters that can break parser compatibility.

## Quality gate (must pass)

Before returning, verify:
- No invented facts.
- No placeholders (`TODO`, `TBD`, `Unknown`) unless explicitly justified.
- `docs/navigation.md` and `docs/flows.md` describe the same real navigation.
- `README.md` links correctly to all generated docs files.
- Cross-file terminology is consistent (same route/screen names everywhere).

## Optional helpers

If helper scripts/templates exist in this skill folder, they are scaffolding only.
They must never be treated as source of truth; final output must be manually validated against repository code.

## Non-goals

- Do not modify runtime code just to “fit” documentation.
- Do not preserve stale docs when repository behavior has changed.
