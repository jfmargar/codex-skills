---
name: kmp-docs-generator
description: Analyze Kotlin Multiplatform Compose repositories and generate docs/architecture.md, docs/navigation.md, docs/overview.md, plus AGENTS.md. Use when you need docs derived from repo analysis; templates are optional examples, not literal content.
---

# kmp-docs-generator

Codex CLI skill that generates project documentation by overwriting:

- docs/architecture.md (generated from analysis)
- docs/navigation.md (summary built from docs/flows.md + project scan)
- docs/overview.md (project analysis)
- AGENTS.md (generated from analysis)

The skill reads the current working directory as the target project.

## Invocation

Default usage (run from target project root):

    kmp-docs-generator()

Example:

    cd /path/to/target/project
    kmp-docs-generator()

## Inputs used

- Optional templates: assets/architecture.md, assets/AGENTS.md (used as layout hints)
- Optional: docs/flows.md (used to summarize navigation)
- Project scan: Kotlin sources, Gradle files, and module layout in the target repo

## Expected output

    AGENTS.md
    docs/
     ├── architecture.md
     ├── navigation.md
     └── overview.md

## Notes

- This skill overwrites AGENTS.md and the three docs files every run.
- If docs/flows.md is missing, navigation.md includes a placeholder note.
- The generator enriches docs with real findings (entry points, layers, dependencies, routes).
