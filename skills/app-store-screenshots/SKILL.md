---
name: app-store-screenshots
description: "Create App Store screenshot sets from real app screens, including capture planning, simulator screenshots, and marketing compositions with short commercial copy. Use when Codex needs to: (1) choose the strongest App Store screens from a project's docs or product brief, (2) capture fresh screenshots from iPhone or iPad simulators, (3) package screenshots into store-ready PNGs in exact App Store Connect dimensions, or (4) regenerate promotional screenshot art for another project."
---

# App Store Screenshots

## Overview

Use this skill to turn real app screens into App Store screenshot sets that are both product-accurate and submission-ready. Start from the project's own product docs, verify current App Store Connect size requirements, capture screens if needed, then generate final marketing PNGs in separate `iphone/` and `ipad/` folders.

## Workflow

1. Read the local `AGENTS.md`, `README.md`, and the most relevant `docs/` files before choosing any screenshot set.
2. Identify the 3-10 screens that best represent the product's core story. Prioritize real product value over utility or settings surfaces.
3. Confirm the current screenshot slot requirements.
   Check App Store Connect placeholders first when available.
   If placeholders are not visible, browse the current Apple documentation before choosing sizes.
4. Capture raw screenshots from the running simulator when the user has not already provided them.
   Prefer the `Build iOS Apps` plugin and `xcodebuildmcp` UI/screenshot tools when available.
   Use the active simulator that matches the requested device class.
5. Keep raw captures and final marketing compositions separate.
   Do not overwrite existing raw screenshots unless the user asked for that.
   Write final compositions to separate `iphone/` and `ipad/` folders.
6. Generate short commercial copy for each screen.
   Keep headlines compact and benefit-led.
   Keep subtitles to one sentence.
   Match the app's tone and language.
7. Validate the outputs.
   Verify every final PNG has exact target dimensions.
   Open at least one file per device class to catch corruption or layout issues.
   If a file is corrupted, regenerate it and prefer atomic writes.

## Choosing Screens

Use the product's own docs as the source of truth.

- Look for the app's primary landing screen, core object detail, organization model, discovery/search, and one distinctive differentiator.
- Avoid debug screens, loading sheets, setup flows, or placeholders unless the user explicitly wants them.
- If one area is weak because the dataset is sparse, replace it with a stronger screen instead of forcing coverage symmetry.
- For iPad, prefer layouts that visibly justify the larger canvas instead of merely repeating the iPhone crop.

## Capturing Screens

When simulator capture is needed:

- Resolve the active iPhone/iPad simulators first.
- Set session defaults explicitly before navigation.
- Navigate the app semantically where possible.
- Capture PNGs at native simulator size.
- Name raw screenshots consistently, for example:
  `01-library-home.png`
  `02-book-detail.png`
  `ipad-01-library-home.png`

## Generating Marketing Art

Use the bundled script when a branded marketing treatment is needed instead of plain raw screenshots.

1. Create a JSON spec based on the example in [references/spec-example.md](references/spec-example.md).
2. Use exact App Store Connect dimensions for each output.
3. Run:

```bash
python3 -m venv .venv-appstore-art
.venv-appstore-art/bin/python -m pip install Pillow
.venv-appstore-art/bin/python /Users/jfmargar/.codex/skills/app-store-screenshots/scripts/generate_marketing_shots.py /absolute/path/to/spec.json
```

4. If a project already has a local venv with Pillow, reuse it instead of creating a new one.
5. If `Pillow` is missing, install it into a local venv only. Do not rely on global `pip install`.

## Copy Rules

- Lead with the user benefit, not the implementation.
- Keep titles to roughly 3-8 words when possible.
- Keep subtitles to one short sentence.
- Avoid feature dumping, buzzwords, and generic claims like "best" or "ultimate".
- Keep the sequence coherent: overview first, deeper detail later.

## Validation

- Check dimensions with `sips -g pixelWidth -g pixelHeight`.
- Open one or more outputs visually after generation.
- If App Store Connect placeholders differ from your assumptions, regenerate to the exact placeholder dimensions.
- If the user asks for a new project, do not reuse old copy blindly. Re-derive the messaging from that project's docs.

## Resources

- `scripts/generate_marketing_shots.py`: generic compositor for App Store marketing screenshots.
- `references/spec-example.md`: example JSON spec for the compositor.
