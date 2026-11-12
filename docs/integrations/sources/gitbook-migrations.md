import MigrationGuide from '@site/static/_migration_guides_upgrade_guide.md';

# GitBook Migration Guide

## Upgrading to 0.1.0

Version 0.1.0 removes the `insights_traffic` stream.

### What changed

The `insights_traffic` stream, which read page-view counts from `GET /v1/spaces/{spaceId}/insights/traffic`, has been removed from the connector. The `users`, `organizations`, `content`, and `org_members` streams are unchanged.

### Why this changed

GitBook removed the `GET /v1/spaces/{spaceId}/insights/traffic` endpoint from its public API. The endpoint now returns `404 API operation not found` and no longer appears in GitBook's published OpenAPI specification (`https://api.gitbook.com/openapi.json`). Site analytics are now exposed only through the org/site-scoped `POST /v1/orgs/{organizationId}/sites/{siteId}/insights/events/aggregate` endpoint, which requires an organization and site ID rather than a space ID and returns a different data shape, so it is not a drop-in replacement for this stream. Any sync that selected `insights_traffic` failed with a 404 error.

### Who is affected

Only connections that have the `insights_traffic` stream selected. Connections syncing only `users`, `organizations`, `content`, or `org_members` are not affected and require no action.

### Required actions

1. Upgrade the connector to 0.1.0.
2. Open the connection's **Schema** tab and refresh the source schema. The `insights_traffic` stream will disappear from the list; confirm the schema change.
3. Optionally drop the `insights_traffic` table in your destination; the connector will no longer write to it.

## Connector upgrade guide

<MigrationGuide />
