# Amazon-Ads full reference

This is the full reference documentation for the Amazon-Ads agent connector.

## Supported entities and actions

The Amazon-Ads connector supports the following entities and actions.

| Entity | Actions |
|--------|---------|
| Profiles | [List](#profiles-list), [Get](#profiles-get), [Context Store Search](#profiles-context-store-search) |
| Portfolios | [List](#portfolios-list), [Get](#portfolios-get) |
| Sponsored Product Campaigns | [List](#sponsored-product-campaigns-list), [Get](#sponsored-product-campaigns-get) |
| Sponsored Product Ad Groups | [List](#sponsored-product-ad-groups-list) |
| Sponsored Product Keywords | [List](#sponsored-product-keywords-list) |
| Sponsored Product Product Ads | [List](#sponsored-product-product-ads-list) |
| Sponsored Product Targets | [List](#sponsored-product-targets-list) |
| Sponsored Product Negative Keywords | [List](#sponsored-product-negative-keywords-list) |
| Sponsored Product Negative Targets | [List](#sponsored-product-negative-targets-list) |
| Sponsored Brands Campaigns | [List](#sponsored-brands-campaigns-list) |
| Sponsored Brands Ad Groups | [List](#sponsored-brands-ad-groups-list) |

## Profiles

### Profiles List

Returns a list of advertising profiles associated with the authenticated user.
Profiles represent an advertiser's account in a specific marketplace. Advertisers
may have a single profile if they advertise in only one marketplace, or a separate
profile for each marketplace if they advertise regionally or globally.


#### Python SDK

```python
await amazon_ads.profiles.list()
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/integrations/connectors/{your_connector_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "profiles",
    "action": "list"
}'
```


#### Parameters

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `profileTypeFilter` | `string` | No | Filter profiles by type. Comma-separated list of profile types.
Valid values: seller, vendor, agency
 |


<details>
<summary><b>Response Schema</b></summary>

#### Records

| Field Name | Type | Description |
|------------|------|-------------|
| `profileId` | `integer` |  |
| `countryCode` | `string \| null` |  |
| `currencyCode` | `string \| null` |  |
| `dailyBudget` | `number \| null` |  |
| `timezone` | `string \| null` |  |
| `accountInfo` | `object \| any` |  |


</details>

### Profiles Get

Retrieves a single advertising profile by its ID. The profile contains
information about the advertiser's account in a specific marketplace.


#### Python SDK

```python
await amazon_ads.profiles.get(
    profile_id=0
)
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/integrations/connectors/{your_connector_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "profiles",
    "action": "get",
    "params": {
        "profileId": 0
    }
}'
```


#### Parameters

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `profileId` | `integer` | Yes | The unique identifier of the profile |


<details>
<summary><b>Response Schema</b></summary>

#### Records

| Field Name | Type | Description |
|------------|------|-------------|
| `profileId` | `integer` |  |
| `countryCode` | `string \| null` |  |
| `currencyCode` | `string \| null` |  |
| `dailyBudget` | `number \| null` |  |
| `timezone` | `string \| null` |  |
| `accountInfo` | `object \| any` |  |


</details>

### Profiles Context Store Search

Search and filter profiles records powered by Airbyte's data sync. This often provides additional fields and operators beyond what the API natively supports, making it easier to narrow down results before performing further operations. Only available in hosted mode.

#### Python SDK

```python
await amazon_ads.profiles.context_store_search(
    query={"filter": {"eq": {"accountInfo": {}}}}
)
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/integrations/connectors/{your_connector_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "profiles",
    "action": "context_store_search",
    "params": {
        "query": {"filter": {"eq": {"accountInfo": {}}}}
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
| `accountInfo` | `object` |  |
| `countryCode` | `string` |  |
| `currencyCode` | `string` |  |
| `dailyBudget` | `number` |  |
| `profileId` | `integer` |  |
| `timezone` | `string` |  |

<details>
<summary><b>Response Schema</b></summary>

| Field Name | Type | Description |
|------------|------|-------------|
| `data` | `array` | List of matching records |
| `meta` | `object` | Pagination metadata |
| `meta.has_more` | `boolean` | Whether additional pages are available |
| `meta.cursor` | `string \| null` | Cursor for next page of results |
| `meta.took_ms` | `number \| null` | Query execution time in milliseconds |
| `data[].accountInfo` | `object` |  |
| `data[].countryCode` | `string` |  |
| `data[].currencyCode` | `string` |  |
| `data[].dailyBudget` | `number` |  |
| `data[].profileId` | `integer` |  |
| `data[].timezone` | `string` |  |

</details>

## Portfolios

### Portfolios List

Returns a list of portfolios for the specified profile. Portfolios are used to
group campaigns together for organizational and budget management purposes.


#### Python SDK

```python
await amazon_ads.portfolios.list()
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/integrations/connectors/{your_connector_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "portfolios",
    "action": "list"
}'
```


#### Parameters

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `includeExtendedDataFields` | `string` | No | Whether to include extended data fields in the response |


<details>
<summary><b>Response Schema</b></summary>



#### Meta

| Field Name | Type | Description |
|------------|------|-------------|
| `next_token` | `string \| null` |  |

</details>

### Portfolios Get

Retrieves a single portfolio by its ID using the v2 API.


#### Python SDK

```python
await amazon_ads.portfolios.get(
    portfolio_id=0
)
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/integrations/connectors/{your_connector_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "portfolios",
    "action": "get",
    "params": {
        "portfolioId": 0
    }
}'
```


#### Parameters

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `portfolioId` | `integer` | Yes | The unique identifier of the portfolio |


<details>
<summary><b>Response Schema</b></summary>

#### Records

| Field Name | Type | Description |
|------------|------|-------------|
| `portfolioId` | `string \| integer` |  |
| `name` | `string \| null` |  |
| `budget` | `object \| any` |  |
| `inBudget` | `boolean \| null` |  |
| `state` | `string \| null` |  |
| `creationDate` | `integer \| null` |  |
| `lastUpdatedDate` | `integer \| null` |  |
| `servingStatus` | `string \| null` |  |


</details>

## Sponsored Product Campaigns

### Sponsored Product Campaigns List

Returns a list of sponsored product campaigns for the specified profile.
Sponsored Products campaigns promote individual product listings on Amazon.


#### Python SDK

```python
await amazon_ads.sponsored_product_campaigns.list()
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/integrations/connectors/{your_connector_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "sponsored_product_campaigns",
    "action": "list"
}'
```


#### Parameters

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `stateFilter` | `object` | No |  |
| `stateFilter.include` | `string` | No | Comma-separated list of states to include (enabled, paused, archived) |
| `maxResults` | `integer` | No | Maximum number of results to return |
| `nextToken` | `string` | No | Token for pagination |


<details>
<summary><b>Response Schema</b></summary>



#### Meta

| Field Name | Type | Description |
|------------|------|-------------|
| `next_token` | `string \| null` |  |

</details>

### Sponsored Product Campaigns Get

Retrieves a single sponsored product campaign by its ID using the v2 API.


#### Python SDK

```python
await amazon_ads.sponsored_product_campaigns.get(
    campaign_id=0
)
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/integrations/connectors/{your_connector_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "sponsored_product_campaigns",
    "action": "get",
    "params": {
        "campaignId": 0
    }
}'
```


#### Parameters

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `campaignId` | `integer` | Yes | The unique identifier of the campaign |


<details>
<summary><b>Response Schema</b></summary>

#### Records

| Field Name | Type | Description |
|------------|------|-------------|
| `campaignId` | `string \| integer` |  |
| `portfolioId` | `string \| integer \| any` |  |
| `name` | `string \| null` |  |
| `campaignType` | `string \| null` |  |
| `tags` | `object \| null` |  |
| `targetingType` | `string \| null` |  |
| `premiumBidAdjustment` | `boolean \| null` |  |
| `state` | `string \| null` |  |
| `dynamicBidding` | `object \| any` |  |
| `bidding` | `object \| any` |  |
| `startDate` | `string \| null` |  |
| `endDate` | `string \| null` |  |
| `dailyBudget` | `number \| null` |  |
| `budget` | `object \| any` |  |
| `extendedData` | `object \| null` |  |
| `marketplaceBudgetAllocation` | `string \| null` |  |
| `offAmazonSettings` | `object \| null` |  |


</details>

## Sponsored Product Ad Groups

### Sponsored Product Ad Groups List

Returns a list of sponsored product ad groups for the specified profile.
Ad groups are used to organize ads and targeting within a campaign.


#### Python SDK

```python
await amazon_ads.sponsored_product_ad_groups.list()
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/integrations/connectors/{your_connector_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "sponsored_product_ad_groups",
    "action": "list"
}'
```


#### Parameters

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `stateFilter` | `object` | No |  |
| `stateFilter.include` | `string` | No | Comma-separated list of states to include (enabled, paused, archived) |
| `maxResults` | `integer` | No | Maximum number of results to return |
| `nextToken` | `string` | No | Token for pagination |


<details>
<summary><b>Response Schema</b></summary>



#### Meta

| Field Name | Type | Description |
|------------|------|-------------|
| `next_token` | `string \| null` |  |

</details>

## Sponsored Product Keywords

### Sponsored Product Keywords List

Returns a list of sponsored product keywords for the specified profile.
Keywords are used in manual targeting campaigns to match shopper search queries.


#### Python SDK

```python
await amazon_ads.sponsored_product_keywords.list()
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/integrations/connectors/{your_connector_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "sponsored_product_keywords",
    "action": "list"
}'
```


#### Parameters

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `stateFilter` | `object` | No |  |
| `stateFilter.include` | `string` | No | Comma-separated list of states to include (enabled, paused, archived) |
| `maxResults` | `integer` | No | Maximum number of results to return |
| `nextToken` | `string` | No | Token for pagination |


<details>
<summary><b>Response Schema</b></summary>



#### Meta

| Field Name | Type | Description |
|------------|------|-------------|
| `next_token` | `string \| null` |  |

</details>

## Sponsored Product Product Ads

### Sponsored Product Product Ads List

Returns a list of sponsored product ads for the specified profile.
Product ads associate an advertised product with an ad group.


#### Python SDK

```python
await amazon_ads.sponsored_product_product_ads.list()
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/integrations/connectors/{your_connector_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "sponsored_product_product_ads",
    "action": "list"
}'
```


#### Parameters

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `stateFilter` | `object` | No |  |
| `stateFilter.include` | `string` | No | Comma-separated list of states to include (enabled, paused, archived) |
| `maxResults` | `integer` | No | Maximum number of results to return |
| `nextToken` | `string` | No | Token for pagination |


<details>
<summary><b>Response Schema</b></summary>



#### Meta

| Field Name | Type | Description |
|------------|------|-------------|
| `next_token` | `string \| null` |  |

</details>

## Sponsored Product Targets

### Sponsored Product Targets List

Returns a list of sponsored product targeting clauses for the specified profile.
Targeting clauses define product or category targeting for ad groups.


#### Python SDK

```python
await amazon_ads.sponsored_product_targets.list()
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/integrations/connectors/{your_connector_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "sponsored_product_targets",
    "action": "list"
}'
```


#### Parameters

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `stateFilter` | `object` | No |  |
| `stateFilter.include` | `string` | No | Comma-separated list of states to include (enabled, paused, archived) |
| `maxResults` | `integer` | No | Maximum number of results to return |
| `nextToken` | `string` | No | Token for pagination |


<details>
<summary><b>Response Schema</b></summary>



#### Meta

| Field Name | Type | Description |
|------------|------|-------------|
| `next_token` | `string \| null` |  |

</details>

## Sponsored Product Negative Keywords

### Sponsored Product Negative Keywords List

Returns a list of sponsored product negative keywords for the specified profile.
Negative keywords prevent ads from showing for specific search terms.


#### Python SDK

```python
await amazon_ads.sponsored_product_negative_keywords.list()
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/integrations/connectors/{your_connector_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "sponsored_product_negative_keywords",
    "action": "list"
}'
```


#### Parameters

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `stateFilter` | `object` | No |  |
| `stateFilter.include` | `string` | No | Comma-separated list of states to include (enabled, paused, archived) |
| `maxResults` | `integer` | No | Maximum number of results to return |
| `nextToken` | `string` | No | Token for pagination |


<details>
<summary><b>Response Schema</b></summary>



#### Meta

| Field Name | Type | Description |
|------------|------|-------------|
| `next_token` | `string \| null` |  |

</details>

## Sponsored Product Negative Targets

### Sponsored Product Negative Targets List

Returns a list of sponsored product negative targeting clauses for the specified profile.
Negative targeting clauses exclude specific products or categories from targeting.


#### Python SDK

```python
await amazon_ads.sponsored_product_negative_targets.list()
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/integrations/connectors/{your_connector_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "sponsored_product_negative_targets",
    "action": "list"
}'
```


#### Parameters

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `stateFilter` | `object` | No |  |
| `stateFilter.include` | `string` | No | Comma-separated list of states to include (enabled, paused, archived) |
| `maxResults` | `integer` | No | Maximum number of results to return |
| `nextToken` | `string` | No | Token for pagination |


<details>
<summary><b>Response Schema</b></summary>



#### Meta

| Field Name | Type | Description |
|------------|------|-------------|
| `next_token` | `string \| null` |  |

</details>

## Sponsored Brands Campaigns

### Sponsored Brands Campaigns List

Returns a list of sponsored brands campaigns for the specified profile.
Sponsored Brands campaigns help drive discovery and sales with creative ad experiences.


#### Python SDK

```python
await amazon_ads.sponsored_brands_campaigns.list()
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/integrations/connectors/{your_connector_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "sponsored_brands_campaigns",
    "action": "list"
}'
```


#### Parameters

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `stateFilter` | `object` | No |  |
| `stateFilter.include` | `string` | No | Comma-separated list of states to include (enabled, paused, archived) |
| `maxResults` | `integer` | No | Maximum number of results to return |
| `nextToken` | `string` | No | Token for pagination |


<details>
<summary><b>Response Schema</b></summary>



#### Meta

| Field Name | Type | Description |
|------------|------|-------------|
| `next_token` | `string \| null` |  |

</details>

## Sponsored Brands Ad Groups

### Sponsored Brands Ad Groups List

Returns a list of sponsored brands ad groups for the specified profile.
Ad groups organize ads and targeting within a Sponsored Brands campaign.


#### Python SDK

```python
await amazon_ads.sponsored_brands_ad_groups.list()
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/integrations/connectors/{your_connector_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "sponsored_brands_ad_groups",
    "action": "list"
}'
```


#### Parameters

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `stateFilter` | `object` | No |  |
| `stateFilter.include` | `string` | No | Comma-separated list of states to include (enabled, paused, archived) |
| `maxResults` | `integer` | No | Maximum number of results to return |
| `nextToken` | `string` | No | Token for pagination |


<details>
<summary><b>Response Schema</b></summary>



#### Meta

| Field Name | Type | Description |
|------------|------|-------------|
| `next_token` | `string \| null` |  |

</details>

