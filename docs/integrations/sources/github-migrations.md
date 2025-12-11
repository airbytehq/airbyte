# GitHub Migration Guide

## Upgrading to 3.0.0

This release changes the primary key for the `workflow_runs` stream to correctly preserve all workflow run attempts.

### What changed

The primary key for the `workflow_runs` stream has been changed from `[id]` to `[id, run_attempt]`. Previously, when a GitHub workflow was re-run, only the latest attempt was preserved because all attempts share the same `id`. With this change, all attempts are now preserved as separate records.

GitHub allows workflows to be [re-run within 30 days](https://docs.github.com/en/actions/managing-workflow-runs/re-running-workflows-and-jobs) of the original run. Each re-run increments the `run_attempt` field while keeping the same `id`. The new composite primary key ensures that all attempts are captured and deduplicated correctly.

### Primary Key changes

| Stream Name     | Old Primary Key | New Primary Key        |
|-----------------|-----------------|------------------------|
| `workflow_runs` | `[id]`          | `[id, run_attempt]`    |

### Affected streams

- `workflow_runs`

### Refresh affected schemas and reset data

1. Select **Connections** in the main navbar.
   1. Select the connection(s) affected by the update.
2. Select the **Replication** tab.
   1. Select **Refresh source schema**.
   2. Select **OK**.

```note
Any detected schema changes will be listed for your review.
```

3. Select **Save changes** at the bottom of the page.
   1. Ensure the **Reset affected streams** option is checked.

```note
Depending on destination type you may not be prompted to reset your data.
```

4. Select **Save connection**.

```note
This will reset the data in your destination and initiate a fresh sync.
```

For more information on resetting your data in Airbyte, see [this page](/platform/operator-guides/clear).

### Update downstream systems

After the data reset completes, update any downstream queries, dashboards, or applications that rely on the `workflow_runs` primary key:

- If you were using `id` as a unique identifier, update your queries to use the composite key `(id, run_attempt)` instead
- If you have foreign key relationships based on `id`, consider whether you need to account for multiple attempts per workflow run
- Review any deduplication logic that assumed `id` was unique

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
