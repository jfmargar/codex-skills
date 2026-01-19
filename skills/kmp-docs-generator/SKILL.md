---
name: kmp-docs-generator
description: Generate and overwrite docs/architecture.md, docs/navigation.md, and docs/overview.md for Kotlin Multiplatform Compose projects. Use when you need to regenerate project docs from a fixed architecture template, docs/flows.md summary, and target project analysis.
---

# kmp-docs-generator

Codex CLI skill that generates project documentation by overwriting:

- docs/architecture.md (from assets/architecture.md)
- docs/navigation.md (summary built from docs/flows.md + project scan)
- docs/overview.md (project analysis)
- AGENTS.md (from assets/AGENTS.md)

The skill reads the current working directory as the target project.

## Invocation

Default usage (run from target project root):

    kmp-docs-generator()

Example:

    cd /path/to/target/project
    kmp-docs-generator()

## Inputs used

- Fixed template: assets/architecture.md
- Optional: docs/flows.md (used to summarize navigation)
- Project scan: Kotlin sources in the target repo

## Expected output

    AGENTS.md
    docs/
     ├── architecture.md
     ├── navigation.md
     └── overview.md

## Notes

- This skill overwrites AGENTS.md and the three docs files every run.
- If docs/flows.md is missing, navigation.md includes a placeholder note.
