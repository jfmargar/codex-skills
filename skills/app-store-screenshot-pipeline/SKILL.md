---
name: app-store-screenshot-pipeline
description: Capture and prepare App Store screenshots for iOS apps across iPhone and iPad. Use when Codex needs to select a product screenshot story, run an app on simulators with Build iOS Apps/XcodeBuildMCP, capture raw simulator PNGs of core functionality, reuse a signed-in simulator session when appropriate, organize artifacts in a project, validate dimensions, or generate commercial App Store marketing screenshots from raw captures.
---

# App Store Screenshot Pipeline

## Overview

Produce two artifact layers:

- `raw/`: native simulator screenshots of real app screens.
- `marketing/`: App Store Connect-ready promotional PNGs built from raw screenshots, copy, and exact target dimensions.

Default to preserving accepted raw captures. If the user explicitly asks to redo or overwrite them, replace the existing files in place so downstream marketing assets can be regenerated from the updated set. Generate marketing images into separate `iphone/` and `ipad/` folders.

## Workflow

1. Read project context first: local `AGENTS.md`, `README.md`, and the most relevant product docs.
2. Derive the screenshot story from the docs before touching the simulator. Write down the core screens, differentiators, and how each one is reached in the app.
3. Resolve simulators: prefer the exact device classes requested by the user. If those simulators are already booted and signed in, reuse that live session instead of rebuilding auth state.
4. Only build and launch when needed: call `session_show_defaults`, then configure defaults with project/workspace, scheme, configuration, simulator, and bundle id. Use `build_run_sim` only if the current running session is missing, stale, or on the wrong simulator.
5. Inspect UI before capture: use `wait_for_ui` or `snapshot_ui`; navigate semantically with element refs and verify that real content is loaded.
6. Capture raw PNGs: prefer native PNGs via `xcrun simctl io <udid> screenshot <path>` after using XcodeBuildMCP for build/navigation. XcodeBuildMCP screenshots may be reduced previews, so validate actual saved PNG dimensions.
7. Save under the project, normally:

```text
AppStoreScreenshots/
  raw/
    iphone-<device>/
    ipad-<device>/
  marketing/
    iphone/
    ipad/
```

8. If the user asks to overwrite previous captures, replace the matching raw files instead of creating parallel duplicates.
9. Write or update `raw/README.md` with device, OS, dimensions, screen purpose, and any caveats.
10. Validate dimensions and non-empty files with `scripts/screenshot_inventory.py`.
11. In the marketing phase, verify current App Store Connect screenshot size requirements before choosing output dimensions. See `references/marketing-workflow.md`.

## Screen Selection

Prefer this sequence when applicable:

1. Main/home/dashboard with real content.
2. Core object detail.
3. Creation/editing flow.
4. Organization/filtering/search.
5. Differentiating feature, such as AI, automation, insights, collaboration, or offline support.
6. Status/history/activity screen.
7. Resume/recap or "continue where you left off" screen when the product has one.

Avoid login/onboarding unless the app cannot be accessed or the user explicitly wants acquisition/auth screenshots. If a simulator is unauthenticated, first try to reuse another signed-in simulator session only when the user approves or asks for it.

When the product uses AI features, explicitly look for screens that prove differentiated value, for example recommendations, summaries, recap/history, or personalized assistance. Do not assume these surfaces are visible immediately; some require background loading or previously generated content.

For detail screens, prefer real user-created or user-followed content over generic placeholders, fixtures, or empty states unless the user requests otherwise.

If the user asks for "the same screenshots on iPad as iPhone", mirror the same story beats first, then adapt framing only where the larger layout exposes more useful context.

## Session Reuse Between Simulators

For Firebase/Auth apps, copying only the app data container may not transfer auth; simulator keychain may be required.

Use this only for local simulator-to-simulator capture workflows:

1. Stop the app on both simulators.
2. Get data containers while simulators are booted, or record paths before shutdown.
3. Copy the source app container `Library/` and `Documents/` into the target app container.
4. If auth still fails, shut down the target simulator and copy the source simulator keychain files:

```text
<sim>/data/Library/Keychains/keychain-2-debug.db*
```

5. Never store keychain backups or database files inside the repo. Use `/tmp` if a backup is needed.
6. Relaunch and verify with `wait_for_ui`.

If both requested simulators are already running and signed in, skip container/keychain transfer and capture directly from those sessions. Only fall back to data migration when a requested simulator is not in the right state.

## Raw Capture Naming

Use stable numeric names:

```text
01-home.png
02-detail.png
03-create-item.png
04-search.png
05-insights.png
```

Use names that describe the screen, not the marketing headline. Keep device separation in folders rather than file prefixes.

When the same story is captured on both device classes, keep the same numbering and semantic names to simplify downstream marketing composition.

Suggested baseline set when the product supports it:

```text
01-home.png
02-list-or-library.png
03-detail.png
04-search-or-discovery.png
05-ai-feature.png
06-recap-or-resume.png
```

## Marketing Phase

Read `references/marketing-workflow.md` before generating marketing images.

Use the raw screenshots as source material. Generate concise commercial copy per screen:

- Headline: 3-8 words, benefit-led.
- Subtitle: one short sentence.
- Tone: match the app and project language.

Validate final PNGs with exact pixel dimensions and open at least one output per device class.

If the user gives device-specific size constraints, treat those exact dimensions as the contract. Do not infer older App Store sizes when the current project already established the required export dimensions.

For async AI or recap screens, wait until the meaningful content has rendered before capturing. A partially loaded summary is worse than skipping the screen and retrying.

## Utility Script

Run this after raw or marketing generation:

```bash
python3 /Users/jfmargar/.codex/skills/app-store-screenshot-pipeline/scripts/screenshot_inventory.py AppStoreScreenshots
```

Use `--json` when another script needs machine-readable output.
