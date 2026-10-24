# GitHub (Experimental, Gen 2) Migration Guide

## Upgrading to 1.0.0

This release removes the `workflow_job_steps`, `contributor_activity_weeks`, and `release_assets` child streams. Their data is now included as arrays on the parent streams.

### What changed

- `workflow_jobs.steps` contains the workflow job steps.
- `contributor_activity.weeks` contains the contributor's weekly activity.
- `releases.assets` contains up to 100 release assets per release.
- `releases.assets` does not include the removed `release_assets` stream's `label` and `state` fields because GitHub's GraphQL `ReleaseAsset` type does not expose them. Keep the existing `release_assets` table before dropping it if you need those values.

### Required actions

After upgrading to version 1.0.0:

1. **Refresh your source schema** to add the array columns and remove the child streams.
2. **Clear or reset `workflow_jobs`, `contributor_activity`, and `releases`** if you need historical data in the new array columns.
3. **Drop the downstream tables** for `workflow_job_steps`, `contributor_activity_weeks`, and `release_assets` after confirming they are no longer needed.
