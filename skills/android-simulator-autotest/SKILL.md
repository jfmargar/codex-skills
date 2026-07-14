---
name: android-simulator-autotest
description: Run near end-to-end Android simulator validation for this KMP app by combining connected tests, unit tests, app launch smoke, logcat crash scan, and docs-driven navigation/flow audit from docs/navigation.md and docs/flows.md.
---

# Android Simulator Autotest

Use this skill when the user asks to validate a feature/screen change on Android with autonomous checks in emulator.

## Preconditions

- Android emulator is running and visible in `adb devices`.
- `ANDROID_SDK_ROOT` is configured (or `ADB_BIN` is passed explicitly).
- Target repo has `./gradlew`.
- For docs-driven flow traversal, include `docs/navigation.md` and `docs/flows.md` (or pass overrides).

## Primary command

```bash
/absolute/path/to/skills/android-simulator-autotest/scripts/run.sh /absolute/path/to/repo
```

This skill is portable: it does not require adding scripts to each project and auto-detects module/app/activity/tasks in the target repo.
The project path argument is mandatory to avoid running against the wrong workspace.

## What it validates

1. Connected Android test task (auto-detected per module, e.g. `:app:connectedDebugAndroidTest`)
2. Unit test task (auto-detected per module, e.g. `:app:testDebugUnitTest` or `:app:test`)
3. App launch smoke (`am start -W`)
4. UI journey smoke in emulator (real control with `adb` + UI hierarchy), with routes inferred from project docs:
   - parses `docs/flows.md` + `docs/navigation.md`
   - derives reachable `Main.*` routes and route transitions
   - attempts auth entry (`Sign In`, `Login`) when visible
   - navigates route labels inferred from docs (not hardcoded to one app)
   - performs scroll interactions and opens detail cards when flow indicates detail transitions
   - attempts profile shortcut if docs mention profile/my-account flow
5. `logcat` critical patterns (`FATAL EXCEPTION`, `AndroidRuntime`, `ANR`)
6. Docs-vs-code audit using:
   - `docs/navigation.md`
   - `docs/flows.md`
   - `composeApp/src/commonMain/kotlin/com/dinamicarea/membersclub/ui/Navigation.kt`
   - `composeApp/src/commonMain/kotlin/com/dinamicarea/membersclub/ui/AppDestination.kt`

## Reports

All outputs are stored in the detected Android module under:

`<android-module>/build/reports/autotest/`

- `connectedDebugAndroidTest.log`
- `test.log`
- `app_launch.log`
- `ui_journey.log`
- `ui_journey_report.md`
- `logcat_critical.log`
- `navigation_flow_audit.md`

## Useful env vars

- `CONNECTED_TEST_TASK`, `UNIT_TEST_TASK` to force Gradle tasks.
- `APP_ID`, `MAIN_ACTIVITY` to override autodetected launch target.
- `FAIL_ON_DOC_DRIFT=1` to fail when docs and routes drift.
- `RUN_UI_JOURNEY=0` to skip UI journey control.
- `ADB_BIN` if SDK path is custom.
- `NAV_DOC`, `FLOWS_DOC`, `NAV_CODE`, `DESTINATION_CODE` to override file paths.

## Agent behavior

1. Run autotest after implementing feature changes.
2. If failing:
   - fix regressions first,
   - rerun until green,
   - summarize exactly what failed and what changed.
3. If docs audit reports drift:
   - state whether code or docs is source of truth,
   - propose/update docs or routes accordingly.
