# Tiktok-Marketing full reference

This is the full reference documentation for the Tiktok-Marketing agent connector.

## Supported entities and actions

The Tiktok-Marketing connector supports the following entities and actions.

| Entity | Actions |
|--------|---------|
| Advertisers | [List](#advertisers-list), [Search](#advertisers-search) |
| Campaigns | [List](#campaigns-list), [Search](#campaigns-search) |
| Ad Groups | [List](#ad-groups-list), [Search](#ad-groups-search) |
| Ads | [List](#ads-list), [Search](#ads-search) |
| Audiences | [List](#audiences-list), [Search](#audiences-search) |
| Creative Assets Images | [List](#creative-assets-images-list), [Search](#creative-assets-images-search) |
| Creative Assets Videos | [List](#creative-assets-videos-list), [Search](#creative-assets-videos-search) |

## Advertisers

### Advertisers List

Get advertiser account information

#### Python SDK

```python
await tiktok_marketing.advertisers.list(
    advertiser_ids="<str>"
)
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/integrations/connectors/{your_connector_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "advertisers",
    "action": "list",
    "params": {
        "advertiser_ids": "<str>"
    }
}'
```


#### Parameters

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `advertiser_ids` | `string` | Yes | Advertiser IDs (JSON array of strings) |
| `page` | `integer` | No | Page number |
| `page_size` | `integer` | No | Number of items per page |


<details>
<summary><b>Response Schema</b></summary>

#### Records

| Field Name | Type | Description |
|------------|------|-------------|
| `advertiser_id` | `string` |  |
| `name` | `string` |  |
| `address` | `null \| string` |  |
| `company` | `null \| string` |  |
| `contacter` | `null \| string` |  |
| `country` | `null \| string` |  |
| `currency` | `null \| string` |  |
| `description` | `null \| string` |  |
| `email` | `null \| string` |  |
| `industry` | `null \| string` |  |
| `language` | `null \| string` |  |
| `license_no` | `null \| string` |  |
| `license_url` | `null \| string` |  |
| `cellphone_number` | `null \| string` |  |
| `promotion_area` | `null \| string` |  |
| `rejection_reason` | `null \| string` |  |
| `role` | `null \| string` |  |
| `status` | `null \| string` |  |
| `timezone` | `null \| string` |  |
| `balance` | `number` |  |
| `create_time` | `integer` |  |
| `telephone_number` | `null \| string` |  |
| `display_timezone` | `null \| string` |  |
| `promotion_center_province` | `null \| string` |  |
| `advertiser_account_type` | `null \| string` |  |
| `license_city` | `null \| string` |  |
| `brand` | `null \| string` |  |
| `license_province` | `null \| string` |  |
| `promotion_center_city` | `null \| string` |  |


</details>

### Advertisers Search

Search and filter advertisers records powered by Airbyte's data sync. This often provides additional fields and operators beyond what the API natively supports, making it easier to narrow down results before performing further operations. Only available in hosted mode.

#### Python SDK

```python
await tiktok_marketing.advertisers.search(
    query={"filter": {"eq": {"address": "<str>"}}}
)
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/integrations/connectors/{your_connector_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "advertisers",
    "action": "search",
    "params": {
        "query": {"filter": {"eq": {"address": "<str>"}}}
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
| `address` | `string` | The physical address of the advertiser. |
| `advertiser_account_type` | `string` | The type of advertiser's account (e.g., individual, business). |
| `advertiser_id` | `integer` | Unique identifier for the advertiser. |
| `balance` | `number` | The current balance in the advertiser's account. |
| `brand` | `string` | The brand name associated with the advertiser. |
| `cellphone_number` | `string` | The cellphone number of the advertiser. |
| `company` | `string` | The name of the company associated with the advertiser. |
| `contacter` | `string` | The contact person for the advertiser. |
| `country` | `string` | The country where the advertiser is located. |
| `create_time` | `integer` | The timestamp when the advertiser account was created. |
| `currency` | `string` | The currency used for transactions in the account. |
| `description` | `string` | A brief description or bio of the advertiser or company. |
| `display_timezone` | `string` | The timezone for display purposes. |
| `email` | `string` | The email address associated with the advertiser. |
| `industry` | `string` | The industry or sector the advertiser operates in. |
| `language` | `string` | The preferred language of communication for the advertiser. |
| `license_city` | `string` | The city where the advertiser's license is registered. |
| `license_no` | `string` | The license number of the advertiser. |
| `license_province` | `string` | The province or state where the advertiser's license is registered. |
| `license_url` | `string` | The URL link to the advertiser's license documentation. |
| `name` | `string` | The name of the advertiser or company. |
| `promotion_area` | `string` | The specific area or region where the advertiser focuses promotion. |
| `promotion_center_city` | `string` | The city at the center of the advertiser's promotion activities. |
| `promotion_center_province` | `string` | The province or state at the center of the advertiser's promotion activities. |
| `rejection_reason` | `string` | Reason for any advertisement rejection by the platform. |
| `role` | `string` | The role or position of the advertiser within the company. |
| `status` | `string` | The current status of the advertiser's account. |
| `telephone_number` | `string` | The telephone number of the advertiser. |
| `timezone` | `string` | The timezone setting for the advertiser's activities. |

<details>
<summary><b>Response Schema</b></summary>

| Field Name | Type | Description |
|------------|------|-------------|
| `data` | `array` | List of matching records |
| `meta` | `object` | Pagination metadata |
| `meta.has_more` | `boolean` | Whether additional pages are available |
| `meta.cursor` | `string \| null` | Cursor for next page of results |
| `meta.took_ms` | `number \| null` | Query execution time in milliseconds |
| `data[].address` | `string` | The physical address of the advertiser. |
| `data[].advertiser_account_type` | `string` | The type of advertiser's account (e.g., individual, business). |
| `data[].advertiser_id` | `integer` | Unique identifier for the advertiser. |
| `data[].balance` | `number` | The current balance in the advertiser's account. |
| `data[].brand` | `string` | The brand name associated with the advertiser. |
| `data[].cellphone_number` | `string` | The cellphone number of the advertiser. |
| `data[].company` | `string` | The name of the company associated with the advertiser. |
| `data[].contacter` | `string` | The contact person for the advertiser. |
| `data[].country` | `string` | The country where the advertiser is located. |
| `data[].create_time` | `integer` | The timestamp when the advertiser account was created. |
| `data[].currency` | `string` | The currency used for transactions in the account. |
| `data[].description` | `string` | A brief description or bio of the advertiser or company. |
| `data[].display_timezone` | `string` | The timezone for display purposes. |
| `data[].email` | `string` | The email address associated with the advertiser. |
| `data[].industry` | `string` | The industry or sector the advertiser operates in. |
| `data[].language` | `string` | The preferred language of communication for the advertiser. |
| `data[].license_city` | `string` | The city where the advertiser's license is registered. |
| `data[].license_no` | `string` | The license number of the advertiser. |
| `data[].license_province` | `string` | The province or state where the advertiser's license is registered. |
| `data[].license_url` | `string` | The URL link to the advertiser's license documentation. |
| `data[].name` | `string` | The name of the advertiser or company. |
| `data[].promotion_area` | `string` | The specific area or region where the advertiser focuses promotion. |
| `data[].promotion_center_city` | `string` | The city at the center of the advertiser's promotion activities. |
| `data[].promotion_center_province` | `string` | The province or state at the center of the advertiser's promotion activities. |
| `data[].rejection_reason` | `string` | Reason for any advertisement rejection by the platform. |
| `data[].role` | `string` | The role or position of the advertiser within the company. |
| `data[].status` | `string` | The current status of the advertiser's account. |
| `data[].telephone_number` | `string` | The telephone number of the advertiser. |
| `data[].timezone` | `string` | The timezone setting for the advertiser's activities. |

</details>

## Campaigns

### Campaigns List

Get campaigns for an advertiser

#### Python SDK

```python
await tiktok_marketing.campaigns.list(
    advertiser_id="<str>"
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
        "advertiser_id": "<str>"
    }
}'
```


#### Parameters

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `advertiser_id` | `string` | Yes | Advertiser ID |
| `page` | `integer` | No | Page number |
| `page_size` | `integer` | No | Number of items per page |


<details>
<summary><b>Response Schema</b></summary>

#### Records

| Field Name | Type | Description |
|------------|------|-------------|
| `campaign_id` | `string` |  |
| `campaign_name` | `string` |  |
| `campaign_type` | `string` |  |
| `advertiser_id` | `string` |  |
| `budget` | `number` |  |
| `budget_mode` | `string` |  |
| `secondary_status` | `string` |  |
| `operation_status` | `null \| string` |  |
| `objective` | `null \| string` |  |
| `objective_type` | `null \| string` |  |
| `budget_optimize_on` | `null \| boolean` |  |
| `bid_type` | `null \| string` |  |
| `deep_bid_type` | `null \| string` |  |
| `optimization_goal` | `null \| string` |  |
| `split_test_variable` | `null \| string` |  |
| `is_new_structure` | `boolean` |  |
| `create_time` | `string` |  |
| `modify_time` | `string` |  |
| `roas_bid` | `null \| number` |  |
| `is_smart_performance_campaign` | `null \| boolean` |  |
| `is_search_campaign` | `null \| boolean` |  |
| `app_promotion_type` | `null \| string` |  |
| `rf_campaign_type` | `null \| string` |  |
| `disable_skan_campaign` | `null \| boolean` |  |
| `is_advanced_dedicated_campaign` | `null \| boolean` |  |
| `rta_id` | `null \| string` |  |
| `campaign_automation_type` | `null \| string` |  |
| `rta_bid_enabled` | `null \| boolean` |  |
| `rta_product_selection_enabled` | `null \| boolean` |  |


#### Meta

| Field Name | Type | Description |
|------------|------|-------------|
| `page_info` | `object` |  |

</details>

### Campaigns Search

Search and filter campaigns records powered by Airbyte's data sync. This often provides additional fields and operators beyond what the API natively supports, making it easier to narrow down results before performing further operations. Only available in hosted mode.

#### Python SDK

```python
await tiktok_marketing.campaigns.search(
    query={"filter": {"eq": {"advertiser_id": 0}}}
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
        "query": {"filter": {"eq": {"advertiser_id": 0}}}
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
| `advertiser_id` | `integer` | The unique identifier of the advertiser associated with the campaign |
| `app_promotion_type` | `string` | Type of app promotion being used in the campaign |
| `bid_type` | `string` | Type of bid strategy being used in the campaign |
| `budget` | `number` | Total budget allocated for the campaign |
| `budget_mode` | `string` | Mode in which the budget is being managed (e.g., daily, lifetime) |
| `budget_optimize_on` | `boolean` | The metric or event that the budget optimization is based on |
| `campaign_id` | `integer` | The unique identifier of the campaign |
| `campaign_name` | `string` | Name of the campaign for easy identification |
| `campaign_type` | `string` | Type of campaign (e.g., awareness, conversion) |
| `create_time` | `string` | Timestamp when the campaign was created |
| `deep_bid_type` | `string` | Advanced bid type used for campaign optimization |
| `is_new_structure` | `boolean` | Flag indicating if the campaign utilizes a new campaign structure |
| `is_search_campaign` | `boolean` | Flag indicating if the campaign is a search campaign |
| `is_smart_performance_campaign` | `boolean` | Flag indicating if the campaign uses smart performance optimization |
| `modify_time` | `string` | Timestamp when the campaign was last modified |
| `objective` | `string` | The objective or goal of the campaign |
| `objective_type` | `string` | Type of objective selected for the campaign |
| `operation_status` | `string` | Current operational status of the campaign |
| `optimization_goal` | `string` | Specific goal to be optimized for in the campaign |
| `rf_campaign_type` | `string` | Type of RF (reach and frequency) campaign being run |
| `roas_bid` | `number` | Return on ad spend goal set for the campaign |
| `secondary_status` | `string` | Additional status information of the campaign |
| `split_test_variable` | `string` | Variable being tested in a split test campaign |

<details>
<summary><b>Response Schema</b></summary>

| Field Name | Type | Description |
|------------|------|-------------|
| `data` | `array` | List of matching records |
| `meta` | `object` | Pagination metadata |
| `meta.has_more` | `boolean` | Whether additional pages are available |
| `meta.cursor` | `string \| null` | Cursor for next page of results |
| `meta.took_ms` | `number \| null` | Query execution time in milliseconds |
| `data[].advertiser_id` | `integer` | The unique identifier of the advertiser associated with the campaign |
| `data[].app_promotion_type` | `string` | Type of app promotion being used in the campaign |
| `data[].bid_type` | `string` | Type of bid strategy being used in the campaign |
| `data[].budget` | `number` | Total budget allocated for the campaign |
| `data[].budget_mode` | `string` | Mode in which the budget is being managed (e.g., daily, lifetime) |
| `data[].budget_optimize_on` | `boolean` | The metric or event that the budget optimization is based on |
| `data[].campaign_id` | `integer` | The unique identifier of the campaign |
| `data[].campaign_name` | `string` | Name of the campaign for easy identification |
| `data[].campaign_type` | `string` | Type of campaign (e.g., awareness, conversion) |
| `data[].create_time` | `string` | Timestamp when the campaign was created |
| `data[].deep_bid_type` | `string` | Advanced bid type used for campaign optimization |
| `data[].is_new_structure` | `boolean` | Flag indicating if the campaign utilizes a new campaign structure |
| `data[].is_search_campaign` | `boolean` | Flag indicating if the campaign is a search campaign |
| `data[].is_smart_performance_campaign` | `boolean` | Flag indicating if the campaign uses smart performance optimization |
| `data[].modify_time` | `string` | Timestamp when the campaign was last modified |
| `data[].objective` | `string` | The objective or goal of the campaign |
| `data[].objective_type` | `string` | Type of objective selected for the campaign |
| `data[].operation_status` | `string` | Current operational status of the campaign |
| `data[].optimization_goal` | `string` | Specific goal to be optimized for in the campaign |
| `data[].rf_campaign_type` | `string` | Type of RF (reach and frequency) campaign being run |
| `data[].roas_bid` | `number` | Return on ad spend goal set for the campaign |
| `data[].secondary_status` | `string` | Additional status information of the campaign |
| `data[].split_test_variable` | `string` | Variable being tested in a split test campaign |

</details>

## Ad Groups

### Ad Groups List

Get ad groups for an advertiser

#### Python SDK

```python
await tiktok_marketing.ad_groups.list(
    advertiser_id="<str>"
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
        "advertiser_id": "<str>"
    }
}'
```


#### Parameters

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `advertiser_id` | `string` | Yes | Advertiser ID |
| `page` | `integer` | No | Page number |
| `page_size` | `integer` | No | Number of items per page |


<details>
<summary><b>Response Schema</b></summary>

#### Records

| Field Name | Type | Description |
|------------|------|-------------|
| `adgroup_id` | `string` |  |
| `campaign_id` | `string` |  |
| `advertiser_id` | `string` |  |
| `adgroup_name` | `string` |  |
| `placement_type` | `string` |  |
| `placements` | `null \| array` |  |
| `budget` | `number` |  |
| `budget_mode` | `string` |  |
| `secondary_status` | `string` |  |
| `operation_status` | `string` |  |
| `optimization_goal` | `string` |  |
| `bid_type` | `null \| string` |  |
| `bid_price` | `number` |  |
| `promotion_type` | `string` |  |
| `creative_material_mode` | `string` |  |
| `schedule_type` | `string` |  |
| `schedule_start_time` | `string` |  |
| `schedule_end_time` | `string` |  |
| `create_time` | `string` |  |
| `modify_time` | `string` |  |
| `gender` | `null \| string` |  |
| `age_groups` | `null \| array` |  |
| `languages` | `null \| array` |  |
| `location_ids` | `null \| array` |  |
| `audience_ids` | `null \| array` |  |
| `excluded_audience_ids` | `null \| array` |  |
| `interest_category_ids` | `null \| array` |  |
| `interest_keyword_ids` | `null \| array` |  |
| `pixel_id` | `null \| string` |  |
| `deep_bid_type` | `null \| string` |  |
| `deep_cpa_bid` | `number` |  |
| `conversion_bid_price` | `number` |  |
| `billing_event` | `null \| string` |  |
| `pacing` | `null \| string` |  |
| `dayparting` | `null \| string` |  |
| `frequency` | `null \| integer` |  |
| `frequency_schedule` | `null \| integer` |  |
| `is_new_structure` | `boolean` |  |
| `is_smart_performance_campaign` | `null \| boolean` |  |
| `app_id` | `null \| string` |  |
| `app_type` | `null \| string` |  |
| `app_download_url` | `null \| string` |  |
| `optimization_event` | `null \| string` |  |
| `secondary_optimization_event` | `null \| string` |  |
| `conversion_window` | `null \| string` |  |
| `comment_disabled` | `null \| boolean` |  |
| `video_download_disabled` | `null \| boolean` |  |
| `share_disabled` | `null \| boolean` |  |
| `auto_targeting_enabled` | `null \| boolean` |  |
| `is_hfss` | `null \| boolean` |  |
| `search_result_enabled` | `null \| boolean` |  |
| `inventory_filter_enabled` | `null \| boolean` |  |
| `skip_learning_phase` | `null \| boolean` |  |
| `brand_safety_type` | `null \| string` |  |
| `brand_safety_partner` | `null \| string` |  |
| `campaign_name` | `null \| string` |  |
| `campaign_automation_type` | `null \| string` |  |
| `bid_display_mode` | `null \| string` |  |
| `scheduled_budget` | `null \| number` |  |
| `category_id` | `null \| string` |  |
| `feed_type` | `null \| string` |  |
| `delivery_mode` | `null \| string` |  |
| `ios14_quota_type` | `null \| string` |  |
| `spending_power` | `null \| string` |  |
| `next_day_retention` | `null \| number` |  |
| `rf_purchased_type` | `null \| string` |  |
| `rf_estimated_cpr` | `null \| number` |  |
| `rf_estimated_frequency` | `null \| number` |  |
| `purchased_impression` | `null \| number` |  |
| `purchased_reach` | `null \| number` |  |
| `actions` | `null \| array` |  |
| `network_types` | `null \| array` |  |
| `operating_systems` | `null \| array` |  |
| `device_model_ids` | `null \| array` |  |
| `device_price_ranges` | `null \| array` |  |
| `included_custom_actions` | `null \| array` |  |
| `excluded_custom_actions` | `null \| array` |  |
| `category_exclusion_ids` | `null \| array` |  |
| `contextual_tag_ids` | `null \| array` |  |
| `zipcode_ids` | `null \| array` |  |
| `household_income` | `null \| array` |  |
| `isp_ids` | `null \| array` |  |
| `schedule_infos` | `null \| array` |  |
| `statistic_type` | `null \| string` |  |
| `keywords` | `null \| string` |  |
| `adgroup_app_profile_page_state` | `null \| string` |  |
| `automated_keywords_enabled` | `null \| boolean` |  |
| `smart_audience_enabled` | `null \| boolean` |  |
| `smart_interest_behavior_enabled` | `null \| boolean` |  |
| `vbo_window` | `null \| string` |  |
| `deep_funnel_optimization_status` | `null \| string` |  |
| `deep_funnel_event_source` | `null \| string` |  |
| `deep_funnel_event_source_id` | `null \| string` |  |
| `deep_funnel_optimization_event` | `null \| string` |  |
| `custom_conversion_id` | `null \| string` |  |
| `app_config` | `null \| object` |  |


#### Meta

| Field Name | Type | Description |
|------------|------|-------------|
| `page_info` | `object` |  |

</details>

### Ad Groups Search

Search and filter ad groups records powered by Airbyte's data sync. This often provides additional fields and operators beyond what the API natively supports, making it easier to narrow down results before performing further operations. Only available in hosted mode.

#### Python SDK

```python
await tiktok_marketing.ad_groups.search(
    query={"filter": {"eq": {"adgroup_id": 0}}}
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
        "query": {"filter": {"eq": {"adgroup_id": 0}}}
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
| `adgroup_id` | `integer` | The unique identifier of the ad group |
| `adgroup_name` | `string` | The name of the ad group |
| `advertiser_id` | `integer` | The unique identifier of the advertiser |
| `budget` | `number` | The allocated budget for the ad group |
| `budget_mode` | `string` | The mode for managing the budget |
| `campaign_id` | `integer` | The unique identifier of the campaign |
| `create_time` | `string` | The timestamp for when the ad group was created |
| `modify_time` | `string` | The timestamp for when the ad group was last modified |
| `operation_status` | `string` | The status of the operation |
| `optimization_goal` | `string` | The goal set for optimization |
| `placement_type` | `string` | The type of ad placement |
| `promotion_type` | `string` | The type of promotion |
| `secondary_status` | `string` | The secondary status of the ad group |

<details>
<summary><b>Response Schema</b></summary>

| Field Name | Type | Description |
|------------|------|-------------|
| `data` | `array` | List of matching records |
| `meta` | `object` | Pagination metadata |
| `meta.has_more` | `boolean` | Whether additional pages are available |
| `meta.cursor` | `string \| null` | Cursor for next page of results |
| `meta.took_ms` | `number \| null` | Query execution time in milliseconds |
| `data[].adgroup_id` | `integer` | The unique identifier of the ad group |
| `data[].adgroup_name` | `string` | The name of the ad group |
| `data[].advertiser_id` | `integer` | The unique identifier of the advertiser |
| `data[].budget` | `number` | The allocated budget for the ad group |
| `data[].budget_mode` | `string` | The mode for managing the budget |
| `data[].campaign_id` | `integer` | The unique identifier of the campaign |
| `data[].create_time` | `string` | The timestamp for when the ad group was created |
| `data[].modify_time` | `string` | The timestamp for when the ad group was last modified |
| `data[].operation_status` | `string` | The status of the operation |
| `data[].optimization_goal` | `string` | The goal set for optimization |
| `data[].placement_type` | `string` | The type of ad placement |
| `data[].promotion_type` | `string` | The type of promotion |
| `data[].secondary_status` | `string` | The secondary status of the ad group |

</details>

## Ads

### Ads List

Get ads for an advertiser

#### Python SDK

```python
await tiktok_marketing.ads.list(
    advertiser_id="<str>"
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
        "advertiser_id": "<str>"
    }
}'
```


#### Parameters

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `advertiser_id` | `string` | Yes | Advertiser ID |
| `page` | `integer` | No | Page number |
| `page_size` | `integer` | No | Number of items per page |


<details>
<summary><b>Response Schema</b></summary>

#### Records

| Field Name | Type | Description |
|------------|------|-------------|
| `ad_id` | `string` |  |
| `advertiser_id` | `string` |  |
| `campaign_id` | `string` |  |
| `campaign_name` | `string` |  |
| `adgroup_id` | `string` |  |
| `adgroup_name` | `string` |  |
| `ad_name` | `string` |  |
| `ad_text` | `null \| string` |  |
| `ad_texts` | `null \| array` |  |
| `ad_format` | `null \| string` |  |
| `secondary_status` | `string` |  |
| `operation_status` | `null \| string` |  |
| `call_to_action` | `null \| string` |  |
| `call_to_action_id` | `null \| string` |  |
| `landing_page_url` | `null \| string` |  |
| `landing_page_urls` | `null \| array` |  |
| `display_name` | `null \| string` |  |
| `profile_image_url` | `null \| string` |  |
| `video_id` | `null \| string` |  |
| `image_ids` | `null \| array` |  |
| `image_mode` | `null \| string` |  |
| `is_aco` | `null \| boolean` |  |
| `is_new_structure` | `null \| boolean` |  |
| `creative_type` | `null \| string` |  |
| `creative_authorized` | `null \| boolean` |  |
| `identity_id` | `null \| string` |  |
| `identity_type` | `null \| string` |  |
| `deeplink` | `null \| string` |  |
| `deeplink_type` | `null \| string` |  |
| `fallback_type` | `null \| string` |  |
| `tracking_pixel_id` | `null \| integer` |  |
| `impression_tracking_url` | `null \| string` |  |
| `click_tracking_url` | `null \| string` |  |
| `music_id` | `null \| string` |  |
| `optimization_event` | `null \| string` |  |
| `vast_moat_enabled` | `null \| boolean` |  |
| `page_id` | `null \| string` |  |
| `viewability_postbid_partner` | `null \| string` |  |
| `viewability_vast_url` | `null \| string` |  |
| `brand_safety_postbid_partner` | `null \| string` |  |
| `brand_safety_vast_url` | `null \| string` |  |
| `app_name` | `null \| string` |  |
| `playable_url` | `null \| string` |  |
| `card_id` | `null \| string` |  |
| `carousel_image_labels` | `null \| array` |  |
| `avatar_icon_web_uri` | `null \| string` |  |
| `campaign_automation_type` | `null \| string` |  |
| `create_time` | `string` |  |
| `modify_time` | `string` |  |


#### Meta

| Field Name | Type | Description |
|------------|------|-------------|
| `page_info` | `object` |  |

</details>

### Ads Search

Search and filter ads records powered by Airbyte's data sync. This often provides additional fields and operators beyond what the API natively supports, making it easier to narrow down results before performing further operations. Only available in hosted mode.

#### Python SDK

```python
await tiktok_marketing.ads.search(
    query={"filter": {"eq": {"ad_format": "<str>"}}}
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
        "query": {"filter": {"eq": {"ad_format": "<str>"}}}
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
| `ad_format` | `string` | The format of the ad |
| `ad_id` | `integer` | The unique identifier of the ad |
| `ad_name` | `string` | The name of the ad |
| `ad_text` | `string` | The text content of the ad |
| `adgroup_id` | `integer` | The unique identifier of the ad group |
| `adgroup_name` | `string` | The name of the ad group |
| `advertiser_id` | `integer` | The unique identifier of the advertiser |
| `campaign_id` | `integer` | The unique identifier of the campaign |
| `campaign_name` | `string` | The name of the campaign |
| `create_time` | `string` | The timestamp when the ad was created |
| `landing_page_url` | `string` | The URL of the landing page for the ad |
| `modify_time` | `string` | The timestamp when the ad was last modified |
| `operation_status` | `string` | The operational status of the ad |
| `secondary_status` | `string` | The secondary status of the ad |
| `video_id` | `string` | The unique identifier of the video |

<details>
<summary><b>Response Schema</b></summary>

| Field Name | Type | Description |
|------------|------|-------------|
| `data` | `array` | List of matching records |
| `meta` | `object` | Pagination metadata |
| `meta.has_more` | `boolean` | Whether additional pages are available |
| `meta.cursor` | `string \| null` | Cursor for next page of results |
| `meta.took_ms` | `number \| null` | Query execution time in milliseconds |
| `data[].ad_format` | `string` | The format of the ad |
| `data[].ad_id` | `integer` | The unique identifier of the ad |
| `data[].ad_name` | `string` | The name of the ad |
| `data[].ad_text` | `string` | The text content of the ad |
| `data[].adgroup_id` | `integer` | The unique identifier of the ad group |
| `data[].adgroup_name` | `string` | The name of the ad group |
| `data[].advertiser_id` | `integer` | The unique identifier of the advertiser |
| `data[].campaign_id` | `integer` | The unique identifier of the campaign |
| `data[].campaign_name` | `string` | The name of the campaign |
| `data[].create_time` | `string` | The timestamp when the ad was created |
| `data[].landing_page_url` | `string` | The URL of the landing page for the ad |
| `data[].modify_time` | `string` | The timestamp when the ad was last modified |
| `data[].operation_status` | `string` | The operational status of the ad |
| `data[].secondary_status` | `string` | The secondary status of the ad |
| `data[].video_id` | `string` | The unique identifier of the video |

</details>

## Audiences

### Audiences List

Get custom audiences for an advertiser

#### Python SDK

```python
await tiktok_marketing.audiences.list(
    advertiser_id="<str>"
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
        "advertiser_id": "<str>"
    }
}'
```


#### Parameters

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `advertiser_id` | `string` | Yes | Advertiser ID |
| `page` | `integer` | No | Page number |
| `page_size` | `integer` | No | Number of items per page |


<details>
<summary><b>Response Schema</b></summary>

#### Records

| Field Name | Type | Description |
|------------|------|-------------|
| `audience_id` | `null \| string` |  |
| `name` | `null \| string` |  |
| `audience_type` | `null \| string` |  |
| `cover_num` | `null \| integer` |  |
| `is_valid` | `null \| boolean` |  |
| `is_expiring` | `null \| boolean` |  |
| `is_creator` | `null \| boolean` |  |
| `shared` | `null \| boolean` |  |
| `calculate_type` | `null \| string` |  |
| `create_time` | `null \| string` |  |
| `expired_time` | `null \| string` |  |


#### Meta

| Field Name | Type | Description |
|------------|------|-------------|
| `page_info` | `object` |  |

</details>

### Audiences Search

Search and filter audiences records powered by Airbyte's data sync. This often provides additional fields and operators beyond what the API natively supports, making it easier to narrow down results before performing further operations. Only available in hosted mode.

#### Python SDK

```python
await tiktok_marketing.audiences.search(
    query={"filter": {"eq": {"audience_id": "<str>"}}}
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
        "query": {"filter": {"eq": {"audience_id": "<str>"}}}
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
| `audience_id` | `string` | Unique identifier for the audience |
| `audience_type` | `string` | Type of audience |
| `cover_num` | `integer` | Number of audience members covered |
| `create_time` | `string` | Timestamp indicating when the audience was created |
| `is_valid` | `boolean` | Flag indicating if the audience data is valid |
| `name` | `string` | Name of the audience |
| `shared` | `boolean` | Flag indicating if the audience is shared |

<details>
<summary><b>Response Schema</b></summary>

| Field Name | Type | Description |
|------------|------|-------------|
| `data` | `array` | List of matching records |
| `meta` | `object` | Pagination metadata |
| `meta.has_more` | `boolean` | Whether additional pages are available |
| `meta.cursor` | `string \| null` | Cursor for next page of results |
| `meta.took_ms` | `number \| null` | Query execution time in milliseconds |
| `data[].audience_id` | `string` | Unique identifier for the audience |
| `data[].audience_type` | `string` | Type of audience |
| `data[].cover_num` | `integer` | Number of audience members covered |
| `data[].create_time` | `string` | Timestamp indicating when the audience was created |
| `data[].is_valid` | `boolean` | Flag indicating if the audience data is valid |
| `data[].name` | `string` | Name of the audience |
| `data[].shared` | `boolean` | Flag indicating if the audience is shared |

</details>

## Creative Assets Images

### Creative Assets Images List

Search creative asset images for an advertiser

#### Python SDK

```python
await tiktok_marketing.creative_assets_images.list(
    advertiser_id="<str>"
)
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/integrations/connectors/{your_connector_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "creative_assets_images",
    "action": "list",
    "params": {
        "advertiser_id": "<str>"
    }
}'
```


#### Parameters

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `advertiser_id` | `string` | Yes | Advertiser ID |
| `page` | `integer` | No | Page number |
| `page_size` | `integer` | No | Number of items per page |


<details>
<summary><b>Response Schema</b></summary>

#### Records

| Field Name | Type | Description |
|------------|------|-------------|
| `image_id` | `null \| string` |  |
| `format` | `null \| string` |  |
| `image_url` | `null \| string` |  |
| `height` | `null \| integer` |  |
| `width` | `null \| integer` |  |
| `signature` | `null \| string` |  |
| `size` | `null \| integer` |  |
| `material_id` | `null \| string` |  |
| `is_carousel_usable` | `null \| boolean` |  |
| `file_name` | `null \| string` |  |
| `create_time` | `null \| string` |  |
| `modify_time` | `null \| string` |  |
| `displayable` | `null \| boolean` |  |


#### Meta

| Field Name | Type | Description |
|------------|------|-------------|
| `page_info` | `object` |  |

</details>

### Creative Assets Images Search

Search and filter creative assets images records powered by Airbyte's data sync. This often provides additional fields and operators beyond what the API natively supports, making it easier to narrow down results before performing further operations. Only available in hosted mode.

#### Python SDK

```python
await tiktok_marketing.creative_assets_images.search(
    query={"filter": {"eq": {"create_time": "<str>"}}}
)
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/integrations/connectors/{your_connector_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "creative_assets_images",
    "action": "search",
    "params": {
        "query": {"filter": {"eq": {"create_time": "<str>"}}}
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
| `create_time` | `string` | The timestamp when the image was created. |
| `file_name` | `string` | The name of the image file. |
| `format` | `string` | The format type of the image file. |
| `height` | `integer` | The height dimension of the image. |
| `image_id` | `string` | The unique identifier for the image. |
| `image_url` | `string` | The URL to access the image. |
| `modify_time` | `string` | The timestamp when the image was last modified. |
| `size` | `integer` | The size of the image file. |
| `width` | `integer` | The width dimension of the image. |

<details>
<summary><b>Response Schema</b></summary>

| Field Name | Type | Description |
|------------|------|-------------|
| `data` | `array` | List of matching records |
| `meta` | `object` | Pagination metadata |
| `meta.has_more` | `boolean` | Whether additional pages are available |
| `meta.cursor` | `string \| null` | Cursor for next page of results |
| `meta.took_ms` | `number \| null` | Query execution time in milliseconds |
| `data[].create_time` | `string` | The timestamp when the image was created. |
| `data[].file_name` | `string` | The name of the image file. |
| `data[].format` | `string` | The format type of the image file. |
| `data[].height` | `integer` | The height dimension of the image. |
| `data[].image_id` | `string` | The unique identifier for the image. |
| `data[].image_url` | `string` | The URL to access the image. |
| `data[].modify_time` | `string` | The timestamp when the image was last modified. |
| `data[].size` | `integer` | The size of the image file. |
| `data[].width` | `integer` | The width dimension of the image. |

</details>

## Creative Assets Videos

### Creative Assets Videos List

Search creative asset videos for an advertiser

#### Python SDK

```python
await tiktok_marketing.creative_assets_videos.list(
    advertiser_id="<str>"
)
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/integrations/connectors/{your_connector_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "creative_assets_videos",
    "action": "list",
    "params": {
        "advertiser_id": "<str>"
    }
}'
```


#### Parameters

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `advertiser_id` | `string` | Yes | Advertiser ID |
| `page` | `integer` | No | Page number |
| `page_size` | `integer` | No | Number of items per page |


<details>
<summary><b>Response Schema</b></summary>

#### Records

| Field Name | Type | Description |
|------------|------|-------------|
| `video_id` | `null \| string` |  |
| `video_cover_url` | `null \| string` |  |
| `format` | `null \| string` |  |
| `preview_url` | `null \| string` |  |
| `preview_url_expire_time` | `null \| string` |  |
| `duration` | `null \| number` |  |
| `height` | `null \| integer` |  |
| `width` | `null \| integer` |  |
| `bit_rate` | `null \| number` |  |
| `signature` | `null \| string` |  |
| `size` | `null \| integer` |  |
| `material_id` | `null \| string` |  |
| `allowed_placements` | `null \| array` |  |
| `allow_download` | `null \| boolean` |  |
| `file_name` | `null \| string` |  |
| `create_time` | `null \| string` |  |
| `modify_time` | `null \| string` |  |
| `displayable` | `null \| boolean` |  |
| `fix_task_id` | `null \| string` |  |
| `flaw_types` | `null \| array` |  |


#### Meta

| Field Name | Type | Description |
|------------|------|-------------|
| `page_info` | `object` |  |

</details>

### Creative Assets Videos Search

Search and filter creative assets videos records powered by Airbyte's data sync. This often provides additional fields and operators beyond what the API natively supports, making it easier to narrow down results before performing further operations. Only available in hosted mode.

#### Python SDK

```python
await tiktok_marketing.creative_assets_videos.search(
    query={"filter": {"eq": {"create_time": "<str>"}}}
)
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/integrations/connectors/{your_connector_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "creative_assets_videos",
    "action": "search",
    "params": {
        "query": {"filter": {"eq": {"create_time": "<str>"}}}
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
| `create_time` | `string` | Timestamp when the video was created. |
| `duration` | `number` | Duration of the video in seconds. |
| `file_name` | `string` | Name of the video file. |
| `format` | `string` | Format of the video file. |
| `height` | `integer` | Height of the video in pixels. |
| `modify_time` | `string` | Timestamp when the video was last modified. |
| `size` | `integer` | Size of the video file in bytes. |
| `video_cover_url` | `string` | URL for the cover image of the video. |
| `video_id` | `string` | ID of the video. |
| `width` | `integer` | Width of the video in pixels. |

<details>
<summary><b>Response Schema</b></summary>

| Field Name | Type | Description |
|------------|------|-------------|
| `data` | `array` | List of matching records |
| `meta` | `object` | Pagination metadata |
| `meta.has_more` | `boolean` | Whether additional pages are available |
| `meta.cursor` | `string \| null` | Cursor for next page of results |
| `meta.took_ms` | `number \| null` | Query execution time in milliseconds |
| `data[].create_time` | `string` | Timestamp when the video was created. |
| `data[].duration` | `number` | Duration of the video in seconds. |
| `data[].file_name` | `string` | Name of the video file. |
| `data[].format` | `string` | Format of the video file. |
| `data[].height` | `integer` | Height of the video in pixels. |
| `data[].modify_time` | `string` | Timestamp when the video was last modified. |
| `data[].size` | `integer` | Size of the video file in bytes. |
| `data[].video_cover_url` | `string` | URL for the cover image of the video. |
| `data[].video_id` | `string` | ID of the video. |
| `data[].width` | `integer` | Width of the video in pixels. |

</details>

