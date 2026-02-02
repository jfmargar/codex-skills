---
name: android-docs
description: Generate and refresh README.md and docs/*.md for Android repos using Mermaid diagrams and a consistent template.
metadata:
  short-description: Android docs generator
---

# Android Docs Generator

Use this skill to generate or refresh project documentation for Android repositories.
It creates or updates `README.md` and `docs/*.md` (including Mermaid diagrams) based on
project analysis.

## What this skill does

- Scans the repo to identify modules, entry points, navigation, and API wiring.
- Generates/updates:
  - `README.md`
  - `docs/arquitectura.md`
  - `docs/dabase-arquitectura.md`
  - `docs/customizacion-dabase.md`
  - `docs/flows.md`
  - `docs/structure.json`
- Uses Mermaid diagrams compatible with GitLab (simple `graph` syntax, semicolons, no special chars).

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

Templates live in `assets/` and are used by the script:
- `assets/README.md.tpl`
- `assets/arquitectura.md.tpl`
- `assets/dabase-arquitectura.md.tpl`
- `assets/customizacion-dabase.md.tpl`
- `assets/flows.md.tpl`
- `assets/structure.json.tpl`

Edit templates if you want to adjust wording or sections.
