# Sentry Migration Guide

## Upgrading to 1.0.0

Sentry deprecated the legacy, non-org-scoped projects endpoint (`GET /api/0/projects/`). This release migrates the `projects` stream to Sentry's organization-scoped endpoint (`GET /api/0/organizations/{organization}/projects/`).

### What changed

- The `projects` stream previously used `GET /api/0/projects/`, which returned every project the authentication token could access across **all** organizations.
- It now uses `GET /api/0/organizations/{organization}/projects/`, which returns **only the projects that belong to the organization configured in the connector setup**.

As a result, if your token had access to projects in organizations other than the one configured in the connector, those projects are no longer returned by the `projects` stream.

### Affected streams

- `projects`

### Required actions

Because the set of projects returned by the stream can change, previously synced project data may no longer be produced by the source and could be removed from your destination on the next Full Refresh - Overwrite sync.

Before accepting this breaking change:

1. **Back up the existing data** for the `projects` stream in your destination, so you retain any historical projects that will no longer be returned.
2. After upgrading, **run a Full Refresh - Overwrite sync** of the `projects` stream so the destination reflects the org-scoped result set.
3. If you need projects from more than one organization, configure a separate connection per organization.

### Required token scopes

Confirm your [authentication token](https://docs.sentry.io/api/auth/#auth-tokens) includes the scopes required by the streams you sync. Across all streams, the required scopes are `org:read`, `event:read`, and `project:read`. The `projects` stream specifically requires `org:read`.
