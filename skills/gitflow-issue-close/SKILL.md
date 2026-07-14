---
name: gitflow-issue-close
description: Complete and close a repository issue using the required GitFlow sequence. Use when the user asks to resolve, finish, complete, merge, or close an issue or task and the repository workflow expects a dedicated feature branch, validation, commit, push, merge into the target branch, and only then issue closure in GitHub or GitLab.
---

# Gitflow Issue Close

Follow this workflow whenever the request is to complete or close an issue in a GitFlow-style repository.

## Required Sequence

1. Identify the target issue and the repository's target integration branch.
2. Confirm there is a dedicated `feature/*` branch for that issue. If it does not exist yet, create it from the integration branch before changing code.
3. Implement the fix or confirm the existing fix is present on the issue branch.
4. Run the narrowest reliable validation that proves the issue is resolved. Quote exact failures if validation does not pass.
5. Commit the changes with a message that matches repository conventions.
6. Push the issue branch to the remote.
7. Merge the issue branch into the target branch required by the repository workflow. Prefer a non-interactive merge path.
8. Push the target branch after the merge if it is not already updated remotely.
9. Close the issue in the tracker only after the merge is complete.
10. Verify the final state: clean working tree, remote branch updated as expected, issue closed.

## Non-Negotiable Rules

- Do not close an issue if the fix exists only locally.
- Do not close an issue after validation alone.
- Do not skip `push`.
- Do not skip the merge into the repository's target branch.
- Do not group unrelated issue work in the same branch.
- If the repository has a local `AGENTS.md`, follow its Git and branching rules when they are stricter or explicitly different.

## Branching Guidance

- In GitFlow repositories, default to `develop` as the integration branch unless the repository documents another rule.
- Use one `feature/*` branch per issue.
- If the fix was started on the wrong branch, stop and move the work into the correct issue branch before closing the issue.

## Closure Behavior

When the user says `close the issue`, interpret that as a request to execute the full closure workflow, not only the tracker action.

Treat issue closure as the last step of delivery:

- validation
- commit
- push
- merge
- remote update confirmation
- tracker closure

If any earlier step is missing, complete it first or explain the blocker instead of closing the issue.
