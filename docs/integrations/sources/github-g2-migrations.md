# GitHub (Experimental, Gen 2) Migration Guide

## Upgrading to 1.0.0

This release removes the `workflow_job_steps`, `contributor_activity_weeks`, and `release_assets` child streams. `workflow_job_steps` and `contributor_activity_weeks` have no replacement; release asset download URLs move to `releases.asset_download_urls`.

### What changed

- `workflow_job_steps` is removed with no replacement. Job-level `status`, `conclusion`, `started_at`, `completed_at`, and `created_at` remain on `workflow_jobs`; per-step timing and step names are no longer emitted.
- `contributor_activity_weeks` is removed with no replacement. Per-week additions, deletions, and commits are no longer emitted.
- `releases.asset_download_urls` contains up to 100 asset download URLs per release.
- Other release asset metadata (`id`, `name`, `size`, `download_count`, `content_type`, `digest`, `label`, `state`, and uploader) is no longer emitted. Keep the existing `release_assets` table if you need those values.

### Required actions

After upgrading to version 1.0.0:

1. **Refresh your source schema** to add `releases.asset_download_urls` and remove the child streams.
2. **Clear or reset `releases`** if you need historical asset download URLs.
3. **Drop the downstream tables** for `workflow_job_steps`, `contributor_activity_weeks`, and `release_assets` after confirming they are no longer needed.
