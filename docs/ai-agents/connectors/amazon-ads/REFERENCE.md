# Amazon-Ads full reference

This is the full reference documentation for the Amazon-Ads agent connector.

## Supported entities and actions

The Amazon-Ads connector supports the following entities and actions.

| Entity | Actions |
|--------|---------|
| Profiles | [List](#profiles-list), [Get](#profiles-get), [Search](#profiles-search) |
| Portfolios | [List](#portfolios-list), [Get](#portfolios-get) |
| Sponsored Product Campaigns | [List](#sponsored-product-campaigns-list), [Get](#sponsored-product-campaigns-get) |

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
curl --location 'https://api.airbyte.ai/api/v1/connectors/sources/{your_source_id}/execute' \
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
curl --location 'https://api.airbyte.ai/api/v1/connectors/sources/{your_source_id}/execute' \
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

### Profiles Search

Search and filter profiles records powered by Airbyte's data sync. This often provides additional fields and operators beyond what the API natively supports, making it easier to narrow down results before performing further operations. Only available in hosted mode.

#### Python SDK

```python
await amazon_ads.profiles.search(
    query={"filter": {"eq": {"accountInfo": {}}}}
)
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/connectors/sources/{your_source_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "profiles",
    "action": "search",
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
| `cursor` | `string` | No | Pagination cursor from previous response's next_cursor |
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
| `hits` | `array` | List of matching records |
| `hits[].id` | `string` | Record identifier |
| `hits[].score` | `number` | Relevance score |
| `hits[].data` | `object` | Record data containing the searchable fields listed above |
| `hits[].data.accountInfo` | `object` |  |
| `hits[].data.countryCode` | `string` |  |
| `hits[].data.currencyCode` | `string` |  |
| `hits[].data.dailyBudget` | `number` |  |
| `hits[].data.profileId` | `integer` |  |
| `hits[].data.timezone` | `string` |  |
| `next_cursor` | `string \| null` | Cursor for next page of results |
| `took_ms` | `number` | Query execution time in milliseconds |

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
curl --location 'https://api.airbyte.ai/api/v1/connectors/sources/{your_source_id}/execute' \
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
curl --location 'https://api.airbyte.ai/api/v1/connectors/sources/{your_source_id}/execute' \
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
curl --location 'https://api.airbyte.ai/api/v1/connectors/sources/{your_source_id}/execute' \
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
curl --location 'https://api.airbyte.ai/api/v1/connectors/sources/{your_source_id}/execute' \
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

