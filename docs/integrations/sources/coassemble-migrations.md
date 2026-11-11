import MigrationGuide from '@site/static/_migration_guides_upgrade_guide.md';

# Coassemble Migration Guide

## Upgrading to 0.1.0

Version 0.1.0 realigns the connector with the current [Coassemble API](https://developers.coassemble.com/api/courses). Coassemble retired the authentication scheme and one of the endpoints the 0.0.x connector relied on, so 0.0.x can no longer authenticate with credentials issued today and fails on the `screen_types` and `trackings` streams.

### What changed

| Area | 0.0.x | 0.1.0 |
| --- | --- | --- |
| Authentication | `Authorization: COASSEMBLE-V1-SHA256 UserId=<user_id>, UserToken=<user_token>` using the `User ID` / `User Token` fields | `Authorization: COASSEMBLE:<workspace_id>:<api_key>` using the new `Workspace ID` / `API Key` fields |
| `screen_types` stream | `GET /api/v1/headless/screen/types` | Removed. The endpoint no longer exists (the API returns `404 NOT_FOUND`) and Coassemble documents no replacement. |
| `trackings` stream | One request to `GET /api/v1/headless/trackings` | One request per course (`?id=<course id>`), because the API now requires a course `id`. Each record gains a `course_id` field identifying the parent course. |
| Pagination | Started at `page=1` with 20 records per page | Starts at `page=0` (the API's first page) with 100 records per page, so the first page of courses and trackings is no longer skipped |

### Who is affected

All users of this connector: the credential fields are replaced, so every existing connection must be reconfigured. Users who had the `screen_types` stream selected must additionally deselect it.

### Required actions

1. In Coassemble, open the Developer section of your workspace settings and copy your **Workspace ID** and generate (or copy) a workspace **API Key**. The legacy user token is not accepted by the new scheme.
2. Upgrade the connector to 0.1.0, then open the source settings in Airbyte and enter the Workspace ID and API Key.
3. Refresh the source schema on each connection, deselect `screen_types` if it was selected, and save the connection.
4. If you sync `trackings`, note that records now include `course_id`; run a sync to backfill the stream (it is full refresh only).

## Connector upgrade guide

<MigrationGuide />
