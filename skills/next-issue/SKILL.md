---
name: next-issue
description: Start work on a GitLab issue by selecting it from conversation context or project triage, assigning it to the authenticated user, creating the appropriate issue branch, and beginning implementation. Use when the user asks to take, start, pick, or work on the next issue in a GitLab project.
---

# Next Issue

Start one issue as an independent unit of work and continue through implementation. Invocation of this skill as part of a request to start an issue authorizes assigning the selected issue to the authenticated GitLab user and creating or switching to its work branch. It does not authorize overwriting unrelated local changes, reassigning another person's issue, or other destructive Git operations.

## Select the issue

1. Confirm the repository uses GitLab and that `glab` is authenticated for its remote. If either check fails, report the exact blocker and stop before mutation.
2. Read the global and applicable local `AGENTS.md`, the repository `README.md`, and any concise triage, contribution, branching, or release documentation relevant to starting work.
3. Prefer an issue explicitly identified in the conversation. Otherwise inspect open GitLab issues and choose according to documented project triage rules and the current conversation, considering priority labels, milestone, status or workflow labels, dependencies, and whether the issue is ready.
4. Exclude issues assigned to another person unless the user explicitly selected one; in that case, report its current assignee and ask before reassigning it.
5. If the evidence does not identify one clear next issue, present the two or three strongest candidates with the deciding metadata and ask the user to choose. Do not assign an issue or change branches while selection is ambiguous.

## Start the work

1. Read the complete issue, including relevant discussion, links, acceptance criteria, and dependencies. Confirm it is open and actionable.
2. Inspect `git status` before changing branches. Preserve unrelated or unexpected changes and stop for direction when they would interfere with the workflow.
3. Assign the issue to the GitLab user authenticated by `glab`. Verify the assignment succeeded before proceeding.
4. Follow repository-specific branch rules. When none are defined, update local `develop` safely from its remote and create `feature/<issue-number>-<short-slug>` from `develop`.
5. Analyze the affected code and tests, state a concise implementation direction, then implement the issue. Follow local architecture, localization, documentation, and validation rules.
6. Run the narrowest reliable validation that demonstrates the change. Do not close the issue merely because implementation exists locally; closing requires the repository's complete validation, commit, push, and merge workflow.

Keep the selected issue number visible in progress updates and the final handoff. Report the assignment, branch name, completed work, validation, and any remaining blockers.
