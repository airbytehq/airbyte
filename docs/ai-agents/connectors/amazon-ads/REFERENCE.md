# Amazon-Ads full reference

This is the full reference documentation for the Amazon-Ads agent connector.

## Supported entities and actions

The Amazon-Ads connector supports the following entities and actions.

| Entity | Actions |
|--------|---------|
| Profiles | [List](#profiles-list), [Get](#profiles-get) |
| Portfolios | [List](#portfolios-list), [Get](#portfolios-get) |
| Sponsored Product Campaigns | [List](#sponsored-product-campaigns-list), [Get](#sponsored-product-campaigns-get) |

### Profiles

#### Profiles List

Returns a list of advertising profiles associated with the authenticated user.
Profiles represent an advertiser's account in a specific marketplace. Advertisers
may have a single profile if they advertise in only one marketplace, or a separate
profile for each marketplace if they advertise regionally or globally.


**Python SDK**

```python
await amazon_ads.profiles.list()
```

**API**

```bash
curl --location 'https://api.airbyte.ai/api/v1/connectors/sources/{your_source_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "profiles",
    "action": "list"
}'
```


**Parameters**

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `profileTypeFilter` | `string` | No | Filter profiles by type. Comma-separated list of profile types.
Valid values: seller, vendor, agency
 |


<details>
<summary><b>Response Schema</b></summary>

**Records**

| Field Name | Type | Description |
|------------|------|-------------|
| `profileId` | `integer` |  |
| `countryCode` | `string \| null` |  |
| `currencyCode` | `string \| null` |  |
| `dailyBudget` | `number \| null` |  |
| `timezone` | `string \| null` |  |
| `accountInfo` | `object \| any` |  |


</details>

#### Profiles Get

Retrieves a single advertising profile by its ID. The profile contains
information about the advertiser's account in a specific marketplace.


**Python SDK**

```python
await amazon_ads.profiles.get(
    profile_id=0
)
```

**API**

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


**Parameters**

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `profileId` | `integer` | Yes | The unique identifier of the profile |


<details>
<summary><b>Response Schema</b></summary>

**Records**

| Field Name | Type | Description |
|------------|------|-------------|
| `profileId` | `integer` |  |
| `countryCode` | `string \| null` |  |
| `currencyCode` | `string \| null` |  |
| `dailyBudget` | `number \| null` |  |
| `timezone` | `string \| null` |  |
| `accountInfo` | `object \| any` |  |


</details>

### Portfolios

#### Portfolios List

Returns a list of portfolios for the specified profile. Portfolios are used to
group campaigns together for organizational and budget management purposes.


**Python SDK**

```python
await amazon_ads.portfolios.list()
```

**API**

```bash
curl --location 'https://api.airbyte.ai/api/v1/connectors/sources/{your_source_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "portfolios",
    "action": "list"
}'
```


**Parameters**

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `includeExtendedDataFields` | `string` | No | Whether to include extended data fields in the response |


#### Portfolios Get

Retrieves a single portfolio by its ID using the v2 API.


**Python SDK**

```python
await amazon_ads.portfolios.get(
    portfolio_id=0
)
```

**API**

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


**Parameters**

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `portfolioId` | `integer` | Yes | The unique identifier of the portfolio |


<details>
<summary><b>Response Schema</b></summary>

**Records**

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

### Sponsored Product Campaigns

#### Sponsored Product Campaigns List

Returns a list of sponsored product campaigns for the specified profile.
Sponsored Products campaigns promote individual product listings on Amazon.


**Python SDK**

```python
await amazon_ads.sponsored_product_campaigns.list()
```

**API**

```bash
curl --location 'https://api.airbyte.ai/api/v1/connectors/sources/{your_source_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "sponsored_product_campaigns",
    "action": "list"
}'
```


**Parameters**

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `stateFilter` | `object` | No |  |
| `stateFilter.include` | `string` | No | Comma-separated list of states to include (enabled, paused, archived) |
| `maxResults` | `integer` | No | Maximum number of results to return |
| `nextToken` | `string` | No | Token for pagination |


#### Sponsored Product Campaigns Get

Retrieves a single sponsored product campaign by its ID using the v2 API.


**Python SDK**

```python
await amazon_ads.sponsored_product_campaigns.get(
    campaign_id=0
)
```

**API**

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


**Parameters**

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `campaignId` | `integer` | Yes | The unique identifier of the campaign |


<details>
<summary><b>Response Schema</b></summary>

**Records**

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



## Configuration

The Amazon-Ads connector requires the following configuration variables. These variables are used to construct the base API URL. Pass them via the `config` parameter when initializing the connector.

| Variable | Type | Required | Default | Description |
|----------|------|----------|---------|-------------|
| `region_url` | `string` | Yes | https://advertising-api.amazon.com | The Amazon Ads API endpoint URL based on region:
- NA (North America): https://advertising-api.amazon.com
- EU (Europe): https://advertising-api-eu.amazon.com
- FE (Far East): https://advertising-api-fe.amazon.com
 |


## Authentication

The Amazon-Ads connector supports the following authentication methods.


### OAuth2 Authentication

| Field Name | Type | Required | Description |
|------------|------|----------|-------------|
| `client_id` | `str` | Yes | The client ID of your Amazon Ads API application |
| `client_secret` | `str` | Yes | The client secret of your Amazon Ads API application |
| `refresh_token` | `str` | Yes | The refresh token obtained from the OAuth authorization flow |

#### Example

**Python SDK**

```python
AmazonAdsConnector(
  auth_config=AmazonAdsAuthConfig(
    client_id="<The client ID of your Amazon Ads API application>",
    client_secret="<The client secret of your Amazon Ads API application>",
    refresh_token="<The refresh token obtained from the OAuth authorization flow>"
  )
)
```

**API**

```bash
curl --location 'https://api.airbyte.ai/api/v1/integrations/sources' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
  "workspace_id": "{your_workspace_id}",
  "source_template_id": "{source_template_id}",
  "auth_config": {
    "client_id": "<The client ID of your Amazon Ads API application>",
    "client_secret": "<The client secret of your Amazon Ads API application>",
    "refresh_token": "<The refresh token obtained from the OAuth authorization flow>"
  },
  "name": "My Amazon-Ads Connector"
}'
```

