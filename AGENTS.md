# AGENTS.md

Personal Codex operating rules.

## Scope

- Workspace: `~/Workspace`.
- Main areas:
  - `~/Workspace/Dinamic`: work/client projects.
  - `~/Workspace/Personal`: personal apps, agents, skills, experiments, OSS clones.
  - `~/Workspace/Interno`: internal shared libraries and tools.
- Local repo `AGENTS.md`/`agents.md` always overrides this global file. Read it before coding when present.
- Work in the requested repo only unless the task explicitly crosses repositories.
- Missing personal repos: clone under `~/Workspace/Personal`.
- 3rd-party/OSS repos: clone under `~/Workspace/Personal/oss`.
- Missing Dinamic/internal repos: ask before cloning unless the user gives the exact source.

## Operating Rules

- Read `README.md`, local `AGENTS.md`, and relevant `docs/` before non-trivial edits.
- Prefer existing project patterns over introducing a new architecture, framework, or style.
- Keep edits small, reviewable, and scoped to the task.
- Do not perform broad repo-wide search/replace scripts.
- Bugs: add a regression test when practical.
- Update docs when behavior, setup, architecture, navigation, permissions, API, or release flow changes.
- New dependencies require a quick health check: recent maintenance, adoption, compatibility, and no duplicated responsibility.
- Prefer end-to-end verification. If blocked, state exactly what is missing.
- Quote exact errors when reporting failures.
- Transcription: use `mlx_whisper` (`mlx-whisper`) by default.

## Stack Defaults

- KMP/Compose: use `composeApp`, `commonMain`, `androidMain`, `iosMain`, and `composeResources` conventions. Prefer Koin, Ktor, Kotlinx Serialization, Navigation Compose, DataStore, Coil, and Material 3 only when the repo already uses or clearly needs them.
- Modern mobile architecture: default to layered/Clean Architecture for new KMP or modern app work: `domain` for business rules/contracts, `data` for implementations/DTOs/persistence, `ui`/`presentation` for screens, state, and ViewModels.
- Legacy Android: do not force modernization. Preserve Activities/XML/ViewBinding/DataBinding/Java/Kotlin patterns unless the task explicitly asks for refactor.
- Android verification: use the repo's Gradle tasks and flavors. Typical commands are `./gradlew assembleDebug`, unit tests, `lint`, and connected tests only when a device/emulator is available.
- iOS: respect the current setup: SwiftUI/UIKit, Xcode project/workspace, CocoaPods/SPM/manual frameworks. Use `xcodebuild` when CLI validation is practical.
- Backend Kotlin/Ktor: keep config externalized, tests under `src/test/kotlin`, and validate with `./gradlew test` or `./gradlew build`.
- Node/agent projects: inspect `package.json` and lockfile first. Prefer pnpm unless the repo specifies otherwise.
- User-facing strings: use the repo's resource/localization system (`composeResources`, Android resources, `.xcstrings`, etc.); avoid scattered literals in UI code.

## Architecture Guardrails

- Let repo maturity decide strictness: new/KMP projects can be strict; MVPs and legacy apps should stay simple and close to existing flows.
- Do not put business logic in UI when the repo has domain/use-case patterns.
- Do not expose DTOs/storage models through ViewModels or UI state in layered projects.
- Prefer constructor injection and existing DI wiring; avoid creating repositories/services directly in views/composables.
- For `StateFlow` UI state, expose immutable state and keep mutable state private.
- Platform-specific code belongs at platform boundaries unless the repo intentionally differs.

## Git

- Safe by default: `git status`, `git diff`, `git log`.
- Branch changes require user consent unless explicitly requested.
- Destructive ops are forbidden unless explicit: `reset --hard`, `clean`, `restore`, `rm`, force push, deleting branches/tags/files.
- Use `trash` for deletes when available.
- Do not delete, rename, or revert unexpected changes; stop and ask if they affect the task.
- If the user types a command such as "pull and push", that is consent for that command.
- No amend unless asked.
- Commits: prefer Conventional Commits unless repo history/local rules use another convention. Spanish short imperative commits are common in Dinamic repos.
- GitHub: use `gh` CLI for PRs, CI, issues, and reviews.

## Build, Test, CI

- Before handoff, run the narrowest reliable gate that proves the change; run the full gate when feasible.
- Typical gates:
  - KMP: `./gradlew :composeApp:check` or `./gradlew build`.
  - Android: affected flavor assemble + unit tests/lint when configured.
  - iOS: `xcodebuild ... build` and tests when a test target exists.
  - Ktor: `./gradlew test` or `./gradlew build`.
  - Node: package-manager lint/test/typecheck scripts.
- CI red: inspect with `gh run list/view`, rerun/fix when part of the task, and keep going until green when asked.
- Release/version/signing work: read `docs/RELEASING.md` or the closest checklist first.

## Security

- Never commit secrets, tokens, keystore passwords, private IDs, personal profiles, or machine-local paths.
- Use env vars or local config for signing, Firebase, API keys, and credentials.
- Treat `google-services.json`, `GoogleService-Info.plist`, entitlements, bundle IDs, App Groups, and signing changes as sensitive and deliberate.
- Codex skills are public by default: write them in English and use placeholders/env vars for private values.
