---
name: close-gitflow-release
description: Close a GitFlow release in a repository that uses `main`, `develop`, and `release/*` branches. Use when the user asks to finish, publish, merge, complete, or close a release that already exists on a `release/*` branch and the workflow requires merging into `main`, tagging the release, integrating it back into `develop`, pushing all required refs, and deleting the release branch.
---

# Close GitFlow Release

Follow this workflow when the release has already been prepared and must be completed end to end.

## Required Sequence

1. Read the repository `AGENTS.md` and confirm the release branch, target version, and current git status.
2. Verify the release branch contains the intended release-preparation commits.
3. Commit any final release-only adjustments still pending on the release branch before closure.
4. Merge `release/<version>` into `main` using a non-interactive merge.
5. Create the release tag, normally `<version>`, on the resulting `main` commit.
6. Integrate the release back into `develop`.
   - Prefer the repository's established pattern.
   - If the repository merges the tag into `develop`, follow that.
   - If it merges the release branch into `develop`, follow that instead.
7. Push the required refs to the canonical remote.
   - Closing a release is not complete without `push`.
   - Push `main`, `develop`, and the release tag.
8. Delete the local release branch after the remote state is confirmed.
9. If the repository workflow expects remote release-branch deletion too and the user did not forbid it, delete it remotely as well.
10. Verify the final state: clean working tree, release branch gone locally, tag present, and remote updated.

## Non-Negotiable Rules

- Do not claim the release is closed if the merge or tag exists only locally.
- Do not skip `push`.
- Do not tag the wrong commit. The tag must represent the published release commit on `main`.
- Do not delete the release branch before confirming the remote update.
- If the repository's local `AGENTS.md` defines stricter release closure rules, follow that file.

## Repository Pattern Check

Before closing, inspect recent history to match the repo's actual convention:

- merge message shape for release branches
- whether `develop` receives the release branch or the release tag
- tag naming style such as `1.0.13` vs `v1.0.13`

Reuse that pattern instead of inventing a new one.

## Finish State

A closed release means all of the following are true:

- `main` contains the release merge
- the release tag exists on the correct commit
- `develop` has the release integrated
- the required refs were pushed
- the local release branch was deleted

If any of those are missing, the release is not closed yet.
