# Google-Analytics-Data-Api full reference

This is the full reference documentation for the Google-Analytics-Data-Api agent connector.

## Supported entities and actions

The Google-Analytics-Data-Api connector supports the following entities and actions.

| Entity | Actions |
|--------|---------|
| Website Overview | [List](#website-overview-list), [Search](#website-overview-search) |
| Daily Active Users | [List](#daily-active-users-list), [Search](#daily-active-users-search) |
| Weekly Active Users | [List](#weekly-active-users-list), [Search](#weekly-active-users-search) |
| Four Weekly Active Users | [List](#four-weekly-active-users-list), [Search](#four-weekly-active-users-search) |
| Traffic Sources | [List](#traffic-sources-list), [Search](#traffic-sources-search) |
| Pages | [List](#pages-list), [Search](#pages-search) |
| Devices | [List](#devices-list), [Search](#devices-search) |
| Locations | [List](#locations-list), [Search](#locations-search) |

## Website Overview

### Website Overview List

Returns website overview metrics including total users, new users, sessions, bounce rate, page views, and average session duration by date.

#### Python SDK

```python
await google_analytics_data_api.website_overview.list(
    property_id="<str>"
)
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/integrations/connectors/{your_connector_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "website_overview",
    "action": "list",
    "params": {
        "property_id": "<str>"
    }
}'
```


#### Parameters

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `dateRanges` | `array<object>` | No |  |
| `dateRanges.startDate` | `string` | No | Start date in YYYY-MM-DD format or relative (e.g., 30daysAgo) |
| `dateRanges.endDate` | `string` | No | End date in YYYY-MM-DD format or relative (e.g., today) |
| `dimensions` | `array<object>` | No |  |
| `dimensions.name` | `string` | No |  |
| `metrics` | `array<object>` | No |  |
| `metrics.name` | `string` | No |  |
| `keepEmptyRows` | `boolean` | No |  |
| `returnPropertyQuota` | `boolean` | No |  |
| `limit` | `integer` | No |  |
| `property_id` | `string` | Yes | GA4 property ID |


<details>
<summary><b>Response Schema</b></summary>

#### Records

| Field Name | Type | Description |
|------------|------|-------------|
| `dimensionValues` | `array<object>` |  |
| `dimensionValues[].value` | `string` |  |
| `metricValues` | `array<object>` |  |
| `metricValues[].value` | `string` |  |


</details>

### Website Overview Search

Search and filter website overview records powered by Airbyte's data sync. This often provides additional fields and operators beyond what the API natively supports, making it easier to narrow down results before performing further operations. Only available in hosted mode.

#### Python SDK

```python
await google_analytics_data_api.website_overview.search(
    query={"filter": {"eq": {"averageSessionDuration": 0.0}}}
)
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/integrations/connectors/{your_connector_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "website_overview",
    "action": "search",
    "params": {
        "query": {"filter": {"eq": {"averageSessionDuration": 0.0}}}
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
| `averageSessionDuration` | `number` | Average duration of sessions in seconds |
| `bounceRate` | `number` | Percentage of sessions that were single-page with no interaction |
| `date` | `string` | Date of the report row in YYYYMMDD format |
| `endDate` | `string` | End date of the reporting period |
| `newUsers` | `integer` | Number of first-time users |
| `property_id` | `string` | GA4 property ID |
| `screenPageViews` | `integer` | Total number of screen or page views |
| `screenPageViewsPerSession` | `number` | Average page views per session |
| `sessions` | `integer` | Total number of sessions |
| `sessionsPerUser` | `number` | Average number of sessions per user |
| `startDate` | `string` | Start date of the reporting period |
| `totalUsers` | `integer` | Total number of unique users |

<details>
<summary><b>Response Schema</b></summary>

| Field Name | Type | Description |
|------------|------|-------------|
| `data` | `array` | List of matching records |
| `meta` | `object` | Pagination metadata |
| `meta.has_more` | `boolean` | Whether additional pages are available |
| `meta.cursor` | `string \| null` | Cursor for next page of results |
| `meta.took_ms` | `number \| null` | Query execution time in milliseconds |
| `data[].averageSessionDuration` | `number` | Average duration of sessions in seconds |
| `data[].bounceRate` | `number` | Percentage of sessions that were single-page with no interaction |
| `data[].date` | `string` | Date of the report row in YYYYMMDD format |
| `data[].endDate` | `string` | End date of the reporting period |
| `data[].newUsers` | `integer` | Number of first-time users |
| `data[].property_id` | `string` | GA4 property ID |
| `data[].screenPageViews` | `integer` | Total number of screen or page views |
| `data[].screenPageViewsPerSession` | `number` | Average page views per session |
| `data[].sessions` | `integer` | Total number of sessions |
| `data[].sessionsPerUser` | `number` | Average number of sessions per user |
| `data[].startDate` | `string` | Start date of the reporting period |
| `data[].totalUsers` | `integer` | Total number of unique users |

</details>

## Daily Active Users

### Daily Active Users List

Returns daily active user counts (1-day active users) by date.

#### Python SDK

```python
await google_analytics_data_api.daily_active_users.list(
    property_id="<str>"
)
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/integrations/connectors/{your_connector_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "daily_active_users",
    "action": "list",
    "params": {
        "property_id": "<str>"
    }
}'
```


#### Parameters

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `dateRanges` | `array<object>` | No |  |
| `dateRanges.startDate` | `string` | No | Start date in YYYY-MM-DD format or relative (e.g., 30daysAgo) |
| `dateRanges.endDate` | `string` | No | End date in YYYY-MM-DD format or relative (e.g., today) |
| `dimensions` | `array<object>` | No |  |
| `dimensions.name` | `string` | No |  |
| `metrics` | `array<object>` | No |  |
| `metrics.name` | `string` | No |  |
| `keepEmptyRows` | `boolean` | No |  |
| `returnPropertyQuota` | `boolean` | No |  |
| `limit` | `integer` | No |  |
| `property_id` | `string` | Yes | GA4 property ID |


<details>
<summary><b>Response Schema</b></summary>

#### Records

| Field Name | Type | Description |
|------------|------|-------------|
| `dimensionValues` | `array<object>` |  |
| `dimensionValues[].value` | `string` |  |
| `metricValues` | `array<object>` |  |
| `metricValues[].value` | `string` |  |


</details>

### Daily Active Users Search

Search and filter daily active users records powered by Airbyte's data sync. This often provides additional fields and operators beyond what the API natively supports, making it easier to narrow down results before performing further operations. Only available in hosted mode.

#### Python SDK

```python
await google_analytics_data_api.daily_active_users.search(
    query={"filter": {"eq": {"active1DayUsers": 0}}}
)
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/integrations/connectors/{your_connector_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "daily_active_users",
    "action": "search",
    "params": {
        "query": {"filter": {"eq": {"active1DayUsers": 0}}}
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
| `active1DayUsers` | `integer` | Number of distinct users active in the last 1 day |
| `date` | `string` | Date of the report row in YYYYMMDD format |
| `endDate` | `string` | End date of the reporting period |
| `property_id` | `string` | GA4 property ID |
| `startDate` | `string` | Start date of the reporting period |

<details>
<summary><b>Response Schema</b></summary>

| Field Name | Type | Description |
|------------|------|-------------|
| `data` | `array` | List of matching records |
| `meta` | `object` | Pagination metadata |
| `meta.has_more` | `boolean` | Whether additional pages are available |
| `meta.cursor` | `string \| null` | Cursor for next page of results |
| `meta.took_ms` | `number \| null` | Query execution time in milliseconds |
| `data[].active1DayUsers` | `integer` | Number of distinct users active in the last 1 day |
| `data[].date` | `string` | Date of the report row in YYYYMMDD format |
| `data[].endDate` | `string` | End date of the reporting period |
| `data[].property_id` | `string` | GA4 property ID |
| `data[].startDate` | `string` | Start date of the reporting period |

</details>

## Weekly Active Users

### Weekly Active Users List

Returns weekly active user counts (7-day active users) by date.

#### Python SDK

```python
await google_analytics_data_api.weekly_active_users.list(
    property_id="<str>"
)
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/integrations/connectors/{your_connector_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "weekly_active_users",
    "action": "list",
    "params": {
        "property_id": "<str>"
    }
}'
```


#### Parameters

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `dateRanges` | `array<object>` | No |  |
| `dateRanges.startDate` | `string` | No | Start date in YYYY-MM-DD format or relative (e.g., 30daysAgo) |
| `dateRanges.endDate` | `string` | No | End date in YYYY-MM-DD format or relative (e.g., today) |
| `dimensions` | `array<object>` | No |  |
| `dimensions.name` | `string` | No |  |
| `metrics` | `array<object>` | No |  |
| `metrics.name` | `string` | No |  |
| `keepEmptyRows` | `boolean` | No |  |
| `returnPropertyQuota` | `boolean` | No |  |
| `limit` | `integer` | No |  |
| `property_id` | `string` | Yes | GA4 property ID |


<details>
<summary><b>Response Schema</b></summary>

#### Records

| Field Name | Type | Description |
|------------|------|-------------|
| `dimensionValues` | `array<object>` |  |
| `dimensionValues[].value` | `string` |  |
| `metricValues` | `array<object>` |  |
| `metricValues[].value` | `string` |  |


</details>

### Weekly Active Users Search

Search and filter weekly active users records powered by Airbyte's data sync. This often provides additional fields and operators beyond what the API natively supports, making it easier to narrow down results before performing further operations. Only available in hosted mode.

#### Python SDK

```python
await google_analytics_data_api.weekly_active_users.search(
    query={"filter": {"eq": {"active7DayUsers": 0}}}
)
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/integrations/connectors/{your_connector_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "weekly_active_users",
    "action": "search",
    "params": {
        "query": {"filter": {"eq": {"active7DayUsers": 0}}}
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
| `active7DayUsers` | `integer` | Number of distinct users active in the last 7 days |
| `date` | `string` | Date of the report row in YYYYMMDD format |
| `endDate` | `string` | End date of the reporting period |
| `property_id` | `string` | GA4 property ID |
| `startDate` | `string` | Start date of the reporting period |

<details>
<summary><b>Response Schema</b></summary>

| Field Name | Type | Description |
|------------|------|-------------|
| `data` | `array` | List of matching records |
| `meta` | `object` | Pagination metadata |
| `meta.has_more` | `boolean` | Whether additional pages are available |
| `meta.cursor` | `string \| null` | Cursor for next page of results |
| `meta.took_ms` | `number \| null` | Query execution time in milliseconds |
| `data[].active7DayUsers` | `integer` | Number of distinct users active in the last 7 days |
| `data[].date` | `string` | Date of the report row in YYYYMMDD format |
| `data[].endDate` | `string` | End date of the reporting period |
| `data[].property_id` | `string` | GA4 property ID |
| `data[].startDate` | `string` | Start date of the reporting period |

</details>

## Four Weekly Active Users

### Four Weekly Active Users List

Returns 28-day active user counts by date.

#### Python SDK

```python
await google_analytics_data_api.four_weekly_active_users.list(
    property_id="<str>"
)
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/integrations/connectors/{your_connector_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "four_weekly_active_users",
    "action": "list",
    "params": {
        "property_id": "<str>"
    }
}'
```


#### Parameters

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `dateRanges` | `array<object>` | No |  |
| `dateRanges.startDate` | `string` | No | Start date in YYYY-MM-DD format or relative (e.g., 30daysAgo) |
| `dateRanges.endDate` | `string` | No | End date in YYYY-MM-DD format or relative (e.g., today) |
| `dimensions` | `array<object>` | No |  |
| `dimensions.name` | `string` | No |  |
| `metrics` | `array<object>` | No |  |
| `metrics.name` | `string` | No |  |
| `keepEmptyRows` | `boolean` | No |  |
| `returnPropertyQuota` | `boolean` | No |  |
| `limit` | `integer` | No |  |
| `property_id` | `string` | Yes | GA4 property ID |


<details>
<summary><b>Response Schema</b></summary>

#### Records

| Field Name | Type | Description |
|------------|------|-------------|
| `dimensionValues` | `array<object>` |  |
| `dimensionValues[].value` | `string` |  |
| `metricValues` | `array<object>` |  |
| `metricValues[].value` | `string` |  |


</details>

### Four Weekly Active Users Search

Search and filter four weekly active users records powered by Airbyte's data sync. This often provides additional fields and operators beyond what the API natively supports, making it easier to narrow down results before performing further operations. Only available in hosted mode.

#### Python SDK

```python
await google_analytics_data_api.four_weekly_active_users.search(
    query={"filter": {"eq": {"active28DayUsers": 0}}}
)
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/integrations/connectors/{your_connector_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "four_weekly_active_users",
    "action": "search",
    "params": {
        "query": {"filter": {"eq": {"active28DayUsers": 0}}}
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
| `active28DayUsers` | `integer` | Number of distinct users active in the last 28 days |
| `date` | `string` | Date of the report row in YYYYMMDD format |
| `endDate` | `string` | End date of the reporting period |
| `property_id` | `string` | GA4 property ID |
| `startDate` | `string` | Start date of the reporting period |

<details>
<summary><b>Response Schema</b></summary>

| Field Name | Type | Description |
|------------|------|-------------|
| `data` | `array` | List of matching records |
| `meta` | `object` | Pagination metadata |
| `meta.has_more` | `boolean` | Whether additional pages are available |
| `meta.cursor` | `string \| null` | Cursor for next page of results |
| `meta.took_ms` | `number \| null` | Query execution time in milliseconds |
| `data[].active28DayUsers` | `integer` | Number of distinct users active in the last 28 days |
| `data[].date` | `string` | Date of the report row in YYYYMMDD format |
| `data[].endDate` | `string` | End date of the reporting period |
| `data[].property_id` | `string` | GA4 property ID |
| `data[].startDate` | `string` | Start date of the reporting period |

</details>

## Traffic Sources

### Traffic Sources List

Returns traffic source metrics broken down by session source, session medium, and date, including users, sessions, bounce rate, and page views.

#### Python SDK

```python
await google_analytics_data_api.traffic_sources.list(
    property_id="<str>"
)
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/integrations/connectors/{your_connector_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "traffic_sources",
    "action": "list",
    "params": {
        "property_id": "<str>"
    }
}'
```


#### Parameters

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `dateRanges` | `array<object>` | No |  |
| `dateRanges.startDate` | `string` | No | Start date in YYYY-MM-DD format or relative (e.g., 30daysAgo) |
| `dateRanges.endDate` | `string` | No | End date in YYYY-MM-DD format or relative (e.g., today) |
| `dimensions` | `array<object>` | No |  |
| `dimensions.name` | `string` | No |  |
| `metrics` | `array<object>` | No |  |
| `metrics.name` | `string` | No |  |
| `keepEmptyRows` | `boolean` | No |  |
| `returnPropertyQuota` | `boolean` | No |  |
| `limit` | `integer` | No |  |
| `property_id` | `string` | Yes | GA4 property ID |


<details>
<summary><b>Response Schema</b></summary>

#### Records

| Field Name | Type | Description |
|------------|------|-------------|
| `dimensionValues` | `array<object>` |  |
| `dimensionValues[].value` | `string` |  |
| `metricValues` | `array<object>` |  |
| `metricValues[].value` | `string` |  |


</details>

### Traffic Sources Search

Search and filter traffic sources records powered by Airbyte's data sync. This often provides additional fields and operators beyond what the API natively supports, making it easier to narrow down results before performing further operations. Only available in hosted mode.

#### Python SDK

```python
await google_analytics_data_api.traffic_sources.search(
    query={"filter": {"eq": {"averageSessionDuration": 0.0}}}
)
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/integrations/connectors/{your_connector_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "traffic_sources",
    "action": "search",
    "params": {
        "query": {"filter": {"eq": {"averageSessionDuration": 0.0}}}
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
| `averageSessionDuration` | `number` | Average duration of sessions in seconds |
| `bounceRate` | `number` | Percentage of sessions that were single-page with no interaction |
| `date` | `string` | Date of the report row in YYYYMMDD format |
| `endDate` | `string` | End date of the reporting period |
| `newUsers` | `integer` | Number of first-time users |
| `property_id` | `string` | GA4 property ID |
| `screenPageViews` | `integer` | Total number of screen or page views |
| `screenPageViewsPerSession` | `number` | Average page views per session |
| `sessionMedium` | `string` | The medium of the traffic source (e.g., organic, cpc, referral) |
| `sessionSource` | `string` | The source of the traffic (e.g., google, direct) |
| `sessions` | `integer` | Total number of sessions |
| `sessionsPerUser` | `number` | Average number of sessions per user |
| `startDate` | `string` | Start date of the reporting period |
| `totalUsers` | `integer` | Total number of unique users |

<details>
<summary><b>Response Schema</b></summary>

| Field Name | Type | Description |
|------------|------|-------------|
| `data` | `array` | List of matching records |
| `meta` | `object` | Pagination metadata |
| `meta.has_more` | `boolean` | Whether additional pages are available |
| `meta.cursor` | `string \| null` | Cursor for next page of results |
| `meta.took_ms` | `number \| null` | Query execution time in milliseconds |
| `data[].averageSessionDuration` | `number` | Average duration of sessions in seconds |
| `data[].bounceRate` | `number` | Percentage of sessions that were single-page with no interaction |
| `data[].date` | `string` | Date of the report row in YYYYMMDD format |
| `data[].endDate` | `string` | End date of the reporting period |
| `data[].newUsers` | `integer` | Number of first-time users |
| `data[].property_id` | `string` | GA4 property ID |
| `data[].screenPageViews` | `integer` | Total number of screen or page views |
| `data[].screenPageViewsPerSession` | `number` | Average page views per session |
| `data[].sessionMedium` | `string` | The medium of the traffic source (e.g., organic, cpc, referral) |
| `data[].sessionSource` | `string` | The source of the traffic (e.g., google, direct) |
| `data[].sessions` | `integer` | Total number of sessions |
| `data[].sessionsPerUser` | `number` | Average number of sessions per user |
| `data[].startDate` | `string` | Start date of the reporting period |
| `data[].totalUsers` | `integer` | Total number of unique users |

</details>

## Pages

### Pages List

Returns page-level metrics including page views and bounce rate, broken down by host name, page path, and date.

#### Python SDK

```python
await google_analytics_data_api.pages.list(
    property_id="<str>"
)
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/integrations/connectors/{your_connector_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "pages",
    "action": "list",
    "params": {
        "property_id": "<str>"
    }
}'
```


#### Parameters

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `dateRanges` | `array<object>` | No |  |
| `dateRanges.startDate` | `string` | No | Start date in YYYY-MM-DD format or relative (e.g., 30daysAgo) |
| `dateRanges.endDate` | `string` | No | End date in YYYY-MM-DD format or relative (e.g., today) |
| `dimensions` | `array<object>` | No |  |
| `dimensions.name` | `string` | No |  |
| `metrics` | `array<object>` | No |  |
| `metrics.name` | `string` | No |  |
| `keepEmptyRows` | `boolean` | No |  |
| `returnPropertyQuota` | `boolean` | No |  |
| `limit` | `integer` | No |  |
| `property_id` | `string` | Yes | GA4 property ID |


<details>
<summary><b>Response Schema</b></summary>

#### Records

| Field Name | Type | Description |
|------------|------|-------------|
| `dimensionValues` | `array<object>` |  |
| `dimensionValues[].value` | `string` |  |
| `metricValues` | `array<object>` |  |
| `metricValues[].value` | `string` |  |


</details>

### Pages Search

Search and filter pages records powered by Airbyte's data sync. This often provides additional fields and operators beyond what the API natively supports, making it easier to narrow down results before performing further operations. Only available in hosted mode.

#### Python SDK

```python
await google_analytics_data_api.pages.search(
    query={"filter": {"eq": {"bounceRate": 0.0}}}
)
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/integrations/connectors/{your_connector_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "pages",
    "action": "search",
    "params": {
        "query": {"filter": {"eq": {"bounceRate": 0.0}}}
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
| `bounceRate` | `number` | Percentage of sessions that were single-page with no interaction |
| `date` | `string` | Date of the report row in YYYYMMDD format |
| `endDate` | `string` | End date of the reporting period |
| `hostName` | `string` | The hostname of the page |
| `pagePathPlusQueryString` | `string` | The page path and query string |
| `property_id` | `string` | GA4 property ID |
| `screenPageViews` | `integer` | Total number of screen or page views |
| `startDate` | `string` | Start date of the reporting period |

<details>
<summary><b>Response Schema</b></summary>

| Field Name | Type | Description |
|------------|------|-------------|
| `data` | `array` | List of matching records |
| `meta` | `object` | Pagination metadata |
| `meta.has_more` | `boolean` | Whether additional pages are available |
| `meta.cursor` | `string \| null` | Cursor for next page of results |
| `meta.took_ms` | `number \| null` | Query execution time in milliseconds |
| `data[].bounceRate` | `number` | Percentage of sessions that were single-page with no interaction |
| `data[].date` | `string` | Date of the report row in YYYYMMDD format |
| `data[].endDate` | `string` | End date of the reporting period |
| `data[].hostName` | `string` | The hostname of the page |
| `data[].pagePathPlusQueryString` | `string` | The page path and query string |
| `data[].property_id` | `string` | GA4 property ID |
| `data[].screenPageViews` | `integer` | Total number of screen or page views |
| `data[].startDate` | `string` | Start date of the reporting period |

</details>

## Devices

### Devices List

Returns device-related metrics broken down by device category, operating system, browser, and date, including users, sessions, and page views.

#### Python SDK

```python
await google_analytics_data_api.devices.list(
    property_id="<str>"
)
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/integrations/connectors/{your_connector_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "devices",
    "action": "list",
    "params": {
        "property_id": "<str>"
    }
}'
```


#### Parameters

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `dateRanges` | `array<object>` | No |  |
| `dateRanges.startDate` | `string` | No | Start date in YYYY-MM-DD format or relative (e.g., 30daysAgo) |
| `dateRanges.endDate` | `string` | No | End date in YYYY-MM-DD format or relative (e.g., today) |
| `dimensions` | `array<object>` | No |  |
| `dimensions.name` | `string` | No |  |
| `metrics` | `array<object>` | No |  |
| `metrics.name` | `string` | No |  |
| `keepEmptyRows` | `boolean` | No |  |
| `returnPropertyQuota` | `boolean` | No |  |
| `limit` | `integer` | No |  |
| `property_id` | `string` | Yes | GA4 property ID |


<details>
<summary><b>Response Schema</b></summary>

#### Records

| Field Name | Type | Description |
|------------|------|-------------|
| `dimensionValues` | `array<object>` |  |
| `dimensionValues[].value` | `string` |  |
| `metricValues` | `array<object>` |  |
| `metricValues[].value` | `string` |  |


</details>

### Devices Search

Search and filter devices records powered by Airbyte's data sync. This often provides additional fields and operators beyond what the API natively supports, making it easier to narrow down results before performing further operations. Only available in hosted mode.

#### Python SDK

```python
await google_analytics_data_api.devices.search(
    query={"filter": {"eq": {"averageSessionDuration": 0.0}}}
)
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/integrations/connectors/{your_connector_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "devices",
    "action": "search",
    "params": {
        "query": {"filter": {"eq": {"averageSessionDuration": 0.0}}}
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
| `averageSessionDuration` | `number` | Average duration of sessions in seconds |
| `bounceRate` | `number` | Percentage of sessions that were single-page with no interaction |
| `browser` | `string` | The web browser used (e.g., Chrome, Safari, Firefox) |
| `date` | `string` | Date of the report row in YYYYMMDD format |
| `deviceCategory` | `string` | The device category (desktop, mobile, tablet) |
| `endDate` | `string` | End date of the reporting period |
| `newUsers` | `integer` | Number of first-time users |
| `operatingSystem` | `string` | The operating system used (e.g., Windows, iOS, Android) |
| `property_id` | `string` | GA4 property ID |
| `screenPageViews` | `integer` | Total number of screen or page views |
| `screenPageViewsPerSession` | `number` | Average page views per session |
| `sessions` | `integer` | Total number of sessions |
| `sessionsPerUser` | `number` | Average number of sessions per user |
| `startDate` | `string` | Start date of the reporting period |
| `totalUsers` | `integer` | Total number of unique users |

<details>
<summary><b>Response Schema</b></summary>

| Field Name | Type | Description |
|------------|------|-------------|
| `data` | `array` | List of matching records |
| `meta` | `object` | Pagination metadata |
| `meta.has_more` | `boolean` | Whether additional pages are available |
| `meta.cursor` | `string \| null` | Cursor for next page of results |
| `meta.took_ms` | `number \| null` | Query execution time in milliseconds |
| `data[].averageSessionDuration` | `number` | Average duration of sessions in seconds |
| `data[].bounceRate` | `number` | Percentage of sessions that were single-page with no interaction |
| `data[].browser` | `string` | The web browser used (e.g., Chrome, Safari, Firefox) |
| `data[].date` | `string` | Date of the report row in YYYYMMDD format |
| `data[].deviceCategory` | `string` | The device category (desktop, mobile, tablet) |
| `data[].endDate` | `string` | End date of the reporting period |
| `data[].newUsers` | `integer` | Number of first-time users |
| `data[].operatingSystem` | `string` | The operating system used (e.g., Windows, iOS, Android) |
| `data[].property_id` | `string` | GA4 property ID |
| `data[].screenPageViews` | `integer` | Total number of screen or page views |
| `data[].screenPageViewsPerSession` | `number` | Average page views per session |
| `data[].sessions` | `integer` | Total number of sessions |
| `data[].sessionsPerUser` | `number` | Average number of sessions per user |
| `data[].startDate` | `string` | Start date of the reporting period |
| `data[].totalUsers` | `integer` | Total number of unique users |

</details>

## Locations

### Locations List

Returns geographic metrics broken down by region, country, city, and date, including users, sessions, bounce rate, and page views.

#### Python SDK

```python
await google_analytics_data_api.locations.list(
    property_id="<str>"
)
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/integrations/connectors/{your_connector_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "locations",
    "action": "list",
    "params": {
        "property_id": "<str>"
    }
}'
```


#### Parameters

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `dateRanges` | `array<object>` | No |  |
| `dateRanges.startDate` | `string` | No | Start date in YYYY-MM-DD format or relative (e.g., 30daysAgo) |
| `dateRanges.endDate` | `string` | No | End date in YYYY-MM-DD format or relative (e.g., today) |
| `dimensions` | `array<object>` | No |  |
| `dimensions.name` | `string` | No |  |
| `metrics` | `array<object>` | No |  |
| `metrics.name` | `string` | No |  |
| `keepEmptyRows` | `boolean` | No |  |
| `returnPropertyQuota` | `boolean` | No |  |
| `limit` | `integer` | No |  |
| `property_id` | `string` | Yes | GA4 property ID |


<details>
<summary><b>Response Schema</b></summary>

#### Records

| Field Name | Type | Description |
|------------|------|-------------|
| `dimensionValues` | `array<object>` |  |
| `dimensionValues[].value` | `string` |  |
| `metricValues` | `array<object>` |  |
| `metricValues[].value` | `string` |  |


</details>

### Locations Search

Search and filter locations records powered by Airbyte's data sync. This often provides additional fields and operators beyond what the API natively supports, making it easier to narrow down results before performing further operations. Only available in hosted mode.

#### Python SDK

```python
await google_analytics_data_api.locations.search(
    query={"filter": {"eq": {"averageSessionDuration": 0.0}}}
)
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/integrations/connectors/{your_connector_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "locations",
    "action": "search",
    "params": {
        "query": {"filter": {"eq": {"averageSessionDuration": 0.0}}}
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
| `averageSessionDuration` | `number` | Average duration of sessions in seconds |
| `bounceRate` | `number` | Percentage of sessions that were single-page with no interaction |
| `city` | `string` | The city of the user |
| `country` | `string` | The country of the user |
| `date` | `string` | Date of the report row in YYYYMMDD format |
| `endDate` | `string` | End date of the reporting period |
| `newUsers` | `integer` | Number of first-time users |
| `property_id` | `string` | GA4 property ID |
| `region` | `string` | The region (state/province) of the user |
| `screenPageViews` | `integer` | Total number of screen or page views |
| `screenPageViewsPerSession` | `number` | Average page views per session |
| `sessions` | `integer` | Total number of sessions |
| `sessionsPerUser` | `number` | Average number of sessions per user |
| `startDate` | `string` | Start date of the reporting period |
| `totalUsers` | `integer` | Total number of unique users |

<details>
<summary><b>Response Schema</b></summary>

| Field Name | Type | Description |
|------------|------|-------------|
| `data` | `array` | List of matching records |
| `meta` | `object` | Pagination metadata |
| `meta.has_more` | `boolean` | Whether additional pages are available |
| `meta.cursor` | `string \| null` | Cursor for next page of results |
| `meta.took_ms` | `number \| null` | Query execution time in milliseconds |
| `data[].averageSessionDuration` | `number` | Average duration of sessions in seconds |
| `data[].bounceRate` | `number` | Percentage of sessions that were single-page with no interaction |
| `data[].city` | `string` | The city of the user |
| `data[].country` | `string` | The country of the user |
| `data[].date` | `string` | Date of the report row in YYYYMMDD format |
| `data[].endDate` | `string` | End date of the reporting period |
| `data[].newUsers` | `integer` | Number of first-time users |
| `data[].property_id` | `string` | GA4 property ID |
| `data[].region` | `string` | The region (state/province) of the user |
| `data[].screenPageViews` | `integer` | Total number of screen or page views |
| `data[].screenPageViewsPerSession` | `number` | Average page views per session |
| `data[].sessions` | `integer` | Total number of sessions |
| `data[].sessionsPerUser` | `number` | Average number of sessions per user |
| `data[].startDate` | `string` | Start date of the reporting period |
| `data[].totalUsers` | `integer` | Total number of unique users |

</details>

