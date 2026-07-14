---
name: prepare-android-release
description: Prepare an Android release in a GitFlow-style repository. Use when the user asks to prepare, start, cut, or bump a release and the workflow requires creating a `release/*` branch from `develop`, updating `versionCode` and `versionName`, moving entries from `Unreleased` into a numbered section in `CHANGELOG.md`, and refreshing Firebase App Distribution `releaseNotes` in `app/build.gradle.kts`.
---

# Prepare Android Release

Follow this workflow when the user wants the release prepared but not yet closed.

## Required Sequence

1. Read the repository `AGENTS.md` and any release-related docs before changing files.
2. Inspect the current branch, recent tags, and the app version in `app/build.gradle.kts`.
3. Determine the next release version from the repository history or the user's explicit target.
4. Create or switch to `release/<version>` from `develop` before editing release files.
5. Update `app/build.gradle.kts`:
   - bump `versionCode`
   - bump `versionName`
   - rewrite Firebase App Distribution `releaseNotes` as a short customer-facing summary of that release
6. Update `CHANGELOG.md`:
   - keep `Unreleased` at the top
   - create `## [<version>] - <YYYY-MM-DD>`
   - move the release-specific entries under that version
7. Review the diff and confirm that only release-preparation files changed unless the user explicitly requested more.
8. Commit with the repository's release message convention, usually `prepara release <version>`.

## Non-Negotiable Rules

- Do not prepare the release on `develop` if the repository expects a dedicated `release/*` branch.
- Do not invent a version when the repository history makes the next version clear.
- Do not leave Firebase App Distribution `releaseNotes` as a developer changelog dump. They must be a brief customer-facing summary.
- Do not modify unrelated release sections in `CHANGELOG.md`.
- If the repository's local `AGENTS.md` defines stricter release steps, follow that file.

## File Checklist

- `app/build.gradle.kts`
- `CHANGELOG.md`
- `AGENTS.md` only if the user explicitly asks to change project rules

## Finish State

A prepared release means all of the following are true:

- the current branch is `release/<version>`
- `versionCode` and `versionName` match the target release
- `CHANGELOG.md` contains the new version section
- Firebase App Distribution `releaseNotes` matches the same release as a customer-facing summary
- the preparation commit exists locally

Do not treat a prepared release as closed. Closing is a separate workflow.
