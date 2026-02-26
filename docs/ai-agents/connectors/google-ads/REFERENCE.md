# Google-Ads full reference

This is the full reference documentation for the Google-Ads agent connector.

## Supported entities and actions

The Google-Ads connector supports the following entities and actions.

| Entity | Actions |
|--------|---------|
| Accessible Customers | [List](#accessible-customers-list) |
| Accounts | [List](#accounts-list), [Search](#accounts-search) |
| Campaigns | [List](#campaigns-list), [Update](#campaigns-update), [Search](#campaigns-search) |
| Ad Groups | [List](#ad-groups-list), [Update](#ad-groups-update), [Search](#ad-groups-search) |
| Ad Group Ads | [List](#ad-group-ads-list), [Search](#ad-group-ads-search) |
| Campaign Labels | [List](#campaign-labels-list), [Create](#campaign-labels-create), [Search](#campaign-labels-search) |
| Ad Group Labels | [List](#ad-group-labels-list), [Create](#ad-group-labels-create), [Search](#ad-group-labels-search) |
| Ad Group Ad Labels | [List](#ad-group-ad-labels-list), [Search](#ad-group-ad-labels-search) |
| Labels | [Create](#labels-create) |

## Accessible Customers

### Accessible Customers List

Returns resource names of customers directly accessible by the user authenticating the call. No customer_id is required for this endpoint.

#### Python SDK

```python
await google_ads.accessible_customers.list()
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/integrations/connectors/{your_connector_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "accessible_customers",
    "action": "list"
}'
```



<details>
<summary><b>Response Schema</b></summary>

#### Records

| Field Name | Type | Description |
|------------|------|-------------|
| `resourceNames` | `array<object>` |  |


</details>

## Accounts

### Accounts List

Retrieves customer account details using GAQL query.

#### Python SDK

```python
await google_ads.accounts.list(
    customer_id="<str>"
)
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/integrations/connectors/{your_connector_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "accounts",
    "action": "list",
    "params": {
        "customer_id": "<str>"
    }
}'
```


#### Parameters

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `query` | `string` | No | Google Ads Query Language (GAQL) query |
| `pageToken` | `string` | No | Token for pagination |
| `pageSize` | `integer` | No | Number of results per page (max 10000) |
| `customer_id` | `string` | Yes | Google Ads customer ID (10 digits, no dashes) |


<details>
<summary><b>Response Schema</b></summary>

#### Records

| Field Name | Type | Description |
|------------|------|-------------|
| `customer` | `object` |  |


#### Meta

| Field Name | Type | Description |
|------------|------|-------------|
| `next_page_token` | `string` |  |

</details>

### Accounts Search

Search and filter accounts records powered by Airbyte's data sync. This often provides additional fields and operators beyond what the API natively supports, making it easier to narrow down results before performing further operations. Only available in hosted mode.

#### Python SDK

```python
await google_ads.accounts.search(
    query={"filter": {"eq": {"customer.auto_tagging_enabled": True}}}
)
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/integrations/connectors/{your_connector_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "accounts",
    "action": "search",
    "params": {
        "query": {"filter": {"eq": {"customer.auto_tagging_enabled": True}}}
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
| `customer.auto_tagging_enabled` | `boolean` | Whether auto-tagging is enabled for the account |
| `customer.call_reporting_setting.call_conversion_action` | `string` | Call conversion action resource name |
| `customer.call_reporting_setting.call_conversion_reporting_enabled` | `boolean` | Whether call conversion reporting is enabled |
| `customer.call_reporting_setting.call_reporting_enabled` | `boolean` | Whether call reporting is enabled |
| `customer.conversion_tracking_setting.conversion_tracking_id` | `integer` | Conversion tracking ID |
| `customer.conversion_tracking_setting.cross_account_conversion_tracking_id` | `integer` | Cross-account conversion tracking ID |
| `customer.currency_code` | `string` | Currency code for the account (e.g., USD) |
| `customer.descriptive_name` | `string` | Descriptive name of the customer account |
| `customer.final_url_suffix` | `string` | URL suffix appended to final URLs |
| `customer.has_partners_badge` | `boolean` | Whether the account has a Google Partners badge |
| `customer.id` | `integer` | Unique customer account ID |
| `customer.manager` | `boolean` | Whether this is a manager (MCC) account |
| `customer.optimization_score` | `number` | Optimization score for the account (0.0 to 1.0) |
| `customer.optimization_score_weight` | `number` | Weight of the optimization score |
| `customer.pay_per_conversion_eligibility_failure_reasons` | `array` | Reasons why pay-per-conversion is not eligible |
| `customer.remarketing_setting.google_global_site_tag` | `string` | Google global site tag snippet |
| `customer.resource_name` | `string` | Resource name of the customer |
| `customer.test_account` | `boolean` | Whether this is a test account |
| `customer.time_zone` | `string` | Time zone of the account |
| `customer.tracking_url_template` | `string` | Tracking URL template for the account |
| `segments.date` | `string` | Date segment for the report row |

<details>
<summary><b>Response Schema</b></summary>

| Field Name | Type | Description |
|------------|------|-------------|
| `data` | `array` | List of matching records |
| `meta` | `object` | Pagination metadata |
| `meta.has_more` | `boolean` | Whether additional pages are available |
| `meta.cursor` | `string \| null` | Cursor for next page of results |
| `meta.took_ms` | `number \| null` | Query execution time in milliseconds |
| `data[].customer.auto_tagging_enabled` | `boolean` | Whether auto-tagging is enabled for the account |
| `data[].customer.call_reporting_setting.call_conversion_action` | `string` | Call conversion action resource name |
| `data[].customer.call_reporting_setting.call_conversion_reporting_enabled` | `boolean` | Whether call conversion reporting is enabled |
| `data[].customer.call_reporting_setting.call_reporting_enabled` | `boolean` | Whether call reporting is enabled |
| `data[].customer.conversion_tracking_setting.conversion_tracking_id` | `integer` | Conversion tracking ID |
| `data[].customer.conversion_tracking_setting.cross_account_conversion_tracking_id` | `integer` | Cross-account conversion tracking ID |
| `data[].customer.currency_code` | `string` | Currency code for the account (e.g., USD) |
| `data[].customer.descriptive_name` | `string` | Descriptive name of the customer account |
| `data[].customer.final_url_suffix` | `string` | URL suffix appended to final URLs |
| `data[].customer.has_partners_badge` | `boolean` | Whether the account has a Google Partners badge |
| `data[].customer.id` | `integer` | Unique customer account ID |
| `data[].customer.manager` | `boolean` | Whether this is a manager (MCC) account |
| `data[].customer.optimization_score` | `number` | Optimization score for the account (0.0 to 1.0) |
| `data[].customer.optimization_score_weight` | `number` | Weight of the optimization score |
| `data[].customer.pay_per_conversion_eligibility_failure_reasons` | `array` | Reasons why pay-per-conversion is not eligible |
| `data[].customer.remarketing_setting.google_global_site_tag` | `string` | Google global site tag snippet |
| `data[].customer.resource_name` | `string` | Resource name of the customer |
| `data[].customer.test_account` | `boolean` | Whether this is a test account |
| `data[].customer.time_zone` | `string` | Time zone of the account |
| `data[].customer.tracking_url_template` | `string` | Tracking URL template for the account |
| `data[].segments.date` | `string` | Date segment for the report row |

</details>

## Campaigns

### Campaigns List

Retrieves campaign data using GAQL query.

#### Python SDK

```python
await google_ads.campaigns.list(
    customer_id="<str>"
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
        "customer_id": "<str>"
    }
}'
```


#### Parameters

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `query` | `string` | No | GAQL query for campaigns |
| `pageToken` | `string` | No | Token for pagination |
| `pageSize` | `integer` | No | Number of results per page (max 10000) |
| `customer_id` | `string` | Yes | Google Ads customer ID (10 digits, no dashes) |


<details>
<summary><b>Response Schema</b></summary>

#### Records

| Field Name | Type | Description |
|------------|------|-------------|
| `campaign` | `object` |  |
| `campaignBudget` | `object` |  |
| `metrics` | `object` |  |
| `segments` | `object` |  |


#### Meta

| Field Name | Type | Description |
|------------|------|-------------|
| `next_page_token` | `string` |  |

</details>

### Campaigns Update

Updates campaign properties such as status (enable/pause), name, or other mutable fields using the Google Ads CampaignService mutate endpoint.

#### Python SDK

```python
await google_ads.campaigns.update(
    operations=[],
    customer_id="<str>"
)
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/integrations/connectors/{your_connector_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "campaigns",
    "action": "update",
    "params": {
        "operations": [],
        "customer_id": "<str>"
    }
}'
```


#### Parameters

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `operations` | `array<object>` | Yes | List of campaign operations to perform |
| `operations.updateMask` | `string` | No | Comma-separated list of field paths to update (e.g., name,status) |
| `operations.update` | `object` | No | Campaign fields to update |
| `operations.update.resourceName` | `string` | Yes | Resource name of the campaign to update (e.g., customers/1234567890/campaigns/111222333) |
| `operations.update.name` | `string` | No | New campaign name |
| `operations.update.status` | `"ENABLED" \| "PAUSED"` | No | Campaign status (ENABLED or PAUSED) |
| `customer_id` | `string` | Yes | Google Ads customer ID (10 digits, no dashes) |


<details>
<summary><b>Response Schema</b></summary>

#### Records

| Field Name | Type | Description |
|------------|------|-------------|
| `results` | `array<object>` |  |


</details>

### Campaigns Search

Search and filter campaigns records powered by Airbyte's data sync. This often provides additional fields and operators beyond what the API natively supports, making it easier to narrow down results before performing further operations. Only available in hosted mode.

#### Python SDK

```python
await google_ads.campaigns.search(
    query={"filter": {"eq": {"campaign.id": 0}}}
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
        "query": {"filter": {"eq": {"campaign.id": 0}}}
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
| `campaign.id` | `integer` | Campaign ID |
| `campaign.name` | `string` | Campaign name |
| `campaign.status` | `string` | Campaign status (ENABLED, PAUSED, REMOVED) |
| `campaign.advertising_channel_type` | `string` | Advertising channel type (SEARCH, DISPLAY, etc.) |
| `campaign.advertising_channel_sub_type` | `string` | Advertising channel sub-type |
| `campaign.bidding_strategy` | `string` | Bidding strategy resource name |
| `campaign.bidding_strategy_type` | `string` | Bidding strategy type |
| `campaign.campaign_budget` | `string` | Campaign budget resource name |
| `campaign_budget.amount_micros` | `integer` | Campaign budget amount in micros |
| `campaign.start_date` | `string` | Campaign start date |
| `campaign.end_date` | `string` | Campaign end date |
| `campaign.serving_status` | `string` | Campaign serving status |
| `campaign.resource_name` | `string` | Resource name of the campaign |
| `campaign.labels` | `array` | Labels applied to the campaign |
| `campaign.network_settings.target_google_search` | `boolean` | Whether targeting Google Search |
| `campaign.network_settings.target_search_network` | `boolean` | Whether targeting search network |
| `campaign.network_settings.target_content_network` | `boolean` | Whether targeting content network |
| `campaign.network_settings.target_partner_search_network` | `boolean` | Whether targeting partner search network |
| `metrics.clicks` | `integer` | Number of clicks |
| `metrics.ctr` | `number` | Click-through rate |
| `metrics.conversions` | `number` | Number of conversions |
| `metrics.conversions_value` | `number` | Total conversions value |
| `metrics.cost_micros` | `integer` | Cost in micros |
| `metrics.impressions` | `integer` | Number of impressions |
| `metrics.average_cpc` | `number` | Average cost per click |
| `metrics.average_cpm` | `number` | Average cost per thousand impressions |
| `metrics.interactions` | `integer` | Number of interactions |
| `segments.date` | `string` | Date segment for the report row |
| `segments.hour` | `integer` | Hour segment |
| `segments.ad_network_type` | `string` | Ad network type segment |

<details>
<summary><b>Response Schema</b></summary>

| Field Name | Type | Description |
|------------|------|-------------|
| `data` | `array` | List of matching records |
| `meta` | `object` | Pagination metadata |
| `meta.has_more` | `boolean` | Whether additional pages are available |
| `meta.cursor` | `string \| null` | Cursor for next page of results |
| `meta.took_ms` | `number \| null` | Query execution time in milliseconds |
| `data[].campaign.id` | `integer` | Campaign ID |
| `data[].campaign.name` | `string` | Campaign name |
| `data[].campaign.status` | `string` | Campaign status (ENABLED, PAUSED, REMOVED) |
| `data[].campaign.advertising_channel_type` | `string` | Advertising channel type (SEARCH, DISPLAY, etc.) |
| `data[].campaign.advertising_channel_sub_type` | `string` | Advertising channel sub-type |
| `data[].campaign.bidding_strategy` | `string` | Bidding strategy resource name |
| `data[].campaign.bidding_strategy_type` | `string` | Bidding strategy type |
| `data[].campaign.campaign_budget` | `string` | Campaign budget resource name |
| `data[].campaign_budget.amount_micros` | `integer` | Campaign budget amount in micros |
| `data[].campaign.start_date` | `string` | Campaign start date |
| `data[].campaign.end_date` | `string` | Campaign end date |
| `data[].campaign.serving_status` | `string` | Campaign serving status |
| `data[].campaign.resource_name` | `string` | Resource name of the campaign |
| `data[].campaign.labels` | `array` | Labels applied to the campaign |
| `data[].campaign.network_settings.target_google_search` | `boolean` | Whether targeting Google Search |
| `data[].campaign.network_settings.target_search_network` | `boolean` | Whether targeting search network |
| `data[].campaign.network_settings.target_content_network` | `boolean` | Whether targeting content network |
| `data[].campaign.network_settings.target_partner_search_network` | `boolean` | Whether targeting partner search network |
| `data[].metrics.clicks` | `integer` | Number of clicks |
| `data[].metrics.ctr` | `number` | Click-through rate |
| `data[].metrics.conversions` | `number` | Number of conversions |
| `data[].metrics.conversions_value` | `number` | Total conversions value |
| `data[].metrics.cost_micros` | `integer` | Cost in micros |
| `data[].metrics.impressions` | `integer` | Number of impressions |
| `data[].metrics.average_cpc` | `number` | Average cost per click |
| `data[].metrics.average_cpm` | `number` | Average cost per thousand impressions |
| `data[].metrics.interactions` | `integer` | Number of interactions |
| `data[].segments.date` | `string` | Date segment for the report row |
| `data[].segments.hour` | `integer` | Hour segment |
| `data[].segments.ad_network_type` | `string` | Ad network type segment |

</details>

## Ad Groups

### Ad Groups List

Retrieves ad group data using GAQL query.

#### Python SDK

```python
await google_ads.ad_groups.list(
    customer_id="<str>"
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
        "customer_id": "<str>"
    }
}'
```


#### Parameters

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `query` | `string` | No | GAQL query for ad groups |
| `pageToken` | `string` | No | Token for pagination |
| `pageSize` | `integer` | No | Number of results per page (max 10000) |
| `customer_id` | `string` | Yes | Google Ads customer ID (10 digits, no dashes) |


<details>
<summary><b>Response Schema</b></summary>

#### Records

| Field Name | Type | Description |
|------------|------|-------------|
| `campaign` | `object` |  |
| `adGroup` | `object` |  |
| `metrics` | `object` |  |
| `segments` | `object` |  |


#### Meta

| Field Name | Type | Description |
|------------|------|-------------|
| `next_page_token` | `string` |  |

</details>

### Ad Groups Update

Updates ad group properties such as status (enable/pause), name, or bid amounts using the Google Ads AdGroupService mutate endpoint.

#### Python SDK

```python
await google_ads.ad_groups.update(
    operations=[],
    customer_id="<str>"
)
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/integrations/connectors/{your_connector_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "ad_groups",
    "action": "update",
    "params": {
        "operations": [],
        "customer_id": "<str>"
    }
}'
```


#### Parameters

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `operations` | `array<object>` | Yes | List of ad group operations to perform |
| `operations.updateMask` | `string` | No | Comma-separated list of field paths to update (e.g., name,status,cpcBidMicros) |
| `operations.update` | `object` | No | Ad group fields to update |
| `operations.update.resourceName` | `string` | Yes | Resource name of the ad group to update (e.g., customers/1234567890/adGroups/111222333) |
| `operations.update.name` | `string` | No | New ad group name |
| `operations.update.status` | `"ENABLED" \| "PAUSED"` | No | Ad group status (ENABLED or PAUSED) |
| `operations.update.cpcBidMicros` | `string` | No | CPC bid amount in micros (1,000,000 micros = 1 currency unit) |
| `customer_id` | `string` | Yes | Google Ads customer ID (10 digits, no dashes) |


<details>
<summary><b>Response Schema</b></summary>

#### Records

| Field Name | Type | Description |
|------------|------|-------------|
| `results` | `array<object>` |  |


</details>

### Ad Groups Search

Search and filter ad groups records powered by Airbyte's data sync. This often provides additional fields and operators beyond what the API natively supports, making it easier to narrow down results before performing further operations. Only available in hosted mode.

#### Python SDK

```python
await google_ads.ad_groups.search(
    query={"filter": {"eq": {"campaign.id": 0}}}
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
        "query": {"filter": {"eq": {"campaign.id": 0}}}
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
| `campaign.id` | `integer` | Parent campaign ID |
| `ad_group.id` | `integer` | Ad group ID |
| `ad_group.name` | `string` | Ad group name |
| `ad_group.status` | `string` | Ad group status (ENABLED, PAUSED, REMOVED) |
| `ad_group.type` | `string` | Ad group type |
| `ad_group.ad_rotation_mode` | `string` | Ad rotation mode |
| `ad_group.base_ad_group` | `string` | Base ad group resource name |
| `ad_group.campaign` | `string` | Parent campaign resource name |
| `ad_group.cpc_bid_micros` | `integer` | CPC bid in micros |
| `ad_group.cpm_bid_micros` | `integer` | CPM bid in micros |
| `ad_group.cpv_bid_micros` | `integer` | CPV bid in micros |
| `ad_group.effective_target_cpa_micros` | `integer` | Effective target CPA in micros |
| `ad_group.effective_target_cpa_source` | `string` | Source of the effective target CPA |
| `ad_group.effective_target_roas` | `number` | Effective target ROAS |
| `ad_group.effective_target_roas_source` | `string` | Source of the effective target ROAS |
| `ad_group.labels` | `array` | Labels applied to the ad group |
| `ad_group.resource_name` | `string` | Resource name of the ad group |
| `ad_group.target_cpa_micros` | `integer` | Target CPA in micros |
| `ad_group.target_roas` | `number` | Target ROAS |
| `ad_group.tracking_url_template` | `string` | Tracking URL template |
| `metrics.cost_micros` | `integer` | Cost in micros |
| `segments.date` | `string` | Date segment for the report row |

<details>
<summary><b>Response Schema</b></summary>

| Field Name | Type | Description |
|------------|------|-------------|
| `data` | `array` | List of matching records |
| `meta` | `object` | Pagination metadata |
| `meta.has_more` | `boolean` | Whether additional pages are available |
| `meta.cursor` | `string \| null` | Cursor for next page of results |
| `meta.took_ms` | `number \| null` | Query execution time in milliseconds |
| `data[].campaign.id` | `integer` | Parent campaign ID |
| `data[].ad_group.id` | `integer` | Ad group ID |
| `data[].ad_group.name` | `string` | Ad group name |
| `data[].ad_group.status` | `string` | Ad group status (ENABLED, PAUSED, REMOVED) |
| `data[].ad_group.type` | `string` | Ad group type |
| `data[].ad_group.ad_rotation_mode` | `string` | Ad rotation mode |
| `data[].ad_group.base_ad_group` | `string` | Base ad group resource name |
| `data[].ad_group.campaign` | `string` | Parent campaign resource name |
| `data[].ad_group.cpc_bid_micros` | `integer` | CPC bid in micros |
| `data[].ad_group.cpm_bid_micros` | `integer` | CPM bid in micros |
| `data[].ad_group.cpv_bid_micros` | `integer` | CPV bid in micros |
| `data[].ad_group.effective_target_cpa_micros` | `integer` | Effective target CPA in micros |
| `data[].ad_group.effective_target_cpa_source` | `string` | Source of the effective target CPA |
| `data[].ad_group.effective_target_roas` | `number` | Effective target ROAS |
| `data[].ad_group.effective_target_roas_source` | `string` | Source of the effective target ROAS |
| `data[].ad_group.labels` | `array` | Labels applied to the ad group |
| `data[].ad_group.resource_name` | `string` | Resource name of the ad group |
| `data[].ad_group.target_cpa_micros` | `integer` | Target CPA in micros |
| `data[].ad_group.target_roas` | `number` | Target ROAS |
| `data[].ad_group.tracking_url_template` | `string` | Tracking URL template |
| `data[].metrics.cost_micros` | `integer` | Cost in micros |
| `data[].segments.date` | `string` | Date segment for the report row |

</details>

## Ad Group Ads

### Ad Group Ads List

Retrieves ad group ad data using GAQL query.

#### Python SDK

```python
await google_ads.ad_group_ads.list(
    customer_id="<str>"
)
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/integrations/connectors/{your_connector_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "ad_group_ads",
    "action": "list",
    "params": {
        "customer_id": "<str>"
    }
}'
```


#### Parameters

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `query` | `string` | No | GAQL query for ad group ads |
| `pageToken` | `string` | No | Token for pagination |
| `pageSize` | `integer` | No | Number of results per page (max 10000) |
| `customer_id` | `string` | Yes | Google Ads customer ID (10 digits, no dashes) |


<details>
<summary><b>Response Schema</b></summary>

#### Records

| Field Name | Type | Description |
|------------|------|-------------|
| `adGroup` | `object` |  |
| `adGroupAd` | `object` |  |
| `segments` | `object` |  |


#### Meta

| Field Name | Type | Description |
|------------|------|-------------|
| `next_page_token` | `string` |  |

</details>

### Ad Group Ads Search

Search and filter ad group ads records powered by Airbyte's data sync. This often provides additional fields and operators beyond what the API natively supports, making it easier to narrow down results before performing further operations. Only available in hosted mode.

#### Python SDK

```python
await google_ads.ad_group_ads.search(
    query={"filter": {"eq": {"ad_group.id": 0}}}
)
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/integrations/connectors/{your_connector_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "ad_group_ads",
    "action": "search",
    "params": {
        "query": {"filter": {"eq": {"ad_group.id": 0}}}
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
| `ad_group.id` | `integer` | Parent ad group ID |
| `ad_group_ad.ad.id` | `integer` | Ad ID |
| `ad_group_ad.ad.name` | `string` | Ad name |
| `ad_group_ad.ad.type` | `string` | Ad type |
| `ad_group_ad.status` | `string` | Ad group ad status (ENABLED, PAUSED, REMOVED) |
| `ad_group_ad.ad_strength` | `string` | Ad strength rating |
| `ad_group_ad.ad.display_url` | `string` | Display URL of the ad |
| `ad_group_ad.ad.final_urls` | `array` | Final URLs for the ad |
| `ad_group_ad.ad.final_mobile_urls` | `array` | Final mobile URLs for the ad |
| `ad_group_ad.ad.final_url_suffix` | `string` | Final URL suffix |
| `ad_group_ad.ad.tracking_url_template` | `string` | Tracking URL template |
| `ad_group_ad.ad.resource_name` | `string` | Resource name of the ad |
| `ad_group_ad.ad_group` | `string` | Ad group resource name |
| `ad_group_ad.resource_name` | `string` | Resource name of the ad group ad |
| `ad_group_ad.labels` | `array` | Labels applied to the ad group ad |
| `ad_group_ad.policy_summary.approval_status` | `string` | Policy approval status |
| `ad_group_ad.policy_summary.review_status` | `string` | Policy review status |
| `segments.date` | `string` | Date segment for the report row |

<details>
<summary><b>Response Schema</b></summary>

| Field Name | Type | Description |
|------------|------|-------------|
| `data` | `array` | List of matching records |
| `meta` | `object` | Pagination metadata |
| `meta.has_more` | `boolean` | Whether additional pages are available |
| `meta.cursor` | `string \| null` | Cursor for next page of results |
| `meta.took_ms` | `number \| null` | Query execution time in milliseconds |
| `data[].ad_group.id` | `integer` | Parent ad group ID |
| `data[].ad_group_ad.ad.id` | `integer` | Ad ID |
| `data[].ad_group_ad.ad.name` | `string` | Ad name |
| `data[].ad_group_ad.ad.type` | `string` | Ad type |
| `data[].ad_group_ad.status` | `string` | Ad group ad status (ENABLED, PAUSED, REMOVED) |
| `data[].ad_group_ad.ad_strength` | `string` | Ad strength rating |
| `data[].ad_group_ad.ad.display_url` | `string` | Display URL of the ad |
| `data[].ad_group_ad.ad.final_urls` | `array` | Final URLs for the ad |
| `data[].ad_group_ad.ad.final_mobile_urls` | `array` | Final mobile URLs for the ad |
| `data[].ad_group_ad.ad.final_url_suffix` | `string` | Final URL suffix |
| `data[].ad_group_ad.ad.tracking_url_template` | `string` | Tracking URL template |
| `data[].ad_group_ad.ad.resource_name` | `string` | Resource name of the ad |
| `data[].ad_group_ad.ad_group` | `string` | Ad group resource name |
| `data[].ad_group_ad.resource_name` | `string` | Resource name of the ad group ad |
| `data[].ad_group_ad.labels` | `array` | Labels applied to the ad group ad |
| `data[].ad_group_ad.policy_summary.approval_status` | `string` | Policy approval status |
| `data[].ad_group_ad.policy_summary.review_status` | `string` | Policy review status |
| `data[].segments.date` | `string` | Date segment for the report row |

</details>

## Campaign Labels

### Campaign Labels List

Retrieves campaign label associations using GAQL query.

#### Python SDK

```python
await google_ads.campaign_labels.list(
    customer_id="<str>"
)
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/integrations/connectors/{your_connector_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "campaign_labels",
    "action": "list",
    "params": {
        "customer_id": "<str>"
    }
}'
```


#### Parameters

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `query` | `string` | No | GAQL query for campaign labels |
| `pageToken` | `string` | No | Token for pagination |
| `pageSize` | `integer` | No | Number of results per page (max 10000) |
| `customer_id` | `string` | Yes | Google Ads customer ID (10 digits, no dashes) |


<details>
<summary><b>Response Schema</b></summary>

#### Records

| Field Name | Type | Description |
|------------|------|-------------|
| `campaign` | `object` |  |
| `campaignLabel` | `object` |  |
| `label` | `object` |  |


#### Meta

| Field Name | Type | Description |
|------------|------|-------------|
| `next_page_token` | `string` |  |

</details>

### Campaign Labels Create

Creates a campaign-label association, applying an existing label to a campaign for organization and filtering.

#### Python SDK

```python
await google_ads.campaign_labels.create(
    operations=[],
    customer_id="<str>"
)
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/integrations/connectors/{your_connector_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "campaign_labels",
    "action": "create",
    "params": {
        "operations": [],
        "customer_id": "<str>"
    }
}'
```


#### Parameters

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `operations` | `array<object>` | Yes | List of campaign label operations to perform |
| `operations.create` | `object` | No | Campaign label association to create |
| `operations.create.campaign` | `string` | Yes | Resource name of the campaign (e.g., customers/1234567890/campaigns/111222333) |
| `operations.create.label` | `string` | Yes | Resource name of the label (e.g., customers/1234567890/labels/444555666) |
| `customer_id` | `string` | Yes | Google Ads customer ID (10 digits, no dashes) |


<details>
<summary><b>Response Schema</b></summary>

#### Records

| Field Name | Type | Description |
|------------|------|-------------|
| `results` | `array<object>` |  |


</details>

### Campaign Labels Search

Search and filter campaign labels records powered by Airbyte's data sync. This often provides additional fields and operators beyond what the API natively supports, making it easier to narrow down results before performing further operations. Only available in hosted mode.

#### Python SDK

```python
await google_ads.campaign_labels.search(
    query={"filter": {"eq": {"campaign.id": 0}}}
)
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/integrations/connectors/{your_connector_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "campaign_labels",
    "action": "search",
    "params": {
        "query": {"filter": {"eq": {"campaign.id": 0}}}
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
| `campaign.id` | `integer` | Campaign ID |
| `campaign_label.campaign` | `string` | Campaign resource name |
| `campaign_label.label` | `string` | Label resource name |
| `campaign_label.resource_name` | `string` | Resource name of the campaign label |
| `label.id` | `integer` | Label ID |
| `label.name` | `string` | Label name |
| `label.resource_name` | `string` | Resource name of the label |

<details>
<summary><b>Response Schema</b></summary>

| Field Name | Type | Description |
|------------|------|-------------|
| `data` | `array` | List of matching records |
| `meta` | `object` | Pagination metadata |
| `meta.has_more` | `boolean` | Whether additional pages are available |
| `meta.cursor` | `string \| null` | Cursor for next page of results |
| `meta.took_ms` | `number \| null` | Query execution time in milliseconds |
| `data[].campaign.id` | `integer` | Campaign ID |
| `data[].campaign_label.campaign` | `string` | Campaign resource name |
| `data[].campaign_label.label` | `string` | Label resource name |
| `data[].campaign_label.resource_name` | `string` | Resource name of the campaign label |
| `data[].label.id` | `integer` | Label ID |
| `data[].label.name` | `string` | Label name |
| `data[].label.resource_name` | `string` | Resource name of the label |

</details>

## Ad Group Labels

### Ad Group Labels List

Retrieves ad group label associations using GAQL query.

#### Python SDK

```python
await google_ads.ad_group_labels.list(
    customer_id="<str>"
)
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/integrations/connectors/{your_connector_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "ad_group_labels",
    "action": "list",
    "params": {
        "customer_id": "<str>"
    }
}'
```


#### Parameters

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `query` | `string` | No | GAQL query for ad group labels |
| `pageToken` | `string` | No | Token for pagination |
| `pageSize` | `integer` | No | Number of results per page (max 10000) |
| `customer_id` | `string` | Yes | Google Ads customer ID (10 digits, no dashes) |


<details>
<summary><b>Response Schema</b></summary>

#### Records

| Field Name | Type | Description |
|------------|------|-------------|
| `adGroup` | `object` |  |
| `adGroupLabel` | `object` |  |
| `label` | `object` |  |


#### Meta

| Field Name | Type | Description |
|------------|------|-------------|
| `next_page_token` | `string` |  |

</details>

### Ad Group Labels Create

Creates an ad group-label association, applying an existing label to an ad group for organization and filtering.

#### Python SDK

```python
await google_ads.ad_group_labels.create(
    operations=[],
    customer_id="<str>"
)
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/integrations/connectors/{your_connector_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "ad_group_labels",
    "action": "create",
    "params": {
        "operations": [],
        "customer_id": "<str>"
    }
}'
```


#### Parameters

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `operations` | `array<object>` | Yes | List of ad group label operations to perform |
| `operations.create` | `object` | No | Ad group label association to create |
| `operations.create.adGroup` | `string` | Yes | Resource name of the ad group (e.g., customers/1234567890/adGroups/111222333) |
| `operations.create.label` | `string` | Yes | Resource name of the label (e.g., customers/1234567890/labels/444555666) |
| `customer_id` | `string` | Yes | Google Ads customer ID (10 digits, no dashes) |


<details>
<summary><b>Response Schema</b></summary>

#### Records

| Field Name | Type | Description |
|------------|------|-------------|
| `results` | `array<object>` |  |


</details>

### Ad Group Labels Search

Search and filter ad group labels records powered by Airbyte's data sync. This often provides additional fields and operators beyond what the API natively supports, making it easier to narrow down results before performing further operations. Only available in hosted mode.

#### Python SDK

```python
await google_ads.ad_group_labels.search(
    query={"filter": {"eq": {"ad_group.id": 0}}}
)
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/integrations/connectors/{your_connector_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "ad_group_labels",
    "action": "search",
    "params": {
        "query": {"filter": {"eq": {"ad_group.id": 0}}}
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
| `ad_group.id` | `integer` | Ad group ID |
| `ad_group_label.ad_group` | `string` | Ad group resource name |
| `ad_group_label.label` | `string` | Label resource name |
| `ad_group_label.resource_name` | `string` | Resource name of the ad group label |
| `label.id` | `integer` | Label ID |
| `label.name` | `string` | Label name |
| `label.resource_name` | `string` | Resource name of the label |

<details>
<summary><b>Response Schema</b></summary>

| Field Name | Type | Description |
|------------|------|-------------|
| `data` | `array` | List of matching records |
| `meta` | `object` | Pagination metadata |
| `meta.has_more` | `boolean` | Whether additional pages are available |
| `meta.cursor` | `string \| null` | Cursor for next page of results |
| `meta.took_ms` | `number \| null` | Query execution time in milliseconds |
| `data[].ad_group.id` | `integer` | Ad group ID |
| `data[].ad_group_label.ad_group` | `string` | Ad group resource name |
| `data[].ad_group_label.label` | `string` | Label resource name |
| `data[].ad_group_label.resource_name` | `string` | Resource name of the ad group label |
| `data[].label.id` | `integer` | Label ID |
| `data[].label.name` | `string` | Label name |
| `data[].label.resource_name` | `string` | Resource name of the label |

</details>

## Ad Group Ad Labels

### Ad Group Ad Labels List

Retrieves ad group ad label associations using GAQL query.

#### Python SDK

```python
await google_ads.ad_group_ad_labels.list(
    customer_id="<str>"
)
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/integrations/connectors/{your_connector_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "ad_group_ad_labels",
    "action": "list",
    "params": {
        "customer_id": "<str>"
    }
}'
```


#### Parameters

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `query` | `string` | No | GAQL query for ad group ad labels |
| `pageToken` | `string` | No | Token for pagination |
| `pageSize` | `integer` | No | Number of results per page (max 10000) |
| `customer_id` | `string` | Yes | Google Ads customer ID (10 digits, no dashes) |


<details>
<summary><b>Response Schema</b></summary>

#### Records

| Field Name | Type | Description |
|------------|------|-------------|
| `adGroupAd` | `object` |  |
| `adGroupAdLabel` | `object` |  |
| `label` | `object` |  |


#### Meta

| Field Name | Type | Description |
|------------|------|-------------|
| `next_page_token` | `string` |  |

</details>

### Ad Group Ad Labels Search

Search and filter ad group ad labels records powered by Airbyte's data sync. This often provides additional fields and operators beyond what the API natively supports, making it easier to narrow down results before performing further operations. Only available in hosted mode.

#### Python SDK

```python
await google_ads.ad_group_ad_labels.search(
    query={"filter": {"eq": {"ad_group_ad.ad.id": 0}}}
)
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/integrations/connectors/{your_connector_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "ad_group_ad_labels",
    "action": "search",
    "params": {
        "query": {"filter": {"eq": {"ad_group_ad.ad.id": 0}}}
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
| `ad_group_ad.ad.id` | `integer` | Ad ID |
| `ad_group_ad_label.ad_group_ad` | `string` | Ad group ad resource name |
| `ad_group_ad_label.label` | `string` | Label resource name |
| `ad_group_ad_label.resource_name` | `string` | Resource name of the ad group ad label |
| `label.id` | `integer` | Label ID |
| `label.name` | `string` | Label name |
| `label.resource_name` | `string` | Resource name of the label |

<details>
<summary><b>Response Schema</b></summary>

| Field Name | Type | Description |
|------------|------|-------------|
| `data` | `array` | List of matching records |
| `meta` | `object` | Pagination metadata |
| `meta.has_more` | `boolean` | Whether additional pages are available |
| `meta.cursor` | `string \| null` | Cursor for next page of results |
| `meta.took_ms` | `number \| null` | Query execution time in milliseconds |
| `data[].ad_group_ad.ad.id` | `integer` | Ad ID |
| `data[].ad_group_ad_label.ad_group_ad` | `string` | Ad group ad resource name |
| `data[].ad_group_ad_label.label` | `string` | Label resource name |
| `data[].ad_group_ad_label.resource_name` | `string` | Resource name of the ad group ad label |
| `data[].label.id` | `integer` | Label ID |
| `data[].label.name` | `string` | Label name |
| `data[].label.resource_name` | `string` | Resource name of the label |

</details>

## Labels

### Labels Create

Creates a new label that can be applied to campaigns, ad groups, or ads for organization and reporting purposes.

#### Python SDK

```python
await google_ads.labels.create(
    operations=[],
    customer_id="<str>"
)
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/integrations/connectors/{your_connector_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "labels",
    "action": "create",
    "params": {
        "operations": [],
        "customer_id": "<str>"
    }
}'
```


#### Parameters

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `operations` | `array<object>` | Yes | List of label operations to perform |
| `operations.create` | `object` | No | Label to create |
| `operations.create.name` | `string` | Yes | Name for the new label |
| `operations.create.description` | `string` | No | Description for the label |
| `operations.create.textLabel` | `object` | No | Text label styling |
| `operations.create.textLabel.backgroundColor` | `string` | No | Background color in hex format (e.g., #FF0000) |
| `operations.create.textLabel.description` | `string` | No | Description of the text label |
| `customer_id` | `string` | Yes | Google Ads customer ID (10 digits, no dashes) |


<details>
<summary><b>Response Schema</b></summary>

#### Records

| Field Name | Type | Description |
|------------|------|-------------|
| `results` | `array<object>` |  |


</details>

