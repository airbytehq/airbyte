# Sentry full reference

This is the full reference documentation for the Sentry agent connector.

## Supported entities and actions

The Sentry connector supports the following entities and actions.

| Entity | Actions |
|--------|---------|
| Projects | [List](#projects-list), [Get](#projects-get), [Search](#projects-search) |
| Issues | [List](#issues-list), [Get](#issues-get), [Search](#issues-search) |
| Events | [List](#events-list), [Get](#events-get), [Search](#events-search) |
| Releases | [List](#releases-list), [Get](#releases-get), [Search](#releases-search) |
| Project Detail | [Get](#project-detail-get) |

## Projects

### Projects List

Return a list of projects available to the authenticated user.

#### Python SDK

```python
await sentry.projects.list()
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/integrations/connectors/{your_connector_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "projects",
    "action": "list"
}'
```


#### Parameters

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `cursor` | `string` | No | Pagination cursor for next page of results. |


<details>
<summary><b>Response Schema</b></summary>

#### Records

| Field Name | Type | Description |
|------------|------|-------------|
| `id` | `string \| null` |  |
| `name` | `string \| null` |  |
| `slug` | `string \| null` |  |
| `status` | `string \| null` |  |
| `platform` | `string \| null` |  |
| `dateCreated` | `string \| null` |  |
| `isBookmarked` | `boolean \| null` |  |
| `isMember` | `boolean \| null` |  |
| `hasAccess` | `boolean \| null` |  |
| `isPublic` | `boolean \| null` |  |
| `isInternal` | `boolean \| null` |  |
| `color` | `string \| null` |  |
| `features` | `array \| null` |  |
| `firstEvent` | `string \| null` |  |
| `firstTransactionEvent` | `boolean \| null` |  |
| `access` | `array \| null` |  |
| `hasMinifiedStackTrace` | `boolean \| null` |  |
| `hasMonitors` | `boolean \| null` |  |
| `hasProfiles` | `boolean \| null` |  |
| `hasReplays` | `boolean \| null` |  |
| `hasFeedbacks` | `boolean \| null` |  |
| `hasFlags` | `boolean \| null` |  |
| `hasNewFeedbacks` | `boolean \| null` |  |
| `hasSessions` | `boolean \| null` |  |
| `hasInsightsHttp` | `boolean \| null` |  |
| `hasInsightsDb` | `boolean \| null` |  |
| `hasInsightsAssets` | `boolean \| null` |  |
| `hasInsightsAppStart` | `boolean \| null` |  |
| `hasInsightsScreenLoad` | `boolean \| null` |  |
| `hasInsightsVitals` | `boolean \| null` |  |
| `hasInsightsCaches` | `boolean \| null` |  |
| `hasInsightsQueues` | `boolean \| null` |  |
| `hasInsightsAgentMonitoring` | `boolean \| null` |  |
| `hasInsightsMCP` | `boolean \| null` |  |
| `hasLogs` | `boolean \| null` |  |
| `hasTraceMetrics` | `boolean \| null` |  |
| `avatar` | `object \| null` |  |
| `organization` | `object \| null` |  |


</details>

### Projects Get

Return details on an individual project.

#### Python SDK

```python
await sentry.projects.get(
    organization_slug="<str>",
    project_slug="<str>"
)
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/integrations/connectors/{your_connector_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "projects",
    "action": "get",
    "params": {
        "organization_slug": "<str>",
        "project_slug": "<str>"
    }
}'
```


#### Parameters

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `organization_slug` | `string` | Yes | The slug of the organization the project belongs to. |
| `project_slug` | `string` | Yes | The slug of the project to retrieve. |


<details>
<summary><b>Response Schema</b></summary>

#### Records

| Field Name | Type | Description |
|------------|------|-------------|
| `id` | `string \| null` |  |
| `name` | `string \| null` |  |
| `slug` | `string \| null` |  |
| `status` | `string \| null` |  |
| `platform` | `string \| null` |  |
| `dateCreated` | `string \| null` |  |
| `isBookmarked` | `boolean \| null` |  |
| `isMember` | `boolean \| null` |  |
| `hasAccess` | `boolean \| null` |  |
| `isPublic` | `boolean \| null` |  |
| `isInternal` | `boolean \| null` |  |
| `color` | `string \| null` |  |
| `features` | `array \| null` |  |
| `firstEvent` | `string \| null` |  |
| `firstTransactionEvent` | `boolean \| null` |  |
| `access` | `array \| null` |  |
| `hasMinifiedStackTrace` | `boolean \| null` |  |
| `hasMonitors` | `boolean \| null` |  |
| `hasProfiles` | `boolean \| null` |  |
| `hasReplays` | `boolean \| null` |  |
| `hasFeedbacks` | `boolean \| null` |  |
| `hasFlags` | `boolean \| null` |  |
| `hasNewFeedbacks` | `boolean \| null` |  |
| `hasSessions` | `boolean \| null` |  |
| `hasInsightsHttp` | `boolean \| null` |  |
| `hasInsightsDb` | `boolean \| null` |  |
| `hasInsightsAssets` | `boolean \| null` |  |
| `hasInsightsAppStart` | `boolean \| null` |  |
| `hasInsightsScreenLoad` | `boolean \| null` |  |
| `hasInsightsVitals` | `boolean \| null` |  |
| `hasInsightsCaches` | `boolean \| null` |  |
| `hasInsightsQueues` | `boolean \| null` |  |
| `hasInsightsAgentMonitoring` | `boolean \| null` |  |
| `hasInsightsMCP` | `boolean \| null` |  |
| `hasLogs` | `boolean \| null` |  |
| `hasTraceMetrics` | `boolean \| null` |  |
| `team` | `object \| null` |  |
| `teams` | `array \| null` |  |
| `avatar` | `object \| null` |  |
| `organization` | `object \| null` |  |
| `latestRelease` | `object \| null` |  |
| `options` | `object \| null` |  |
| `digestsMinDelay` | `integer \| null` |  |
| `digestsMaxDelay` | `integer \| null` |  |
| `resolveAge` | `integer \| null` |  |
| `dataScrubber` | `boolean \| null` |  |
| `safeFields` | `array \| null` |  |
| `sensitiveFields` | `array \| null` |  |
| `verifySSL` | `boolean \| null` |  |
| `scrubIPAddresses` | `boolean \| null` |  |
| `scrapeJavaScript` | `boolean \| null` |  |
| `allowedDomains` | `array \| null` |  |
| `processingIssues` | `integer \| null` |  |
| `securityToken` | `string \| null` |  |
| `subjectPrefix` | `string \| null` |  |
| `dataScrubberDefaults` | `boolean \| null` |  |
| `storeCrashReports` | `boolean \| integer \| null` |  |
| `subjectTemplate` | `string \| null` |  |
| `securityTokenHeader` | `string \| null` |  |
| `groupingConfig` | `string \| null` |  |
| `groupingEnhancements` | `string \| null` |  |
| `derivedGroupingEnhancements` | `string \| null` |  |
| `secondaryGroupingExpiry` | `integer \| null` |  |
| `secondaryGroupingConfig` | `string \| null` |  |
| `fingerprintingRules` | `string \| null` |  |
| `plugins` | `array \| null` |  |
| `platforms` | `array \| null` |  |
| `defaultEnvironment` | `string \| null` |  |
| `relayPiiConfig` | `string \| null` |  |
| `builtinSymbolSources` | `array \| null` |  |
| `dynamicSamplingBiases` | `array \| null` |  |
| `symbolSources` | `string \| null` |  |
| `isDynamicallySampled` | `boolean \| null` |  |
| `autofixAutomationTuning` | `string \| null` |  |
| `seerScannerAutomation` | `boolean \| null` |  |
| `highlightTags` | `array \| null` |  |
| `highlightContext` | `object \| null` |  |
| `highlightPreset` | `object \| null` |  |
| `debugFilesRole` | `string \| null` |  |


</details>

### Projects Search

Search and filter projects records powered by Airbyte's data sync. This often provides additional fields and operators beyond what the API natively supports, making it easier to narrow down results before performing further operations. Only available in hosted mode.

#### Python SDK

```python
await sentry.projects.search(
    query={"filter": {"eq": {"access": []}}}
)
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/integrations/connectors/{your_connector_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "projects",
    "action": "search",
    "params": {
        "query": {"filter": {"eq": {"access": []}}}
    }
}'
```

#### Parameters

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `query` | `object` | Yes | Filter and sort conditions. Supports operators: eq, neq, gt, gte, lt, lte, in, like, fuzzy, keyword, not, and, or |
| `query.filter` | `object` | No | Filter conditions |
| `query.sort` | `array` | No | Sort conditions |
| `limit` | `integer` | No | Maximum results to return (default 1000) |
| `cursor` | `string` | No | Pagination cursor from previous response's `meta.cursor` |
| `fields` | `array` | No | Field paths to include in results |

#### Searchable Fields

| Field Name | Type | Description |
|------------|------|-------------|
| `access` | `array` | List of access permissions for the authenticated user. |
| `avatar` | `object` | Project avatar information. |
| `color` | `string` | Project color code. |
| `dateCreated` | `string` | Date the project was created. |
| `features` | `array` | List of enabled features. |
| `firstEvent` | `string` | Timestamp of the first event. |
| `firstTransactionEvent` | `boolean` | Whether a transaction event has been received. |
| `hasAccess` | `boolean` | Whether the user has access to this project. |
| `hasCustomMetrics` | `boolean` | Whether the project has custom metrics. |
| `hasFeedbacks` | `boolean` | Whether the project has user feedback. |
| `hasMinifiedStackTrace` | `boolean` | Whether the project has minified stack traces. |
| `hasMonitors` | `boolean` | Whether the project has cron monitors. |
| `hasNewFeedbacks` | `boolean` | Whether the project has new user feedback. |
| `hasProfiles` | `boolean` | Whether the project has profiling data. |
| `hasReplays` | `boolean` | Whether the project has session replays. |
| `hasSessions` | `boolean` | Whether the project has session data. |
| `id` | `string` | Unique project identifier. |
| `isBookmarked` | `boolean` | Whether the project is bookmarked. |
| `isInternal` | `boolean` | Whether the project is internal. |
| `isMember` | `boolean` | Whether the authenticated user is a member. |
| `isPublic` | `boolean` | Whether the project is public. |
| `name` | `string` | Human-readable project name. |
| `organization` | `object` | Organization this project belongs to. |
| `platform` | `string` | The platform for this project. |
| `slug` | `string` | URL-friendly project identifier. |
| `status` | `string` | Project status. |

<details>
<summary><b>Response Schema</b></summary>

| Field Name | Type | Description |
|------------|------|-------------|
| `data` | `array` | List of matching records |
| `meta` | `object` | Pagination metadata |
| `meta.has_more` | `boolean` | Whether additional pages are available |
| `meta.cursor` | `string \| null` | Cursor for next page of results |
| `meta.took_ms` | `number \| null` | Query execution time in milliseconds |
| `data[].access` | `array` | List of access permissions for the authenticated user. |
| `data[].avatar` | `object` | Project avatar information. |
| `data[].color` | `string` | Project color code. |
| `data[].dateCreated` | `string` | Date the project was created. |
| `data[].features` | `array` | List of enabled features. |
| `data[].firstEvent` | `string` | Timestamp of the first event. |
| `data[].firstTransactionEvent` | `boolean` | Whether a transaction event has been received. |
| `data[].hasAccess` | `boolean` | Whether the user has access to this project. |
| `data[].hasCustomMetrics` | `boolean` | Whether the project has custom metrics. |
| `data[].hasFeedbacks` | `boolean` | Whether the project has user feedback. |
| `data[].hasMinifiedStackTrace` | `boolean` | Whether the project has minified stack traces. |
| `data[].hasMonitors` | `boolean` | Whether the project has cron monitors. |
| `data[].hasNewFeedbacks` | `boolean` | Whether the project has new user feedback. |
| `data[].hasProfiles` | `boolean` | Whether the project has profiling data. |
| `data[].hasReplays` | `boolean` | Whether the project has session replays. |
| `data[].hasSessions` | `boolean` | Whether the project has session data. |
| `data[].id` | `string` | Unique project identifier. |
| `data[].isBookmarked` | `boolean` | Whether the project is bookmarked. |
| `data[].isInternal` | `boolean` | Whether the project is internal. |
| `data[].isMember` | `boolean` | Whether the authenticated user is a member. |
| `data[].isPublic` | `boolean` | Whether the project is public. |
| `data[].name` | `string` | Human-readable project name. |
| `data[].organization` | `object` | Organization this project belongs to. |
| `data[].platform` | `string` | The platform for this project. |
| `data[].slug` | `string` | URL-friendly project identifier. |
| `data[].status` | `string` | Project status. |

</details>

## Issues

### Issues List

Return a list of issues (groups) bound to a project. A default query of is:unresolved is applied. To return results with other statuses send a new query value (i.e. ?query= for all results).

#### Python SDK

```python
await sentry.issues.list(
    organization_slug="<str>",
    project_slug="<str>"
)
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/integrations/connectors/{your_connector_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "issues",
    "action": "list",
    "params": {
        "organization_slug": "<str>",
        "project_slug": "<str>"
    }
}'
```


#### Parameters

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `organization_slug` | `string` | Yes | The slug of the organization the issues belong to. |
| `project_slug` | `string` | Yes | The slug of the project the issues belong to. |
| `query` | `string` | No | An optional Sentry structured search query. If not provided an implied "is:unresolved" is assumed. |
| `statsPeriod` | `string` | No | An optional stat period (can be one of "24h", "14d", and ""). |
| `cursor` | `string` | No | Pagination cursor for next page of results. |


<details>
<summary><b>Response Schema</b></summary>

#### Records

| Field Name | Type | Description |
|------------|------|-------------|
| `id` | `string \| null` |  |
| `title` | `string \| null` |  |
| `shortId` | `string \| null` |  |
| `culprit` | `string \| null` |  |
| `level` | `string \| null` |  |
| `status` | `string \| null` |  |
| `type` | `string \| null` |  |
| `count` | `string \| null` |  |
| `userCount` | `integer \| null` |  |
| `firstSeen` | `string \| null` |  |
| `lastSeen` | `string \| null` |  |
| `hasSeen` | `boolean \| null` |  |
| `isBookmarked` | `boolean \| null` |  |
| `isPublic` | `boolean \| null` |  |
| `isSubscribed` | `boolean \| null` |  |
| `logger` | `string \| null` |  |
| `permalink` | `string \| null` |  |
| `platform` | `string \| null` |  |
| `shareId` | `string \| null` |  |
| `numComments` | `integer \| null` |  |
| `issueType` | `string \| null` |  |
| `issueCategory` | `string \| null` |  |
| `isUnhandled` | `boolean \| null` |  |
| `substatus` | `string \| null` |  |
| `metadata` | `object \| null` |  |
| `project` | `object \| null` |  |
| `stats` | `object \| null` |  |
| `statusDetails` | `object \| null` |  |
| `assignedTo` | `object \| null` |  |
| `annotations` | `array \| null` |  |
| `subscriptionDetails` | `object \| null` |  |


</details>

### Issues Get

Return details on an individual issue. This returns the basic stats for the issue (title, last seen, first seen), some overall numbers (number of comments, user reports) as well as the summarized event data.

#### Python SDK

```python
await sentry.issues.get(
    organization_slug="<str>",
    issue_id="<str>"
)
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/integrations/connectors/{your_connector_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "issues",
    "action": "get",
    "params": {
        "organization_slug": "<str>",
        "issue_id": "<str>"
    }
}'
```


#### Parameters

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `organization_slug` | `string` | Yes | The slug of the organization the issue belongs to. |
| `issue_id` | `string` | Yes | The ID of the issue to retrieve. |


<details>
<summary><b>Response Schema</b></summary>

#### Records

| Field Name | Type | Description |
|------------|------|-------------|
| `id` | `string \| null` |  |
| `title` | `string \| null` |  |
| `shortId` | `string \| null` |  |
| `culprit` | `string \| null` |  |
| `level` | `string \| null` |  |
| `status` | `string \| null` |  |
| `type` | `string \| null` |  |
| `count` | `string \| null` |  |
| `userCount` | `integer \| null` |  |
| `firstSeen` | `string \| null` |  |
| `lastSeen` | `string \| null` |  |
| `hasSeen` | `boolean \| null` |  |
| `isBookmarked` | `boolean \| null` |  |
| `isPublic` | `boolean \| null` |  |
| `isSubscribed` | `boolean \| null` |  |
| `logger` | `string \| null` |  |
| `permalink` | `string \| null` |  |
| `platform` | `string \| null` |  |
| `shareId` | `string \| null` |  |
| `numComments` | `integer \| null` |  |
| `issueType` | `string \| null` |  |
| `issueCategory` | `string \| null` |  |
| `isUnhandled` | `boolean \| null` |  |
| `substatus` | `string \| null` |  |
| `metadata` | `object \| null` |  |
| `project` | `object \| null` |  |
| `stats` | `object \| null` |  |
| `statusDetails` | `object \| null` |  |
| `assignedTo` | `object \| null` |  |
| `annotations` | `array \| null` |  |
| `subscriptionDetails` | `object \| null` |  |


</details>

### Issues Search

Search and filter issues records powered by Airbyte's data sync. This often provides additional fields and operators beyond what the API natively supports, making it easier to narrow down results before performing further operations. Only available in hosted mode.

#### Python SDK

```python
await sentry.issues.search(
    query={"filter": {"eq": {"annotations": []}}}
)
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/integrations/connectors/{your_connector_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "issues",
    "action": "search",
    "params": {
        "query": {"filter": {"eq": {"annotations": []}}}
    }
}'
```

#### Parameters

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `query` | `object` | Yes | Filter and sort conditions. Supports operators: eq, neq, gt, gte, lt, lte, in, like, fuzzy, keyword, not, and, or |
| `query.filter` | `object` | No | Filter conditions |
| `query.sort` | `array` | No | Sort conditions |
| `limit` | `integer` | No | Maximum results to return (default 1000) |
| `cursor` | `string` | No | Pagination cursor from previous response's `meta.cursor` |
| `fields` | `array` | No | Field paths to include in results |

#### Searchable Fields

| Field Name | Type | Description |
|------------|------|-------------|
| `annotations` | `array` | Annotations on the issue. |
| `assignedTo` | `object` | User or team assigned to this issue. |
| `count` | `string` | Number of events for this issue. |
| `culprit` | `string` | The culprit (source) of the issue. |
| `firstSeen` | `string` | When the issue was first seen. |
| `hasSeen` | `boolean` | Whether the authenticated user has seen the issue. |
| `id` | `string` | Unique issue identifier. |
| `isBookmarked` | `boolean` | Whether the issue is bookmarked. |
| `isPublic` | `boolean` | Whether the issue is public. |
| `isSubscribed` | `boolean` | Whether the user is subscribed to the issue. |
| `isUnhandled` | `boolean` | Whether the issue is from an unhandled error. |
| `issueCategory` | `string` | The category classification of the issue. |
| `issueType` | `string` | The type classification of the issue. |
| `lastSeen` | `string` | When the issue was last seen. |
| `level` | `string` | Issue severity level. |
| `logger` | `string` | Logger that generated the issue. |
| `metadata` | `object` | Issue metadata. |
| `numComments` | `integer` | Number of comments on the issue. |
| `permalink` | `string` | Permalink to the issue in the Sentry UI. |
| `platform` | `string` | Platform for this issue. |
| `project` | `object` | Project this issue belongs to. |
| `shareId` | `string` | Share ID if the issue is shared. |
| `shortId` | `string` | Short human-readable identifier. |
| `stats` | `object` | Issue event statistics. |
| `status` | `string` | Issue status (resolved, unresolved, ignored). |
| `statusDetails` | `object` | Status detail information. |
| `subscriptionDetails` | `object` | Subscription details. |
| `substatus` | `string` | Issue substatus. |
| `title` | `string` | Issue title. |
| `type` | `string` | Issue type. |
| `userCount` | `integer` | Number of users affected. |

<details>
<summary><b>Response Schema</b></summary>

| Field Name | Type | Description |
|------------|------|-------------|
| `data` | `array` | List of matching records |
| `meta` | `object` | Pagination metadata |
| `meta.has_more` | `boolean` | Whether additional pages are available |
| `meta.cursor` | `string \| null` | Cursor for next page of results |
| `meta.took_ms` | `number \| null` | Query execution time in milliseconds |
| `data[].annotations` | `array` | Annotations on the issue. |
| `data[].assignedTo` | `object` | User or team assigned to this issue. |
| `data[].count` | `string` | Number of events for this issue. |
| `data[].culprit` | `string` | The culprit (source) of the issue. |
| `data[].firstSeen` | `string` | When the issue was first seen. |
| `data[].hasSeen` | `boolean` | Whether the authenticated user has seen the issue. |
| `data[].id` | `string` | Unique issue identifier. |
| `data[].isBookmarked` | `boolean` | Whether the issue is bookmarked. |
| `data[].isPublic` | `boolean` | Whether the issue is public. |
| `data[].isSubscribed` | `boolean` | Whether the user is subscribed to the issue. |
| `data[].isUnhandled` | `boolean` | Whether the issue is from an unhandled error. |
| `data[].issueCategory` | `string` | The category classification of the issue. |
| `data[].issueType` | `string` | The type classification of the issue. |
| `data[].lastSeen` | `string` | When the issue was last seen. |
| `data[].level` | `string` | Issue severity level. |
| `data[].logger` | `string` | Logger that generated the issue. |
| `data[].metadata` | `object` | Issue metadata. |
| `data[].numComments` | `integer` | Number of comments on the issue. |
| `data[].permalink` | `string` | Permalink to the issue in the Sentry UI. |
| `data[].platform` | `string` | Platform for this issue. |
| `data[].project` | `object` | Project this issue belongs to. |
| `data[].shareId` | `string` | Share ID if the issue is shared. |
| `data[].shortId` | `string` | Short human-readable identifier. |
| `data[].stats` | `object` | Issue event statistics. |
| `data[].status` | `string` | Issue status (resolved, unresolved, ignored). |
| `data[].statusDetails` | `object` | Status detail information. |
| `data[].subscriptionDetails` | `object` | Subscription details. |
| `data[].substatus` | `string` | Issue substatus. |
| `data[].title` | `string` | Issue title. |
| `data[].type` | `string` | Issue type. |
| `data[].userCount` | `integer` | Number of users affected. |

</details>

## Events

### Events List

Return a list of events bound to a project.

#### Python SDK

```python
await sentry.events.list(
    organization_slug="<str>",
    project_slug="<str>"
)
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/integrations/connectors/{your_connector_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "events",
    "action": "list",
    "params": {
        "organization_slug": "<str>",
        "project_slug": "<str>"
    }
}'
```


#### Parameters

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `organization_slug` | `string` | Yes | The slug of the organization the events belong to. |
| `project_slug` | `string` | Yes | The slug of the project the events belong to. |
| `full` | `string` | No | If set to true, the event payload will include the full event body. |
| `cursor` | `string` | No | Pagination cursor for next page of results. |


<details>
<summary><b>Response Schema</b></summary>

#### Records

| Field Name | Type | Description |
|------------|------|-------------|
| `id` | `string \| null` |  |
| `eventID` | `string \| null` |  |
| `groupID` | `string \| null` |  |
| `title` | `string \| null` |  |
| `message` | `string \| null` |  |
| `type` | `string \| null` |  |
| `platform` | `string \| null` |  |
| `dateCreated` | `string \| null` |  |
| `dateReceived` | `string \| null` |  |
| `culprit` | `string \| null` |  |
| `location` | `string \| null` |  |
| `crashFile` | `string \| null` |  |
| `projectID` | `string \| null` |  |
| `sdk` | `string \| null` |  |
| `dist` | `string \| null` |  |
| `size` | `integer \| null` |  |
| `event.type` | `string \| null` |  |
| `tags` | `array \| null` |  |
| `user` | `object \| null` |  |
| `metadata` | `object \| null` |  |
| `context` | `object \| null` |  |
| `contexts` | `object \| null` |  |
| `entries` | `array \| null` |  |
| `errors` | `array \| null` |  |
| `fingerprints` | `array \| null` |  |
| `packages` | `object \| null` |  |
| `groupingConfig` | `object \| null` |  |
| `_meta` | `object \| null` |  |


</details>

### Events Get

Return details on an individual event.

#### Python SDK

```python
await sentry.events.get(
    organization_slug="<str>",
    project_slug="<str>",
    event_id="<str>"
)
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/integrations/connectors/{your_connector_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "events",
    "action": "get",
    "params": {
        "organization_slug": "<str>",
        "project_slug": "<str>",
        "event_id": "<str>"
    }
}'
```


#### Parameters

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `organization_slug` | `string` | Yes | The slug of the organization the event belongs to. |
| `project_slug` | `string` | Yes | The slug of the project the event belongs to. |
| `event_id` | `string` | Yes | The ID of the event to retrieve (hexadecimal). |


<details>
<summary><b>Response Schema</b></summary>

#### Records

| Field Name | Type | Description |
|------------|------|-------------|
| `id` | `string \| null` |  |
| `eventID` | `string \| null` |  |
| `groupID` | `string \| null` |  |
| `title` | `string \| null` |  |
| `message` | `string \| null` |  |
| `type` | `string \| null` |  |
| `platform` | `string \| null` |  |
| `dateCreated` | `string \| null` |  |
| `dateReceived` | `string \| null` |  |
| `culprit` | `string \| null` |  |
| `location` | `string \| null` |  |
| `crashFile` | `string \| null` |  |
| `projectID` | `string \| null` |  |
| `sdk` | `string \| null` |  |
| `dist` | `string \| null` |  |
| `size` | `integer \| null` |  |
| `event.type` | `string \| null` |  |
| `tags` | `array \| null` |  |
| `user` | `object \| null` |  |
| `metadata` | `object \| null` |  |
| `context` | `object \| null` |  |
| `contexts` | `object \| null` |  |
| `entries` | `array \| null` |  |
| `errors` | `array \| null` |  |
| `fingerprints` | `array \| null` |  |
| `packages` | `object \| null` |  |
| `groupingConfig` | `object \| null` |  |
| `_meta` | `object \| null` |  |


</details>

### Events Search

Search and filter events records powered by Airbyte's data sync. This often provides additional fields and operators beyond what the API natively supports, making it easier to narrow down results before performing further operations. Only available in hosted mode.

#### Python SDK

```python
await sentry.events.search(
    query={"filter": {"eq": {"_meta": {}}}}
)
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/integrations/connectors/{your_connector_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "events",
    "action": "search",
    "params": {
        "query": {"filter": {"eq": {"_meta": {}}}}
    }
}'
```

#### Parameters

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `query` | `object` | Yes | Filter and sort conditions. Supports operators: eq, neq, gt, gte, lt, lte, in, like, fuzzy, keyword, not, and, or |
| `query.filter` | `object` | No | Filter conditions |
| `query.sort` | `array` | No | Sort conditions |
| `limit` | `integer` | No | Maximum results to return (default 1000) |
| `cursor` | `string` | No | Pagination cursor from previous response's `meta.cursor` |
| `fields` | `array` | No | Field paths to include in results |

#### Searchable Fields

| Field Name | Type | Description |
|------------|------|-------------|
| `_meta` | `object` | Meta information for data scrubbing. |
| `context` | `object` | Additional context data. |
| `contexts` | `object` | Structured context information. |
| `crashFile` | `string` | Crash file reference. |
| `culprit` | `string` | The culprit (source) of the event. |
| `dateCreated` | `string` | When the event was created. |
| `dateReceived` | `string` | When the event was received by Sentry. |
| `dist` | `string` | Distribution information. |
| `entries` | `array` | Event entries (exception, breadcrumbs, request, etc.). |
| `errors` | `array` | Processing errors. |
| `event.type` | `string` | The type of the event. |
| `eventID` | `string` | Event ID as reported by the client. |
| `fingerprints` | `array` | Fingerprints used for grouping. |
| `groupID` | `string` | ID of the issue group this event belongs to. |
| `groupingConfig` | `object` | Grouping configuration. |
| `id` | `string` | Unique event identifier. |
| `location` | `string` | Location in source code. |
| `message` | `string` | Event message. |
| `metadata` | `object` | Event metadata. |
| `occurrence` | `string` | Occurrence information for the event. |
| `packages` | `object` | Package information. |
| `platform` | `string` | Platform the event was generated on. |
| `projectID` | `string` | Project ID this event belongs to. |
| `sdk` | `string` | SDK information. |
| `size` | `integer` | Event payload size in bytes. |
| `tags` | `array` | Tags associated with the event. |
| `title` | `string` | Event title. |
| `type` | `string` | Event type. |
| `user` | `object` | User associated with the event. |

<details>
<summary><b>Response Schema</b></summary>

| Field Name | Type | Description |
|------------|------|-------------|
| `data` | `array` | List of matching records |
| `meta` | `object` | Pagination metadata |
| `meta.has_more` | `boolean` | Whether additional pages are available |
| `meta.cursor` | `string \| null` | Cursor for next page of results |
| `meta.took_ms` | `number \| null` | Query execution time in milliseconds |
| `data[]._meta` | `object` | Meta information for data scrubbing. |
| `data[].context` | `object` | Additional context data. |
| `data[].contexts` | `object` | Structured context information. |
| `data[].crashFile` | `string` | Crash file reference. |
| `data[].culprit` | `string` | The culprit (source) of the event. |
| `data[].dateCreated` | `string` | When the event was created. |
| `data[].dateReceived` | `string` | When the event was received by Sentry. |
| `data[].dist` | `string` | Distribution information. |
| `data[].entries` | `array` | Event entries (exception, breadcrumbs, request, etc.). |
| `data[].errors` | `array` | Processing errors. |
| `data[].event.type` | `string` | The type of the event. |
| `data[].eventID` | `string` | Event ID as reported by the client. |
| `data[].fingerprints` | `array` | Fingerprints used for grouping. |
| `data[].groupID` | `string` | ID of the issue group this event belongs to. |
| `data[].groupingConfig` | `object` | Grouping configuration. |
| `data[].id` | `string` | Unique event identifier. |
| `data[].location` | `string` | Location in source code. |
| `data[].message` | `string` | Event message. |
| `data[].metadata` | `object` | Event metadata. |
| `data[].occurrence` | `string` | Occurrence information for the event. |
| `data[].packages` | `object` | Package information. |
| `data[].platform` | `string` | Platform the event was generated on. |
| `data[].projectID` | `string` | Project ID this event belongs to. |
| `data[].sdk` | `string` | SDK information. |
| `data[].size` | `integer` | Event payload size in bytes. |
| `data[].tags` | `array` | Tags associated with the event. |
| `data[].title` | `string` | Event title. |
| `data[].type` | `string` | Event type. |
| `data[].user` | `object` | User associated with the event. |

</details>

## Releases

### Releases List

Return a list of releases for a given organization.

#### Python SDK

```python
await sentry.releases.list(
    organization_slug="<str>"
)
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/integrations/connectors/{your_connector_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "releases",
    "action": "list",
    "params": {
        "organization_slug": "<str>"
    }
}'
```


#### Parameters

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `organization_slug` | `string` | Yes | The slug of the organization. |
| `query` | `string` | No | This parameter can be used to create a "starts with" filter for the version. |
| `cursor` | `string` | No | Pagination cursor for next page of results. |


<details>
<summary><b>Response Schema</b></summary>

#### Records

| Field Name | Type | Description |
|------------|------|-------------|
| `id` | `integer \| null` |  |
| `version` | `string \| null` |  |
| `shortVersion` | `string \| null` |  |
| `ref` | `string \| null` |  |
| `url` | `string \| null` |  |
| `status` | `string \| null` |  |
| `dateCreated` | `string \| null` |  |
| `dateReleased` | `string \| null` |  |
| `owner` | `string \| null` |  |
| `newGroups` | `integer \| null` |  |
| `commitCount` | `integer \| null` |  |
| `deployCount` | `integer \| null` |  |
| `firstEvent` | `string \| null` |  |
| `lastEvent` | `string \| null` |  |
| `lastCommit` | `object \| null` |  |
| `lastDeploy` | `object \| null` |  |
| `data` | `object \| null` |  |
| `userAgent` | `string \| null` |  |
| `authors` | `array \| null` |  |
| `projects` | `array \| null` |  |
| `versionInfo` | `object \| null` |  |
| `currentProjectMeta` | `object \| null` |  |


</details>

### Releases Get

Return a release for a given organization.

#### Python SDK

```python
await sentry.releases.get(
    organization_slug="<str>",
    version="<str>"
)
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/integrations/connectors/{your_connector_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "releases",
    "action": "get",
    "params": {
        "organization_slug": "<str>",
        "version": "<str>"
    }
}'
```


#### Parameters

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `organization_slug` | `string` | Yes | The slug of the organization. |
| `version` | `string` | Yes | The version identifier of the release. |


<details>
<summary><b>Response Schema</b></summary>

#### Records

| Field Name | Type | Description |
|------------|------|-------------|
| `id` | `integer \| null` |  |
| `version` | `string \| null` |  |
| `shortVersion` | `string \| null` |  |
| `ref` | `string \| null` |  |
| `url` | `string \| null` |  |
| `status` | `string \| null` |  |
| `dateCreated` | `string \| null` |  |
| `dateReleased` | `string \| null` |  |
| `owner` | `string \| null` |  |
| `newGroups` | `integer \| null` |  |
| `commitCount` | `integer \| null` |  |
| `deployCount` | `integer \| null` |  |
| `firstEvent` | `string \| null` |  |
| `lastEvent` | `string \| null` |  |
| `lastCommit` | `object \| null` |  |
| `lastDeploy` | `object \| null` |  |
| `data` | `object \| null` |  |
| `userAgent` | `string \| null` |  |
| `authors` | `array \| null` |  |
| `projects` | `array \| null` |  |
| `versionInfo` | `object \| null` |  |
| `currentProjectMeta` | `object \| null` |  |


</details>

### Releases Search

Search and filter releases records powered by Airbyte's data sync. This often provides additional fields and operators beyond what the API natively supports, making it easier to narrow down results before performing further operations. Only available in hosted mode.

#### Python SDK

```python
await sentry.releases.search(
    query={"filter": {"eq": {"authors": []}}}
)
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/integrations/connectors/{your_connector_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "releases",
    "action": "search",
    "params": {
        "query": {"filter": {"eq": {"authors": []}}}
    }
}'
```

#### Parameters

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `query` | `object` | Yes | Filter and sort conditions. Supports operators: eq, neq, gt, gte, lt, lte, in, like, fuzzy, keyword, not, and, or |
| `query.filter` | `object` | No | Filter conditions |
| `query.sort` | `array` | No | Sort conditions |
| `limit` | `integer` | No | Maximum results to return (default 1000) |
| `cursor` | `string` | No | Pagination cursor from previous response's `meta.cursor` |
| `fields` | `array` | No | Field paths to include in results |

#### Searchable Fields

| Field Name | Type | Description |
|------------|------|-------------|
| `authors` | `array` | Authors of commits in this release. |
| `commitCount` | `integer` | Number of commits in this release. |
| `currentProjectMeta` | `object` | Metadata for the current project context. |
| `data` | `object` | Additional release data. |
| `dateCreated` | `string` | When the release was created. |
| `dateReleased` | `string` | When the release was deployed. |
| `deployCount` | `integer` | Number of deploys for this release. |
| `firstEvent` | `string` | Timestamp of the first event in this release. |
| `id` | `integer` | Unique release identifier. |
| `lastCommit` | `object` | Last commit in this release. |
| `lastDeploy` | `object` | Last deploy of this release. |
| `lastEvent` | `string` | Timestamp of the last event in this release. |
| `newGroups` | `integer` | Number of new issue groups in this release. |
| `owner` | `string` | Owner of the release. |
| `projects` | `array` | Projects associated with this release. |
| `ref` | `string` | Git reference (commit SHA, tag, etc.). |
| `shortVersion` | `string` | Short version string. |
| `status` | `string` | Release status. |
| `url` | `string` | URL associated with the release. |
| `userAgent` | `string` | User agent that created the release. |
| `version` | `string` | Release version string. |
| `versionInfo` | `object` | Parsed version information. |

<details>
<summary><b>Response Schema</b></summary>

| Field Name | Type | Description |
|------------|------|-------------|
| `data` | `array` | List of matching records |
| `meta` | `object` | Pagination metadata |
| `meta.has_more` | `boolean` | Whether additional pages are available |
| `meta.cursor` | `string \| null` | Cursor for next page of results |
| `meta.took_ms` | `number \| null` | Query execution time in milliseconds |
| `data[].authors` | `array` | Authors of commits in this release. |
| `data[].commitCount` | `integer` | Number of commits in this release. |
| `data[].currentProjectMeta` | `object` | Metadata for the current project context. |
| `data[].data` | `object` | Additional release data. |
| `data[].dateCreated` | `string` | When the release was created. |
| `data[].dateReleased` | `string` | When the release was deployed. |
| `data[].deployCount` | `integer` | Number of deploys for this release. |
| `data[].firstEvent` | `string` | Timestamp of the first event in this release. |
| `data[].id` | `integer` | Unique release identifier. |
| `data[].lastCommit` | `object` | Last commit in this release. |
| `data[].lastDeploy` | `object` | Last deploy of this release. |
| `data[].lastEvent` | `string` | Timestamp of the last event in this release. |
| `data[].newGroups` | `integer` | Number of new issue groups in this release. |
| `data[].owner` | `string` | Owner of the release. |
| `data[].projects` | `array` | Projects associated with this release. |
| `data[].ref` | `string` | Git reference (commit SHA, tag, etc.). |
| `data[].shortVersion` | `string` | Short version string. |
| `data[].status` | `string` | Release status. |
| `data[].url` | `string` | URL associated with the release. |
| `data[].userAgent` | `string` | User agent that created the release. |
| `data[].version` | `string` | Release version string. |
| `data[].versionInfo` | `object` | Parsed version information. |

</details>

## Project Detail

### Project Detail Get

Return detailed information about a specific project.

#### Python SDK

```python
await sentry.project_detail.get(
    organization_slug="<str>",
    project_slug="<str>"
)
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/integrations/connectors/{your_connector_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "project_detail",
    "action": "get",
    "params": {
        "organization_slug": "<str>",
        "project_slug": "<str>"
    }
}'
```


#### Parameters

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `organization_slug` | `string` | Yes | The slug of the organization the project belongs to. |
| `project_slug` | `string` | Yes | The slug of the project. |


<details>
<summary><b>Response Schema</b></summary>

#### Records

| Field Name | Type | Description |
|------------|------|-------------|
| `id` | `string \| null` |  |
| `name` | `string \| null` |  |
| `slug` | `string \| null` |  |
| `status` | `string \| null` |  |
| `platform` | `string \| null` |  |
| `dateCreated` | `string \| null` |  |
| `isBookmarked` | `boolean \| null` |  |
| `isMember` | `boolean \| null` |  |
| `hasAccess` | `boolean \| null` |  |
| `isPublic` | `boolean \| null` |  |
| `isInternal` | `boolean \| null` |  |
| `color` | `string \| null` |  |
| `features` | `array \| null` |  |
| `firstEvent` | `string \| null` |  |
| `firstTransactionEvent` | `boolean \| null` |  |
| `access` | `array \| null` |  |
| `hasMinifiedStackTrace` | `boolean \| null` |  |
| `hasMonitors` | `boolean \| null` |  |
| `hasProfiles` | `boolean \| null` |  |
| `hasReplays` | `boolean \| null` |  |
| `hasFeedbacks` | `boolean \| null` |  |
| `hasFlags` | `boolean \| null` |  |
| `hasNewFeedbacks` | `boolean \| null` |  |
| `hasSessions` | `boolean \| null` |  |
| `hasInsightsHttp` | `boolean \| null` |  |
| `hasInsightsDb` | `boolean \| null` |  |
| `hasInsightsAssets` | `boolean \| null` |  |
| `hasInsightsAppStart` | `boolean \| null` |  |
| `hasInsightsScreenLoad` | `boolean \| null` |  |
| `hasInsightsVitals` | `boolean \| null` |  |
| `hasInsightsCaches` | `boolean \| null` |  |
| `hasInsightsQueues` | `boolean \| null` |  |
| `hasInsightsAgentMonitoring` | `boolean \| null` |  |
| `hasInsightsMCP` | `boolean \| null` |  |
| `hasLogs` | `boolean \| null` |  |
| `hasTraceMetrics` | `boolean \| null` |  |
| `team` | `object \| null` |  |
| `teams` | `array \| null` |  |
| `avatar` | `object \| null` |  |
| `organization` | `object \| null` |  |
| `latestRelease` | `object \| null` |  |
| `options` | `object \| null` |  |
| `digestsMinDelay` | `integer \| null` |  |
| `digestsMaxDelay` | `integer \| null` |  |
| `resolveAge` | `integer \| null` |  |
| `dataScrubber` | `boolean \| null` |  |
| `safeFields` | `array \| null` |  |
| `sensitiveFields` | `array \| null` |  |
| `verifySSL` | `boolean \| null` |  |
| `scrubIPAddresses` | `boolean \| null` |  |
| `scrapeJavaScript` | `boolean \| null` |  |
| `allowedDomains` | `array \| null` |  |
| `processingIssues` | `integer \| null` |  |
| `securityToken` | `string \| null` |  |
| `subjectPrefix` | `string \| null` |  |
| `dataScrubberDefaults` | `boolean \| null` |  |
| `storeCrashReports` | `boolean \| integer \| null` |  |
| `subjectTemplate` | `string \| null` |  |
| `securityTokenHeader` | `string \| null` |  |
| `groupingConfig` | `string \| null` |  |
| `groupingEnhancements` | `string \| null` |  |
| `derivedGroupingEnhancements` | `string \| null` |  |
| `secondaryGroupingExpiry` | `integer \| null` |  |
| `secondaryGroupingConfig` | `string \| null` |  |
| `fingerprintingRules` | `string \| null` |  |
| `plugins` | `array \| null` |  |
| `platforms` | `array \| null` |  |
| `defaultEnvironment` | `string \| null` |  |
| `relayPiiConfig` | `string \| null` |  |
| `builtinSymbolSources` | `array \| null` |  |
| `dynamicSamplingBiases` | `array \| null` |  |
| `symbolSources` | `string \| null` |  |
| `isDynamicallySampled` | `boolean \| null` |  |
| `autofixAutomationTuning` | `string \| null` |  |
| `seerScannerAutomation` | `boolean \| null` |  |
| `highlightTags` | `array \| null` |  |
| `highlightContext` | `object \| null` |  |
| `highlightPreset` | `object \| null` |  |
| `debugFilesRole` | `string \| null` |  |


</details>

