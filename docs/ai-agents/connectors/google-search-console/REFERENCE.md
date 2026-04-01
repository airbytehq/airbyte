# Google-Search-Console full reference

This is the full reference documentation for the Google-Search-Console agent connector.

## Supported entities and actions

The Google-Search-Console connector supports the following entities and actions.

| Entity | Actions |
|--------|---------|
| Sites | [List](#sites-list), [Get](#sites-get), [Search](#sites-search) |
| Sitemaps | [List](#sitemaps-list), [Get](#sitemaps-get), [Search](#sitemaps-search) |
| Search Analytics By Date | [List](#search-analytics-by-date-list), [Search](#search-analytics-by-date-search) |
| Search Analytics By Country | [List](#search-analytics-by-country-list), [Search](#search-analytics-by-country-search) |
| Search Analytics By Device | [List](#search-analytics-by-device-list), [Search](#search-analytics-by-device-search) |
| Search Analytics By Page | [List](#search-analytics-by-page-list), [Search](#search-analytics-by-page-search) |
| Search Analytics By Query | [List](#search-analytics-by-query-list), [Search](#search-analytics-by-query-search) |
| Search Analytics All Fields | [List](#search-analytics-all-fields-list), [Search](#search-analytics-all-fields-search) |

## Sites

### Sites List

Lists the user's Search Console sites.

#### Python SDK

```python
await google_search_console.sites.list()
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/integrations/connectors/{your_connector_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "sites",
    "action": "list"
}'
```



<details>
<summary><b>Response Schema</b></summary>

#### Records

| Field Name | Type | Description |
|------------|------|-------------|
| `siteUrl` | `null \| string` |  |
| `permissionLevel` | `null \| string` |  |


</details>

### Sites Get

Retrieves information about a specific site.

#### Python SDK

```python
await google_search_console.sites.get(
    site_url="<str>"
)
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/integrations/connectors/{your_connector_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "sites",
    "action": "get",
    "params": {
        "siteUrl": "<str>"
    }
}'
```


#### Parameters

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `siteUrl` | `string` | Yes | The URL of the property as defined in Search Console. Examples: http://www.example.com/ (for a URL-prefix property) or sc-domain:example.com (for a Domain property)
 |


<details>
<summary><b>Response Schema</b></summary>

#### Records

| Field Name | Type | Description |
|------------|------|-------------|
| `siteUrl` | `null \| string` |  |
| `permissionLevel` | `null \| string` |  |


</details>

### Sites Search

Search and filter sites records powered by Airbyte's data sync. This often provides additional fields and operators beyond what the API natively supports, making it easier to narrow down results before performing further operations. Only available in hosted mode.

#### Python SDK

```python
await google_search_console.sites.search(
    query={"filter": {"eq": {"permissionLevel": "<str>"}}}
)
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/integrations/connectors/{your_connector_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "sites",
    "action": "search",
    "params": {
        "query": {"filter": {"eq": {"permissionLevel": "<str>"}}}
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
| `permissionLevel` | `string` | The user's permission level for the site (owner, full, restricted, etc.) |
| `siteUrl` | `string` | The URL of the site data being fetched |

<details>
<summary><b>Response Schema</b></summary>

| Field Name | Type | Description |
|------------|------|-------------|
| `data` | `array` | List of matching records |
| `meta` | `object` | Pagination metadata |
| `meta.has_more` | `boolean` | Whether additional pages are available |
| `meta.cursor` | `string \| null` | Cursor for next page of results |
| `meta.took_ms` | `number \| null` | Query execution time in milliseconds |
| `data[].permissionLevel` | `string` | The user's permission level for the site (owner, full, restricted, etc.) |
| `data[].siteUrl` | `string` | The URL of the site data being fetched |

</details>

## Sitemaps

### Sitemaps List

Lists the sitemaps submitted for a site.

#### Python SDK

```python
await google_search_console.sitemaps.list(
    site_url="<str>"
)
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/integrations/connectors/{your_connector_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "sitemaps",
    "action": "list",
    "params": {
        "siteUrl": "<str>"
    }
}'
```


#### Parameters

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `siteUrl` | `string` | Yes | The URL of the property as defined in Search Console.
 |


<details>
<summary><b>Response Schema</b></summary>

#### Records

| Field Name | Type | Description |
|------------|------|-------------|
| `path` | `null \| string` |  |
| `lastSubmitted` | `null \| string` |  |
| `isPending` | `null \| boolean` |  |
| `isSitemapsIndex` | `null \| boolean` |  |
| `type` | `null \| string` |  |
| `lastDownloaded` | `null \| string` |  |
| `warnings` | `null \| string` |  |
| `errors` | `null \| string` |  |
| `contents` | `null \| array` |  |
| `contents[].type` | `null \| string` |  |
| `contents[].submitted` | `null \| string` |  |
| `contents[].indexed` | `null \| string` |  |


</details>

### Sitemaps Get

Retrieves information about a specific sitemap.

#### Python SDK

```python
await google_search_console.sitemaps.get(
    site_url="<str>",
    feedpath="<str>"
)
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/integrations/connectors/{your_connector_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "sitemaps",
    "action": "get",
    "params": {
        "siteUrl": "<str>",
        "feedpath": "<str>"
    }
}'
```


#### Parameters

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `siteUrl` | `string` | Yes | The URL of the property as defined in Search Console.
 |
| `feedpath` | `string` | Yes | The URL of the sitemap. |


<details>
<summary><b>Response Schema</b></summary>

#### Records

| Field Name | Type | Description |
|------------|------|-------------|
| `path` | `null \| string` |  |
| `lastSubmitted` | `null \| string` |  |
| `isPending` | `null \| boolean` |  |
| `isSitemapsIndex` | `null \| boolean` |  |
| `type` | `null \| string` |  |
| `lastDownloaded` | `null \| string` |  |
| `warnings` | `null \| string` |  |
| `errors` | `null \| string` |  |
| `contents` | `null \| array` |  |
| `contents[].type` | `null \| string` |  |
| `contents[].submitted` | `null \| string` |  |
| `contents[].indexed` | `null \| string` |  |


</details>

### Sitemaps Search

Search and filter sitemaps records powered by Airbyte's data sync. This often provides additional fields and operators beyond what the API natively supports, making it easier to narrow down results before performing further operations. Only available in hosted mode.

#### Python SDK

```python
await google_search_console.sitemaps.search(
    query={"filter": {"eq": {"contents": []}}}
)
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/integrations/connectors/{your_connector_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "sitemaps",
    "action": "search",
    "params": {
        "query": {"filter": {"eq": {"contents": []}}}
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
| `contents` | `array` | Data related to the sitemap contents |
| `errors` | `string` | Errors encountered while processing the sitemaps |
| `isPending` | `boolean` | Flag indicating if the sitemap is pending for processing |
| `isSitemapsIndex` | `boolean` | Flag indicating if the data represents a sitemap index |
| `lastDownloaded` | `string` | Timestamp when the sitemap was last downloaded |
| `lastSubmitted` | `string` | Timestamp when the sitemap was last submitted |
| `path` | `string` | Path to the sitemap file |
| `type` | `string` | Type of the sitemap |
| `warnings` | `string` | Warnings encountered while processing the sitemaps |

<details>
<summary><b>Response Schema</b></summary>

| Field Name | Type | Description |
|------------|------|-------------|
| `data` | `array` | List of matching records |
| `meta` | `object` | Pagination metadata |
| `meta.has_more` | `boolean` | Whether additional pages are available |
| `meta.cursor` | `string \| null` | Cursor for next page of results |
| `meta.took_ms` | `number \| null` | Query execution time in milliseconds |
| `data[].contents` | `array` | Data related to the sitemap contents |
| `data[].errors` | `string` | Errors encountered while processing the sitemaps |
| `data[].isPending` | `boolean` | Flag indicating if the sitemap is pending for processing |
| `data[].isSitemapsIndex` | `boolean` | Flag indicating if the data represents a sitemap index |
| `data[].lastDownloaded` | `string` | Timestamp when the sitemap was last downloaded |
| `data[].lastSubmitted` | `string` | Timestamp when the sitemap was last submitted |
| `data[].path` | `string` | Path to the sitemap file |
| `data[].type` | `string` | Type of the sitemap |
| `data[].warnings` | `string` | Warnings encountered while processing the sitemaps |

</details>

## Search Analytics By Date

### Search Analytics By Date List

Query search analytics data grouped by date. Returns clicks, impressions, CTR, and average position for each date in the specified range.


#### Python SDK

```python
await google_search_console.search_analytics_by_date.list(
    start_date="<str>",
    end_date="<str>",
    site_url="<str>"
)
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/integrations/connectors/{your_connector_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "search_analytics_by_date",
    "action": "list",
    "params": {
        "startDate": "<str>",
        "endDate": "<str>",
        "siteUrl": "<str>"
    }
}'
```


#### Parameters

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `startDate` | `string` | Yes | Start date of the requested date range, in YYYY-MM-DD format. |
| `endDate` | `string` | Yes | End date of the requested date range, in YYYY-MM-DD format. |
| `dimensions` | `array<string>` | No | Dimensions to group results by. |
| `rowLimit` | `integer` | No | The maximum number of rows to return. |
| `startRow` | `integer` | No | Zero-based index of the first row in the response. |
| `type` | `string` | No | Filter results by type: web, discover, googleNews, news, image, video.
 |
| `aggregationType` | `string` | No | How data is aggregated: auto, byPage, byProperty, byNewsShowcasePanel.
 |
| `dataState` | `string` | No | Data freshness: final (stable data only) or all (includes fresh data).
 |
| `siteUrl` | `string` | Yes | The URL of the property as defined in Search Console. |


<details>
<summary><b>Response Schema</b></summary>

#### Records

| Field Name | Type | Description |
|------------|------|-------------|
| `keys` | `null \| array` |  |
| `clicks` | `null \| number` |  |
| `impressions` | `null \| number` |  |
| `ctr` | `null \| number` |  |
| `position` | `null \| number` |  |


</details>

### Search Analytics By Date Search

Search and filter search analytics by date records powered by Airbyte's data sync. This often provides additional fields and operators beyond what the API natively supports, making it easier to narrow down results before performing further operations. Only available in hosted mode.

#### Python SDK

```python
await google_search_console.search_analytics_by_date.search(
    query={"filter": {"eq": {"clicks": 0}}}
)
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/integrations/connectors/{your_connector_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "search_analytics_by_date",
    "action": "search",
    "params": {
        "query": {"filter": {"eq": {"clicks": 0}}}
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
| `clicks` | `integer` | The total number of clicks on the specific date |
| `ctr` | `number` | The click-through rate for the specific date |
| `date` | `string` | The date for which the search analytics data is being reported |
| `impressions` | `integer` | The number of impressions on the specific date |
| `position` | `number` | The average position in search results for the specific date |
| `search_type` | `string` | The type of search query that generated the data |
| `site_url` | `string` | The URL of the site for which the search analytics data is being reported |

<details>
<summary><b>Response Schema</b></summary>

| Field Name | Type | Description |
|------------|------|-------------|
| `data` | `array` | List of matching records |
| `meta` | `object` | Pagination metadata |
| `meta.has_more` | `boolean` | Whether additional pages are available |
| `meta.cursor` | `string \| null` | Cursor for next page of results |
| `meta.took_ms` | `number \| null` | Query execution time in milliseconds |
| `data[].clicks` | `integer` | The total number of clicks on the specific date |
| `data[].ctr` | `number` | The click-through rate for the specific date |
| `data[].date` | `string` | The date for which the search analytics data is being reported |
| `data[].impressions` | `integer` | The number of impressions on the specific date |
| `data[].position` | `number` | The average position in search results for the specific date |
| `data[].search_type` | `string` | The type of search query that generated the data |
| `data[].site_url` | `string` | The URL of the site for which the search analytics data is being reported |

</details>

## Search Analytics By Country

### Search Analytics By Country List

Query search analytics data grouped by date and country. Returns clicks, impressions, CTR, and average position for each country.


#### Python SDK

```python
await google_search_console.search_analytics_by_country.list(
    start_date="<str>",
    end_date="<str>",
    site_url="<str>"
)
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/integrations/connectors/{your_connector_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "search_analytics_by_country",
    "action": "list",
    "params": {
        "startDate": "<str>",
        "endDate": "<str>",
        "siteUrl": "<str>"
    }
}'
```


#### Parameters

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `startDate` | `string` | Yes | Start date of the requested date range, in YYYY-MM-DD format. |
| `endDate` | `string` | Yes | End date of the requested date range, in YYYY-MM-DD format. |
| `dimensions` | `array<string>` | No | Dimensions to group results by. |
| `rowLimit` | `integer` | No | The maximum number of rows to return. |
| `startRow` | `integer` | No | Zero-based index of the first row in the response. |
| `type` | `string` | No | Filter results by type: web, discover, googleNews, news, image, video.
 |
| `aggregationType` | `string` | No | How data is aggregated: auto, byPage, byProperty.
 |
| `dataState` | `string` | No | Data freshness: final (stable data only) or all (includes fresh data).
 |
| `siteUrl` | `string` | Yes | The URL of the property as defined in Search Console. |


<details>
<summary><b>Response Schema</b></summary>

#### Records

| Field Name | Type | Description |
|------------|------|-------------|
| `keys` | `null \| array` |  |
| `clicks` | `null \| number` |  |
| `impressions` | `null \| number` |  |
| `ctr` | `null \| number` |  |
| `position` | `null \| number` |  |


</details>

### Search Analytics By Country Search

Search and filter search analytics by country records powered by Airbyte's data sync. This often provides additional fields and operators beyond what the API natively supports, making it easier to narrow down results before performing further operations. Only available in hosted mode.

#### Python SDK

```python
await google_search_console.search_analytics_by_country.search(
    query={"filter": {"eq": {"clicks": 0}}}
)
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/integrations/connectors/{your_connector_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "search_analytics_by_country",
    "action": "search",
    "params": {
        "query": {"filter": {"eq": {"clicks": 0}}}
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
| `clicks` | `integer` | The number of times users clicked on the search result for a specific country |
| `country` | `string` | The country for which the search analytics data is being reported |
| `ctr` | `number` | The click-through rate for a specific country |
| `date` | `string` | The date for which the search analytics data is being reported |
| `impressions` | `integer` | The total number of times a search result was shown for a specific country |
| `position` | `number` | The average position at which the site's search result appeared for a specific country |
| `search_type` | `string` | The type of search for which the data is being reported |
| `site_url` | `string` | The URL of the site for which the search analytics data is being reported |

<details>
<summary><b>Response Schema</b></summary>

| Field Name | Type | Description |
|------------|------|-------------|
| `data` | `array` | List of matching records |
| `meta` | `object` | Pagination metadata |
| `meta.has_more` | `boolean` | Whether additional pages are available |
| `meta.cursor` | `string \| null` | Cursor for next page of results |
| `meta.took_ms` | `number \| null` | Query execution time in milliseconds |
| `data[].clicks` | `integer` | The number of times users clicked on the search result for a specific country |
| `data[].country` | `string` | The country for which the search analytics data is being reported |
| `data[].ctr` | `number` | The click-through rate for a specific country |
| `data[].date` | `string` | The date for which the search analytics data is being reported |
| `data[].impressions` | `integer` | The total number of times a search result was shown for a specific country |
| `data[].position` | `number` | The average position at which the site's search result appeared for a specific country |
| `data[].search_type` | `string` | The type of search for which the data is being reported |
| `data[].site_url` | `string` | The URL of the site for which the search analytics data is being reported |

</details>

## Search Analytics By Device

### Search Analytics By Device List

Query search analytics data grouped by date and device. Returns clicks, impressions, CTR, and average position for each device type.


#### Python SDK

```python
await google_search_console.search_analytics_by_device.list(
    start_date="<str>",
    end_date="<str>",
    site_url="<str>"
)
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/integrations/connectors/{your_connector_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "search_analytics_by_device",
    "action": "list",
    "params": {
        "startDate": "<str>",
        "endDate": "<str>",
        "siteUrl": "<str>"
    }
}'
```


#### Parameters

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `startDate` | `string` | Yes | Start date of the requested date range, in YYYY-MM-DD format. |
| `endDate` | `string` | Yes | End date of the requested date range, in YYYY-MM-DD format. |
| `dimensions` | `array<string>` | No | Dimensions to group results by. |
| `rowLimit` | `integer` | No | The maximum number of rows to return. |
| `startRow` | `integer` | No | Zero-based index of the first row in the response. |
| `type` | `string` | No | Filter results by type: web, discover, googleNews, news, image, video.
 |
| `aggregationType` | `string` | No | How data is aggregated: auto, byPage, byProperty.
 |
| `dataState` | `string` | No | Data freshness: final (stable data only) or all (includes fresh data).
 |
| `siteUrl` | `string` | Yes | The URL of the property as defined in Search Console. |


<details>
<summary><b>Response Schema</b></summary>

#### Records

| Field Name | Type | Description |
|------------|------|-------------|
| `keys` | `null \| array` |  |
| `clicks` | `null \| number` |  |
| `impressions` | `null \| number` |  |
| `ctr` | `null \| number` |  |
| `position` | `null \| number` |  |


</details>

### Search Analytics By Device Search

Search and filter search analytics by device records powered by Airbyte's data sync. This often provides additional fields and operators beyond what the API natively supports, making it easier to narrow down results before performing further operations. Only available in hosted mode.

#### Python SDK

```python
await google_search_console.search_analytics_by_device.search(
    query={"filter": {"eq": {"clicks": 0}}}
)
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/integrations/connectors/{your_connector_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "search_analytics_by_device",
    "action": "search",
    "params": {
        "query": {"filter": {"eq": {"clicks": 0}}}
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
| `clicks` | `integer` | The total number of clicks by device type |
| `ctr` | `number` | Click-through rate by device type |
| `date` | `string` | The date for which the search analytics data is provided |
| `device` | `string` | The type of device used by the user (e.g., desktop, mobile) |
| `impressions` | `integer` | The total number of impressions by device type |
| `position` | `number` | The average position in search results by device type |
| `search_type` | `string` | The type of search performed |
| `site_url` | `string` | The URL of the site for which search analytics data is being provided |

<details>
<summary><b>Response Schema</b></summary>

| Field Name | Type | Description |
|------------|------|-------------|
| `data` | `array` | List of matching records |
| `meta` | `object` | Pagination metadata |
| `meta.has_more` | `boolean` | Whether additional pages are available |
| `meta.cursor` | `string \| null` | Cursor for next page of results |
| `meta.took_ms` | `number \| null` | Query execution time in milliseconds |
| `data[].clicks` | `integer` | The total number of clicks by device type |
| `data[].ctr` | `number` | Click-through rate by device type |
| `data[].date` | `string` | The date for which the search analytics data is provided |
| `data[].device` | `string` | The type of device used by the user (e.g., desktop, mobile) |
| `data[].impressions` | `integer` | The total number of impressions by device type |
| `data[].position` | `number` | The average position in search results by device type |
| `data[].search_type` | `string` | The type of search performed |
| `data[].site_url` | `string` | The URL of the site for which search analytics data is being provided |

</details>

## Search Analytics By Page

### Search Analytics By Page List

Query search analytics data grouped by date and page. Returns clicks, impressions, CTR, and average position for each page URL.


#### Python SDK

```python
await google_search_console.search_analytics_by_page.list(
    start_date="<str>",
    end_date="<str>",
    site_url="<str>"
)
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/integrations/connectors/{your_connector_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "search_analytics_by_page",
    "action": "list",
    "params": {
        "startDate": "<str>",
        "endDate": "<str>",
        "siteUrl": "<str>"
    }
}'
```


#### Parameters

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `startDate` | `string` | Yes | Start date of the requested date range, in YYYY-MM-DD format. |
| `endDate` | `string` | Yes | End date of the requested date range, in YYYY-MM-DD format. |
| `dimensions` | `array<string>` | No | Dimensions to group results by. |
| `rowLimit` | `integer` | No | The maximum number of rows to return. |
| `startRow` | `integer` | No | Zero-based index of the first row in the response. |
| `type` | `string` | No | Filter results by type: web, discover, googleNews, news, image, video.
 |
| `aggregationType` | `string` | No | How data is aggregated: auto, byPage, byProperty.
 |
| `dataState` | `string` | No | Data freshness: final (stable data only) or all (includes fresh data).
 |
| `siteUrl` | `string` | Yes | The URL of the property as defined in Search Console. |


<details>
<summary><b>Response Schema</b></summary>

#### Records

| Field Name | Type | Description |
|------------|------|-------------|
| `keys` | `null \| array` |  |
| `clicks` | `null \| number` |  |
| `impressions` | `null \| number` |  |
| `ctr` | `null \| number` |  |
| `position` | `null \| number` |  |


</details>

### Search Analytics By Page Search

Search and filter search analytics by page records powered by Airbyte's data sync. This often provides additional fields and operators beyond what the API natively supports, making it easier to narrow down results before performing further operations. Only available in hosted mode.

#### Python SDK

```python
await google_search_console.search_analytics_by_page.search(
    query={"filter": {"eq": {"clicks": 0}}}
)
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/integrations/connectors/{your_connector_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "search_analytics_by_page",
    "action": "search",
    "params": {
        "query": {"filter": {"eq": {"clicks": 0}}}
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
| `clicks` | `integer` | The number of clicks for a specific page |
| `ctr` | `number` | Click-through rate for the page |
| `date` | `string` | The date for which the search analytics data is reported |
| `impressions` | `integer` | The number of impressions for the page |
| `page` | `string` | The URL of the specific page being analyzed |
| `position` | `number` | The average position at which the page appeared in search results |
| `search_type` | `string` | The type of search query that led to the page being displayed |
| `site_url` | `string` | The URL of the site for which the search analytics data is being reported |

<details>
<summary><b>Response Schema</b></summary>

| Field Name | Type | Description |
|------------|------|-------------|
| `data` | `array` | List of matching records |
| `meta` | `object` | Pagination metadata |
| `meta.has_more` | `boolean` | Whether additional pages are available |
| `meta.cursor` | `string \| null` | Cursor for next page of results |
| `meta.took_ms` | `number \| null` | Query execution time in milliseconds |
| `data[].clicks` | `integer` | The number of clicks for a specific page |
| `data[].ctr` | `number` | Click-through rate for the page |
| `data[].date` | `string` | The date for which the search analytics data is reported |
| `data[].impressions` | `integer` | The number of impressions for the page |
| `data[].page` | `string` | The URL of the specific page being analyzed |
| `data[].position` | `number` | The average position at which the page appeared in search results |
| `data[].search_type` | `string` | The type of search query that led to the page being displayed |
| `data[].site_url` | `string` | The URL of the site for which the search analytics data is being reported |

</details>

## Search Analytics By Query

### Search Analytics By Query List

Query search analytics data grouped by date and query. Returns clicks, impressions, CTR, and average position for each search query.


#### Python SDK

```python
await google_search_console.search_analytics_by_query.list(
    start_date="<str>",
    end_date="<str>",
    site_url="<str>"
)
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/integrations/connectors/{your_connector_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "search_analytics_by_query",
    "action": "list",
    "params": {
        "startDate": "<str>",
        "endDate": "<str>",
        "siteUrl": "<str>"
    }
}'
```


#### Parameters

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `startDate` | `string` | Yes | Start date of the requested date range, in YYYY-MM-DD format. |
| `endDate` | `string` | Yes | End date of the requested date range, in YYYY-MM-DD format. |
| `dimensions` | `array<string>` | No | Dimensions to group results by. |
| `rowLimit` | `integer` | No | The maximum number of rows to return. |
| `startRow` | `integer` | No | Zero-based index of the first row in the response. |
| `type` | `string` | No | Filter results by type: web, discover, googleNews, news, image, video.
 |
| `aggregationType` | `string` | No | How data is aggregated: auto, byPage, byProperty.
 |
| `dataState` | `string` | No | Data freshness: final (stable data only) or all (includes fresh data).
 |
| `siteUrl` | `string` | Yes | The URL of the property as defined in Search Console. |


<details>
<summary><b>Response Schema</b></summary>

#### Records

| Field Name | Type | Description |
|------------|------|-------------|
| `keys` | `null \| array` |  |
| `clicks` | `null \| number` |  |
| `impressions` | `null \| number` |  |
| `ctr` | `null \| number` |  |
| `position` | `null \| number` |  |


</details>

### Search Analytics By Query Search

Search and filter search analytics by query records powered by Airbyte's data sync. This often provides additional fields and operators beyond what the API natively supports, making it easier to narrow down results before performing further operations. Only available in hosted mode.

#### Python SDK

```python
await google_search_console.search_analytics_by_query.search(
    query={"filter": {"eq": {"clicks": 0}}}
)
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/integrations/connectors/{your_connector_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "search_analytics_by_query",
    "action": "search",
    "params": {
        "query": {"filter": {"eq": {"clicks": 0}}}
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
| `clicks` | `integer` | The number of clicks for the specific query |
| `ctr` | `number` | The click-through rate for the specific query |
| `date` | `string` | The date for which the search analytics data is recorded |
| `impressions` | `integer` | The number of impressions for the specific query |
| `position` | `number` | The average position for the specific query |
| `query` | `string` | The search query for which the data is recorded |
| `search_type` | `string` | The type of search result for the specific query |
| `site_url` | `string` | The URL of the site for which the search analytics data is captured |

<details>
<summary><b>Response Schema</b></summary>

| Field Name | Type | Description |
|------------|------|-------------|
| `data` | `array` | List of matching records |
| `meta` | `object` | Pagination metadata |
| `meta.has_more` | `boolean` | Whether additional pages are available |
| `meta.cursor` | `string \| null` | Cursor for next page of results |
| `meta.took_ms` | `number \| null` | Query execution time in milliseconds |
| `data[].clicks` | `integer` | The number of clicks for the specific query |
| `data[].ctr` | `number` | The click-through rate for the specific query |
| `data[].date` | `string` | The date for which the search analytics data is recorded |
| `data[].impressions` | `integer` | The number of impressions for the specific query |
| `data[].position` | `number` | The average position for the specific query |
| `data[].query` | `string` | The search query for which the data is recorded |
| `data[].search_type` | `string` | The type of search result for the specific query |
| `data[].site_url` | `string` | The URL of the site for which the search analytics data is captured |

</details>

## Search Analytics All Fields

### Search Analytics All Fields List

Query search analytics data grouped by all dimensions (date, country, device, page, query). Returns the most granular breakdown of search data.


#### Python SDK

```python
await google_search_console.search_analytics_all_fields.list(
    start_date="<str>",
    end_date="<str>",
    site_url="<str>"
)
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/integrations/connectors/{your_connector_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "search_analytics_all_fields",
    "action": "list",
    "params": {
        "startDate": "<str>",
        "endDate": "<str>",
        "siteUrl": "<str>"
    }
}'
```


#### Parameters

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `startDate` | `string` | Yes | Start date of the requested date range, in YYYY-MM-DD format. |
| `endDate` | `string` | Yes | End date of the requested date range, in YYYY-MM-DD format. |
| `dimensions` | `array<string>` | No | Dimensions to group results by. |
| `rowLimit` | `integer` | No | The maximum number of rows to return. |
| `startRow` | `integer` | No | Zero-based index of the first row in the response. |
| `type` | `string` | No | Filter results by type: web, discover, googleNews, news, image, video.
 |
| `aggregationType` | `string` | No | How data is aggregated: auto, byPage, byProperty.
 |
| `dataState` | `string` | No | Data freshness: final (stable data only) or all (includes fresh data).
 |
| `siteUrl` | `string` | Yes | The URL of the property as defined in Search Console. |


<details>
<summary><b>Response Schema</b></summary>

#### Records

| Field Name | Type | Description |
|------------|------|-------------|
| `keys` | `null \| array` |  |
| `clicks` | `null \| number` |  |
| `impressions` | `null \| number` |  |
| `ctr` | `null \| number` |  |
| `position` | `null \| number` |  |


</details>

### Search Analytics All Fields Search

Search and filter search analytics all fields records powered by Airbyte's data sync. This often provides additional fields and operators beyond what the API natively supports, making it easier to narrow down results before performing further operations. Only available in hosted mode.

#### Python SDK

```python
await google_search_console.search_analytics_all_fields.search(
    query={"filter": {"eq": {"clicks": 0}}}
)
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/integrations/connectors/{your_connector_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "search_analytics_all_fields",
    "action": "search",
    "params": {
        "query": {"filter": {"eq": {"clicks": 0}}}
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
| `clicks` | `integer` | The number of times users clicked on the search result for a specific query |
| `country` | `string` | The country from which the search query originated |
| `ctr` | `number` | Click-through rate, calculated as clicks divided by impressions |
| `date` | `string` | The date when the search query occurred |
| `device` | `string` | The type of device used by the user (e.g., desktop, mobile) |
| `impressions` | `integer` | The number of times a search result appeared in response to a query |
| `page` | `string` | The page URL that appeared in the search results |
| `position` | `number` | The average position of the search result on the search engine results page |
| `query` | `string` | The search query entered by the user |
| `search_type` | `string` | The type of search (e.g., web, image, video) that triggered the search result |
| `site_url` | `string` | The URL of the site from which the data originates |

<details>
<summary><b>Response Schema</b></summary>

| Field Name | Type | Description |
|------------|------|-------------|
| `data` | `array` | List of matching records |
| `meta` | `object` | Pagination metadata |
| `meta.has_more` | `boolean` | Whether additional pages are available |
| `meta.cursor` | `string \| null` | Cursor for next page of results |
| `meta.took_ms` | `number \| null` | Query execution time in milliseconds |
| `data[].clicks` | `integer` | The number of times users clicked on the search result for a specific query |
| `data[].country` | `string` | The country from which the search query originated |
| `data[].ctr` | `number` | Click-through rate, calculated as clicks divided by impressions |
| `data[].date` | `string` | The date when the search query occurred |
| `data[].device` | `string` | The type of device used by the user (e.g., desktop, mobile) |
| `data[].impressions` | `integer` | The number of times a search result appeared in response to a query |
| `data[].page` | `string` | The page URL that appeared in the search results |
| `data[].position` | `number` | The average position of the search result on the search engine results page |
| `data[].query` | `string` | The search query entered by the user |
| `data[].search_type` | `string` | The type of search (e.g., web, image, video) that triggered the search result |
| `data[].site_url` | `string` | The URL of the site from which the data originates |

</details>

