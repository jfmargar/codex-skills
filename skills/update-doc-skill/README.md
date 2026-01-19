# Codex Skill --- update_project_docs

This repository provides a **Codex CLI skill** that automates
documentation generation for mobile projects.\
It executes a structure extractor, prepares documentation prompts, and
writes the required artifacts into the target project --- without adding
tooling inside the project itself.

The skill is designed to integrate with a Codex-based documentation
workflow using:
- `extract_structure.py` to generate `docs/structure.json`
- Language-specific prompts in `prompts/<lang>/` to later generate `docs/flows.md`

------------------------------------------------------------------------

## What this skill does

When invoked, the skill:

1.  Runs `extract_structure.py` against the target project.

2.  Generates `docs/structure.json` inside the project.

3.  Installs documentation prompts for the selected language:

        prompts/flow_prompt.md
        prompts/generate_flows.md

4.  Leaves the project ready for Codex to generate final Markdown
    documentation.

No Python scripts or tooling are stored inside the project --- only
generated documentation artifacts.

------------------------------------------------------------------------

## Repository contents

    update-doc-skill/
     ├── skill.json              Codex skill descriptor
     ├── run.py                  Skill launcher
     ├── extract_structure.py    Project structure extractor
     ├── prompts/
     │    ├── en/
     │    │    ├── flow_prompt.md
     │    │    └── generate_flows.md
     │    └── es/
     │         ├── flow_prompt.md
     │         └── generate_flows.md
     └── README.md               This file

------------------------------------------------------------------------

## Requirements

-   Codex CLI installed and configured
-   Python 3.9+
-   Git

------------------------------------------------------------------------

## Installation

Clone the repository into the Codex skills directory:

``` bash
mkdir -p ~/.codex/skills
cd ~/.codex/skills

git clone https://github.com/<your-user>/update-doc-skill.git update-doc-skill
```

Make the launcher executable:

``` bash
chmod +x ~/.codex/skills/update-doc-skill/run.py
```

Restart Codex CLI if it was running.

------------------------------------------------------------------------

## Verify installation

``` bash
codex skills
```

Expected output:

    update_project_docs  - Updates project documentation by generating structure.json and installing prompts

------------------------------------------------------------------------

## Usage

### Direct CLI invocation

Run it from the target project directory (Codex uses the current working directory):

``` bash
cd /Users/julian/Workspace/MyProject
codex run update_project_docs
```

### Natural language usage

Inside Codex CLI (target directory is used automatically):

    Actualiza la documentación del proyecto

Codex will automatically invoke the skill.

------------------------------------------------------------------------

## Output generated in the project

After execution, the target project will contain:

    MyProject/
     ├── docs/
     │    └── structure.json
     └── prompts/
          ├── flow_prompt.md
          └── generate_flows.md

At this point, Codex can be instructed to generate `docs/flows.md` using
the installed prompts.

------------------------------------------------------------------------

## Updating the skill

``` bash
cd ~/.codex/skills/update-doc-skill
git pull
```

All projects will immediately use the updated extractor and prompts.

------------------------------------------------------------------------

## Using in CI pipelines

Example (GitLab CI):

``` bash
git clone https://github.com/<your-user>/update-doc-skill.git ~/.codex/skills/update-doc-skill
chmod +x ~/.codex/skills/update-doc-skill/run.py

codex run update_project_docs --path $CI_PROJECT_DIR
```

------------------------------------------------------------------------

## Design principles

-   Tooling lives outside projects.
-   Projects receive only generated documentation.
-   Centralized extractor for all repositories.
-   Fully reproducible and CI-friendly.
-   No interactive input required.

------------------------------------------------------------------------

## License

Internal use. Adapt as needed.
