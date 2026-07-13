# Sentry Migration Guide

## Upgrading to 1.0.0

Sentry deprecated the legacy, non-org-scoped projects endpoint (`GET /api/0/projects/`). This release migrates the `projects` stream to Sentry's organization-scoped endpoint (`GET /api/0/organizations/{organization}/projects/`) and adds a new `all_projects_detail` stream.

### What changed

- The `projects` stream previously used `GET /api/0/projects/`, which returned every project the authentication token could access across **all** organizations.
- It now uses `GET /api/0/organizations/{organization}/projects/`, which returns **only the projects that belong to the organization configured in the connector setup**.
- The org-scoped endpoint does not return the following six fields that the legacy endpoint returned: `avatar`, `color`, `isInternal`, `isPublic`, `organization`, and `status`. On the `projects` stream these fields are now `null`.
- A new `all_projects_detail` stream was added. It returns the full project-detail payload (the same data as the existing `project_detail` stream, via `GET /api/0/projects/{organization}/{project}/`) for **every** project in the organization, so the six fields above — and the rest of the detailed project serializer — remain available.

### Affected streams

- `projects` — the six fields listed above now return `null`; the stream is scoped to the configured organization.
- `all_projects_detail` — new stream.

### Required actions

:::error Risk of data loss
Follow the steps below to preserve historical data. If you don't, you risk permanent and irreversible loss of data in your destination.
:::

- If you sync the `projects` stream in **Full Refresh - Overwrite** mode, back up the existing `projects` records before upgrading. After the upgrade, the next sync overwrites all previously stored records with the new ones. In the new records the six fields `avatar`, `color`, `isInternal`, `isPublic`, `organization`, and `status` return `null`. In addition, the new endpoint returns only the projects that belong to the organization configured in the connector setup, so any previously stored projects that are no longer returned (for example, projects from other organizations the token could reach) are removed by the overwrite.
- The six fields remain retrievable from the new `all_projects_detail` stream. Enable `all_projects_detail` if you need `avatar`, `color`, `isInternal`, `isPublic`, `organization`, or `status` for your projects.
- Be aware that the `projects` stream now returns information **only for the projects that belong to the organization specified during setup**. If your token previously returned projects from other organizations, those projects will no longer appear in the `projects` stream. If you need projects from more than one organization, configure a separate connection per organization.

### Required token scopes

Confirm your [authentication token](https://docs.sentry.io/api/auth/#auth-tokens) includes the scopes required by the streams you sync. Across all streams, the required scopes are `org:read`, `event:read`, and `project:read`. The `projects` stream specifically requires `org:read`, and the `all_projects_detail` stream requires both `org:read` (to list the organization's projects) and `project:read` (to read each project's detail).
