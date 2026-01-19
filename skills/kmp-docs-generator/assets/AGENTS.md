# Repository Guidelines

## Project Structure & Module Organization

This is a Kotlin Multiplatform project with shared UI using Compose Multiplatform.
- `composeApp/src/commonMain/kotlin` holds shared Kotlin code.
- `composeApp/src/androidMain/kotlin` contains Android-specific code and `AndroidManifest.xml`.
- `composeApp/src/iosMain/kotlin` contains iOS-specific Kotlin code and the entry point for iOS interop.
- `composeApp/src/commonTest/kotlin` contains shared tests.
- `composeApp/src/commonMain/composeResources` contains shared resources.
- `iosApp/iosApp` contains the SwiftUI iOS app wrapper and Xcode project assets.

## Build, Test, and Development Commands

- `./gradlew :composeApp:assembleDebug` builds the Android debug APK.
- `./gradlew :composeApp:test` runs shared (common) unit tests.
- `./gradlew build` runs the full Gradle build for all configured targets.
- iOS: open `iosApp` in Xcode and run the `iosApp` scheme.

## Coding Style & Naming Conventions

- Kotlin and Gradle Kotlin DSL: 4-space indentation, standard Kotlin style, and `PascalCase` for types, `camelCase` for functions/vars.
- Swift files under `iosApp/iosApp`: follow Xcode formatting defaults (typically 2 spaces) and Swift naming conventions.
- Keep Compose UI elements in `App.kt` and shared logic in `commonMain` unless platform APIs are required.
- All user-facing strings must live in `composeApp/src/commonMain/composeResources/values/strings.xml` and be accessed via `stringResource`.

## Testing Guidelines

- Test framework: `kotlin.test` via `commonTest`.
- Place shared tests in `composeApp/src/commonTest/kotlin` and name test classes/functions clearly (e.g., `GreetingTest`, `testGreeting`).
- No coverage thresholds are configured; prioritize testing shared business logic.

## Commit & Pull Request Guidelines

- Current Git history is minimal (`b594b59 initial`), so no established commit message convention is visible.
- Use concise, imperative commit messages (e.g., "Add onboarding screen").
- PRs should include a short summary, linked issue (if any), and screenshots for UI changes on Android and iOS.

## Configuration & Security Notes

- `local.properties` is present and typically contains machine-local SDK paths; avoid committing secrets.
- Prefer editing `gradle.properties` and module `build.gradle.kts` for build configuration changes.

## Architecture & Collaboration Rules

You are an expert mobile architect. This repository enforces Clean Architecture.

Global rules:
- Domain layer contains no framework imports.
- UI layer depends on ViewModels only.
- No business logic in UI.
- Domain-to-UI mappers live in the UI layer (prefer `ui/**/model` or `ui/mappers`), not in Domain or Data.
- No mutable state exposed publicly.
- UI state in ViewModels must be exposed as `StateFlow`; keep `_uiState` as `MutableStateFlow` private.
- Prefer composition over inheritance.
- KMP: shared module owns domain and data contracts.

If a request violates architecture:
- Explain why.
- Propose a compliant alternative.
- Do NOT implement invalid solutions.

Reference docs:
- `docs/overview.md`
- `docs/architecture.md`
- `docs/navigation.md`
