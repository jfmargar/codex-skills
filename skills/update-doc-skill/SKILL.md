---
description: Prepare architecture and navigation documentation for
  Kotlin Multiplatform Compose projects.
name: update_project_docs
---

# update_project_docs

Codex CLI skill that prepares architecture and navigation documentation
for Kotlin Multiplatform Compose projects.

------------------------------------------------------------------------

## Purpose

This skill automates the preparation of project documentation by:

-   Extracting project structure into `docs/structure.json`
-   Installing documentation prompts into `prompts/`
-   Preparing the project for Codex-driven Markdown flow generation

The skill does not generate the final narrative documentation itself.\
It prepares the inputs required for Codex to generate `docs/flows.md`.

------------------------------------------------------------------------

## Invocation

Default usage (uses Codex target as working directory):

    update_project_docs()

Example (runs against current working directory):

    cd /path/to/target/project
    update_project_docs()

Specify output language:

    update_project_docs(lang="es")

Note: The skill always runs against the current working directory. In Codex,
this is the target project directory.

------------------------------------------------------------------------

## Expected project state after execution

    docs/
     └── structure.json

    prompts/
     ├── flow_prompt.md
     └── generate_flows.md

------------------------------------------------------------------------

## Typical follow-up instruction to Codex

    Generate docs/flows.md using the installed prompts and docs/structure.json

------------------------------------------------------------------------

## Scope

Designed for:

-   Kotlin Multiplatform projects
-   Compose Multiplatform UI
-   Clean Architecture + MVVM patterns
-   State-driven navigation (BottomSheets)

------------------------------------------------------------------------

## Output

Text status messages indicating successful preparation or error details.
