# GitHub Migration Guide

## Upgrading to 3.0.0

This release changes the primary key for the `workflow_runs` stream to correctly preserve all workflow run attempts.

### What changed

The primary key for the `workflow_runs` stream has been changed from `[id]` to `[id, run_attempt]`. Previously, when a workflow was re-run, only the latest attempt was preserved because all attempts share the same `id`. With this change, all attempts are now preserved as separate records.

### Affected streams

- `workflow_runs`

### Required actions

After upgrading to version 3.0.0:

1. **Reset the `workflow_runs` stream** to re-sync all historical data with the new composite primary key
2. **Update downstream queries and dashboards** that rely on the `workflow_runs` primary key to account for the new `[id, run_attempt]` composite key

## Upgrading to 2.0.0

This release introduces breaking changes to the `reactions` object schema, which appears in multiple streams. The GitHub API returns reaction fields named `+1` and `-1`, but these field names contain special characters that are not supported by some destinations, causing sync errors.

### What changed

The reaction fields have been renamed for compatibility:

- `+1` → `plus_one`
- `-1` → `minus_one`

### Affected streams

All streams containing the `reactions` object are affected:

- `comments`
- `commit_comments`
- `issue_events`
- `issues`
- `releases`
- `review_comments`

### Required actions

After upgrading to version 2.0.0:

1. **Refresh your source schema** in the Airbyte UI to see the updated field names
2. **Reset affected streams** to re-sync data with the new field names (recommended if you need historical data with the corrected schema)
3. **Update downstream queries and dashboards** that reference the old `+1` and `-1` fields to use `plus_one` and `minus_one` instead
