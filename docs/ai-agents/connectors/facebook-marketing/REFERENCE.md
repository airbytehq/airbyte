# Facebook-Marketing full reference

This is the full reference documentation for the Facebook-Marketing agent connector.

## Supported entities and actions

The Facebook-Marketing connector supports the following entities and actions.

| Entity | Actions |
|--------|---------|
| Campaigns | [List](#campaigns-list), [Get](#campaigns-get), [Search](#campaigns-search) |
| Ad Sets | [List](#ad-sets-list), [Get](#ad-sets-get), [Search](#ad-sets-search) |
| Ads | [List](#ads-list), [Get](#ads-get), [Search](#ads-search) |
| Ad Creatives | [List](#ad-creatives-list), [Search](#ad-creatives-search) |
| Ads Insights | [List](#ads-insights-list), [Search](#ads-insights-search) |
| Custom Conversions | [List](#custom-conversions-list), [Search](#custom-conversions-search) |
| Images | [List](#images-list), [Search](#images-search) |
| Videos | [List](#videos-list), [Search](#videos-search) |

## Campaigns

### Campaigns List

Returns a list of campaigns for the specified ad account

#### Python SDK

```python
await facebook_marketing.campaigns.list(
    account_id="<str>"
)
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/connectors/sources/{your_source_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "campaigns",
    "action": "list",
    "params": {
        "account_id": "<str>"
    }
}'
```


#### Parameters

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `account_id` | `string` | Yes | The Facebook Ad Account ID (without act_ prefix) |
| `fields` | `string` | No | Comma-separated list of fields to return |
| `limit` | `integer` | No | Maximum number of results to return |
| `after` | `string` | No | Cursor for pagination |


<details>
<summary><b>Response Schema</b></summary>

#### Records

| Field Name | Type | Description |
|------------|------|-------------|
| `id` | `string` |  |
| `name` | `string \| null` |  |
| `account_id` | `string \| null` |  |
| `adlabels` | `array \| null` |  |
| `adlabels[].id` | `string \| null` |  |
| `adlabels[].name` | `string \| null` |  |
| `adlabels[].created_time` | `string \| null` |  |
| `adlabels[].updated_time` | `string \| null` |  |
| `bid_strategy` | `string \| null` |  |
| `boosted_object_id` | `string \| null` |  |
| `budget_rebalance_flag` | `boolean \| null` |  |
| `budget_remaining` | `number \| null` |  |
| `buying_type` | `string \| null` |  |
| `daily_budget` | `number \| null` |  |
| `created_time` | `string \| null` |  |
| `configured_status` | `string \| null` |  |
| `effective_status` | `string \| null` |  |
| `issues_info` | `array \| null` |  |
| `issues_info[].error_code` | `string \| null` |  |
| `issues_info[].error_message` | `string \| null` |  |
| `issues_info[].error_summary` | `string \| null` |  |
| `issues_info[].error_type` | `string \| null` |  |
| `issues_info[].level` | `string \| null` |  |
| `lifetime_budget` | `number \| null` |  |
| `objective` | `string \| null` |  |
| `smart_promotion_type` | `string \| null` |  |
| `source_campaign_id` | `string \| null` |  |
| `special_ad_category` | `string \| null` |  |
| `special_ad_category_country` | `array \| null` |  |
| `spend_cap` | `number \| null` |  |
| `start_time` | `string \| null` |  |
| `status` | `string \| null` |  |
| `stop_time` | `string \| null` |  |
| `updated_time` | `string \| null` |  |


#### Meta

| Field Name | Type | Description |
|------------|------|-------------|
| `after` | `string \| null` |  |

</details>

### Campaigns Get

Returns a single campaign by ID

#### Python SDK

```python
await facebook_marketing.campaigns.get(
    campaign_id="<str>"
)
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/connectors/sources/{your_source_id}/execute' \
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
| `fields` | `string` | No | Comma-separated list of fields to return |


<details>
<summary><b>Response Schema</b></summary>

#### Records

| Field Name | Type | Description |
|------------|------|-------------|
| `id` | `string` |  |
| `name` | `string \| null` |  |
| `account_id` | `string \| null` |  |
| `adlabels` | `array \| null` |  |
| `adlabels[].id` | `string \| null` |  |
| `adlabels[].name` | `string \| null` |  |
| `adlabels[].created_time` | `string \| null` |  |
| `adlabels[].updated_time` | `string \| null` |  |
| `bid_strategy` | `string \| null` |  |
| `boosted_object_id` | `string \| null` |  |
| `budget_rebalance_flag` | `boolean \| null` |  |
| `budget_remaining` | `number \| null` |  |
| `buying_type` | `string \| null` |  |
| `daily_budget` | `number \| null` |  |
| `created_time` | `string \| null` |  |
| `configured_status` | `string \| null` |  |
| `effective_status` | `string \| null` |  |
| `issues_info` | `array \| null` |  |
| `issues_info[].error_code` | `string \| null` |  |
| `issues_info[].error_message` | `string \| null` |  |
| `issues_info[].error_summary` | `string \| null` |  |
| `issues_info[].error_type` | `string \| null` |  |
| `issues_info[].level` | `string \| null` |  |
| `lifetime_budget` | `number \| null` |  |
| `objective` | `string \| null` |  |
| `smart_promotion_type` | `string \| null` |  |
| `source_campaign_id` | `string \| null` |  |
| `special_ad_category` | `string \| null` |  |
| `special_ad_category_country` | `array \| null` |  |
| `spend_cap` | `number \| null` |  |
| `start_time` | `string \| null` |  |
| `status` | `string \| null` |  |
| `stop_time` | `string \| null` |  |
| `updated_time` | `string \| null` |  |


</details>

### Campaigns Search

Search and filter campaigns records powered by Airbyte's data sync. This often provides additional fields and operators beyond what the API natively supports, making it easier to narrow down results before performing further operations. Only available in hosted mode.

#### Python SDK

```python
await facebook_marketing.campaigns.search(
    query={"filter": {"eq": {"id": "<str>"}}}
)
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/connectors/sources/{your_source_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "campaigns",
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
| `cursor` | `string` | No | Pagination cursor from previous response's next_cursor |
| `fields` | `array` | No | Field paths to include in results |

#### Searchable Fields

| Field Name | Type | Description |
|------------|------|-------------|
| `id` | `string` | Campaign ID |
| `name` | `string` | Campaign name |
| `account_id` | `string` | Ad account ID |
| `status` | `string` | Campaign status |
| `effective_status` | `string` | Effective status |
| `objective` | `string` | Campaign objective |
| `daily_budget` | `number` | Daily budget in account currency |
| `lifetime_budget` | `number` | Lifetime budget |
| `budget_remaining` | `number` | Remaining budget |
| `created_time` | `string` | Campaign creation time |
| `start_time` | `string` | Campaign start time |
| `stop_time` | `string` | Campaign stop time |
| `updated_time` | `string` | Last update time |

<details>
<summary><b>Response Schema</b></summary>

| Field Name | Type | Description |
|------------|------|-------------|
| `hits` | `array` | List of matching records |
| `hits[].id` | `string` | Record identifier |
| `hits[].score` | `number` | Relevance score |
| `hits[].data` | `object` | Record data containing the searchable fields listed above |
| `hits[].data.id` | `string` | Campaign ID |
| `hits[].data.name` | `string` | Campaign name |
| `hits[].data.account_id` | `string` | Ad account ID |
| `hits[].data.status` | `string` | Campaign status |
| `hits[].data.effective_status` | `string` | Effective status |
| `hits[].data.objective` | `string` | Campaign objective |
| `hits[].data.daily_budget` | `number` | Daily budget in account currency |
| `hits[].data.lifetime_budget` | `number` | Lifetime budget |
| `hits[].data.budget_remaining` | `number` | Remaining budget |
| `hits[].data.created_time` | `string` | Campaign creation time |
| `hits[].data.start_time` | `string` | Campaign start time |
| `hits[].data.stop_time` | `string` | Campaign stop time |
| `hits[].data.updated_time` | `string` | Last update time |
| `next_cursor` | `string \| null` | Cursor for next page of results |
| `took_ms` | `number` | Query execution time in milliseconds |

</details>

## Ad Sets

### Ad Sets List

Returns a list of ad sets for the specified ad account

#### Python SDK

```python
await facebook_marketing.ad_sets.list(
    account_id="<str>"
)
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/connectors/sources/{your_source_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "ad_sets",
    "action": "list",
    "params": {
        "account_id": "<str>"
    }
}'
```


#### Parameters

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `account_id` | `string` | Yes | The Facebook Ad Account ID (without act_ prefix) |
| `fields` | `string` | No | Comma-separated list of fields to return |
| `limit` | `integer` | No | Maximum number of results to return |
| `after` | `string` | No | Cursor for pagination |


<details>
<summary><b>Response Schema</b></summary>

#### Records

| Field Name | Type | Description |
|------------|------|-------------|
| `id` | `string` |  |
| `name` | `string \| null` |  |
| `account_id` | `string \| null` |  |
| `adlabels` | `array \| null` |  |
| `adlabels[].id` | `string \| null` |  |
| `adlabels[].name` | `string \| null` |  |
| `adlabels[].created_time` | `string \| null` |  |
| `adlabels[].updated_time` | `string \| null` |  |
| `bid_amount` | `number \| null` |  |
| `bid_info` | `object \| any` |  |
| `bid_strategy` | `string \| null` |  |
| `bid_constraints` | `object \| any` |  |
| `budget_remaining` | `number \| null` |  |
| `campaign_id` | `string \| null` |  |
| `created_time` | `string \| null` |  |
| `daily_budget` | `number \| null` |  |
| `effective_status` | `string \| null` |  |
| `end_time` | `string \| null` |  |
| `learning_stage_info` | `object \| any` |  |
| `lifetime_budget` | `number \| null` |  |
| `promoted_object` | `object \| any` |  |
| `start_time` | `string \| null` |  |
| `targeting` | `object \| null` |  |
| `updated_time` | `string \| null` |  |


#### Meta

| Field Name | Type | Description |
|------------|------|-------------|
| `after` | `string \| null` |  |

</details>

### Ad Sets Get

Returns a single ad set by ID

#### Python SDK

```python
await facebook_marketing.ad_sets.get(
    adset_id="<str>"
)
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/connectors/sources/{your_source_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "ad_sets",
    "action": "get",
    "params": {
        "adset_id": "<str>"
    }
}'
```


#### Parameters

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `adset_id` | `string` | Yes | The ad set ID |
| `fields` | `string` | No | Comma-separated list of fields to return |


<details>
<summary><b>Response Schema</b></summary>

#### Records

| Field Name | Type | Description |
|------------|------|-------------|
| `id` | `string` |  |
| `name` | `string \| null` |  |
| `account_id` | `string \| null` |  |
| `adlabels` | `array \| null` |  |
| `adlabels[].id` | `string \| null` |  |
| `adlabels[].name` | `string \| null` |  |
| `adlabels[].created_time` | `string \| null` |  |
| `adlabels[].updated_time` | `string \| null` |  |
| `bid_amount` | `number \| null` |  |
| `bid_info` | `object \| any` |  |
| `bid_strategy` | `string \| null` |  |
| `bid_constraints` | `object \| any` |  |
| `budget_remaining` | `number \| null` |  |
| `campaign_id` | `string \| null` |  |
| `created_time` | `string \| null` |  |
| `daily_budget` | `number \| null` |  |
| `effective_status` | `string \| null` |  |
| `end_time` | `string \| null` |  |
| `learning_stage_info` | `object \| any` |  |
| `lifetime_budget` | `number \| null` |  |
| `promoted_object` | `object \| any` |  |
| `start_time` | `string \| null` |  |
| `targeting` | `object \| null` |  |
| `updated_time` | `string \| null` |  |


</details>

### Ad Sets Search

Search and filter ad sets records powered by Airbyte's data sync. This often provides additional fields and operators beyond what the API natively supports, making it easier to narrow down results before performing further operations. Only available in hosted mode.

#### Python SDK

```python
await facebook_marketing.ad_sets.search(
    query={"filter": {"eq": {"id": "<str>"}}}
)
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/connectors/sources/{your_source_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "ad_sets",
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
| `cursor` | `string` | No | Pagination cursor from previous response's next_cursor |
| `fields` | `array` | No | Field paths to include in results |

#### Searchable Fields

| Field Name | Type | Description |
|------------|------|-------------|
| `id` | `string` | Ad Set ID |
| `name` | `string` | Ad Set name |
| `account_id` | `string` | Ad account ID |
| `campaign_id` | `string` | Parent campaign ID |
| `effective_status` | `string` | Effective status |
| `daily_budget` | `number` | Daily budget |
| `lifetime_budget` | `number` | Lifetime budget |
| `budget_remaining` | `number` | Remaining budget |
| `bid_amount` | `number` | Bid amount |
| `bid_strategy` | `string` | Bid strategy |
| `created_time` | `string` | Ad set creation time |
| `start_time` | `string` | Ad set start time |
| `end_time` | `string` | Ad set end time |
| `updated_time` | `string` | Last update time |

<details>
<summary><b>Response Schema</b></summary>

| Field Name | Type | Description |
|------------|------|-------------|
| `hits` | `array` | List of matching records |
| `hits[].id` | `string` | Record identifier |
| `hits[].score` | `number` | Relevance score |
| `hits[].data` | `object` | Record data containing the searchable fields listed above |
| `hits[].data.id` | `string` | Ad Set ID |
| `hits[].data.name` | `string` | Ad Set name |
| `hits[].data.account_id` | `string` | Ad account ID |
| `hits[].data.campaign_id` | `string` | Parent campaign ID |
| `hits[].data.effective_status` | `string` | Effective status |
| `hits[].data.daily_budget` | `number` | Daily budget |
| `hits[].data.lifetime_budget` | `number` | Lifetime budget |
| `hits[].data.budget_remaining` | `number` | Remaining budget |
| `hits[].data.bid_amount` | `number` | Bid amount |
| `hits[].data.bid_strategy` | `string` | Bid strategy |
| `hits[].data.created_time` | `string` | Ad set creation time |
| `hits[].data.start_time` | `string` | Ad set start time |
| `hits[].data.end_time` | `string` | Ad set end time |
| `hits[].data.updated_time` | `string` | Last update time |
| `next_cursor` | `string \| null` | Cursor for next page of results |
| `took_ms` | `number` | Query execution time in milliseconds |

</details>

## Ads

### Ads List

Returns a list of ads for the specified ad account

#### Python SDK

```python
await facebook_marketing.ads.list(
    account_id="<str>"
)
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/connectors/sources/{your_source_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "ads",
    "action": "list",
    "params": {
        "account_id": "<str>"
    }
}'
```


#### Parameters

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `account_id` | `string` | Yes | The Facebook Ad Account ID (without act_ prefix) |
| `fields` | `string` | No | Comma-separated list of fields to return |
| `limit` | `integer` | No | Maximum number of results to return |
| `after` | `string` | No | Cursor for pagination |


<details>
<summary><b>Response Schema</b></summary>

#### Records

| Field Name | Type | Description |
|------------|------|-------------|
| `id` | `string` |  |
| `name` | `string \| null` |  |
| `account_id` | `string \| null` |  |
| `adset_id` | `string \| null` |  |
| `campaign_id` | `string \| null` |  |
| `adlabels` | `array \| null` |  |
| `adlabels[].id` | `string \| null` |  |
| `adlabels[].name` | `string \| null` |  |
| `adlabels[].created_time` | `string \| null` |  |
| `adlabels[].updated_time` | `string \| null` |  |
| `bid_amount` | `integer \| null` |  |
| `bid_info` | `object \| any` |  |
| `bid_type` | `string \| null` |  |
| `configured_status` | `string \| null` |  |
| `conversion_specs` | `array \| null` |  |
| `created_time` | `string \| null` |  |
| `creative` | `object \| any` |  |
| `effective_status` | `string \| null` |  |
| `last_updated_by_app_id` | `string \| null` |  |
| `recommendations` | `array \| null` |  |
| `recommendations[].blame_field` | `string \| null` |  |
| `recommendations[].code` | `integer \| null` |  |
| `recommendations[].confidence` | `string \| null` |  |
| `recommendations[].importance` | `string \| null` |  |
| `recommendations[].message` | `string \| null` |  |
| `recommendations[].title` | `string \| null` |  |
| `source_ad_id` | `string \| null` |  |
| `status` | `string \| null` |  |
| `tracking_specs` | `array \| null` |  |
| `updated_time` | `string \| null` |  |


#### Meta

| Field Name | Type | Description |
|------------|------|-------------|
| `after` | `string \| null` |  |

</details>

### Ads Get

Returns a single ad by ID

#### Python SDK

```python
await facebook_marketing.ads.get(
    ad_id="<str>"
)
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/connectors/sources/{your_source_id}/execute' \
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
| `fields` | `string` | No | Comma-separated list of fields to return |


<details>
<summary><b>Response Schema</b></summary>

#### Records

| Field Name | Type | Description |
|------------|------|-------------|
| `id` | `string` |  |
| `name` | `string \| null` |  |
| `account_id` | `string \| null` |  |
| `adset_id` | `string \| null` |  |
| `campaign_id` | `string \| null` |  |
| `adlabels` | `array \| null` |  |
| `adlabels[].id` | `string \| null` |  |
| `adlabels[].name` | `string \| null` |  |
| `adlabels[].created_time` | `string \| null` |  |
| `adlabels[].updated_time` | `string \| null` |  |
| `bid_amount` | `integer \| null` |  |
| `bid_info` | `object \| any` |  |
| `bid_type` | `string \| null` |  |
| `configured_status` | `string \| null` |  |
| `conversion_specs` | `array \| null` |  |
| `created_time` | `string \| null` |  |
| `creative` | `object \| any` |  |
| `effective_status` | `string \| null` |  |
| `last_updated_by_app_id` | `string \| null` |  |
| `recommendations` | `array \| null` |  |
| `recommendations[].blame_field` | `string \| null` |  |
| `recommendations[].code` | `integer \| null` |  |
| `recommendations[].confidence` | `string \| null` |  |
| `recommendations[].importance` | `string \| null` |  |
| `recommendations[].message` | `string \| null` |  |
| `recommendations[].title` | `string \| null` |  |
| `source_ad_id` | `string \| null` |  |
| `status` | `string \| null` |  |
| `tracking_specs` | `array \| null` |  |
| `updated_time` | `string \| null` |  |


</details>

### Ads Search

Search and filter ads records powered by Airbyte's data sync. This often provides additional fields and operators beyond what the API natively supports, making it easier to narrow down results before performing further operations. Only available in hosted mode.

#### Python SDK

```python
await facebook_marketing.ads.search(
    query={"filter": {"eq": {"id": "<str>"}}}
)
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/connectors/sources/{your_source_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "ads",
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
| `cursor` | `string` | No | Pagination cursor from previous response's next_cursor |
| `fields` | `array` | No | Field paths to include in results |

#### Searchable Fields

| Field Name | Type | Description |
|------------|------|-------------|
| `id` | `string` | Ad ID |
| `name` | `string` | Ad name |
| `account_id` | `string` | Ad account ID |
| `adset_id` | `string` | Parent ad set ID |
| `campaign_id` | `string` | Parent campaign ID |
| `status` | `string` | Ad status |
| `effective_status` | `string` | Effective status |
| `created_time` | `string` | Ad creation time |
| `updated_time` | `string` | Last update time |

<details>
<summary><b>Response Schema</b></summary>

| Field Name | Type | Description |
|------------|------|-------------|
| `hits` | `array` | List of matching records |
| `hits[].id` | `string` | Record identifier |
| `hits[].score` | `number` | Relevance score |
| `hits[].data` | `object` | Record data containing the searchable fields listed above |
| `hits[].data.id` | `string` | Ad ID |
| `hits[].data.name` | `string` | Ad name |
| `hits[].data.account_id` | `string` | Ad account ID |
| `hits[].data.adset_id` | `string` | Parent ad set ID |
| `hits[].data.campaign_id` | `string` | Parent campaign ID |
| `hits[].data.status` | `string` | Ad status |
| `hits[].data.effective_status` | `string` | Effective status |
| `hits[].data.created_time` | `string` | Ad creation time |
| `hits[].data.updated_time` | `string` | Last update time |
| `next_cursor` | `string \| null` | Cursor for next page of results |
| `took_ms` | `number` | Query execution time in milliseconds |

</details>

## Ad Creatives

### Ad Creatives List

Returns a list of ad creatives for the specified ad account

#### Python SDK

```python
await facebook_marketing.ad_creatives.list(
    account_id="<str>"
)
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/connectors/sources/{your_source_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "ad_creatives",
    "action": "list",
    "params": {
        "account_id": "<str>"
    }
}'
```


#### Parameters

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `account_id` | `string` | Yes | The Facebook Ad Account ID (without act_ prefix) |
| `fields` | `string` | No | Comma-separated list of fields to return |
| `limit` | `integer` | No | Maximum number of results to return |
| `after` | `string` | No | Cursor for pagination |


<details>
<summary><b>Response Schema</b></summary>

#### Records

| Field Name | Type | Description |
|------------|------|-------------|
| `id` | `string` |  |
| `name` | `string \| null` |  |
| `account_id` | `string \| null` |  |
| `actor_id` | `string \| null` |  |
| `body` | `string \| null` |  |
| `call_to_action_type` | `string \| null` |  |
| `effective_object_story_id` | `string \| null` |  |
| `image_hash` | `string \| null` |  |
| `image_url` | `string \| null` |  |
| `link_url` | `string \| null` |  |
| `object_story_id` | `string \| null` |  |
| `object_story_spec` | `object \| null` |  |
| `object_type` | `string \| null` |  |
| `status` | `string \| null` |  |
| `thumbnail_url` | `string \| null` |  |
| `title` | `string \| null` |  |
| `url_tags` | `string \| null` |  |


#### Meta

| Field Name | Type | Description |
|------------|------|-------------|
| `after` | `string \| null` |  |

</details>

### Ad Creatives Search

Search and filter ad creatives records powered by Airbyte's data sync. This often provides additional fields and operators beyond what the API natively supports, making it easier to narrow down results before performing further operations. Only available in hosted mode.

#### Python SDK

```python
await facebook_marketing.ad_creatives.search(
    query={"filter": {"eq": {"id": "<str>"}}}
)
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/connectors/sources/{your_source_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "ad_creatives",
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
| `cursor` | `string` | No | Pagination cursor from previous response's next_cursor |
| `fields` | `array` | No | Field paths to include in results |

#### Searchable Fields

| Field Name | Type | Description |
|------------|------|-------------|
| `id` | `string` | Ad Creative ID |
| `name` | `string` | Ad Creative name |
| `account_id` | `string` | Ad account ID |
| `body` | `string` | Ad body text |
| `title` | `string` | Ad title |
| `status` | `string` | Creative status |
| `image_url` | `string` | Image URL |
| `thumbnail_url` | `string` | Thumbnail URL |
| `link_url` | `string` | Link URL |
| `call_to_action_type` | `string` | Call to action type |

<details>
<summary><b>Response Schema</b></summary>

| Field Name | Type | Description |
|------------|------|-------------|
| `hits` | `array` | List of matching records |
| `hits[].id` | `string` | Record identifier |
| `hits[].score` | `number` | Relevance score |
| `hits[].data` | `object` | Record data containing the searchable fields listed above |
| `hits[].data.id` | `string` | Ad Creative ID |
| `hits[].data.name` | `string` | Ad Creative name |
| `hits[].data.account_id` | `string` | Ad account ID |
| `hits[].data.body` | `string` | Ad body text |
| `hits[].data.title` | `string` | Ad title |
| `hits[].data.status` | `string` | Creative status |
| `hits[].data.image_url` | `string` | Image URL |
| `hits[].data.thumbnail_url` | `string` | Thumbnail URL |
| `hits[].data.link_url` | `string` | Link URL |
| `hits[].data.call_to_action_type` | `string` | Call to action type |
| `next_cursor` | `string \| null` | Cursor for next page of results |
| `took_ms` | `number` | Query execution time in milliseconds |

</details>

## Ads Insights

### Ads Insights List

Returns performance insights for the specified ad account

#### Python SDK

```python
await facebook_marketing.ads_insights.list(
    account_id="<str>"
)
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/connectors/sources/{your_source_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "ads_insights",
    "action": "list",
    "params": {
        "account_id": "<str>"
    }
}'
```


#### Parameters

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `account_id` | `string` | Yes | The Facebook Ad Account ID (without act_ prefix) |
| `fields` | `string` | No | Comma-separated list of fields to return |
| `date_preset` | `"today" \| "yesterday" \| "this_month" \| "last_month" \| "this_quarter" \| "maximum" \| "last_3d" \| "last_7d" \| "last_14d" \| "last_28d" \| "last_30d" \| "last_90d" \| "last_week_mon_sun" \| "last_week_sun_sat" \| "last_quarter" \| "last_year" \| "this_week_mon_today" \| "this_week_sun_today" \| "this_year"` | No | Predefined date range |
| `time_range` | `string` | No | Time range as JSON object with since and until dates (YYYY-MM-DD) |
| `level` | `"ad" \| "adset" \| "campaign" \| "account"` | No | Level of aggregation |
| `limit` | `integer` | No | Maximum number of results to return |
| `after` | `string` | No | Cursor for pagination |


<details>
<summary><b>Response Schema</b></summary>

#### Records

| Field Name | Type | Description |
|------------|------|-------------|
| `account_id` | `string \| null` |  |
| `account_name` | `string \| null` |  |
| `campaign_id` | `string \| null` |  |
| `campaign_name` | `string \| null` |  |
| `adset_id` | `string \| null` |  |
| `adset_name` | `string \| null` |  |
| `ad_id` | `string \| null` |  |
| `ad_name` | `string \| null` |  |
| `clicks` | `integer \| null` |  |
| `impressions` | `integer \| null` |  |
| `reach` | `integer \| null` |  |
| `spend` | `number \| null` |  |
| `cpc` | `number \| null` |  |
| `cpm` | `number \| null` |  |
| `ctr` | `number \| null` |  |
| `date_start` | `string \| null` |  |
| `date_stop` | `string \| null` |  |


#### Meta

| Field Name | Type | Description |
|------------|------|-------------|
| `after` | `string \| null` |  |

</details>

### Ads Insights Search

Search and filter ads insights records powered by Airbyte's data sync. This often provides additional fields and operators beyond what the API natively supports, making it easier to narrow down results before performing further operations. Only available in hosted mode.

#### Python SDK

```python
await facebook_marketing.ads_insights.search(
    query={"filter": {"eq": {"account_id": "<str>"}}}
)
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/connectors/sources/{your_source_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "ads_insights",
    "action": "search",
    "params": {
        "query": {"filter": {"eq": {"account_id": "<str>"}}}
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
| `cursor` | `string` | No | Pagination cursor from previous response's next_cursor |
| `fields` | `array` | No | Field paths to include in results |

#### Searchable Fields

| Field Name | Type | Description |
|------------|------|-------------|
| `account_id` | `string` | Ad account ID |
| `account_name` | `string` | Ad account name |
| `campaign_id` | `string` | Campaign ID |
| `campaign_name` | `string` | Campaign name |
| `adset_id` | `string` | Ad set ID |
| `adset_name` | `string` | Ad set name |
| `ad_id` | `string` | Ad ID |
| `ad_name` | `string` | Ad name |
| `clicks` | `integer` | Number of clicks |
| `impressions` | `integer` | Number of impressions |
| `reach` | `integer` | Number of unique people reached |
| `spend` | `number` | Amount spent |
| `cpc` | `number` | Cost per click |
| `cpm` | `number` | Cost per 1000 impressions |
| `ctr` | `number` | Click-through rate |
| `date_start` | `string` | Start date of the reporting period |
| `date_stop` | `string` | End date of the reporting period |

<details>
<summary><b>Response Schema</b></summary>

| Field Name | Type | Description |
|------------|------|-------------|
| `hits` | `array` | List of matching records |
| `hits[].id` | `string` | Record identifier |
| `hits[].score` | `number` | Relevance score |
| `hits[].data` | `object` | Record data containing the searchable fields listed above |
| `hits[].data.account_id` | `string` | Ad account ID |
| `hits[].data.account_name` | `string` | Ad account name |
| `hits[].data.campaign_id` | `string` | Campaign ID |
| `hits[].data.campaign_name` | `string` | Campaign name |
| `hits[].data.adset_id` | `string` | Ad set ID |
| `hits[].data.adset_name` | `string` | Ad set name |
| `hits[].data.ad_id` | `string` | Ad ID |
| `hits[].data.ad_name` | `string` | Ad name |
| `hits[].data.clicks` | `integer` | Number of clicks |
| `hits[].data.impressions` | `integer` | Number of impressions |
| `hits[].data.reach` | `integer` | Number of unique people reached |
| `hits[].data.spend` | `number` | Amount spent |
| `hits[].data.cpc` | `number` | Cost per click |
| `hits[].data.cpm` | `number` | Cost per 1000 impressions |
| `hits[].data.ctr` | `number` | Click-through rate |
| `hits[].data.date_start` | `string` | Start date of the reporting period |
| `hits[].data.date_stop` | `string` | End date of the reporting period |
| `next_cursor` | `string \| null` | Cursor for next page of results |
| `took_ms` | `number` | Query execution time in milliseconds |

</details>

## Custom Conversions

### Custom Conversions List

Returns a list of custom conversions for the specified ad account

#### Python SDK

```python
await facebook_marketing.custom_conversions.list(
    account_id="<str>"
)
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/connectors/sources/{your_source_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "custom_conversions",
    "action": "list",
    "params": {
        "account_id": "<str>"
    }
}'
```


#### Parameters

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `account_id` | `string` | Yes | The Facebook Ad Account ID (without act_ prefix) |
| `fields` | `string` | No | Comma-separated list of fields to return |
| `limit` | `integer` | No | Maximum number of results to return |
| `after` | `string` | No | Cursor for pagination |


<details>
<summary><b>Response Schema</b></summary>

#### Records

| Field Name | Type | Description |
|------------|------|-------------|
| `id` | `string` |  |
| `name` | `string \| null` |  |
| `account_id` | `string \| null` |  |
| `business` | `string \| null` |  |
| `creation_time` | `string \| null` |  |
| `custom_event_type` | `string \| null` |  |
| `data_sources` | `array \| null` |  |
| `data_sources[].id` | `string \| null` |  |
| `data_sources[].source_type` | `string \| null` |  |
| `data_sources[].name` | `string \| null` |  |
| `default_conversion_value` | `number \| null` |  |
| `description` | `string \| null` |  |
| `event_source_type` | `string \| null` |  |
| `first_fired_time` | `string \| null` |  |
| `is_archived` | `boolean \| null` |  |
| `is_unavailable` | `boolean \| null` |  |
| `last_fired_time` | `string \| null` |  |
| `offline_conversion_data_set` | `string \| null` |  |
| `retention_days` | `number \| null` |  |
| `rule` | `string \| null` |  |


#### Meta

| Field Name | Type | Description |
|------------|------|-------------|
| `after` | `string \| null` |  |

</details>

### Custom Conversions Search

Search and filter custom conversions records powered by Airbyte's data sync. This often provides additional fields and operators beyond what the API natively supports, making it easier to narrow down results before performing further operations. Only available in hosted mode.

#### Python SDK

```python
await facebook_marketing.custom_conversions.search(
    query={"filter": {"eq": {"id": "<str>"}}}
)
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/connectors/sources/{your_source_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "custom_conversions",
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
| `cursor` | `string` | No | Pagination cursor from previous response's next_cursor |
| `fields` | `array` | No | Field paths to include in results |

#### Searchable Fields

| Field Name | Type | Description |
|------------|------|-------------|
| `id` | `string` | Custom Conversion ID |
| `name` | `string` | Custom Conversion name |
| `account_id` | `string` | Ad account ID |
| `description` | `string` | Description |
| `custom_event_type` | `string` | Custom event type |
| `creation_time` | `string` | Creation time |
| `first_fired_time` | `string` | First fired time |
| `last_fired_time` | `string` | Last fired time |
| `is_archived` | `boolean` | Whether the conversion is archived |

<details>
<summary><b>Response Schema</b></summary>

| Field Name | Type | Description |
|------------|------|-------------|
| `hits` | `array` | List of matching records |
| `hits[].id` | `string` | Record identifier |
| `hits[].score` | `number` | Relevance score |
| `hits[].data` | `object` | Record data containing the searchable fields listed above |
| `hits[].data.id` | `string` | Custom Conversion ID |
| `hits[].data.name` | `string` | Custom Conversion name |
| `hits[].data.account_id` | `string` | Ad account ID |
| `hits[].data.description` | `string` | Description |
| `hits[].data.custom_event_type` | `string` | Custom event type |
| `hits[].data.creation_time` | `string` | Creation time |
| `hits[].data.first_fired_time` | `string` | First fired time |
| `hits[].data.last_fired_time` | `string` | Last fired time |
| `hits[].data.is_archived` | `boolean` | Whether the conversion is archived |
| `next_cursor` | `string \| null` | Cursor for next page of results |
| `took_ms` | `number` | Query execution time in milliseconds |

</details>

## Images

### Images List

Returns a list of ad images for the specified ad account

#### Python SDK

```python
await facebook_marketing.images.list(
    account_id="<str>"
)
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/connectors/sources/{your_source_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "images",
    "action": "list",
    "params": {
        "account_id": "<str>"
    }
}'
```


#### Parameters

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `account_id` | `string` | Yes | The Facebook Ad Account ID (without act_ prefix) |
| `fields` | `string` | No | Comma-separated list of fields to return |
| `limit` | `integer` | No | Maximum number of results to return |
| `after` | `string` | No | Cursor for pagination |


<details>
<summary><b>Response Schema</b></summary>

#### Records

| Field Name | Type | Description |
|------------|------|-------------|
| `id` | `string \| null` |  |
| `name` | `string \| null` |  |
| `account_id` | `string \| null` |  |
| `created_time` | `string \| null` |  |
| `creatives` | `array \| null` |  |
| `filename` | `string \| null` |  |
| `hash` | `string \| null` |  |
| `height` | `integer \| null` |  |
| `is_associated_creatives_in_adgroups` | `boolean \| null` |  |
| `original_height` | `integer \| null` |  |
| `original_width` | `integer \| null` |  |
| `permalink_url` | `string \| null` |  |
| `status` | `string \| null` |  |
| `updated_time` | `string \| null` |  |
| `url` | `string \| null` |  |
| `url_128` | `string \| null` |  |
| `width` | `integer \| null` |  |


#### Meta

| Field Name | Type | Description |
|------------|------|-------------|
| `after` | `string \| null` |  |

</details>

### Images Search

Search and filter images records powered by Airbyte's data sync. This often provides additional fields and operators beyond what the API natively supports, making it easier to narrow down results before performing further operations. Only available in hosted mode.

#### Python SDK

```python
await facebook_marketing.images.search(
    query={"filter": {"eq": {"id": "<str>"}}}
)
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/connectors/sources/{your_source_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "images",
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
| `cursor` | `string` | No | Pagination cursor from previous response's next_cursor |
| `fields` | `array` | No | Field paths to include in results |

#### Searchable Fields

| Field Name | Type | Description |
|------------|------|-------------|
| `id` | `string` | Image ID |
| `name` | `string` | Image name |
| `account_id` | `string` | Ad account ID |
| `hash` | `string` | Image hash |
| `url` | `string` | Image URL |
| `permalink_url` | `string` | Permalink URL |
| `width` | `integer` | Image width |
| `height` | `integer` | Image height |
| `status` | `string` | Image status |
| `created_time` | `string` | Creation time |
| `updated_time` | `string` | Last update time |

<details>
<summary><b>Response Schema</b></summary>

| Field Name | Type | Description |
|------------|------|-------------|
| `hits` | `array` | List of matching records |
| `hits[].id` | `string` | Record identifier |
| `hits[].score` | `number` | Relevance score |
| `hits[].data` | `object` | Record data containing the searchable fields listed above |
| `hits[].data.id` | `string` | Image ID |
| `hits[].data.name` | `string` | Image name |
| `hits[].data.account_id` | `string` | Ad account ID |
| `hits[].data.hash` | `string` | Image hash |
| `hits[].data.url` | `string` | Image URL |
| `hits[].data.permalink_url` | `string` | Permalink URL |
| `hits[].data.width` | `integer` | Image width |
| `hits[].data.height` | `integer` | Image height |
| `hits[].data.status` | `string` | Image status |
| `hits[].data.created_time` | `string` | Creation time |
| `hits[].data.updated_time` | `string` | Last update time |
| `next_cursor` | `string \| null` | Cursor for next page of results |
| `took_ms` | `number` | Query execution time in milliseconds |

</details>

## Videos

### Videos List

Returns a list of ad videos for the specified ad account

#### Python SDK

```python
await facebook_marketing.videos.list(
    account_id="<str>"
)
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/connectors/sources/{your_source_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "videos",
    "action": "list",
    "params": {
        "account_id": "<str>"
    }
}'
```


#### Parameters

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `account_id` | `string` | Yes | The Facebook Ad Account ID (without act_ prefix) |
| `fields` | `string` | No | Comma-separated list of fields to return |
| `limit` | `integer` | No | Maximum number of results to return |
| `after` | `string` | No | Cursor for pagination |


<details>
<summary><b>Response Schema</b></summary>

#### Records

| Field Name | Type | Description |
|------------|------|-------------|
| `id` | `string` |  |
| `title` | `string \| null` |  |
| `account_id` | `string \| null` |  |
| `ad_breaks` | `array \| null` |  |
| `backdated_time` | `string \| null` |  |
| `backdated_time_granularity` | `string \| null` |  |
| `content_category` | `string \| null` |  |
| `content_tags` | `array \| null` |  |
| `created_time` | `string \| null` |  |
| `custom_labels` | `array \| null` |  |
| `description` | `string \| null` |  |
| `embed_html` | `string \| null` |  |
| `embeddable` | `boolean \| null` |  |
| `format` | `array \| null` |  |
| `format[].filter` | `string \| null` |  |
| `format[].embed_html` | `string \| null` |  |
| `format[].width` | `integer \| null` |  |
| `format[].height` | `integer \| null` |  |
| `format[].picture` | `string \| null` |  |
| `icon` | `string \| null` |  |
| `is_crosspost_video` | `boolean \| null` |  |
| `is_crossposting_eligible` | `boolean \| null` |  |
| `is_episode` | `boolean \| null` |  |
| `is_instagram_eligible` | `boolean \| null` |  |
| `length` | `number \| null` |  |
| `live_status` | `string \| null` |  |
| `permalink_url` | `string \| null` |  |
| `post_views` | `integer \| null` |  |
| `premiere_living_room_status` | `boolean \| null` |  |
| `published` | `boolean \| null` |  |
| `scheduled_publish_time` | `string \| null` |  |
| `source` | `string \| null` |  |
| `universal_video_id` | `string \| null` |  |
| `updated_time` | `string \| null` |  |
| `views` | `integer \| null` |  |


#### Meta

| Field Name | Type | Description |
|------------|------|-------------|
| `after` | `string \| null` |  |

</details>

### Videos Search

Search and filter videos records powered by Airbyte's data sync. This often provides additional fields and operators beyond what the API natively supports, making it easier to narrow down results before performing further operations. Only available in hosted mode.

#### Python SDK

```python
await facebook_marketing.videos.search(
    query={"filter": {"eq": {"id": "<str>"}}}
)
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/connectors/sources/{your_source_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "videos",
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
| `cursor` | `string` | No | Pagination cursor from previous response's next_cursor |
| `fields` | `array` | No | Field paths to include in results |

#### Searchable Fields

| Field Name | Type | Description |
|------------|------|-------------|
| `id` | `string` | Video ID |
| `title` | `string` | Video title |
| `account_id` | `string` | Ad account ID |
| `description` | `string` | Video description |
| `length` | `number` | Video length in seconds |
| `source` | `string` | Video source URL |
| `permalink_url` | `string` | Permalink URL |
| `views` | `integer` | Number of views |
| `created_time` | `string` | Creation time |
| `updated_time` | `string` | Last update time |

<details>
<summary><b>Response Schema</b></summary>

| Field Name | Type | Description |
|------------|------|-------------|
| `hits` | `array` | List of matching records |
| `hits[].id` | `string` | Record identifier |
| `hits[].score` | `number` | Relevance score |
| `hits[].data` | `object` | Record data containing the searchable fields listed above |
| `hits[].data.id` | `string` | Video ID |
| `hits[].data.title` | `string` | Video title |
| `hits[].data.account_id` | `string` | Ad account ID |
| `hits[].data.description` | `string` | Video description |
| `hits[].data.length` | `number` | Video length in seconds |
| `hits[].data.source` | `string` | Video source URL |
| `hits[].data.permalink_url` | `string` | Permalink URL |
| `hits[].data.views` | `integer` | Number of views |
| `hits[].data.created_time` | `string` | Creation time |
| `hits[].data.updated_time` | `string` | Last update time |
| `next_cursor` | `string \| null` | Cursor for next page of results |
| `took_ms` | `number` | Query execution time in milliseconds |

</details>

