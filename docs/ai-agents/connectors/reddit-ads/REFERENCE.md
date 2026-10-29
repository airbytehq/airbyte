# Reddit-Ads full reference

This is the full reference documentation for the Reddit-Ads agent connector.

## Supported entities and actions

The Reddit-Ads connector supports the following entities and actions.

| Entity | Actions |
|--------|---------|
| Businesses | [List](#businesses-list) |
| Ad Accounts | [List](#ad-accounts-list), [Get](#ad-accounts-get) |
| Campaigns | [List](#campaigns-list), [Get](#campaigns-get), [Context Store Search](#campaigns-context-store-search), [Context Store SQL Query](#campaigns-context-store-sql-query) |
| Ad Groups | [List](#ad-groups-list), [Get](#ad-groups-get) |
| Ads | [List](#ads-list), [Get](#ads-get), [Context Store Search](#ads-context-store-search), [Context Store SQL Query](#ads-context-store-sql-query) |

## Businesses

### Businesses List

Retrieve all businesses associated with the authenticated user.

#### CLI

```bash
airbyte-agent connectors execute --json '{
  "workspace": "<your_workspace_name>",
  "name": "reddit-ads",
  "entity": "businesses",
  "action": "list"
}'
```

#### Python SDK

```python
await reddit_ads.businesses.list()
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/integrations/connectors/{your_connector_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "businesses",
    "action": "list"
}'
```


#### Parameters

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `page.size` | `integer` | No | Number of items per page (max 1000) |
| `page.token` | `string` | No | Pagination token for next page |


<details>
<summary><b>Response Schema</b></summary>

#### Records

| Field Name | Type | Description |
|------------|------|-------------|
| `id` | `string` |  |
| `name` | `string` |  |
| `country` | `string` |  |
| `primary_contact_id` | `string` |  |
| `creator_id` | `string` |  |
| `industry` | `string` |  |
| `website_url` | `null \| string` |  |
| `phone` | `null \| string` |  |
| `agency_affiliated` | `boolean` |  |
| `two_fa_enforcement` | `string` |  |
| `created_at` | `string` |  |
| `modified_at` | `string` |  |


#### Meta

| Field Name | Type | Description |
|------------|------|-------------|
| `next_link` | `null \| string` |  |

</details>

## Ad Accounts

### Ad Accounts List

Retrieve the ad accounts in a business.

#### CLI

```bash
airbyte-agent connectors execute --json '{
  "workspace": "<your_workspace_name>",
  "name": "reddit-ads",
  "entity": "ad_accounts",
  "action": "list",
  "params": {
    "business_id": "<str>"
  }
}'
```

#### Python SDK

```python
await reddit_ads.ad_accounts.list(
    business_id="<str>"
)
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/integrations/connectors/{your_connector_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "ad_accounts",
    "action": "list",
    "params": {
        "business_id": "<str>"
    }
}'
```


#### Parameters

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `business_id` | `string` | Yes | The business ID |
| `page.size` | `integer` | No | Number of items per page (max 1000) |
| `page.token` | `string` | No | Pagination token for next page |


<details>
<summary><b>Response Schema</b></summary>

#### Records

| Field Name | Type | Description |
|------------|------|-------------|
| `id` | `string` |  |
| `name` | `string` |  |
| `business_id` | `string` |  |
| `type` | `"MANAGED" \| "SELF_SERVE"` |  |
| `currency` | `string` |  |
| `time_zone_id` | `string` |  |
| `admin_approval` | `"ADMIN" \| "BANNED" \| "NEEDS_ID_VERIFICATION" \| "PENDING" \| "SUSPENDED" \| "SUSPICIOUS" \| "TRUSTED" \| "VALID"` |  |
| `attribution_type` | `string` |  |
| `click_attribution_window` | `"DAY" \| "MONTH" \| "WEEK"` |  |
| `view_attribution_window` | `"DAY" \| "MONTH" \| "WEEK"` |  |
| `app_attribution_type` | `string` |  |
| `app_click_attribution_window` | `string` |  |
| `app_view_attribution_window` | `string` |  |
| `primary_contact_member_id` | `string` |  |
| `suspension_reason` | `null \| string` |  |
| `created_at` | `string` |  |
| `modified_at` | `string` |  |
| `excluded_communities` | `array<string>` |  |
| `excluded_keywords` | `array<string>` |  |
| `pixel_partner_preferences` | `array<string>` |  |


#### Meta

| Field Name | Type | Description |
|------------|------|-------------|
| `next_link` | `null \| string` |  |

</details>

### Ad Accounts Get

Retrieve ad account by ID.

#### CLI

```bash
airbyte-agent connectors execute --json '{
  "workspace": "<your_workspace_name>",
  "name": "reddit-ads",
  "entity": "ad_accounts",
  "action": "get",
  "params": {
    "ad_account_id": "<str>"
  }
}'
```

#### Python SDK

```python
await reddit_ads.ad_accounts.get(
    ad_account_id="<str>"
)
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/integrations/connectors/{your_connector_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "ad_accounts",
    "action": "get",
    "params": {
        "ad_account_id": "<str>"
    }
}'
```


#### Parameters

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `ad_account_id` | `string` | Yes | The ad account ID |


<details>
<summary><b>Response Schema</b></summary>

#### Records

| Field Name | Type | Description |
|------------|------|-------------|
| `id` | `string` |  |
| `name` | `string` |  |
| `business_id` | `string` |  |
| `type` | `"MANAGED" \| "SELF_SERVE"` |  |
| `currency` | `string` |  |
| `time_zone_id` | `string` |  |
| `admin_approval` | `"ADMIN" \| "BANNED" \| "NEEDS_ID_VERIFICATION" \| "PENDING" \| "SUSPENDED" \| "SUSPICIOUS" \| "TRUSTED" \| "VALID"` |  |
| `attribution_type` | `string` |  |
| `click_attribution_window` | `"DAY" \| "MONTH" \| "WEEK"` |  |
| `view_attribution_window` | `"DAY" \| "MONTH" \| "WEEK"` |  |
| `app_attribution_type` | `string` |  |
| `app_click_attribution_window` | `string` |  |
| `app_view_attribution_window` | `string` |  |
| `primary_contact_member_id` | `string` |  |
| `suspension_reason` | `null \| string` |  |
| `created_at` | `string` |  |
| `modified_at` | `string` |  |
| `excluded_communities` | `array<string>` |  |
| `excluded_keywords` | `array<string>` |  |
| `pixel_partner_preferences` | `array<string>` |  |


</details>

## Campaigns

### Campaigns List

Retrieve campaigns by ad account.

#### CLI

```bash
airbyte-agent connectors execute --json '{
  "workspace": "<your_workspace_name>",
  "name": "reddit-ads",
  "entity": "campaigns",
  "action": "list",
  "params": {
    "ad_account_id": "<str>"
  }
}'
```

#### Python SDK

```python
await reddit_ads.campaigns.list(
    ad_account_id="<str>"
)
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/integrations/connectors/{your_connector_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "campaigns",
    "action": "list",
    "params": {
        "ad_account_id": "<str>"
    }
}'
```


#### Parameters

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `ad_account_id` | `string` | Yes | The ad account ID |
| `id` | `array<string>` | No | Filter by campaign IDs (comma-separated) |
| `page.size` | `integer` | No | Number of items per page (max 1000) |
| `page.token` | `string` | No | Pagination token for next page |


<details>
<summary><b>Response Schema</b></summary>

#### Records

| Field Name | Type | Description |
|------------|------|-------------|
| `id` | `string` |  |
| `name` | `string` |  |
| `ad_account_id` | `string` |  |
| `objective` | `"APP_INSTALLS" \| "CATALOG_SALES" \| "CLICKS" \| "CONVERSIONS" \| "IMPRESSIONS" \| "LEAD_GENERATION" \| "VIDEO_VIEWABLE_IMPRESSIONS"` |  |
| `configured_status` | `"ACTIVE" \| "ARCHIVED" \| "DELETED" \| "PAUSED"` |  |
| `effective_status` | `"ACTIVE" \| "AD_GROUP_PAUSED" \| "ARCHIVED" \| "CAMPAIGN_PAUSED" \| "COMPLETED" \| "DELETED" \| "PAUSED" \| "PENDING_APPROVAL" \| "PENDING_BILLING_INFO" \| "PENDING_ID_VERIFICATION" \| "REJECTED" \| "PROCESSING"` |  |
| `delivery_status` | `null \| array` |  |
| `funding_instrument_id` | `string` |  |
| `goal_type` | `"LIFETIME_SPEND" \| "DAILY_SPEND"` |  |
| `goal_value` | `integer` |  |
| `is_campaign_budget_optimization` | `boolean` |  |
| `spend_cap` | `null \| integer` |  |
| `start_time` | `null \| string` |  |
| `end_time` | `null \| string` |  |
| `optimization_goal` | `null \| string` |  |
| `bid_strategy` | `null \| string` |  |
| `bid_type` | `null \| string` |  |
| `bid_value` | `null \| integer` |  |
| `app_id` | `null \| string` |  |
| `view_through_conversion_type` | `null \| string` |  |
| `special_ad_categories` | `array<string>` |  |
| `schedule` | `array` |  |
| `skadnetwork_metadata` | `null \| object` |  |
| `age_restriction` | `null \| string` |  |
| `invoice_label` | `null \| string` |  |
| `conversion_pixel_id` | `null \| string` |  |
| `is_max` | `boolean` |  |
| `use_catalog` | `boolean` |  |
| `type` | `string` |  |
| `created_at` | `string` |  |
| `modified_at` | `string` |  |


#### Meta

| Field Name | Type | Description |
|------------|------|-------------|
| `next_link` | `null \| string` |  |

</details>

### Campaigns Get

Retrieve a campaign by ID.

#### CLI

```bash
airbyte-agent connectors execute --json '{
  "workspace": "<your_workspace_name>",
  "name": "reddit-ads",
  "entity": "campaigns",
  "action": "get",
  "params": {
    "campaign_id": "<str>"
  }
}'
```

#### Python SDK

```python
await reddit_ads.campaigns.get(
    campaign_id="<str>"
)
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/integrations/connectors/{your_connector_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "campaigns",
    "action": "get",
    "params": {
        "campaign_id": "<str>"
    }
}'
```


#### Parameters

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `campaign_id` | `string` | Yes | The campaign ID |


<details>
<summary><b>Response Schema</b></summary>

#### Records

| Field Name | Type | Description |
|------------|------|-------------|
| `id` | `string` |  |
| `name` | `string` |  |
| `ad_account_id` | `string` |  |
| `objective` | `"APP_INSTALLS" \| "CATALOG_SALES" \| "CLICKS" \| "CONVERSIONS" \| "IMPRESSIONS" \| "LEAD_GENERATION" \| "VIDEO_VIEWABLE_IMPRESSIONS"` |  |
| `configured_status` | `"ACTIVE" \| "ARCHIVED" \| "DELETED" \| "PAUSED"` |  |
| `effective_status` | `"ACTIVE" \| "AD_GROUP_PAUSED" \| "ARCHIVED" \| "CAMPAIGN_PAUSED" \| "COMPLETED" \| "DELETED" \| "PAUSED" \| "PENDING_APPROVAL" \| "PENDING_BILLING_INFO" \| "PENDING_ID_VERIFICATION" \| "REJECTED" \| "PROCESSING"` |  |
| `delivery_status` | `null \| array` |  |
| `funding_instrument_id` | `string` |  |
| `goal_type` | `"LIFETIME_SPEND" \| "DAILY_SPEND"` |  |
| `goal_value` | `integer` |  |
| `is_campaign_budget_optimization` | `boolean` |  |
| `spend_cap` | `null \| integer` |  |
| `start_time` | `null \| string` |  |
| `end_time` | `null \| string` |  |
| `optimization_goal` | `null \| string` |  |
| `bid_strategy` | `null \| string` |  |
| `bid_type` | `null \| string` |  |
| `bid_value` | `null \| integer` |  |
| `app_id` | `null \| string` |  |
| `view_through_conversion_type` | `null \| string` |  |
| `special_ad_categories` | `array<string>` |  |
| `schedule` | `array` |  |
| `skadnetwork_metadata` | `null \| object` |  |
| `age_restriction` | `null \| string` |  |
| `invoice_label` | `null \| string` |  |
| `conversion_pixel_id` | `null \| string` |  |
| `is_max` | `boolean` |  |
| `use_catalog` | `boolean` |  |
| `type` | `string` |  |
| `created_at` | `string` |  |
| `modified_at` | `string` |  |


</details>

### Campaigns Context Store Search

Search and filter campaigns records powered by Airbyte's data sync. This often provides additional fields and operators beyond what the API natively supports, making it easier to narrow down results before performing further operations. Only available in hosted mode.

#### CLI

```bash
airbyte-agent connectors execute --json '{
  "workspace": "<your_workspace_name>",
  "name": "reddit-ads",
  "entity": "campaigns",
  "action": "context_store_search",
  "params": {
    "query": {
      "filter": {
        "eq": {
          "ad_account_id": "<str>"
        }
      }
    }
  }
}'
```

#### Python SDK

```python
await reddit_ads.campaigns.context_store_search(
    query={"filter": {"eq": {"ad_account_id": "<str>"}}}
)
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/integrations/connectors/{your_connector_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "campaigns",
    "action": "context_store_search",
    "params": {
        "query": {"filter": {"eq": {"ad_account_id": "<str>"}}}
    }
}'
```

#### Parameters

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `query` | `object` | Yes | Filter and sort conditions. Supports operators: eq, neq, gt, gte, lt, lte, in, startswith, endswith, contains, array_contains, fuzzy, keyword, not, and, or |
| `query.filter` | `object` | No | Filter conditions |
| `query.sort` | `array` | No | Sort conditions |
| `limit` | `integer` | No | Maximum results to return (default 1000) |
| `cursor` | `string` | No | Pagination cursor from previous response's `meta.cursor` |
| `fields` | `array` | No | Field paths to include in results |

#### Searchable Fields

| Field Name | Type | Description |
|------------|------|-------------|
| `ad_account_id` | `string` | The ad account this campaign belongs to |
| `app_id` | `string` | App Store or Play Store ID |
| `configured_status` | `string` | User-configured status (ACTIVE, ARCHIVED, DELETED, PAUSED) |
| `created_at` | `string` | Creation timestamp in ISO 8601 format |
| `effective_status` | `string` | Effective delivery status |
| `funding_instrument_id` | `string` | Funding instrument ID |
| `goal_type` | `string` | Goal type (LIFETIME_SPEND, DAILY_SPEND) |
| `goal_value` | `integer` | Goal value in microcurrency |
| `id` | `string` | Unique campaign identifier |
| `is_campaign_budget_optimization` | `boolean` | Whether campaign budget optimization is enabled |
| `modified_at` | `string` | Last modification timestamp |
| `name` | `string` | Campaign name |
| `objective` | `string` | Campaign objective |
| `spend_cap` | `integer` | Spend cap in microcurrency |

<details>
<summary><b>Response Schema</b></summary>

| Field Name | Type | Description |
|------------|------|-------------|
| `data` | `array` | List of matching records |
| `meta` | `object` | Pagination metadata |
| `meta.has_more` | `boolean` | Whether additional pages are available |
| `meta.cursor` | `string \| null` | Cursor for next page of results |
| `meta.took_ms` | `number \| null` | Query execution time in milliseconds |
| `data[].ad_account_id` | `string` | The ad account this campaign belongs to |
| `data[].app_id` | `string` | App Store or Play Store ID |
| `data[].configured_status` | `string` | User-configured status (ACTIVE, ARCHIVED, DELETED, PAUSED) |
| `data[].created_at` | `string` | Creation timestamp in ISO 8601 format |
| `data[].effective_status` | `string` | Effective delivery status |
| `data[].funding_instrument_id` | `string` | Funding instrument ID |
| `data[].goal_type` | `string` | Goal type (LIFETIME_SPEND, DAILY_SPEND) |
| `data[].goal_value` | `integer` | Goal value in microcurrency |
| `data[].id` | `string` | Unique campaign identifier |
| `data[].is_campaign_budget_optimization` | `boolean` | Whether campaign budget optimization is enabled |
| `data[].modified_at` | `string` | Last modification timestamp |
| `data[].name` | `string` | Campaign name |
| `data[].objective` | `string` | Campaign objective |
| `data[].spend_cap` | `integer` | Spend cap in microcurrency |

</details>

### Campaigns Context Store SQL Query

Run a SQL query against campaigns records in the Airbyte Context Store. SQL projections may return any set of columns, so each result row is a dictionary matching the query's selected fields. Only available in hosted mode.

Use the hosted server documentation to find the qualified Context Store table name and SQL guidance.

#### CLI

```bash
airbyte-agent connectors execute --json '{
  "workspace": "<your_workspace_name>",
  "name": "reddit-ads",
  "entity": "campaigns",
  "action": "context_store_sql_query",
  "params": {
    "sql": "SELECT * FROM <qualified_context_store_table> LIMIT 100"
  }
}'
```

#### Python SDK

```python
await reddit_ads.campaigns.context_store_sql_query(
    sql="SELECT * FROM <qualified_context_store_table> LIMIT 100"
)
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/integrations/connectors/{your_connector_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "campaigns",
    "action": "context_store_sql_query",
    "params": {
        "sql": "SELECT * FROM <qualified_context_store_table> LIMIT 100"
    }
}'
```

#### Parameters

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `sql` | `string` | Yes | SQL query to execute against this entity's Context Store data |
| `limit` | `integer` | No | Maximum results to return |

<details>
<summary><b>Response Schema</b></summary>

| Field Name | Type | Description |
|------------|------|-------------|
| `data` | `array` | Projected rows, with dictionary keys matching the selected columns |
| `meta` | `object` | Query metadata |
| `meta.has_more` | `boolean` | Whether the result was limited and more rows are available |
| `meta.cursor` | `null` | SQL query results do not use cursor pagination |
| `meta.took_ms` | `number \| null` | Query execution time in milliseconds |

</details>

## Ad Groups

### Ad Groups List

Retrieve ad groups by ad account.

#### CLI

```bash
airbyte-agent connectors execute --json '{
  "workspace": "<your_workspace_name>",
  "name": "reddit-ads",
  "entity": "ad_groups",
  "action": "list",
  "params": {
    "ad_account_id": "<str>"
  }
}'
```

#### Python SDK

```python
await reddit_ads.ad_groups.list(
    ad_account_id="<str>"
)
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/integrations/connectors/{your_connector_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "ad_groups",
    "action": "list",
    "params": {
        "ad_account_id": "<str>"
    }
}'
```


#### Parameters

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `ad_account_id` | `string` | Yes | The ad account ID |
| `campaign_id` | `string` | No | Filter by campaign ID |
| `page.size` | `integer` | No | Number of items per page (max 1000) |
| `page.token` | `string` | No | Pagination token for next page |


<details>
<summary><b>Response Schema</b></summary>

#### Records

| Field Name | Type | Description |
|------------|------|-------------|
| `id` | `string` |  |
| `name` | `string` |  |
| `type` | `"MANUAL" \| "AUTOMATED"` |  |
| `ad_account_id` | `string` |  |
| `campaign_id` | `string` |  |
| `configured_status` | `"ACTIVE" \| "ARCHIVED" \| "DELETED" \| "PAUSED"` |  |
| `effective_status` | `"ACTIVE" \| "AD_GROUP_PAUSED" \| "ARCHIVED" \| "CAMPAIGN_PAUSED" \| "COMPLETED" \| "DELETED" \| "PAUSED" \| "PENDING_APPROVAL" \| "PENDING_BILLING_INFO" \| "PENDING_ID_VERIFICATION" \| "REJECTED" \| "PROCESSING"` |  |
| `delivery_status` | `null \| array` |  |
| `bid_strategy` | `null \| string` |  |
| `bid_type` | `null \| string` |  |
| `bid_value` | `null \| integer` |  |
| `optimization_goal` | `null \| string` |  |
| `campaign_objective_type` | `null \| string` |  |
| `goal_type` | `null \| string` |  |
| `goal_value` | `null \| integer` |  |
| `is_campaign_budget_optimization` | `null \| boolean` |  |
| `start_time` | `null \| string` |  |
| `end_time` | `null \| string` |  |
| `targeting` | `object` |  |
| `view_through_conversion_type` | `null \| string` |  |
| `conversion_pixel_id` | `null \| string` |  |
| `app_id` | `null \| string` |  |
| `optimization_strategy_type` | `null \| string` |  |
| `product_set_id` | `null \| string` |  |
| `saved_audience_id` | `null \| string` |  |
| `schedule` | `array` |  |
| `skadnetwork_metadata` | `null \| object` |  |
| `shopping_type` | `null \| string` |  |
| `created_at` | `string` |  |
| `modified_at` | `string` |  |


#### Meta

| Field Name | Type | Description |
|------------|------|-------------|
| `next_link` | `null \| string` |  |

</details>

### Ad Groups Get

Retrieve an ad group by ID.

#### CLI

```bash
airbyte-agent connectors execute --json '{
  "workspace": "<your_workspace_name>",
  "name": "reddit-ads",
  "entity": "ad_groups",
  "action": "get",
  "params": {
    "ad_group_id": "<str>"
  }
}'
```

#### Python SDK

```python
await reddit_ads.ad_groups.get(
    ad_group_id="<str>"
)
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/integrations/connectors/{your_connector_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "ad_groups",
    "action": "get",
    "params": {
        "ad_group_id": "<str>"
    }
}'
```


#### Parameters

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `ad_group_id` | `string` | Yes | The ad group ID |


<details>
<summary><b>Response Schema</b></summary>

#### Records

| Field Name | Type | Description |
|------------|------|-------------|
| `id` | `string` |  |
| `name` | `string` |  |
| `type` | `"MANUAL" \| "AUTOMATED"` |  |
| `ad_account_id` | `string` |  |
| `campaign_id` | `string` |  |
| `configured_status` | `"ACTIVE" \| "ARCHIVED" \| "DELETED" \| "PAUSED"` |  |
| `effective_status` | `"ACTIVE" \| "AD_GROUP_PAUSED" \| "ARCHIVED" \| "CAMPAIGN_PAUSED" \| "COMPLETED" \| "DELETED" \| "PAUSED" \| "PENDING_APPROVAL" \| "PENDING_BILLING_INFO" \| "PENDING_ID_VERIFICATION" \| "REJECTED" \| "PROCESSING"` |  |
| `delivery_status` | `null \| array` |  |
| `bid_strategy` | `null \| string` |  |
| `bid_type` | `null \| string` |  |
| `bid_value` | `null \| integer` |  |
| `optimization_goal` | `null \| string` |  |
| `campaign_objective_type` | `null \| string` |  |
| `goal_type` | `null \| string` |  |
| `goal_value` | `null \| integer` |  |
| `is_campaign_budget_optimization` | `null \| boolean` |  |
| `start_time` | `null \| string` |  |
| `end_time` | `null \| string` |  |
| `targeting` | `object` |  |
| `view_through_conversion_type` | `null \| string` |  |
| `conversion_pixel_id` | `null \| string` |  |
| `app_id` | `null \| string` |  |
| `optimization_strategy_type` | `null \| string` |  |
| `product_set_id` | `null \| string` |  |
| `saved_audience_id` | `null \| string` |  |
| `schedule` | `array` |  |
| `skadnetwork_metadata` | `null \| object` |  |
| `shopping_type` | `null \| string` |  |
| `created_at` | `string` |  |
| `modified_at` | `string` |  |


</details>

## Ads

### Ads List

Retrieve ads by ad account. Filters combine with logical AND across different query parameters.


#### CLI

```bash
airbyte-agent connectors execute --json '{
  "workspace": "<your_workspace_name>",
  "name": "reddit-ads",
  "entity": "ads",
  "action": "list",
  "params": {
    "ad_account_id": "<str>"
  }
}'
```

#### Python SDK

```python
await reddit_ads.ads.list(
    ad_account_id="<str>"
)
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/integrations/connectors/{your_connector_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "ads",
    "action": "list",
    "params": {
        "ad_account_id": "<str>"
    }
}'
```


#### Parameters

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `ad_account_id` | `string` | Yes | The ad account ID |
| `campaign_id` | `array<string>` | No | Filter by campaign IDs (comma-separated) |
| `ad_group_id` | `array<string>` | No | Filter by ad group IDs (comma-separated) |
| `configured_status` | `array<"ACTIVE" \| "ARCHIVED" \| "DELETED" \| "PAUSED">` | No | Filter by configured status |
| `effective_status` | `array<"ACTIVE" \| "AD_GROUP_PAUSED" \| "ARCHIVED" \| "CAMPAIGN_PAUSED" \| "COMPLETED" \| "DELETED" \| "MISSING_PERMISSIONS" \| "PAUSED" \| "PENDING_APPROVAL" \| "PENDING_BILLING_INFO" \| "PENDING_ID_VERIFICATION" \| "PROCESSING" \| "REJECTED">` | No | Filter by effective status |
| `page.size` | `integer` | No | Number of items per page (max 1000) |
| `page.token` | `string` | No | Pagination token for next page |


<details>
<summary><b>Response Schema</b></summary>

#### Records

| Field Name | Type | Description |
|------------|------|-------------|
| `id` | `string` |  |
| `name` | `string` |  |
| `type` | `"UNSPECIFIED" \| "DYNAMIC_CREATIVE_AD_TEMPLATE"` |  |
| `ad_account_id` | `string` |  |
| `ad_group_id` | `string` |  |
| `campaign_id` | `string` |  |
| `campaign_objective_type` | `null \| string` |  |
| `click_url` | `null \| string` |  |
| `click_url_query_parameters` | `array<object>` |  |
| `configured_status` | `"ACTIVE" \| "ARCHIVED" \| "DELETED" \| "PAUSED"` |  |
| `effective_status` | `"ACTIVE" \| "AD_GROUP_PAUSED" \| "ARCHIVED" \| "CAMPAIGN_PAUSED" \| "COMPLETED" \| "DELETED" \| "MISSING_PERMISSIONS" \| "PAUSED" \| "PENDING_APPROVAL" \| "PENDING_BILLING_INFO" \| "PENDING_ID_VERIFICATION" \| "PROCESSING" \| "REJECTED"` |  |
| `delivery_status` | `null \| array` |  |
| `event_trackers` | `array<object>` |  |
| `post_id` | `null \| string` |  |
| `post_url` | `null \| string` |  |
| `preview_url` | `null \| string` |  |
| `preview_expiry` | `null \| string` |  |
| `rejection_reason` | `null \| string` |  |
| `profile_id` | `null \| string` |  |
| `products` | `null \| array` |  |
| `shopping_creative` | `null \| object` |  |
| `skadnetwork_metadata` | `null \| object` |  |
| `extensions` | `null \| object` |  |
| `created_at` | `string` |  |
| `modified_at` | `string` |  |


#### Meta

| Field Name | Type | Description |
|------------|------|-------------|
| `next_link` | `null \| string` |  |

</details>

### Ads Get

Retrieve an ad by ID.

#### CLI

```bash
airbyte-agent connectors execute --json '{
  "workspace": "<your_workspace_name>",
  "name": "reddit-ads",
  "entity": "ads",
  "action": "get",
  "params": {
    "ad_id": "<str>"
  }
}'
```

#### Python SDK

```python
await reddit_ads.ads.get(
    ad_id="<str>"
)
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/integrations/connectors/{your_connector_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "ads",
    "action": "get",
    "params": {
        "ad_id": "<str>"
    }
}'
```


#### Parameters

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `ad_id` | `string` | Yes | The ad ID |


<details>
<summary><b>Response Schema</b></summary>

#### Records

| Field Name | Type | Description |
|------------|------|-------------|
| `id` | `string` |  |
| `name` | `string` |  |
| `type` | `"UNSPECIFIED" \| "DYNAMIC_CREATIVE_AD_TEMPLATE"` |  |
| `ad_account_id` | `string` |  |
| `ad_group_id` | `string` |  |
| `campaign_id` | `string` |  |
| `campaign_objective_type` | `null \| string` |  |
| `click_url` | `null \| string` |  |
| `click_url_query_parameters` | `array<object>` |  |
| `configured_status` | `"ACTIVE" \| "ARCHIVED" \| "DELETED" \| "PAUSED"` |  |
| `effective_status` | `"ACTIVE" \| "AD_GROUP_PAUSED" \| "ARCHIVED" \| "CAMPAIGN_PAUSED" \| "COMPLETED" \| "DELETED" \| "MISSING_PERMISSIONS" \| "PAUSED" \| "PENDING_APPROVAL" \| "PENDING_BILLING_INFO" \| "PENDING_ID_VERIFICATION" \| "PROCESSING" \| "REJECTED"` |  |
| `delivery_status` | `null \| array` |  |
| `event_trackers` | `array<object>` |  |
| `post_id` | `null \| string` |  |
| `post_url` | `null \| string` |  |
| `preview_url` | `null \| string` |  |
| `preview_expiry` | `null \| string` |  |
| `rejection_reason` | `null \| string` |  |
| `profile_id` | `null \| string` |  |
| `products` | `null \| array` |  |
| `shopping_creative` | `null \| object` |  |
| `skadnetwork_metadata` | `null \| object` |  |
| `extensions` | `null \| object` |  |
| `created_at` | `string` |  |
| `modified_at` | `string` |  |


</details>

### Ads Context Store Search

Search and filter ads records powered by Airbyte's data sync. This often provides additional fields and operators beyond what the API natively supports, making it easier to narrow down results before performing further operations. Only available in hosted mode.

#### CLI

```bash
airbyte-agent connectors execute --json '{
  "workspace": "<your_workspace_name>",
  "name": "reddit-ads",
  "entity": "ads",
  "action": "context_store_search",
  "params": {
    "query": {
      "filter": {
        "eq": {
          "ad_account_id": "<str>"
        }
      }
    }
  }
}'
```

#### Python SDK

```python
await reddit_ads.ads.context_store_search(
    query={"filter": {"eq": {"ad_account_id": "<str>"}}}
)
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/integrations/connectors/{your_connector_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "ads",
    "action": "context_store_search",
    "params": {
        "query": {"filter": {"eq": {"ad_account_id": "<str>"}}}
    }
}'
```

#### Parameters

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `query` | `object` | Yes | Filter and sort conditions. Supports operators: eq, neq, gt, gte, lt, lte, in, startswith, endswith, contains, array_contains, fuzzy, keyword, not, and, or |
| `query.filter` | `object` | No | Filter conditions |
| `query.sort` | `array` | No | Sort conditions |
| `limit` | `integer` | No | Maximum results to return (default 1000) |
| `cursor` | `string` | No | Pagination cursor from previous response's `meta.cursor` |
| `fields` | `array` | No | Field paths to include in results |

#### Searchable Fields

| Field Name | Type | Description |
|------------|------|-------------|
| `ad_account_id` | `string` | The ad account this ad belongs to |
| `ad_group_id` | `string` | The ad group this ad belongs to |
| `campaign_id` | `string` | The campaign this ad belongs to |
| `click_url` | `string` | Click destination URL |
| `configured_status` | `string` | User-configured status |
| `created_at` | `string` | Creation timestamp |
| `effective_status` | `string` | Effective delivery status |
| `id` | `string` | Unique ad identifier |
| `modified_at` | `string` | Last modification timestamp |
| `name` | `string` | Ad name |
| `post_id` | `string` | Reddit post ID (t3_ prefix) |
| `post_url` | `string` | Reddit post URL |
| `preview_url` | `string` | Ad preview URL |
| `rejection_reason` | `string` | Reason the ad was rejected |

<details>
<summary><b>Response Schema</b></summary>

| Field Name | Type | Description |
|------------|------|-------------|
| `data` | `array` | List of matching records |
| `meta` | `object` | Pagination metadata |
| `meta.has_more` | `boolean` | Whether additional pages are available |
| `meta.cursor` | `string \| null` | Cursor for next page of results |
| `meta.took_ms` | `number \| null` | Query execution time in milliseconds |
| `data[].ad_account_id` | `string` | The ad account this ad belongs to |
| `data[].ad_group_id` | `string` | The ad group this ad belongs to |
| `data[].campaign_id` | `string` | The campaign this ad belongs to |
| `data[].click_url` | `string` | Click destination URL |
| `data[].configured_status` | `string` | User-configured status |
| `data[].created_at` | `string` | Creation timestamp |
| `data[].effective_status` | `string` | Effective delivery status |
| `data[].id` | `string` | Unique ad identifier |
| `data[].modified_at` | `string` | Last modification timestamp |
| `data[].name` | `string` | Ad name |
| `data[].post_id` | `string` | Reddit post ID (t3_ prefix) |
| `data[].post_url` | `string` | Reddit post URL |
| `data[].preview_url` | `string` | Ad preview URL |
| `data[].rejection_reason` | `string` | Reason the ad was rejected |

</details>

### Ads Context Store SQL Query

Run a SQL query against ads records in the Airbyte Context Store. SQL projections may return any set of columns, so each result row is a dictionary matching the query's selected fields. Only available in hosted mode.

Use the hosted server documentation to find the qualified Context Store table name and SQL guidance.

#### CLI

```bash
airbyte-agent connectors execute --json '{
  "workspace": "<your_workspace_name>",
  "name": "reddit-ads",
  "entity": "ads",
  "action": "context_store_sql_query",
  "params": {
    "sql": "SELECT * FROM <qualified_context_store_table> LIMIT 100"
  }
}'
```

#### Python SDK

```python
await reddit_ads.ads.context_store_sql_query(
    sql="SELECT * FROM <qualified_context_store_table> LIMIT 100"
)
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/integrations/connectors/{your_connector_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "ads",
    "action": "context_store_sql_query",
    "params": {
        "sql": "SELECT * FROM <qualified_context_store_table> LIMIT 100"
    }
}'
```

#### Parameters

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `sql` | `string` | Yes | SQL query to execute against this entity's Context Store data |
| `limit` | `integer` | No | Maximum results to return |

<details>
<summary><b>Response Schema</b></summary>

| Field Name | Type | Description |
|------------|------|-------------|
| `data` | `array` | Projected rows, with dictionary keys matching the selected columns |
| `meta` | `object` | Query metadata |
| `meta.has_more` | `boolean` | Whether the result was limited and more rows are available |
| `meta.cursor` | `null` | SQL query results do not use cursor pagination |
| `meta.took_ms` | `number \| null` | Query execution time in milliseconds |

</details>

