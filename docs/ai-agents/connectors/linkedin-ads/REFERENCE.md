# Linkedin-Ads full reference

This is the full reference documentation for the Linkedin-Ads agent connector.

## Supported entities and actions

The Linkedin-Ads connector supports the following entities and actions.

| Entity | Actions |
|--------|---------|
| Accounts | [List](#accounts-list), [Create](#accounts-create), [Get](#accounts-get), [Update](#accounts-update), [Delete](#accounts-delete), [Context Store Search](#accounts-context-store-search) |
| Account Users | [List](#account-users-list), [Update](#account-users-update), [Create](#account-users-create), [Delete](#account-users-delete), [Context Store Search](#account-users-context-store-search) |
| Campaigns | [List](#campaigns-list), [Create](#campaigns-create), [Get](#campaigns-get), [Update](#campaigns-update), [Delete](#campaigns-delete), [Context Store Search](#campaigns-context-store-search) |
| Campaign Groups | [List](#campaign-groups-list), [Create](#campaign-groups-create), [Get](#campaign-groups-get), [Update](#campaign-groups-update), [Delete](#campaign-groups-delete), [Context Store Search](#campaign-groups-context-store-search) |
| Creatives | [List](#creatives-list), [Create](#creatives-create), [Get](#creatives-get), [Update](#creatives-update), [Delete](#creatives-delete), [Context Store Search](#creatives-context-store-search) |
| Conversions | [List](#conversions-list), [Create](#conversions-create), [Get](#conversions-get), [Update](#conversions-update), [Context Store Search](#conversions-context-store-search) |
| Conversion Events | [Create](#conversion-events-create) |
| Campaign Conversions | [Create](#campaign-conversions-create), [Delete](#campaign-conversions-delete) |
| Ad Campaign Analytics | [List](#ad-campaign-analytics-list), [Context Store Search](#ad-campaign-analytics-context-store-search) |
| Ad Creative Analytics | [List](#ad-creative-analytics-list), [Context Store Search](#ad-creative-analytics-context-store-search) |
| Ad Impression Device Analytics | [List](#ad-impression-device-analytics-list), [Context Store Search](#ad-impression-device-analytics-context-store-search) |
| Ad Member Company Analytics | [List](#ad-member-company-analytics-list), [Context Store Search](#ad-member-company-analytics-context-store-search) |
| Ad Member Company Size Analytics | [List](#ad-member-company-size-analytics-list), [Context Store Search](#ad-member-company-size-analytics-context-store-search) |
| Ad Member Country Analytics | [List](#ad-member-country-analytics-list), [Context Store Search](#ad-member-country-analytics-context-store-search) |
| Ad Member Industry Analytics | [List](#ad-member-industry-analytics-list), [Context Store Search](#ad-member-industry-analytics-context-store-search) |
| Ad Member Job Function Analytics | [List](#ad-member-job-function-analytics-list), [Context Store Search](#ad-member-job-function-analytics-context-store-search) |
| Ad Member Job Title Analytics | [List](#ad-member-job-title-analytics-list), [Context Store Search](#ad-member-job-title-analytics-context-store-search) |
| Ad Member Region Analytics | [List](#ad-member-region-analytics-list), [Context Store Search](#ad-member-region-analytics-context-store-search) |
| Ad Member Seniority Analytics | [List](#ad-member-seniority-analytics-list), [Context Store Search](#ad-member-seniority-analytics-context-store-search) |
| Lead Forms | [List](#lead-forms-list), [Context Store Search](#lead-forms-context-store-search) |
| Lead Form Responses | [List](#lead-form-responses-list), [Context Store Search](#lead-form-responses-context-store-search) |

## Accounts

### Accounts List

Returns a list of ad accounts the authenticated user has access to

#### CLI

```bash
airbyte-agent connectors execute --json '{
  "workspace": "<your_workspace_name>",
  "name": "linkedin-ads",
  "entity": "accounts",
  "action": "list",
  "params": {
    "q": "<str>"
  }
}'
```

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
| `q` | `string` | Yes | LinkedIn API finder method for querying ad accounts |
| `pageSize` | `integer` | No | Number of items per page |
| `pageToken` | `string` | No | Token for the next page of results |


<details>
<summary><b>Response Schema</b></summary>



#### Meta

| Field Name | Type | Description |
|------------|------|-------------|
| `nextPageToken` | `string` |  |

</details>

### Accounts Create

Creates a new ad account. Only type BUSINESS can be created via the API (ENTERPRISE accounts cannot). Requires the rw_ads OAuth scope. The new account ID is returned in the x-restli-id response header.


#### CLI

```bash
airbyte-agent connectors execute --json '{
  "workspace": "<your_workspace_name>",
  "name": "linkedin-ads",
  "entity": "accounts",
  "action": "create",
  "params": {
    "name": "<str>",
    "type": "<str>",
    "currency": "<str>",
    "reference": "<str>",
    "test": true
  }
}'
```

#### Python SDK

```python
await linkedin_ads.accounts.create(
    name="<str>",
    type="<str>",
    currency="<str>",
    reference="<str>",
    test=True
)
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/integrations/connectors/{your_connector_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "accounts",
    "action": "create",
    "params": {
        "name": "<str>",
        "type": "<str>",
        "currency": "<str>",
        "reference": "<str>",
        "test": True
    }
}'
```


#### Parameters

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `name` | `string` | Yes | Ad account name |
| `type` | `"BUSINESS"` | Yes | Account type; only BUSINESS accounts can be created via the API |
| `currency` | `string` | No | ISO 4217 currency code, e.g. USD (defaults to USD) |
| `reference` | `string` | No | Optional owning organization URN, e.g. urn:li:organization:123456 |
| `test` | `boolean` | No | Whether to create a test account |


<details>
<summary><b>Response Schema</b></summary>



#### Meta

| Field Name | Type | Description |
|------------|------|-------------|
| `created_id` | `string` |  |

</details>

### Accounts Get

Get a single ad account by ID

#### CLI

```bash
airbyte-agent connectors execute --json '{
  "workspace": "<your_workspace_name>",
  "name": "linkedin-ads",
  "entity": "accounts",
  "action": "get",
  "params": {
    "id": 0
  }
}'
```

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

### Accounts Update

Partially updates an ad account using the Rest.li PARTIAL_UPDATE pattern: the body wraps the fields to change in patch.$set. Requires the rw_ads OAuth scope; most account fields require the ACCOUNT_BILLING_ADMIN role. To soft-delete a non-DRAFT account, set status to PENDING_DELETION here (billing admin only).


#### CLI

```bash
airbyte-agent connectors execute --json '{
  "workspace": "<your_workspace_name>",
  "name": "linkedin-ads",
  "entity": "accounts",
  "action": "update",
  "params": {
    "patch": {
      "$set": {}
    },
    "id": 0
  }
}'
```

#### Python SDK

```python
await linkedin_ads.accounts.update(
    patch={
        "$set": {}
    },
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
    "action": "update",
    "params": {
        "patch": {
            "$set": {}
        },
        "id": 0
    }
}'
```


#### Parameters

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `patch` | `object` | Yes |  |
| `patch.$set` | `object` | Yes | Map of field names to their new values |
| `id` | `integer` | Yes | Ad account ID |


### Accounts Delete

Hard-deletes an ad account. Only accounts in DRAFT status accept a true DELETE; for non-DRAFT accounts use the update operation to set status to PENDING_DELETION. Both forms require the ACCOUNT_BILLING_ADMIN role and the rw_ads OAuth scope.


#### CLI

```bash
airbyte-agent connectors execute --json '{
  "workspace": "<your_workspace_name>",
  "name": "linkedin-ads",
  "entity": "accounts",
  "action": "delete",
  "params": {
    "id": 0
  }
}'
```

#### Python SDK

```python
await linkedin_ads.accounts.delete(
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
    "action": "delete",
    "params": {
        "id": 0
    }
}'
```


#### Parameters

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `id` | `integer` | Yes | Ad account ID |


### Accounts Context Store Search

Search and filter accounts records powered by Airbyte's data sync. This often provides additional fields and operators beyond what the API natively supports, making it easier to narrow down results before performing further operations. Only available in hosted mode.

#### CLI

```bash
airbyte-agent connectors execute --json '{
  "workspace": "<your_workspace_name>",
  "name": "linkedin-ads",
  "entity": "accounts",
  "action": "context_store_search",
  "params": {
    "query": {
      "filter": {
        "eq": {
          "test": true
        }
      }
    }
  }
}'
```

#### Python SDK

```python
await linkedin_ads.accounts.context_store_search(
    query={"filter": {"eq": {"test": True}}}
)
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/integrations/connectors/{your_connector_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "accounts",
    "action": "context_store_search",
    "params": {
        "query": {"filter": {"eq": {"test": True}}}
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
| `test` | `boolean` | Flag indicating if the account is in a test mode. |
| `notifiedOnCreativeRejection` | `boolean` | Flag for notifications on creative rejection. |
| `notifiedOnNewFeaturesEnabled` | `boolean` | Flag for notifications on new features being enabled. |
| `notifiedOnEndOfCampaign` | `boolean` | Flag for notifications on the end of campaign. |
| `servingStatuses` | `array` | The serving statuses associated with the account. |
| `notifiedOnCampaignOptimization` | `boolean` | Flag for notifications on campaign optimization. |
| `type` | `string` | The type or category of the account. |
| `version` | `object` | The version information related to the account. |
| `reference` | `string` | A reference identifier for the account. |
| `notifiedOnCreativeApproval` | `boolean` | Flag for notifications on creative approval. |
| `created` | `string` | The timestamp indicating when the account was created. |
| `lastModified` | `string` | The timestamp of the last modification made to the account. |
| `name` | `string` | The name of the account. |
| `currency` | `string` | The currency used for financial transactions in the account. |
| `id` | `integer` | The unique identifier for the account. |
| `status` | `string` | The status of the account. |

<details>
<summary><b>Response Schema</b></summary>

| Field Name | Type | Description |
|------------|------|-------------|
| `data` | `array` | List of matching records |
| `meta` | `object` | Pagination metadata |
| `meta.has_more` | `boolean` | Whether additional pages are available |
| `meta.cursor` | `string \| null` | Cursor for next page of results |
| `meta.took_ms` | `number \| null` | Query execution time in milliseconds |
| `data[].test` | `boolean` | Flag indicating if the account is in a test mode. |
| `data[].notifiedOnCreativeRejection` | `boolean` | Flag for notifications on creative rejection. |
| `data[].notifiedOnNewFeaturesEnabled` | `boolean` | Flag for notifications on new features being enabled. |
| `data[].notifiedOnEndOfCampaign` | `boolean` | Flag for notifications on the end of campaign. |
| `data[].servingStatuses` | `array` | The serving statuses associated with the account. |
| `data[].notifiedOnCampaignOptimization` | `boolean` | Flag for notifications on campaign optimization. |
| `data[].type` | `string` | The type or category of the account. |
| `data[].version` | `object` | The version information related to the account. |
| `data[].reference` | `string` | A reference identifier for the account. |
| `data[].notifiedOnCreativeApproval` | `boolean` | Flag for notifications on creative approval. |
| `data[].created` | `string` | The timestamp indicating when the account was created. |
| `data[].lastModified` | `string` | The timestamp of the last modification made to the account. |
| `data[].name` | `string` | The name of the account. |
| `data[].currency` | `string` | The currency used for financial transactions in the account. |
| `data[].id` | `integer` | The unique identifier for the account. |
| `data[].status` | `string` | The status of the account. |

</details>

## Account Users

### Account Users List

Returns a list of users associated with ad accounts

#### CLI

```bash
airbyte-agent connectors execute --json '{
  "workspace": "<your_workspace_name>",
  "name": "linkedin-ads",
  "entity": "account_users",
  "action": "list",
  "params": {
    "q": "<str>",
    "accounts": "<str>"
  }
}'
```

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
| `q` | `string` | Yes | LinkedIn API finder method for querying by account URN |
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
| `start` | `integer` |  |
| `count` | `integer` |  |
| `total` | `integer` |  |

</details>

### Account Users Update

Partially updates an account user's role using the Rest.li PARTIAL_UPDATE pattern: the body wraps the fields to change in patch.$set (e.g. \{"patch": \{"$set": \{"role": "CAMPAIGN_MANAGER"\}\}\}). Pass the raw account and user URNs as parameters; they are URL-encoded automatically. Requires the rw_ads OAuth scope and the ACCOUNT_BILLING_ADMIN or ACCOUNT_MANAGER role.


#### CLI

```bash
airbyte-agent connectors execute --json '{
  "workspace": "<your_workspace_name>",
  "name": "linkedin-ads",
  "entity": "account_users",
  "action": "update",
  "params": {
    "patch": {
      "$set": {}
    },
    "account": "<str>",
    "user": "<str>"
  }
}'
```

#### Python SDK

```python
await linkedin_ads.account_users.update(
    patch={
        "$set": {}
    },
    account="<str>",
    user="<str>"
)
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/integrations/connectors/{your_connector_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "account_users",
    "action": "update",
    "params": {
        "patch": {
            "$set": {}
        },
        "account": "<str>",
        "user": "<str>"
    }
}'
```


#### Parameters

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `patch` | `object` | Yes |  |
| `patch.$set` | `object` | Yes | Map of field names to their new values |
| `account` | `string` | Yes | Sponsored account URN, e.g. urn:li:sponsoredAccount:123456 |
| `user` | `string` | Yes | Person URN, e.g. urn:li:person:abc123 |


### Account Users Create

Grants a user a role on an ad account. Note the non-standard Rest.li compound-key shape: this is a PUT (not POST) keyed by both the account and user URNs. Pass the raw URNs as parameters; they are URL-encoded automatically. Requires the rw_ads OAuth scope and the ACCOUNT_BILLING_ADMIN or ACCOUNT_MANAGER role.


#### CLI

```bash
airbyte-agent connectors execute --json '{
  "workspace": "<your_workspace_name>",
  "name": "linkedin-ads",
  "entity": "account_users",
  "action": "create",
  "params": {
    "role": "<str>",
    "account": "<str>",
    "user": "<str>"
  }
}'
```

#### Python SDK

```python
await linkedin_ads.account_users.create(
    role="<str>",
    account="<str>",
    user="<str>"
)
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/integrations/connectors/{your_connector_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "account_users",
    "action": "create",
    "params": {
        "role": "<str>",
        "account": "<str>",
        "user": "<str>"
    }
}'
```


#### Parameters

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `role` | `"ACCOUNT_BILLING_ADMIN" \| "ACCOUNT_MANAGER" \| "CAMPAIGN_MANAGER" \| "CREATIVE_MANAGER" \| "VIEWER"` | Yes | Role to grant on the ad account |
| `account` | `string` | Yes | Sponsored account URN, e.g. urn:li:sponsoredAccount:123456 |
| `user` | `string` | Yes | Person URN, e.g. urn:li:person:abc123 |


### Account Users Delete

Removes a user's role from an ad account. Pass the raw account and user URNs as parameters; they are URL-encoded automatically. Requires the rw_ads OAuth scope and the ACCOUNT_BILLING_ADMIN or ACCOUNT_MANAGER role.


#### CLI

```bash
airbyte-agent connectors execute --json '{
  "workspace": "<your_workspace_name>",
  "name": "linkedin-ads",
  "entity": "account_users",
  "action": "delete",
  "params": {
    "account": "<str>",
    "user": "<str>"
  }
}'
```

#### Python SDK

```python
await linkedin_ads.account_users.delete(
    account="<str>",
    user="<str>"
)
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/integrations/connectors/{your_connector_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "account_users",
    "action": "delete",
    "params": {
        "account": "<str>",
        "user": "<str>"
    }
}'
```


#### Parameters

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `account` | `string` | Yes | Sponsored account URN, e.g. urn:li:sponsoredAccount:123456 |
| `user` | `string` | Yes | Person URN, e.g. urn:li:person:abc123 |


### Account Users Context Store Search

Search and filter account users records powered by Airbyte's data sync. This often provides additional fields and operators beyond what the API natively supports, making it easier to narrow down results before performing further operations. Only available in hosted mode.

#### CLI

```bash
airbyte-agent connectors execute --json '{
  "workspace": "<your_workspace_name>",
  "name": "linkedin-ads",
  "entity": "account_users",
  "action": "context_store_search",
  "params": {
    "query": {
      "filter": {
        "eq": {
          "account": "<str>"
        }
      }
    }
  }
}'
```

#### Python SDK

```python
await linkedin_ads.account_users.context_store_search(
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
    "action": "context_store_search",
    "params": {
        "query": {"filter": {"eq": {"account": "<str>"}}}
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
| `account` | `string` | The account associated with the user |
| `created` | `string` | The date and time when the user account was created |
| `lastModified` | `string` | The date and time when the user account was last modified |
| `role` | `string` | The role assigned to the user in the account |
| `user` | `string` | The user details including name, email, etc. |

<details>
<summary><b>Response Schema</b></summary>

| Field Name | Type | Description |
|------------|------|-------------|
| `data` | `array` | List of matching records |
| `meta` | `object` | Pagination metadata |
| `meta.has_more` | `boolean` | Whether additional pages are available |
| `meta.cursor` | `string \| null` | Cursor for next page of results |
| `meta.took_ms` | `number \| null` | Query execution time in milliseconds |
| `data[].account` | `string` | The account associated with the user |
| `data[].created` | `string` | The date and time when the user account was created |
| `data[].lastModified` | `string` | The date and time when the user account was last modified |
| `data[].role` | `string` | The role assigned to the user in the account |
| `data[].user` | `string` | The user details including name, email, etc. |

</details>

## Campaigns

### Campaigns List

Returns a list of campaigns for an ad account

#### CLI

```bash
airbyte-agent connectors execute --json '{
  "workspace": "<your_workspace_name>",
  "name": "linkedin-ads",
  "entity": "campaigns",
  "action": "list",
  "params": {
    "account_id": 0,
    "q": "<str>"
  }
}'
```

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
| `q` | `string` | Yes | LinkedIn API finder method for querying campaigns |
| `pageSize` | `integer` | No | Number of items per page |
| `pageToken` | `string` | No | Token for the next page of results |


<details>
<summary><b>Response Schema</b></summary>



#### Meta

| Field Name | Type | Description |
|------------|------|-------------|
| `nextPageToken` | `string` |  |

</details>

### Campaigns Create

Creates a new campaign in the ad account. Requires the rw_ads OAuth scope and an ad-account role of CAMPAIGN_MANAGER or higher (VIEWER is read-only). The new campaign ID is returned in the x-restli-id response header. Commonly required fields beyond account and name include type, costType, unitCost or dailyBudget, locale, and targetingCriteria; LinkedIn returns a descriptive 400 when a required field is missing.


#### CLI

```bash
airbyte-agent connectors execute --json '{
  "workspace": "<your_workspace_name>",
  "name": "linkedin-ads",
  "entity": "campaigns",
  "action": "create",
  "params": {
    "account": "<str>",
    "name": "<str>",
    "politicalIntent": "<str>",
    "campaignGroup": "<str>",
    "type": "<str>",
    "objectiveType": "<str>",
    "status": "<str>",
    "costType": "<str>",
    "dailyBudget": {},
    "unitCost": {},
    "locale": {},
    "runSchedule": {},
    "targetingCriteria": {},
    "audienceExpansionEnabled": true,
    "offsiteDeliveryEnabled": true,
    "creativeSelection": "<str>",
    "account_id": 0
  }
}'
```

#### Python SDK

```python
await linkedin_ads.campaigns.create(
    account="<str>",
    name="<str>",
    political_intent="<str>",
    campaign_group="<str>",
    type="<str>",
    objective_type="<str>",
    status="<str>",
    cost_type="<str>",
    daily_budget={},
    unit_cost={},
    locale={},
    run_schedule={},
    targeting_criteria={},
    audience_expansion_enabled=True,
    offsite_delivery_enabled=True,
    creative_selection="<str>",
    account_id=0
)
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/integrations/connectors/{your_connector_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "campaigns",
    "action": "create",
    "params": {
        "account": "<str>",
        "name": "<str>",
        "politicalIntent": "<str>",
        "campaignGroup": "<str>",
        "type": "<str>",
        "objectiveType": "<str>",
        "status": "<str>",
        "costType": "<str>",
        "dailyBudget": {},
        "unitCost": {},
        "locale": {},
        "runSchedule": {},
        "targetingCriteria": {},
        "audienceExpansionEnabled": True,
        "offsiteDeliveryEnabled": True,
        "creativeSelection": "<str>",
        "account_id": 0
    }
}'
```


#### Parameters

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `account` | `string` | Yes | Sponsored account URN; must match the account_id path parameter, e.g. urn:li:sponsoredAccount:123456 |
| `name` | `string` | Yes | Campaign name |
| `politicalIntent` | `"NOT_POLITICAL" \| "POLITICAL"` | Yes | Whether the campaign contains political content; LinkedIn requires this on create |
| `campaignGroup` | `string` | No | Campaign group URN, e.g. urn:li:sponsoredCampaignGroup:123456 |
| `type` | `"TEXT_AD" \| "SPONSORED_UPDATES" \| "SPONSORED_INMAILS" \| "DYNAMIC"` | No | Campaign format |
| `objectiveType` | `string` | No | Campaign objective, e.g. BRAND_AWARENESS, WEBSITE_VISIT, LEAD_GENERATION, WEBSITE_CONVERSION, VIDEO_VIEW, ENGAGEMENT, JOB_APPLICANT |
| `status` | `"ACTIVE" \| "PAUSED" \| "DRAFT"` | No | Initial campaign status |
| `costType` | `string` | No | Bidding cost type, e.g. CPM, CPC, CPV |
| `dailyBudget` | `object` | No | Daily budget |
| `dailyBudget.amount` | `string` | No |  |
| `dailyBudget.currencyCode` | `string` | No |  |
| `unitCost` | `object` | No | Bid amount per unit (per click, per impression, etc.) |
| `unitCost.amount` | `string` | No |  |
| `unitCost.currencyCode` | `string` | No |  |
| `locale` | `object` | No | Campaign locale |
| `locale.country` | `string` | No |  |
| `locale.language` | `string` | No |  |
| `runSchedule` | `object` | Yes | Scheduled run window (epoch milliseconds) |
| `runSchedule.start` | `integer` | No |  |
| `runSchedule.end` | `integer` | No |  |
| `targetingCriteria` | `object` | No | Audience targeting criteria (include/exclude clauses) |
| `audienceExpansionEnabled` | `boolean` | No | Whether audience expansion is enabled |
| `offsiteDeliveryEnabled` | `boolean` | Yes | Whether ads may be served on the LinkedIn Audience Network |
| `creativeSelection` | `string` | No | Creative rotation strategy, e.g. ROUND_ROBIN, OPTIMIZED |
| `account_id` | `integer` | Yes | Ad account ID |


<details>
<summary><b>Response Schema</b></summary>



#### Meta

| Field Name | Type | Description |
|------------|------|-------------|
| `created_id` | `string` |  |

</details>

### Campaigns Get

Get a single campaign by ID

#### CLI

```bash
airbyte-agent connectors execute --json '{
  "workspace": "<your_workspace_name>",
  "name": "linkedin-ads",
  "entity": "campaigns",
  "action": "get",
  "params": {
    "account_id": 0,
    "id": 0
  }
}'
```

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

### Campaigns Update

Partially updates a campaign using the Rest.li PARTIAL_UPDATE pattern: the body wraps the fields to change in patch.$set. Requires the rw_ads OAuth scope and a CAMPAIGN_MANAGER or higher ad-account role. Note that $set on an array field (e.g. targetingCriteria lists) replaces the whole array, so re-send all existing elements. To soft-delete a non-DRAFT campaign, set status to PENDING_DELETION here.


#### CLI

```bash
airbyte-agent connectors execute --json '{
  "workspace": "<your_workspace_name>",
  "name": "linkedin-ads",
  "entity": "campaigns",
  "action": "update",
  "params": {
    "patch": {
      "$set": {}
    },
    "account_id": 0,
    "id": 0
  }
}'
```

#### Python SDK

```python
await linkedin_ads.campaigns.update(
    patch={
        "$set": {}
    },
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
    "action": "update",
    "params": {
        "patch": {
            "$set": {}
        },
        "account_id": 0,
        "id": 0
    }
}'
```


#### Parameters

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `patch` | `object` | Yes |  |
| `patch.$set` | `object` | Yes | Map of field names to their new values |
| `account_id` | `integer` | Yes | Ad account ID |
| `id` | `integer` | Yes | Campaign ID |


### Campaigns Delete

Hard-deletes a campaign. Only campaigns in DRAFT status accept a true DELETE; for non-DRAFT campaigns LinkedIn requires a soft delete instead - use the update operation to set status to PENDING_DELETION. Requires the rw_ads OAuth scope and a CAMPAIGN_MANAGER or higher ad-account role.


#### CLI

```bash
airbyte-agent connectors execute --json '{
  "workspace": "<your_workspace_name>",
  "name": "linkedin-ads",
  "entity": "campaigns",
  "action": "delete",
  "params": {
    "account_id": 0,
    "id": 0
  }
}'
```

#### Python SDK

```python
await linkedin_ads.campaigns.delete(
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
    "action": "delete",
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


### Campaigns Context Store Search

Search and filter campaigns records powered by Airbyte's data sync. This often provides additional fields and operators beyond what the API natively supports, making it easier to narrow down results before performing further operations. Only available in hosted mode.

#### CLI

```bash
airbyte-agent connectors execute --json '{
  "workspace": "<your_workspace_name>",
  "name": "linkedin-ads",
  "entity": "campaigns",
  "action": "context_store_search",
  "params": {
    "query": {
      "filter": {
        "eq": {
          "targetingCriteria": {}
        }
      }
    }
  }
}'
```

#### Python SDK

```python
await linkedin_ads.campaigns.context_store_search(
    query={"filter": {"eq": {"targetingCriteria": {}}}}
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
        "query": {"filter": {"eq": {"targetingCriteria": {}}}}
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
| `targetingCriteria` | `object` | Criteria for targeting in the campaign. |
| `servingStatuses` | `array` | The serving statuses of the campaign. |
| `type` | `string` | The type of campaign. |
| `locale` | `object` | The locale settings for the campaign. |
| `version` | `object` | The version information for the campaign. |
| `associatedEntity` | `string` | The entity associated with the campaign. |
| `runSchedule` | `object` | The schedule for running the campaign. |
| `optimizationTargetType` | `string` | The type of optimization target for the campaign. |
| `created` | `string` | The date and time when the campaign was created. |
| `lastModified` | `string` | The date and time when the campaign was last modified. |
| `campaignGroup` | `string` | The group to which the campaign belongs. |
| `dailyBudget` | `object` | The daily budget set for the campaign. |
| `totalBudget` | `object` | The total budget amount for the campaign. |
| `unitCost` | `object` | The unit cost for the campaign. |
| `creativeSelection` | `string` | Information about the creative selection for the campaign. |
| `costType` | `string` | The type of cost associated with the campaign. |
| `name` | `string` | The name of the campaign. |
| `offsiteDeliveryEnabled` | `boolean` | Indicates if offsite delivery is enabled for the campaign. |
| `id` | `integer` | The unique identifier of the campaign. |
| `audienceExpansionEnabled` | `boolean` | Indicates if audience expansion is enabled for this campaign. |
| `test` | `boolean` | Indicates if the campaign is a test campaign. |
| `account` | `string` | The account associated with the campaign data. |
| `status` | `string` | The status of the campaign. |
| `storyDeliveryEnabled` | `boolean` | Indicates if story delivery is enabled for the campaign. |
| `pacingStrategy` | `string` | The pacing strategy for the campaign. |
| `format` | `string` | The format of the campaign. |
| `objectiveType` | `string` | The type of objective for the campaign. |
| `offsitePreferences` | `object` | Preferences related to offsite delivery. |

<details>
<summary><b>Response Schema</b></summary>

| Field Name | Type | Description |
|------------|------|-------------|
| `data` | `array` | List of matching records |
| `meta` | `object` | Pagination metadata |
| `meta.has_more` | `boolean` | Whether additional pages are available |
| `meta.cursor` | `string \| null` | Cursor for next page of results |
| `meta.took_ms` | `number \| null` | Query execution time in milliseconds |
| `data[].targetingCriteria` | `object` | Criteria for targeting in the campaign. |
| `data[].servingStatuses` | `array` | The serving statuses of the campaign. |
| `data[].type` | `string` | The type of campaign. |
| `data[].locale` | `object` | The locale settings for the campaign. |
| `data[].version` | `object` | The version information for the campaign. |
| `data[].associatedEntity` | `string` | The entity associated with the campaign. |
| `data[].runSchedule` | `object` | The schedule for running the campaign. |
| `data[].optimizationTargetType` | `string` | The type of optimization target for the campaign. |
| `data[].created` | `string` | The date and time when the campaign was created. |
| `data[].lastModified` | `string` | The date and time when the campaign was last modified. |
| `data[].campaignGroup` | `string` | The group to which the campaign belongs. |
| `data[].dailyBudget` | `object` | The daily budget set for the campaign. |
| `data[].totalBudget` | `object` | The total budget amount for the campaign. |
| `data[].unitCost` | `object` | The unit cost for the campaign. |
| `data[].creativeSelection` | `string` | Information about the creative selection for the campaign. |
| `data[].costType` | `string` | The type of cost associated with the campaign. |
| `data[].name` | `string` | The name of the campaign. |
| `data[].offsiteDeliveryEnabled` | `boolean` | Indicates if offsite delivery is enabled for the campaign. |
| `data[].id` | `integer` | The unique identifier of the campaign. |
| `data[].audienceExpansionEnabled` | `boolean` | Indicates if audience expansion is enabled for this campaign. |
| `data[].test` | `boolean` | Indicates if the campaign is a test campaign. |
| `data[].account` | `string` | The account associated with the campaign data. |
| `data[].status` | `string` | The status of the campaign. |
| `data[].storyDeliveryEnabled` | `boolean` | Indicates if story delivery is enabled for the campaign. |
| `data[].pacingStrategy` | `string` | The pacing strategy for the campaign. |
| `data[].format` | `string` | The format of the campaign. |
| `data[].objectiveType` | `string` | The type of objective for the campaign. |
| `data[].offsitePreferences` | `object` | Preferences related to offsite delivery. |

</details>

## Campaign Groups

### Campaign Groups List

Returns a list of campaign groups for an ad account

#### CLI

```bash
airbyte-agent connectors execute --json '{
  "workspace": "<your_workspace_name>",
  "name": "linkedin-ads",
  "entity": "campaign_groups",
  "action": "list",
  "params": {
    "account_id": 0,
    "q": "<str>"
  }
}'
```

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
| `q` | `string` | Yes | LinkedIn API finder method for querying campaign groups |
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

### Campaign Groups Create

Creates a new campaign group in the ad account. Requires the rw_ads OAuth scope and a CAMPAIGN_MANAGER or higher ad-account role. The new campaign group ID is returned in the x-restli-id response header. runSchedule.start is required when creating with ACTIVE status.


#### CLI

```bash
airbyte-agent connectors execute --json '{
  "workspace": "<your_workspace_name>",
  "name": "linkedin-ads",
  "entity": "campaign_groups",
  "action": "create",
  "params": {
    "account": "<str>",
    "name": "<str>",
    "status": "<str>",
    "runSchedule": {},
    "totalBudget": {},
    "objectiveType": "<str>",
    "account_id": 0
  }
}'
```

#### Python SDK

```python
await linkedin_ads.campaign_groups.create(
    account="<str>",
    name="<str>",
    status="<str>",
    run_schedule={},
    total_budget={},
    objective_type="<str>",
    account_id=0
)
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/integrations/connectors/{your_connector_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "campaign_groups",
    "action": "create",
    "params": {
        "account": "<str>",
        "name": "<str>",
        "status": "<str>",
        "runSchedule": {},
        "totalBudget": {},
        "objectiveType": "<str>",
        "account_id": 0
    }
}'
```


#### Parameters

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `account` | `string` | Yes | Sponsored account URN; must match the account_id path parameter, e.g. urn:li:sponsoredAccount:123456 |
| `name` | `string` | Yes | Campaign group name |
| `status` | `"ACTIVE" \| "DRAFT"` | No | Initial status |
| `runSchedule` | `object` | Yes | Scheduled run window (epoch milliseconds) |
| `runSchedule.start` | `integer` | No |  |
| `runSchedule.end` | `integer` | No |  |
| `totalBudget` | `object` | No | Total budget across the group's lifetime |
| `totalBudget.amount` | `string` | No |  |
| `totalBudget.currencyCode` | `string` | No |  |
| `objectiveType` | `string` | No | Objective shared by campaigns in this group |
| `account_id` | `integer` | Yes | Ad account ID |


<details>
<summary><b>Response Schema</b></summary>



#### Meta

| Field Name | Type | Description |
|------------|------|-------------|
| `created_id` | `string` |  |

</details>

### Campaign Groups Get

Get a single campaign group by ID

#### CLI

```bash
airbyte-agent connectors execute --json '{
  "workspace": "<your_workspace_name>",
  "name": "linkedin-ads",
  "entity": "campaign_groups",
  "action": "get",
  "params": {
    "account_id": 0,
    "id": 0
  }
}'
```

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

### Campaign Groups Update

Partially updates a campaign group using the Rest.li PARTIAL_UPDATE pattern: the body wraps the fields to change in patch.$set. Requires the rw_ads OAuth scope and a CAMPAIGN_MANAGER or higher ad-account role. $set on an array field replaces the whole array, so re-send all existing elements. To soft-delete a non-DRAFT campaign group, set status to PENDING_DELETION here.


#### CLI

```bash
airbyte-agent connectors execute --json '{
  "workspace": "<your_workspace_name>",
  "name": "linkedin-ads",
  "entity": "campaign_groups",
  "action": "update",
  "params": {
    "patch": {
      "$set": {}
    },
    "account_id": 0,
    "id": 0
  }
}'
```

#### Python SDK

```python
await linkedin_ads.campaign_groups.update(
    patch={
        "$set": {}
    },
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
    "action": "update",
    "params": {
        "patch": {
            "$set": {}
        },
        "account_id": 0,
        "id": 0
    }
}'
```


#### Parameters

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `patch` | `object` | Yes |  |
| `patch.$set` | `object` | Yes | Map of field names to their new values |
| `account_id` | `integer` | Yes | Ad account ID |
| `id` | `integer` | Yes | Campaign group ID |


### Campaign Groups Delete

Hard-deletes a campaign group. Only campaign groups in DRAFT status accept a true DELETE; for non-DRAFT campaign groups LinkedIn requires a soft delete instead - use the update operation to set status to PENDING_DELETION. Requires the rw_ads OAuth scope and a CAMPAIGN_MANAGER or higher ad-account role.


#### CLI

```bash
airbyte-agent connectors execute --json '{
  "workspace": "<your_workspace_name>",
  "name": "linkedin-ads",
  "entity": "campaign_groups",
  "action": "delete",
  "params": {
    "account_id": 0,
    "id": 0
  }
}'
```

#### Python SDK

```python
await linkedin_ads.campaign_groups.delete(
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
    "action": "delete",
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


### Campaign Groups Context Store Search

Search and filter campaign groups records powered by Airbyte's data sync. This often provides additional fields and operators beyond what the API natively supports, making it easier to narrow down results before performing further operations. Only available in hosted mode.

#### CLI

```bash
airbyte-agent connectors execute --json '{
  "workspace": "<your_workspace_name>",
  "name": "linkedin-ads",
  "entity": "campaign_groups",
  "action": "context_store_search",
  "params": {
    "query": {
      "filter": {
        "eq": {
          "runSchedule": {}
        }
      }
    }
  }
}'
```

#### Python SDK

```python
await linkedin_ads.campaign_groups.context_store_search(
    query={"filter": {"eq": {"runSchedule": {}}}}
)
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/integrations/connectors/{your_connector_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "campaign_groups",
    "action": "context_store_search",
    "params": {
        "query": {"filter": {"eq": {"runSchedule": {}}}}
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
| `runSchedule` | `object` | Schedule for running the campaign group. |
| `created` | `string` | The date and time when the campaign group was created. |
| `lastModified` | `string` | The date and time when the campaign group was last modified. |
| `name` | `string` | Name of the campaign group. |
| `test` | `boolean` | Indicates if the campaign group is a test campaign. |
| `totalBudget` | `object` | Total budget allocated for the campaign group. |
| `servingStatuses` | `array` | List of serving statuses for the campaign group. |
| `backfilled` | `boolean` | Indicates if the campaign group was backfilled. |
| `id` | `integer` | Unique identifier for the campaign group. |
| `account` | `string` | The account associated with the campaign group. |
| `status` | `string` | Current status of the campaign group. |
| `allowedCampaignTypes` | `array` | List of campaign types allowed for this campaign group. |

<details>
<summary><b>Response Schema</b></summary>

| Field Name | Type | Description |
|------------|------|-------------|
| `data` | `array` | List of matching records |
| `meta` | `object` | Pagination metadata |
| `meta.has_more` | `boolean` | Whether additional pages are available |
| `meta.cursor` | `string \| null` | Cursor for next page of results |
| `meta.took_ms` | `number \| null` | Query execution time in milliseconds |
| `data[].runSchedule` | `object` | Schedule for running the campaign group. |
| `data[].created` | `string` | The date and time when the campaign group was created. |
| `data[].lastModified` | `string` | The date and time when the campaign group was last modified. |
| `data[].name` | `string` | Name of the campaign group. |
| `data[].test` | `boolean` | Indicates if the campaign group is a test campaign. |
| `data[].totalBudget` | `object` | Total budget allocated for the campaign group. |
| `data[].servingStatuses` | `array` | List of serving statuses for the campaign group. |
| `data[].backfilled` | `boolean` | Indicates if the campaign group was backfilled. |
| `data[].id` | `integer` | Unique identifier for the campaign group. |
| `data[].account` | `string` | The account associated with the campaign group. |
| `data[].status` | `string` | Current status of the campaign group. |
| `data[].allowedCampaignTypes` | `array` | List of campaign types allowed for this campaign group. |

</details>

## Creatives

### Creatives List

Returns a list of creatives for an ad account

#### CLI

```bash
airbyte-agent connectors execute --json '{
  "workspace": "<your_workspace_name>",
  "name": "linkedin-ads",
  "entity": "creatives",
  "action": "list",
  "params": {
    "account_id": 0,
    "q": "<str>"
  }
}'
```

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
| `q` | `string` | Yes | LinkedIn API finder method for querying creatives |
| `pageSize` | `integer` | No | Number of items per page |
| `pageToken` | `string` | No | Token for the next page of results |


<details>
<summary><b>Response Schema</b></summary>



#### Meta

| Field Name | Type | Description |
|------------|------|-------------|
| `nextPageToken` | `string` |  |

</details>

### Creatives Create

Creates a new creative in the ad account. Requires the rw_ads OAuth scope and a CREATIVE_MANAGER or higher ad-account role. The new creative URN is returned in the x-restli-id response header. The creative's content must reference existing assets (e.g. a post URN in content.reference for sponsored content).


#### CLI

```bash
airbyte-agent connectors execute --json '{
  "workspace": "<your_workspace_name>",
  "name": "linkedin-ads",
  "entity": "creatives",
  "action": "create",
  "params": {
    "campaign": "<str>",
    "content": {},
    "intendedStatus": "<str>",
    "name": "<str>",
    "account_id": 0
  }
}'
```

#### Python SDK

```python
await linkedin_ads.creatives.create(
    campaign="<str>",
    content={},
    intended_status="<str>",
    name="<str>",
    account_id=0
)
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/integrations/connectors/{your_connector_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "creatives",
    "action": "create",
    "params": {
        "campaign": "<str>",
        "content": {},
        "intendedStatus": "<str>",
        "name": "<str>",
        "account_id": 0
    }
}'
```


#### Parameters

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `campaign` | `string` | Yes | Campaign URN the creative belongs to, e.g. urn:li:sponsoredCampaign:123456 |
| `content` | `object` | No | Creative content. For sponsored content, reference an existing post URN via content.reference; other formats (textAd, spotlight, jobs) use their own sub-objects per the LinkedIn Creatives API documentation.
 |
| `intendedStatus` | `"ACTIVE" \| "PAUSED" \| "DRAFT"` | No | Desired serving status |
| `name` | `string` | No | Creative name |
| `account_id` | `integer` | Yes | Ad account ID |


<details>
<summary><b>Response Schema</b></summary>



#### Meta

| Field Name | Type | Description |
|------------|------|-------------|
| `created_id` | `string` |  |

</details>

### Creatives Get

Get a single creative by ID

#### CLI

```bash
airbyte-agent connectors execute --json '{
  "workspace": "<your_workspace_name>",
  "name": "linkedin-ads",
  "entity": "creatives",
  "action": "get",
  "params": {
    "account_id": 0,
    "id": "<str>"
  }
}'
```

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

### Creatives Update

Partially updates a creative using the Rest.li PARTIAL_UPDATE pattern: the body wraps the fields to change in patch.$set. Only a limited set of creative fields is mutable (e.g. intendedStatus, name, leadgenCallToAction). Requires the rw_ads OAuth scope and a CREATIVE_MANAGER or higher ad-account role. To soft-delete a non-draft creative, set intendedStatus to PENDING_DELETION here.


#### CLI

```bash
airbyte-agent connectors execute --json '{
  "workspace": "<your_workspace_name>",
  "name": "linkedin-ads",
  "entity": "creatives",
  "action": "update",
  "params": {
    "patch": {
      "$set": {}
    },
    "account_id": 0,
    "id": "<str>"
  }
}'
```

#### Python SDK

```python
await linkedin_ads.creatives.update(
    patch={
        "$set": {}
    },
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
    "action": "update",
    "params": {
        "patch": {
            "$set": {}
        },
        "account_id": 0,
        "id": "<str>"
    }
}'
```


#### Parameters

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `patch` | `object` | Yes |  |
| `patch.$set` | `object` | Yes | Map of field names to their new values |
| `account_id` | `integer` | Yes | Ad account ID |
| `id` | `string` | Yes | Creative URN, e.g. urn:li:sponsoredCreative:123456 |


### Creatives Delete

Hard-deletes a creative. Only creatives in DRAFT intendedStatus (or linked to a draft campaign, or with failed video uploads) accept a true DELETE; LinkedIn uniquely requires the X-RestLi-Method DELETE header on this call. For other creatives, soft-delete via the update operation by setting intendedStatus to PENDING_DELETION. Requires the rw_ads OAuth scope and a CREATIVE_MANAGER or higher ad-account role.


#### CLI

```bash
airbyte-agent connectors execute --json '{
  "workspace": "<your_workspace_name>",
  "name": "linkedin-ads",
  "entity": "creatives",
  "action": "delete",
  "params": {
    "account_id": 0,
    "id": "<str>"
  }
}'
```

#### Python SDK

```python
await linkedin_ads.creatives.delete(
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
    "action": "delete",
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
| `id` | `string` | Yes | Creative URN, e.g. urn:li:sponsoredCreative:123456 |


### Creatives Context Store Search

Search and filter creatives records powered by Airbyte's data sync. This often provides additional fields and operators beyond what the API natively supports, making it easier to narrow down results before performing further operations. Only available in hosted mode.

#### CLI

```bash
airbyte-agent connectors execute --json '{
  "workspace": "<your_workspace_name>",
  "name": "linkedin-ads",
  "entity": "creatives",
  "action": "context_store_search",
  "params": {
    "query": {
      "filter": {
        "eq": {
          "servingHoldReasons": []
        }
      }
    }
  }
}'
```

#### Python SDK

```python
await linkedin_ads.creatives.context_store_search(
    query={"filter": {"eq": {"servingHoldReasons": []}}}
)
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/integrations/connectors/{your_connector_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "creatives",
    "action": "context_store_search",
    "params": {
        "query": {"filter": {"eq": {"servingHoldReasons": []}}}
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
| `servingHoldReasons` | `array` | Reasons for holding the creative from serving. |
| `lastModifiedAt` | `integer` | The timestamp when the creative was last modified. |
| `lastModifiedBy` | `string` | The user who last modified the creative. |
| `content` | `object` | The actual content of the creative. |
| `createdAt` | `integer` | The timestamp when the creative was created. |
| `isTest` | `boolean` | Boolean indicating if the creative is a test creative. |
| `createdBy` | `string` | The user who created the creative. |
| `review` | `object` | Review information for the creative. |
| `name` | `string` | The name of the creative. |
| `isServing` | `boolean` | Boolean indicating if the creative is currently serving. |
| `campaign` | `string` | The campaign to which the creative belongs. |
| `id` | `string` | The unique identifier of the creative. |
| `intendedStatus` | `string` | The intended status of the creative. |
| `account` | `string` | The account associated with the creative. |
| `leadgenCallToAction` | `object` | Call-to-action information for lead generation purposes. |

<details>
<summary><b>Response Schema</b></summary>

| Field Name | Type | Description |
|------------|------|-------------|
| `data` | `array` | List of matching records |
| `meta` | `object` | Pagination metadata |
| `meta.has_more` | `boolean` | Whether additional pages are available |
| `meta.cursor` | `string \| null` | Cursor for next page of results |
| `meta.took_ms` | `number \| null` | Query execution time in milliseconds |
| `data[].servingHoldReasons` | `array` | Reasons for holding the creative from serving. |
| `data[].lastModifiedAt` | `integer` | The timestamp when the creative was last modified. |
| `data[].lastModifiedBy` | `string` | The user who last modified the creative. |
| `data[].content` | `object` | The actual content of the creative. |
| `data[].createdAt` | `integer` | The timestamp when the creative was created. |
| `data[].isTest` | `boolean` | Boolean indicating if the creative is a test creative. |
| `data[].createdBy` | `string` | The user who created the creative. |
| `data[].review` | `object` | Review information for the creative. |
| `data[].name` | `string` | The name of the creative. |
| `data[].isServing` | `boolean` | Boolean indicating if the creative is currently serving. |
| `data[].campaign` | `string` | The campaign to which the creative belongs. |
| `data[].id` | `string` | The unique identifier of the creative. |
| `data[].intendedStatus` | `string` | The intended status of the creative. |
| `data[].account` | `string` | The account associated with the creative. |
| `data[].leadgenCallToAction` | `object` | Call-to-action information for lead generation purposes. |

</details>

## Conversions

### Conversions List

Returns a list of conversion rules for an ad account

#### CLI

```bash
airbyte-agent connectors execute --json '{
  "workspace": "<your_workspace_name>",
  "name": "linkedin-ads",
  "entity": "conversions",
  "action": "list",
  "params": {
    "q": "<str>",
    "account": "<str>"
  }
}'
```

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
| `q` | `string` | Yes | LinkedIn API finder method for querying conversions by account |
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
| `ownershipType` | `null \| string` |  |
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

### Conversions Create

Creates a new conversion tracking rule. Conversions API write access is gated behind a separate LinkedIn partner approval - the rw_conversions OAuth scope alone is not sufficient until access is granted. The new conversion ID is returned in the x-restli-id response header. Set autoAssociationType to ALL_CAMPAIGNS to associate the rule with every campaign in the account automatically.


#### CLI

```bash
airbyte-agent connectors execute --json '{
  "workspace": "<your_workspace_name>",
  "name": "linkedin-ads",
  "entity": "conversions",
  "action": "create",
  "params": {
    "account": "<str>",
    "name": "<str>",
    "type": "<str>",
    "attributionType": "<str>",
    "postClickAttributionWindowSize": 0,
    "viewThroughAttributionWindowSize": 0,
    "enabled": true,
    "urlMatchRuleExpression": [],
    "value": {},
    "autoAssociationType": "<str>"
  }
}'
```

#### Python SDK

```python
await linkedin_ads.conversions.create(
    account="<str>",
    name="<str>",
    type="<str>",
    attribution_type="<str>",
    post_click_attribution_window_size=0,
    view_through_attribution_window_size=0,
    enabled=True,
    url_match_rule_expression=[],
    value={},
    auto_association_type="<str>"
)
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/integrations/connectors/{your_connector_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "conversions",
    "action": "create",
    "params": {
        "account": "<str>",
        "name": "<str>",
        "type": "<str>",
        "attributionType": "<str>",
        "postClickAttributionWindowSize": 0,
        "viewThroughAttributionWindowSize": 0,
        "enabled": True,
        "urlMatchRuleExpression": [],
        "value": {},
        "autoAssociationType": "<str>"
    }
}'
```


#### Parameters

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `account` | `string` | Yes | Sponsored account URN, e.g. urn:li:sponsoredAccount:123456 |
| `name` | `string` | Yes | Conversion rule name |
| `type` | `string` | Yes | Conversion category, e.g. LEAD, PURCHASE, SIGN_UP, DOWNLOAD, ADD_TO_CART, INSTALL, KEY_PAGE_VIEW, OTHER |
| `attributionType` | `"LAST_TOUCH_BY_CAMPAIGN" \| "LAST_TOUCH_BY_CONVERSION"` | No | How conversions are attributed to campaigns |
| `postClickAttributionWindowSize` | `integer` | No | Post-click attribution window in days (1, 7, 30, or 90) |
| `viewThroughAttributionWindowSize` | `integer` | No | View-through attribution window in days (1, 7, or 30) |
| `enabled` | `boolean` | No | Whether the rule is active |
| `urlMatchRuleExpression` | `array<array<object>>` | No | URL match rules for page-based conversion tracking |
| `value` | `object` | No | Monetary value assigned to each conversion |
| `value.amount` | `string` | No |  |
| `value.currencyCode` | `string` | No |  |
| `autoAssociationType` | `"ALL_CAMPAIGNS"` | No | Set to ALL_CAMPAIGNS to auto-associate with all campaigns in the account |


<details>
<summary><b>Response Schema</b></summary>



#### Meta

| Field Name | Type | Description |
|------------|------|-------------|
| `created_id` | `string` |  |

</details>

### Conversions Get

Get a single conversion rule by ID

#### CLI

```bash
airbyte-agent connectors execute --json '{
  "workspace": "<your_workspace_name>",
  "name": "linkedin-ads",
  "entity": "conversions",
  "action": "get",
  "params": {
    "id": 0
  }
}'
```

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
| `ownershipType` | `null \| string` |  |
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

### Conversions Update

Partially updates a conversion rule using the Rest.li PARTIAL_UPDATE pattern: the body wraps the fields to change in patch.$set. The account query parameter is required. Conversion rules have no hard delete - to retire one, soft-disable it here with \{"patch": \{"$set": \{"enabled": false\}\}\}. Conversions API write access is gated behind a separate LinkedIn partner approval.


#### CLI

```bash
airbyte-agent connectors execute --json '{
  "workspace": "<your_workspace_name>",
  "name": "linkedin-ads",
  "entity": "conversions",
  "action": "update",
  "params": {
    "patch": {
      "$set": {}
    },
    "id": 0,
    "account": "<str>"
  }
}'
```

#### Python SDK

```python
await linkedin_ads.conversions.update(
    patch={
        "$set": {}
    },
    id=0,
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
    "action": "update",
    "params": {
        "patch": {
            "$set": {}
        },
        "id": 0,
        "account": "<str>"
    }
}'
```


#### Parameters

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `patch` | `object` | Yes |  |
| `patch.$set` | `object` | Yes | Map of field names to their new values |
| `id` | `integer` | Yes | Conversion rule ID |
| `account` | `string` | Yes | Sponsored account URN, e.g. urn:li:sponsoredAccount:123456 |


### Conversions Context Store Search

Search and filter conversions records powered by Airbyte's data sync. This often provides additional fields and operators beyond what the API natively supports, making it easier to narrow down results before performing further operations. Only available in hosted mode.

#### CLI

```bash
airbyte-agent connectors execute --json '{
  "workspace": "<your_workspace_name>",
  "name": "linkedin-ads",
  "entity": "conversions",
  "action": "context_store_search",
  "params": {
    "query": {
      "filter": {
        "eq": {
          "attributionType": "<str>"
        }
      }
    }
  }
}'
```

#### Python SDK

```python
await linkedin_ads.conversions.context_store_search(
    query={"filter": {"eq": {"attributionType": "<str>"}}}
)
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/integrations/connectors/{your_connector_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "conversions",
    "action": "context_store_search",
    "params": {
        "query": {"filter": {"eq": {"attributionType": "<str>"}}}
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
| `attributionType` | `string` | The type of attribution for the conversion. |
| `account` | `string` | The account associated with the conversion data. |
| `campaigns` | `array` | List of campaigns related to the conversion. |
| `created` | `integer` | Timestamp of when the conversion was created. |
| `enabled` | `boolean` | Flag indicating if the conversion tracking is enabled. |
| `id` | `integer` | Unique identifier for the conversion. |
| `imagePixelTag` | `string` | Pixel tag used for tracking the conversion. |
| `name` | `string` | Name of the conversion. |
| `type` | `string` | Type of conversion. |
| `latestFirstPartyCallbackAt` | `integer` | Timestamp of the latest first-party callback for the conversion. |
| `postClickAttributionWindowSize` | `integer` | Window size for post-click attribution. |
| `viewThroughAttributionWindowSize` | `integer` | Window size for view-through attribution. |
| `lastCallbackAt` | `integer` | Timestamp of the last callback for the conversion. |
| `lastModified` | `integer` | Timestamp of the last modification made to the conversion. |
| `value` | `object` | Value associated with the conversion. |
| `associatedCampaigns` | `array` | Campaigns associated with the conversion. |
| `urlMatchRuleExpression` | `array` | Expression used for matching URLs for attribution. |
| `urlRules` | `array` | Rules for URL matching in the conversion. |

<details>
<summary><b>Response Schema</b></summary>

| Field Name | Type | Description |
|------------|------|-------------|
| `data` | `array` | List of matching records |
| `meta` | `object` | Pagination metadata |
| `meta.has_more` | `boolean` | Whether additional pages are available |
| `meta.cursor` | `string \| null` | Cursor for next page of results |
| `meta.took_ms` | `number \| null` | Query execution time in milliseconds |
| `data[].attributionType` | `string` | The type of attribution for the conversion. |
| `data[].account` | `string` | The account associated with the conversion data. |
| `data[].campaigns` | `array` | List of campaigns related to the conversion. |
| `data[].created` | `integer` | Timestamp of when the conversion was created. |
| `data[].enabled` | `boolean` | Flag indicating if the conversion tracking is enabled. |
| `data[].id` | `integer` | Unique identifier for the conversion. |
| `data[].imagePixelTag` | `string` | Pixel tag used for tracking the conversion. |
| `data[].name` | `string` | Name of the conversion. |
| `data[].type` | `string` | Type of conversion. |
| `data[].latestFirstPartyCallbackAt` | `integer` | Timestamp of the latest first-party callback for the conversion. |
| `data[].postClickAttributionWindowSize` | `integer` | Window size for post-click attribution. |
| `data[].viewThroughAttributionWindowSize` | `integer` | Window size for view-through attribution. |
| `data[].lastCallbackAt` | `integer` | Timestamp of the last callback for the conversion. |
| `data[].lastModified` | `integer` | Timestamp of the last modification made to the conversion. |
| `data[].value` | `object` | Value associated with the conversion. |
| `data[].associatedCampaigns` | `array` | Campaigns associated with the conversion. |
| `data[].urlMatchRuleExpression` | `array` | Expression used for matching URLs for attribution. |
| `data[].urlRules` | `array` | Rules for URL matching in the conversion. |

</details>

## Conversion Events

### Conversion Events Create

Streams offline conversion events to LinkedIn (Conversions API event ingestion). This is a write-only Rest.li BATCH_CREATE: the body's elements array accepts up to 5,000 events per request. Each event references a conversion rule URN (urn:lla:llaPartnerConversion:\{id\}) and identifies the converting user by hashed email or other supported ID types. Conversions API access is gated behind a separate LinkedIn partner approval.


#### CLI

```bash
airbyte-agent connectors execute --json '{
  "workspace": "<your_workspace_name>",
  "name": "linkedin-ads",
  "entity": "conversion_events",
  "action": "create",
  "params": {
    "elements": []
  }
}'
```

#### Python SDK

```python
await linkedin_ads.conversion_events.create(
    elements=[]
)
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/integrations/connectors/{your_connector_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "conversion_events",
    "action": "create",
    "params": {
        "elements": []
    }
}'
```


#### Parameters

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `elements` | `array<object>` | Yes | Conversion events to ingest |
| `elements.conversion` | `string` | Yes | Conversion rule URN, e.g. urn:lla:llaPartnerConversion:123456 |
| `elements.conversionHappenedAt` | `integer` | Yes | Epoch milliseconds when the conversion occurred |
| `elements.user` | `object` | No | Identifies the converting user (hashed email or other supported ID types) |
| `elements.user.userIds` | `array<object>` | No |  |
| `elements.user.userIds.idType` | `string` | No | e.g. SHA256_EMAIL, LINKEDIN_FIRST_PARTY_ADS_TRACKING_UUID |
| `elements.user.userIds.idValue` | `string` | No |  |
| `elements.user.userInfo` | `object` | No |  |
| `elements.conversionValue` | `object` | No | Monetary value of this conversion |
| `elements.conversionValue.amount` | `string` | No |  |
| `elements.conversionValue.currencyCode` | `string` | No |  |
| `elements.eventId` | `string` | No | Optional unique event ID for deduplication |


## Campaign Conversions

### Campaign Conversions Create

Creates a campaign-to-conversion association using the Rest.li compound-key PUT pattern. Pass the raw campaign URN (urn:li:sponsoredCampaign:\{id\}) and conversion URN (urn:lla:llaPartnerConversion:\{id\}); they are URL-encoded automatically. Conversions API access is gated behind a separate LinkedIn partner approval.


#### CLI

```bash
airbyte-agent connectors execute --json '{
  "workspace": "<your_workspace_name>",
  "name": "linkedin-ads",
  "entity": "campaign_conversions",
  "action": "create",
  "params": {
    "campaign": "<str>",
    "conversion": "<str>",
    "campaign_urn": "<str>",
    "conversion_urn": "<str>"
  }
}'
```

#### Python SDK

```python
await linkedin_ads.campaign_conversions.create(
    campaign="<str>",
    conversion="<str>",
    campaign_urn="<str>",
    conversion_urn="<str>"
)
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/integrations/connectors/{your_connector_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "campaign_conversions",
    "action": "create",
    "params": {
        "campaign": "<str>",
        "conversion": "<str>",
        "campaign_urn": "<str>",
        "conversion_urn": "<str>"
    }
}'
```


#### Parameters

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `campaign` | `string` | No | Campaign URN, e.g. urn:li:sponsoredCampaign:123456 |
| `conversion` | `string` | No | Conversion rule URN, e.g. urn:lla:llaPartnerConversion:123456 |
| `campaign_urn` | `string` | Yes | Campaign URN, e.g. urn:li:sponsoredCampaign:123456 |
| `conversion_urn` | `string` | Yes | Conversion rule URN, e.g. urn:lla:llaPartnerConversion:123456 |


### Campaign Conversions Delete

Deletes a campaign-to-conversion association by its compound key. Pass the raw campaign and conversion URNs; they are URL-encoded automatically. Conversions API access is gated behind a separate LinkedIn partner approval.


#### CLI

```bash
airbyte-agent connectors execute --json '{
  "workspace": "<your_workspace_name>",
  "name": "linkedin-ads",
  "entity": "campaign_conversions",
  "action": "delete",
  "params": {
    "campaign_urn": "<str>",
    "conversion_urn": "<str>"
  }
}'
```

#### Python SDK

```python
await linkedin_ads.campaign_conversions.delete(
    campaign_urn="<str>",
    conversion_urn="<str>"
)
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/integrations/connectors/{your_connector_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "campaign_conversions",
    "action": "delete",
    "params": {
        "campaign_urn": "<str>",
        "conversion_urn": "<str>"
    }
}'
```


#### Parameters

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `campaign_urn` | `string` | Yes | Campaign URN, e.g. urn:li:sponsoredCampaign:123456 |
| `conversion_urn` | `string` | Yes | Conversion rule URN, e.g. urn:lla:llaPartnerConversion:123456 |


## Ad Campaign Analytics

### Ad Campaign Analytics List

Returns ad analytics data pivoted by campaign. Provides performance metrics including clicks, impressions, spend, and engagement data grouped by campaign.


#### CLI

```bash
airbyte-agent connectors execute --json '{
  "workspace": "<your_workspace_name>",
  "name": "linkedin-ads",
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
| `q` | `string` | Yes | LinkedIn API finder method for querying ad analytics |
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

### Ad Campaign Analytics Context Store Search

Search and filter ad campaign analytics records powered by Airbyte's data sync. This often provides additional fields and operators beyond what the API natively supports, making it easier to narrow down results before performing further operations. Only available in hosted mode.

#### CLI

```bash
airbyte-agent connectors execute --json '{
  "workspace": "<your_workspace_name>",
  "name": "linkedin-ads",
  "entity": "ad_campaign_analytics",
  "action": "context_store_search",
  "params": {
    "query": {
      "filter": {
        "eq": {
          "actionClicks": 0.0
        }
      }
    }
  }
}'
```

#### Python SDK

```python
await linkedin_ads.ad_campaign_analytics.context_store_search(
    query={"filter": {"eq": {"actionClicks": 0.0}}}
)
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/integrations/connectors/{your_connector_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "ad_campaign_analytics",
    "action": "context_store_search",
    "params": {
        "query": {"filter": {"eq": {"actionClicks": 0.0}}}
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
| `actionClicks` | `number` | The number of clicks on action buttons in the ad. |
| `adUnitClicks` | `number` | The number of clicks on ad unit components. |
| `approximateMemberReach` | `number` | An approximation of unique ad impressions. |
| `cardClicks` | `number` | The number of clicks on interactive card elements. |
| `cardImpressions` | `number` | The number of times interactive cards were displayed. |
| `clicks` | `number` | Total number of clicks on the ad. |
| `commentLikes` | `number` | The count of likes on comments related to the ad. |
| `comments` | `number` | The number of comments on the ad. |
| `companyPageClicks` | `number` | Clicks on the company page associated with the ad. |
| `conversionValueInLocalCurrency` | `number` | Conversion value in the local currency. |
| `costInLocalCurrency` | `number` | Cost of ad campaign in the local currency. |
| `costInUsd` | `number` | Cost of ad campaign in USD. |
| `documentCompletions` | `number` | Number of completions for document views. |
| `documentFirstQuartileCompletions` | `number` | Completions for first quartile of document views. |
| `documentMidpointCompletions` | `number` | Completions for midpoint of document views. |
| `documentThirdQuartileCompletions` | `number` | Completions for third quartile of document views. |
| `downloadClicks` | `number` | Clicks on download links in the ad. |
| `end_date` | `string` | End date of the ad analytics data. |
| `externalWebsiteConversions` | `number` | Conversions that lead to external websites. |
| `externalWebsitePostClickConversions` | `number` | Post-click conversions on external websites. |
| `externalWebsitePostViewConversions` | `number` | Post-view conversions on external websites. |
| `follows` | `number` | Number of follows generated by the ad. |
| `fullScreenPlays` | `number` | Number of times videos were played in fullscreen mode. |
| `impressions` | `number` | Total number of times the ad was displayed. |
| `jobApplications` | `number` | Number of job applications initiated through the ad. |
| `jobApplyClicks` | `number` | Clicks on apply job button in the ad. |
| `landingPageClicks` | `number` | Clicks on the landing page associated with the ad. |
| `leadGenerationMailContactInfoShares` | `number` | Shares of contact information through lead generation. |
| `leadGenerationMailInterestedClicks` | `number` | Clicks on expressing interest through lead generation mail. |
| `likes` | `number` | Total likes received on the ad. |
| `oneClickLeadFormOpens` | `number` | Number of times lead forms were opened in one click. |
| `oneClickLeads` | `number` | Leads generated in one click. |
| `opens` | `number` | The number of times the ad was opened or expanded. |
| `otherEngagements` | `number` | Engagements other than clicks on the ad. |
| `pivotValues` | `array` | Values used for pivoting the analytics. |
| `string_of_pivot_values` | `string` | Comma-separated string of pivot values for this analytics record |
| `postClickJobApplications` | `number` | Job applications initiated post-clicking on the ad. |
| `postClickJobApplyClicks` | `number` | Clicks on apply job button post-clicking on the ad. |
| `postClickRegistrations` | `number` | Registrations completed post-clicking on the ad. |
| `postViewJobApplications` | `number` | Job applications initiated post-viewing the ad. |
| `postViewJobApplyClicks` | `number` | Clicks on apply job button post-viewing the ad. |
| `postViewRegistrations` | `number` | Registrations completed post-viewing the ad. |
| `reactions` | `number` | Total reactions (e.g., like, love, celebrate) on the ad. |
| `registrations` | `number` | Total registrations completed through the ad. |
| `sends` | `number` | Number of messages sent through the ad. |
| `shares` | `number` | Total shares generated by the ad. |
| `start_date` | `string` | Start date of the ad analytics data. |
| `talentLeads` | `number` | Number of leads related to talent acquisition. |
| `textUrlClicks` | `number` | Clicks on text URLs within the ad. |
| `totalEngagements` | `number` | Total number of engagements on the ad. |
| `validWorkEmailLeads` | `number` | Leads generated through valid work emails. |
| `videoCompletions` | `number` | Number of times videos were watched till completion. |
| `videoFirstQuartileCompletions` | `number` | Completions for first quartile of video views. |
| `videoMidpointCompletions` | `number` | Completions for midpoint of video views. |
| `videoStarts` | `number` | Total video starts initiated by users. |
| `videoThirdQuartileCompletions` | `number` | Completions for third quartile of video views. |
| `videoViews` | `number` | Total views of videos in the ad. |
| `viralCardClicks` | `number` | Clicks on interactive card components in viral distribution. |
| `viralCardImpressions` | `number` | Impressions of interactive cards in viral distribution. |
| `viralClicks` | `number` | Total clicks in viral distribution of the ad. |
| `viralCommentLikes` | `number` | Likes received on comments in viral distribution. |
| `viralComments` | `number` | Number of comments in viral distribution of the ad. |
| `viralCompanyPageClicks` | `number` | Clicks on the company page in viral distribution. |
| `viralDocumentCompletions` | `number` | Complete views of documents in viral distribution. |
| `viralDocumentFirstQuartileCompletions` | `number` | First quartile completions of documents in viral distribution. |
| `viralDocumentMidpointCompletions` | `number` | Midpoint completions of documents in viral distribution. |
| `viralDocumentThirdQuartileCompletions` | `number` | Third quartile completions of documents in viral distribution. |
| `viralDownloadClicks` | `number` | Clicks on downloads in viral distribution of the ad. |
| `viralExternalWebsiteConversions` | `number` | External website conversions in viral distribution. |
| `viralExternalWebsitePostClickConversions` | `number` | Post-click conversions on external websites in viral distribution. |
| `viralExternalWebsitePostViewConversions` | `number` | Post-view conversions on external websites in viral distribution. |
| `viralFollows` | `number` | Follows generated in viral distribution of the ad. |
| `viralFullScreenPlays` | `number` | Fullscreen video plays in viral distribution. |
| `viralImpressions` | `number` | Total impressions in viral distribution of the ad. |
| `viralJobApplications` | `number` | Job applications initiated in viral distribution. |
| `viralJobApplyClicks` | `number` | Clicks on apply job button in viral distribution of the ad. |
| `viralLandingPageClicks` | `number` | Clicks on landing page in viral distribution. |
| `viralLikes` | `number` | Total likes in viral distribution of the ad. |
| `viralOneClickLeadFormOpens` | `number` | One-click lead form opens in viral distribution. |
| `viralOneClickLeads` | `number` | Leads generated in one click in viral distribution. |
| `viralOtherEngagements` | `number` | Other engagements in viral distribution of the ad. |
| `viralPostClickJobApplications` | `number` | Job applications initiated post-clicking in viral distribution. |
| `viralPostClickJobApplyClicks` | `number` | Clicks on apply job button post-clicking in viral distribution. |
| `viralPostClickRegistrations` | `number` | Registrations completed post-clicking in viral distribution. |
| `viralPostViewJobApplications` | `number` | Job applications initiated post-viewing in viral distribution. |
| `viralPostViewJobApplyClicks` | `number` | Clicks on apply job button post-viewing in viral distribution. |
| `viralPostViewRegistrations` | `number` | Registrations completed post-viewing in viral distribution. |
| `viralReactions` | `number` | Total reactions in viral distribution of the ad. |
| `viralRegistrations` | `number` | Total registrations in viral distribution of the ad. |
| `viralShares` | `number` | Total shares in viral distribution of the ad. |
| `viralTotalEngagements` | `number` | Total engagements in viral distribution of the ad. |
| `viralVideoCompletions` | `number` | Completions of videos in viral distribution. |
| `viralVideoFirstQuartileCompletions` | `number` | First quartile completions of videos in viral distribution. |
| `viralVideoMidpointCompletions` | `number` | Midpoint completions of videos in viral distribution. |
| `viralVideoStarts` | `number` | Total video starts in viral distribution of the ad. |
| `viralVideoThirdQuartileCompletions` | `number` | Third quartile completions of videos in viral distribution. |
| `viralVideoViews` | `number` | Total views of videos in viral distribution of the ad. |
| `pivot` | `string` | Pivot dimension used for this analytics record |
| `sponsoredCampaign` | `string` | URN of the sponsored campaign this analytics record belongs to |

<details>
<summary><b>Response Schema</b></summary>

| Field Name | Type | Description |
|------------|------|-------------|
| `data` | `array` | List of matching records |
| `meta` | `object` | Pagination metadata |
| `meta.has_more` | `boolean` | Whether additional pages are available |
| `meta.cursor` | `string \| null` | Cursor for next page of results |
| `meta.took_ms` | `number \| null` | Query execution time in milliseconds |
| `data[].actionClicks` | `number` | The number of clicks on action buttons in the ad. |
| `data[].adUnitClicks` | `number` | The number of clicks on ad unit components. |
| `data[].approximateMemberReach` | `number` | An approximation of unique ad impressions. |
| `data[].cardClicks` | `number` | The number of clicks on interactive card elements. |
| `data[].cardImpressions` | `number` | The number of times interactive cards were displayed. |
| `data[].clicks` | `number` | Total number of clicks on the ad. |
| `data[].commentLikes` | `number` | The count of likes on comments related to the ad. |
| `data[].comments` | `number` | The number of comments on the ad. |
| `data[].companyPageClicks` | `number` | Clicks on the company page associated with the ad. |
| `data[].conversionValueInLocalCurrency` | `number` | Conversion value in the local currency. |
| `data[].costInLocalCurrency` | `number` | Cost of ad campaign in the local currency. |
| `data[].costInUsd` | `number` | Cost of ad campaign in USD. |
| `data[].documentCompletions` | `number` | Number of completions for document views. |
| `data[].documentFirstQuartileCompletions` | `number` | Completions for first quartile of document views. |
| `data[].documentMidpointCompletions` | `number` | Completions for midpoint of document views. |
| `data[].documentThirdQuartileCompletions` | `number` | Completions for third quartile of document views. |
| `data[].downloadClicks` | `number` | Clicks on download links in the ad. |
| `data[].end_date` | `string` | End date of the ad analytics data. |
| `data[].externalWebsiteConversions` | `number` | Conversions that lead to external websites. |
| `data[].externalWebsitePostClickConversions` | `number` | Post-click conversions on external websites. |
| `data[].externalWebsitePostViewConversions` | `number` | Post-view conversions on external websites. |
| `data[].follows` | `number` | Number of follows generated by the ad. |
| `data[].fullScreenPlays` | `number` | Number of times videos were played in fullscreen mode. |
| `data[].impressions` | `number` | Total number of times the ad was displayed. |
| `data[].jobApplications` | `number` | Number of job applications initiated through the ad. |
| `data[].jobApplyClicks` | `number` | Clicks on apply job button in the ad. |
| `data[].landingPageClicks` | `number` | Clicks on the landing page associated with the ad. |
| `data[].leadGenerationMailContactInfoShares` | `number` | Shares of contact information through lead generation. |
| `data[].leadGenerationMailInterestedClicks` | `number` | Clicks on expressing interest through lead generation mail. |
| `data[].likes` | `number` | Total likes received on the ad. |
| `data[].oneClickLeadFormOpens` | `number` | Number of times lead forms were opened in one click. |
| `data[].oneClickLeads` | `number` | Leads generated in one click. |
| `data[].opens` | `number` | The number of times the ad was opened or expanded. |
| `data[].otherEngagements` | `number` | Engagements other than clicks on the ad. |
| `data[].pivotValues` | `array` | Values used for pivoting the analytics. |
| `data[].string_of_pivot_values` | `string` | Comma-separated string of pivot values for this analytics record |
| `data[].postClickJobApplications` | `number` | Job applications initiated post-clicking on the ad. |
| `data[].postClickJobApplyClicks` | `number` | Clicks on apply job button post-clicking on the ad. |
| `data[].postClickRegistrations` | `number` | Registrations completed post-clicking on the ad. |
| `data[].postViewJobApplications` | `number` | Job applications initiated post-viewing the ad. |
| `data[].postViewJobApplyClicks` | `number` | Clicks on apply job button post-viewing the ad. |
| `data[].postViewRegistrations` | `number` | Registrations completed post-viewing the ad. |
| `data[].reactions` | `number` | Total reactions (e.g., like, love, celebrate) on the ad. |
| `data[].registrations` | `number` | Total registrations completed through the ad. |
| `data[].sends` | `number` | Number of messages sent through the ad. |
| `data[].shares` | `number` | Total shares generated by the ad. |
| `data[].start_date` | `string` | Start date of the ad analytics data. |
| `data[].talentLeads` | `number` | Number of leads related to talent acquisition. |
| `data[].textUrlClicks` | `number` | Clicks on text URLs within the ad. |
| `data[].totalEngagements` | `number` | Total number of engagements on the ad. |
| `data[].validWorkEmailLeads` | `number` | Leads generated through valid work emails. |
| `data[].videoCompletions` | `number` | Number of times videos were watched till completion. |
| `data[].videoFirstQuartileCompletions` | `number` | Completions for first quartile of video views. |
| `data[].videoMidpointCompletions` | `number` | Completions for midpoint of video views. |
| `data[].videoStarts` | `number` | Total video starts initiated by users. |
| `data[].videoThirdQuartileCompletions` | `number` | Completions for third quartile of video views. |
| `data[].videoViews` | `number` | Total views of videos in the ad. |
| `data[].viralCardClicks` | `number` | Clicks on interactive card components in viral distribution. |
| `data[].viralCardImpressions` | `number` | Impressions of interactive cards in viral distribution. |
| `data[].viralClicks` | `number` | Total clicks in viral distribution of the ad. |
| `data[].viralCommentLikes` | `number` | Likes received on comments in viral distribution. |
| `data[].viralComments` | `number` | Number of comments in viral distribution of the ad. |
| `data[].viralCompanyPageClicks` | `number` | Clicks on the company page in viral distribution. |
| `data[].viralDocumentCompletions` | `number` | Complete views of documents in viral distribution. |
| `data[].viralDocumentFirstQuartileCompletions` | `number` | First quartile completions of documents in viral distribution. |
| `data[].viralDocumentMidpointCompletions` | `number` | Midpoint completions of documents in viral distribution. |
| `data[].viralDocumentThirdQuartileCompletions` | `number` | Third quartile completions of documents in viral distribution. |
| `data[].viralDownloadClicks` | `number` | Clicks on downloads in viral distribution of the ad. |
| `data[].viralExternalWebsiteConversions` | `number` | External website conversions in viral distribution. |
| `data[].viralExternalWebsitePostClickConversions` | `number` | Post-click conversions on external websites in viral distribution. |
| `data[].viralExternalWebsitePostViewConversions` | `number` | Post-view conversions on external websites in viral distribution. |
| `data[].viralFollows` | `number` | Follows generated in viral distribution of the ad. |
| `data[].viralFullScreenPlays` | `number` | Fullscreen video plays in viral distribution. |
| `data[].viralImpressions` | `number` | Total impressions in viral distribution of the ad. |
| `data[].viralJobApplications` | `number` | Job applications initiated in viral distribution. |
| `data[].viralJobApplyClicks` | `number` | Clicks on apply job button in viral distribution of the ad. |
| `data[].viralLandingPageClicks` | `number` | Clicks on landing page in viral distribution. |
| `data[].viralLikes` | `number` | Total likes in viral distribution of the ad. |
| `data[].viralOneClickLeadFormOpens` | `number` | One-click lead form opens in viral distribution. |
| `data[].viralOneClickLeads` | `number` | Leads generated in one click in viral distribution. |
| `data[].viralOtherEngagements` | `number` | Other engagements in viral distribution of the ad. |
| `data[].viralPostClickJobApplications` | `number` | Job applications initiated post-clicking in viral distribution. |
| `data[].viralPostClickJobApplyClicks` | `number` | Clicks on apply job button post-clicking in viral distribution. |
| `data[].viralPostClickRegistrations` | `number` | Registrations completed post-clicking in viral distribution. |
| `data[].viralPostViewJobApplications` | `number` | Job applications initiated post-viewing in viral distribution. |
| `data[].viralPostViewJobApplyClicks` | `number` | Clicks on apply job button post-viewing in viral distribution. |
| `data[].viralPostViewRegistrations` | `number` | Registrations completed post-viewing in viral distribution. |
| `data[].viralReactions` | `number` | Total reactions in viral distribution of the ad. |
| `data[].viralRegistrations` | `number` | Total registrations in viral distribution of the ad. |
| `data[].viralShares` | `number` | Total shares in viral distribution of the ad. |
| `data[].viralTotalEngagements` | `number` | Total engagements in viral distribution of the ad. |
| `data[].viralVideoCompletions` | `number` | Completions of videos in viral distribution. |
| `data[].viralVideoFirstQuartileCompletions` | `number` | First quartile completions of videos in viral distribution. |
| `data[].viralVideoMidpointCompletions` | `number` | Midpoint completions of videos in viral distribution. |
| `data[].viralVideoStarts` | `number` | Total video starts in viral distribution of the ad. |
| `data[].viralVideoThirdQuartileCompletions` | `number` | Third quartile completions of videos in viral distribution. |
| `data[].viralVideoViews` | `number` | Total views of videos in viral distribution of the ad. |
| `data[].pivot` | `string` | Pivot dimension used for this analytics record |
| `data[].sponsoredCampaign` | `string` | URN of the sponsored campaign this analytics record belongs to |

</details>

## Ad Creative Analytics

### Ad Creative Analytics List

Returns ad analytics data pivoted by creative. Provides performance metrics including clicks, impressions, spend, and engagement data grouped by creative.


#### CLI

```bash
airbyte-agent connectors execute --json '{
  "workspace": "<your_workspace_name>",
  "name": "linkedin-ads",
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
| `q` | `string` | Yes | LinkedIn API finder method for querying ad analytics |
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

### Ad Creative Analytics Context Store Search

Search and filter ad creative analytics records powered by Airbyte's data sync. This often provides additional fields and operators beyond what the API natively supports, making it easier to narrow down results before performing further operations. Only available in hosted mode.

#### CLI

```bash
airbyte-agent connectors execute --json '{
  "workspace": "<your_workspace_name>",
  "name": "linkedin-ads",
  "entity": "ad_creative_analytics",
  "action": "context_store_search",
  "params": {
    "query": {
      "filter": {
        "eq": {
          "actionClicks": 0.0
        }
      }
    }
  }
}'
```

#### Python SDK

```python
await linkedin_ads.ad_creative_analytics.context_store_search(
    query={"filter": {"eq": {"actionClicks": 0.0}}}
)
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/integrations/connectors/{your_connector_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "ad_creative_analytics",
    "action": "context_store_search",
    "params": {
        "query": {"filter": {"eq": {"actionClicks": 0.0}}}
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
| `actionClicks` | `number` | The number of clicks on action buttons in the ad. |
| `adUnitClicks` | `number` | The number of clicks on ad unit components. |
| `approximateMemberReach` | `number` | An approximation of unique ad impressions. |
| `cardClicks` | `number` | The number of clicks on interactive card elements. |
| `cardImpressions` | `number` | The number of times interactive cards were displayed. |
| `clicks` | `number` | Total number of clicks on the ad. |
| `commentLikes` | `number` | The count of likes on comments related to the ad. |
| `comments` | `number` | The number of comments on the ad. |
| `companyPageClicks` | `number` | Clicks on the company page associated with the ad. |
| `conversionValueInLocalCurrency` | `number` | Conversion value in the local currency. |
| `costInLocalCurrency` | `number` | Cost of ad campaign in the local currency. |
| `costInUsd` | `number` | Cost of ad campaign in USD. |
| `documentCompletions` | `number` | Number of completions for document views. |
| `documentFirstQuartileCompletions` | `number` | Completions for first quartile of document views. |
| `documentMidpointCompletions` | `number` | Completions for midpoint of document views. |
| `documentThirdQuartileCompletions` | `number` | Completions for third quartile of document views. |
| `downloadClicks` | `number` | Clicks on download links in the ad. |
| `end_date` | `string` | End date of the ad analytics data. |
| `externalWebsiteConversions` | `number` | Conversions that lead to external websites. |
| `externalWebsitePostClickConversions` | `number` | Post-click conversions on external websites. |
| `externalWebsitePostViewConversions` | `number` | Post-view conversions on external websites. |
| `follows` | `number` | Number of follows generated by the ad. |
| `fullScreenPlays` | `number` | Number of times videos were played in fullscreen mode. |
| `impressions` | `number` | Total number of times the ad was displayed. |
| `jobApplications` | `number` | Number of job applications initiated through the ad. |
| `jobApplyClicks` | `number` | Clicks on apply job button in the ad. |
| `landingPageClicks` | `number` | Clicks on the landing page associated with the ad. |
| `leadGenerationMailContactInfoShares` | `number` | Shares of contact information through lead generation. |
| `leadGenerationMailInterestedClicks` | `number` | Clicks on expressing interest through lead generation mail. |
| `likes` | `number` | Total likes received on the ad. |
| `oneClickLeadFormOpens` | `number` | Number of times lead forms were opened in one click. |
| `oneClickLeads` | `number` | Leads generated in one click. |
| `opens` | `number` | The number of times the ad was opened or expanded. |
| `otherEngagements` | `number` | Engagements other than clicks on the ad. |
| `pivotValues` | `array` | Values used for pivoting the analytics. |
| `string_of_pivot_values` | `string` | Comma-separated string of pivot values for this analytics record |
| `postClickJobApplications` | `number` | Job applications initiated post-clicking on the ad. |
| `postClickJobApplyClicks` | `number` | Clicks on apply job button post-clicking on the ad. |
| `postClickRegistrations` | `number` | Registrations completed post-clicking on the ad. |
| `postViewJobApplications` | `number` | Job applications initiated post-viewing the ad. |
| `postViewJobApplyClicks` | `number` | Clicks on apply job button post-viewing the ad. |
| `postViewRegistrations` | `number` | Registrations completed post-viewing the ad. |
| `reactions` | `number` | Total reactions (e.g., like, love, celebrate) on the ad. |
| `registrations` | `number` | Total registrations completed through the ad. |
| `sends` | `number` | Number of messages sent through the ad. |
| `shares` | `number` | Total shares generated by the ad. |
| `start_date` | `string` | Start date of the ad analytics data. |
| `talentLeads` | `number` | Number of leads related to talent acquisition. |
| `textUrlClicks` | `number` | Clicks on text URLs within the ad. |
| `totalEngagements` | `number` | Total number of engagements on the ad. |
| `validWorkEmailLeads` | `number` | Leads generated through valid work emails. |
| `videoCompletions` | `number` | Number of times videos were watched till completion. |
| `videoFirstQuartileCompletions` | `number` | Completions for first quartile of video views. |
| `videoMidpointCompletions` | `number` | Completions for midpoint of video views. |
| `videoStarts` | `number` | Total video starts initiated by users. |
| `videoThirdQuartileCompletions` | `number` | Completions for third quartile of video views. |
| `videoViews` | `number` | Total views of videos in the ad. |
| `viralCardClicks` | `number` | Clicks on interactive card components in viral distribution. |
| `viralCardImpressions` | `number` | Impressions of interactive cards in viral distribution. |
| `viralClicks` | `number` | Total clicks in viral distribution of the ad. |
| `viralCommentLikes` | `number` | Likes received on comments in viral distribution. |
| `viralComments` | `number` | Number of comments in viral distribution of the ad. |
| `viralCompanyPageClicks` | `number` | Clicks on the company page in viral distribution. |
| `viralDocumentCompletions` | `number` | Complete views of documents in viral distribution. |
| `viralDocumentFirstQuartileCompletions` | `number` | First quartile completions of documents in viral distribution. |
| `viralDocumentMidpointCompletions` | `number` | Midpoint completions of documents in viral distribution. |
| `viralDocumentThirdQuartileCompletions` | `number` | Third quartile completions of documents in viral distribution. |
| `viralDownloadClicks` | `number` | Clicks on downloads in viral distribution of the ad. |
| `viralExternalWebsiteConversions` | `number` | External website conversions in viral distribution. |
| `viralExternalWebsitePostClickConversions` | `number` | Post-click conversions on external websites in viral distribution. |
| `viralExternalWebsitePostViewConversions` | `number` | Post-view conversions on external websites in viral distribution. |
| `viralFollows` | `number` | Follows generated in viral distribution of the ad. |
| `viralFullScreenPlays` | `number` | Fullscreen video plays in viral distribution. |
| `viralImpressions` | `number` | Total impressions in viral distribution of the ad. |
| `viralJobApplications` | `number` | Job applications initiated in viral distribution. |
| `viralJobApplyClicks` | `number` | Clicks on apply job button in viral distribution of the ad. |
| `viralLandingPageClicks` | `number` | Clicks on landing page in viral distribution. |
| `viralLikes` | `number` | Total likes in viral distribution of the ad. |
| `viralOneClickLeadFormOpens` | `number` | One-click lead form opens in viral distribution. |
| `viralOneClickLeads` | `number` | Leads generated in one click in viral distribution. |
| `viralOtherEngagements` | `number` | Other engagements in viral distribution of the ad. |
| `viralPostClickJobApplications` | `number` | Job applications initiated post-clicking in viral distribution. |
| `viralPostClickJobApplyClicks` | `number` | Clicks on apply job button post-clicking in viral distribution. |
| `viralPostClickRegistrations` | `number` | Registrations completed post-clicking in viral distribution. |
| `viralPostViewJobApplications` | `number` | Job applications initiated post-viewing in viral distribution. |
| `viralPostViewJobApplyClicks` | `number` | Clicks on apply job button post-viewing in viral distribution. |
| `viralPostViewRegistrations` | `number` | Registrations completed post-viewing in viral distribution. |
| `viralReactions` | `number` | Total reactions in viral distribution of the ad. |
| `viralRegistrations` | `number` | Total registrations in viral distribution of the ad. |
| `viralShares` | `number` | Total shares in viral distribution of the ad. |
| `viralTotalEngagements` | `number` | Total engagements in viral distribution of the ad. |
| `viralVideoCompletions` | `number` | Completions of videos in viral distribution. |
| `viralVideoFirstQuartileCompletions` | `number` | First quartile completions of videos in viral distribution. |
| `viralVideoMidpointCompletions` | `number` | Midpoint completions of videos in viral distribution. |
| `viralVideoStarts` | `number` | Total video starts in viral distribution of the ad. |
| `viralVideoThirdQuartileCompletions` | `number` | Third quartile completions of videos in viral distribution. |
| `viralVideoViews` | `number` | Total views of videos in viral distribution of the ad. |
| `pivot` | `string` | Pivot dimension used for this analytics record |
| `sponsoredCreative` | `string` | Sponsored creative |

<details>
<summary><b>Response Schema</b></summary>

| Field Name | Type | Description |
|------------|------|-------------|
| `data` | `array` | List of matching records |
| `meta` | `object` | Pagination metadata |
| `meta.has_more` | `boolean` | Whether additional pages are available |
| `meta.cursor` | `string \| null` | Cursor for next page of results |
| `meta.took_ms` | `number \| null` | Query execution time in milliseconds |
| `data[].actionClicks` | `number` | The number of clicks on action buttons in the ad. |
| `data[].adUnitClicks` | `number` | The number of clicks on ad unit components. |
| `data[].approximateMemberReach` | `number` | An approximation of unique ad impressions. |
| `data[].cardClicks` | `number` | The number of clicks on interactive card elements. |
| `data[].cardImpressions` | `number` | The number of times interactive cards were displayed. |
| `data[].clicks` | `number` | Total number of clicks on the ad. |
| `data[].commentLikes` | `number` | The count of likes on comments related to the ad. |
| `data[].comments` | `number` | The number of comments on the ad. |
| `data[].companyPageClicks` | `number` | Clicks on the company page associated with the ad. |
| `data[].conversionValueInLocalCurrency` | `number` | Conversion value in the local currency. |
| `data[].costInLocalCurrency` | `number` | Cost of ad campaign in the local currency. |
| `data[].costInUsd` | `number` | Cost of ad campaign in USD. |
| `data[].documentCompletions` | `number` | Number of completions for document views. |
| `data[].documentFirstQuartileCompletions` | `number` | Completions for first quartile of document views. |
| `data[].documentMidpointCompletions` | `number` | Completions for midpoint of document views. |
| `data[].documentThirdQuartileCompletions` | `number` | Completions for third quartile of document views. |
| `data[].downloadClicks` | `number` | Clicks on download links in the ad. |
| `data[].end_date` | `string` | End date of the ad analytics data. |
| `data[].externalWebsiteConversions` | `number` | Conversions that lead to external websites. |
| `data[].externalWebsitePostClickConversions` | `number` | Post-click conversions on external websites. |
| `data[].externalWebsitePostViewConversions` | `number` | Post-view conversions on external websites. |
| `data[].follows` | `number` | Number of follows generated by the ad. |
| `data[].fullScreenPlays` | `number` | Number of times videos were played in fullscreen mode. |
| `data[].impressions` | `number` | Total number of times the ad was displayed. |
| `data[].jobApplications` | `number` | Number of job applications initiated through the ad. |
| `data[].jobApplyClicks` | `number` | Clicks on apply job button in the ad. |
| `data[].landingPageClicks` | `number` | Clicks on the landing page associated with the ad. |
| `data[].leadGenerationMailContactInfoShares` | `number` | Shares of contact information through lead generation. |
| `data[].leadGenerationMailInterestedClicks` | `number` | Clicks on expressing interest through lead generation mail. |
| `data[].likes` | `number` | Total likes received on the ad. |
| `data[].oneClickLeadFormOpens` | `number` | Number of times lead forms were opened in one click. |
| `data[].oneClickLeads` | `number` | Leads generated in one click. |
| `data[].opens` | `number` | The number of times the ad was opened or expanded. |
| `data[].otherEngagements` | `number` | Engagements other than clicks on the ad. |
| `data[].pivotValues` | `array` | Values used for pivoting the analytics. |
| `data[].string_of_pivot_values` | `string` | Comma-separated string of pivot values for this analytics record |
| `data[].postClickJobApplications` | `number` | Job applications initiated post-clicking on the ad. |
| `data[].postClickJobApplyClicks` | `number` | Clicks on apply job button post-clicking on the ad. |
| `data[].postClickRegistrations` | `number` | Registrations completed post-clicking on the ad. |
| `data[].postViewJobApplications` | `number` | Job applications initiated post-viewing the ad. |
| `data[].postViewJobApplyClicks` | `number` | Clicks on apply job button post-viewing the ad. |
| `data[].postViewRegistrations` | `number` | Registrations completed post-viewing the ad. |
| `data[].reactions` | `number` | Total reactions (e.g., like, love, celebrate) on the ad. |
| `data[].registrations` | `number` | Total registrations completed through the ad. |
| `data[].sends` | `number` | Number of messages sent through the ad. |
| `data[].shares` | `number` | Total shares generated by the ad. |
| `data[].start_date` | `string` | Start date of the ad analytics data. |
| `data[].talentLeads` | `number` | Number of leads related to talent acquisition. |
| `data[].textUrlClicks` | `number` | Clicks on text URLs within the ad. |
| `data[].totalEngagements` | `number` | Total number of engagements on the ad. |
| `data[].validWorkEmailLeads` | `number` | Leads generated through valid work emails. |
| `data[].videoCompletions` | `number` | Number of times videos were watched till completion. |
| `data[].videoFirstQuartileCompletions` | `number` | Completions for first quartile of video views. |
| `data[].videoMidpointCompletions` | `number` | Completions for midpoint of video views. |
| `data[].videoStarts` | `number` | Total video starts initiated by users. |
| `data[].videoThirdQuartileCompletions` | `number` | Completions for third quartile of video views. |
| `data[].videoViews` | `number` | Total views of videos in the ad. |
| `data[].viralCardClicks` | `number` | Clicks on interactive card components in viral distribution. |
| `data[].viralCardImpressions` | `number` | Impressions of interactive cards in viral distribution. |
| `data[].viralClicks` | `number` | Total clicks in viral distribution of the ad. |
| `data[].viralCommentLikes` | `number` | Likes received on comments in viral distribution. |
| `data[].viralComments` | `number` | Number of comments in viral distribution of the ad. |
| `data[].viralCompanyPageClicks` | `number` | Clicks on the company page in viral distribution. |
| `data[].viralDocumentCompletions` | `number` | Complete views of documents in viral distribution. |
| `data[].viralDocumentFirstQuartileCompletions` | `number` | First quartile completions of documents in viral distribution. |
| `data[].viralDocumentMidpointCompletions` | `number` | Midpoint completions of documents in viral distribution. |
| `data[].viralDocumentThirdQuartileCompletions` | `number` | Third quartile completions of documents in viral distribution. |
| `data[].viralDownloadClicks` | `number` | Clicks on downloads in viral distribution of the ad. |
| `data[].viralExternalWebsiteConversions` | `number` | External website conversions in viral distribution. |
| `data[].viralExternalWebsitePostClickConversions` | `number` | Post-click conversions on external websites in viral distribution. |
| `data[].viralExternalWebsitePostViewConversions` | `number` | Post-view conversions on external websites in viral distribution. |
| `data[].viralFollows` | `number` | Follows generated in viral distribution of the ad. |
| `data[].viralFullScreenPlays` | `number` | Fullscreen video plays in viral distribution. |
| `data[].viralImpressions` | `number` | Total impressions in viral distribution of the ad. |
| `data[].viralJobApplications` | `number` | Job applications initiated in viral distribution. |
| `data[].viralJobApplyClicks` | `number` | Clicks on apply job button in viral distribution of the ad. |
| `data[].viralLandingPageClicks` | `number` | Clicks on landing page in viral distribution. |
| `data[].viralLikes` | `number` | Total likes in viral distribution of the ad. |
| `data[].viralOneClickLeadFormOpens` | `number` | One-click lead form opens in viral distribution. |
| `data[].viralOneClickLeads` | `number` | Leads generated in one click in viral distribution. |
| `data[].viralOtherEngagements` | `number` | Other engagements in viral distribution of the ad. |
| `data[].viralPostClickJobApplications` | `number` | Job applications initiated post-clicking in viral distribution. |
| `data[].viralPostClickJobApplyClicks` | `number` | Clicks on apply job button post-clicking in viral distribution. |
| `data[].viralPostClickRegistrations` | `number` | Registrations completed post-clicking in viral distribution. |
| `data[].viralPostViewJobApplications` | `number` | Job applications initiated post-viewing in viral distribution. |
| `data[].viralPostViewJobApplyClicks` | `number` | Clicks on apply job button post-viewing in viral distribution. |
| `data[].viralPostViewRegistrations` | `number` | Registrations completed post-viewing in viral distribution. |
| `data[].viralReactions` | `number` | Total reactions in viral distribution of the ad. |
| `data[].viralRegistrations` | `number` | Total registrations in viral distribution of the ad. |
| `data[].viralShares` | `number` | Total shares in viral distribution of the ad. |
| `data[].viralTotalEngagements` | `number` | Total engagements in viral distribution of the ad. |
| `data[].viralVideoCompletions` | `number` | Completions of videos in viral distribution. |
| `data[].viralVideoFirstQuartileCompletions` | `number` | First quartile completions of videos in viral distribution. |
| `data[].viralVideoMidpointCompletions` | `number` | Midpoint completions of videos in viral distribution. |
| `data[].viralVideoStarts` | `number` | Total video starts in viral distribution of the ad. |
| `data[].viralVideoThirdQuartileCompletions` | `number` | Third quartile completions of videos in viral distribution. |
| `data[].viralVideoViews` | `number` | Total views of videos in viral distribution of the ad. |
| `data[].pivot` | `string` | Pivot dimension used for this analytics record |
| `data[].sponsoredCreative` | `string` | Sponsored creative |

</details>

## Ad Impression Device Analytics

### Ad Impression Device Analytics List

Returns ad analytics data pivoted by impression device type. Provides performance metrics including clicks, impressions, spend, and engagement data grouped by impression device type.


#### CLI

```bash
airbyte-agent connectors execute --json '{
  "workspace": "<your_workspace_name>",
  "name": "linkedin-ads",
  "entity": "ad_impression_device_analytics",
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

#### Python SDK

```python
await linkedin_ads.ad_impression_device_analytics.list(
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
    "entity": "ad_impression_device_analytics",
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
| `q` | `string` | Yes | LinkedIn API finder method for querying ad analytics |
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

### Ad Impression Device Analytics Context Store Search

Search and filter ad impression device analytics records powered by Airbyte's data sync. This often provides additional fields and operators beyond what the API natively supports, making it easier to narrow down results before performing further operations. Only available in hosted mode.

#### CLI

```bash
airbyte-agent connectors execute --json '{
  "workspace": "<your_workspace_name>",
  "name": "linkedin-ads",
  "entity": "ad_impression_device_analytics",
  "action": "context_store_search",
  "params": {
    "query": {
      "filter": {
        "eq": {
          "actionClicks": 0.0
        }
      }
    }
  }
}'
```

#### Python SDK

```python
await linkedin_ads.ad_impression_device_analytics.context_store_search(
    query={"filter": {"eq": {"actionClicks": 0.0}}}
)
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/integrations/connectors/{your_connector_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "ad_impression_device_analytics",
    "action": "context_store_search",
    "params": {
        "query": {"filter": {"eq": {"actionClicks": 0.0}}}
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
| `actionClicks` | `number` | The number of clicks on action buttons in the ad. |
| `adUnitClicks` | `number` | The number of clicks on ad unit components. |
| `approximateMemberReach` | `number` | An approximation of unique ad impressions. |
| `cardClicks` | `number` | The number of clicks on interactive card elements. |
| `cardImpressions` | `number` | The number of times interactive cards were displayed. |
| `clicks` | `number` | Total number of clicks on the ad. |
| `commentLikes` | `number` | The count of likes on comments related to the ad. |
| `comments` | `number` | The number of comments on the ad. |
| `companyPageClicks` | `number` | Clicks on the company page associated with the ad. |
| `conversionValueInLocalCurrency` | `number` | Conversion value in the local currency. |
| `costInLocalCurrency` | `number` | Cost of ad campaign in the local currency. |
| `costInUsd` | `number` | Cost of ad campaign in USD. |
| `documentCompletions` | `number` | Number of completions for document views. |
| `documentFirstQuartileCompletions` | `number` | Completions for first quartile of document views. |
| `documentMidpointCompletions` | `number` | Completions for midpoint of document views. |
| `documentThirdQuartileCompletions` | `number` | Completions for third quartile of document views. |
| `downloadClicks` | `number` | Clicks on download links in the ad. |
| `end_date` | `string` | End date of the ad analytics data. |
| `externalWebsiteConversions` | `number` | Conversions that lead to external websites. |
| `externalWebsitePostClickConversions` | `number` | Post-click conversions on external websites. |
| `externalWebsitePostViewConversions` | `number` | Post-view conversions on external websites. |
| `follows` | `number` | Number of follows generated by the ad. |
| `fullScreenPlays` | `number` | Number of times videos were played in fullscreen mode. |
| `impressions` | `number` | Total number of times the ad was displayed. |
| `jobApplications` | `number` | Number of job applications initiated through the ad. |
| `jobApplyClicks` | `number` | Clicks on apply job button in the ad. |
| `landingPageClicks` | `number` | Clicks on the landing page associated with the ad. |
| `leadGenerationMailContactInfoShares` | `number` | Shares of contact information through lead generation. |
| `leadGenerationMailInterestedClicks` | `number` | Clicks on expressing interest through lead generation mail. |
| `likes` | `number` | Total likes received on the ad. |
| `oneClickLeadFormOpens` | `number` | Number of times lead forms were opened in one click. |
| `oneClickLeads` | `number` | Leads generated in one click. |
| `opens` | `number` | The number of times the ad was opened or expanded. |
| `otherEngagements` | `number` | Engagements other than clicks on the ad. |
| `pivotValues` | `array` | Values used for pivoting the analytics. |
| `string_of_pivot_values` | `string` | Comma-separated string of pivot values for this analytics record |
| `postClickJobApplications` | `number` | Job applications initiated post-clicking on the ad. |
| `postClickJobApplyClicks` | `number` | Clicks on apply job button post-clicking on the ad. |
| `postClickRegistrations` | `number` | Registrations completed post-clicking on the ad. |
| `postViewJobApplications` | `number` | Job applications initiated post-viewing the ad. |
| `postViewJobApplyClicks` | `number` | Clicks on apply job button post-viewing the ad. |
| `postViewRegistrations` | `number` | Registrations completed post-viewing the ad. |
| `reactions` | `number` | Total reactions (e.g., like, love, celebrate) on the ad. |
| `registrations` | `number` | Total registrations completed through the ad. |
| `sends` | `number` | Number of messages sent through the ad. |
| `shares` | `number` | Total shares generated by the ad. |
| `start_date` | `string` | Start date of the ad analytics data. |
| `talentLeads` | `number` | Number of leads related to talent acquisition. |
| `textUrlClicks` | `number` | Clicks on text URLs within the ad. |
| `totalEngagements` | `number` | Total number of engagements on the ad. |
| `validWorkEmailLeads` | `number` | Leads generated through valid work emails. |
| `videoCompletions` | `number` | Number of times videos were watched till completion. |
| `videoFirstQuartileCompletions` | `number` | Completions for first quartile of video views. |
| `videoMidpointCompletions` | `number` | Completions for midpoint of video views. |
| `videoStarts` | `number` | Total video starts initiated by users. |
| `videoThirdQuartileCompletions` | `number` | Completions for third quartile of video views. |
| `videoViews` | `number` | Total views of videos in the ad. |
| `viralCardClicks` | `number` | Clicks on interactive card components in viral distribution. |
| `viralCardImpressions` | `number` | Impressions of interactive cards in viral distribution. |
| `viralClicks` | `number` | Total clicks in viral distribution of the ad. |
| `viralCommentLikes` | `number` | Likes received on comments in viral distribution. |
| `viralComments` | `number` | Number of comments in viral distribution of the ad. |
| `viralCompanyPageClicks` | `number` | Clicks on the company page in viral distribution. |
| `viralDocumentCompletions` | `number` | Complete views of documents in viral distribution. |
| `viralDocumentFirstQuartileCompletions` | `number` | First quartile completions of documents in viral distribution. |
| `viralDocumentMidpointCompletions` | `number` | Midpoint completions of documents in viral distribution. |
| `viralDocumentThirdQuartileCompletions` | `number` | Third quartile completions of documents in viral distribution. |
| `viralDownloadClicks` | `number` | Clicks on downloads in viral distribution of the ad. |
| `viralExternalWebsiteConversions` | `number` | External website conversions in viral distribution. |
| `viralExternalWebsitePostClickConversions` | `number` | Post-click conversions on external websites in viral distribution. |
| `viralExternalWebsitePostViewConversions` | `number` | Post-view conversions on external websites in viral distribution. |
| `viralFollows` | `number` | Follows generated in viral distribution of the ad. |
| `viralFullScreenPlays` | `number` | Fullscreen video plays in viral distribution. |
| `viralImpressions` | `number` | Total impressions in viral distribution of the ad. |
| `viralJobApplications` | `number` | Job applications initiated in viral distribution. |
| `viralJobApplyClicks` | `number` | Clicks on apply job button in viral distribution of the ad. |
| `viralLandingPageClicks` | `number` | Clicks on landing page in viral distribution. |
| `viralLikes` | `number` | Total likes in viral distribution of the ad. |
| `viralOneClickLeadFormOpens` | `number` | One-click lead form opens in viral distribution. |
| `viralOneClickLeads` | `number` | Leads generated in one click in viral distribution. |
| `viralOtherEngagements` | `number` | Other engagements in viral distribution of the ad. |
| `viralPostClickJobApplications` | `number` | Job applications initiated post-clicking in viral distribution. |
| `viralPostClickJobApplyClicks` | `number` | Clicks on apply job button post-clicking in viral distribution. |
| `viralPostClickRegistrations` | `number` | Registrations completed post-clicking in viral distribution. |
| `viralPostViewJobApplications` | `number` | Job applications initiated post-viewing in viral distribution. |
| `viralPostViewJobApplyClicks` | `number` | Clicks on apply job button post-viewing in viral distribution. |
| `viralPostViewRegistrations` | `number` | Registrations completed post-viewing in viral distribution. |
| `viralReactions` | `number` | Total reactions in viral distribution of the ad. |
| `viralRegistrations` | `number` | Total registrations in viral distribution of the ad. |
| `viralShares` | `number` | Total shares in viral distribution of the ad. |
| `viralTotalEngagements` | `number` | Total engagements in viral distribution of the ad. |
| `viralVideoCompletions` | `number` | Completions of videos in viral distribution. |
| `viralVideoFirstQuartileCompletions` | `number` | First quartile completions of videos in viral distribution. |
| `viralVideoMidpointCompletions` | `number` | Midpoint completions of videos in viral distribution. |
| `viralVideoStarts` | `number` | Total video starts in viral distribution of the ad. |
| `viralVideoThirdQuartileCompletions` | `number` | Third quartile completions of videos in viral distribution. |
| `viralVideoViews` | `number` | Total views of videos in viral distribution of the ad. |
| `pivot` | `string` | Pivot dimension used for this analytics record |
| `sponsoredCampaign` | `string` | URN of the sponsored campaign this analytics record belongs to |

<details>
<summary><b>Response Schema</b></summary>

| Field Name | Type | Description |
|------------|------|-------------|
| `data` | `array` | List of matching records |
| `meta` | `object` | Pagination metadata |
| `meta.has_more` | `boolean` | Whether additional pages are available |
| `meta.cursor` | `string \| null` | Cursor for next page of results |
| `meta.took_ms` | `number \| null` | Query execution time in milliseconds |
| `data[].actionClicks` | `number` | The number of clicks on action buttons in the ad. |
| `data[].adUnitClicks` | `number` | The number of clicks on ad unit components. |
| `data[].approximateMemberReach` | `number` | An approximation of unique ad impressions. |
| `data[].cardClicks` | `number` | The number of clicks on interactive card elements. |
| `data[].cardImpressions` | `number` | The number of times interactive cards were displayed. |
| `data[].clicks` | `number` | Total number of clicks on the ad. |
| `data[].commentLikes` | `number` | The count of likes on comments related to the ad. |
| `data[].comments` | `number` | The number of comments on the ad. |
| `data[].companyPageClicks` | `number` | Clicks on the company page associated with the ad. |
| `data[].conversionValueInLocalCurrency` | `number` | Conversion value in the local currency. |
| `data[].costInLocalCurrency` | `number` | Cost of ad campaign in the local currency. |
| `data[].costInUsd` | `number` | Cost of ad campaign in USD. |
| `data[].documentCompletions` | `number` | Number of completions for document views. |
| `data[].documentFirstQuartileCompletions` | `number` | Completions for first quartile of document views. |
| `data[].documentMidpointCompletions` | `number` | Completions for midpoint of document views. |
| `data[].documentThirdQuartileCompletions` | `number` | Completions for third quartile of document views. |
| `data[].downloadClicks` | `number` | Clicks on download links in the ad. |
| `data[].end_date` | `string` | End date of the ad analytics data. |
| `data[].externalWebsiteConversions` | `number` | Conversions that lead to external websites. |
| `data[].externalWebsitePostClickConversions` | `number` | Post-click conversions on external websites. |
| `data[].externalWebsitePostViewConversions` | `number` | Post-view conversions on external websites. |
| `data[].follows` | `number` | Number of follows generated by the ad. |
| `data[].fullScreenPlays` | `number` | Number of times videos were played in fullscreen mode. |
| `data[].impressions` | `number` | Total number of times the ad was displayed. |
| `data[].jobApplications` | `number` | Number of job applications initiated through the ad. |
| `data[].jobApplyClicks` | `number` | Clicks on apply job button in the ad. |
| `data[].landingPageClicks` | `number` | Clicks on the landing page associated with the ad. |
| `data[].leadGenerationMailContactInfoShares` | `number` | Shares of contact information through lead generation. |
| `data[].leadGenerationMailInterestedClicks` | `number` | Clicks on expressing interest through lead generation mail. |
| `data[].likes` | `number` | Total likes received on the ad. |
| `data[].oneClickLeadFormOpens` | `number` | Number of times lead forms were opened in one click. |
| `data[].oneClickLeads` | `number` | Leads generated in one click. |
| `data[].opens` | `number` | The number of times the ad was opened or expanded. |
| `data[].otherEngagements` | `number` | Engagements other than clicks on the ad. |
| `data[].pivotValues` | `array` | Values used for pivoting the analytics. |
| `data[].string_of_pivot_values` | `string` | Comma-separated string of pivot values for this analytics record |
| `data[].postClickJobApplications` | `number` | Job applications initiated post-clicking on the ad. |
| `data[].postClickJobApplyClicks` | `number` | Clicks on apply job button post-clicking on the ad. |
| `data[].postClickRegistrations` | `number` | Registrations completed post-clicking on the ad. |
| `data[].postViewJobApplications` | `number` | Job applications initiated post-viewing the ad. |
| `data[].postViewJobApplyClicks` | `number` | Clicks on apply job button post-viewing the ad. |
| `data[].postViewRegistrations` | `number` | Registrations completed post-viewing the ad. |
| `data[].reactions` | `number` | Total reactions (e.g., like, love, celebrate) on the ad. |
| `data[].registrations` | `number` | Total registrations completed through the ad. |
| `data[].sends` | `number` | Number of messages sent through the ad. |
| `data[].shares` | `number` | Total shares generated by the ad. |
| `data[].start_date` | `string` | Start date of the ad analytics data. |
| `data[].talentLeads` | `number` | Number of leads related to talent acquisition. |
| `data[].textUrlClicks` | `number` | Clicks on text URLs within the ad. |
| `data[].totalEngagements` | `number` | Total number of engagements on the ad. |
| `data[].validWorkEmailLeads` | `number` | Leads generated through valid work emails. |
| `data[].videoCompletions` | `number` | Number of times videos were watched till completion. |
| `data[].videoFirstQuartileCompletions` | `number` | Completions for first quartile of video views. |
| `data[].videoMidpointCompletions` | `number` | Completions for midpoint of video views. |
| `data[].videoStarts` | `number` | Total video starts initiated by users. |
| `data[].videoThirdQuartileCompletions` | `number` | Completions for third quartile of video views. |
| `data[].videoViews` | `number` | Total views of videos in the ad. |
| `data[].viralCardClicks` | `number` | Clicks on interactive card components in viral distribution. |
| `data[].viralCardImpressions` | `number` | Impressions of interactive cards in viral distribution. |
| `data[].viralClicks` | `number` | Total clicks in viral distribution of the ad. |
| `data[].viralCommentLikes` | `number` | Likes received on comments in viral distribution. |
| `data[].viralComments` | `number` | Number of comments in viral distribution of the ad. |
| `data[].viralCompanyPageClicks` | `number` | Clicks on the company page in viral distribution. |
| `data[].viralDocumentCompletions` | `number` | Complete views of documents in viral distribution. |
| `data[].viralDocumentFirstQuartileCompletions` | `number` | First quartile completions of documents in viral distribution. |
| `data[].viralDocumentMidpointCompletions` | `number` | Midpoint completions of documents in viral distribution. |
| `data[].viralDocumentThirdQuartileCompletions` | `number` | Third quartile completions of documents in viral distribution. |
| `data[].viralDownloadClicks` | `number` | Clicks on downloads in viral distribution of the ad. |
| `data[].viralExternalWebsiteConversions` | `number` | External website conversions in viral distribution. |
| `data[].viralExternalWebsitePostClickConversions` | `number` | Post-click conversions on external websites in viral distribution. |
| `data[].viralExternalWebsitePostViewConversions` | `number` | Post-view conversions on external websites in viral distribution. |
| `data[].viralFollows` | `number` | Follows generated in viral distribution of the ad. |
| `data[].viralFullScreenPlays` | `number` | Fullscreen video plays in viral distribution. |
| `data[].viralImpressions` | `number` | Total impressions in viral distribution of the ad. |
| `data[].viralJobApplications` | `number` | Job applications initiated in viral distribution. |
| `data[].viralJobApplyClicks` | `number` | Clicks on apply job button in viral distribution of the ad. |
| `data[].viralLandingPageClicks` | `number` | Clicks on landing page in viral distribution. |
| `data[].viralLikes` | `number` | Total likes in viral distribution of the ad. |
| `data[].viralOneClickLeadFormOpens` | `number` | One-click lead form opens in viral distribution. |
| `data[].viralOneClickLeads` | `number` | Leads generated in one click in viral distribution. |
| `data[].viralOtherEngagements` | `number` | Other engagements in viral distribution of the ad. |
| `data[].viralPostClickJobApplications` | `number` | Job applications initiated post-clicking in viral distribution. |
| `data[].viralPostClickJobApplyClicks` | `number` | Clicks on apply job button post-clicking in viral distribution. |
| `data[].viralPostClickRegistrations` | `number` | Registrations completed post-clicking in viral distribution. |
| `data[].viralPostViewJobApplications` | `number` | Job applications initiated post-viewing in viral distribution. |
| `data[].viralPostViewJobApplyClicks` | `number` | Clicks on apply job button post-viewing in viral distribution. |
| `data[].viralPostViewRegistrations` | `number` | Registrations completed post-viewing in viral distribution. |
| `data[].viralReactions` | `number` | Total reactions in viral distribution of the ad. |
| `data[].viralRegistrations` | `number` | Total registrations in viral distribution of the ad. |
| `data[].viralShares` | `number` | Total shares in viral distribution of the ad. |
| `data[].viralTotalEngagements` | `number` | Total engagements in viral distribution of the ad. |
| `data[].viralVideoCompletions` | `number` | Completions of videos in viral distribution. |
| `data[].viralVideoFirstQuartileCompletions` | `number` | First quartile completions of videos in viral distribution. |
| `data[].viralVideoMidpointCompletions` | `number` | Midpoint completions of videos in viral distribution. |
| `data[].viralVideoStarts` | `number` | Total video starts in viral distribution of the ad. |
| `data[].viralVideoThirdQuartileCompletions` | `number` | Third quartile completions of videos in viral distribution. |
| `data[].viralVideoViews` | `number` | Total views of videos in viral distribution of the ad. |
| `data[].pivot` | `string` | Pivot dimension used for this analytics record |
| `data[].sponsoredCampaign` | `string` | URN of the sponsored campaign this analytics record belongs to |

</details>

## Ad Member Company Analytics

### Ad Member Company Analytics List

Returns ad analytics data pivoted by member company. Provides performance metrics including clicks, impressions, spend, and engagement data grouped by member company.


#### CLI

```bash
airbyte-agent connectors execute --json '{
  "workspace": "<your_workspace_name>",
  "name": "linkedin-ads",
  "entity": "ad_member_company_analytics",
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

#### Python SDK

```python
await linkedin_ads.ad_member_company_analytics.list(
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
    "entity": "ad_member_company_analytics",
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
| `q` | `string` | Yes | LinkedIn API finder method for querying ad analytics |
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

### Ad Member Company Analytics Context Store Search

Search and filter ad member company analytics records powered by Airbyte's data sync. This often provides additional fields and operators beyond what the API natively supports, making it easier to narrow down results before performing further operations. Only available in hosted mode.

#### CLI

```bash
airbyte-agent connectors execute --json '{
  "workspace": "<your_workspace_name>",
  "name": "linkedin-ads",
  "entity": "ad_member_company_analytics",
  "action": "context_store_search",
  "params": {
    "query": {
      "filter": {
        "eq": {
          "actionClicks": 0.0
        }
      }
    }
  }
}'
```

#### Python SDK

```python
await linkedin_ads.ad_member_company_analytics.context_store_search(
    query={"filter": {"eq": {"actionClicks": 0.0}}}
)
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/integrations/connectors/{your_connector_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "ad_member_company_analytics",
    "action": "context_store_search",
    "params": {
        "query": {"filter": {"eq": {"actionClicks": 0.0}}}
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
| `actionClicks` | `number` | The number of clicks on action buttons in the ad. |
| `adUnitClicks` | `number` | The number of clicks on ad unit components. |
| `approximateMemberReach` | `number` | An approximation of unique ad impressions. |
| `cardClicks` | `number` | The number of clicks on interactive card elements. |
| `cardImpressions` | `number` | The number of times interactive cards were displayed. |
| `clicks` | `number` | Total number of clicks on the ad. |
| `commentLikes` | `number` | The count of likes on comments related to the ad. |
| `comments` | `number` | The number of comments on the ad. |
| `companyPageClicks` | `number` | Clicks on the company page associated with the ad. |
| `conversionValueInLocalCurrency` | `number` | Conversion value in the local currency. |
| `costInLocalCurrency` | `number` | Cost of ad campaign in the local currency. |
| `costInUsd` | `number` | Cost of ad campaign in USD. |
| `documentCompletions` | `number` | Number of completions for document views. |
| `documentFirstQuartileCompletions` | `number` | Completions for first quartile of document views. |
| `documentMidpointCompletions` | `number` | Completions for midpoint of document views. |
| `documentThirdQuartileCompletions` | `number` | Completions for third quartile of document views. |
| `downloadClicks` | `number` | Clicks on download links in the ad. |
| `end_date` | `string` | End date of the ad analytics data. |
| `externalWebsiteConversions` | `number` | Conversions that lead to external websites. |
| `externalWebsitePostClickConversions` | `number` | Post-click conversions on external websites. |
| `externalWebsitePostViewConversions` | `number` | Post-view conversions on external websites. |
| `follows` | `number` | Number of follows generated by the ad. |
| `fullScreenPlays` | `number` | Number of times videos were played in fullscreen mode. |
| `impressions` | `number` | Total number of times the ad was displayed. |
| `jobApplications` | `number` | Number of job applications initiated through the ad. |
| `jobApplyClicks` | `number` | Clicks on apply job button in the ad. |
| `landingPageClicks` | `number` | Clicks on the landing page associated with the ad. |
| `leadGenerationMailContactInfoShares` | `number` | Shares of contact information through lead generation. |
| `leadGenerationMailInterestedClicks` | `number` | Clicks on expressing interest through lead generation mail. |
| `likes` | `number` | Total likes received on the ad. |
| `oneClickLeadFormOpens` | `number` | Number of times lead forms were opened in one click. |
| `oneClickLeads` | `number` | Leads generated in one click. |
| `opens` | `number` | The number of times the ad was opened or expanded. |
| `otherEngagements` | `number` | Engagements other than clicks on the ad. |
| `pivotValues` | `array` | Values used for pivoting the analytics. |
| `string_of_pivot_values` | `string` | Comma-separated string of pivot values for this analytics record |
| `postClickJobApplications` | `number` | Job applications initiated post-clicking on the ad. |
| `postClickJobApplyClicks` | `number` | Clicks on apply job button post-clicking on the ad. |
| `postClickRegistrations` | `number` | Registrations completed post-clicking on the ad. |
| `postViewJobApplications` | `number` | Job applications initiated post-viewing the ad. |
| `postViewJobApplyClicks` | `number` | Clicks on apply job button post-viewing the ad. |
| `postViewRegistrations` | `number` | Registrations completed post-viewing the ad. |
| `reactions` | `number` | Total reactions (e.g., like, love, celebrate) on the ad. |
| `registrations` | `number` | Total registrations completed through the ad. |
| `sends` | `number` | Number of messages sent through the ad. |
| `shares` | `number` | Total shares generated by the ad. |
| `start_date` | `string` | Start date of the ad analytics data. |
| `talentLeads` | `number` | Number of leads related to talent acquisition. |
| `textUrlClicks` | `number` | Clicks on text URLs within the ad. |
| `totalEngagements` | `number` | Total number of engagements on the ad. |
| `validWorkEmailLeads` | `number` | Leads generated through valid work emails. |
| `videoCompletions` | `number` | Number of times videos were watched till completion. |
| `videoFirstQuartileCompletions` | `number` | Completions for first quartile of video views. |
| `videoMidpointCompletions` | `number` | Completions for midpoint of video views. |
| `videoStarts` | `number` | Total video starts initiated by users. |
| `videoThirdQuartileCompletions` | `number` | Completions for third quartile of video views. |
| `videoViews` | `number` | Total views of videos in the ad. |
| `viralCardClicks` | `number` | Clicks on interactive card components in viral distribution. |
| `viralCardImpressions` | `number` | Impressions of interactive cards in viral distribution. |
| `viralClicks` | `number` | Total clicks in viral distribution of the ad. |
| `viralCommentLikes` | `number` | Likes received on comments in viral distribution. |
| `viralComments` | `number` | Number of comments in viral distribution of the ad. |
| `viralCompanyPageClicks` | `number` | Clicks on the company page in viral distribution. |
| `viralDocumentCompletions` | `number` | Complete views of documents in viral distribution. |
| `viralDocumentFirstQuartileCompletions` | `number` | First quartile completions of documents in viral distribution. |
| `viralDocumentMidpointCompletions` | `number` | Midpoint completions of documents in viral distribution. |
| `viralDocumentThirdQuartileCompletions` | `number` | Third quartile completions of documents in viral distribution. |
| `viralDownloadClicks` | `number` | Clicks on downloads in viral distribution of the ad. |
| `viralExternalWebsiteConversions` | `number` | External website conversions in viral distribution. |
| `viralExternalWebsitePostClickConversions` | `number` | Post-click conversions on external websites in viral distribution. |
| `viralExternalWebsitePostViewConversions` | `number` | Post-view conversions on external websites in viral distribution. |
| `viralFollows` | `number` | Follows generated in viral distribution of the ad. |
| `viralFullScreenPlays` | `number` | Fullscreen video plays in viral distribution. |
| `viralImpressions` | `number` | Total impressions in viral distribution of the ad. |
| `viralJobApplications` | `number` | Job applications initiated in viral distribution. |
| `viralJobApplyClicks` | `number` | Clicks on apply job button in viral distribution of the ad. |
| `viralLandingPageClicks` | `number` | Clicks on landing page in viral distribution. |
| `viralLikes` | `number` | Total likes in viral distribution of the ad. |
| `viralOneClickLeadFormOpens` | `number` | One-click lead form opens in viral distribution. |
| `viralOneClickLeads` | `number` | Leads generated in one click in viral distribution. |
| `viralOtherEngagements` | `number` | Other engagements in viral distribution of the ad. |
| `viralPostClickJobApplications` | `number` | Job applications initiated post-clicking in viral distribution. |
| `viralPostClickJobApplyClicks` | `number` | Clicks on apply job button post-clicking in viral distribution. |
| `viralPostClickRegistrations` | `number` | Registrations completed post-clicking in viral distribution. |
| `viralPostViewJobApplications` | `number` | Job applications initiated post-viewing in viral distribution. |
| `viralPostViewJobApplyClicks` | `number` | Clicks on apply job button post-viewing in viral distribution. |
| `viralPostViewRegistrations` | `number` | Registrations completed post-viewing in viral distribution. |
| `viralReactions` | `number` | Total reactions in viral distribution of the ad. |
| `viralRegistrations` | `number` | Total registrations in viral distribution of the ad. |
| `viralShares` | `number` | Total shares in viral distribution of the ad. |
| `viralTotalEngagements` | `number` | Total engagements in viral distribution of the ad. |
| `viralVideoCompletions` | `number` | Completions of videos in viral distribution. |
| `viralVideoFirstQuartileCompletions` | `number` | First quartile completions of videos in viral distribution. |
| `viralVideoMidpointCompletions` | `number` | Midpoint completions of videos in viral distribution. |
| `viralVideoStarts` | `number` | Total video starts in viral distribution of the ad. |
| `viralVideoThirdQuartileCompletions` | `number` | Third quartile completions of videos in viral distribution. |
| `viralVideoViews` | `number` | Total views of videos in viral distribution of the ad. |
| `pivot` | `string` | Pivot dimension used for this analytics record |
| `sponsoredCampaign` | `string` | URN of the sponsored campaign this analytics record belongs to |

<details>
<summary><b>Response Schema</b></summary>

| Field Name | Type | Description |
|------------|------|-------------|
| `data` | `array` | List of matching records |
| `meta` | `object` | Pagination metadata |
| `meta.has_more` | `boolean` | Whether additional pages are available |
| `meta.cursor` | `string \| null` | Cursor for next page of results |
| `meta.took_ms` | `number \| null` | Query execution time in milliseconds |
| `data[].actionClicks` | `number` | The number of clicks on action buttons in the ad. |
| `data[].adUnitClicks` | `number` | The number of clicks on ad unit components. |
| `data[].approximateMemberReach` | `number` | An approximation of unique ad impressions. |
| `data[].cardClicks` | `number` | The number of clicks on interactive card elements. |
| `data[].cardImpressions` | `number` | The number of times interactive cards were displayed. |
| `data[].clicks` | `number` | Total number of clicks on the ad. |
| `data[].commentLikes` | `number` | The count of likes on comments related to the ad. |
| `data[].comments` | `number` | The number of comments on the ad. |
| `data[].companyPageClicks` | `number` | Clicks on the company page associated with the ad. |
| `data[].conversionValueInLocalCurrency` | `number` | Conversion value in the local currency. |
| `data[].costInLocalCurrency` | `number` | Cost of ad campaign in the local currency. |
| `data[].costInUsd` | `number` | Cost of ad campaign in USD. |
| `data[].documentCompletions` | `number` | Number of completions for document views. |
| `data[].documentFirstQuartileCompletions` | `number` | Completions for first quartile of document views. |
| `data[].documentMidpointCompletions` | `number` | Completions for midpoint of document views. |
| `data[].documentThirdQuartileCompletions` | `number` | Completions for third quartile of document views. |
| `data[].downloadClicks` | `number` | Clicks on download links in the ad. |
| `data[].end_date` | `string` | End date of the ad analytics data. |
| `data[].externalWebsiteConversions` | `number` | Conversions that lead to external websites. |
| `data[].externalWebsitePostClickConversions` | `number` | Post-click conversions on external websites. |
| `data[].externalWebsitePostViewConversions` | `number` | Post-view conversions on external websites. |
| `data[].follows` | `number` | Number of follows generated by the ad. |
| `data[].fullScreenPlays` | `number` | Number of times videos were played in fullscreen mode. |
| `data[].impressions` | `number` | Total number of times the ad was displayed. |
| `data[].jobApplications` | `number` | Number of job applications initiated through the ad. |
| `data[].jobApplyClicks` | `number` | Clicks on apply job button in the ad. |
| `data[].landingPageClicks` | `number` | Clicks on the landing page associated with the ad. |
| `data[].leadGenerationMailContactInfoShares` | `number` | Shares of contact information through lead generation. |
| `data[].leadGenerationMailInterestedClicks` | `number` | Clicks on expressing interest through lead generation mail. |
| `data[].likes` | `number` | Total likes received on the ad. |
| `data[].oneClickLeadFormOpens` | `number` | Number of times lead forms were opened in one click. |
| `data[].oneClickLeads` | `number` | Leads generated in one click. |
| `data[].opens` | `number` | The number of times the ad was opened or expanded. |
| `data[].otherEngagements` | `number` | Engagements other than clicks on the ad. |
| `data[].pivotValues` | `array` | Values used for pivoting the analytics. |
| `data[].string_of_pivot_values` | `string` | Comma-separated string of pivot values for this analytics record |
| `data[].postClickJobApplications` | `number` | Job applications initiated post-clicking on the ad. |
| `data[].postClickJobApplyClicks` | `number` | Clicks on apply job button post-clicking on the ad. |
| `data[].postClickRegistrations` | `number` | Registrations completed post-clicking on the ad. |
| `data[].postViewJobApplications` | `number` | Job applications initiated post-viewing the ad. |
| `data[].postViewJobApplyClicks` | `number` | Clicks on apply job button post-viewing the ad. |
| `data[].postViewRegistrations` | `number` | Registrations completed post-viewing the ad. |
| `data[].reactions` | `number` | Total reactions (e.g., like, love, celebrate) on the ad. |
| `data[].registrations` | `number` | Total registrations completed through the ad. |
| `data[].sends` | `number` | Number of messages sent through the ad. |
| `data[].shares` | `number` | Total shares generated by the ad. |
| `data[].start_date` | `string` | Start date of the ad analytics data. |
| `data[].talentLeads` | `number` | Number of leads related to talent acquisition. |
| `data[].textUrlClicks` | `number` | Clicks on text URLs within the ad. |
| `data[].totalEngagements` | `number` | Total number of engagements on the ad. |
| `data[].validWorkEmailLeads` | `number` | Leads generated through valid work emails. |
| `data[].videoCompletions` | `number` | Number of times videos were watched till completion. |
| `data[].videoFirstQuartileCompletions` | `number` | Completions for first quartile of video views. |
| `data[].videoMidpointCompletions` | `number` | Completions for midpoint of video views. |
| `data[].videoStarts` | `number` | Total video starts initiated by users. |
| `data[].videoThirdQuartileCompletions` | `number` | Completions for third quartile of video views. |
| `data[].videoViews` | `number` | Total views of videos in the ad. |
| `data[].viralCardClicks` | `number` | Clicks on interactive card components in viral distribution. |
| `data[].viralCardImpressions` | `number` | Impressions of interactive cards in viral distribution. |
| `data[].viralClicks` | `number` | Total clicks in viral distribution of the ad. |
| `data[].viralCommentLikes` | `number` | Likes received on comments in viral distribution. |
| `data[].viralComments` | `number` | Number of comments in viral distribution of the ad. |
| `data[].viralCompanyPageClicks` | `number` | Clicks on the company page in viral distribution. |
| `data[].viralDocumentCompletions` | `number` | Complete views of documents in viral distribution. |
| `data[].viralDocumentFirstQuartileCompletions` | `number` | First quartile completions of documents in viral distribution. |
| `data[].viralDocumentMidpointCompletions` | `number` | Midpoint completions of documents in viral distribution. |
| `data[].viralDocumentThirdQuartileCompletions` | `number` | Third quartile completions of documents in viral distribution. |
| `data[].viralDownloadClicks` | `number` | Clicks on downloads in viral distribution of the ad. |
| `data[].viralExternalWebsiteConversions` | `number` | External website conversions in viral distribution. |
| `data[].viralExternalWebsitePostClickConversions` | `number` | Post-click conversions on external websites in viral distribution. |
| `data[].viralExternalWebsitePostViewConversions` | `number` | Post-view conversions on external websites in viral distribution. |
| `data[].viralFollows` | `number` | Follows generated in viral distribution of the ad. |
| `data[].viralFullScreenPlays` | `number` | Fullscreen video plays in viral distribution. |
| `data[].viralImpressions` | `number` | Total impressions in viral distribution of the ad. |
| `data[].viralJobApplications` | `number` | Job applications initiated in viral distribution. |
| `data[].viralJobApplyClicks` | `number` | Clicks on apply job button in viral distribution of the ad. |
| `data[].viralLandingPageClicks` | `number` | Clicks on landing page in viral distribution. |
| `data[].viralLikes` | `number` | Total likes in viral distribution of the ad. |
| `data[].viralOneClickLeadFormOpens` | `number` | One-click lead form opens in viral distribution. |
| `data[].viralOneClickLeads` | `number` | Leads generated in one click in viral distribution. |
| `data[].viralOtherEngagements` | `number` | Other engagements in viral distribution of the ad. |
| `data[].viralPostClickJobApplications` | `number` | Job applications initiated post-clicking in viral distribution. |
| `data[].viralPostClickJobApplyClicks` | `number` | Clicks on apply job button post-clicking in viral distribution. |
| `data[].viralPostClickRegistrations` | `number` | Registrations completed post-clicking in viral distribution. |
| `data[].viralPostViewJobApplications` | `number` | Job applications initiated post-viewing in viral distribution. |
| `data[].viralPostViewJobApplyClicks` | `number` | Clicks on apply job button post-viewing in viral distribution. |
| `data[].viralPostViewRegistrations` | `number` | Registrations completed post-viewing in viral distribution. |
| `data[].viralReactions` | `number` | Total reactions in viral distribution of the ad. |
| `data[].viralRegistrations` | `number` | Total registrations in viral distribution of the ad. |
| `data[].viralShares` | `number` | Total shares in viral distribution of the ad. |
| `data[].viralTotalEngagements` | `number` | Total engagements in viral distribution of the ad. |
| `data[].viralVideoCompletions` | `number` | Completions of videos in viral distribution. |
| `data[].viralVideoFirstQuartileCompletions` | `number` | First quartile completions of videos in viral distribution. |
| `data[].viralVideoMidpointCompletions` | `number` | Midpoint completions of videos in viral distribution. |
| `data[].viralVideoStarts` | `number` | Total video starts in viral distribution of the ad. |
| `data[].viralVideoThirdQuartileCompletions` | `number` | Third quartile completions of videos in viral distribution. |
| `data[].viralVideoViews` | `number` | Total views of videos in viral distribution of the ad. |
| `data[].pivot` | `string` | Pivot dimension used for this analytics record |
| `data[].sponsoredCampaign` | `string` | URN of the sponsored campaign this analytics record belongs to |

</details>

## Ad Member Company Size Analytics

### Ad Member Company Size Analytics List

Returns ad analytics data pivoted by member company size. Provides performance metrics including clicks, impressions, spend, and engagement data grouped by member company size.


#### CLI

```bash
airbyte-agent connectors execute --json '{
  "workspace": "<your_workspace_name>",
  "name": "linkedin-ads",
  "entity": "ad_member_company_size_analytics",
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

#### Python SDK

```python
await linkedin_ads.ad_member_company_size_analytics.list(
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
    "entity": "ad_member_company_size_analytics",
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
| `q` | `string` | Yes | LinkedIn API finder method for querying ad analytics |
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

### Ad Member Company Size Analytics Context Store Search

Search and filter ad member company size analytics records powered by Airbyte's data sync. This often provides additional fields and operators beyond what the API natively supports, making it easier to narrow down results before performing further operations. Only available in hosted mode.

#### CLI

```bash
airbyte-agent connectors execute --json '{
  "workspace": "<your_workspace_name>",
  "name": "linkedin-ads",
  "entity": "ad_member_company_size_analytics",
  "action": "context_store_search",
  "params": {
    "query": {
      "filter": {
        "eq": {
          "actionClicks": 0.0
        }
      }
    }
  }
}'
```

#### Python SDK

```python
await linkedin_ads.ad_member_company_size_analytics.context_store_search(
    query={"filter": {"eq": {"actionClicks": 0.0}}}
)
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/integrations/connectors/{your_connector_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "ad_member_company_size_analytics",
    "action": "context_store_search",
    "params": {
        "query": {"filter": {"eq": {"actionClicks": 0.0}}}
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
| `actionClicks` | `number` | The number of clicks on action buttons in the ad. |
| `adUnitClicks` | `number` | The number of clicks on ad unit components. |
| `approximateMemberReach` | `number` | An approximation of unique ad impressions. |
| `cardClicks` | `number` | The number of clicks on interactive card elements. |
| `cardImpressions` | `number` | The number of times interactive cards were displayed. |
| `clicks` | `number` | Total number of clicks on the ad. |
| `commentLikes` | `number` | The count of likes on comments related to the ad. |
| `comments` | `number` | The number of comments on the ad. |
| `companyPageClicks` | `number` | Clicks on the company page associated with the ad. |
| `conversionValueInLocalCurrency` | `number` | Conversion value in the local currency. |
| `costInLocalCurrency` | `number` | Cost of ad campaign in the local currency. |
| `costInUsd` | `number` | Cost of ad campaign in USD. |
| `documentCompletions` | `number` | Number of completions for document views. |
| `documentFirstQuartileCompletions` | `number` | Completions for first quartile of document views. |
| `documentMidpointCompletions` | `number` | Completions for midpoint of document views. |
| `documentThirdQuartileCompletions` | `number` | Completions for third quartile of document views. |
| `downloadClicks` | `number` | Clicks on download links in the ad. |
| `end_date` | `string` | End date of the ad analytics data. |
| `externalWebsiteConversions` | `number` | Conversions that lead to external websites. |
| `externalWebsitePostClickConversions` | `number` | Post-click conversions on external websites. |
| `externalWebsitePostViewConversions` | `number` | Post-view conversions on external websites. |
| `follows` | `number` | Number of follows generated by the ad. |
| `fullScreenPlays` | `number` | Number of times videos were played in fullscreen mode. |
| `impressions` | `number` | Total number of times the ad was displayed. |
| `jobApplications` | `number` | Number of job applications initiated through the ad. |
| `jobApplyClicks` | `number` | Clicks on apply job button in the ad. |
| `landingPageClicks` | `number` | Clicks on the landing page associated with the ad. |
| `leadGenerationMailContactInfoShares` | `number` | Shares of contact information through lead generation. |
| `leadGenerationMailInterestedClicks` | `number` | Clicks on expressing interest through lead generation mail. |
| `likes` | `number` | Total likes received on the ad. |
| `oneClickLeadFormOpens` | `number` | Number of times lead forms were opened in one click. |
| `oneClickLeads` | `number` | Leads generated in one click. |
| `opens` | `number` | The number of times the ad was opened or expanded. |
| `otherEngagements` | `number` | Engagements other than clicks on the ad. |
| `pivotValues` | `array` | Values used for pivoting the analytics. |
| `string_of_pivot_values` | `string` | Comma-separated string of pivot values for this analytics record |
| `postClickJobApplications` | `number` | Job applications initiated post-clicking on the ad. |
| `postClickJobApplyClicks` | `number` | Clicks on apply job button post-clicking on the ad. |
| `postClickRegistrations` | `number` | Registrations completed post-clicking on the ad. |
| `postViewJobApplications` | `number` | Job applications initiated post-viewing the ad. |
| `postViewJobApplyClicks` | `number` | Clicks on apply job button post-viewing the ad. |
| `postViewRegistrations` | `number` | Registrations completed post-viewing the ad. |
| `reactions` | `number` | Total reactions (e.g., like, love, celebrate) on the ad. |
| `registrations` | `number` | Total registrations completed through the ad. |
| `sends` | `number` | Number of messages sent through the ad. |
| `shares` | `number` | Total shares generated by the ad. |
| `start_date` | `string` | Start date of the ad analytics data. |
| `talentLeads` | `number` | Number of leads related to talent acquisition. |
| `textUrlClicks` | `number` | Clicks on text URLs within the ad. |
| `totalEngagements` | `number` | Total number of engagements on the ad. |
| `validWorkEmailLeads` | `number` | Leads generated through valid work emails. |
| `videoCompletions` | `number` | Number of times videos were watched till completion. |
| `videoFirstQuartileCompletions` | `number` | Completions for first quartile of video views. |
| `videoMidpointCompletions` | `number` | Completions for midpoint of video views. |
| `videoStarts` | `number` | Total video starts initiated by users. |
| `videoThirdQuartileCompletions` | `number` | Completions for third quartile of video views. |
| `videoViews` | `number` | Total views of videos in the ad. |
| `viralCardClicks` | `number` | Clicks on interactive card components in viral distribution. |
| `viralCardImpressions` | `number` | Impressions of interactive cards in viral distribution. |
| `viralClicks` | `number` | Total clicks in viral distribution of the ad. |
| `viralCommentLikes` | `number` | Likes received on comments in viral distribution. |
| `viralComments` | `number` | Number of comments in viral distribution of the ad. |
| `viralCompanyPageClicks` | `number` | Clicks on the company page in viral distribution. |
| `viralDocumentCompletions` | `number` | Complete views of documents in viral distribution. |
| `viralDocumentFirstQuartileCompletions` | `number` | First quartile completions of documents in viral distribution. |
| `viralDocumentMidpointCompletions` | `number` | Midpoint completions of documents in viral distribution. |
| `viralDocumentThirdQuartileCompletions` | `number` | Third quartile completions of documents in viral distribution. |
| `viralDownloadClicks` | `number` | Clicks on downloads in viral distribution of the ad. |
| `viralExternalWebsiteConversions` | `number` | External website conversions in viral distribution. |
| `viralExternalWebsitePostClickConversions` | `number` | Post-click conversions on external websites in viral distribution. |
| `viralExternalWebsitePostViewConversions` | `number` | Post-view conversions on external websites in viral distribution. |
| `viralFollows` | `number` | Follows generated in viral distribution of the ad. |
| `viralFullScreenPlays` | `number` | Fullscreen video plays in viral distribution. |
| `viralImpressions` | `number` | Total impressions in viral distribution of the ad. |
| `viralJobApplications` | `number` | Job applications initiated in viral distribution. |
| `viralJobApplyClicks` | `number` | Clicks on apply job button in viral distribution of the ad. |
| `viralLandingPageClicks` | `number` | Clicks on landing page in viral distribution. |
| `viralLikes` | `number` | Total likes in viral distribution of the ad. |
| `viralOneClickLeadFormOpens` | `number` | One-click lead form opens in viral distribution. |
| `viralOneClickLeads` | `number` | Leads generated in one click in viral distribution. |
| `viralOtherEngagements` | `number` | Other engagements in viral distribution of the ad. |
| `viralPostClickJobApplications` | `number` | Job applications initiated post-clicking in viral distribution. |
| `viralPostClickJobApplyClicks` | `number` | Clicks on apply job button post-clicking in viral distribution. |
| `viralPostClickRegistrations` | `number` | Registrations completed post-clicking in viral distribution. |
| `viralPostViewJobApplications` | `number` | Job applications initiated post-viewing in viral distribution. |
| `viralPostViewJobApplyClicks` | `number` | Clicks on apply job button post-viewing in viral distribution. |
| `viralPostViewRegistrations` | `number` | Registrations completed post-viewing in viral distribution. |
| `viralReactions` | `number` | Total reactions in viral distribution of the ad. |
| `viralRegistrations` | `number` | Total registrations in viral distribution of the ad. |
| `viralShares` | `number` | Total shares in viral distribution of the ad. |
| `viralTotalEngagements` | `number` | Total engagements in viral distribution of the ad. |
| `viralVideoCompletions` | `number` | Completions of videos in viral distribution. |
| `viralVideoFirstQuartileCompletions` | `number` | First quartile completions of videos in viral distribution. |
| `viralVideoMidpointCompletions` | `number` | Midpoint completions of videos in viral distribution. |
| `viralVideoStarts` | `number` | Total video starts in viral distribution of the ad. |
| `viralVideoThirdQuartileCompletions` | `number` | Third quartile completions of videos in viral distribution. |
| `viralVideoViews` | `number` | Total views of videos in viral distribution of the ad. |
| `pivot` | `string` | Pivot dimension used for this analytics record |
| `sponsoredCampaign` | `string` | URN of the sponsored campaign this analytics record belongs to |

<details>
<summary><b>Response Schema</b></summary>

| Field Name | Type | Description |
|------------|------|-------------|
| `data` | `array` | List of matching records |
| `meta` | `object` | Pagination metadata |
| `meta.has_more` | `boolean` | Whether additional pages are available |
| `meta.cursor` | `string \| null` | Cursor for next page of results |
| `meta.took_ms` | `number \| null` | Query execution time in milliseconds |
| `data[].actionClicks` | `number` | The number of clicks on action buttons in the ad. |
| `data[].adUnitClicks` | `number` | The number of clicks on ad unit components. |
| `data[].approximateMemberReach` | `number` | An approximation of unique ad impressions. |
| `data[].cardClicks` | `number` | The number of clicks on interactive card elements. |
| `data[].cardImpressions` | `number` | The number of times interactive cards were displayed. |
| `data[].clicks` | `number` | Total number of clicks on the ad. |
| `data[].commentLikes` | `number` | The count of likes on comments related to the ad. |
| `data[].comments` | `number` | The number of comments on the ad. |
| `data[].companyPageClicks` | `number` | Clicks on the company page associated with the ad. |
| `data[].conversionValueInLocalCurrency` | `number` | Conversion value in the local currency. |
| `data[].costInLocalCurrency` | `number` | Cost of ad campaign in the local currency. |
| `data[].costInUsd` | `number` | Cost of ad campaign in USD. |
| `data[].documentCompletions` | `number` | Number of completions for document views. |
| `data[].documentFirstQuartileCompletions` | `number` | Completions for first quartile of document views. |
| `data[].documentMidpointCompletions` | `number` | Completions for midpoint of document views. |
| `data[].documentThirdQuartileCompletions` | `number` | Completions for third quartile of document views. |
| `data[].downloadClicks` | `number` | Clicks on download links in the ad. |
| `data[].end_date` | `string` | End date of the ad analytics data. |
| `data[].externalWebsiteConversions` | `number` | Conversions that lead to external websites. |
| `data[].externalWebsitePostClickConversions` | `number` | Post-click conversions on external websites. |
| `data[].externalWebsitePostViewConversions` | `number` | Post-view conversions on external websites. |
| `data[].follows` | `number` | Number of follows generated by the ad. |
| `data[].fullScreenPlays` | `number` | Number of times videos were played in fullscreen mode. |
| `data[].impressions` | `number` | Total number of times the ad was displayed. |
| `data[].jobApplications` | `number` | Number of job applications initiated through the ad. |
| `data[].jobApplyClicks` | `number` | Clicks on apply job button in the ad. |
| `data[].landingPageClicks` | `number` | Clicks on the landing page associated with the ad. |
| `data[].leadGenerationMailContactInfoShares` | `number` | Shares of contact information through lead generation. |
| `data[].leadGenerationMailInterestedClicks` | `number` | Clicks on expressing interest through lead generation mail. |
| `data[].likes` | `number` | Total likes received on the ad. |
| `data[].oneClickLeadFormOpens` | `number` | Number of times lead forms were opened in one click. |
| `data[].oneClickLeads` | `number` | Leads generated in one click. |
| `data[].opens` | `number` | The number of times the ad was opened or expanded. |
| `data[].otherEngagements` | `number` | Engagements other than clicks on the ad. |
| `data[].pivotValues` | `array` | Values used for pivoting the analytics. |
| `data[].string_of_pivot_values` | `string` | Comma-separated string of pivot values for this analytics record |
| `data[].postClickJobApplications` | `number` | Job applications initiated post-clicking on the ad. |
| `data[].postClickJobApplyClicks` | `number` | Clicks on apply job button post-clicking on the ad. |
| `data[].postClickRegistrations` | `number` | Registrations completed post-clicking on the ad. |
| `data[].postViewJobApplications` | `number` | Job applications initiated post-viewing the ad. |
| `data[].postViewJobApplyClicks` | `number` | Clicks on apply job button post-viewing the ad. |
| `data[].postViewRegistrations` | `number` | Registrations completed post-viewing the ad. |
| `data[].reactions` | `number` | Total reactions (e.g., like, love, celebrate) on the ad. |
| `data[].registrations` | `number` | Total registrations completed through the ad. |
| `data[].sends` | `number` | Number of messages sent through the ad. |
| `data[].shares` | `number` | Total shares generated by the ad. |
| `data[].start_date` | `string` | Start date of the ad analytics data. |
| `data[].talentLeads` | `number` | Number of leads related to talent acquisition. |
| `data[].textUrlClicks` | `number` | Clicks on text URLs within the ad. |
| `data[].totalEngagements` | `number` | Total number of engagements on the ad. |
| `data[].validWorkEmailLeads` | `number` | Leads generated through valid work emails. |
| `data[].videoCompletions` | `number` | Number of times videos were watched till completion. |
| `data[].videoFirstQuartileCompletions` | `number` | Completions for first quartile of video views. |
| `data[].videoMidpointCompletions` | `number` | Completions for midpoint of video views. |
| `data[].videoStarts` | `number` | Total video starts initiated by users. |
| `data[].videoThirdQuartileCompletions` | `number` | Completions for third quartile of video views. |
| `data[].videoViews` | `number` | Total views of videos in the ad. |
| `data[].viralCardClicks` | `number` | Clicks on interactive card components in viral distribution. |
| `data[].viralCardImpressions` | `number` | Impressions of interactive cards in viral distribution. |
| `data[].viralClicks` | `number` | Total clicks in viral distribution of the ad. |
| `data[].viralCommentLikes` | `number` | Likes received on comments in viral distribution. |
| `data[].viralComments` | `number` | Number of comments in viral distribution of the ad. |
| `data[].viralCompanyPageClicks` | `number` | Clicks on the company page in viral distribution. |
| `data[].viralDocumentCompletions` | `number` | Complete views of documents in viral distribution. |
| `data[].viralDocumentFirstQuartileCompletions` | `number` | First quartile completions of documents in viral distribution. |
| `data[].viralDocumentMidpointCompletions` | `number` | Midpoint completions of documents in viral distribution. |
| `data[].viralDocumentThirdQuartileCompletions` | `number` | Third quartile completions of documents in viral distribution. |
| `data[].viralDownloadClicks` | `number` | Clicks on downloads in viral distribution of the ad. |
| `data[].viralExternalWebsiteConversions` | `number` | External website conversions in viral distribution. |
| `data[].viralExternalWebsitePostClickConversions` | `number` | Post-click conversions on external websites in viral distribution. |
| `data[].viralExternalWebsitePostViewConversions` | `number` | Post-view conversions on external websites in viral distribution. |
| `data[].viralFollows` | `number` | Follows generated in viral distribution of the ad. |
| `data[].viralFullScreenPlays` | `number` | Fullscreen video plays in viral distribution. |
| `data[].viralImpressions` | `number` | Total impressions in viral distribution of the ad. |
| `data[].viralJobApplications` | `number` | Job applications initiated in viral distribution. |
| `data[].viralJobApplyClicks` | `number` | Clicks on apply job button in viral distribution of the ad. |
| `data[].viralLandingPageClicks` | `number` | Clicks on landing page in viral distribution. |
| `data[].viralLikes` | `number` | Total likes in viral distribution of the ad. |
| `data[].viralOneClickLeadFormOpens` | `number` | One-click lead form opens in viral distribution. |
| `data[].viralOneClickLeads` | `number` | Leads generated in one click in viral distribution. |
| `data[].viralOtherEngagements` | `number` | Other engagements in viral distribution of the ad. |
| `data[].viralPostClickJobApplications` | `number` | Job applications initiated post-clicking in viral distribution. |
| `data[].viralPostClickJobApplyClicks` | `number` | Clicks on apply job button post-clicking in viral distribution. |
| `data[].viralPostClickRegistrations` | `number` | Registrations completed post-clicking in viral distribution. |
| `data[].viralPostViewJobApplications` | `number` | Job applications initiated post-viewing in viral distribution. |
| `data[].viralPostViewJobApplyClicks` | `number` | Clicks on apply job button post-viewing in viral distribution. |
| `data[].viralPostViewRegistrations` | `number` | Registrations completed post-viewing in viral distribution. |
| `data[].viralReactions` | `number` | Total reactions in viral distribution of the ad. |
| `data[].viralRegistrations` | `number` | Total registrations in viral distribution of the ad. |
| `data[].viralShares` | `number` | Total shares in viral distribution of the ad. |
| `data[].viralTotalEngagements` | `number` | Total engagements in viral distribution of the ad. |
| `data[].viralVideoCompletions` | `number` | Completions of videos in viral distribution. |
| `data[].viralVideoFirstQuartileCompletions` | `number` | First quartile completions of videos in viral distribution. |
| `data[].viralVideoMidpointCompletions` | `number` | Midpoint completions of videos in viral distribution. |
| `data[].viralVideoStarts` | `number` | Total video starts in viral distribution of the ad. |
| `data[].viralVideoThirdQuartileCompletions` | `number` | Third quartile completions of videos in viral distribution. |
| `data[].viralVideoViews` | `number` | Total views of videos in viral distribution of the ad. |
| `data[].pivot` | `string` | Pivot dimension used for this analytics record |
| `data[].sponsoredCampaign` | `string` | URN of the sponsored campaign this analytics record belongs to |

</details>

## Ad Member Country Analytics

### Ad Member Country Analytics List

Returns ad analytics data pivoted by member country. Provides performance metrics including clicks, impressions, spend, and engagement data grouped by member country.


#### CLI

```bash
airbyte-agent connectors execute --json '{
  "workspace": "<your_workspace_name>",
  "name": "linkedin-ads",
  "entity": "ad_member_country_analytics",
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

#### Python SDK

```python
await linkedin_ads.ad_member_country_analytics.list(
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
    "entity": "ad_member_country_analytics",
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
| `q` | `string` | Yes | LinkedIn API finder method for querying ad analytics |
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

### Ad Member Country Analytics Context Store Search

Search and filter ad member country analytics records powered by Airbyte's data sync. This often provides additional fields and operators beyond what the API natively supports, making it easier to narrow down results before performing further operations. Only available in hosted mode.

#### CLI

```bash
airbyte-agent connectors execute --json '{
  "workspace": "<your_workspace_name>",
  "name": "linkedin-ads",
  "entity": "ad_member_country_analytics",
  "action": "context_store_search",
  "params": {
    "query": {
      "filter": {
        "eq": {
          "actionClicks": 0.0
        }
      }
    }
  }
}'
```

#### Python SDK

```python
await linkedin_ads.ad_member_country_analytics.context_store_search(
    query={"filter": {"eq": {"actionClicks": 0.0}}}
)
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/integrations/connectors/{your_connector_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "ad_member_country_analytics",
    "action": "context_store_search",
    "params": {
        "query": {"filter": {"eq": {"actionClicks": 0.0}}}
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
| `actionClicks` | `number` | The number of clicks on action buttons in the ad. |
| `adUnitClicks` | `number` | The number of clicks on ad unit components. |
| `approximateMemberReach` | `number` | An approximation of unique ad impressions. |
| `cardClicks` | `number` | The number of clicks on interactive card elements. |
| `cardImpressions` | `number` | The number of times interactive cards were displayed. |
| `clicks` | `number` | Total number of clicks on the ad. |
| `commentLikes` | `number` | The count of likes on comments related to the ad. |
| `comments` | `number` | The number of comments on the ad. |
| `companyPageClicks` | `number` | Clicks on the company page associated with the ad. |
| `conversionValueInLocalCurrency` | `number` | Conversion value in the local currency. |
| `costInLocalCurrency` | `number` | Cost of ad campaign in the local currency. |
| `costInUsd` | `number` | Cost of ad campaign in USD. |
| `documentCompletions` | `number` | Number of completions for document views. |
| `documentFirstQuartileCompletions` | `number` | Completions for first quartile of document views. |
| `documentMidpointCompletions` | `number` | Completions for midpoint of document views. |
| `documentThirdQuartileCompletions` | `number` | Completions for third quartile of document views. |
| `downloadClicks` | `number` | Clicks on download links in the ad. |
| `end_date` | `string` | End date of the ad analytics data. |
| `externalWebsiteConversions` | `number` | Conversions that lead to external websites. |
| `externalWebsitePostClickConversions` | `number` | Post-click conversions on external websites. |
| `externalWebsitePostViewConversions` | `number` | Post-view conversions on external websites. |
| `follows` | `number` | Number of follows generated by the ad. |
| `fullScreenPlays` | `number` | Number of times videos were played in fullscreen mode. |
| `impressions` | `number` | Total number of times the ad was displayed. |
| `jobApplications` | `number` | Number of job applications initiated through the ad. |
| `jobApplyClicks` | `number` | Clicks on apply job button in the ad. |
| `landingPageClicks` | `number` | Clicks on the landing page associated with the ad. |
| `leadGenerationMailContactInfoShares` | `number` | Shares of contact information through lead generation. |
| `leadGenerationMailInterestedClicks` | `number` | Clicks on expressing interest through lead generation mail. |
| `likes` | `number` | Total likes received on the ad. |
| `oneClickLeadFormOpens` | `number` | Number of times lead forms were opened in one click. |
| `oneClickLeads` | `number` | Leads generated in one click. |
| `opens` | `number` | The number of times the ad was opened or expanded. |
| `otherEngagements` | `number` | Engagements other than clicks on the ad. |
| `pivotValues` | `array` | Values used for pivoting the analytics. |
| `string_of_pivot_values` | `string` | Comma-separated string of pivot values for this analytics record |
| `postClickJobApplications` | `number` | Job applications initiated post-clicking on the ad. |
| `postClickJobApplyClicks` | `number` | Clicks on apply job button post-clicking on the ad. |
| `postClickRegistrations` | `number` | Registrations completed post-clicking on the ad. |
| `postViewJobApplications` | `number` | Job applications initiated post-viewing the ad. |
| `postViewJobApplyClicks` | `number` | Clicks on apply job button post-viewing the ad. |
| `postViewRegistrations` | `number` | Registrations completed post-viewing the ad. |
| `reactions` | `number` | Total reactions (e.g., like, love, celebrate) on the ad. |
| `registrations` | `number` | Total registrations completed through the ad. |
| `sends` | `number` | Number of messages sent through the ad. |
| `shares` | `number` | Total shares generated by the ad. |
| `start_date` | `string` | Start date of the ad analytics data. |
| `talentLeads` | `number` | Number of leads related to talent acquisition. |
| `textUrlClicks` | `number` | Clicks on text URLs within the ad. |
| `totalEngagements` | `number` | Total number of engagements on the ad. |
| `validWorkEmailLeads` | `number` | Leads generated through valid work emails. |
| `videoCompletions` | `number` | Number of times videos were watched till completion. |
| `videoFirstQuartileCompletions` | `number` | Completions for first quartile of video views. |
| `videoMidpointCompletions` | `number` | Completions for midpoint of video views. |
| `videoStarts` | `number` | Total video starts initiated by users. |
| `videoThirdQuartileCompletions` | `number` | Completions for third quartile of video views. |
| `videoViews` | `number` | Total views of videos in the ad. |
| `viralCardClicks` | `number` | Clicks on interactive card components in viral distribution. |
| `viralCardImpressions` | `number` | Impressions of interactive cards in viral distribution. |
| `viralClicks` | `number` | Total clicks in viral distribution of the ad. |
| `viralCommentLikes` | `number` | Likes received on comments in viral distribution. |
| `viralComments` | `number` | Number of comments in viral distribution of the ad. |
| `viralCompanyPageClicks` | `number` | Clicks on the company page in viral distribution. |
| `viralDocumentCompletions` | `number` | Complete views of documents in viral distribution. |
| `viralDocumentFirstQuartileCompletions` | `number` | First quartile completions of documents in viral distribution. |
| `viralDocumentMidpointCompletions` | `number` | Midpoint completions of documents in viral distribution. |
| `viralDocumentThirdQuartileCompletions` | `number` | Third quartile completions of documents in viral distribution. |
| `viralDownloadClicks` | `number` | Clicks on downloads in viral distribution of the ad. |
| `viralExternalWebsiteConversions` | `number` | External website conversions in viral distribution. |
| `viralExternalWebsitePostClickConversions` | `number` | Post-click conversions on external websites in viral distribution. |
| `viralExternalWebsitePostViewConversions` | `number` | Post-view conversions on external websites in viral distribution. |
| `viralFollows` | `number` | Follows generated in viral distribution of the ad. |
| `viralFullScreenPlays` | `number` | Fullscreen video plays in viral distribution. |
| `viralImpressions` | `number` | Total impressions in viral distribution of the ad. |
| `viralJobApplications` | `number` | Job applications initiated in viral distribution. |
| `viralJobApplyClicks` | `number` | Clicks on apply job button in viral distribution of the ad. |
| `viralLandingPageClicks` | `number` | Clicks on landing page in viral distribution. |
| `viralLikes` | `number` | Total likes in viral distribution of the ad. |
| `viralOneClickLeadFormOpens` | `number` | One-click lead form opens in viral distribution. |
| `viralOneClickLeads` | `number` | Leads generated in one click in viral distribution. |
| `viralOtherEngagements` | `number` | Other engagements in viral distribution of the ad. |
| `viralPostClickJobApplications` | `number` | Job applications initiated post-clicking in viral distribution. |
| `viralPostClickJobApplyClicks` | `number` | Clicks on apply job button post-clicking in viral distribution. |
| `viralPostClickRegistrations` | `number` | Registrations completed post-clicking in viral distribution. |
| `viralPostViewJobApplications` | `number` | Job applications initiated post-viewing in viral distribution. |
| `viralPostViewJobApplyClicks` | `number` | Clicks on apply job button post-viewing in viral distribution. |
| `viralPostViewRegistrations` | `number` | Registrations completed post-viewing in viral distribution. |
| `viralReactions` | `number` | Total reactions in viral distribution of the ad. |
| `viralRegistrations` | `number` | Total registrations in viral distribution of the ad. |
| `viralShares` | `number` | Total shares in viral distribution of the ad. |
| `viralTotalEngagements` | `number` | Total engagements in viral distribution of the ad. |
| `viralVideoCompletions` | `number` | Completions of videos in viral distribution. |
| `viralVideoFirstQuartileCompletions` | `number` | First quartile completions of videos in viral distribution. |
| `viralVideoMidpointCompletions` | `number` | Midpoint completions of videos in viral distribution. |
| `viralVideoStarts` | `number` | Total video starts in viral distribution of the ad. |
| `viralVideoThirdQuartileCompletions` | `number` | Third quartile completions of videos in viral distribution. |
| `viralVideoViews` | `number` | Total views of videos in viral distribution of the ad. |
| `pivot` | `string` | Pivot dimension used for this analytics record |
| `sponsoredCampaign` | `string` | URN of the sponsored campaign this analytics record belongs to |

<details>
<summary><b>Response Schema</b></summary>

| Field Name | Type | Description |
|------------|------|-------------|
| `data` | `array` | List of matching records |
| `meta` | `object` | Pagination metadata |
| `meta.has_more` | `boolean` | Whether additional pages are available |
| `meta.cursor` | `string \| null` | Cursor for next page of results |
| `meta.took_ms` | `number \| null` | Query execution time in milliseconds |
| `data[].actionClicks` | `number` | The number of clicks on action buttons in the ad. |
| `data[].adUnitClicks` | `number` | The number of clicks on ad unit components. |
| `data[].approximateMemberReach` | `number` | An approximation of unique ad impressions. |
| `data[].cardClicks` | `number` | The number of clicks on interactive card elements. |
| `data[].cardImpressions` | `number` | The number of times interactive cards were displayed. |
| `data[].clicks` | `number` | Total number of clicks on the ad. |
| `data[].commentLikes` | `number` | The count of likes on comments related to the ad. |
| `data[].comments` | `number` | The number of comments on the ad. |
| `data[].companyPageClicks` | `number` | Clicks on the company page associated with the ad. |
| `data[].conversionValueInLocalCurrency` | `number` | Conversion value in the local currency. |
| `data[].costInLocalCurrency` | `number` | Cost of ad campaign in the local currency. |
| `data[].costInUsd` | `number` | Cost of ad campaign in USD. |
| `data[].documentCompletions` | `number` | Number of completions for document views. |
| `data[].documentFirstQuartileCompletions` | `number` | Completions for first quartile of document views. |
| `data[].documentMidpointCompletions` | `number` | Completions for midpoint of document views. |
| `data[].documentThirdQuartileCompletions` | `number` | Completions for third quartile of document views. |
| `data[].downloadClicks` | `number` | Clicks on download links in the ad. |
| `data[].end_date` | `string` | End date of the ad analytics data. |
| `data[].externalWebsiteConversions` | `number` | Conversions that lead to external websites. |
| `data[].externalWebsitePostClickConversions` | `number` | Post-click conversions on external websites. |
| `data[].externalWebsitePostViewConversions` | `number` | Post-view conversions on external websites. |
| `data[].follows` | `number` | Number of follows generated by the ad. |
| `data[].fullScreenPlays` | `number` | Number of times videos were played in fullscreen mode. |
| `data[].impressions` | `number` | Total number of times the ad was displayed. |
| `data[].jobApplications` | `number` | Number of job applications initiated through the ad. |
| `data[].jobApplyClicks` | `number` | Clicks on apply job button in the ad. |
| `data[].landingPageClicks` | `number` | Clicks on the landing page associated with the ad. |
| `data[].leadGenerationMailContactInfoShares` | `number` | Shares of contact information through lead generation. |
| `data[].leadGenerationMailInterestedClicks` | `number` | Clicks on expressing interest through lead generation mail. |
| `data[].likes` | `number` | Total likes received on the ad. |
| `data[].oneClickLeadFormOpens` | `number` | Number of times lead forms were opened in one click. |
| `data[].oneClickLeads` | `number` | Leads generated in one click. |
| `data[].opens` | `number` | The number of times the ad was opened or expanded. |
| `data[].otherEngagements` | `number` | Engagements other than clicks on the ad. |
| `data[].pivotValues` | `array` | Values used for pivoting the analytics. |
| `data[].string_of_pivot_values` | `string` | Comma-separated string of pivot values for this analytics record |
| `data[].postClickJobApplications` | `number` | Job applications initiated post-clicking on the ad. |
| `data[].postClickJobApplyClicks` | `number` | Clicks on apply job button post-clicking on the ad. |
| `data[].postClickRegistrations` | `number` | Registrations completed post-clicking on the ad. |
| `data[].postViewJobApplications` | `number` | Job applications initiated post-viewing the ad. |
| `data[].postViewJobApplyClicks` | `number` | Clicks on apply job button post-viewing the ad. |
| `data[].postViewRegistrations` | `number` | Registrations completed post-viewing the ad. |
| `data[].reactions` | `number` | Total reactions (e.g., like, love, celebrate) on the ad. |
| `data[].registrations` | `number` | Total registrations completed through the ad. |
| `data[].sends` | `number` | Number of messages sent through the ad. |
| `data[].shares` | `number` | Total shares generated by the ad. |
| `data[].start_date` | `string` | Start date of the ad analytics data. |
| `data[].talentLeads` | `number` | Number of leads related to talent acquisition. |
| `data[].textUrlClicks` | `number` | Clicks on text URLs within the ad. |
| `data[].totalEngagements` | `number` | Total number of engagements on the ad. |
| `data[].validWorkEmailLeads` | `number` | Leads generated through valid work emails. |
| `data[].videoCompletions` | `number` | Number of times videos were watched till completion. |
| `data[].videoFirstQuartileCompletions` | `number` | Completions for first quartile of video views. |
| `data[].videoMidpointCompletions` | `number` | Completions for midpoint of video views. |
| `data[].videoStarts` | `number` | Total video starts initiated by users. |
| `data[].videoThirdQuartileCompletions` | `number` | Completions for third quartile of video views. |
| `data[].videoViews` | `number` | Total views of videos in the ad. |
| `data[].viralCardClicks` | `number` | Clicks on interactive card components in viral distribution. |
| `data[].viralCardImpressions` | `number` | Impressions of interactive cards in viral distribution. |
| `data[].viralClicks` | `number` | Total clicks in viral distribution of the ad. |
| `data[].viralCommentLikes` | `number` | Likes received on comments in viral distribution. |
| `data[].viralComments` | `number` | Number of comments in viral distribution of the ad. |
| `data[].viralCompanyPageClicks` | `number` | Clicks on the company page in viral distribution. |
| `data[].viralDocumentCompletions` | `number` | Complete views of documents in viral distribution. |
| `data[].viralDocumentFirstQuartileCompletions` | `number` | First quartile completions of documents in viral distribution. |
| `data[].viralDocumentMidpointCompletions` | `number` | Midpoint completions of documents in viral distribution. |
| `data[].viralDocumentThirdQuartileCompletions` | `number` | Third quartile completions of documents in viral distribution. |
| `data[].viralDownloadClicks` | `number` | Clicks on downloads in viral distribution of the ad. |
| `data[].viralExternalWebsiteConversions` | `number` | External website conversions in viral distribution. |
| `data[].viralExternalWebsitePostClickConversions` | `number` | Post-click conversions on external websites in viral distribution. |
| `data[].viralExternalWebsitePostViewConversions` | `number` | Post-view conversions on external websites in viral distribution. |
| `data[].viralFollows` | `number` | Follows generated in viral distribution of the ad. |
| `data[].viralFullScreenPlays` | `number` | Fullscreen video plays in viral distribution. |
| `data[].viralImpressions` | `number` | Total impressions in viral distribution of the ad. |
| `data[].viralJobApplications` | `number` | Job applications initiated in viral distribution. |
| `data[].viralJobApplyClicks` | `number` | Clicks on apply job button in viral distribution of the ad. |
| `data[].viralLandingPageClicks` | `number` | Clicks on landing page in viral distribution. |
| `data[].viralLikes` | `number` | Total likes in viral distribution of the ad. |
| `data[].viralOneClickLeadFormOpens` | `number` | One-click lead form opens in viral distribution. |
| `data[].viralOneClickLeads` | `number` | Leads generated in one click in viral distribution. |
| `data[].viralOtherEngagements` | `number` | Other engagements in viral distribution of the ad. |
| `data[].viralPostClickJobApplications` | `number` | Job applications initiated post-clicking in viral distribution. |
| `data[].viralPostClickJobApplyClicks` | `number` | Clicks on apply job button post-clicking in viral distribution. |
| `data[].viralPostClickRegistrations` | `number` | Registrations completed post-clicking in viral distribution. |
| `data[].viralPostViewJobApplications` | `number` | Job applications initiated post-viewing in viral distribution. |
| `data[].viralPostViewJobApplyClicks` | `number` | Clicks on apply job button post-viewing in viral distribution. |
| `data[].viralPostViewRegistrations` | `number` | Registrations completed post-viewing in viral distribution. |
| `data[].viralReactions` | `number` | Total reactions in viral distribution of the ad. |
| `data[].viralRegistrations` | `number` | Total registrations in viral distribution of the ad. |
| `data[].viralShares` | `number` | Total shares in viral distribution of the ad. |
| `data[].viralTotalEngagements` | `number` | Total engagements in viral distribution of the ad. |
| `data[].viralVideoCompletions` | `number` | Completions of videos in viral distribution. |
| `data[].viralVideoFirstQuartileCompletions` | `number` | First quartile completions of videos in viral distribution. |
| `data[].viralVideoMidpointCompletions` | `number` | Midpoint completions of videos in viral distribution. |
| `data[].viralVideoStarts` | `number` | Total video starts in viral distribution of the ad. |
| `data[].viralVideoThirdQuartileCompletions` | `number` | Third quartile completions of videos in viral distribution. |
| `data[].viralVideoViews` | `number` | Total views of videos in viral distribution of the ad. |
| `data[].pivot` | `string` | Pivot dimension used for this analytics record |
| `data[].sponsoredCampaign` | `string` | URN of the sponsored campaign this analytics record belongs to |

</details>

## Ad Member Industry Analytics

### Ad Member Industry Analytics List

Returns ad analytics data pivoted by member industry. Provides performance metrics including clicks, impressions, spend, and engagement data grouped by member industry.


#### CLI

```bash
airbyte-agent connectors execute --json '{
  "workspace": "<your_workspace_name>",
  "name": "linkedin-ads",
  "entity": "ad_member_industry_analytics",
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

#### Python SDK

```python
await linkedin_ads.ad_member_industry_analytics.list(
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
    "entity": "ad_member_industry_analytics",
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
| `q` | `string` | Yes | LinkedIn API finder method for querying ad analytics |
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

### Ad Member Industry Analytics Context Store Search

Search and filter ad member industry analytics records powered by Airbyte's data sync. This often provides additional fields and operators beyond what the API natively supports, making it easier to narrow down results before performing further operations. Only available in hosted mode.

#### CLI

```bash
airbyte-agent connectors execute --json '{
  "workspace": "<your_workspace_name>",
  "name": "linkedin-ads",
  "entity": "ad_member_industry_analytics",
  "action": "context_store_search",
  "params": {
    "query": {
      "filter": {
        "eq": {
          "actionClicks": 0.0
        }
      }
    }
  }
}'
```

#### Python SDK

```python
await linkedin_ads.ad_member_industry_analytics.context_store_search(
    query={"filter": {"eq": {"actionClicks": 0.0}}}
)
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/integrations/connectors/{your_connector_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "ad_member_industry_analytics",
    "action": "context_store_search",
    "params": {
        "query": {"filter": {"eq": {"actionClicks": 0.0}}}
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
| `actionClicks` | `number` | The number of clicks on action buttons in the ad. |
| `adUnitClicks` | `number` | The number of clicks on ad unit components. |
| `approximateMemberReach` | `number` | An approximation of unique ad impressions. |
| `cardClicks` | `number` | The number of clicks on interactive card elements. |
| `cardImpressions` | `number` | The number of times interactive cards were displayed. |
| `clicks` | `number` | Total number of clicks on the ad. |
| `commentLikes` | `number` | The count of likes on comments related to the ad. |
| `comments` | `number` | The number of comments on the ad. |
| `companyPageClicks` | `number` | Clicks on the company page associated with the ad. |
| `conversionValueInLocalCurrency` | `number` | Conversion value in the local currency. |
| `costInLocalCurrency` | `number` | Cost of ad campaign in the local currency. |
| `costInUsd` | `number` | Cost of ad campaign in USD. |
| `documentCompletions` | `number` | Number of completions for document views. |
| `documentFirstQuartileCompletions` | `number` | Completions for first quartile of document views. |
| `documentMidpointCompletions` | `number` | Completions for midpoint of document views. |
| `documentThirdQuartileCompletions` | `number` | Completions for third quartile of document views. |
| `downloadClicks` | `number` | Clicks on download links in the ad. |
| `end_date` | `string` | End date of the ad analytics data. |
| `externalWebsiteConversions` | `number` | Conversions that lead to external websites. |
| `externalWebsitePostClickConversions` | `number` | Post-click conversions on external websites. |
| `externalWebsitePostViewConversions` | `number` | Post-view conversions on external websites. |
| `follows` | `number` | Number of follows generated by the ad. |
| `fullScreenPlays` | `number` | Number of times videos were played in fullscreen mode. |
| `impressions` | `number` | Total number of times the ad was displayed. |
| `jobApplications` | `number` | Number of job applications initiated through the ad. |
| `jobApplyClicks` | `number` | Clicks on apply job button in the ad. |
| `landingPageClicks` | `number` | Clicks on the landing page associated with the ad. |
| `leadGenerationMailContactInfoShares` | `number` | Shares of contact information through lead generation. |
| `leadGenerationMailInterestedClicks` | `number` | Clicks on expressing interest through lead generation mail. |
| `likes` | `number` | Total likes received on the ad. |
| `oneClickLeadFormOpens` | `number` | Number of times lead forms were opened in one click. |
| `oneClickLeads` | `number` | Leads generated in one click. |
| `opens` | `number` | The number of times the ad was opened or expanded. |
| `otherEngagements` | `number` | Engagements other than clicks on the ad. |
| `pivotValues` | `array` | Values used for pivoting the analytics. |
| `string_of_pivot_values` | `string` | Comma-separated string of pivot values for this analytics record |
| `postClickJobApplications` | `number` | Job applications initiated post-clicking on the ad. |
| `postClickJobApplyClicks` | `number` | Clicks on apply job button post-clicking on the ad. |
| `postClickRegistrations` | `number` | Registrations completed post-clicking on the ad. |
| `postViewJobApplications` | `number` | Job applications initiated post-viewing the ad. |
| `postViewJobApplyClicks` | `number` | Clicks on apply job button post-viewing the ad. |
| `postViewRegistrations` | `number` | Registrations completed post-viewing the ad. |
| `reactions` | `number` | Total reactions (e.g., like, love, celebrate) on the ad. |
| `registrations` | `number` | Total registrations completed through the ad. |
| `sends` | `number` | Number of messages sent through the ad. |
| `shares` | `number` | Total shares generated by the ad. |
| `start_date` | `string` | Start date of the ad analytics data. |
| `talentLeads` | `number` | Number of leads related to talent acquisition. |
| `textUrlClicks` | `number` | Clicks on text URLs within the ad. |
| `totalEngagements` | `number` | Total number of engagements on the ad. |
| `validWorkEmailLeads` | `number` | Leads generated through valid work emails. |
| `videoCompletions` | `number` | Number of times videos were watched till completion. |
| `videoFirstQuartileCompletions` | `number` | Completions for first quartile of video views. |
| `videoMidpointCompletions` | `number` | Completions for midpoint of video views. |
| `videoStarts` | `number` | Total video starts initiated by users. |
| `videoThirdQuartileCompletions` | `number` | Completions for third quartile of video views. |
| `videoViews` | `number` | Total views of videos in the ad. |
| `viralCardClicks` | `number` | Clicks on interactive card components in viral distribution. |
| `viralCardImpressions` | `number` | Impressions of interactive cards in viral distribution. |
| `viralClicks` | `number` | Total clicks in viral distribution of the ad. |
| `viralCommentLikes` | `number` | Likes received on comments in viral distribution. |
| `viralComments` | `number` | Number of comments in viral distribution of the ad. |
| `viralCompanyPageClicks` | `number` | Clicks on the company page in viral distribution. |
| `viralDocumentCompletions` | `number` | Complete views of documents in viral distribution. |
| `viralDocumentFirstQuartileCompletions` | `number` | First quartile completions of documents in viral distribution. |
| `viralDocumentMidpointCompletions` | `number` | Midpoint completions of documents in viral distribution. |
| `viralDocumentThirdQuartileCompletions` | `number` | Third quartile completions of documents in viral distribution. |
| `viralDownloadClicks` | `number` | Clicks on downloads in viral distribution of the ad. |
| `viralExternalWebsiteConversions` | `number` | External website conversions in viral distribution. |
| `viralExternalWebsitePostClickConversions` | `number` | Post-click conversions on external websites in viral distribution. |
| `viralExternalWebsitePostViewConversions` | `number` | Post-view conversions on external websites in viral distribution. |
| `viralFollows` | `number` | Follows generated in viral distribution of the ad. |
| `viralFullScreenPlays` | `number` | Fullscreen video plays in viral distribution. |
| `viralImpressions` | `number` | Total impressions in viral distribution of the ad. |
| `viralJobApplications` | `number` | Job applications initiated in viral distribution. |
| `viralJobApplyClicks` | `number` | Clicks on apply job button in viral distribution of the ad. |
| `viralLandingPageClicks` | `number` | Clicks on landing page in viral distribution. |
| `viralLikes` | `number` | Total likes in viral distribution of the ad. |
| `viralOneClickLeadFormOpens` | `number` | One-click lead form opens in viral distribution. |
| `viralOneClickLeads` | `number` | Leads generated in one click in viral distribution. |
| `viralOtherEngagements` | `number` | Other engagements in viral distribution of the ad. |
| `viralPostClickJobApplications` | `number` | Job applications initiated post-clicking in viral distribution. |
| `viralPostClickJobApplyClicks` | `number` | Clicks on apply job button post-clicking in viral distribution. |
| `viralPostClickRegistrations` | `number` | Registrations completed post-clicking in viral distribution. |
| `viralPostViewJobApplications` | `number` | Job applications initiated post-viewing in viral distribution. |
| `viralPostViewJobApplyClicks` | `number` | Clicks on apply job button post-viewing in viral distribution. |
| `viralPostViewRegistrations` | `number` | Registrations completed post-viewing in viral distribution. |
| `viralReactions` | `number` | Total reactions in viral distribution of the ad. |
| `viralRegistrations` | `number` | Total registrations in viral distribution of the ad. |
| `viralShares` | `number` | Total shares in viral distribution of the ad. |
| `viralTotalEngagements` | `number` | Total engagements in viral distribution of the ad. |
| `viralVideoCompletions` | `number` | Completions of videos in viral distribution. |
| `viralVideoFirstQuartileCompletions` | `number` | First quartile completions of videos in viral distribution. |
| `viralVideoMidpointCompletions` | `number` | Midpoint completions of videos in viral distribution. |
| `viralVideoStarts` | `number` | Total video starts in viral distribution of the ad. |
| `viralVideoThirdQuartileCompletions` | `number` | Third quartile completions of videos in viral distribution. |
| `viralVideoViews` | `number` | Total views of videos in viral distribution of the ad. |
| `pivot` | `string` | Pivot dimension used for this analytics record |
| `sponsoredCampaign` | `string` | URN of the sponsored campaign this analytics record belongs to |

<details>
<summary><b>Response Schema</b></summary>

| Field Name | Type | Description |
|------------|------|-------------|
| `data` | `array` | List of matching records |
| `meta` | `object` | Pagination metadata |
| `meta.has_more` | `boolean` | Whether additional pages are available |
| `meta.cursor` | `string \| null` | Cursor for next page of results |
| `meta.took_ms` | `number \| null` | Query execution time in milliseconds |
| `data[].actionClicks` | `number` | The number of clicks on action buttons in the ad. |
| `data[].adUnitClicks` | `number` | The number of clicks on ad unit components. |
| `data[].approximateMemberReach` | `number` | An approximation of unique ad impressions. |
| `data[].cardClicks` | `number` | The number of clicks on interactive card elements. |
| `data[].cardImpressions` | `number` | The number of times interactive cards were displayed. |
| `data[].clicks` | `number` | Total number of clicks on the ad. |
| `data[].commentLikes` | `number` | The count of likes on comments related to the ad. |
| `data[].comments` | `number` | The number of comments on the ad. |
| `data[].companyPageClicks` | `number` | Clicks on the company page associated with the ad. |
| `data[].conversionValueInLocalCurrency` | `number` | Conversion value in the local currency. |
| `data[].costInLocalCurrency` | `number` | Cost of ad campaign in the local currency. |
| `data[].costInUsd` | `number` | Cost of ad campaign in USD. |
| `data[].documentCompletions` | `number` | Number of completions for document views. |
| `data[].documentFirstQuartileCompletions` | `number` | Completions for first quartile of document views. |
| `data[].documentMidpointCompletions` | `number` | Completions for midpoint of document views. |
| `data[].documentThirdQuartileCompletions` | `number` | Completions for third quartile of document views. |
| `data[].downloadClicks` | `number` | Clicks on download links in the ad. |
| `data[].end_date` | `string` | End date of the ad analytics data. |
| `data[].externalWebsiteConversions` | `number` | Conversions that lead to external websites. |
| `data[].externalWebsitePostClickConversions` | `number` | Post-click conversions on external websites. |
| `data[].externalWebsitePostViewConversions` | `number` | Post-view conversions on external websites. |
| `data[].follows` | `number` | Number of follows generated by the ad. |
| `data[].fullScreenPlays` | `number` | Number of times videos were played in fullscreen mode. |
| `data[].impressions` | `number` | Total number of times the ad was displayed. |
| `data[].jobApplications` | `number` | Number of job applications initiated through the ad. |
| `data[].jobApplyClicks` | `number` | Clicks on apply job button in the ad. |
| `data[].landingPageClicks` | `number` | Clicks on the landing page associated with the ad. |
| `data[].leadGenerationMailContactInfoShares` | `number` | Shares of contact information through lead generation. |
| `data[].leadGenerationMailInterestedClicks` | `number` | Clicks on expressing interest through lead generation mail. |
| `data[].likes` | `number` | Total likes received on the ad. |
| `data[].oneClickLeadFormOpens` | `number` | Number of times lead forms were opened in one click. |
| `data[].oneClickLeads` | `number` | Leads generated in one click. |
| `data[].opens` | `number` | The number of times the ad was opened or expanded. |
| `data[].otherEngagements` | `number` | Engagements other than clicks on the ad. |
| `data[].pivotValues` | `array` | Values used for pivoting the analytics. |
| `data[].string_of_pivot_values` | `string` | Comma-separated string of pivot values for this analytics record |
| `data[].postClickJobApplications` | `number` | Job applications initiated post-clicking on the ad. |
| `data[].postClickJobApplyClicks` | `number` | Clicks on apply job button post-clicking on the ad. |
| `data[].postClickRegistrations` | `number` | Registrations completed post-clicking on the ad. |
| `data[].postViewJobApplications` | `number` | Job applications initiated post-viewing the ad. |
| `data[].postViewJobApplyClicks` | `number` | Clicks on apply job button post-viewing the ad. |
| `data[].postViewRegistrations` | `number` | Registrations completed post-viewing the ad. |
| `data[].reactions` | `number` | Total reactions (e.g., like, love, celebrate) on the ad. |
| `data[].registrations` | `number` | Total registrations completed through the ad. |
| `data[].sends` | `number` | Number of messages sent through the ad. |
| `data[].shares` | `number` | Total shares generated by the ad. |
| `data[].start_date` | `string` | Start date of the ad analytics data. |
| `data[].talentLeads` | `number` | Number of leads related to talent acquisition. |
| `data[].textUrlClicks` | `number` | Clicks on text URLs within the ad. |
| `data[].totalEngagements` | `number` | Total number of engagements on the ad. |
| `data[].validWorkEmailLeads` | `number` | Leads generated through valid work emails. |
| `data[].videoCompletions` | `number` | Number of times videos were watched till completion. |
| `data[].videoFirstQuartileCompletions` | `number` | Completions for first quartile of video views. |
| `data[].videoMidpointCompletions` | `number` | Completions for midpoint of video views. |
| `data[].videoStarts` | `number` | Total video starts initiated by users. |
| `data[].videoThirdQuartileCompletions` | `number` | Completions for third quartile of video views. |
| `data[].videoViews` | `number` | Total views of videos in the ad. |
| `data[].viralCardClicks` | `number` | Clicks on interactive card components in viral distribution. |
| `data[].viralCardImpressions` | `number` | Impressions of interactive cards in viral distribution. |
| `data[].viralClicks` | `number` | Total clicks in viral distribution of the ad. |
| `data[].viralCommentLikes` | `number` | Likes received on comments in viral distribution. |
| `data[].viralComments` | `number` | Number of comments in viral distribution of the ad. |
| `data[].viralCompanyPageClicks` | `number` | Clicks on the company page in viral distribution. |
| `data[].viralDocumentCompletions` | `number` | Complete views of documents in viral distribution. |
| `data[].viralDocumentFirstQuartileCompletions` | `number` | First quartile completions of documents in viral distribution. |
| `data[].viralDocumentMidpointCompletions` | `number` | Midpoint completions of documents in viral distribution. |
| `data[].viralDocumentThirdQuartileCompletions` | `number` | Third quartile completions of documents in viral distribution. |
| `data[].viralDownloadClicks` | `number` | Clicks on downloads in viral distribution of the ad. |
| `data[].viralExternalWebsiteConversions` | `number` | External website conversions in viral distribution. |
| `data[].viralExternalWebsitePostClickConversions` | `number` | Post-click conversions on external websites in viral distribution. |
| `data[].viralExternalWebsitePostViewConversions` | `number` | Post-view conversions on external websites in viral distribution. |
| `data[].viralFollows` | `number` | Follows generated in viral distribution of the ad. |
| `data[].viralFullScreenPlays` | `number` | Fullscreen video plays in viral distribution. |
| `data[].viralImpressions` | `number` | Total impressions in viral distribution of the ad. |
| `data[].viralJobApplications` | `number` | Job applications initiated in viral distribution. |
| `data[].viralJobApplyClicks` | `number` | Clicks on apply job button in viral distribution of the ad. |
| `data[].viralLandingPageClicks` | `number` | Clicks on landing page in viral distribution. |
| `data[].viralLikes` | `number` | Total likes in viral distribution of the ad. |
| `data[].viralOneClickLeadFormOpens` | `number` | One-click lead form opens in viral distribution. |
| `data[].viralOneClickLeads` | `number` | Leads generated in one click in viral distribution. |
| `data[].viralOtherEngagements` | `number` | Other engagements in viral distribution of the ad. |
| `data[].viralPostClickJobApplications` | `number` | Job applications initiated post-clicking in viral distribution. |
| `data[].viralPostClickJobApplyClicks` | `number` | Clicks on apply job button post-clicking in viral distribution. |
| `data[].viralPostClickRegistrations` | `number` | Registrations completed post-clicking in viral distribution. |
| `data[].viralPostViewJobApplications` | `number` | Job applications initiated post-viewing in viral distribution. |
| `data[].viralPostViewJobApplyClicks` | `number` | Clicks on apply job button post-viewing in viral distribution. |
| `data[].viralPostViewRegistrations` | `number` | Registrations completed post-viewing in viral distribution. |
| `data[].viralReactions` | `number` | Total reactions in viral distribution of the ad. |
| `data[].viralRegistrations` | `number` | Total registrations in viral distribution of the ad. |
| `data[].viralShares` | `number` | Total shares in viral distribution of the ad. |
| `data[].viralTotalEngagements` | `number` | Total engagements in viral distribution of the ad. |
| `data[].viralVideoCompletions` | `number` | Completions of videos in viral distribution. |
| `data[].viralVideoFirstQuartileCompletions` | `number` | First quartile completions of videos in viral distribution. |
| `data[].viralVideoMidpointCompletions` | `number` | Midpoint completions of videos in viral distribution. |
| `data[].viralVideoStarts` | `number` | Total video starts in viral distribution of the ad. |
| `data[].viralVideoThirdQuartileCompletions` | `number` | Third quartile completions of videos in viral distribution. |
| `data[].viralVideoViews` | `number` | Total views of videos in viral distribution of the ad. |
| `data[].pivot` | `string` | Pivot dimension used for this analytics record |
| `data[].sponsoredCampaign` | `string` | URN of the sponsored campaign this analytics record belongs to |

</details>

## Ad Member Job Function Analytics

### Ad Member Job Function Analytics List

Returns ad analytics data pivoted by member job function. Provides performance metrics including clicks, impressions, spend, and engagement data grouped by member job function.


#### CLI

```bash
airbyte-agent connectors execute --json '{
  "workspace": "<your_workspace_name>",
  "name": "linkedin-ads",
  "entity": "ad_member_job_function_analytics",
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

#### Python SDK

```python
await linkedin_ads.ad_member_job_function_analytics.list(
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
    "entity": "ad_member_job_function_analytics",
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
| `q` | `string` | Yes | LinkedIn API finder method for querying ad analytics |
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

### Ad Member Job Function Analytics Context Store Search

Search and filter ad member job function analytics records powered by Airbyte's data sync. This often provides additional fields and operators beyond what the API natively supports, making it easier to narrow down results before performing further operations. Only available in hosted mode.

#### CLI

```bash
airbyte-agent connectors execute --json '{
  "workspace": "<your_workspace_name>",
  "name": "linkedin-ads",
  "entity": "ad_member_job_function_analytics",
  "action": "context_store_search",
  "params": {
    "query": {
      "filter": {
        "eq": {
          "actionClicks": 0.0
        }
      }
    }
  }
}'
```

#### Python SDK

```python
await linkedin_ads.ad_member_job_function_analytics.context_store_search(
    query={"filter": {"eq": {"actionClicks": 0.0}}}
)
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/integrations/connectors/{your_connector_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "ad_member_job_function_analytics",
    "action": "context_store_search",
    "params": {
        "query": {"filter": {"eq": {"actionClicks": 0.0}}}
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
| `actionClicks` | `number` | The number of clicks on action buttons in the ad. |
| `adUnitClicks` | `number` | The number of clicks on ad unit components. |
| `approximateMemberReach` | `number` | An approximation of unique ad impressions. |
| `cardClicks` | `number` | The number of clicks on interactive card elements. |
| `cardImpressions` | `number` | The number of times interactive cards were displayed. |
| `clicks` | `number` | Total number of clicks on the ad. |
| `commentLikes` | `number` | The count of likes on comments related to the ad. |
| `comments` | `number` | The number of comments on the ad. |
| `companyPageClicks` | `number` | Clicks on the company page associated with the ad. |
| `conversionValueInLocalCurrency` | `number` | Conversion value in the local currency. |
| `costInLocalCurrency` | `number` | Cost of ad campaign in the local currency. |
| `costInUsd` | `number` | Cost of ad campaign in USD. |
| `documentCompletions` | `number` | Number of completions for document views. |
| `documentFirstQuartileCompletions` | `number` | Completions for first quartile of document views. |
| `documentMidpointCompletions` | `number` | Completions for midpoint of document views. |
| `documentThirdQuartileCompletions` | `number` | Completions for third quartile of document views. |
| `downloadClicks` | `number` | Clicks on download links in the ad. |
| `end_date` | `string` | End date of the ad analytics data. |
| `externalWebsiteConversions` | `number` | Conversions that lead to external websites. |
| `externalWebsitePostClickConversions` | `number` | Post-click conversions on external websites. |
| `externalWebsitePostViewConversions` | `number` | Post-view conversions on external websites. |
| `follows` | `number` | Number of follows generated by the ad. |
| `fullScreenPlays` | `number` | Number of times videos were played in fullscreen mode. |
| `impressions` | `number` | Total number of times the ad was displayed. |
| `jobApplications` | `number` | Number of job applications initiated through the ad. |
| `jobApplyClicks` | `number` | Clicks on apply job button in the ad. |
| `landingPageClicks` | `number` | Clicks on the landing page associated with the ad. |
| `leadGenerationMailContactInfoShares` | `number` | Shares of contact information through lead generation. |
| `leadGenerationMailInterestedClicks` | `number` | Clicks on expressing interest through lead generation mail. |
| `likes` | `number` | Total likes received on the ad. |
| `oneClickLeadFormOpens` | `number` | Number of times lead forms were opened in one click. |
| `oneClickLeads` | `number` | Leads generated in one click. |
| `opens` | `number` | The number of times the ad was opened or expanded. |
| `otherEngagements` | `number` | Engagements other than clicks on the ad. |
| `pivotValues` | `array` | Values used for pivoting the analytics. |
| `string_of_pivot_values` | `string` | Comma-separated string of pivot values for this analytics record |
| `postClickJobApplications` | `number` | Job applications initiated post-clicking on the ad. |
| `postClickJobApplyClicks` | `number` | Clicks on apply job button post-clicking on the ad. |
| `postClickRegistrations` | `number` | Registrations completed post-clicking on the ad. |
| `postViewJobApplications` | `number` | Job applications initiated post-viewing the ad. |
| `postViewJobApplyClicks` | `number` | Clicks on apply job button post-viewing the ad. |
| `postViewRegistrations` | `number` | Registrations completed post-viewing the ad. |
| `reactions` | `number` | Total reactions (e.g., like, love, celebrate) on the ad. |
| `registrations` | `number` | Total registrations completed through the ad. |
| `sends` | `number` | Number of messages sent through the ad. |
| `shares` | `number` | Total shares generated by the ad. |
| `start_date` | `string` | Start date of the ad analytics data. |
| `talentLeads` | `number` | Number of leads related to talent acquisition. |
| `textUrlClicks` | `number` | Clicks on text URLs within the ad. |
| `totalEngagements` | `number` | Total number of engagements on the ad. |
| `validWorkEmailLeads` | `number` | Leads generated through valid work emails. |
| `videoCompletions` | `number` | Number of times videos were watched till completion. |
| `videoFirstQuartileCompletions` | `number` | Completions for first quartile of video views. |
| `videoMidpointCompletions` | `number` | Completions for midpoint of video views. |
| `videoStarts` | `number` | Total video starts initiated by users. |
| `videoThirdQuartileCompletions` | `number` | Completions for third quartile of video views. |
| `videoViews` | `number` | Total views of videos in the ad. |
| `viralCardClicks` | `number` | Clicks on interactive card components in viral distribution. |
| `viralCardImpressions` | `number` | Impressions of interactive cards in viral distribution. |
| `viralClicks` | `number` | Total clicks in viral distribution of the ad. |
| `viralCommentLikes` | `number` | Likes received on comments in viral distribution. |
| `viralComments` | `number` | Number of comments in viral distribution of the ad. |
| `viralCompanyPageClicks` | `number` | Clicks on the company page in viral distribution. |
| `viralDocumentCompletions` | `number` | Complete views of documents in viral distribution. |
| `viralDocumentFirstQuartileCompletions` | `number` | First quartile completions of documents in viral distribution. |
| `viralDocumentMidpointCompletions` | `number` | Midpoint completions of documents in viral distribution. |
| `viralDocumentThirdQuartileCompletions` | `number` | Third quartile completions of documents in viral distribution. |
| `viralDownloadClicks` | `number` | Clicks on downloads in viral distribution of the ad. |
| `viralExternalWebsiteConversions` | `number` | External website conversions in viral distribution. |
| `viralExternalWebsitePostClickConversions` | `number` | Post-click conversions on external websites in viral distribution. |
| `viralExternalWebsitePostViewConversions` | `number` | Post-view conversions on external websites in viral distribution. |
| `viralFollows` | `number` | Follows generated in viral distribution of the ad. |
| `viralFullScreenPlays` | `number` | Fullscreen video plays in viral distribution. |
| `viralImpressions` | `number` | Total impressions in viral distribution of the ad. |
| `viralJobApplications` | `number` | Job applications initiated in viral distribution. |
| `viralJobApplyClicks` | `number` | Clicks on apply job button in viral distribution of the ad. |
| `viralLandingPageClicks` | `number` | Clicks on landing page in viral distribution. |
| `viralLikes` | `number` | Total likes in viral distribution of the ad. |
| `viralOneClickLeadFormOpens` | `number` | One-click lead form opens in viral distribution. |
| `viralOneClickLeads` | `number` | Leads generated in one click in viral distribution. |
| `viralOtherEngagements` | `number` | Other engagements in viral distribution of the ad. |
| `viralPostClickJobApplications` | `number` | Job applications initiated post-clicking in viral distribution. |
| `viralPostClickJobApplyClicks` | `number` | Clicks on apply job button post-clicking in viral distribution. |
| `viralPostClickRegistrations` | `number` | Registrations completed post-clicking in viral distribution. |
| `viralPostViewJobApplications` | `number` | Job applications initiated post-viewing in viral distribution. |
| `viralPostViewJobApplyClicks` | `number` | Clicks on apply job button post-viewing in viral distribution. |
| `viralPostViewRegistrations` | `number` | Registrations completed post-viewing in viral distribution. |
| `viralReactions` | `number` | Total reactions in viral distribution of the ad. |
| `viralRegistrations` | `number` | Total registrations in viral distribution of the ad. |
| `viralShares` | `number` | Total shares in viral distribution of the ad. |
| `viralTotalEngagements` | `number` | Total engagements in viral distribution of the ad. |
| `viralVideoCompletions` | `number` | Completions of videos in viral distribution. |
| `viralVideoFirstQuartileCompletions` | `number` | First quartile completions of videos in viral distribution. |
| `viralVideoMidpointCompletions` | `number` | Midpoint completions of videos in viral distribution. |
| `viralVideoStarts` | `number` | Total video starts in viral distribution of the ad. |
| `viralVideoThirdQuartileCompletions` | `number` | Third quartile completions of videos in viral distribution. |
| `viralVideoViews` | `number` | Total views of videos in viral distribution of the ad. |
| `pivot` | `string` | Pivot dimension used for this analytics record |
| `sponsoredCampaign` | `string` | URN of the sponsored campaign this analytics record belongs to |

<details>
<summary><b>Response Schema</b></summary>

| Field Name | Type | Description |
|------------|------|-------------|
| `data` | `array` | List of matching records |
| `meta` | `object` | Pagination metadata |
| `meta.has_more` | `boolean` | Whether additional pages are available |
| `meta.cursor` | `string \| null` | Cursor for next page of results |
| `meta.took_ms` | `number \| null` | Query execution time in milliseconds |
| `data[].actionClicks` | `number` | The number of clicks on action buttons in the ad. |
| `data[].adUnitClicks` | `number` | The number of clicks on ad unit components. |
| `data[].approximateMemberReach` | `number` | An approximation of unique ad impressions. |
| `data[].cardClicks` | `number` | The number of clicks on interactive card elements. |
| `data[].cardImpressions` | `number` | The number of times interactive cards were displayed. |
| `data[].clicks` | `number` | Total number of clicks on the ad. |
| `data[].commentLikes` | `number` | The count of likes on comments related to the ad. |
| `data[].comments` | `number` | The number of comments on the ad. |
| `data[].companyPageClicks` | `number` | Clicks on the company page associated with the ad. |
| `data[].conversionValueInLocalCurrency` | `number` | Conversion value in the local currency. |
| `data[].costInLocalCurrency` | `number` | Cost of ad campaign in the local currency. |
| `data[].costInUsd` | `number` | Cost of ad campaign in USD. |
| `data[].documentCompletions` | `number` | Number of completions for document views. |
| `data[].documentFirstQuartileCompletions` | `number` | Completions for first quartile of document views. |
| `data[].documentMidpointCompletions` | `number` | Completions for midpoint of document views. |
| `data[].documentThirdQuartileCompletions` | `number` | Completions for third quartile of document views. |
| `data[].downloadClicks` | `number` | Clicks on download links in the ad. |
| `data[].end_date` | `string` | End date of the ad analytics data. |
| `data[].externalWebsiteConversions` | `number` | Conversions that lead to external websites. |
| `data[].externalWebsitePostClickConversions` | `number` | Post-click conversions on external websites. |
| `data[].externalWebsitePostViewConversions` | `number` | Post-view conversions on external websites. |
| `data[].follows` | `number` | Number of follows generated by the ad. |
| `data[].fullScreenPlays` | `number` | Number of times videos were played in fullscreen mode. |
| `data[].impressions` | `number` | Total number of times the ad was displayed. |
| `data[].jobApplications` | `number` | Number of job applications initiated through the ad. |
| `data[].jobApplyClicks` | `number` | Clicks on apply job button in the ad. |
| `data[].landingPageClicks` | `number` | Clicks on the landing page associated with the ad. |
| `data[].leadGenerationMailContactInfoShares` | `number` | Shares of contact information through lead generation. |
| `data[].leadGenerationMailInterestedClicks` | `number` | Clicks on expressing interest through lead generation mail. |
| `data[].likes` | `number` | Total likes received on the ad. |
| `data[].oneClickLeadFormOpens` | `number` | Number of times lead forms were opened in one click. |
| `data[].oneClickLeads` | `number` | Leads generated in one click. |
| `data[].opens` | `number` | The number of times the ad was opened or expanded. |
| `data[].otherEngagements` | `number` | Engagements other than clicks on the ad. |
| `data[].pivotValues` | `array` | Values used for pivoting the analytics. |
| `data[].string_of_pivot_values` | `string` | Comma-separated string of pivot values for this analytics record |
| `data[].postClickJobApplications` | `number` | Job applications initiated post-clicking on the ad. |
| `data[].postClickJobApplyClicks` | `number` | Clicks on apply job button post-clicking on the ad. |
| `data[].postClickRegistrations` | `number` | Registrations completed post-clicking on the ad. |
| `data[].postViewJobApplications` | `number` | Job applications initiated post-viewing the ad. |
| `data[].postViewJobApplyClicks` | `number` | Clicks on apply job button post-viewing the ad. |
| `data[].postViewRegistrations` | `number` | Registrations completed post-viewing the ad. |
| `data[].reactions` | `number` | Total reactions (e.g., like, love, celebrate) on the ad. |
| `data[].registrations` | `number` | Total registrations completed through the ad. |
| `data[].sends` | `number` | Number of messages sent through the ad. |
| `data[].shares` | `number` | Total shares generated by the ad. |
| `data[].start_date` | `string` | Start date of the ad analytics data. |
| `data[].talentLeads` | `number` | Number of leads related to talent acquisition. |
| `data[].textUrlClicks` | `number` | Clicks on text URLs within the ad. |
| `data[].totalEngagements` | `number` | Total number of engagements on the ad. |
| `data[].validWorkEmailLeads` | `number` | Leads generated through valid work emails. |
| `data[].videoCompletions` | `number` | Number of times videos were watched till completion. |
| `data[].videoFirstQuartileCompletions` | `number` | Completions for first quartile of video views. |
| `data[].videoMidpointCompletions` | `number` | Completions for midpoint of video views. |
| `data[].videoStarts` | `number` | Total video starts initiated by users. |
| `data[].videoThirdQuartileCompletions` | `number` | Completions for third quartile of video views. |
| `data[].videoViews` | `number` | Total views of videos in the ad. |
| `data[].viralCardClicks` | `number` | Clicks on interactive card components in viral distribution. |
| `data[].viralCardImpressions` | `number` | Impressions of interactive cards in viral distribution. |
| `data[].viralClicks` | `number` | Total clicks in viral distribution of the ad. |
| `data[].viralCommentLikes` | `number` | Likes received on comments in viral distribution. |
| `data[].viralComments` | `number` | Number of comments in viral distribution of the ad. |
| `data[].viralCompanyPageClicks` | `number` | Clicks on the company page in viral distribution. |
| `data[].viralDocumentCompletions` | `number` | Complete views of documents in viral distribution. |
| `data[].viralDocumentFirstQuartileCompletions` | `number` | First quartile completions of documents in viral distribution. |
| `data[].viralDocumentMidpointCompletions` | `number` | Midpoint completions of documents in viral distribution. |
| `data[].viralDocumentThirdQuartileCompletions` | `number` | Third quartile completions of documents in viral distribution. |
| `data[].viralDownloadClicks` | `number` | Clicks on downloads in viral distribution of the ad. |
| `data[].viralExternalWebsiteConversions` | `number` | External website conversions in viral distribution. |
| `data[].viralExternalWebsitePostClickConversions` | `number` | Post-click conversions on external websites in viral distribution. |
| `data[].viralExternalWebsitePostViewConversions` | `number` | Post-view conversions on external websites in viral distribution. |
| `data[].viralFollows` | `number` | Follows generated in viral distribution of the ad. |
| `data[].viralFullScreenPlays` | `number` | Fullscreen video plays in viral distribution. |
| `data[].viralImpressions` | `number` | Total impressions in viral distribution of the ad. |
| `data[].viralJobApplications` | `number` | Job applications initiated in viral distribution. |
| `data[].viralJobApplyClicks` | `number` | Clicks on apply job button in viral distribution of the ad. |
| `data[].viralLandingPageClicks` | `number` | Clicks on landing page in viral distribution. |
| `data[].viralLikes` | `number` | Total likes in viral distribution of the ad. |
| `data[].viralOneClickLeadFormOpens` | `number` | One-click lead form opens in viral distribution. |
| `data[].viralOneClickLeads` | `number` | Leads generated in one click in viral distribution. |
| `data[].viralOtherEngagements` | `number` | Other engagements in viral distribution of the ad. |
| `data[].viralPostClickJobApplications` | `number` | Job applications initiated post-clicking in viral distribution. |
| `data[].viralPostClickJobApplyClicks` | `number` | Clicks on apply job button post-clicking in viral distribution. |
| `data[].viralPostClickRegistrations` | `number` | Registrations completed post-clicking in viral distribution. |
| `data[].viralPostViewJobApplications` | `number` | Job applications initiated post-viewing in viral distribution. |
| `data[].viralPostViewJobApplyClicks` | `number` | Clicks on apply job button post-viewing in viral distribution. |
| `data[].viralPostViewRegistrations` | `number` | Registrations completed post-viewing in viral distribution. |
| `data[].viralReactions` | `number` | Total reactions in viral distribution of the ad. |
| `data[].viralRegistrations` | `number` | Total registrations in viral distribution of the ad. |
| `data[].viralShares` | `number` | Total shares in viral distribution of the ad. |
| `data[].viralTotalEngagements` | `number` | Total engagements in viral distribution of the ad. |
| `data[].viralVideoCompletions` | `number` | Completions of videos in viral distribution. |
| `data[].viralVideoFirstQuartileCompletions` | `number` | First quartile completions of videos in viral distribution. |
| `data[].viralVideoMidpointCompletions` | `number` | Midpoint completions of videos in viral distribution. |
| `data[].viralVideoStarts` | `number` | Total video starts in viral distribution of the ad. |
| `data[].viralVideoThirdQuartileCompletions` | `number` | Third quartile completions of videos in viral distribution. |
| `data[].viralVideoViews` | `number` | Total views of videos in viral distribution of the ad. |
| `data[].pivot` | `string` | Pivot dimension used for this analytics record |
| `data[].sponsoredCampaign` | `string` | URN of the sponsored campaign this analytics record belongs to |

</details>

## Ad Member Job Title Analytics

### Ad Member Job Title Analytics List

Returns ad analytics data pivoted by member job title. Provides performance metrics including clicks, impressions, spend, and engagement data grouped by member job title.


#### CLI

```bash
airbyte-agent connectors execute --json '{
  "workspace": "<your_workspace_name>",
  "name": "linkedin-ads",
  "entity": "ad_member_job_title_analytics",
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

#### Python SDK

```python
await linkedin_ads.ad_member_job_title_analytics.list(
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
    "entity": "ad_member_job_title_analytics",
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
| `q` | `string` | Yes | LinkedIn API finder method for querying ad analytics |
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

### Ad Member Job Title Analytics Context Store Search

Search and filter ad member job title analytics records powered by Airbyte's data sync. This often provides additional fields and operators beyond what the API natively supports, making it easier to narrow down results before performing further operations. Only available in hosted mode.

#### CLI

```bash
airbyte-agent connectors execute --json '{
  "workspace": "<your_workspace_name>",
  "name": "linkedin-ads",
  "entity": "ad_member_job_title_analytics",
  "action": "context_store_search",
  "params": {
    "query": {
      "filter": {
        "eq": {
          "actionClicks": 0.0
        }
      }
    }
  }
}'
```

#### Python SDK

```python
await linkedin_ads.ad_member_job_title_analytics.context_store_search(
    query={"filter": {"eq": {"actionClicks": 0.0}}}
)
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/integrations/connectors/{your_connector_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "ad_member_job_title_analytics",
    "action": "context_store_search",
    "params": {
        "query": {"filter": {"eq": {"actionClicks": 0.0}}}
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
| `actionClicks` | `number` | The number of clicks on action buttons in the ad. |
| `adUnitClicks` | `number` | The number of clicks on ad unit components. |
| `approximateMemberReach` | `number` | An approximation of unique ad impressions. |
| `cardClicks` | `number` | The number of clicks on interactive card elements. |
| `cardImpressions` | `number` | The number of times interactive cards were displayed. |
| `clicks` | `number` | Total number of clicks on the ad. |
| `commentLikes` | `number` | The count of likes on comments related to the ad. |
| `comments` | `number` | The number of comments on the ad. |
| `companyPageClicks` | `number` | Clicks on the company page associated with the ad. |
| `conversionValueInLocalCurrency` | `number` | Conversion value in the local currency. |
| `costInLocalCurrency` | `number` | Cost of ad campaign in the local currency. |
| `costInUsd` | `number` | Cost of ad campaign in USD. |
| `documentCompletions` | `number` | Number of completions for document views. |
| `documentFirstQuartileCompletions` | `number` | Completions for first quartile of document views. |
| `documentMidpointCompletions` | `number` | Completions for midpoint of document views. |
| `documentThirdQuartileCompletions` | `number` | Completions for third quartile of document views. |
| `downloadClicks` | `number` | Clicks on download links in the ad. |
| `end_date` | `string` | End date of the ad analytics data. |
| `externalWebsiteConversions` | `number` | Conversions that lead to external websites. |
| `externalWebsitePostClickConversions` | `number` | Post-click conversions on external websites. |
| `externalWebsitePostViewConversions` | `number` | Post-view conversions on external websites. |
| `follows` | `number` | Number of follows generated by the ad. |
| `fullScreenPlays` | `number` | Number of times videos were played in fullscreen mode. |
| `impressions` | `number` | Total number of times the ad was displayed. |
| `jobApplications` | `number` | Number of job applications initiated through the ad. |
| `jobApplyClicks` | `number` | Clicks on apply job button in the ad. |
| `landingPageClicks` | `number` | Clicks on the landing page associated with the ad. |
| `leadGenerationMailContactInfoShares` | `number` | Shares of contact information through lead generation. |
| `leadGenerationMailInterestedClicks` | `number` | Clicks on expressing interest through lead generation mail. |
| `likes` | `number` | Total likes received on the ad. |
| `oneClickLeadFormOpens` | `number` | Number of times lead forms were opened in one click. |
| `oneClickLeads` | `number` | Leads generated in one click. |
| `opens` | `number` | The number of times the ad was opened or expanded. |
| `otherEngagements` | `number` | Engagements other than clicks on the ad. |
| `pivotValues` | `array` | Values used for pivoting the analytics. |
| `string_of_pivot_values` | `string` | Comma-separated string of pivot values for this analytics record |
| `postClickJobApplications` | `number` | Job applications initiated post-clicking on the ad. |
| `postClickJobApplyClicks` | `number` | Clicks on apply job button post-clicking on the ad. |
| `postClickRegistrations` | `number` | Registrations completed post-clicking on the ad. |
| `postViewJobApplications` | `number` | Job applications initiated post-viewing the ad. |
| `postViewJobApplyClicks` | `number` | Clicks on apply job button post-viewing the ad. |
| `postViewRegistrations` | `number` | Registrations completed post-viewing the ad. |
| `reactions` | `number` | Total reactions (e.g., like, love, celebrate) on the ad. |
| `registrations` | `number` | Total registrations completed through the ad. |
| `sends` | `number` | Number of messages sent through the ad. |
| `shares` | `number` | Total shares generated by the ad. |
| `start_date` | `string` | Start date of the ad analytics data. |
| `talentLeads` | `number` | Number of leads related to talent acquisition. |
| `textUrlClicks` | `number` | Clicks on text URLs within the ad. |
| `totalEngagements` | `number` | Total number of engagements on the ad. |
| `validWorkEmailLeads` | `number` | Leads generated through valid work emails. |
| `videoCompletions` | `number` | Number of times videos were watched till completion. |
| `videoFirstQuartileCompletions` | `number` | Completions for first quartile of video views. |
| `videoMidpointCompletions` | `number` | Completions for midpoint of video views. |
| `videoStarts` | `number` | Total video starts initiated by users. |
| `videoThirdQuartileCompletions` | `number` | Completions for third quartile of video views. |
| `videoViews` | `number` | Total views of videos in the ad. |
| `viralCardClicks` | `number` | Clicks on interactive card components in viral distribution. |
| `viralCardImpressions` | `number` | Impressions of interactive cards in viral distribution. |
| `viralClicks` | `number` | Total clicks in viral distribution of the ad. |
| `viralCommentLikes` | `number` | Likes received on comments in viral distribution. |
| `viralComments` | `number` | Number of comments in viral distribution of the ad. |
| `viralCompanyPageClicks` | `number` | Clicks on the company page in viral distribution. |
| `viralDocumentCompletions` | `number` | Complete views of documents in viral distribution. |
| `viralDocumentFirstQuartileCompletions` | `number` | First quartile completions of documents in viral distribution. |
| `viralDocumentMidpointCompletions` | `number` | Midpoint completions of documents in viral distribution. |
| `viralDocumentThirdQuartileCompletions` | `number` | Third quartile completions of documents in viral distribution. |
| `viralDownloadClicks` | `number` | Clicks on downloads in viral distribution of the ad. |
| `viralExternalWebsiteConversions` | `number` | External website conversions in viral distribution. |
| `viralExternalWebsitePostClickConversions` | `number` | Post-click conversions on external websites in viral distribution. |
| `viralExternalWebsitePostViewConversions` | `number` | Post-view conversions on external websites in viral distribution. |
| `viralFollows` | `number` | Follows generated in viral distribution of the ad. |
| `viralFullScreenPlays` | `number` | Fullscreen video plays in viral distribution. |
| `viralImpressions` | `number` | Total impressions in viral distribution of the ad. |
| `viralJobApplications` | `number` | Job applications initiated in viral distribution. |
| `viralJobApplyClicks` | `number` | Clicks on apply job button in viral distribution of the ad. |
| `viralLandingPageClicks` | `number` | Clicks on landing page in viral distribution. |
| `viralLikes` | `number` | Total likes in viral distribution of the ad. |
| `viralOneClickLeadFormOpens` | `number` | One-click lead form opens in viral distribution. |
| `viralOneClickLeads` | `number` | Leads generated in one click in viral distribution. |
| `viralOtherEngagements` | `number` | Other engagements in viral distribution of the ad. |
| `viralPostClickJobApplications` | `number` | Job applications initiated post-clicking in viral distribution. |
| `viralPostClickJobApplyClicks` | `number` | Clicks on apply job button post-clicking in viral distribution. |
| `viralPostClickRegistrations` | `number` | Registrations completed post-clicking in viral distribution. |
| `viralPostViewJobApplications` | `number` | Job applications initiated post-viewing in viral distribution. |
| `viralPostViewJobApplyClicks` | `number` | Clicks on apply job button post-viewing in viral distribution. |
| `viralPostViewRegistrations` | `number` | Registrations completed post-viewing in viral distribution. |
| `viralReactions` | `number` | Total reactions in viral distribution of the ad. |
| `viralRegistrations` | `number` | Total registrations in viral distribution of the ad. |
| `viralShares` | `number` | Total shares in viral distribution of the ad. |
| `viralTotalEngagements` | `number` | Total engagements in viral distribution of the ad. |
| `viralVideoCompletions` | `number` | Completions of videos in viral distribution. |
| `viralVideoFirstQuartileCompletions` | `number` | First quartile completions of videos in viral distribution. |
| `viralVideoMidpointCompletions` | `number` | Midpoint completions of videos in viral distribution. |
| `viralVideoStarts` | `number` | Total video starts in viral distribution of the ad. |
| `viralVideoThirdQuartileCompletions` | `number` | Third quartile completions of videos in viral distribution. |
| `viralVideoViews` | `number` | Total views of videos in viral distribution of the ad. |
| `pivot` | `string` | Pivot dimension used for this analytics record |
| `sponsoredCampaign` | `string` | URN of the sponsored campaign this analytics record belongs to |

<details>
<summary><b>Response Schema</b></summary>

| Field Name | Type | Description |
|------------|------|-------------|
| `data` | `array` | List of matching records |
| `meta` | `object` | Pagination metadata |
| `meta.has_more` | `boolean` | Whether additional pages are available |
| `meta.cursor` | `string \| null` | Cursor for next page of results |
| `meta.took_ms` | `number \| null` | Query execution time in milliseconds |
| `data[].actionClicks` | `number` | The number of clicks on action buttons in the ad. |
| `data[].adUnitClicks` | `number` | The number of clicks on ad unit components. |
| `data[].approximateMemberReach` | `number` | An approximation of unique ad impressions. |
| `data[].cardClicks` | `number` | The number of clicks on interactive card elements. |
| `data[].cardImpressions` | `number` | The number of times interactive cards were displayed. |
| `data[].clicks` | `number` | Total number of clicks on the ad. |
| `data[].commentLikes` | `number` | The count of likes on comments related to the ad. |
| `data[].comments` | `number` | The number of comments on the ad. |
| `data[].companyPageClicks` | `number` | Clicks on the company page associated with the ad. |
| `data[].conversionValueInLocalCurrency` | `number` | Conversion value in the local currency. |
| `data[].costInLocalCurrency` | `number` | Cost of ad campaign in the local currency. |
| `data[].costInUsd` | `number` | Cost of ad campaign in USD. |
| `data[].documentCompletions` | `number` | Number of completions for document views. |
| `data[].documentFirstQuartileCompletions` | `number` | Completions for first quartile of document views. |
| `data[].documentMidpointCompletions` | `number` | Completions for midpoint of document views. |
| `data[].documentThirdQuartileCompletions` | `number` | Completions for third quartile of document views. |
| `data[].downloadClicks` | `number` | Clicks on download links in the ad. |
| `data[].end_date` | `string` | End date of the ad analytics data. |
| `data[].externalWebsiteConversions` | `number` | Conversions that lead to external websites. |
| `data[].externalWebsitePostClickConversions` | `number` | Post-click conversions on external websites. |
| `data[].externalWebsitePostViewConversions` | `number` | Post-view conversions on external websites. |
| `data[].follows` | `number` | Number of follows generated by the ad. |
| `data[].fullScreenPlays` | `number` | Number of times videos were played in fullscreen mode. |
| `data[].impressions` | `number` | Total number of times the ad was displayed. |
| `data[].jobApplications` | `number` | Number of job applications initiated through the ad. |
| `data[].jobApplyClicks` | `number` | Clicks on apply job button in the ad. |
| `data[].landingPageClicks` | `number` | Clicks on the landing page associated with the ad. |
| `data[].leadGenerationMailContactInfoShares` | `number` | Shares of contact information through lead generation. |
| `data[].leadGenerationMailInterestedClicks` | `number` | Clicks on expressing interest through lead generation mail. |
| `data[].likes` | `number` | Total likes received on the ad. |
| `data[].oneClickLeadFormOpens` | `number` | Number of times lead forms were opened in one click. |
| `data[].oneClickLeads` | `number` | Leads generated in one click. |
| `data[].opens` | `number` | The number of times the ad was opened or expanded. |
| `data[].otherEngagements` | `number` | Engagements other than clicks on the ad. |
| `data[].pivotValues` | `array` | Values used for pivoting the analytics. |
| `data[].string_of_pivot_values` | `string` | Comma-separated string of pivot values for this analytics record |
| `data[].postClickJobApplications` | `number` | Job applications initiated post-clicking on the ad. |
| `data[].postClickJobApplyClicks` | `number` | Clicks on apply job button post-clicking on the ad. |
| `data[].postClickRegistrations` | `number` | Registrations completed post-clicking on the ad. |
| `data[].postViewJobApplications` | `number` | Job applications initiated post-viewing the ad. |
| `data[].postViewJobApplyClicks` | `number` | Clicks on apply job button post-viewing the ad. |
| `data[].postViewRegistrations` | `number` | Registrations completed post-viewing the ad. |
| `data[].reactions` | `number` | Total reactions (e.g., like, love, celebrate) on the ad. |
| `data[].registrations` | `number` | Total registrations completed through the ad. |
| `data[].sends` | `number` | Number of messages sent through the ad. |
| `data[].shares` | `number` | Total shares generated by the ad. |
| `data[].start_date` | `string` | Start date of the ad analytics data. |
| `data[].talentLeads` | `number` | Number of leads related to talent acquisition. |
| `data[].textUrlClicks` | `number` | Clicks on text URLs within the ad. |
| `data[].totalEngagements` | `number` | Total number of engagements on the ad. |
| `data[].validWorkEmailLeads` | `number` | Leads generated through valid work emails. |
| `data[].videoCompletions` | `number` | Number of times videos were watched till completion. |
| `data[].videoFirstQuartileCompletions` | `number` | Completions for first quartile of video views. |
| `data[].videoMidpointCompletions` | `number` | Completions for midpoint of video views. |
| `data[].videoStarts` | `number` | Total video starts initiated by users. |
| `data[].videoThirdQuartileCompletions` | `number` | Completions for third quartile of video views. |
| `data[].videoViews` | `number` | Total views of videos in the ad. |
| `data[].viralCardClicks` | `number` | Clicks on interactive card components in viral distribution. |
| `data[].viralCardImpressions` | `number` | Impressions of interactive cards in viral distribution. |
| `data[].viralClicks` | `number` | Total clicks in viral distribution of the ad. |
| `data[].viralCommentLikes` | `number` | Likes received on comments in viral distribution. |
| `data[].viralComments` | `number` | Number of comments in viral distribution of the ad. |
| `data[].viralCompanyPageClicks` | `number` | Clicks on the company page in viral distribution. |
| `data[].viralDocumentCompletions` | `number` | Complete views of documents in viral distribution. |
| `data[].viralDocumentFirstQuartileCompletions` | `number` | First quartile completions of documents in viral distribution. |
| `data[].viralDocumentMidpointCompletions` | `number` | Midpoint completions of documents in viral distribution. |
| `data[].viralDocumentThirdQuartileCompletions` | `number` | Third quartile completions of documents in viral distribution. |
| `data[].viralDownloadClicks` | `number` | Clicks on downloads in viral distribution of the ad. |
| `data[].viralExternalWebsiteConversions` | `number` | External website conversions in viral distribution. |
| `data[].viralExternalWebsitePostClickConversions` | `number` | Post-click conversions on external websites in viral distribution. |
| `data[].viralExternalWebsitePostViewConversions` | `number` | Post-view conversions on external websites in viral distribution. |
| `data[].viralFollows` | `number` | Follows generated in viral distribution of the ad. |
| `data[].viralFullScreenPlays` | `number` | Fullscreen video plays in viral distribution. |
| `data[].viralImpressions` | `number` | Total impressions in viral distribution of the ad. |
| `data[].viralJobApplications` | `number` | Job applications initiated in viral distribution. |
| `data[].viralJobApplyClicks` | `number` | Clicks on apply job button in viral distribution of the ad. |
| `data[].viralLandingPageClicks` | `number` | Clicks on landing page in viral distribution. |
| `data[].viralLikes` | `number` | Total likes in viral distribution of the ad. |
| `data[].viralOneClickLeadFormOpens` | `number` | One-click lead form opens in viral distribution. |
| `data[].viralOneClickLeads` | `number` | Leads generated in one click in viral distribution. |
| `data[].viralOtherEngagements` | `number` | Other engagements in viral distribution of the ad. |
| `data[].viralPostClickJobApplications` | `number` | Job applications initiated post-clicking in viral distribution. |
| `data[].viralPostClickJobApplyClicks` | `number` | Clicks on apply job button post-clicking in viral distribution. |
| `data[].viralPostClickRegistrations` | `number` | Registrations completed post-clicking in viral distribution. |
| `data[].viralPostViewJobApplications` | `number` | Job applications initiated post-viewing in viral distribution. |
| `data[].viralPostViewJobApplyClicks` | `number` | Clicks on apply job button post-viewing in viral distribution. |
| `data[].viralPostViewRegistrations` | `number` | Registrations completed post-viewing in viral distribution. |
| `data[].viralReactions` | `number` | Total reactions in viral distribution of the ad. |
| `data[].viralRegistrations` | `number` | Total registrations in viral distribution of the ad. |
| `data[].viralShares` | `number` | Total shares in viral distribution of the ad. |
| `data[].viralTotalEngagements` | `number` | Total engagements in viral distribution of the ad. |
| `data[].viralVideoCompletions` | `number` | Completions of videos in viral distribution. |
| `data[].viralVideoFirstQuartileCompletions` | `number` | First quartile completions of videos in viral distribution. |
| `data[].viralVideoMidpointCompletions` | `number` | Midpoint completions of videos in viral distribution. |
| `data[].viralVideoStarts` | `number` | Total video starts in viral distribution of the ad. |
| `data[].viralVideoThirdQuartileCompletions` | `number` | Third quartile completions of videos in viral distribution. |
| `data[].viralVideoViews` | `number` | Total views of videos in viral distribution of the ad. |
| `data[].pivot` | `string` | Pivot dimension used for this analytics record |
| `data[].sponsoredCampaign` | `string` | URN of the sponsored campaign this analytics record belongs to |

</details>

## Ad Member Region Analytics

### Ad Member Region Analytics List

Returns ad analytics data pivoted by member region. Provides performance metrics including clicks, impressions, spend, and engagement data grouped by member region.


#### CLI

```bash
airbyte-agent connectors execute --json '{
  "workspace": "<your_workspace_name>",
  "name": "linkedin-ads",
  "entity": "ad_member_region_analytics",
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

#### Python SDK

```python
await linkedin_ads.ad_member_region_analytics.list(
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
    "entity": "ad_member_region_analytics",
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
| `q` | `string` | Yes | LinkedIn API finder method for querying ad analytics |
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

### Ad Member Region Analytics Context Store Search

Search and filter ad member region analytics records powered by Airbyte's data sync. This often provides additional fields and operators beyond what the API natively supports, making it easier to narrow down results before performing further operations. Only available in hosted mode.

#### CLI

```bash
airbyte-agent connectors execute --json '{
  "workspace": "<your_workspace_name>",
  "name": "linkedin-ads",
  "entity": "ad_member_region_analytics",
  "action": "context_store_search",
  "params": {
    "query": {
      "filter": {
        "eq": {
          "actionClicks": 0.0
        }
      }
    }
  }
}'
```

#### Python SDK

```python
await linkedin_ads.ad_member_region_analytics.context_store_search(
    query={"filter": {"eq": {"actionClicks": 0.0}}}
)
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/integrations/connectors/{your_connector_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "ad_member_region_analytics",
    "action": "context_store_search",
    "params": {
        "query": {"filter": {"eq": {"actionClicks": 0.0}}}
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
| `actionClicks` | `number` | The number of clicks on action buttons in the ad. |
| `adUnitClicks` | `number` | The number of clicks on ad unit components. |
| `approximateMemberReach` | `number` | An approximation of unique ad impressions. |
| `cardClicks` | `number` | The number of clicks on interactive card elements. |
| `cardImpressions` | `number` | The number of times interactive cards were displayed. |
| `clicks` | `number` | Total number of clicks on the ad. |
| `commentLikes` | `number` | The count of likes on comments related to the ad. |
| `comments` | `number` | The number of comments on the ad. |
| `companyPageClicks` | `number` | Clicks on the company page associated with the ad. |
| `conversionValueInLocalCurrency` | `number` | Conversion value in the local currency. |
| `costInLocalCurrency` | `number` | Cost of ad campaign in the local currency. |
| `costInUsd` | `number` | Cost of ad campaign in USD. |
| `documentCompletions` | `number` | Number of completions for document views. |
| `documentFirstQuartileCompletions` | `number` | Completions for first quartile of document views. |
| `documentMidpointCompletions` | `number` | Completions for midpoint of document views. |
| `documentThirdQuartileCompletions` | `number` | Completions for third quartile of document views. |
| `downloadClicks` | `number` | Clicks on download links in the ad. |
| `end_date` | `string` | End date of the ad analytics data. |
| `externalWebsiteConversions` | `number` | Conversions that lead to external websites. |
| `externalWebsitePostClickConversions` | `number` | Post-click conversions on external websites. |
| `externalWebsitePostViewConversions` | `number` | Post-view conversions on external websites. |
| `follows` | `number` | Number of follows generated by the ad. |
| `fullScreenPlays` | `number` | Number of times videos were played in fullscreen mode. |
| `impressions` | `number` | Total number of times the ad was displayed. |
| `jobApplications` | `number` | Number of job applications initiated through the ad. |
| `jobApplyClicks` | `number` | Clicks on apply job button in the ad. |
| `landingPageClicks` | `number` | Clicks on the landing page associated with the ad. |
| `leadGenerationMailContactInfoShares` | `number` | Shares of contact information through lead generation. |
| `leadGenerationMailInterestedClicks` | `number` | Clicks on expressing interest through lead generation mail. |
| `likes` | `number` | Total likes received on the ad. |
| `oneClickLeadFormOpens` | `number` | Number of times lead forms were opened in one click. |
| `oneClickLeads` | `number` | Leads generated in one click. |
| `opens` | `number` | The number of times the ad was opened or expanded. |
| `otherEngagements` | `number` | Engagements other than clicks on the ad. |
| `pivotValues` | `array` | Values used for pivoting the analytics. |
| `string_of_pivot_values` | `string` | Comma-separated string of pivot values for this analytics record |
| `postClickJobApplications` | `number` | Job applications initiated post-clicking on the ad. |
| `postClickJobApplyClicks` | `number` | Clicks on apply job button post-clicking on the ad. |
| `postClickRegistrations` | `number` | Registrations completed post-clicking on the ad. |
| `postViewJobApplications` | `number` | Job applications initiated post-viewing the ad. |
| `postViewJobApplyClicks` | `number` | Clicks on apply job button post-viewing the ad. |
| `postViewRegistrations` | `number` | Registrations completed post-viewing the ad. |
| `reactions` | `number` | Total reactions (e.g., like, love, celebrate) on the ad. |
| `registrations` | `number` | Total registrations completed through the ad. |
| `sends` | `number` | Number of messages sent through the ad. |
| `shares` | `number` | Total shares generated by the ad. |
| `start_date` | `string` | Start date of the ad analytics data. |
| `talentLeads` | `number` | Number of leads related to talent acquisition. |
| `textUrlClicks` | `number` | Clicks on text URLs within the ad. |
| `totalEngagements` | `number` | Total number of engagements on the ad. |
| `validWorkEmailLeads` | `number` | Leads generated through valid work emails. |
| `videoCompletions` | `number` | Number of times videos were watched till completion. |
| `videoFirstQuartileCompletions` | `number` | Completions for first quartile of video views. |
| `videoMidpointCompletions` | `number` | Completions for midpoint of video views. |
| `videoStarts` | `number` | Total video starts initiated by users. |
| `videoThirdQuartileCompletions` | `number` | Completions for third quartile of video views. |
| `videoViews` | `number` | Total views of videos in the ad. |
| `viralCardClicks` | `number` | Clicks on interactive card components in viral distribution. |
| `viralCardImpressions` | `number` | Impressions of interactive cards in viral distribution. |
| `viralClicks` | `number` | Total clicks in viral distribution of the ad. |
| `viralCommentLikes` | `number` | Likes received on comments in viral distribution. |
| `viralComments` | `number` | Number of comments in viral distribution of the ad. |
| `viralCompanyPageClicks` | `number` | Clicks on the company page in viral distribution. |
| `viralDocumentCompletions` | `number` | Complete views of documents in viral distribution. |
| `viralDocumentFirstQuartileCompletions` | `number` | First quartile completions of documents in viral distribution. |
| `viralDocumentMidpointCompletions` | `number` | Midpoint completions of documents in viral distribution. |
| `viralDocumentThirdQuartileCompletions` | `number` | Third quartile completions of documents in viral distribution. |
| `viralDownloadClicks` | `number` | Clicks on downloads in viral distribution of the ad. |
| `viralExternalWebsiteConversions` | `number` | External website conversions in viral distribution. |
| `viralExternalWebsitePostClickConversions` | `number` | Post-click conversions on external websites in viral distribution. |
| `viralExternalWebsitePostViewConversions` | `number` | Post-view conversions on external websites in viral distribution. |
| `viralFollows` | `number` | Follows generated in viral distribution of the ad. |
| `viralFullScreenPlays` | `number` | Fullscreen video plays in viral distribution. |
| `viralImpressions` | `number` | Total impressions in viral distribution of the ad. |
| `viralJobApplications` | `number` | Job applications initiated in viral distribution. |
| `viralJobApplyClicks` | `number` | Clicks on apply job button in viral distribution of the ad. |
| `viralLandingPageClicks` | `number` | Clicks on landing page in viral distribution. |
| `viralLikes` | `number` | Total likes in viral distribution of the ad. |
| `viralOneClickLeadFormOpens` | `number` | One-click lead form opens in viral distribution. |
| `viralOneClickLeads` | `number` | Leads generated in one click in viral distribution. |
| `viralOtherEngagements` | `number` | Other engagements in viral distribution of the ad. |
| `viralPostClickJobApplications` | `number` | Job applications initiated post-clicking in viral distribution. |
| `viralPostClickJobApplyClicks` | `number` | Clicks on apply job button post-clicking in viral distribution. |
| `viralPostClickRegistrations` | `number` | Registrations completed post-clicking in viral distribution. |
| `viralPostViewJobApplications` | `number` | Job applications initiated post-viewing in viral distribution. |
| `viralPostViewJobApplyClicks` | `number` | Clicks on apply job button post-viewing in viral distribution. |
| `viralPostViewRegistrations` | `number` | Registrations completed post-viewing in viral distribution. |
| `viralReactions` | `number` | Total reactions in viral distribution of the ad. |
| `viralRegistrations` | `number` | Total registrations in viral distribution of the ad. |
| `viralShares` | `number` | Total shares in viral distribution of the ad. |
| `viralTotalEngagements` | `number` | Total engagements in viral distribution of the ad. |
| `viralVideoCompletions` | `number` | Completions of videos in viral distribution. |
| `viralVideoFirstQuartileCompletions` | `number` | First quartile completions of videos in viral distribution. |
| `viralVideoMidpointCompletions` | `number` | Midpoint completions of videos in viral distribution. |
| `viralVideoStarts` | `number` | Total video starts in viral distribution of the ad. |
| `viralVideoThirdQuartileCompletions` | `number` | Third quartile completions of videos in viral distribution. |
| `viralVideoViews` | `number` | Total views of videos in viral distribution of the ad. |
| `pivot` | `string` | Pivot dimension used for this analytics record |
| `sponsoredCampaign` | `string` | URN of the sponsored campaign this analytics record belongs to |

<details>
<summary><b>Response Schema</b></summary>

| Field Name | Type | Description |
|------------|------|-------------|
| `data` | `array` | List of matching records |
| `meta` | `object` | Pagination metadata |
| `meta.has_more` | `boolean` | Whether additional pages are available |
| `meta.cursor` | `string \| null` | Cursor for next page of results |
| `meta.took_ms` | `number \| null` | Query execution time in milliseconds |
| `data[].actionClicks` | `number` | The number of clicks on action buttons in the ad. |
| `data[].adUnitClicks` | `number` | The number of clicks on ad unit components. |
| `data[].approximateMemberReach` | `number` | An approximation of unique ad impressions. |
| `data[].cardClicks` | `number` | The number of clicks on interactive card elements. |
| `data[].cardImpressions` | `number` | The number of times interactive cards were displayed. |
| `data[].clicks` | `number` | Total number of clicks on the ad. |
| `data[].commentLikes` | `number` | The count of likes on comments related to the ad. |
| `data[].comments` | `number` | The number of comments on the ad. |
| `data[].companyPageClicks` | `number` | Clicks on the company page associated with the ad. |
| `data[].conversionValueInLocalCurrency` | `number` | Conversion value in the local currency. |
| `data[].costInLocalCurrency` | `number` | Cost of ad campaign in the local currency. |
| `data[].costInUsd` | `number` | Cost of ad campaign in USD. |
| `data[].documentCompletions` | `number` | Number of completions for document views. |
| `data[].documentFirstQuartileCompletions` | `number` | Completions for first quartile of document views. |
| `data[].documentMidpointCompletions` | `number` | Completions for midpoint of document views. |
| `data[].documentThirdQuartileCompletions` | `number` | Completions for third quartile of document views. |
| `data[].downloadClicks` | `number` | Clicks on download links in the ad. |
| `data[].end_date` | `string` | End date of the ad analytics data. |
| `data[].externalWebsiteConversions` | `number` | Conversions that lead to external websites. |
| `data[].externalWebsitePostClickConversions` | `number` | Post-click conversions on external websites. |
| `data[].externalWebsitePostViewConversions` | `number` | Post-view conversions on external websites. |
| `data[].follows` | `number` | Number of follows generated by the ad. |
| `data[].fullScreenPlays` | `number` | Number of times videos were played in fullscreen mode. |
| `data[].impressions` | `number` | Total number of times the ad was displayed. |
| `data[].jobApplications` | `number` | Number of job applications initiated through the ad. |
| `data[].jobApplyClicks` | `number` | Clicks on apply job button in the ad. |
| `data[].landingPageClicks` | `number` | Clicks on the landing page associated with the ad. |
| `data[].leadGenerationMailContactInfoShares` | `number` | Shares of contact information through lead generation. |
| `data[].leadGenerationMailInterestedClicks` | `number` | Clicks on expressing interest through lead generation mail. |
| `data[].likes` | `number` | Total likes received on the ad. |
| `data[].oneClickLeadFormOpens` | `number` | Number of times lead forms were opened in one click. |
| `data[].oneClickLeads` | `number` | Leads generated in one click. |
| `data[].opens` | `number` | The number of times the ad was opened or expanded. |
| `data[].otherEngagements` | `number` | Engagements other than clicks on the ad. |
| `data[].pivotValues` | `array` | Values used for pivoting the analytics. |
| `data[].string_of_pivot_values` | `string` | Comma-separated string of pivot values for this analytics record |
| `data[].postClickJobApplications` | `number` | Job applications initiated post-clicking on the ad. |
| `data[].postClickJobApplyClicks` | `number` | Clicks on apply job button post-clicking on the ad. |
| `data[].postClickRegistrations` | `number` | Registrations completed post-clicking on the ad. |
| `data[].postViewJobApplications` | `number` | Job applications initiated post-viewing the ad. |
| `data[].postViewJobApplyClicks` | `number` | Clicks on apply job button post-viewing the ad. |
| `data[].postViewRegistrations` | `number` | Registrations completed post-viewing the ad. |
| `data[].reactions` | `number` | Total reactions (e.g., like, love, celebrate) on the ad. |
| `data[].registrations` | `number` | Total registrations completed through the ad. |
| `data[].sends` | `number` | Number of messages sent through the ad. |
| `data[].shares` | `number` | Total shares generated by the ad. |
| `data[].start_date` | `string` | Start date of the ad analytics data. |
| `data[].talentLeads` | `number` | Number of leads related to talent acquisition. |
| `data[].textUrlClicks` | `number` | Clicks on text URLs within the ad. |
| `data[].totalEngagements` | `number` | Total number of engagements on the ad. |
| `data[].validWorkEmailLeads` | `number` | Leads generated through valid work emails. |
| `data[].videoCompletions` | `number` | Number of times videos were watched till completion. |
| `data[].videoFirstQuartileCompletions` | `number` | Completions for first quartile of video views. |
| `data[].videoMidpointCompletions` | `number` | Completions for midpoint of video views. |
| `data[].videoStarts` | `number` | Total video starts initiated by users. |
| `data[].videoThirdQuartileCompletions` | `number` | Completions for third quartile of video views. |
| `data[].videoViews` | `number` | Total views of videos in the ad. |
| `data[].viralCardClicks` | `number` | Clicks on interactive card components in viral distribution. |
| `data[].viralCardImpressions` | `number` | Impressions of interactive cards in viral distribution. |
| `data[].viralClicks` | `number` | Total clicks in viral distribution of the ad. |
| `data[].viralCommentLikes` | `number` | Likes received on comments in viral distribution. |
| `data[].viralComments` | `number` | Number of comments in viral distribution of the ad. |
| `data[].viralCompanyPageClicks` | `number` | Clicks on the company page in viral distribution. |
| `data[].viralDocumentCompletions` | `number` | Complete views of documents in viral distribution. |
| `data[].viralDocumentFirstQuartileCompletions` | `number` | First quartile completions of documents in viral distribution. |
| `data[].viralDocumentMidpointCompletions` | `number` | Midpoint completions of documents in viral distribution. |
| `data[].viralDocumentThirdQuartileCompletions` | `number` | Third quartile completions of documents in viral distribution. |
| `data[].viralDownloadClicks` | `number` | Clicks on downloads in viral distribution of the ad. |
| `data[].viralExternalWebsiteConversions` | `number` | External website conversions in viral distribution. |
| `data[].viralExternalWebsitePostClickConversions` | `number` | Post-click conversions on external websites in viral distribution. |
| `data[].viralExternalWebsitePostViewConversions` | `number` | Post-view conversions on external websites in viral distribution. |
| `data[].viralFollows` | `number` | Follows generated in viral distribution of the ad. |
| `data[].viralFullScreenPlays` | `number` | Fullscreen video plays in viral distribution. |
| `data[].viralImpressions` | `number` | Total impressions in viral distribution of the ad. |
| `data[].viralJobApplications` | `number` | Job applications initiated in viral distribution. |
| `data[].viralJobApplyClicks` | `number` | Clicks on apply job button in viral distribution of the ad. |
| `data[].viralLandingPageClicks` | `number` | Clicks on landing page in viral distribution. |
| `data[].viralLikes` | `number` | Total likes in viral distribution of the ad. |
| `data[].viralOneClickLeadFormOpens` | `number` | One-click lead form opens in viral distribution. |
| `data[].viralOneClickLeads` | `number` | Leads generated in one click in viral distribution. |
| `data[].viralOtherEngagements` | `number` | Other engagements in viral distribution of the ad. |
| `data[].viralPostClickJobApplications` | `number` | Job applications initiated post-clicking in viral distribution. |
| `data[].viralPostClickJobApplyClicks` | `number` | Clicks on apply job button post-clicking in viral distribution. |
| `data[].viralPostClickRegistrations` | `number` | Registrations completed post-clicking in viral distribution. |
| `data[].viralPostViewJobApplications` | `number` | Job applications initiated post-viewing in viral distribution. |
| `data[].viralPostViewJobApplyClicks` | `number` | Clicks on apply job button post-viewing in viral distribution. |
| `data[].viralPostViewRegistrations` | `number` | Registrations completed post-viewing in viral distribution. |
| `data[].viralReactions` | `number` | Total reactions in viral distribution of the ad. |
| `data[].viralRegistrations` | `number` | Total registrations in viral distribution of the ad. |
| `data[].viralShares` | `number` | Total shares in viral distribution of the ad. |
| `data[].viralTotalEngagements` | `number` | Total engagements in viral distribution of the ad. |
| `data[].viralVideoCompletions` | `number` | Completions of videos in viral distribution. |
| `data[].viralVideoFirstQuartileCompletions` | `number` | First quartile completions of videos in viral distribution. |
| `data[].viralVideoMidpointCompletions` | `number` | Midpoint completions of videos in viral distribution. |
| `data[].viralVideoStarts` | `number` | Total video starts in viral distribution of the ad. |
| `data[].viralVideoThirdQuartileCompletions` | `number` | Third quartile completions of videos in viral distribution. |
| `data[].viralVideoViews` | `number` | Total views of videos in viral distribution of the ad. |
| `data[].pivot` | `string` | Pivot dimension used for this analytics record |
| `data[].sponsoredCampaign` | `string` | URN of the sponsored campaign this analytics record belongs to |

</details>

## Ad Member Seniority Analytics

### Ad Member Seniority Analytics List

Returns ad analytics data pivoted by member seniority. Provides performance metrics including clicks, impressions, spend, and engagement data grouped by member seniority.


#### CLI

```bash
airbyte-agent connectors execute --json '{
  "workspace": "<your_workspace_name>",
  "name": "linkedin-ads",
  "entity": "ad_member_seniority_analytics",
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

#### Python SDK

```python
await linkedin_ads.ad_member_seniority_analytics.list(
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
    "entity": "ad_member_seniority_analytics",
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
| `q` | `string` | Yes | LinkedIn API finder method for querying ad analytics |
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

### Ad Member Seniority Analytics Context Store Search

Search and filter ad member seniority analytics records powered by Airbyte's data sync. This often provides additional fields and operators beyond what the API natively supports, making it easier to narrow down results before performing further operations. Only available in hosted mode.

#### CLI

```bash
airbyte-agent connectors execute --json '{
  "workspace": "<your_workspace_name>",
  "name": "linkedin-ads",
  "entity": "ad_member_seniority_analytics",
  "action": "context_store_search",
  "params": {
    "query": {
      "filter": {
        "eq": {
          "actionClicks": 0.0
        }
      }
    }
  }
}'
```

#### Python SDK

```python
await linkedin_ads.ad_member_seniority_analytics.context_store_search(
    query={"filter": {"eq": {"actionClicks": 0.0}}}
)
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/integrations/connectors/{your_connector_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "ad_member_seniority_analytics",
    "action": "context_store_search",
    "params": {
        "query": {"filter": {"eq": {"actionClicks": 0.0}}}
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
| `actionClicks` | `number` | The number of clicks on action buttons in the ad. |
| `adUnitClicks` | `number` | The number of clicks on ad unit components. |
| `approximateMemberReach` | `number` | An approximation of unique ad impressions. |
| `cardClicks` | `number` | The number of clicks on interactive card elements. |
| `cardImpressions` | `number` | The number of times interactive cards were displayed. |
| `clicks` | `number` | Total number of clicks on the ad. |
| `commentLikes` | `number` | The count of likes on comments related to the ad. |
| `comments` | `number` | The number of comments on the ad. |
| `companyPageClicks` | `number` | Clicks on the company page associated with the ad. |
| `conversionValueInLocalCurrency` | `number` | Conversion value in the local currency. |
| `costInLocalCurrency` | `number` | Cost of ad campaign in the local currency. |
| `costInUsd` | `number` | Cost of ad campaign in USD. |
| `documentCompletions` | `number` | Number of completions for document views. |
| `documentFirstQuartileCompletions` | `number` | Completions for first quartile of document views. |
| `documentMidpointCompletions` | `number` | Completions for midpoint of document views. |
| `documentThirdQuartileCompletions` | `number` | Completions for third quartile of document views. |
| `downloadClicks` | `number` | Clicks on download links in the ad. |
| `end_date` | `string` | End date of the ad analytics data. |
| `externalWebsiteConversions` | `number` | Conversions that lead to external websites. |
| `externalWebsitePostClickConversions` | `number` | Post-click conversions on external websites. |
| `externalWebsitePostViewConversions` | `number` | Post-view conversions on external websites. |
| `follows` | `number` | Number of follows generated by the ad. |
| `fullScreenPlays` | `number` | Number of times videos were played in fullscreen mode. |
| `impressions` | `number` | Total number of times the ad was displayed. |
| `jobApplications` | `number` | Number of job applications initiated through the ad. |
| `jobApplyClicks` | `number` | Clicks on apply job button in the ad. |
| `landingPageClicks` | `number` | Clicks on the landing page associated with the ad. |
| `leadGenerationMailContactInfoShares` | `number` | Shares of contact information through lead generation. |
| `leadGenerationMailInterestedClicks` | `number` | Clicks on expressing interest through lead generation mail. |
| `likes` | `number` | Total likes received on the ad. |
| `oneClickLeadFormOpens` | `number` | Number of times lead forms were opened in one click. |
| `oneClickLeads` | `number` | Leads generated in one click. |
| `opens` | `number` | The number of times the ad was opened or expanded. |
| `otherEngagements` | `number` | Engagements other than clicks on the ad. |
| `pivotValues` | `array` | Values used for pivoting the analytics. |
| `string_of_pivot_values` | `string` | Comma-separated string of pivot values for this analytics record |
| `postClickJobApplications` | `number` | Job applications initiated post-clicking on the ad. |
| `postClickJobApplyClicks` | `number` | Clicks on apply job button post-clicking on the ad. |
| `postClickRegistrations` | `number` | Registrations completed post-clicking on the ad. |
| `postViewJobApplications` | `number` | Job applications initiated post-viewing the ad. |
| `postViewJobApplyClicks` | `number` | Clicks on apply job button post-viewing the ad. |
| `postViewRegistrations` | `number` | Registrations completed post-viewing the ad. |
| `reactions` | `number` | Total reactions (e.g., like, love, celebrate) on the ad. |
| `registrations` | `number` | Total registrations completed through the ad. |
| `sends` | `number` | Number of messages sent through the ad. |
| `shares` | `number` | Total shares generated by the ad. |
| `start_date` | `string` | Start date of the ad analytics data. |
| `talentLeads` | `number` | Number of leads related to talent acquisition. |
| `textUrlClicks` | `number` | Clicks on text URLs within the ad. |
| `totalEngagements` | `number` | Total number of engagements on the ad. |
| `validWorkEmailLeads` | `number` | Leads generated through valid work emails. |
| `videoCompletions` | `number` | Number of times videos were watched till completion. |
| `videoFirstQuartileCompletions` | `number` | Completions for first quartile of video views. |
| `videoMidpointCompletions` | `number` | Completions for midpoint of video views. |
| `videoStarts` | `number` | Total video starts initiated by users. |
| `videoThirdQuartileCompletions` | `number` | Completions for third quartile of video views. |
| `videoViews` | `number` | Total views of videos in the ad. |
| `viralCardClicks` | `number` | Clicks on interactive card components in viral distribution. |
| `viralCardImpressions` | `number` | Impressions of interactive cards in viral distribution. |
| `viralClicks` | `number` | Total clicks in viral distribution of the ad. |
| `viralCommentLikes` | `number` | Likes received on comments in viral distribution. |
| `viralComments` | `number` | Number of comments in viral distribution of the ad. |
| `viralCompanyPageClicks` | `number` | Clicks on the company page in viral distribution. |
| `viralDocumentCompletions` | `number` | Complete views of documents in viral distribution. |
| `viralDocumentFirstQuartileCompletions` | `number` | First quartile completions of documents in viral distribution. |
| `viralDocumentMidpointCompletions` | `number` | Midpoint completions of documents in viral distribution. |
| `viralDocumentThirdQuartileCompletions` | `number` | Third quartile completions of documents in viral distribution. |
| `viralDownloadClicks` | `number` | Clicks on downloads in viral distribution of the ad. |
| `viralExternalWebsiteConversions` | `number` | External website conversions in viral distribution. |
| `viralExternalWebsitePostClickConversions` | `number` | Post-click conversions on external websites in viral distribution. |
| `viralExternalWebsitePostViewConversions` | `number` | Post-view conversions on external websites in viral distribution. |
| `viralFollows` | `number` | Follows generated in viral distribution of the ad. |
| `viralFullScreenPlays` | `number` | Fullscreen video plays in viral distribution. |
| `viralImpressions` | `number` | Total impressions in viral distribution of the ad. |
| `viralJobApplications` | `number` | Job applications initiated in viral distribution. |
| `viralJobApplyClicks` | `number` | Clicks on apply job button in viral distribution of the ad. |
| `viralLandingPageClicks` | `number` | Clicks on landing page in viral distribution. |
| `viralLikes` | `number` | Total likes in viral distribution of the ad. |
| `viralOneClickLeadFormOpens` | `number` | One-click lead form opens in viral distribution. |
| `viralOneClickLeads` | `number` | Leads generated in one click in viral distribution. |
| `viralOtherEngagements` | `number` | Other engagements in viral distribution of the ad. |
| `viralPostClickJobApplications` | `number` | Job applications initiated post-clicking in viral distribution. |
| `viralPostClickJobApplyClicks` | `number` | Clicks on apply job button post-clicking in viral distribution. |
| `viralPostClickRegistrations` | `number` | Registrations completed post-clicking in viral distribution. |
| `viralPostViewJobApplications` | `number` | Job applications initiated post-viewing in viral distribution. |
| `viralPostViewJobApplyClicks` | `number` | Clicks on apply job button post-viewing in viral distribution. |
| `viralPostViewRegistrations` | `number` | Registrations completed post-viewing in viral distribution. |
| `viralReactions` | `number` | Total reactions in viral distribution of the ad. |
| `viralRegistrations` | `number` | Total registrations in viral distribution of the ad. |
| `viralShares` | `number` | Total shares in viral distribution of the ad. |
| `viralTotalEngagements` | `number` | Total engagements in viral distribution of the ad. |
| `viralVideoCompletions` | `number` | Completions of videos in viral distribution. |
| `viralVideoFirstQuartileCompletions` | `number` | First quartile completions of videos in viral distribution. |
| `viralVideoMidpointCompletions` | `number` | Midpoint completions of videos in viral distribution. |
| `viralVideoStarts` | `number` | Total video starts in viral distribution of the ad. |
| `viralVideoThirdQuartileCompletions` | `number` | Third quartile completions of videos in viral distribution. |
| `viralVideoViews` | `number` | Total views of videos in viral distribution of the ad. |
| `pivot` | `string` | Pivot dimension used for this analytics record |
| `sponsoredCampaign` | `string` | URN of the sponsored campaign this analytics record belongs to |

<details>
<summary><b>Response Schema</b></summary>

| Field Name | Type | Description |
|------------|------|-------------|
| `data` | `array` | List of matching records |
| `meta` | `object` | Pagination metadata |
| `meta.has_more` | `boolean` | Whether additional pages are available |
| `meta.cursor` | `string \| null` | Cursor for next page of results |
| `meta.took_ms` | `number \| null` | Query execution time in milliseconds |
| `data[].actionClicks` | `number` | The number of clicks on action buttons in the ad. |
| `data[].adUnitClicks` | `number` | The number of clicks on ad unit components. |
| `data[].approximateMemberReach` | `number` | An approximation of unique ad impressions. |
| `data[].cardClicks` | `number` | The number of clicks on interactive card elements. |
| `data[].cardImpressions` | `number` | The number of times interactive cards were displayed. |
| `data[].clicks` | `number` | Total number of clicks on the ad. |
| `data[].commentLikes` | `number` | The count of likes on comments related to the ad. |
| `data[].comments` | `number` | The number of comments on the ad. |
| `data[].companyPageClicks` | `number` | Clicks on the company page associated with the ad. |
| `data[].conversionValueInLocalCurrency` | `number` | Conversion value in the local currency. |
| `data[].costInLocalCurrency` | `number` | Cost of ad campaign in the local currency. |
| `data[].costInUsd` | `number` | Cost of ad campaign in USD. |
| `data[].documentCompletions` | `number` | Number of completions for document views. |
| `data[].documentFirstQuartileCompletions` | `number` | Completions for first quartile of document views. |
| `data[].documentMidpointCompletions` | `number` | Completions for midpoint of document views. |
| `data[].documentThirdQuartileCompletions` | `number` | Completions for third quartile of document views. |
| `data[].downloadClicks` | `number` | Clicks on download links in the ad. |
| `data[].end_date` | `string` | End date of the ad analytics data. |
| `data[].externalWebsiteConversions` | `number` | Conversions that lead to external websites. |
| `data[].externalWebsitePostClickConversions` | `number` | Post-click conversions on external websites. |
| `data[].externalWebsitePostViewConversions` | `number` | Post-view conversions on external websites. |
| `data[].follows` | `number` | Number of follows generated by the ad. |
| `data[].fullScreenPlays` | `number` | Number of times videos were played in fullscreen mode. |
| `data[].impressions` | `number` | Total number of times the ad was displayed. |
| `data[].jobApplications` | `number` | Number of job applications initiated through the ad. |
| `data[].jobApplyClicks` | `number` | Clicks on apply job button in the ad. |
| `data[].landingPageClicks` | `number` | Clicks on the landing page associated with the ad. |
| `data[].leadGenerationMailContactInfoShares` | `number` | Shares of contact information through lead generation. |
| `data[].leadGenerationMailInterestedClicks` | `number` | Clicks on expressing interest through lead generation mail. |
| `data[].likes` | `number` | Total likes received on the ad. |
| `data[].oneClickLeadFormOpens` | `number` | Number of times lead forms were opened in one click. |
| `data[].oneClickLeads` | `number` | Leads generated in one click. |
| `data[].opens` | `number` | The number of times the ad was opened or expanded. |
| `data[].otherEngagements` | `number` | Engagements other than clicks on the ad. |
| `data[].pivotValues` | `array` | Values used for pivoting the analytics. |
| `data[].string_of_pivot_values` | `string` | Comma-separated string of pivot values for this analytics record |
| `data[].postClickJobApplications` | `number` | Job applications initiated post-clicking on the ad. |
| `data[].postClickJobApplyClicks` | `number` | Clicks on apply job button post-clicking on the ad. |
| `data[].postClickRegistrations` | `number` | Registrations completed post-clicking on the ad. |
| `data[].postViewJobApplications` | `number` | Job applications initiated post-viewing the ad. |
| `data[].postViewJobApplyClicks` | `number` | Clicks on apply job button post-viewing the ad. |
| `data[].postViewRegistrations` | `number` | Registrations completed post-viewing the ad. |
| `data[].reactions` | `number` | Total reactions (e.g., like, love, celebrate) on the ad. |
| `data[].registrations` | `number` | Total registrations completed through the ad. |
| `data[].sends` | `number` | Number of messages sent through the ad. |
| `data[].shares` | `number` | Total shares generated by the ad. |
| `data[].start_date` | `string` | Start date of the ad analytics data. |
| `data[].talentLeads` | `number` | Number of leads related to talent acquisition. |
| `data[].textUrlClicks` | `number` | Clicks on text URLs within the ad. |
| `data[].totalEngagements` | `number` | Total number of engagements on the ad. |
| `data[].validWorkEmailLeads` | `number` | Leads generated through valid work emails. |
| `data[].videoCompletions` | `number` | Number of times videos were watched till completion. |
| `data[].videoFirstQuartileCompletions` | `number` | Completions for first quartile of video views. |
| `data[].videoMidpointCompletions` | `number` | Completions for midpoint of video views. |
| `data[].videoStarts` | `number` | Total video starts initiated by users. |
| `data[].videoThirdQuartileCompletions` | `number` | Completions for third quartile of video views. |
| `data[].videoViews` | `number` | Total views of videos in the ad. |
| `data[].viralCardClicks` | `number` | Clicks on interactive card components in viral distribution. |
| `data[].viralCardImpressions` | `number` | Impressions of interactive cards in viral distribution. |
| `data[].viralClicks` | `number` | Total clicks in viral distribution of the ad. |
| `data[].viralCommentLikes` | `number` | Likes received on comments in viral distribution. |
| `data[].viralComments` | `number` | Number of comments in viral distribution of the ad. |
| `data[].viralCompanyPageClicks` | `number` | Clicks on the company page in viral distribution. |
| `data[].viralDocumentCompletions` | `number` | Complete views of documents in viral distribution. |
| `data[].viralDocumentFirstQuartileCompletions` | `number` | First quartile completions of documents in viral distribution. |
| `data[].viralDocumentMidpointCompletions` | `number` | Midpoint completions of documents in viral distribution. |
| `data[].viralDocumentThirdQuartileCompletions` | `number` | Third quartile completions of documents in viral distribution. |
| `data[].viralDownloadClicks` | `number` | Clicks on downloads in viral distribution of the ad. |
| `data[].viralExternalWebsiteConversions` | `number` | External website conversions in viral distribution. |
| `data[].viralExternalWebsitePostClickConversions` | `number` | Post-click conversions on external websites in viral distribution. |
| `data[].viralExternalWebsitePostViewConversions` | `number` | Post-view conversions on external websites in viral distribution. |
| `data[].viralFollows` | `number` | Follows generated in viral distribution of the ad. |
| `data[].viralFullScreenPlays` | `number` | Fullscreen video plays in viral distribution. |
| `data[].viralImpressions` | `number` | Total impressions in viral distribution of the ad. |
| `data[].viralJobApplications` | `number` | Job applications initiated in viral distribution. |
| `data[].viralJobApplyClicks` | `number` | Clicks on apply job button in viral distribution of the ad. |
| `data[].viralLandingPageClicks` | `number` | Clicks on landing page in viral distribution. |
| `data[].viralLikes` | `number` | Total likes in viral distribution of the ad. |
| `data[].viralOneClickLeadFormOpens` | `number` | One-click lead form opens in viral distribution. |
| `data[].viralOneClickLeads` | `number` | Leads generated in one click in viral distribution. |
| `data[].viralOtherEngagements` | `number` | Other engagements in viral distribution of the ad. |
| `data[].viralPostClickJobApplications` | `number` | Job applications initiated post-clicking in viral distribution. |
| `data[].viralPostClickJobApplyClicks` | `number` | Clicks on apply job button post-clicking in viral distribution. |
| `data[].viralPostClickRegistrations` | `number` | Registrations completed post-clicking in viral distribution. |
| `data[].viralPostViewJobApplications` | `number` | Job applications initiated post-viewing in viral distribution. |
| `data[].viralPostViewJobApplyClicks` | `number` | Clicks on apply job button post-viewing in viral distribution. |
| `data[].viralPostViewRegistrations` | `number` | Registrations completed post-viewing in viral distribution. |
| `data[].viralReactions` | `number` | Total reactions in viral distribution of the ad. |
| `data[].viralRegistrations` | `number` | Total registrations in viral distribution of the ad. |
| `data[].viralShares` | `number` | Total shares in viral distribution of the ad. |
| `data[].viralTotalEngagements` | `number` | Total engagements in viral distribution of the ad. |
| `data[].viralVideoCompletions` | `number` | Completions of videos in viral distribution. |
| `data[].viralVideoFirstQuartileCompletions` | `number` | First quartile completions of videos in viral distribution. |
| `data[].viralVideoMidpointCompletions` | `number` | Midpoint completions of videos in viral distribution. |
| `data[].viralVideoStarts` | `number` | Total video starts in viral distribution of the ad. |
| `data[].viralVideoThirdQuartileCompletions` | `number` | Third quartile completions of videos in viral distribution. |
| `data[].viralVideoViews` | `number` | Total views of videos in viral distribution of the ad. |
| `data[].pivot` | `string` | Pivot dimension used for this analytics record |
| `data[].sponsoredCampaign` | `string` | URN of the sponsored campaign this analytics record belongs to |

</details>

## Lead Forms

### Lead Forms List

Returns a list of lead generation forms owned by a sponsored ad account

#### CLI

```bash
airbyte-agent connectors execute --json '{
  "workspace": "<your_workspace_name>",
  "name": "linkedin-ads",
  "entity": "lead_forms",
  "action": "list",
  "params": {
    "q": "<str>",
    "owner": "<str>"
  }
}'
```

#### Python SDK

```python
await linkedin_ads.lead_forms.list(
    q="<str>",
    owner="<str>"
)
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/integrations/connectors/{your_connector_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "lead_forms",
    "action": "list",
    "params": {
        "q": "<str>",
        "owner": "<str>"
    }
}'
```


#### Parameters

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `q` | `string` | Yes | LinkedIn API finder method for querying lead forms by owner |
| `owner` | `string` | Yes | Owner of the lead forms, e.g. (sponsoredAccount:urn%3Ali%3AsponsoredAccount%3A123456) |
| `count` | `integer` | No | Number of items per page |
| `start` | `integer` | No | Offset for pagination |


<details>
<summary><b>Response Schema</b></summary>

#### Records

| Field Name | Type | Description |
|------------|------|-------------|
| `id` | `integer` |  |
| `name` | `null \| string` |  |
| `owner` | `null \| object` |  |
| `state` | `null \| string` |  |
| `content` | `null \| object` |  |
| `created` | `null \| integer` |  |
| `lastModified` | `null \| integer` |  |
| `creationLocale` | `null \| object` |  |
| `hiddenFields` | `null \| array` |  |
| `reviewInfo` | `null \| object` |  |
| `versionId` | `null \| integer` |  |
| `versionTag` | `null \| string` |  |


#### Meta

| Field Name | Type | Description |
|------------|------|-------------|
| `start` | `integer` |  |
| `count` | `integer` |  |
| `total` | `integer` |  |

</details>

### Lead Forms Context Store Search

Search and filter lead forms records powered by Airbyte's data sync. This often provides additional fields and operators beyond what the API natively supports, making it easier to narrow down results before performing further operations. Only available in hosted mode.

#### CLI

```bash
airbyte-agent connectors execute --json '{
  "workspace": "<your_workspace_name>",
  "name": "linkedin-ads",
  "entity": "lead_forms",
  "action": "context_store_search",
  "params": {
    "query": {
      "filter": {
        "eq": {
          "id": 0
        }
      }
    }
  }
}'
```

#### Python SDK

```python
await linkedin_ads.lead_forms.context_store_search(
    query={"filter": {"eq": {"id": 0}}}
)
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/integrations/connectors/{your_connector_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "lead_forms",
    "action": "context_store_search",
    "params": {
        "query": {"filter": {"eq": {"id": 0}}}
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
| `id` | `integer` | Numerical identifier for the form. |
| `name` | `string` | Name of the Lead Form provided by the owner. |
| `owner` | `object` | URN that identifies the owner of the Lead Form.
It's a Union of sponsoredAccount and organization.
sponsoredAccount is an URN of SponsoredAccountUrn that indicates the account of the advertiser.
organization is an URN of OrganizationUrn that indicates the company account of the marketer.
 |
| `state` | `string` | Information about the current state of the Lead Form. |
| `content` | `object` | Content of the Lead Form which will be displayed to the viewer. |
| `created` | `integer` | An epoch time corresponding to the creation of the form. |
| `lastModified` | `integer` | An epoch time corresponding to the last modified of of the form. |
| `creationLocale` | `object` | Locale of the entity.
This field serves as the preferred locale for all fields within the Lead Form with an object type that is capable of localization, such as MultiLocaleString.
 |
| `hiddenFields` | `array` | Hidden fields used by the owner to track key attributes of the form that generated the lead.
The field is empty if the owner chooses to not append any tracking attributes to the Lead Form.
 |
| `reviewInfo` | `object` | Latest information about the content review of the Lead Form.
It will not be present if the form has not been reviewed by the review pipeline.
 |
| `versionId` | `integer` | The version ID of the form. This is a derived field and is generated on the server side. |
| `versionTag` | `string` | The number of times the form has been modified. |

<details>
<summary><b>Response Schema</b></summary>

| Field Name | Type | Description |
|------------|------|-------------|
| `data` | `array` | List of matching records |
| `meta` | `object` | Pagination metadata |
| `meta.has_more` | `boolean` | Whether additional pages are available |
| `meta.cursor` | `string \| null` | Cursor for next page of results |
| `meta.took_ms` | `number \| null` | Query execution time in milliseconds |
| `data[].id` | `integer` | Numerical identifier for the form. |
| `data[].name` | `string` | Name of the Lead Form provided by the owner. |
| `data[].owner` | `object` | URN that identifies the owner of the Lead Form.
It's a Union of sponsoredAccount and organization.
sponsoredAccount is an URN of SponsoredAccountUrn that indicates the account of the advertiser.
organization is an URN of OrganizationUrn that indicates the company account of the marketer.
 |
| `data[].state` | `string` | Information about the current state of the Lead Form. |
| `data[].content` | `object` | Content of the Lead Form which will be displayed to the viewer. |
| `data[].created` | `integer` | An epoch time corresponding to the creation of the form. |
| `data[].lastModified` | `integer` | An epoch time corresponding to the last modified of of the form. |
| `data[].creationLocale` | `object` | Locale of the entity.
This field serves as the preferred locale for all fields within the Lead Form with an object type that is capable of localization, such as MultiLocaleString.
 |
| `data[].hiddenFields` | `array` | Hidden fields used by the owner to track key attributes of the form that generated the lead.
The field is empty if the owner chooses to not append any tracking attributes to the Lead Form.
 |
| `data[].reviewInfo` | `object` | Latest information about the content review of the Lead Form.
It will not be present if the form has not been reviewed by the review pipeline.
 |
| `data[].versionId` | `integer` | The version ID of the form. This is a derived field and is generated on the server side. |
| `data[].versionTag` | `string` | The number of times the form has been modified. |

</details>

## Lead Form Responses

### Lead Form Responses List

Returns a list of lead form responses submitted to forms owned by a sponsored ad account

#### CLI

```bash
airbyte-agent connectors execute --json '{
  "workspace": "<your_workspace_name>",
  "name": "linkedin-ads",
  "entity": "lead_form_responses",
  "action": "list",
  "params": {
    "q": "<str>",
    "owner": "<str>",
    "leadType": "<str>"
  }
}'
```

#### Python SDK

```python
await linkedin_ads.lead_form_responses.list(
    q="<str>",
    owner="<str>",
    lead_type="<str>"
)
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/integrations/connectors/{your_connector_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "lead_form_responses",
    "action": "list",
    "params": {
        "q": "<str>",
        "owner": "<str>",
        "leadType": "<str>"
    }
}'
```


#### Parameters

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `q` | `string` | Yes | LinkedIn API finder method for querying lead form responses by owner |
| `owner` | `string` | Yes | Owner of the lead form responses, e.g. (sponsoredAccount:urn%3Ali%3AsponsoredAccount%3A123456) |
| `leadType` | `string` | Yes | Type of leads to return, e.g. (leadType:SPONSORED) |
| `count` | `integer` | No | Number of items per page |
| `start` | `integer` | No | Offset for pagination |


<details>
<summary><b>Response Schema</b></summary>

#### Records

| Field Name | Type | Description |
|------------|------|-------------|
| `id` | `null \| string` |  |
| `leadType` | `null \| string` |  |
| `form` | `null \| object` |  |
| `owner` | `null \| object` |  |
| `ownerInfo` | `null \| object` |  |
| `leadMetadata` | `null \| object` |  |
| `leadMetadataInfo` | `null \| object` |  |
| `associatedEntity` | `null \| object` |  |
| `associatedEntityInfo` | `null \| object` |  |
| `submittedAt` | `null \| integer` |  |
| `responseId` | `null \| object` |  |
| `formResponse` | `null \| object` |  |
| `testLead` | `null \| boolean` |  |
| `submitter` | `null \| string` |  |
| `versionedLeadGenFormUrn` | `null \| string` |  |


#### Meta

| Field Name | Type | Description |
|------------|------|-------------|
| `start` | `integer` |  |
| `count` | `integer` |  |
| `total` | `integer` |  |

</details>

### Lead Form Responses Context Store Search

Search and filter lead form responses records powered by Airbyte's data sync. This often provides additional fields and operators beyond what the API natively supports, making it easier to narrow down results before performing further operations. Only available in hosted mode.

#### CLI

```bash
airbyte-agent connectors execute --json '{
  "workspace": "<your_workspace_name>",
  "name": "linkedin-ads",
  "entity": "lead_form_responses",
  "action": "context_store_search",
  "params": {
    "query": {
      "filter": {
        "eq": {
          "id": "<str>"
        }
      }
    }
  }
}'
```

#### Python SDK

```python
await linkedin_ads.lead_form_responses.context_store_search(
    query={"filter": {"eq": {"id": "<str>"}}}
)
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/integrations/connectors/{your_connector_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "lead_form_responses",
    "action": "context_store_search",
    "params": {
        "query": {"filter": {"eq": {"id": "<str>"}}}
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
| `id` | `string` | Unique id to identify the Lead Form Response. |
| `leadType` | `string` | Type of the lead representing the origination of the lead. |
| `form` | `object` | URN identifying which form this FormResponse belongs to. |
| `owner` | `object` | Owner of this Lead Form Response.
It is a Union of sponsoredAccount and organization.
sponsoredAccount is an URN of SponsoredAccountUrn that indicates the ad account of the advertiser.
organization is an URN of OrganizationUrn that indicates the company page of the advertiser.
 |
| `ownerInfo` | `object` | Record containing entity info that owns this Lead Form Response. It's a optional Union of sponsoredAccountInfo and organizationInfo. |
| `leadMetadata` | `object` | Metadata of a lead. This field is optional for test leads and other use cases where sponsored lead metadata (e.g. campaign) may not be relevant. If there is no value, the field is not returned. |
| `leadMetadataInfo` | `object` | Record containing a subset of fields resolved on demand from the lead metadata references (e.g. campaign name , campaign type). If there is no value, an empty object is returned. |
| `associatedEntity` | `object` | URN identifying which entity the lead is associated with. This field is optional for test leads and other use cases where leads don't have any associatedEntity. If there is no value, the field is not returned. |
| `associatedEntityInfo` | `object` | Record containing useful fields (creative status, ugc reference etc.) resolved on demand from the associated entity object. If there is no value, an empty object is returned. |
| `submittedAt` | `integer` | An epoch timestamp that recording when the form response was submitted. |
| `responseId` | `object` | The unique identifier for the form response generated in the front-end when a submitter submits the response. |
| `formResponse` | `object` | Answers provided by the form submitter. |
| `testLead` | `boolean` | Whether this is a test lead created for testing purposes. |
| `submitter` | `string` | From version 202408 onwards, Guest Leads (when a user submits a form without being logged in) submitted to lead forms, submitter field is treated as a null field and omitted from the JSON response.
For non-guest leads, the submitter field will still be included in the response and will provide the person's URN. Ex: "submitter": "urn:li:person:MpGcnvaU_p".	Yes
 |
| `versionedLeadGenFormUrn` | `string` | URN identifying which form this FormResponse belongs to. |

<details>
<summary><b>Response Schema</b></summary>

| Field Name | Type | Description |
|------------|------|-------------|
| `data` | `array` | List of matching records |
| `meta` | `object` | Pagination metadata |
| `meta.has_more` | `boolean` | Whether additional pages are available |
| `meta.cursor` | `string \| null` | Cursor for next page of results |
| `meta.took_ms` | `number \| null` | Query execution time in milliseconds |
| `data[].id` | `string` | Unique id to identify the Lead Form Response. |
| `data[].leadType` | `string` | Type of the lead representing the origination of the lead. |
| `data[].form` | `object` | URN identifying which form this FormResponse belongs to. |
| `data[].owner` | `object` | Owner of this Lead Form Response.
It is a Union of sponsoredAccount and organization.
sponsoredAccount is an URN of SponsoredAccountUrn that indicates the ad account of the advertiser.
organization is an URN of OrganizationUrn that indicates the company page of the advertiser.
 |
| `data[].ownerInfo` | `object` | Record containing entity info that owns this Lead Form Response. It's a optional Union of sponsoredAccountInfo and organizationInfo. |
| `data[].leadMetadata` | `object` | Metadata of a lead. This field is optional for test leads and other use cases where sponsored lead metadata (e.g. campaign) may not be relevant. If there is no value, the field is not returned. |
| `data[].leadMetadataInfo` | `object` | Record containing a subset of fields resolved on demand from the lead metadata references (e.g. campaign name , campaign type). If there is no value, an empty object is returned. |
| `data[].associatedEntity` | `object` | URN identifying which entity the lead is associated with. This field is optional for test leads and other use cases where leads don't have any associatedEntity. If there is no value, the field is not returned. |
| `data[].associatedEntityInfo` | `object` | Record containing useful fields (creative status, ugc reference etc.) resolved on demand from the associated entity object. If there is no value, an empty object is returned. |
| `data[].submittedAt` | `integer` | An epoch timestamp that recording when the form response was submitted. |
| `data[].responseId` | `object` | The unique identifier for the form response generated in the front-end when a submitter submits the response. |
| `data[].formResponse` | `object` | Answers provided by the form submitter. |
| `data[].testLead` | `boolean` | Whether this is a test lead created for testing purposes. |
| `data[].submitter` | `string` | From version 202408 onwards, Guest Leads (when a user submits a form without being logged in) submitted to lead forms, submitter field is treated as a null field and omitted from the JSON response.
For non-guest leads, the submitter field will still be included in the response and will provide the person's URN. Ex: "submitter": "urn:li:person:MpGcnvaU_p".	Yes
 |
| `data[].versionedLeadGenFormUrn` | `string` | URN identifying which form this FormResponse belongs to. |

</details>

