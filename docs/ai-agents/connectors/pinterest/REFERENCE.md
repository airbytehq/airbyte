# Pinterest full reference

This is the full reference documentation for the Pinterest agent connector.

## Supported entities and actions

The Pinterest connector supports the following entities and actions.

| Entity | Actions |
|--------|---------|
| Ad Accounts | [List](#ad-accounts-list), [Get](#ad-accounts-get), [Search](#ad-accounts-search) |
| Boards | [List](#boards-list), [Get](#boards-get), [Search](#boards-search) |
| Campaigns | [List](#campaigns-list), [Search](#campaigns-search) |
| Ad Groups | [List](#ad-groups-list), [Search](#ad-groups-search) |
| Ads | [List](#ads-list), [Search](#ads-search) |
| Board Sections | [List](#board-sections-list), [Search](#board-sections-search) |
| Board Pins | [List](#board-pins-list), [Search](#board-pins-search) |
| Catalogs | [List](#catalogs-list), [Search](#catalogs-search) |
| Catalogs Feeds | [List](#catalogs-feeds-list), [Search](#catalogs-feeds-search) |
| Catalogs Product Groups | [List](#catalogs-product-groups-list), [Search](#catalogs-product-groups-search) |
| Audiences | [List](#audiences-list), [Search](#audiences-search) |
| Conversion Tags | [List](#conversion-tags-list), [Search](#conversion-tags-search) |
| Customer Lists | [List](#customer-lists-list), [Search](#customer-lists-search) |
| Keywords | [List](#keywords-list), [Search](#keywords-search) |

## Ad Accounts

### Ad Accounts List

Get a list of the ad accounts that the authenticated user has access to.

#### Python SDK

```python
await pinterest.ad_accounts.list()
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/integrations/connectors/{your_connector_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "ad_accounts",
    "action": "list"
}'
```


#### Parameters

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `page_size` | `integer` | No | Maximum number of items to include in a single page of the response. |
| `bookmark` | `string` | No | Cursor value for paginating through results. |
| `include_shared_accounts` | `boolean` | No | Include shared ad accounts. |


<details>
<summary><b>Response Schema</b></summary>

#### Records

| Field Name | Type | Description |
|------------|------|-------------|
| `id` | `null \| string` |  |
| `name` | `null \| string` |  |
| `owner` | `null \| object` |  |
| `country` | `null \| string` |  |
| `currency` | `null \| string` |  |
| `created_time` | `null \| integer` |  |
| `updated_time` | `null \| integer` |  |
| `permissions` | `null \| array` |  |


#### Meta

| Field Name | Type | Description |
|------------|------|-------------|
| `bookmark` | `null \| string` |  |

</details>

### Ad Accounts Get

Get an ad account by ID.

#### Python SDK

```python
await pinterest.ad_accounts.get(
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
| `ad_account_id` | `string` | Yes | Unique identifier of the ad account. |


<details>
<summary><b>Response Schema</b></summary>

#### Records

| Field Name | Type | Description |
|------------|------|-------------|
| `id` | `null \| string` |  |
| `name` | `null \| string` |  |
| `owner` | `null \| object` |  |
| `country` | `null \| string` |  |
| `currency` | `null \| string` |  |
| `created_time` | `null \| integer` |  |
| `updated_time` | `null \| integer` |  |
| `permissions` | `null \| array` |  |


</details>

### Ad Accounts Search

Search and filter ad accounts records powered by Airbyte's data sync. This often provides additional fields and operators beyond what the API natively supports, making it easier to narrow down results before performing further operations. Only available in hosted mode.

#### Python SDK

```python
await pinterest.ad_accounts.search(
    query={"filter": {"eq": {"country": "<str>"}}}
)
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/integrations/connectors/{your_connector_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "ad_accounts",
    "action": "search",
    "params": {
        "query": {"filter": {"eq": {"country": "<str>"}}}
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
| `country` | `string` | Country associated with the ad account |
| `created_time` | `integer` | Timestamp when the ad account was created (Unix seconds) |
| `currency` | `string` | Currency used for billing |
| `id` | `string` | Unique identifier for the ad account |
| `name` | `string` | Name of the ad account |
| `owner` | `object` | Owner details of the ad account |
| `permissions` | `array` | Permissions assigned to the ad account |
| `updated_time` | `integer` | Timestamp when the ad account was last updated (Unix seconds) |

<details>
<summary><b>Response Schema</b></summary>

| Field Name | Type | Description |
|------------|------|-------------|
| `data` | `array` | List of matching records |
| `meta` | `object` | Pagination metadata |
| `meta.has_more` | `boolean` | Whether additional pages are available |
| `meta.cursor` | `string \| null` | Cursor for next page of results |
| `meta.took_ms` | `number \| null` | Query execution time in milliseconds |
| `data[].country` | `string` | Country associated with the ad account |
| `data[].created_time` | `integer` | Timestamp when the ad account was created (Unix seconds) |
| `data[].currency` | `string` | Currency used for billing |
| `data[].id` | `string` | Unique identifier for the ad account |
| `data[].name` | `string` | Name of the ad account |
| `data[].owner` | `object` | Owner details of the ad account |
| `data[].permissions` | `array` | Permissions assigned to the ad account |
| `data[].updated_time` | `integer` | Timestamp when the ad account was last updated (Unix seconds) |

</details>

## Boards

### Boards List

Get a list of the boards owned by the authenticated user.

#### Python SDK

```python
await pinterest.boards.list()
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/integrations/connectors/{your_connector_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "boards",
    "action": "list"
}'
```


#### Parameters

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `page_size` | `integer` | No | Maximum number of items to include in a single page of the response. |
| `bookmark` | `string` | No | Cursor value for paginating through results. |
| `privacy` | `"PUBLIC" \| "PROTECTED" \| "SECRET"` | No | Filter by board privacy setting. |


<details>
<summary><b>Response Schema</b></summary>

#### Records

| Field Name | Type | Description |
|------------|------|-------------|
| `id` | `null \| string` |  |
| `name` | `null \| string` |  |
| `description` | `null \| string` |  |
| `owner` | `null \| object` |  |
| `is_ads_only` | `null \| boolean` |  |
| `privacy` | `null \| string` |  |
| `follower_count` | `null \| integer` |  |
| `collaborator_count` | `null \| integer` |  |
| `pin_count` | `null \| integer` |  |
| `media` | `null \| object` |  |
| `created_at` | `null \| string` |  |
| `board_pins_modified_at` | `null \| string` |  |


#### Meta

| Field Name | Type | Description |
|------------|------|-------------|
| `bookmark` | `null \| string` |  |

</details>

### Boards Get

Get a board by ID.

#### Python SDK

```python
await pinterest.boards.get(
    board_id="<str>"
)
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/integrations/connectors/{your_connector_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "boards",
    "action": "get",
    "params": {
        "board_id": "<str>"
    }
}'
```


#### Parameters

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `board_id` | `string` | Yes | Unique identifier of the board. |


<details>
<summary><b>Response Schema</b></summary>

#### Records

| Field Name | Type | Description |
|------------|------|-------------|
| `id` | `null \| string` |  |
| `name` | `null \| string` |  |
| `description` | `null \| string` |  |
| `owner` | `null \| object` |  |
| `is_ads_only` | `null \| boolean` |  |
| `privacy` | `null \| string` |  |
| `follower_count` | `null \| integer` |  |
| `collaborator_count` | `null \| integer` |  |
| `pin_count` | `null \| integer` |  |
| `media` | `null \| object` |  |
| `created_at` | `null \| string` |  |
| `board_pins_modified_at` | `null \| string` |  |


</details>

### Boards Search

Search and filter boards records powered by Airbyte's data sync. This often provides additional fields and operators beyond what the API natively supports, making it easier to narrow down results before performing further operations. Only available in hosted mode.

#### Python SDK

```python
await pinterest.boards.search(
    query={"filter": {"eq": {"board_pins_modified_at": "<str>"}}}
)
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/integrations/connectors/{your_connector_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "boards",
    "action": "search",
    "params": {
        "query": {"filter": {"eq": {"board_pins_modified_at": "<str>"}}}
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
| `board_pins_modified_at` | `string` | Timestamp when pins on the board were last modified |
| `collaborator_count` | `integer` | Number of collaborators |
| `created_at` | `string` | Timestamp when the board was created |
| `description` | `string` | Board description |
| `follower_count` | `integer` | Number of followers |
| `id` | `string` | Unique identifier for the board |
| `media` | `object` | Media content for the board |
| `name` | `string` | Board name |
| `owner` | `object` | Board owner details |
| `pin_count` | `integer` | Number of pins on the board |
| `privacy` | `string` | Board privacy setting |

<details>
<summary><b>Response Schema</b></summary>

| Field Name | Type | Description |
|------------|------|-------------|
| `data` | `array` | List of matching records |
| `meta` | `object` | Pagination metadata |
| `meta.has_more` | `boolean` | Whether additional pages are available |
| `meta.cursor` | `string \| null` | Cursor for next page of results |
| `meta.took_ms` | `number \| null` | Query execution time in milliseconds |
| `data[].board_pins_modified_at` | `string` | Timestamp when pins on the board were last modified |
| `data[].collaborator_count` | `integer` | Number of collaborators |
| `data[].created_at` | `string` | Timestamp when the board was created |
| `data[].description` | `string` | Board description |
| `data[].follower_count` | `integer` | Number of followers |
| `data[].id` | `string` | Unique identifier for the board |
| `data[].media` | `object` | Media content for the board |
| `data[].name` | `string` | Board name |
| `data[].owner` | `object` | Board owner details |
| `data[].pin_count` | `integer` | Number of pins on the board |
| `data[].privacy` | `string` | Board privacy setting |

</details>

## Campaigns

### Campaigns List

Get a list of campaigns in the specified ad account.

#### Python SDK

```python
await pinterest.campaigns.list(
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
| `ad_account_id` | `string` | Yes | Unique identifier of the ad account. |
| `page_size` | `integer` | No | Maximum number of items to include in a single page of the response. |
| `bookmark` | `string` | No | Cursor value for paginating through results. |
| `entity_statuses` | `array<"ACTIVE" \| "PAUSED" \| "ARCHIVED" \| "DRAFT" \| "DELETED_DRAFT">` | No | Filter by entity status. |
| `order` | `"ASCENDING" \| "DESCENDING"` | No | Sort order. |


<details>
<summary><b>Response Schema</b></summary>

#### Records

| Field Name | Type | Description |
|------------|------|-------------|
| `id` | `null \| string` |  |
| `ad_account_id` | `null \| string` |  |
| `name` | `null \| string` |  |
| `status` | `null \| string` |  |
| `lifetime_spend_cap` | `null \| integer` |  |
| `daily_spend_cap` | `null \| integer` |  |
| `order_line_id` | `null \| string` |  |
| `tracking_urls` | `null \| object` |  |
| `objective_type` | `null \| string` |  |
| `created_time` | `null \| integer` |  |
| `updated_time` | `null \| integer` |  |
| `type` | `null \| string` |  |
| `start_time` | `null \| integer` |  |
| `end_time` | `null \| integer` |  |
| `summary_status` | `null \| string` |  |
| `is_campaign_budget_optimization` | `null \| boolean` |  |
| `is_flexible_daily_budgets` | `null \| boolean` |  |
| `is_performance_plus` | `null \| boolean` |  |
| `is_top_of_search` | `null \| boolean` |  |
| `is_automated_campaign` | `null \| boolean` |  |
| `bid_options` | `null \| object` |  |


#### Meta

| Field Name | Type | Description |
|------------|------|-------------|
| `bookmark` | `null \| string` |  |

</details>

### Campaigns Search

Search and filter campaigns records powered by Airbyte's data sync. This often provides additional fields and operators beyond what the API natively supports, making it easier to narrow down results before performing further operations. Only available in hosted mode.

#### Python SDK

```python
await pinterest.campaigns.search(
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
    "action": "search",
    "params": {
        "query": {"filter": {"eq": {"ad_account_id": "<str>"}}}
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
| `ad_account_id` | `string` | Ad account ID |
| `created_time` | `integer` | Creation timestamp (Unix seconds) |
| `daily_spend_cap` | `integer` | Maximum daily spend in microcurrency |
| `end_time` | `integer` | End timestamp (Unix seconds) |
| `id` | `string` | Campaign ID |
| `is_campaign_budget_optimization` | `boolean` | Whether CBO is enabled |
| `is_flexible_daily_budgets` | `boolean` | Whether flexible daily budgets are enabled |
| `lifetime_spend_cap` | `integer` | Maximum lifetime spend in microcurrency |
| `name` | `string` | Campaign name |
| `objective_type` | `string` | Campaign objective type |
| `order_line_id` | `string` | Order line ID on invoice |
| `start_time` | `integer` | Start timestamp (Unix seconds) |
| `status` | `string` | Entity status |
| `summary_status` | `string` | Summary status |
| `tracking_urls` | `object` | Third-party tracking URLs |
| `type` | `string` | Always 'campaign' |
| `updated_time` | `integer` | Last update timestamp (Unix seconds) |

<details>
<summary><b>Response Schema</b></summary>

| Field Name | Type | Description |
|------------|------|-------------|
| `data` | `array` | List of matching records |
| `meta` | `object` | Pagination metadata |
| `meta.has_more` | `boolean` | Whether additional pages are available |
| `meta.cursor` | `string \| null` | Cursor for next page of results |
| `meta.took_ms` | `number \| null` | Query execution time in milliseconds |
| `data[].ad_account_id` | `string` | Ad account ID |
| `data[].created_time` | `integer` | Creation timestamp (Unix seconds) |
| `data[].daily_spend_cap` | `integer` | Maximum daily spend in microcurrency |
| `data[].end_time` | `integer` | End timestamp (Unix seconds) |
| `data[].id` | `string` | Campaign ID |
| `data[].is_campaign_budget_optimization` | `boolean` | Whether CBO is enabled |
| `data[].is_flexible_daily_budgets` | `boolean` | Whether flexible daily budgets are enabled |
| `data[].lifetime_spend_cap` | `integer` | Maximum lifetime spend in microcurrency |
| `data[].name` | `string` | Campaign name |
| `data[].objective_type` | `string` | Campaign objective type |
| `data[].order_line_id` | `string` | Order line ID on invoice |
| `data[].start_time` | `integer` | Start timestamp (Unix seconds) |
| `data[].status` | `string` | Entity status |
| `data[].summary_status` | `string` | Summary status |
| `data[].tracking_urls` | `object` | Third-party tracking URLs |
| `data[].type` | `string` | Always 'campaign' |
| `data[].updated_time` | `integer` | Last update timestamp (Unix seconds) |

</details>

## Ad Groups

### Ad Groups List

Get a list of ad groups in the specified ad account.

#### Python SDK

```python
await pinterest.ad_groups.list(
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
| `ad_account_id` | `string` | Yes | Unique identifier of the ad account. |
| `page_size` | `integer` | No | Maximum number of items to include in a single page of the response. |
| `bookmark` | `string` | No | Cursor value for paginating through results. |
| `entity_statuses` | `array<"ACTIVE" \| "PAUSED" \| "ARCHIVED" \| "DRAFT" \| "DELETED_DRAFT">` | No | Filter by entity status. |
| `order` | `"ASCENDING" \| "DESCENDING"` | No | Sort order. |


<details>
<summary><b>Response Schema</b></summary>

#### Records

| Field Name | Type | Description |
|------------|------|-------------|
| `id` | `null \| string` |  |
| `ad_account_id` | `null \| string` |  |
| `campaign_id` | `null \| string` |  |
| `name` | `null \| string` |  |
| `status` | `null \| string` |  |
| `budget_in_micro_currency` | `null \| number` |  |
| `bid_in_micro_currency` | `null \| number` |  |
| `budget_type` | `null \| string` |  |
| `start_time` | `null \| number` |  |
| `end_time` | `null \| number` |  |
| `targeting_spec` | `null \| object` |  |
| `lifetime_frequency_cap` | `null \| number` |  |
| `tracking_urls` | `null \| object` |  |
| `auto_targeting_enabled` | `null \| boolean` |  |
| `placement_group` | `null \| string` |  |
| `pacing_delivery_type` | `null \| string` |  |
| `conversion_learning_mode_type` | `null \| string` |  |
| `summary_status` | `null \| string` |  |
| `feed_profile_id` | `null \| string` |  |
| `billable_event` | `null \| string` |  |
| `type` | `null \| string` |  |
| `created_time` | `null \| number` |  |
| `updated_time` | `null \| number` |  |
| `bid_strategy_type` | `null \| string` |  |
| `optimization_goal_metadata` | `null \| object` |  |
| `placement_traffic_type` | `null \| string` |  |
| `targeting_template_ids` | `null \| array` |  |
| `is_creative_optimization` | `null \| boolean` |  |
| `promotion_id` | `null \| string` |  |
| `promotion_ids` | `null \| array` |  |
| `promotion_application_level` | `null \| string` |  |
| `bid_multiplier` | `null \| number` |  |


#### Meta

| Field Name | Type | Description |
|------------|------|-------------|
| `bookmark` | `null \| string` |  |

</details>

### Ad Groups Search

Search and filter ad groups records powered by Airbyte's data sync. This often provides additional fields and operators beyond what the API natively supports, making it easier to narrow down results before performing further operations. Only available in hosted mode.

#### Python SDK

```python
await pinterest.ad_groups.search(
    query={"filter": {"eq": {"ad_account_id": "<str>"}}}
)
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/integrations/connectors/{your_connector_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "ad_groups",
    "action": "search",
    "params": {
        "query": {"filter": {"eq": {"ad_account_id": "<str>"}}}
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
| `ad_account_id` | `string` | Ad account ID |
| `auto_targeting_enabled` | `boolean` | Whether auto targeting is enabled |
| `bid_in_micro_currency` | `number` | Bid in microcurrency |
| `bid_strategy_type` | `string` | Bid strategy type |
| `billable_event` | `string` | Billable event type |
| `budget_in_micro_currency` | `number` | Budget in microcurrency |
| `budget_type` | `string` | Budget type |
| `campaign_id` | `string` | Parent campaign ID |
| `conversion_learning_mode_type` | `string` | oCPM learn mode type |
| `created_time` | `number` | Creation timestamp (Unix seconds) |
| `end_time` | `number` | End time (Unix seconds) |
| `feed_profile_id` | `string` | Feed profile ID |
| `id` | `string` | Ad group ID |
| `lifetime_frequency_cap` | `number` | Max impressions per user in 30 days |
| `name` | `string` | Ad group name |
| `optimization_goal_metadata` | `object` | Optimization goal metadata |
| `pacing_delivery_type` | `string` | Pacing delivery type |
| `placement_group` | `string` | Placement group |
| `start_time` | `number` | Start time (Unix seconds) |
| `status` | `string` | Entity status |
| `summary_status` | `string` | Summary status |
| `targeting_spec` | `object` | Targeting specifications |
| `tracking_urls` | `object` | Third-party tracking URLs |
| `type` | `string` | Always 'adgroup' |
| `updated_time` | `number` | Last update timestamp (Unix seconds) |

<details>
<summary><b>Response Schema</b></summary>

| Field Name | Type | Description |
|------------|------|-------------|
| `data` | `array` | List of matching records |
| `meta` | `object` | Pagination metadata |
| `meta.has_more` | `boolean` | Whether additional pages are available |
| `meta.cursor` | `string \| null` | Cursor for next page of results |
| `meta.took_ms` | `number \| null` | Query execution time in milliseconds |
| `data[].ad_account_id` | `string` | Ad account ID |
| `data[].auto_targeting_enabled` | `boolean` | Whether auto targeting is enabled |
| `data[].bid_in_micro_currency` | `number` | Bid in microcurrency |
| `data[].bid_strategy_type` | `string` | Bid strategy type |
| `data[].billable_event` | `string` | Billable event type |
| `data[].budget_in_micro_currency` | `number` | Budget in microcurrency |
| `data[].budget_type` | `string` | Budget type |
| `data[].campaign_id` | `string` | Parent campaign ID |
| `data[].conversion_learning_mode_type` | `string` | oCPM learn mode type |
| `data[].created_time` | `number` | Creation timestamp (Unix seconds) |
| `data[].end_time` | `number` | End time (Unix seconds) |
| `data[].feed_profile_id` | `string` | Feed profile ID |
| `data[].id` | `string` | Ad group ID |
| `data[].lifetime_frequency_cap` | `number` | Max impressions per user in 30 days |
| `data[].name` | `string` | Ad group name |
| `data[].optimization_goal_metadata` | `object` | Optimization goal metadata |
| `data[].pacing_delivery_type` | `string` | Pacing delivery type |
| `data[].placement_group` | `string` | Placement group |
| `data[].start_time` | `number` | Start time (Unix seconds) |
| `data[].status` | `string` | Entity status |
| `data[].summary_status` | `string` | Summary status |
| `data[].targeting_spec` | `object` | Targeting specifications |
| `data[].tracking_urls` | `object` | Third-party tracking URLs |
| `data[].type` | `string` | Always 'adgroup' |
| `data[].updated_time` | `number` | Last update timestamp (Unix seconds) |

</details>

## Ads

### Ads List

Get a list of ads in the specified ad account.

#### Python SDK

```python
await pinterest.ads.list(
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
| `ad_account_id` | `string` | Yes | Unique identifier of the ad account. |
| `page_size` | `integer` | No | Maximum number of items to include in a single page of the response. |
| `bookmark` | `string` | No | Cursor value for paginating through results. |
| `entity_statuses` | `array<"ACTIVE" \| "PAUSED" \| "ARCHIVED" \| "DRAFT" \| "DELETED_DRAFT">` | No | Filter by entity status. |
| `order` | `"ASCENDING" \| "DESCENDING"` | No | Sort order. |


<details>
<summary><b>Response Schema</b></summary>

#### Records

| Field Name | Type | Description |
|------------|------|-------------|
| `id` | `null \| string` |  |
| `ad_group_id` | `null \| string` |  |
| `ad_account_id` | `null \| string` |  |
| `campaign_id` | `null \| string` |  |
| `pin_id` | `null \| string` |  |
| `name` | `null \| string` |  |
| `status` | `null \| string` |  |
| `creative_type` | `null \| string` |  |
| `destination_url` | `null \| string` |  |
| `click_tracking_url` | `null \| string` |  |
| `view_tracking_url` | `null \| string` |  |
| `android_deep_link` | `null \| string` |  |
| `ios_deep_link` | `null \| string` |  |
| `carousel_android_deep_links` | `null \| array` |  |
| `carousel_destination_urls` | `null \| array` |  |
| `carousel_ios_deep_links` | `null \| array` |  |
| `tracking_urls` | `null \| object` |  |
| `is_pin_deleted` | `null \| boolean` |  |
| `is_removable` | `null \| boolean` |  |
| `lead_form_id` | `null \| string` |  |
| `collection_items_destination_url_template` | `null \| string` |  |
| `created_time` | `null \| integer` |  |
| `updated_time` | `null \| integer` |  |
| `rejected_reasons` | `null \| array` |  |
| `rejection_labels` | `null \| array` |  |
| `review_status` | `null \| string` |  |
| `type` | `null \| string` |  |
| `summary_status` | `null \| string` |  |
| `quiz_pin_data` | `null \| object` |  |
| `grid_click_type` | `null \| string` |  |
| `customizable_cta_type` | `null \| string` |  |
| `disclosure_type` | `null \| string` |  |
| `disclosure_url` | `null \| string` |  |


#### Meta

| Field Name | Type | Description |
|------------|------|-------------|
| `bookmark` | `null \| string` |  |

</details>

### Ads Search

Search and filter ads records powered by Airbyte's data sync. This often provides additional fields and operators beyond what the API natively supports, making it easier to narrow down results before performing further operations. Only available in hosted mode.

#### Python SDK

```python
await pinterest.ads.search(
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
    "action": "search",
    "params": {
        "query": {"filter": {"eq": {"ad_account_id": "<str>"}}}
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
| `ad_account_id` | `string` | Ad account ID |
| `ad_group_id` | `string` | Ad group ID |
| `android_deep_link` | `string` | Android deep link |
| `campaign_id` | `string` | Campaign ID |
| `carousel_android_deep_links` | `array` | Carousel Android deep links |
| `carousel_destination_urls` | `array` | Carousel destination URLs |
| `carousel_ios_deep_links` | `array` | Carousel iOS deep links |
| `click_tracking_url` | `string` | Click tracking URL |
| `collection_items_destination_url_template` | `string` | Template URL for collection items |
| `created_time` | `integer` | Creation timestamp (Unix seconds) |
| `creative_type` | `string` | Creative type |
| `destination_url` | `string` | Main destination URL |
| `id` | `string` | Unique ad ID |
| `ios_deep_link` | `string` | iOS deep link |
| `is_pin_deleted` | `boolean` | Whether the original pin is deleted |
| `is_removable` | `boolean` | Whether the ad is removable |
| `lead_form_id` | `string` | Lead form ID |
| `name` | `string` | Ad name |
| `pin_id` | `string` | Associated pin ID |
| `rejected_reasons` | `array` | Rejection reasons |
| `rejection_labels` | `array` | Rejection text labels |
| `review_status` | `string` | Review status |
| `status` | `string` | Entity status |
| `summary_status` | `string` | Summary status |
| `tracking_urls` | `object` | Third-party tracking URLs |
| `type` | `string` | Always 'pinpromotion' |
| `updated_time` | `integer` | Last update timestamp (Unix seconds) |
| `view_tracking_url` | `string` | View tracking URL |

<details>
<summary><b>Response Schema</b></summary>

| Field Name | Type | Description |
|------------|------|-------------|
| `data` | `array` | List of matching records |
| `meta` | `object` | Pagination metadata |
| `meta.has_more` | `boolean` | Whether additional pages are available |
| `meta.cursor` | `string \| null` | Cursor for next page of results |
| `meta.took_ms` | `number \| null` | Query execution time in milliseconds |
| `data[].ad_account_id` | `string` | Ad account ID |
| `data[].ad_group_id` | `string` | Ad group ID |
| `data[].android_deep_link` | `string` | Android deep link |
| `data[].campaign_id` | `string` | Campaign ID |
| `data[].carousel_android_deep_links` | `array` | Carousel Android deep links |
| `data[].carousel_destination_urls` | `array` | Carousel destination URLs |
| `data[].carousel_ios_deep_links` | `array` | Carousel iOS deep links |
| `data[].click_tracking_url` | `string` | Click tracking URL |
| `data[].collection_items_destination_url_template` | `string` | Template URL for collection items |
| `data[].created_time` | `integer` | Creation timestamp (Unix seconds) |
| `data[].creative_type` | `string` | Creative type |
| `data[].destination_url` | `string` | Main destination URL |
| `data[].id` | `string` | Unique ad ID |
| `data[].ios_deep_link` | `string` | iOS deep link |
| `data[].is_pin_deleted` | `boolean` | Whether the original pin is deleted |
| `data[].is_removable` | `boolean` | Whether the ad is removable |
| `data[].lead_form_id` | `string` | Lead form ID |
| `data[].name` | `string` | Ad name |
| `data[].pin_id` | `string` | Associated pin ID |
| `data[].rejected_reasons` | `array` | Rejection reasons |
| `data[].rejection_labels` | `array` | Rejection text labels |
| `data[].review_status` | `string` | Review status |
| `data[].status` | `string` | Entity status |
| `data[].summary_status` | `string` | Summary status |
| `data[].tracking_urls` | `object` | Third-party tracking URLs |
| `data[].type` | `string` | Always 'pinpromotion' |
| `data[].updated_time` | `integer` | Last update timestamp (Unix seconds) |
| `data[].view_tracking_url` | `string` | View tracking URL |

</details>

## Board Sections

### Board Sections List

Get a list of sections for a specific board.

#### Python SDK

```python
await pinterest.board_sections.list(
    board_id="<str>"
)
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/integrations/connectors/{your_connector_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "board_sections",
    "action": "list",
    "params": {
        "board_id": "<str>"
    }
}'
```


#### Parameters

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `board_id` | `string` | Yes | Unique identifier of the board. |
| `page_size` | `integer` | No | Maximum number of items to include in a single page of the response. |
| `bookmark` | `string` | No | Cursor value for paginating through results. |


<details>
<summary><b>Response Schema</b></summary>

#### Records

| Field Name | Type | Description |
|------------|------|-------------|
| `id` | `null \| string` |  |
| `name` | `null \| string` |  |


#### Meta

| Field Name | Type | Description |
|------------|------|-------------|
| `bookmark` | `null \| string` |  |

</details>

### Board Sections Search

Search and filter board sections records powered by Airbyte's data sync. This often provides additional fields and operators beyond what the API natively supports, making it easier to narrow down results before performing further operations. Only available in hosted mode.

#### Python SDK

```python
await pinterest.board_sections.search(
    query={"filter": {"eq": {"id": "<str>"}}}
)
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/integrations/connectors/{your_connector_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "board_sections",
    "action": "search",
    "params": {
        "query": {"filter": {"eq": {"id": "<str>"}}}
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
| `id` | `string` | Unique identifier for the board section |
| `name` | `string` | Name of the board section |

<details>
<summary><b>Response Schema</b></summary>

| Field Name | Type | Description |
|------------|------|-------------|
| `data` | `array` | List of matching records |
| `meta` | `object` | Pagination metadata |
| `meta.has_more` | `boolean` | Whether additional pages are available |
| `meta.cursor` | `string \| null` | Cursor for next page of results |
| `meta.took_ms` | `number \| null` | Query execution time in milliseconds |
| `data[].id` | `string` | Unique identifier for the board section |
| `data[].name` | `string` | Name of the board section |

</details>

## Board Pins

### Board Pins List

Get a list of pins on a specific board.

#### Python SDK

```python
await pinterest.board_pins.list(
    board_id="<str>"
)
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/integrations/connectors/{your_connector_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "board_pins",
    "action": "list",
    "params": {
        "board_id": "<str>"
    }
}'
```


#### Parameters

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `board_id` | `string` | Yes | Unique identifier of the board. |
| `page_size` | `integer` | No | Maximum number of items to include in a single page of the response. |
| `bookmark` | `string` | No | Cursor value for paginating through results. |


<details>
<summary><b>Response Schema</b></summary>

#### Records

| Field Name | Type | Description |
|------------|------|-------------|
| `id` | `null \| string` |  |
| `created_at` | `null \| string` |  |
| `creative_type` | `null \| string` |  |
| `is_standard` | `null \| boolean` |  |
| `is_owner` | `null \| boolean` |  |
| `dominant_color` | `null \| string` |  |
| `parent_pin_id` | `null \| string` |  |
| `link` | `null \| string` |  |
| `title` | `null \| string` |  |
| `description` | `null \| string` |  |
| `alt_text` | `null \| string` |  |
| `board_id` | `null \| string` |  |
| `board_section_id` | `null \| string` |  |
| `board_owner` | `null \| object` |  |
| `media` | `null \| object` |  |
| `pin_metrics` | `null \| object` |  |
| `has_been_promoted` | `null \| boolean` |  |
| `is_removable` | `null \| boolean` |  |
| `product_tags` | `null \| array` |  |


#### Meta

| Field Name | Type | Description |
|------------|------|-------------|
| `bookmark` | `null \| string` |  |

</details>

### Board Pins Search

Search and filter board pins records powered by Airbyte's data sync. This often provides additional fields and operators beyond what the API natively supports, making it easier to narrow down results before performing further operations. Only available in hosted mode.

#### Python SDK

```python
await pinterest.board_pins.search(
    query={"filter": {"eq": {"alt_text": "<str>"}}}
)
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/integrations/connectors/{your_connector_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "board_pins",
    "action": "search",
    "params": {
        "query": {"filter": {"eq": {"alt_text": "<str>"}}}
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
| `alt_text` | `string` | Alternate text for accessibility |
| `board_id` | `string` | Board the pin belongs to |
| `board_owner` | `object` | Board owner info |
| `board_section_id` | `string` | Section within the board |
| `created_at` | `string` | Timestamp when the pin was created |
| `creative_type` | `string` | Creative type |
| `description` | `string` | Pin description |
| `dominant_color` | `string` | Dominant color from the pin image |
| `has_been_promoted` | `boolean` | Whether the pin has been promoted |
| `id` | `string` | Unique pin identifier |
| `is_owner` | `boolean` | Whether the current user is the owner |
| `is_standard` | `boolean` | Whether the pin is a standard pin |
| `link` | `string` | URL link associated with the pin |
| `media` | `object` | Media content |
| `parent_pin_id` | `string` | Parent pin ID if this is a repin |
| `pin_metrics` | `object` | Pin metrics data |
| `title` | `string` | Pin title |

<details>
<summary><b>Response Schema</b></summary>

| Field Name | Type | Description |
|------------|------|-------------|
| `data` | `array` | List of matching records |
| `meta` | `object` | Pagination metadata |
| `meta.has_more` | `boolean` | Whether additional pages are available |
| `meta.cursor` | `string \| null` | Cursor for next page of results |
| `meta.took_ms` | `number \| null` | Query execution time in milliseconds |
| `data[].alt_text` | `string` | Alternate text for accessibility |
| `data[].board_id` | `string` | Board the pin belongs to |
| `data[].board_owner` | `object` | Board owner info |
| `data[].board_section_id` | `string` | Section within the board |
| `data[].created_at` | `string` | Timestamp when the pin was created |
| `data[].creative_type` | `string` | Creative type |
| `data[].description` | `string` | Pin description |
| `data[].dominant_color` | `string` | Dominant color from the pin image |
| `data[].has_been_promoted` | `boolean` | Whether the pin has been promoted |
| `data[].id` | `string` | Unique pin identifier |
| `data[].is_owner` | `boolean` | Whether the current user is the owner |
| `data[].is_standard` | `boolean` | Whether the pin is a standard pin |
| `data[].link` | `string` | URL link associated with the pin |
| `data[].media` | `object` | Media content |
| `data[].parent_pin_id` | `string` | Parent pin ID if this is a repin |
| `data[].pin_metrics` | `object` | Pin metrics data |
| `data[].title` | `string` | Pin title |

</details>

## Catalogs

### Catalogs List

Get a list of catalogs for the authenticated user.

#### Python SDK

```python
await pinterest.catalogs.list()
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/integrations/connectors/{your_connector_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "catalogs",
    "action": "list"
}'
```


#### Parameters

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `page_size` | `integer` | No | Maximum number of items to include in a single page of the response. |
| `bookmark` | `string` | No | Cursor value for paginating through results. |


<details>
<summary><b>Response Schema</b></summary>

#### Records

| Field Name | Type | Description |
|------------|------|-------------|
| `id` | `null \| string` |  |
| `created_at` | `null \| string` |  |
| `updated_at` | `null \| string` |  |
| `name` | `null \| string` |  |
| `catalog_type` | `null \| string` |  |


#### Meta

| Field Name | Type | Description |
|------------|------|-------------|
| `bookmark` | `null \| string` |  |

</details>

### Catalogs Search

Search and filter catalogs records powered by Airbyte's data sync. This often provides additional fields and operators beyond what the API natively supports, making it easier to narrow down results before performing further operations. Only available in hosted mode.

#### Python SDK

```python
await pinterest.catalogs.search(
    query={"filter": {"eq": {"catalog_type": "<str>"}}}
)
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/integrations/connectors/{your_connector_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "catalogs",
    "action": "search",
    "params": {
        "query": {"filter": {"eq": {"catalog_type": "<str>"}}}
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
| `catalog_type` | `string` | Type of catalog |
| `created_at` | `string` | Timestamp when the catalog was created |
| `id` | `string` | Unique catalog identifier |
| `name` | `string` | Catalog name |
| `updated_at` | `string` | Timestamp when the catalog was last updated |

<details>
<summary><b>Response Schema</b></summary>

| Field Name | Type | Description |
|------------|------|-------------|
| `data` | `array` | List of matching records |
| `meta` | `object` | Pagination metadata |
| `meta.has_more` | `boolean` | Whether additional pages are available |
| `meta.cursor` | `string \| null` | Cursor for next page of results |
| `meta.took_ms` | `number \| null` | Query execution time in milliseconds |
| `data[].catalog_type` | `string` | Type of catalog |
| `data[].created_at` | `string` | Timestamp when the catalog was created |
| `data[].id` | `string` | Unique catalog identifier |
| `data[].name` | `string` | Catalog name |
| `data[].updated_at` | `string` | Timestamp when the catalog was last updated |

</details>

## Catalogs Feeds

### Catalogs Feeds List

Get a list of catalog feeds for the authenticated user.

#### Python SDK

```python
await pinterest.catalogs_feeds.list()
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/integrations/connectors/{your_connector_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "catalogs_feeds",
    "action": "list"
}'
```


#### Parameters

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `page_size` | `integer` | No | Maximum number of items to include in a single page of the response. |
| `bookmark` | `string` | No | Cursor value for paginating through results. |


<details>
<summary><b>Response Schema</b></summary>

#### Records

| Field Name | Type | Description |
|------------|------|-------------|
| `id` | `null \| string` |  |
| `created_at` | `null \| string` |  |
| `updated_at` | `null \| string` |  |
| `name` | `null \| string` |  |
| `format` | `null \| string` |  |
| `catalog_type` | `null \| string` |  |
| `location` | `null \| string` |  |
| `preferred_processing_schedule` | `null \| object` |  |
| `status` | `null \| string` |  |
| `default_currency` | `null \| string` |  |
| `default_locale` | `null \| string` |  |
| `default_country` | `null \| string` |  |
| `default_availability` | `null \| string` |  |


#### Meta

| Field Name | Type | Description |
|------------|------|-------------|
| `bookmark` | `null \| string` |  |

</details>

### Catalogs Feeds Search

Search and filter catalogs feeds records powered by Airbyte's data sync. This often provides additional fields and operators beyond what the API natively supports, making it easier to narrow down results before performing further operations. Only available in hosted mode.

#### Python SDK

```python
await pinterest.catalogs_feeds.search(
    query={"filter": {"eq": {"catalog_type": "<str>"}}}
)
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/integrations/connectors/{your_connector_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "catalogs_feeds",
    "action": "search",
    "params": {
        "query": {"filter": {"eq": {"catalog_type": "<str>"}}}
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
| `catalog_type` | `string` | Type of catalog |
| `created_at` | `string` | Timestamp when the feed was created |
| `default_availability` | `string` | Default availability status |
| `default_country` | `string` | Default country |
| `default_currency` | `string` | Default currency for pricing |
| `default_locale` | `string` | Default locale |
| `format` | `string` | Feed format |
| `id` | `string` | Unique feed identifier |
| `location` | `string` | URL where the feed is available |
| `name` | `string` | Feed name |
| `preferred_processing_schedule` | `object` | Preferred processing schedule |
| `status` | `string` | Feed status |
| `updated_at` | `string` | Timestamp when the feed was last updated |

<details>
<summary><b>Response Schema</b></summary>

| Field Name | Type | Description |
|------------|------|-------------|
| `data` | `array` | List of matching records |
| `meta` | `object` | Pagination metadata |
| `meta.has_more` | `boolean` | Whether additional pages are available |
| `meta.cursor` | `string \| null` | Cursor for next page of results |
| `meta.took_ms` | `number \| null` | Query execution time in milliseconds |
| `data[].catalog_type` | `string` | Type of catalog |
| `data[].created_at` | `string` | Timestamp when the feed was created |
| `data[].default_availability` | `string` | Default availability status |
| `data[].default_country` | `string` | Default country |
| `data[].default_currency` | `string` | Default currency for pricing |
| `data[].default_locale` | `string` | Default locale |
| `data[].format` | `string` | Feed format |
| `data[].id` | `string` | Unique feed identifier |
| `data[].location` | `string` | URL where the feed is available |
| `data[].name` | `string` | Feed name |
| `data[].preferred_processing_schedule` | `object` | Preferred processing schedule |
| `data[].status` | `string` | Feed status |
| `data[].updated_at` | `string` | Timestamp when the feed was last updated |

</details>

## Catalogs Product Groups

### Catalogs Product Groups List

Get a list of catalog product groups for the authenticated user.

#### Python SDK

```python
await pinterest.catalogs_product_groups.list()
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/integrations/connectors/{your_connector_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "catalogs_product_groups",
    "action": "list"
}'
```


#### Parameters

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `page_size` | `integer` | No | Maximum number of items to include in a single page of the response. |
| `bookmark` | `string` | No | Cursor value for paginating through results. |


<details>
<summary><b>Response Schema</b></summary>

#### Records

| Field Name | Type | Description |
|------------|------|-------------|
| `id` | `null \| string` |  |
| `created_at` | `null \| integer` |  |
| `updated_at` | `null \| integer` |  |
| `name` | `null \| string` |  |
| `description` | `null \| string` |  |
| `feed_id` | `null \| string` |  |
| `is_featured` | `null \| boolean` |  |
| `status` | `null \| string` |  |
| `type` | `null \| string` |  |


#### Meta

| Field Name | Type | Description |
|------------|------|-------------|
| `bookmark` | `null \| string` |  |

</details>

### Catalogs Product Groups Search

Search and filter catalogs product groups records powered by Airbyte's data sync. This often provides additional fields and operators beyond what the API natively supports, making it easier to narrow down results before performing further operations. Only available in hosted mode.

#### Python SDK

```python
await pinterest.catalogs_product_groups.search(
    query={"filter": {"eq": {"created_at": 0}}}
)
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/integrations/connectors/{your_connector_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "catalogs_product_groups",
    "action": "search",
    "params": {
        "query": {"filter": {"eq": {"created_at": 0}}}
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
| `created_at` | `integer` | Creation timestamp (Unix seconds) |
| `description` | `string` | Product group description |
| `feed_id` | `string` | Associated feed ID |
| `id` | `string` | Unique product group identifier |
| `is_featured` | `boolean` | Whether the product group is featured |
| `name` | `string` | Product group name |
| `status` | `string` | Product group status |
| `type` | `string` | Product group type |
| `updated_at` | `integer` | Last update timestamp (Unix seconds) |

<details>
<summary><b>Response Schema</b></summary>

| Field Name | Type | Description |
|------------|------|-------------|
| `data` | `array` | List of matching records |
| `meta` | `object` | Pagination metadata |
| `meta.has_more` | `boolean` | Whether additional pages are available |
| `meta.cursor` | `string \| null` | Cursor for next page of results |
| `meta.took_ms` | `number \| null` | Query execution time in milliseconds |
| `data[].created_at` | `integer` | Creation timestamp (Unix seconds) |
| `data[].description` | `string` | Product group description |
| `data[].feed_id` | `string` | Associated feed ID |
| `data[].id` | `string` | Unique product group identifier |
| `data[].is_featured` | `boolean` | Whether the product group is featured |
| `data[].name` | `string` | Product group name |
| `data[].status` | `string` | Product group status |
| `data[].type` | `string` | Product group type |
| `data[].updated_at` | `integer` | Last update timestamp (Unix seconds) |

</details>

## Audiences

### Audiences List

Get a list of audiences for the specified ad account.

#### Python SDK

```python
await pinterest.audiences.list(
    ad_account_id="<str>"
)
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/integrations/connectors/{your_connector_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "audiences",
    "action": "list",
    "params": {
        "ad_account_id": "<str>"
    }
}'
```


#### Parameters

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `ad_account_id` | `string` | Yes | Unique identifier of the ad account. |
| `page_size` | `integer` | No | Maximum number of items to include in a single page of the response. |
| `bookmark` | `string` | No | Cursor value for paginating through results. |


<details>
<summary><b>Response Schema</b></summary>

#### Records

| Field Name | Type | Description |
|------------|------|-------------|
| `id` | `null \| string` |  |
| `ad_account_id` | `null \| string` |  |
| `name` | `null \| string` |  |
| `audience_type` | `null \| string` |  |
| `description` | `null \| string` |  |
| `rule` | `null \| object` |  |
| `size` | `null \| integer` |  |
| `status` | `null \| string` |  |
| `type` | `null \| string` |  |
| `created_timestamp` | `null \| integer` |  |
| `updated_timestamp` | `null \| integer` |  |
| `created_by_company_name` | `null \| string` |  |


#### Meta

| Field Name | Type | Description |
|------------|------|-------------|
| `bookmark` | `null \| string` |  |

</details>

### Audiences Search

Search and filter audiences records powered by Airbyte's data sync. This often provides additional fields and operators beyond what the API natively supports, making it easier to narrow down results before performing further operations. Only available in hosted mode.

#### Python SDK

```python
await pinterest.audiences.search(
    query={"filter": {"eq": {"ad_account_id": "<str>"}}}
)
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/integrations/connectors/{your_connector_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "audiences",
    "action": "search",
    "params": {
        "query": {"filter": {"eq": {"ad_account_id": "<str>"}}}
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
| `ad_account_id` | `string` | Ad account ID |
| `audience_type` | `string` | Audience type |
| `created_timestamp` | `integer` | Creation time (Unix seconds) |
| `description` | `string` | Audience description |
| `id` | `string` | Unique audience identifier |
| `name` | `string` | Audience name |
| `rule` | `object` | Audience targeting rules |
| `size` | `integer` | Estimated audience size |
| `status` | `string` | Audience status |
| `type` | `string` | Always 'audience' |
| `updated_timestamp` | `integer` | Last update time (Unix seconds) |

<details>
<summary><b>Response Schema</b></summary>

| Field Name | Type | Description |
|------------|------|-------------|
| `data` | `array` | List of matching records |
| `meta` | `object` | Pagination metadata |
| `meta.has_more` | `boolean` | Whether additional pages are available |
| `meta.cursor` | `string \| null` | Cursor for next page of results |
| `meta.took_ms` | `number \| null` | Query execution time in milliseconds |
| `data[].ad_account_id` | `string` | Ad account ID |
| `data[].audience_type` | `string` | Audience type |
| `data[].created_timestamp` | `integer` | Creation time (Unix seconds) |
| `data[].description` | `string` | Audience description |
| `data[].id` | `string` | Unique audience identifier |
| `data[].name` | `string` | Audience name |
| `data[].rule` | `object` | Audience targeting rules |
| `data[].size` | `integer` | Estimated audience size |
| `data[].status` | `string` | Audience status |
| `data[].type` | `string` | Always 'audience' |
| `data[].updated_timestamp` | `integer` | Last update time (Unix seconds) |

</details>

## Conversion Tags

### Conversion Tags List

Get a list of conversion tags for the specified ad account.

#### Python SDK

```python
await pinterest.conversion_tags.list(
    ad_account_id="<str>"
)
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/integrations/connectors/{your_connector_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "conversion_tags",
    "action": "list",
    "params": {
        "ad_account_id": "<str>"
    }
}'
```


#### Parameters

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `ad_account_id` | `string` | Yes | Unique identifier of the ad account. |
| `page_size` | `integer` | No | Maximum number of items to include in a single page of the response. |
| `bookmark` | `string` | No | Cursor value for paginating through results. |


<details>
<summary><b>Response Schema</b></summary>

#### Records

| Field Name | Type | Description |
|------------|------|-------------|
| `id` | `null \| string` |  |
| `ad_account_id` | `null \| string` |  |
| `name` | `null \| string` |  |
| `code_snippet` | `null \| string` |  |
| `enhanced_match_status` | `null \| string` |  |
| `last_fired_time_ms` | `null \| integer` |  |
| `status` | `null \| string` |  |
| `version` | `null \| string` |  |
| `configs` | `null \| object` |  |


#### Meta

| Field Name | Type | Description |
|------------|------|-------------|
| `bookmark` | `null \| string` |  |

</details>

### Conversion Tags Search

Search and filter conversion tags records powered by Airbyte's data sync. This often provides additional fields and operators beyond what the API natively supports, making it easier to narrow down results before performing further operations. Only available in hosted mode.

#### Python SDK

```python
await pinterest.conversion_tags.search(
    query={"filter": {"eq": {"ad_account_id": "<str>"}}}
)
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/integrations/connectors/{your_connector_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "conversion_tags",
    "action": "search",
    "params": {
        "query": {"filter": {"eq": {"ad_account_id": "<str>"}}}
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
| `ad_account_id` | `string` | Ad account ID |
| `code_snippet` | `string` | JavaScript code snippet for tracking |
| `configs` | `object` | Tag configurations |
| `enhanced_match_status` | `string` | Enhanced match status |
| `id` | `string` | Unique conversion tag identifier |
| `last_fired_time_ms` | `integer` | Timestamp of last event fired (milliseconds) |
| `name` | `string` | Conversion tag name |
| `status` | `string` | Status |
| `version` | `string` | Version number |

<details>
<summary><b>Response Schema</b></summary>

| Field Name | Type | Description |
|------------|------|-------------|
| `data` | `array` | List of matching records |
| `meta` | `object` | Pagination metadata |
| `meta.has_more` | `boolean` | Whether additional pages are available |
| `meta.cursor` | `string \| null` | Cursor for next page of results |
| `meta.took_ms` | `number \| null` | Query execution time in milliseconds |
| `data[].ad_account_id` | `string` | Ad account ID |
| `data[].code_snippet` | `string` | JavaScript code snippet for tracking |
| `data[].configs` | `object` | Tag configurations |
| `data[].enhanced_match_status` | `string` | Enhanced match status |
| `data[].id` | `string` | Unique conversion tag identifier |
| `data[].last_fired_time_ms` | `integer` | Timestamp of last event fired (milliseconds) |
| `data[].name` | `string` | Conversion tag name |
| `data[].status` | `string` | Status |
| `data[].version` | `string` | Version number |

</details>

## Customer Lists

### Customer Lists List

Get a list of customer lists for the specified ad account.

#### Python SDK

```python
await pinterest.customer_lists.list(
    ad_account_id="<str>"
)
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/integrations/connectors/{your_connector_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "customer_lists",
    "action": "list",
    "params": {
        "ad_account_id": "<str>"
    }
}'
```


#### Parameters

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `ad_account_id` | `string` | Yes | Unique identifier of the ad account. |
| `page_size` | `integer` | No | Maximum number of items to include in a single page of the response. |
| `bookmark` | `string` | No | Cursor value for paginating through results. |


<details>
<summary><b>Response Schema</b></summary>

#### Records

| Field Name | Type | Description |
|------------|------|-------------|
| `id` | `null \| string` |  |
| `ad_account_id` | `null \| string` |  |
| `name` | `null \| string` |  |
| `created_time` | `null \| integer` |  |
| `updated_time` | `null \| integer` |  |
| `num_batches` | `null \| integer` |  |
| `num_removed_user_records` | `null \| integer` |  |
| `num_uploaded_user_records` | `null \| integer` |  |
| `status` | `null \| string` |  |
| `type` | `null \| string` |  |


#### Meta

| Field Name | Type | Description |
|------------|------|-------------|
| `bookmark` | `null \| string` |  |

</details>

### Customer Lists Search

Search and filter customer lists records powered by Airbyte's data sync. This often provides additional fields and operators beyond what the API natively supports, making it easier to narrow down results before performing further operations. Only available in hosted mode.

#### Python SDK

```python
await pinterest.customer_lists.search(
    query={"filter": {"eq": {"ad_account_id": "<str>"}}}
)
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/integrations/connectors/{your_connector_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "customer_lists",
    "action": "search",
    "params": {
        "query": {"filter": {"eq": {"ad_account_id": "<str>"}}}
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
| `ad_account_id` | `string` | Associated ad account ID |
| `created_time` | `integer` | Creation time (Unix seconds) |
| `id` | `string` | Unique customer list identifier |
| `name` | `string` | Customer list name |
| `num_batches` | `integer` | Total number of list updates |
| `num_removed_user_records` | `integer` | Count of removed user records |
| `num_uploaded_user_records` | `integer` | Count of uploaded user records |
| `status` | `string` | Status |
| `type` | `string` | Always 'customerlist' |
| `updated_time` | `integer` | Last update time (Unix seconds) |

<details>
<summary><b>Response Schema</b></summary>

| Field Name | Type | Description |
|------------|------|-------------|
| `data` | `array` | List of matching records |
| `meta` | `object` | Pagination metadata |
| `meta.has_more` | `boolean` | Whether additional pages are available |
| `meta.cursor` | `string \| null` | Cursor for next page of results |
| `meta.took_ms` | `number \| null` | Query execution time in milliseconds |
| `data[].ad_account_id` | `string` | Associated ad account ID |
| `data[].created_time` | `integer` | Creation time (Unix seconds) |
| `data[].id` | `string` | Unique customer list identifier |
| `data[].name` | `string` | Customer list name |
| `data[].num_batches` | `integer` | Total number of list updates |
| `data[].num_removed_user_records` | `integer` | Count of removed user records |
| `data[].num_uploaded_user_records` | `integer` | Count of uploaded user records |
| `data[].status` | `string` | Status |
| `data[].type` | `string` | Always 'customerlist' |
| `data[].updated_time` | `integer` | Last update time (Unix seconds) |

</details>

## Keywords

### Keywords List

Get a list of keywords for the specified ad account. Requires an ad_group_id filter.

#### Python SDK

```python
await pinterest.keywords.list(
    ad_account_id="<str>",
    ad_group_id="<str>"
)
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/integrations/connectors/{your_connector_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "keywords",
    "action": "list",
    "params": {
        "ad_account_id": "<str>",
        "ad_group_id": "<str>"
    }
}'
```


#### Parameters

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `ad_account_id` | `string` | Yes | Unique identifier of the ad account. |
| `ad_group_id` | `string` | Yes | Ad group ID to filter keywords by. |
| `page_size` | `integer` | No | Maximum number of items to include in a single page of the response. |
| `bookmark` | `string` | No | Cursor value for paginating through results. |


<details>
<summary><b>Response Schema</b></summary>

#### Records

| Field Name | Type | Description |
|------------|------|-------------|
| `id` | `null \| string` |  |
| `archived` | `null \| boolean` |  |
| `parent_id` | `null \| string` |  |
| `parent_type` | `null \| string` |  |
| `type` | `null \| string` |  |
| `bid` | `null \| integer` |  |
| `match_type` | `null \| string` |  |
| `value` | `null \| string` |  |


#### Meta

| Field Name | Type | Description |
|------------|------|-------------|
| `bookmark` | `null \| string` |  |

</details>

### Keywords Search

Search and filter keywords records powered by Airbyte's data sync. This often provides additional fields and operators beyond what the API natively supports, making it easier to narrow down results before performing further operations. Only available in hosted mode.

#### Python SDK

```python
await pinterest.keywords.search(
    query={"filter": {"eq": {"archived": True}}}
)
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/integrations/connectors/{your_connector_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "keywords",
    "action": "search",
    "params": {
        "query": {"filter": {"eq": {"archived": True}}}
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
| `archived` | `boolean` | Whether the keyword is archived |
| `bid` | `integer` | Bid value in microcurrency |
| `id` | `string` | Unique keyword identifier |
| `match_type` | `string` | Match type |
| `parent_id` | `string` | Parent entity ID |
| `parent_type` | `string` | Parent entity type |
| `type` | `string` | Always 'keyword' |
| `value` | `string` | Keyword text value |

<details>
<summary><b>Response Schema</b></summary>

| Field Name | Type | Description |
|------------|------|-------------|
| `data` | `array` | List of matching records |
| `meta` | `object` | Pagination metadata |
| `meta.has_more` | `boolean` | Whether additional pages are available |
| `meta.cursor` | `string \| null` | Cursor for next page of results |
| `meta.took_ms` | `number \| null` | Query execution time in milliseconds |
| `data[].archived` | `boolean` | Whether the keyword is archived |
| `data[].bid` | `integer` | Bid value in microcurrency |
| `data[].id` | `string` | Unique keyword identifier |
| `data[].match_type` | `string` | Match type |
| `data[].parent_id` | `string` | Parent entity ID |
| `data[].parent_type` | `string` | Parent entity type |
| `data[].type` | `string` | Always 'keyword' |
| `data[].value` | `string` | Keyword text value |

</details>

