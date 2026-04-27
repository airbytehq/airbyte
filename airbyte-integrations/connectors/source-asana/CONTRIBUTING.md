# Contributing to source-asana

For general guidance on contributing to Airbyte connectors, see the [Connector Development documentation](https://docs.airbyte.com/connector-development/).

## Incremental Stream Considerations

The Asana API supports `modified_since` filtering on the `projects` and `tasks` endpoints. The connector is a hybrid manifest + Python custom components connector. All streams are defined in `manifest.yaml`; Python components (`AsanaHttpRequester`) handle `opt_fields` construction and request signing.

**Connector type:** Hybrid (manifest.yaml + Python custom components)

**Analysis status:** Complete stream-by-stream analysis performed. Two streams now support incremental sync (`projects` via this PR, `tasks` via airbytehq/airbyte#76838). Remaining streams are substreams without independent filtering, small reference datasets, or endpoints lacking `modified_since` support.

### Incremental Streams

| Stream | Sync Mode | Cursor Field | API Filter | Notes |
|--------|-----------|-------------|------------|-------|
| projects | incremental | modified_at | `modified_since` query param | `GET /projects?modified_since=<cursor>` |
| tasks | incremental | modified_at | `modified_since` query param | Added by airbytehq/airbyte#76838 |

### Full-Refresh Streams (Not Actionable)

| Stream | Reason | Evidence |
|--------|--------|----------|
| workspaces | Small dataset; no `modified_since` | `GET /workspaces` returns all workspaces; typically 1-5 per account |
| tags | No `modified_since` support | Asana Tags API has no date-based filtering |
| users | No `modified_since` support | Asana Users API has no date-based filtering |
| teams | No `modified_since` support | Asana Teams API has no date-based filtering |
| team_memberships | Substream of teams; no filtering | Per-team endpoint; no `modified_since` |
| sections_compact | Substream of projects; no filtering | Per-project endpoint; no `modified_since` |
| sections | Substream of projects; no filtering | Per-project endpoint; no `modified_since` |
| stories_compact | Substream of tasks; no filtering | Per-task endpoint; no `modified_since` |
| stories | Substream of tasks; no filtering | Per-task endpoint; no `modified_since` |
| attachments_compact | Substream of tasks; no filtering | Per-task endpoint; no `modified_since` |
| attachments | Substream of tasks; no filtering | Per-task endpoint; no `modified_since` |
| portfolios_compact | No `modified_since` support | Asana Portfolios API has no date-based filtering |
| portfolios | No `modified_since` support | Asana Portfolios API has no date-based filtering |
| portfolios_memberships | Substream of portfolios; no filtering | Per-portfolio endpoint |
| custom_fields | Per-workspace; no filtering | `GET /custom_fields` has no date-based filtering |
| organization_exports | Job-based; not time-series | Returns export job objects |
| events | Event-based sync token model | Uses sync tokens, not timestamp cursors |
| portfolio_items | Substream of portfolios; no filtering | Per-portfolio endpoint |
