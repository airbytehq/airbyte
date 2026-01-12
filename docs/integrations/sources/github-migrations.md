# GitHub Migration Guide

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
