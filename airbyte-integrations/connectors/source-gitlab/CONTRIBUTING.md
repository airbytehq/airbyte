# Contributing to source-gitlab

For general guidance on contributing to Airbyte connectors, see the [Connector Development documentation](https://docs.airbyte.com/connector-development/).

## Incremental Stream Considerations

**Connector type:** Hybrid (manifest.yaml + Python custom components for partition routing and URL validation)

**Analysis status:** Complete. 23 streams analyzed. 4 use incremental sync via `DatetimeBasedCursor` with `updated_after`/`updated_before` params. 19 are full-refresh. Several full-refresh streams have potential for incremental sync (marked below), but require implementation work.

### Incremental Streams

| Stream | Cursor Field | API Filter | Notes |
|--------|-------------|------------|-------|
| commits | `created_at` (parameterized) | `since`/`until` | Per-project commits |
| issues | `updated_at` (parameterized) | `updated_after`/`updated_before` | Per-project issues |
| merge_requests | `updated_at` (parameterized) | `updated_after`/`updated_before` | Per-project MRs |
| pipelines | `updated_at` (parameterized) | `updated_after`/`updated_before` | Per-project pipelines |

### Full-Refresh Streams

| Stream | Reason | Evidence |
|--------|--------|----------|
| groups | Top-level enumeration; no date filter | GitLab Groups API has no `updated_after` param on list endpoint |
| group_milestones | No `updated_after` support | `GET /groups/:id/milestones` lacks date filtering |
| group_members | No `updated_after` support | `GET /groups/:id/members` lacks date filtering |
| group_labels | No `updated_after` support | `GET /groups/:id/labels` lacks date filtering |
| group_issue_boards | No `updated_after` support | `GET /groups/:id/boards` lacks date filtering |
| epics | Potential for incremental (`updated_after` supported) | `GET /groups/:id/epics?updated_after=` is available but not implemented |
| epic_issues | Substream of epics; no independent filtering | Per-epic endpoint |
| projects | Top-level enumeration; `last_activity_after` exists but different semantics | `GET /projects?last_activity_after=` tracks git activity, not project metadata changes |
| project_milestones | No `updated_after` support | `GET /projects/:id/milestones` lacks date filtering |
| project_members | No `updated_after` support | `GET /projects/:id/members` lacks date filtering |
| project_labels | No `updated_after` support | `GET /projects/:id/labels` lacks date filtering |
| branches | No `updated_after` support | `GET /projects/:id/repository/branches` lacks date filtering |
| releases | Potential for incremental (`updated_at` field exists) | `GET /projects/:id/releases` has `released_at` but no filter param |
| tags | No date fields | Git tags are immutable; no modification timestamps |
| users | No `updated_after` support | `GET /projects/:id/users` lacks date filtering |
| deployments | Potential for incremental (`updated_after` supported) | `GET /projects/:id/deployments?updated_after=` exists but not implemented |
| merge_request_commits | Substream of merge_requests; no independent filtering | Per-MR endpoint |
| pipelines_extended | Substream detail of pipelines; no independent filtering | Per-pipeline detail endpoint |
| jobs | No `updated_after` support | `GET /projects/:id/jobs` only supports `scope[]` filter |
