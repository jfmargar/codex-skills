---
name: android-docs
description: Analyze Android repositories and always generate architecture and navigation documentation. Use when Codex must produce README.md as summary/index plus docs/*.md with Mermaid diagrams, treating templates as optional examples (not literal content).
---

# Android Docs Generator

Use this skill to generate or refresh project documentation for Android repositories.
The agent must analyze the repo directly (read key files) and enrich the docs with
real findings. The script is optional and should only be used as a scaffold; final
docs must reflect the agent's analysis, not template defaults.

## What this skill does

- Analyze the repo to identify modules, entry points, navigation, layers, and key wiring.
- Always generate/update:
  - `README.md` (summary + index)
  - `docs/architecture.md` (architecture)
  - `docs/navigation.md` (navigation)
- Ensures `docs/` exists at the repository root.
- Uses Mermaid diagrams compatible with GitLab (simple `graph`/`sequenceDiagram`, semicolons, no special chars).

## Required analysis (agent-driven)

Read and extract facts from:
- `app/src/main/AndroidManifest.xml` (package, launcher, declared activities)
- `app/build.gradle(.kts)` and root Gradle files (deps and modules)
- `app/src/main/res/navigation/*.xml` when present (NavGraph routes)
- Navigation/router classes (e.g., `Router.kt`, `Navigate.kt`, `NavController` usage)
- Package layout (`ui/`, `domain/`, `data/`, `injection/`) and key entry points

Summarize findings in the docs using concrete file references (paths) and real names.
Avoid generic statements that are not backed by the repo content.

## Quick start

From the repository root:

```
python3 /Users/jfmargar/.codex/skills/android-docs/scripts/generate_docs.py
```

This overwrites existing docs with updated content.

## Behavior and expectations

- If docs already exist, the script re-analyzes the project and overwrites them.
- Diagram labels are sanitized to avoid GitLab Mermaid parse errors.
- If some elements are missing (e.g., no `dabase` module), the script will still
  generate the files with best-effort data.

## Templates

Templates live in `assets/` and are optional examples:
- `assets/README.md.tpl`
- `assets/architecture.md.tpl`
- `assets/navigation.md.tpl`

Edit templates if you want to adjust sections or layout. The agent should use them
as layout hints, not as literal content.
