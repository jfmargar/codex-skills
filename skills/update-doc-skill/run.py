#!/usr/bin/env python3
import sys
import shutil
import subprocess
from pathlib import Path

DEFAULT_LANG = "en"
SUPPORTED_LANGS = {"en", "es"}

def main():
    # Project path is always the current working directory
    project_path = Path.cwd().resolve()

    # Optional language argument
    lang = sys.argv[1] if len(sys.argv) >= 2 else DEFAULT_LANG

    if lang not in SUPPORTED_LANGS:
        print(f"Error: unsupported language '{lang}'. Supported languages: {', '.join(SUPPORTED_LANGS)}")
        return 1

    if not project_path.exists():
        print(f"Error: project path not found -> {project_path}")
        return 1

    docs_dir = project_path / "docs"
    prompts_target_dir = project_path / "prompts"

    docs_dir.mkdir(exist_ok=True)
    prompts_target_dir.mkdir(exist_ok=True)

    skill_root = Path(__file__).parent.resolve()

    # 1. Run structure extractor
    extract_script = skill_root / "extract_structure.py"
    if not extract_script.exists():
        print("Error: extract_structure.py not found in skill folder")
        return 1

    print("Generating docs/structure.json ...")

    result = subprocess.run(
        ["python3", str(extract_script), str(project_path)],
        capture_output=True,
        text=True
    )

    if result.returncode != 0:
        print("Structure extraction failed:")
        print(result.stderr)
        return result.returncode

    # 2. Copy language-specific prompts
    prompts_source_dir = skill_root / "prompts" / lang

    if not prompts_source_dir.exists():
        print(f"Error: prompt folder for language '{lang}' not found in skill")
        return 1

    shutil.copy(prompts_source_dir / "flow_prompt.md",
                prompts_target_dir / "flow_prompt.md")

    shutil.copy(prompts_source_dir / "generate_flows.md",
                prompts_target_dir / "generate_flows.md")

    print("Documentation preparation completed successfully.")
    print(f"Project (cwd): {project_path}")
    print(f"Language: {lang}")
    print("Generated: docs/structure.json")
    print("Installed prompts:")
    print(" - prompts/flow_prompt.md")
    print(" - prompts/generate_flows.md")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
