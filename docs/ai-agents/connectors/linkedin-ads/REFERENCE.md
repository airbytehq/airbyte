# Linkedin-Ads full reference

This is the full reference documentation for the Linkedin-Ads agent connector.

## Supported entities and actions

The Linkedin-Ads connector supports the following entities and actions.

| Entity | Actions |
|--------|---------|
| Accounts | [List](#accounts-list), [Get](#accounts-get), [Search](#accounts-search) |
| Account Users | [List](#account-users-list), [Search](#account-users-search) |
| Campaigns | [List](#campaigns-list), [Get](#campaigns-get), [Search](#campaigns-search) |
| Campaign Groups | [List](#campaign-groups-list), [Get](#campaign-groups-get), [Search](#campaign-groups-search) |
| Creatives | [List](#creatives-list), [Get](#creatives-get), [Search](#creatives-search) |
| Conversions | [List](#conversions-list), [Get](#conversions-get), [Search](#conversions-search) |
| Ad Campaign Analytics | [List](#ad-campaign-analytics-list), [Search](#ad-campaign-analytics-search) |
| Ad Creative Analytics | [List](#ad-creative-analytics-list), [Search](#ad-creative-analytics-search) |

## Accounts

### Accounts List

Returns a list of ad accounts the authenticated user has access to

#### Python SDK

```python
await linkedin_ads.accounts.list(
    q="<str>"
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
        "q": "<str>"
    }
}'
```


#### Parameters

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `q` | `string` | Yes |  |
| `pageSize` | `integer` | No | Number of items per page |
| `pageToken` | `string` | No | Token for the next page of results |


<details>
<summary><b>Response Schema</b></summary>

#### Records

| Field Name | Type | Description |
|------------|------|-------------|
| `id` | `null \| integer` |  |
| `name` | `null \| string` |  |
| `currency` | `null \| string` |  |
| `status` | `null \| string` |  |
| `type` | `null \| string` |  |
| `reference` | `null \| string` |  |
| `test` | `null \| boolean` |  |
| `changeAuditStamps` | `null \| object` |  |
| `notifiedOnCampaignOptimization` | `null \| boolean` |  |
| `notifiedOnCreativeApproval` | `null \| boolean` |  |
| `notifiedOnCreativeRejection` | `null \| boolean` |  |
| `notifiedOnEndOfCampaign` | `null \| boolean` |  |
| `notifiedOnNewFeaturesEnabled` | `null \| boolean` |  |
| `servingStatuses` | `null \| array` |  |
| `version` | `null \| object` |  |


#### Meta

| Field Name | Type | Description |
|------------|------|-------------|
| `nextPageToken` | `string` |  |

</details>

### Accounts Get

Get a single ad account by ID

#### Python SDK

```python
await linkedin_ads.accounts.get(
    id=0
)
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/integrations/connectors/{your_connector_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "accounts",
    "action": "get",
    "params": {
        "id": 0
    }
}'
```


#### Parameters

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `id` | `integer` | Yes | Ad account ID |


<details>
<summary><b>Response Schema</b></summary>

#### Records

| Field Name | Type | Description |
|------------|------|-------------|
| `id` | `null \| integer` |  |
| `name` | `null \| string` |  |
| `currency` | `null \| string` |  |
| `status` | `null \| string` |  |
| `type` | `null \| string` |  |
| `reference` | `null \| string` |  |
| `test` | `null \| boolean` |  |
| `changeAuditStamps` | `null \| object` |  |
| `notifiedOnCampaignOptimization` | `null \| boolean` |  |
| `notifiedOnCreativeApproval` | `null \| boolean` |  |
| `notifiedOnCreativeRejection` | `null \| boolean` |  |
| `notifiedOnEndOfCampaign` | `null \| boolean` |  |
| `notifiedOnNewFeaturesEnabled` | `null \| boolean` |  |
| `servingStatuses` | `null \| array` |  |
| `version` | `null \| object` |  |


</details>

### Accounts Search

Search and filter accounts records powered by Airbyte's data sync. This often provides additional fields and operators beyond what the API natively supports, making it easier to narrow down results before performing further operations. Only available in hosted mode.

#### Python SDK

```python
await linkedin_ads.accounts.search(
    query={"filter": {"eq": {"id": 0}}}
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
        "query": {"filter": {"eq": {"id": 0}}}
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
| `id` | `integer` | Unique account identifier |
| `name` | `string` | Account name |
| `currency` | `string` | Currency code used by the account |
| `status` | `string` | Account status |
| `type` | `string` | Account type |
| `reference` | `string` | Reference organization URN |
| `test` | `boolean` | Whether this is a test account |
| `notifiedOnCampaignOptimization` | `boolean` | Flag for notifications on campaign optimization |
| `notifiedOnCreativeApproval` | `boolean` | Flag for notifications on creative approval |
| `notifiedOnCreativeRejection` | `boolean` | Flag for notifications on creative rejection |
| `notifiedOnEndOfCampaign` | `boolean` | Flag for notifications on end of campaign |
| `notifiedOnNewFeaturesEnabled` | `boolean` | Flag for notifications on new features |
| `servingStatuses` | `array` | List of serving statuses |
| `version` | `object` | Version information |

<details>
<summary><b>Response Schema</b></summary>

| Field Name | Type | Description |
|------------|------|-------------|
| `data` | `array` | List of matching records |
| `meta` | `object` | Pagination metadata |
| `meta.has_more` | `boolean` | Whether additional pages are available |
| `meta.cursor` | `string \| null` | Cursor for next page of results |
| `meta.took_ms` | `number \| null` | Query execution time in milliseconds |
| `data[].id` | `integer` | Unique account identifier |
| `data[].name` | `string` | Account name |
| `data[].currency` | `string` | Currency code used by the account |
| `data[].status` | `string` | Account status |
| `data[].type` | `string` | Account type |
| `data[].reference` | `string` | Reference organization URN |
| `data[].test` | `boolean` | Whether this is a test account |
| `data[].notifiedOnCampaignOptimization` | `boolean` | Flag for notifications on campaign optimization |
| `data[].notifiedOnCreativeApproval` | `boolean` | Flag for notifications on creative approval |
| `data[].notifiedOnCreativeRejection` | `boolean` | Flag for notifications on creative rejection |
| `data[].notifiedOnEndOfCampaign` | `boolean` | Flag for notifications on end of campaign |
| `data[].notifiedOnNewFeaturesEnabled` | `boolean` | Flag for notifications on new features |
| `data[].servingStatuses` | `array` | List of serving statuses |
| `data[].version` | `object` | Version information |

</details>

## Account Users

### Account Users List

Returns a list of users associated with ad accounts

#### Python SDK

```python
await linkedin_ads.account_users.list(
    q="<str>",
    accounts="<str>"
)
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/integrations/connectors/{your_connector_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "account_users",
    "action": "list",
    "params": {
        "q": "<str>",
        "accounts": "<str>"
    }
}'
```


#### Parameters

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `q` | `string` | Yes |  |
| `accounts` | `string` | Yes | Account URN, e.g. urn:li:sponsoredAccount:123456 |
| `count` | `integer` | No | Number of items per page |
| `start` | `integer` | No | Offset for pagination |


<details>
<summary><b>Response Schema</b></summary>

#### Records

| Field Name | Type | Description |
|------------|------|-------------|
| `account` | `null \| string` |  |
| `user` | `null \| string` |  |
| `role` | `null \| string` |  |
| `changeAuditStamps` | `null \| object` |  |


#### Meta

| Field Name | Type | Description |
|------------|------|-------------|
| `nextPageToken` | `string` |  |

</details>

### Account Users Search

Search and filter account users records powered by Airbyte's data sync. This often provides additional fields and operators beyond what the API natively supports, making it easier to narrow down results before performing further operations. Only available in hosted mode.

#### Python SDK

```python
await linkedin_ads.account_users.search(
    query={"filter": {"eq": {"account": "<str>"}}}
)
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/integrations/connectors/{your_connector_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "account_users",
    "action": "search",
    "params": {
        "query": {"filter": {"eq": {"account": "<str>"}}}
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
| `account` | `string` | Associated account URN |
| `user` | `string` | User URN |
| `role` | `string` | User role in the account |

<details>
<summary><b>Response Schema</b></summary>

| Field Name | Type | Description |
|------------|------|-------------|
| `data` | `array` | List of matching records |
| `meta` | `object` | Pagination metadata |
| `meta.has_more` | `boolean` | Whether additional pages are available |
| `meta.cursor` | `string \| null` | Cursor for next page of results |
| `meta.took_ms` | `number \| null` | Query execution time in milliseconds |
| `data[].account` | `string` | Associated account URN |
| `data[].user` | `string` | User URN |
| `data[].role` | `string` | User role in the account |

</details>

## Campaigns

### Campaigns List

Returns a list of campaigns for an ad account

#### Python SDK

```python
await linkedin_ads.campaigns.list(
    account_id=0,
    q="<str>"
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
        "account_id": 0,
        "q": "<str>"
    }
}'
```


#### Parameters

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `account_id` | `integer` | Yes | Ad account ID |
| `q` | `string` | Yes |  |
| `pageSize` | `integer` | No | Number of items per page |
| `pageToken` | `string` | No | Token for the next page of results |


<details>
<summary><b>Response Schema</b></summary>

#### Records

| Field Name | Type | Description |
|------------|------|-------------|
| `id` | `null \| integer` |  |
| `name` | `null \| string` |  |
| `account` | `null \| string` |  |
| `campaignGroup` | `null \| string` |  |
| `status` | `null \| string` |  |
| `type` | `null \| string` |  |
| `costType` | `null \| string` |  |
| `format` | `null \| string` |  |
| `objectiveType` | `null \| string` |  |
| `optimizationTargetType` | `null \| string` |  |
| `creativeSelection` | `null \| string` |  |
| `pacingStrategy` | `null \| string` |  |
| `audienceExpansionEnabled` | `null \| boolean` |  |
| `offsiteDeliveryEnabled` | `null \| boolean` |  |
| `storyDeliveryEnabled` | `null \| boolean` |  |
| `test` | `null \| boolean` |  |
| `associatedEntity` | `null \| string` |  |
| `connectedTelevisionOnly` | `null \| boolean` |  |
| `politicalIntent` | `null \| string` |  |
| `changeAuditStamps` | `null \| object` |  |
| `dailyBudget` | `null \| object` |  |
| `totalBudget` | `null \| object` |  |
| `unitCost` | `null \| object` |  |
| `runSchedule` | `null \| object` |  |
| `locale` | `null \| object` |  |
| `targetingCriteria` | `null \| object` |  |
| `offsitePreferences` | `null \| object` |  |
| `servingStatuses` | `null \| array` |  |
| `version` | `null \| object` |  |


#### Meta

| Field Name | Type | Description |
|------------|------|-------------|
| `nextPageToken` | `string` |  |

</details>

### Campaigns Get

Get a single campaign by ID

#### Python SDK

```python
await linkedin_ads.campaigns.get(
    account_id=0,
    id=0
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
        "account_id": 0,
        "id": 0
    }
}'
```


#### Parameters

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `account_id` | `integer` | Yes | Ad account ID |
| `id` | `integer` | Yes | Campaign ID |


<details>
<summary><b>Response Schema</b></summary>

#### Records

| Field Name | Type | Description |
|------------|------|-------------|
| `id` | `null \| integer` |  |
| `name` | `null \| string` |  |
| `account` | `null \| string` |  |
| `campaignGroup` | `null \| string` |  |
| `status` | `null \| string` |  |
| `type` | `null \| string` |  |
| `costType` | `null \| string` |  |
| `format` | `null \| string` |  |
| `objectiveType` | `null \| string` |  |
| `optimizationTargetType` | `null \| string` |  |
| `creativeSelection` | `null \| string` |  |
| `pacingStrategy` | `null \| string` |  |
| `audienceExpansionEnabled` | `null \| boolean` |  |
| `offsiteDeliveryEnabled` | `null \| boolean` |  |
| `storyDeliveryEnabled` | `null \| boolean` |  |
| `test` | `null \| boolean` |  |
| `associatedEntity` | `null \| string` |  |
| `connectedTelevisionOnly` | `null \| boolean` |  |
| `politicalIntent` | `null \| string` |  |
| `changeAuditStamps` | `null \| object` |  |
| `dailyBudget` | `null \| object` |  |
| `totalBudget` | `null \| object` |  |
| `unitCost` | `null \| object` |  |
| `runSchedule` | `null \| object` |  |
| `locale` | `null \| object` |  |
| `targetingCriteria` | `null \| object` |  |
| `offsitePreferences` | `null \| object` |  |
| `servingStatuses` | `null \| array` |  |
| `version` | `null \| object` |  |


</details>

### Campaigns Search

Search and filter campaigns records powered by Airbyte's data sync. This often provides additional fields and operators beyond what the API natively supports, making it easier to narrow down results before performing further operations. Only available in hosted mode.

#### Python SDK

```python
await linkedin_ads.campaigns.search(
    query={"filter": {"eq": {"id": 0}}}
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
        "query": {"filter": {"eq": {"id": 0}}}
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
| `id` | `integer` | Unique campaign identifier |
| `name` | `string` | Campaign name |
| `account` | `string` | Associated account URN |
| `campaignGroup` | `string` | Parent campaign group URN |
| `status` | `string` | Campaign status |
| `type` | `string` | Campaign type |
| `costType` | `string` | Cost type (CPC CPM etc) |
| `format` | `string` | Campaign ad format |
| `objectiveType` | `string` | Campaign objective type |
| `optimizationTargetType` | `string` | Optimization target type |
| `creativeSelection` | `string` | Creative selection mode |
| `pacingStrategy` | `string` | Budget pacing strategy |
| `audienceExpansionEnabled` | `boolean` | Whether audience expansion is enabled |
| `offsiteDeliveryEnabled` | `boolean` | Whether offsite delivery is enabled |
| `storyDeliveryEnabled` | `boolean` | Whether story delivery is enabled |
| `test` | `boolean` | Whether this is a test campaign |
| `associatedEntity` | `string` | Associated entity URN |
| `dailyBudget` | `object` | Daily budget configuration |
| `totalBudget` | `object` | Total budget configuration |
| `unitCost` | `object` | Cost per unit (bid amount) |
| `runSchedule` | `object` | Campaign run schedule |
| `locale` | `object` | Campaign locale settings |
| `servingStatuses` | `array` | List of serving statuses |
| `version` | `object` | Version information |

<details>
<summary><b>Response Schema</b></summary>

| Field Name | Type | Description |
|------------|------|-------------|
| `data` | `array` | List of matching records |
| `meta` | `object` | Pagination metadata |
| `meta.has_more` | `boolean` | Whether additional pages are available |
| `meta.cursor` | `string \| null` | Cursor for next page of results |
| `meta.took_ms` | `number \| null` | Query execution time in milliseconds |
| `data[].id` | `integer` | Unique campaign identifier |
| `data[].name` | `string` | Campaign name |
| `data[].account` | `string` | Associated account URN |
| `data[].campaignGroup` | `string` | Parent campaign group URN |
| `data[].status` | `string` | Campaign status |
| `data[].type` | `string` | Campaign type |
| `data[].costType` | `string` | Cost type (CPC CPM etc) |
| `data[].format` | `string` | Campaign ad format |
| `data[].objectiveType` | `string` | Campaign objective type |
| `data[].optimizationTargetType` | `string` | Optimization target type |
| `data[].creativeSelection` | `string` | Creative selection mode |
| `data[].pacingStrategy` | `string` | Budget pacing strategy |
| `data[].audienceExpansionEnabled` | `boolean` | Whether audience expansion is enabled |
| `data[].offsiteDeliveryEnabled` | `boolean` | Whether offsite delivery is enabled |
| `data[].storyDeliveryEnabled` | `boolean` | Whether story delivery is enabled |
| `data[].test` | `boolean` | Whether this is a test campaign |
| `data[].associatedEntity` | `string` | Associated entity URN |
| `data[].dailyBudget` | `object` | Daily budget configuration |
| `data[].totalBudget` | `object` | Total budget configuration |
| `data[].unitCost` | `object` | Cost per unit (bid amount) |
| `data[].runSchedule` | `object` | Campaign run schedule |
| `data[].locale` | `object` | Campaign locale settings |
| `data[].servingStatuses` | `array` | List of serving statuses |
| `data[].version` | `object` | Version information |

</details>

## Campaign Groups

### Campaign Groups List

Returns a list of campaign groups for an ad account

#### Python SDK

```python
await linkedin_ads.campaign_groups.list(
    account_id=0,
    q="<str>"
)
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/integrations/connectors/{your_connector_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "campaign_groups",
    "action": "list",
    "params": {
        "account_id": 0,
        "q": "<str>"
    }
}'
```


#### Parameters

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `account_id` | `integer` | Yes | Ad account ID |
| `q` | `string` | Yes |  |
| `pageSize` | `integer` | No | Number of items per page |
| `pageToken` | `string` | No | Token for the next page of results |


<details>
<summary><b>Response Schema</b></summary>

#### Records

| Field Name | Type | Description |
|------------|------|-------------|
| `id` | `null \| integer` |  |
| `name` | `null \| string` |  |
| `account` | `null \| string` |  |
| `status` | `null \| string` |  |
| `test` | `null \| boolean` |  |
| `backfilled` | `null \| boolean` |  |
| `changeAuditStamps` | `null \| object` |  |
| `totalBudget` | `null \| object` |  |
| `runSchedule` | `null \| object` |  |
| `servingStatuses` | `null \| array` |  |
| `allowedCampaignTypes` | `null \| array` |  |


#### Meta

| Field Name | Type | Description |
|------------|------|-------------|
| `nextPageToken` | `string` |  |

</details>

### Campaign Groups Get

Get a single campaign group by ID

#### Python SDK

```python
await linkedin_ads.campaign_groups.get(
    account_id=0,
    id=0
)
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/integrations/connectors/{your_connector_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "campaign_groups",
    "action": "get",
    "params": {
        "account_id": 0,
        "id": 0
    }
}'
```


#### Parameters

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `account_id` | `integer` | Yes | Ad account ID |
| `id` | `integer` | Yes | Campaign group ID |


<details>
<summary><b>Response Schema</b></summary>

#### Records

| Field Name | Type | Description |
|------------|------|-------------|
| `id` | `null \| integer` |  |
| `name` | `null \| string` |  |
| `account` | `null \| string` |  |
| `status` | `null \| string` |  |
| `test` | `null \| boolean` |  |
| `backfilled` | `null \| boolean` |  |
| `changeAuditStamps` | `null \| object` |  |
| `totalBudget` | `null \| object` |  |
| `runSchedule` | `null \| object` |  |
| `servingStatuses` | `null \| array` |  |
| `allowedCampaignTypes` | `null \| array` |  |


</details>

### Campaign Groups Search

Search and filter campaign groups records powered by Airbyte's data sync. This often provides additional fields and operators beyond what the API natively supports, making it easier to narrow down results before performing further operations. Only available in hosted mode.

#### Python SDK

```python
await linkedin_ads.campaign_groups.search(
    query={"filter": {"eq": {"id": 0}}}
)
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/integrations/connectors/{your_connector_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "campaign_groups",
    "action": "search",
    "params": {
        "query": {"filter": {"eq": {"id": 0}}}
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
| `id` | `integer` | Unique campaign group identifier |
| `name` | `string` | Campaign group name |
| `account` | `string` | Associated account URN |
| `status` | `string` | Campaign group status |
| `test` | `boolean` | Whether this is a test campaign group |
| `backfilled` | `boolean` | Whether the campaign group is backfilled |
| `totalBudget` | `object` | Total budget for the campaign group |
| `runSchedule` | `object` | Campaign group run schedule |
| `servingStatuses` | `array` | List of serving statuses |
| `allowedCampaignTypes` | `array` | Types of campaigns allowed in this group |

<details>
<summary><b>Response Schema</b></summary>

| Field Name | Type | Description |
|------------|------|-------------|
| `data` | `array` | List of matching records |
| `meta` | `object` | Pagination metadata |
| `meta.has_more` | `boolean` | Whether additional pages are available |
| `meta.cursor` | `string \| null` | Cursor for next page of results |
| `meta.took_ms` | `number \| null` | Query execution time in milliseconds |
| `data[].id` | `integer` | Unique campaign group identifier |
| `data[].name` | `string` | Campaign group name |
| `data[].account` | `string` | Associated account URN |
| `data[].status` | `string` | Campaign group status |
| `data[].test` | `boolean` | Whether this is a test campaign group |
| `data[].backfilled` | `boolean` | Whether the campaign group is backfilled |
| `data[].totalBudget` | `object` | Total budget for the campaign group |
| `data[].runSchedule` | `object` | Campaign group run schedule |
| `data[].servingStatuses` | `array` | List of serving statuses |
| `data[].allowedCampaignTypes` | `array` | Types of campaigns allowed in this group |

</details>

## Creatives

### Creatives List

Returns a list of creatives for an ad account

#### Python SDK

```python
await linkedin_ads.creatives.list(
    account_id=0,
    q="<str>"
)
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/integrations/connectors/{your_connector_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "creatives",
    "action": "list",
    "params": {
        "account_id": 0,
        "q": "<str>"
    }
}'
```


#### Parameters

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `account_id` | `integer` | Yes | Ad account ID |
| `q` | `string` | Yes |  |
| `pageSize` | `integer` | No | Number of items per page |
| `pageToken` | `string` | No | Token for the next page of results |


<details>
<summary><b>Response Schema</b></summary>

#### Records

| Field Name | Type | Description |
|------------|------|-------------|
| `id` | `null \| string` |  |
| `name` | `null \| string` |  |
| `account` | `null \| string` |  |
| `campaign` | `null \| string` |  |
| `intendedStatus` | `null \| string` |  |
| `isServing` | `null \| boolean` |  |
| `isTest` | `null \| boolean` |  |
| `createdAt` | `null \| integer` |  |
| `createdBy` | `null \| string` |  |
| `lastModifiedAt` | `null \| integer` |  |
| `lastModifiedBy` | `null \| string` |  |
| `content` | `null \| object` |  |
| `review` | `null \| object` |  |
| `servingHoldReasons` | `null \| array` |  |
| `leadgenCallToAction` | `null \| object` |  |


#### Meta

| Field Name | Type | Description |
|------------|------|-------------|
| `nextPageToken` | `string` |  |

</details>

### Creatives Get

Get a single creative by ID

#### Python SDK

```python
await linkedin_ads.creatives.get(
    account_id=0,
    id="<str>"
)
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/integrations/connectors/{your_connector_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "creatives",
    "action": "get",
    "params": {
        "account_id": 0,
        "id": "<str>"
    }
}'
```


#### Parameters

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `account_id` | `integer` | Yes | Ad account ID |
| `id` | `string` | Yes | Creative ID |


<details>
<summary><b>Response Schema</b></summary>

#### Records

| Field Name | Type | Description |
|------------|------|-------------|
| `id` | `null \| string` |  |
| `name` | `null \| string` |  |
| `account` | `null \| string` |  |
| `campaign` | `null \| string` |  |
| `intendedStatus` | `null \| string` |  |
| `isServing` | `null \| boolean` |  |
| `isTest` | `null \| boolean` |  |
| `createdAt` | `null \| integer` |  |
| `createdBy` | `null \| string` |  |
| `lastModifiedAt` | `null \| integer` |  |
| `lastModifiedBy` | `null \| string` |  |
| `content` | `null \| object` |  |
| `review` | `null \| object` |  |
| `servingHoldReasons` | `null \| array` |  |
| `leadgenCallToAction` | `null \| object` |  |


</details>

### Creatives Search

Search and filter creatives records powered by Airbyte's data sync. This often provides additional fields and operators beyond what the API natively supports, making it easier to narrow down results before performing further operations. Only available in hosted mode.

#### Python SDK

```python
await linkedin_ads.creatives.search(
    query={"filter": {"eq": {"id": "<str>"}}}
)
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/integrations/connectors/{your_connector_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "creatives",
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
| `id` | `string` | Unique creative identifier |
| `name` | `string` | Creative name |
| `account` | `string` | Associated account URN |
| `campaign` | `string` | Parent campaign URN |
| `intendedStatus` | `string` | Intended creative status |
| `isServing` | `boolean` | Whether the creative is currently serving |
| `isTest` | `boolean` | Whether this is a test creative |
| `createdAt` | `integer` | Creation timestamp (epoch milliseconds) |
| `createdBy` | `string` | URN of the user who created the creative |
| `lastModifiedAt` | `integer` | Last modification timestamp (epoch milliseconds) |
| `lastModifiedBy` | `string` | URN of the user who last modified the creative |
| `content` | `object` | Creative content configuration |
| `servingHoldReasons` | `array` | Reasons for holding creative from serving |

<details>
<summary><b>Response Schema</b></summary>

| Field Name | Type | Description |
|------------|------|-------------|
| `data` | `array` | List of matching records |
| `meta` | `object` | Pagination metadata |
| `meta.has_more` | `boolean` | Whether additional pages are available |
| `meta.cursor` | `string \| null` | Cursor for next page of results |
| `meta.took_ms` | `number \| null` | Query execution time in milliseconds |
| `data[].id` | `string` | Unique creative identifier |
| `data[].name` | `string` | Creative name |
| `data[].account` | `string` | Associated account URN |
| `data[].campaign` | `string` | Parent campaign URN |
| `data[].intendedStatus` | `string` | Intended creative status |
| `data[].isServing` | `boolean` | Whether the creative is currently serving |
| `data[].isTest` | `boolean` | Whether this is a test creative |
| `data[].createdAt` | `integer` | Creation timestamp (epoch milliseconds) |
| `data[].createdBy` | `string` | URN of the user who created the creative |
| `data[].lastModifiedAt` | `integer` | Last modification timestamp (epoch milliseconds) |
| `data[].lastModifiedBy` | `string` | URN of the user who last modified the creative |
| `data[].content` | `object` | Creative content configuration |
| `data[].servingHoldReasons` | `array` | Reasons for holding creative from serving |

</details>

## Conversions

### Conversions List

Returns a list of conversion rules for an ad account

#### Python SDK

```python
await linkedin_ads.conversions.list(
    q="<str>",
    account="<str>"
)
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/integrations/connectors/{your_connector_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "conversions",
    "action": "list",
    "params": {
        "q": "<str>",
        "account": "<str>"
    }
}'
```


#### Parameters

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `q` | `string` | Yes |  |
| `account` | `string` | Yes | Account URN, e.g. urn:li:sponsoredAccount:123456 |
| `count` | `integer` | No | Number of items per page |
| `start` | `integer` | No | Offset for pagination |


<details>
<summary><b>Response Schema</b></summary>

#### Records

| Field Name | Type | Description |
|------------|------|-------------|
| `id` | `null \| integer` |  |
| `name` | `null \| string` |  |
| `account` | `null \| string` |  |
| `type` | `null \| string` |  |
| `attributionType` | `null \| string` |  |
| `conversionMethod` | `null \| string` |  |
| `valueType` | `null \| string` |  |
| `enabled` | `null \| boolean` |  |
| `created` | `null \| integer` |  |
| `lastModified` | `null \| integer` |  |
| `postClickAttributionWindowSize` | `null \| integer` |  |
| `viewThroughAttributionWindowSize` | `null \| integer` |  |
| `campaigns` | `null \| array` |  |
| `associatedCampaigns` | `null \| array` |  |
| `imagePixelTag` | `null \| string` |  |
| `lastCallbackAt` | `null \| integer` |  |
| `latestFirstPartyCallbackAt` | `null \| integer` |  |
| `urlMatchRuleExpression` | `null \| array` |  |
| `urlRules` | `null \| array` |  |
| `value` | `null \| object` |  |


#### Meta

| Field Name | Type | Description |
|------------|------|-------------|
| `total` | `integer` |  |

</details>

### Conversions Get

Get a single conversion rule by ID

#### Python SDK

```python
await linkedin_ads.conversions.get(
    id=0
)
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/integrations/connectors/{your_connector_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "conversions",
    "action": "get",
    "params": {
        "id": 0
    }
}'
```


#### Parameters

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `id` | `integer` | Yes | Conversion ID |


<details>
<summary><b>Response Schema</b></summary>

#### Records

| Field Name | Type | Description |
|------------|------|-------------|
| `id` | `null \| integer` |  |
| `name` | `null \| string` |  |
| `account` | `null \| string` |  |
| `type` | `null \| string` |  |
| `attributionType` | `null \| string` |  |
| `conversionMethod` | `null \| string` |  |
| `valueType` | `null \| string` |  |
| `enabled` | `null \| boolean` |  |
| `created` | `null \| integer` |  |
| `lastModified` | `null \| integer` |  |
| `postClickAttributionWindowSize` | `null \| integer` |  |
| `viewThroughAttributionWindowSize` | `null \| integer` |  |
| `campaigns` | `null \| array` |  |
| `associatedCampaigns` | `null \| array` |  |
| `imagePixelTag` | `null \| string` |  |
| `lastCallbackAt` | `null \| integer` |  |
| `latestFirstPartyCallbackAt` | `null \| integer` |  |
| `urlMatchRuleExpression` | `null \| array` |  |
| `urlRules` | `null \| array` |  |
| `value` | `null \| object` |  |


</details>

### Conversions Search

Search and filter conversions records powered by Airbyte's data sync. This often provides additional fields and operators beyond what the API natively supports, making it easier to narrow down results before performing further operations. Only available in hosted mode.

#### Python SDK

```python
await linkedin_ads.conversions.search(
    query={"filter": {"eq": {"id": 0}}}
)
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/integrations/connectors/{your_connector_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "conversions",
    "action": "search",
    "params": {
        "query": {"filter": {"eq": {"id": 0}}}
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
| `id` | `integer` | Unique conversion identifier |
| `name` | `string` | Conversion name |
| `account` | `string` | Associated account URN |
| `type` | `string` | Conversion type |
| `attributionType` | `string` | Attribution type for the conversion |
| `enabled` | `boolean` | Whether the conversion tracking is enabled |
| `created` | `integer` | Creation timestamp (epoch milliseconds) |
| `lastModified` | `integer` | Last modification timestamp (epoch milliseconds) |
| `postClickAttributionWindowSize` | `integer` | Post-click attribution window size in days |
| `viewThroughAttributionWindowSize` | `integer` | View-through attribution window size in days |
| `campaigns` | `array` | Related campaign URNs |
| `associatedCampaigns` | `array` | Associated campaigns |
| `imagePixelTag` | `string` | Image pixel tracking tag |
| `value` | `object` | Conversion value |

<details>
<summary><b>Response Schema</b></summary>

| Field Name | Type | Description |
|------------|------|-------------|
| `data` | `array` | List of matching records |
| `meta` | `object` | Pagination metadata |
| `meta.has_more` | `boolean` | Whether additional pages are available |
| `meta.cursor` | `string \| null` | Cursor for next page of results |
| `meta.took_ms` | `number \| null` | Query execution time in milliseconds |
| `data[].id` | `integer` | Unique conversion identifier |
| `data[].name` | `string` | Conversion name |
| `data[].account` | `string` | Associated account URN |
| `data[].type` | `string` | Conversion type |
| `data[].attributionType` | `string` | Attribution type for the conversion |
| `data[].enabled` | `boolean` | Whether the conversion tracking is enabled |
| `data[].created` | `integer` | Creation timestamp (epoch milliseconds) |
| `data[].lastModified` | `integer` | Last modification timestamp (epoch milliseconds) |
| `data[].postClickAttributionWindowSize` | `integer` | Post-click attribution window size in days |
| `data[].viewThroughAttributionWindowSize` | `integer` | View-through attribution window size in days |
| `data[].campaigns` | `array` | Related campaign URNs |
| `data[].associatedCampaigns` | `array` | Associated campaigns |
| `data[].imagePixelTag` | `string` | Image pixel tracking tag |
| `data[].value` | `object` | Conversion value |

</details>

## Ad Campaign Analytics

### Ad Campaign Analytics List

Returns ad analytics data pivoted by campaign. Provides performance metrics including clicks, impressions, spend, and engagement data grouped by campaign.


#### Python SDK

```python
await linkedin_ads.ad_campaign_analytics.list(
    q="<str>",
    pivot="<str>",
    time_granularity="<str>",
    date_range="<str>",
    campaigns="<str>"
)
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/integrations/connectors/{your_connector_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "ad_campaign_analytics",
    "action": "list",
    "params": {
        "q": "<str>",
        "pivot": "<str>",
        "timeGranularity": "<str>",
        "dateRange": "<str>",
        "campaigns": "<str>"
    }
}'
```


#### Parameters

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `q` | `string` | Yes |  |
| `pivot` | `string` | Yes | Pivot dimension for analytics grouping |
| `timeGranularity` | `"DAILY" \| "MONTHLY" \| "ALL"` | Yes | Time granularity for analytics data |
| `dateRange` | `string` | Yes | Date range in LinkedIn format, e.g. (start:(year:2024,month:1,day:1),end:(year:2024,month:12,day:31)) |
| `campaigns` | `string` | Yes | List of campaign URNs, e.g. List(urn%3Ali%3AsponsoredCampaign%3A123) |
| `fields` | `string` | No | Comma-separated list of metric fields to return |


<details>
<summary><b>Response Schema</b></summary>

#### Records

| Field Name | Type | Description |
|------------|------|-------------|
| `dateRange` | `null \| object` |  |
| `pivotValues` | `null \| array` |  |
| `impressions` | `null \| integer` |  |
| `clicks` | `null \| integer` |  |
| `costInLocalCurrency` | `null \| string` |  |
| `costInUsd` | `null \| string` |  |
| `likes` | `null \| integer` |  |
| `shares` | `null \| integer` |  |
| `comments` | `null \| integer` |  |
| `reactions` | `null \| integer` |  |
| `follows` | `null \| integer` |  |
| `totalEngagements` | `null \| integer` |  |
| `landingPageClicks` | `null \| integer` |  |
| `companyPageClicks` | `null \| integer` |  |
| `externalWebsiteConversions` | `null \| integer` |  |
| `externalWebsitePostClickConversions` | `null \| integer` |  |
| `externalWebsitePostViewConversions` | `null \| integer` |  |
| `conversionValueInLocalCurrency` | `null \| string` |  |
| `approximateMemberReach` | `null \| integer` |  |
| `cardClicks` | `null \| integer` |  |
| `cardImpressions` | `null \| integer` |  |
| `videoStarts` | `null \| integer` |  |
| `videoViews` | `null \| integer` |  |
| `videoFirstQuartileCompletions` | `null \| integer` |  |
| `videoMidpointCompletions` | `null \| integer` |  |
| `videoThirdQuartileCompletions` | `null \| integer` |  |
| `videoCompletions` | `null \| integer` |  |
| `fullScreenPlays` | `null \| integer` |  |
| `oneClickLeads` | `null \| integer` |  |
| `oneClickLeadFormOpens` | `null \| integer` |  |
| `otherEngagements` | `null \| integer` |  |
| `adUnitClicks` | `null \| integer` |  |
| `actionClicks` | `null \| integer` |  |
| `textUrlClicks` | `null \| integer` |  |
| `commentLikes` | `null \| integer` |  |
| `sends` | `null \| integer` |  |
| `opens` | `null \| integer` |  |
| `downloadClicks` | `null \| integer` |  |
| `jobApplications` | `null \| integer` |  |
| `jobApplyClicks` | `null \| integer` |  |
| `registrations` | `null \| integer` |  |
| `talentLeads` | `null \| integer` |  |
| `validWorkEmailLeads` | `null \| integer` |  |
| `postClickJobApplications` | `null \| integer` |  |
| `postClickJobApplyClicks` | `null \| integer` |  |
| `postClickRegistrations` | `null \| integer` |  |
| `postViewJobApplications` | `null \| integer` |  |
| `postViewJobApplyClicks` | `null \| integer` |  |
| `postViewRegistrations` | `null \| integer` |  |
| `leadGenerationMailContactInfoShares` | `null \| integer` |  |
| `leadGenerationMailInterestedClicks` | `null \| integer` |  |
| `documentCompletions` | `null \| integer` |  |
| `documentFirstQuartileCompletions` | `null \| integer` |  |
| `documentMidpointCompletions` | `null \| integer` |  |
| `documentThirdQuartileCompletions` | `null \| integer` |  |


</details>

### Ad Campaign Analytics Search

Search and filter ad campaign analytics records powered by Airbyte's data sync. This often provides additional fields and operators beyond what the API natively supports, making it easier to narrow down results before performing further operations. Only available in hosted mode.

#### Python SDK

```python
await linkedin_ads.ad_campaign_analytics.search(
    query={"filter": {"eq": {"impressions": 0.0}}}
)
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/integrations/connectors/{your_connector_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "ad_campaign_analytics",
    "action": "search",
    "params": {
        "query": {"filter": {"eq": {"impressions": 0.0}}}
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
| `impressions` | `number` | Number of times the ad was shown |
| `clicks` | `number` | Number of clicks on the ad |
| `costInLocalCurrency` | `number` | Total cost in the accounts local currency |
| `costInUsd` | `number` | Total cost in USD |
| `likes` | `number` | Number of likes |
| `shares` | `number` | Number of shares |
| `comments` | `number` | Number of comments |
| `reactions` | `number` | Number of reactions |
| `follows` | `number` | Number of follows |
| `totalEngagements` | `number` | Total number of engagements |
| `landingPageClicks` | `number` | Number of landing page clicks |
| `companyPageClicks` | `number` | Number of company page clicks |
| `externalWebsiteConversions` | `number` | Number of conversions on external websites |
| `externalWebsitePostClickConversions` | `number` | Post-click conversions on external websites |
| `externalWebsitePostViewConversions` | `number` | Post-view conversions on external websites |
| `conversionValueInLocalCurrency` | `number` | Conversion value in local currency |
| `approximateMemberReach` | `number` | Approximate unique member reach |
| `cardClicks` | `number` | Number of carousel card clicks |
| `cardImpressions` | `number` | Number of carousel card impressions |
| `videoStarts` | `number` | Number of video starts |
| `videoViews` | `number` | Number of video views |
| `videoFirstQuartileCompletions` | `number` | Number of times video played to 25% |
| `videoMidpointCompletions` | `number` | Number of times video played to 50% |
| `videoThirdQuartileCompletions` | `number` | Number of times video played to 75% |
| `videoCompletions` | `number` | Number of times video played to 100% |
| `fullScreenPlays` | `number` | Number of full screen video plays |
| `oneClickLeads` | `number` | Number of one-click leads |
| `oneClickLeadFormOpens` | `number` | Number of one-click lead form opens |
| `otherEngagements` | `number` | Number of other engagements |
| `adUnitClicks` | `number` | Number of ad unit clicks |
| `actionClicks` | `number` | Number of action clicks |
| `textUrlClicks` | `number` | Number of text URL clicks |
| `commentLikes` | `number` | Number of comment likes |
| `sends` | `number` | Number of sends (InMail) |
| `opens` | `number` | Number of opens (InMail) |
| `downloadClicks` | `number` | Number of download clicks |
| `pivotValues` | `array` | Pivot values (URNs) for this analytics record |
| `start_date` | `string` | Start date of the ad analytics data |
| `end_date` | `string` | End date of the ad analytics data |

<details>
<summary><b>Response Schema</b></summary>

| Field Name | Type | Description |
|------------|------|-------------|
| `data` | `array` | List of matching records |
| `meta` | `object` | Pagination metadata |
| `meta.has_more` | `boolean` | Whether additional pages are available |
| `meta.cursor` | `string \| null` | Cursor for next page of results |
| `meta.took_ms` | `number \| null` | Query execution time in milliseconds |
| `data[].impressions` | `number` | Number of times the ad was shown |
| `data[].clicks` | `number` | Number of clicks on the ad |
| `data[].costInLocalCurrency` | `number` | Total cost in the accounts local currency |
| `data[].costInUsd` | `number` | Total cost in USD |
| `data[].likes` | `number` | Number of likes |
| `data[].shares` | `number` | Number of shares |
| `data[].comments` | `number` | Number of comments |
| `data[].reactions` | `number` | Number of reactions |
| `data[].follows` | `number` | Number of follows |
| `data[].totalEngagements` | `number` | Total number of engagements |
| `data[].landingPageClicks` | `number` | Number of landing page clicks |
| `data[].companyPageClicks` | `number` | Number of company page clicks |
| `data[].externalWebsiteConversions` | `number` | Number of conversions on external websites |
| `data[].externalWebsitePostClickConversions` | `number` | Post-click conversions on external websites |
| `data[].externalWebsitePostViewConversions` | `number` | Post-view conversions on external websites |
| `data[].conversionValueInLocalCurrency` | `number` | Conversion value in local currency |
| `data[].approximateMemberReach` | `number` | Approximate unique member reach |
| `data[].cardClicks` | `number` | Number of carousel card clicks |
| `data[].cardImpressions` | `number` | Number of carousel card impressions |
| `data[].videoStarts` | `number` | Number of video starts |
| `data[].videoViews` | `number` | Number of video views |
| `data[].videoFirstQuartileCompletions` | `number` | Number of times video played to 25% |
| `data[].videoMidpointCompletions` | `number` | Number of times video played to 50% |
| `data[].videoThirdQuartileCompletions` | `number` | Number of times video played to 75% |
| `data[].videoCompletions` | `number` | Number of times video played to 100% |
| `data[].fullScreenPlays` | `number` | Number of full screen video plays |
| `data[].oneClickLeads` | `number` | Number of one-click leads |
| `data[].oneClickLeadFormOpens` | `number` | Number of one-click lead form opens |
| `data[].otherEngagements` | `number` | Number of other engagements |
| `data[].adUnitClicks` | `number` | Number of ad unit clicks |
| `data[].actionClicks` | `number` | Number of action clicks |
| `data[].textUrlClicks` | `number` | Number of text URL clicks |
| `data[].commentLikes` | `number` | Number of comment likes |
| `data[].sends` | `number` | Number of sends (InMail) |
| `data[].opens` | `number` | Number of opens (InMail) |
| `data[].downloadClicks` | `number` | Number of download clicks |
| `data[].pivotValues` | `array` | Pivot values (URNs) for this analytics record |
| `data[].start_date` | `string` | Start date of the ad analytics data |
| `data[].end_date` | `string` | End date of the ad analytics data |

</details>

## Ad Creative Analytics

### Ad Creative Analytics List

Returns ad analytics data pivoted by creative. Provides performance metrics including clicks, impressions, spend, and engagement data grouped by creative.


#### Python SDK

```python
await linkedin_ads.ad_creative_analytics.list(
    q="<str>",
    pivot="<str>",
    time_granularity="<str>",
    date_range="<str>",
    creatives="<str>"
)
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/integrations/connectors/{your_connector_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "ad_creative_analytics",
    "action": "list",
    "params": {
        "q": "<str>",
        "pivot": "<str>",
        "timeGranularity": "<str>",
        "dateRange": "<str>",
        "creatives": "<str>"
    }
}'
```


#### Parameters

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `q` | `string` | Yes |  |
| `pivot` | `string` | Yes | Pivot dimension for analytics grouping |
| `timeGranularity` | `"DAILY" \| "MONTHLY" \| "ALL"` | Yes | Time granularity for analytics data |
| `dateRange` | `string` | Yes | Date range in LinkedIn format, e.g. (start:(year:2024,month:1,day:1),end:(year:2024,month:12,day:31)) |
| `creatives` | `string` | Yes | List of creative URNs, e.g. List(urn%3Ali%3AsponsoredCreative%3A123) |
| `fields` | `string` | No | Comma-separated list of metric fields to return |


<details>
<summary><b>Response Schema</b></summary>

#### Records

| Field Name | Type | Description |
|------------|------|-------------|
| `dateRange` | `null \| object` |  |
| `pivotValues` | `null \| array` |  |
| `impressions` | `null \| integer` |  |
| `clicks` | `null \| integer` |  |
| `costInLocalCurrency` | `null \| string` |  |
| `costInUsd` | `null \| string` |  |
| `likes` | `null \| integer` |  |
| `shares` | `null \| integer` |  |
| `comments` | `null \| integer` |  |
| `reactions` | `null \| integer` |  |
| `follows` | `null \| integer` |  |
| `totalEngagements` | `null \| integer` |  |
| `landingPageClicks` | `null \| integer` |  |
| `companyPageClicks` | `null \| integer` |  |
| `externalWebsiteConversions` | `null \| integer` |  |
| `externalWebsitePostClickConversions` | `null \| integer` |  |
| `externalWebsitePostViewConversions` | `null \| integer` |  |
| `conversionValueInLocalCurrency` | `null \| string` |  |
| `approximateMemberReach` | `null \| integer` |  |
| `cardClicks` | `null \| integer` |  |
| `cardImpressions` | `null \| integer` |  |
| `videoStarts` | `null \| integer` |  |
| `videoViews` | `null \| integer` |  |
| `videoFirstQuartileCompletions` | `null \| integer` |  |
| `videoMidpointCompletions` | `null \| integer` |  |
| `videoThirdQuartileCompletions` | `null \| integer` |  |
| `videoCompletions` | `null \| integer` |  |
| `fullScreenPlays` | `null \| integer` |  |
| `oneClickLeads` | `null \| integer` |  |
| `oneClickLeadFormOpens` | `null \| integer` |  |
| `otherEngagements` | `null \| integer` |  |
| `adUnitClicks` | `null \| integer` |  |
| `actionClicks` | `null \| integer` |  |
| `textUrlClicks` | `null \| integer` |  |
| `commentLikes` | `null \| integer` |  |
| `sends` | `null \| integer` |  |
| `opens` | `null \| integer` |  |
| `downloadClicks` | `null \| integer` |  |
| `jobApplications` | `null \| integer` |  |
| `jobApplyClicks` | `null \| integer` |  |
| `registrations` | `null \| integer` |  |
| `talentLeads` | `null \| integer` |  |
| `validWorkEmailLeads` | `null \| integer` |  |
| `postClickJobApplications` | `null \| integer` |  |
| `postClickJobApplyClicks` | `null \| integer` |  |
| `postClickRegistrations` | `null \| integer` |  |
| `postViewJobApplications` | `null \| integer` |  |
| `postViewJobApplyClicks` | `null \| integer` |  |
| `postViewRegistrations` | `null \| integer` |  |
| `leadGenerationMailContactInfoShares` | `null \| integer` |  |
| `leadGenerationMailInterestedClicks` | `null \| integer` |  |
| `documentCompletions` | `null \| integer` |  |
| `documentFirstQuartileCompletions` | `null \| integer` |  |
| `documentMidpointCompletions` | `null \| integer` |  |
| `documentThirdQuartileCompletions` | `null \| integer` |  |


</details>

### Ad Creative Analytics Search

Search and filter ad creative analytics records powered by Airbyte's data sync. This often provides additional fields and operators beyond what the API natively supports, making it easier to narrow down results before performing further operations. Only available in hosted mode.

#### Python SDK

```python
await linkedin_ads.ad_creative_analytics.search(
    query={"filter": {"eq": {"impressions": 0.0}}}
)
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/integrations/connectors/{your_connector_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "ad_creative_analytics",
    "action": "search",
    "params": {
        "query": {"filter": {"eq": {"impressions": 0.0}}}
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
| `impressions` | `number` | Number of times the ad was shown |
| `clicks` | `number` | Number of clicks on the ad |
| `costInLocalCurrency` | `number` | Total cost in the accounts local currency |
| `costInUsd` | `number` | Total cost in USD |
| `likes` | `number` | Number of likes |
| `shares` | `number` | Number of shares |
| `comments` | `number` | Number of comments |
| `reactions` | `number` | Number of reactions |
| `follows` | `number` | Number of follows |
| `totalEngagements` | `number` | Total number of engagements |
| `landingPageClicks` | `number` | Number of landing page clicks |
| `companyPageClicks` | `number` | Number of company page clicks |
| `externalWebsiteConversions` | `number` | Number of conversions on external websites |
| `externalWebsitePostClickConversions` | `number` | Post-click conversions on external websites |
| `externalWebsitePostViewConversions` | `number` | Post-view conversions on external websites |
| `conversionValueInLocalCurrency` | `number` | Conversion value in local currency |
| `approximateMemberReach` | `number` | Approximate unique member reach |
| `cardClicks` | `number` | Number of carousel card clicks |
| `cardImpressions` | `number` | Number of carousel card impressions |
| `videoStarts` | `number` | Number of video starts |
| `videoViews` | `number` | Number of video views |
| `videoFirstQuartileCompletions` | `number` | Number of times video played to 25% |
| `videoMidpointCompletions` | `number` | Number of times video played to 50% |
| `videoThirdQuartileCompletions` | `number` | Number of times video played to 75% |
| `videoCompletions` | `number` | Number of times video played to 100% |
| `fullScreenPlays` | `number` | Number of full screen video plays |
| `oneClickLeads` | `number` | Number of one-click leads |
| `oneClickLeadFormOpens` | `number` | Number of one-click lead form opens |
| `otherEngagements` | `number` | Number of other engagements |
| `adUnitClicks` | `number` | Number of ad unit clicks |
| `actionClicks` | `number` | Number of action clicks |
| `textUrlClicks` | `number` | Number of text URL clicks |
| `commentLikes` | `number` | Number of comment likes |
| `sends` | `number` | Number of sends (InMail) |
| `opens` | `number` | Number of opens (InMail) |
| `downloadClicks` | `number` | Number of download clicks |
| `pivotValues` | `array` | Pivot values (URNs) for this analytics record |
| `start_date` | `string` | Start date of the ad analytics data |
| `end_date` | `string` | End date of the ad analytics data |

<details>
<summary><b>Response Schema</b></summary>

| Field Name | Type | Description |
|------------|------|-------------|
| `data` | `array` | List of matching records |
| `meta` | `object` | Pagination metadata |
| `meta.has_more` | `boolean` | Whether additional pages are available |
| `meta.cursor` | `string \| null` | Cursor for next page of results |
| `meta.took_ms` | `number \| null` | Query execution time in milliseconds |
| `data[].impressions` | `number` | Number of times the ad was shown |
| `data[].clicks` | `number` | Number of clicks on the ad |
| `data[].costInLocalCurrency` | `number` | Total cost in the accounts local currency |
| `data[].costInUsd` | `number` | Total cost in USD |
| `data[].likes` | `number` | Number of likes |
| `data[].shares` | `number` | Number of shares |
| `data[].comments` | `number` | Number of comments |
| `data[].reactions` | `number` | Number of reactions |
| `data[].follows` | `number` | Number of follows |
| `data[].totalEngagements` | `number` | Total number of engagements |
| `data[].landingPageClicks` | `number` | Number of landing page clicks |
| `data[].companyPageClicks` | `number` | Number of company page clicks |
| `data[].externalWebsiteConversions` | `number` | Number of conversions on external websites |
| `data[].externalWebsitePostClickConversions` | `number` | Post-click conversions on external websites |
| `data[].externalWebsitePostViewConversions` | `number` | Post-view conversions on external websites |
| `data[].conversionValueInLocalCurrency` | `number` | Conversion value in local currency |
| `data[].approximateMemberReach` | `number` | Approximate unique member reach |
| `data[].cardClicks` | `number` | Number of carousel card clicks |
| `data[].cardImpressions` | `number` | Number of carousel card impressions |
| `data[].videoStarts` | `number` | Number of video starts |
| `data[].videoViews` | `number` | Number of video views |
| `data[].videoFirstQuartileCompletions` | `number` | Number of times video played to 25% |
| `data[].videoMidpointCompletions` | `number` | Number of times video played to 50% |
| `data[].videoThirdQuartileCompletions` | `number` | Number of times video played to 75% |
| `data[].videoCompletions` | `number` | Number of times video played to 100% |
| `data[].fullScreenPlays` | `number` | Number of full screen video plays |
| `data[].oneClickLeads` | `number` | Number of one-click leads |
| `data[].oneClickLeadFormOpens` | `number` | Number of one-click lead form opens |
| `data[].otherEngagements` | `number` | Number of other engagements |
| `data[].adUnitClicks` | `number` | Number of ad unit clicks |
| `data[].actionClicks` | `number` | Number of action clicks |
| `data[].textUrlClicks` | `number` | Number of text URL clicks |
| `data[].commentLikes` | `number` | Number of comment likes |
| `data[].sends` | `number` | Number of sends (InMail) |
| `data[].opens` | `number` | Number of opens (InMail) |
| `data[].downloadClicks` | `number` | Number of download clicks |
| `data[].pivotValues` | `array` | Pivot values (URNs) for this analytics record |
| `data[].start_date` | `string` | Start date of the ad analytics data |
| `data[].end_date` | `string` | End date of the ad analytics data |

</details>

