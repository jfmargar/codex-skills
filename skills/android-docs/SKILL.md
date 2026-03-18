---
name: android-docs
description: Analyze Android repositories and always generate architecture and navigation documentation. Use when Codex must produce README.md as summary/index plus docs/*.md with Mermaid diagrams, treating templates as optional examples (not literal content).
---

# Android Docs Generator

Use this skill to generate or refresh project documentation for Android repositories.
The agent must analyze the repo directly and write docs from real findings.

## Default mode (required)

This skill is **agent-driven by default**. Do not depend on scripts for core behavior.

- The agent must inspect the repository and produce docs directly.
- The agent must prioritize real code evidence over templates.
- The agent must document navigation flows, routes, and screens from actual implementation.

## Required outputs

Always generate/update:
- `README.md` (summary + docs index)
- `docs/architecture.md`
- `docs/navigation.md`

Ensure `docs/` exists in repository root.

## Required repository analysis

Read and extract facts from:
- `app/src/main/AndroidManifest.xml` (package, launcher, declared activities, `Application`)
- `app/build.gradle(.kts)` + root Gradle files (`settings.gradle(.kts)`, `gradle/libs.versions.toml`)
- `app/src/main/res/navigation/*.xml` when present
- Compose navigation code (`NavHost`, `navigation<...>`, `composable<...>`, `navigate(...)`)
- Router/screen models (`AppScreen`, `Screen`, `Router`, etc.)
- Project layers/packages (`ui/`, `domain/`, `data/`, `injection/`, `di/`, and project-specific variants)
- DI wiring (`Koin`/`Hilt`/etc.), repositories, use cases, and key entry points

## Execution workflow (agent)

1. Inspect manifest + entry points.
2. Inspect Gradle + version catalog to identify stack.
3. Inspect navigation implementation (Compose and/or XML nav graphs).
4. Inspect package/layer structure and key wiring (DI, repositories, use cases).
5. Write/update `README.md`, `docs/architecture.md`, `docs/navigation.md` with concrete repo evidence.
6. Validate docs against quality gate before finishing.

## Documentation expectations

- Use concrete names and real paths from repo.
- Avoid generic claims not backed by code.
- Include Mermaid diagrams compatible with GitLab:
  - `graph TD/LR` and `sequenceDiagram`
  - keep labels simple; avoid special characters that break parsing.
- Navigation doc must include:
  - route inventory
  - major functional flows
  - back-stack/pop-up behavior if present
  - shared/reused screens between flows when applicable

## Quality gate before finishing

Before returning, verify docs are not template-like:
- No placeholders (`TODO`, `TBD`, `Unknown`, etc.) unless truly unknown and explicitly stated.
- Navigation section must mention the actual navigation mechanism used by the app.
- Architecture section must mention real stack elements detected (DI, storage, networking, analytics/crash).
- README must link to generated docs.

## Optional helper script

A helper script exists and can be used only as a scaffold, never as final source of truth:

```bash
python3 /Users/jfmargar/.codex/skills/android-docs/scripts/generate_docs.py
```

If used, the agent must still review and correct output before final delivery.
Do not use this script when user explicitly asks for agent-only execution.

## Templates

Templates in `assets/` are optional layout references:
- `assets/README.md.tpl`
- `assets/architecture.md.tpl`
- `assets/navigation.md.tpl`

Do not copy templates literally if repo findings differ.
