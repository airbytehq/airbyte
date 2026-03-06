# Snapchat-Marketing full reference

This is the full reference documentation for the Snapchat-Marketing agent connector.

## Supported entities and actions

The Snapchat-Marketing connector supports the following entities and actions.

| Entity | Actions |
|--------|---------|
| Organizations | [List](#organizations-list), [Get](#organizations-get), [Search](#organizations-search) |
| Adaccounts | [List](#adaccounts-list), [Get](#adaccounts-get), [Search](#adaccounts-search) |
| Campaigns | [List](#campaigns-list), [Get](#campaigns-get), [Search](#campaigns-search) |
| Adsquads | [List](#adsquads-list), [Get](#adsquads-get), [Search](#adsquads-search) |
| Ads | [List](#ads-list), [Get](#ads-get), [Search](#ads-search) |
| Creatives | [List](#creatives-list), [Get](#creatives-get), [Search](#creatives-search) |
| Media | [List](#media-list), [Get](#media-get), [Search](#media-search) |
| Segments | [List](#segments-list), [Get](#segments-get), [Search](#segments-search) |

## Organizations

### Organizations List

Returns the organizations the authenticated user belongs to

#### Python SDK

```python
await snapchat_marketing.organizations.list()
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/integrations/connectors/{your_connector_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "organizations",
    "action": "list"
}'
```



<details>
<summary><b>Response Schema</b></summary>

#### Records

| Field Name | Type | Description |
|------------|------|-------------|
| `id` | `string` |  |
| `name` | `string` |  |
| `type` | `string` |  |
| `state` | `string` |  |
| `address_line_1` | `string` |  |
| `administrative_district_level_1` | `string` |  |
| `locality` | `string` |  |
| `postal_code` | `string` |  |
| `country` | `string` |  |
| `contact_name` | `string` |  |
| `contact_email` | `string` |  |
| `contact_phone` | `string` |  |
| `contact_phone_optin` | `boolean` |  |
| `accepted_term_version` | `string` |  |
| `configuration_settings` | `object` |  |
| `my_display_name` | `string` |  |
| `my_invited_email` | `string` |  |
| `my_member_id` | `string` |  |
| `roles` | `array<string>` |  |
| `createdByCaller` | `boolean` |  |
| `is_agency` | `boolean` |  |
| `verification_request_id` | `string` |  |
| `demand_source` | `string` |  |
| `created_at` | `string` |  |
| `updated_at` | `string` |  |


#### Meta

| Field Name | Type | Description |
|------------|------|-------------|
| `next_link` | `string` |  |

</details>

### Organizations Get

Get a single organization by ID

#### Python SDK

```python
await snapchat_marketing.organizations.get(
    id="<str>"
)
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/integrations/connectors/{your_connector_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "organizations",
    "action": "get",
    "params": {
        "id": "<str>"
    }
}'
```


#### Parameters

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `id` | `string` | Yes | Organization ID |


### Organizations Search

Search and filter organizations records powered by Airbyte's data sync. This often provides additional fields and operators beyond what the API natively supports, making it easier to narrow down results before performing further operations. Only available in hosted mode.

#### Python SDK

```python
await snapchat_marketing.organizations.search(
    query={"filter": {"eq": {"accepted_term_version": "<str>"}}}
)
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/integrations/connectors/{your_connector_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "organizations",
    "action": "search",
    "params": {
        "query": {"filter": {"eq": {"accepted_term_version": "<str>"}}}
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
| `accepted_term_version` | `string` | Version of accepted terms |
| `address_line_1` | `string` | Street address |
| `administrative_district_level_1` | `string` | State or province |
| `configuration_settings` | `object` | Organization configuration settings |
| `contact_email` | `string` | Contact email address |
| `contact_name` | `string` | Contact person name |
| `contact_phone` | `string` | Contact phone number |
| `contact_phone_optin` | `boolean` | Whether the contact opted in for phone communications |
| `country` | `string` | Country code |
| `createdByCaller` | `boolean` | Whether the organization was created by the caller |
| `created_at` | `string` | Creation timestamp |
| `id` | `string` | Unique organization identifier |
| `locality` | `string` | City or locality |
| `my_display_name` | `string` | Display name of the authenticated user in the organization |
| `my_invited_email` | `string` | Email used to invite the authenticated user |
| `my_member_id` | `string` | Member ID of the authenticated user |
| `name` | `string` | Organization name |
| `postal_code` | `string` | Postal code |
| `roles` | `array` | Roles of the authenticated user in this organization |
| `state` | `string` | Organization state |
| `type` | `string` | Organization type |
| `updated_at` | `string` | Last update timestamp |

<details>
<summary><b>Response Schema</b></summary>

| Field Name | Type | Description |
|------------|------|-------------|
| `data` | `array` | List of matching records |
| `meta` | `object` | Pagination metadata |
| `meta.has_more` | `boolean` | Whether additional pages are available |
| `meta.cursor` | `string \| null` | Cursor for next page of results |
| `meta.took_ms` | `number \| null` | Query execution time in milliseconds |
| `data[].accepted_term_version` | `string` | Version of accepted terms |
| `data[].address_line_1` | `string` | Street address |
| `data[].administrative_district_level_1` | `string` | State or province |
| `data[].configuration_settings` | `object` | Organization configuration settings |
| `data[].contact_email` | `string` | Contact email address |
| `data[].contact_name` | `string` | Contact person name |
| `data[].contact_phone` | `string` | Contact phone number |
| `data[].contact_phone_optin` | `boolean` | Whether the contact opted in for phone communications |
| `data[].country` | `string` | Country code |
| `data[].createdByCaller` | `boolean` | Whether the organization was created by the caller |
| `data[].created_at` | `string` | Creation timestamp |
| `data[].id` | `string` | Unique organization identifier |
| `data[].locality` | `string` | City or locality |
| `data[].my_display_name` | `string` | Display name of the authenticated user in the organization |
| `data[].my_invited_email` | `string` | Email used to invite the authenticated user |
| `data[].my_member_id` | `string` | Member ID of the authenticated user |
| `data[].name` | `string` | Organization name |
| `data[].postal_code` | `string` | Postal code |
| `data[].roles` | `array` | Roles of the authenticated user in this organization |
| `data[].state` | `string` | Organization state |
| `data[].type` | `string` | Organization type |
| `data[].updated_at` | `string` | Last update timestamp |

</details>

## Adaccounts

### Adaccounts List

Returns ad accounts belonging to an organization

#### Python SDK

```python
await snapchat_marketing.adaccounts.list(
    organization_id="<str>"
)
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/integrations/connectors/{your_connector_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "adaccounts",
    "action": "list",
    "params": {
        "organization_id": "<str>"
    }
}'
```


#### Parameters

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `organization_id` | `string` | Yes | Organization ID |


<details>
<summary><b>Response Schema</b></summary>

#### Records

| Field Name | Type | Description |
|------------|------|-------------|
| `id` | `string` |  |
| `name` | `string` |  |
| `type` | `string` |  |
| `status` | `string` |  |
| `organization_id` | `string` |  |
| `advertiser_organization_id` | `string` |  |
| `currency` | `string` |  |
| `timezone` | `string` |  |
| `billing_type` | `string` |  |
| `billing_center_id` | `string` |  |
| `agency_representing_client` | `boolean` |  |
| `client_paying_invoices` | `boolean` |  |
| `funding_source_ids` | `array<string>` |  |
| `regulations` | `object` |  |
| `created_at` | `string` |  |
| `updated_at` | `string` |  |


#### Meta

| Field Name | Type | Description |
|------------|------|-------------|
| `next_link` | `string` |  |

</details>

### Adaccounts Get

Get a single ad account by ID

#### Python SDK

```python
await snapchat_marketing.adaccounts.get(
    id="<str>"
)
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/integrations/connectors/{your_connector_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "adaccounts",
    "action": "get",
    "params": {
        "id": "<str>"
    }
}'
```


#### Parameters

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `id` | `string` | Yes | Ad Account ID |


### Adaccounts Search

Search and filter adaccounts records powered by Airbyte's data sync. This often provides additional fields and operators beyond what the API natively supports, making it easier to narrow down results before performing further operations. Only available in hosted mode.

#### Python SDK

```python
await snapchat_marketing.adaccounts.search(
    query={"filter": {"eq": {"advertiser_organization_id": "<str>"}}}
)
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/integrations/connectors/{your_connector_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "adaccounts",
    "action": "search",
    "params": {
        "query": {"filter": {"eq": {"advertiser_organization_id": "<str>"}}}
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
| `advertiser_organization_id` | `string` | Advertiser organization ID |
| `agency_representing_client` | `boolean` | Whether the account is managed by an agency |
| `billing_center_id` | `string` | Billing center ID |
| `billing_type` | `string` | Billing type |
| `client_paying_invoices` | `boolean` | Whether the client pays invoices directly |
| `created_at` | `string` | Creation timestamp |
| `currency` | `string` | Account currency code |
| `funding_source_ids` | `array` | Associated funding source IDs |
| `id` | `string` | Unique ad account identifier |
| `name` | `string` | Ad account name |
| `organization_id` | `string` | Parent organization ID |
| `regulations` | `object` | Regulatory settings |
| `status` | `string` | Ad account status |
| `timezone` | `string` | Account timezone |
| `type` | `string` | Ad account type |
| `updated_at` | `string` | Last update timestamp |

<details>
<summary><b>Response Schema</b></summary>

| Field Name | Type | Description |
|------------|------|-------------|
| `data` | `array` | List of matching records |
| `meta` | `object` | Pagination metadata |
| `meta.has_more` | `boolean` | Whether additional pages are available |
| `meta.cursor` | `string \| null` | Cursor for next page of results |
| `meta.took_ms` | `number \| null` | Query execution time in milliseconds |
| `data[].advertiser_organization_id` | `string` | Advertiser organization ID |
| `data[].agency_representing_client` | `boolean` | Whether the account is managed by an agency |
| `data[].billing_center_id` | `string` | Billing center ID |
| `data[].billing_type` | `string` | Billing type |
| `data[].client_paying_invoices` | `boolean` | Whether the client pays invoices directly |
| `data[].created_at` | `string` | Creation timestamp |
| `data[].currency` | `string` | Account currency code |
| `data[].funding_source_ids` | `array` | Associated funding source IDs |
| `data[].id` | `string` | Unique ad account identifier |
| `data[].name` | `string` | Ad account name |
| `data[].organization_id` | `string` | Parent organization ID |
| `data[].regulations` | `object` | Regulatory settings |
| `data[].status` | `string` | Ad account status |
| `data[].timezone` | `string` | Account timezone |
| `data[].type` | `string` | Ad account type |
| `data[].updated_at` | `string` | Last update timestamp |

</details>

## Campaigns

### Campaigns List

Returns campaigns belonging to an ad account

#### Python SDK

```python
await snapchat_marketing.campaigns.list(
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
| `ad_account_id` | `string` | Yes | Ad Account ID |


<details>
<summary><b>Response Schema</b></summary>

#### Records

| Field Name | Type | Description |
|------------|------|-------------|
| `id` | `string` |  |
| `name` | `string` |  |
| `ad_account_id` | `string` |  |
| `status` | `string` |  |
| `objective` | `string` |  |
| `buy_model` | `string` |  |
| `creation_state` | `string` |  |
| `start_time` | `string` |  |
| `delivery_status` | `array<string>` |  |
| `objective_v2_properties` | `object` |  |
| `pacing_properties_version` | `integer` |  |
| `created_at` | `string` |  |
| `updated_at` | `string` |  |


#### Meta

| Field Name | Type | Description |
|------------|------|-------------|
| `next_link` | `string` |  |

</details>

### Campaigns Get

Get a single campaign by ID

#### Python SDK

```python
await snapchat_marketing.campaigns.get(
    id="<str>"
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
        "id": "<str>"
    }
}'
```


#### Parameters

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `id` | `string` | Yes | Campaign ID |


### Campaigns Search

Search and filter campaigns records powered by Airbyte's data sync. This often provides additional fields and operators beyond what the API natively supports, making it easier to narrow down results before performing further operations. Only available in hosted mode.

#### Python SDK

```python
await snapchat_marketing.campaigns.search(
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
| `ad_account_id` | `string` | Parent ad account ID |
| `buy_model` | `string` | Buy model type |
| `created_at` | `string` | Creation timestamp |
| `creation_state` | `string` | Creation state |
| `delivery_status` | `array` | Delivery status messages |
| `id` | `string` | Unique campaign identifier |
| `name` | `string` | Campaign name |
| `objective` | `string` | Campaign objective |
| `start_time` | `string` | Campaign start time |
| `status` | `string` | Campaign status |
| `updated_at` | `string` | Last update timestamp |

<details>
<summary><b>Response Schema</b></summary>

| Field Name | Type | Description |
|------------|------|-------------|
| `data` | `array` | List of matching records |
| `meta` | `object` | Pagination metadata |
| `meta.has_more` | `boolean` | Whether additional pages are available |
| `meta.cursor` | `string \| null` | Cursor for next page of results |
| `meta.took_ms` | `number \| null` | Query execution time in milliseconds |
| `data[].ad_account_id` | `string` | Parent ad account ID |
| `data[].buy_model` | `string` | Buy model type |
| `data[].created_at` | `string` | Creation timestamp |
| `data[].creation_state` | `string` | Creation state |
| `data[].delivery_status` | `array` | Delivery status messages |
| `data[].id` | `string` | Unique campaign identifier |
| `data[].name` | `string` | Campaign name |
| `data[].objective` | `string` | Campaign objective |
| `data[].start_time` | `string` | Campaign start time |
| `data[].status` | `string` | Campaign status |
| `data[].updated_at` | `string` | Last update timestamp |

</details>

## Adsquads

### Adsquads List

Returns ad squads belonging to an ad account

#### Python SDK

```python
await snapchat_marketing.adsquads.list(
    ad_account_id="<str>"
)
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/integrations/connectors/{your_connector_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "adsquads",
    "action": "list",
    "params": {
        "ad_account_id": "<str>"
    }
}'
```


#### Parameters

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `ad_account_id` | `string` | Yes | Ad Account ID |


<details>
<summary><b>Response Schema</b></summary>

#### Records

| Field Name | Type | Description |
|------------|------|-------------|
| `id` | `string` |  |
| `name` | `string` |  |
| `type` | `string` |  |
| `campaign_id` | `string` |  |
| `status` | `string` |  |
| `auto_bid` | `boolean` |  |
| `bid_strategy` | `string` |  |
| `billing_event` | `string` |  |
| `child_ad_type` | `string` |  |
| `creation_state` | `string` |  |
| `daily_budget_micro` | `integer` |  |
| `lifetime_budget_micro` | `integer` |  |
| `delivery_constraint` | `string` |  |
| `delivery_properties_version` | `integer` |  |
| `delivery_status` | `array<string>` |  |
| `end_time` | `string` |  |
| `start_time` | `string` |  |
| `forced_view_setting` | `string` |  |
| `optimization_goal` | `string` |  |
| `pacing_type` | `string` |  |
| `placement` | `string` |  |
| `target_bid` | `boolean` |  |
| `targeting` | `object` |  |
| `targeting_reach_status` | `string` |  |
| `skadnetwork_properties` | `object` |  |
| `event_sources` | `object` |  |
| `created_at` | `string` |  |
| `updated_at` | `string` |  |


#### Meta

| Field Name | Type | Description |
|------------|------|-------------|
| `next_link` | `string` |  |

</details>

### Adsquads Get

Get a single ad squad by ID

#### Python SDK

```python
await snapchat_marketing.adsquads.get(
    id="<str>"
)
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/integrations/connectors/{your_connector_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "adsquads",
    "action": "get",
    "params": {
        "id": "<str>"
    }
}'
```


#### Parameters

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `id` | `string` | Yes | Ad Squad ID |


### Adsquads Search

Search and filter adsquads records powered by Airbyte's data sync. This often provides additional fields and operators beyond what the API natively supports, making it easier to narrow down results before performing further operations. Only available in hosted mode.

#### Python SDK

```python
await snapchat_marketing.adsquads.search(
    query={"filter": {"eq": {"auto_bid": True}}}
)
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/integrations/connectors/{your_connector_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "adsquads",
    "action": "search",
    "params": {
        "query": {"filter": {"eq": {"auto_bid": True}}}
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
| `auto_bid` | `boolean` | Whether auto bidding is enabled |
| `bid_strategy` | `string` | Bid strategy |
| `billing_event` | `string` | Billing event type |
| `campaign_id` | `string` | Parent campaign ID |
| `child_ad_type` | `string` | Child ad type |
| `created_at` | `string` | Creation timestamp |
| `creation_state` | `string` | Creation state |
| `daily_budget_micro` | `integer` | Daily budget in micro-currency |
| `delivery_constraint` | `string` | Delivery constraint |
| `delivery_properties_version` | `integer` | Delivery properties version |
| `delivery_status` | `array` | Delivery status messages |
| `end_time` | `string` | Ad squad end time |
| `event_sources` | `object` | Event sources configuration |
| `forced_view_setting` | `string` | Forced view setting |
| `id` | `string` | Unique ad squad identifier |
| `lifetime_budget_micro` | `integer` | Lifetime budget in micro-currency |
| `name` | `string` | Ad squad name |
| `optimization_goal` | `string` | Optimization goal |
| `pacing_type` | `string` | Pacing type |
| `placement` | `string` | Placement type |
| `skadnetwork_properties` | `object` | SKAdNetwork properties |
| `start_time` | `string` | Ad squad start time |
| `status` | `string` | Ad squad status |
| `target_bid` | `boolean` | Whether target bid is enabled |
| `targeting` | `object` | Targeting specification |
| `targeting_reach_status` | `string` | Targeting reach status |
| `type` | `string` | Ad squad type |
| `updated_at` | `string` | Last update timestamp |

<details>
<summary><b>Response Schema</b></summary>

| Field Name | Type | Description |
|------------|------|-------------|
| `data` | `array` | List of matching records |
| `meta` | `object` | Pagination metadata |
| `meta.has_more` | `boolean` | Whether additional pages are available |
| `meta.cursor` | `string \| null` | Cursor for next page of results |
| `meta.took_ms` | `number \| null` | Query execution time in milliseconds |
| `data[].auto_bid` | `boolean` | Whether auto bidding is enabled |
| `data[].bid_strategy` | `string` | Bid strategy |
| `data[].billing_event` | `string` | Billing event type |
| `data[].campaign_id` | `string` | Parent campaign ID |
| `data[].child_ad_type` | `string` | Child ad type |
| `data[].created_at` | `string` | Creation timestamp |
| `data[].creation_state` | `string` | Creation state |
| `data[].daily_budget_micro` | `integer` | Daily budget in micro-currency |
| `data[].delivery_constraint` | `string` | Delivery constraint |
| `data[].delivery_properties_version` | `integer` | Delivery properties version |
| `data[].delivery_status` | `array` | Delivery status messages |
| `data[].end_time` | `string` | Ad squad end time |
| `data[].event_sources` | `object` | Event sources configuration |
| `data[].forced_view_setting` | `string` | Forced view setting |
| `data[].id` | `string` | Unique ad squad identifier |
| `data[].lifetime_budget_micro` | `integer` | Lifetime budget in micro-currency |
| `data[].name` | `string` | Ad squad name |
| `data[].optimization_goal` | `string` | Optimization goal |
| `data[].pacing_type` | `string` | Pacing type |
| `data[].placement` | `string` | Placement type |
| `data[].skadnetwork_properties` | `object` | SKAdNetwork properties |
| `data[].start_time` | `string` | Ad squad start time |
| `data[].status` | `string` | Ad squad status |
| `data[].target_bid` | `boolean` | Whether target bid is enabled |
| `data[].targeting` | `object` | Targeting specification |
| `data[].targeting_reach_status` | `string` | Targeting reach status |
| `data[].type` | `string` | Ad squad type |
| `data[].updated_at` | `string` | Last update timestamp |

</details>

## Ads

### Ads List

Returns ads belonging to an ad account

#### Python SDK

```python
await snapchat_marketing.ads.list(
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
| `ad_account_id` | `string` | Yes | Ad Account ID |


<details>
<summary><b>Response Schema</b></summary>

#### Records

| Field Name | Type | Description |
|------------|------|-------------|
| `id` | `string` |  |
| `name` | `string` |  |
| `type` | `string` |  |
| `ad_squad_id` | `string` |  |
| `creative_id` | `string` |  |
| `status` | `string` |  |
| `render_type` | `string` |  |
| `review_status` | `string` |  |
| `review_status_reasons` | `array<string>` |  |
| `delivery_status` | `array<string>` |  |
| `created_at` | `string` |  |
| `updated_at` | `string` |  |


#### Meta

| Field Name | Type | Description |
|------------|------|-------------|
| `next_link` | `string` |  |

</details>

### Ads Get

Get a single ad by ID

#### Python SDK

```python
await snapchat_marketing.ads.get(
    id="<str>"
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
        "id": "<str>"
    }
}'
```


#### Parameters

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `id` | `string` | Yes | Ad ID |


### Ads Search

Search and filter ads records powered by Airbyte's data sync. This often provides additional fields and operators beyond what the API natively supports, making it easier to narrow down results before performing further operations. Only available in hosted mode.

#### Python SDK

```python
await snapchat_marketing.ads.search(
    query={"filter": {"eq": {"ad_squad_id": "<str>"}}}
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
        "query": {"filter": {"eq": {"ad_squad_id": "<str>"}}}
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
| `ad_squad_id` | `string` | Parent ad squad ID |
| `created_at` | `string` | Creation timestamp |
| `creative_id` | `string` | Associated creative ID |
| `delivery_status` | `array` | Delivery status messages |
| `id` | `string` | Unique ad identifier |
| `name` | `string` | Ad name |
| `render_type` | `string` | Render type |
| `review_status` | `string` | Review status |
| `review_status_reasons` | `array` | Reasons for review status |
| `status` | `string` | Ad status |
| `type` | `string` | Ad type |
| `updated_at` | `string` | Last update timestamp |

<details>
<summary><b>Response Schema</b></summary>

| Field Name | Type | Description |
|------------|------|-------------|
| `data` | `array` | List of matching records |
| `meta` | `object` | Pagination metadata |
| `meta.has_more` | `boolean` | Whether additional pages are available |
| `meta.cursor` | `string \| null` | Cursor for next page of results |
| `meta.took_ms` | `number \| null` | Query execution time in milliseconds |
| `data[].ad_squad_id` | `string` | Parent ad squad ID |
| `data[].created_at` | `string` | Creation timestamp |
| `data[].creative_id` | `string` | Associated creative ID |
| `data[].delivery_status` | `array` | Delivery status messages |
| `data[].id` | `string` | Unique ad identifier |
| `data[].name` | `string` | Ad name |
| `data[].render_type` | `string` | Render type |
| `data[].review_status` | `string` | Review status |
| `data[].review_status_reasons` | `array` | Reasons for review status |
| `data[].status` | `string` | Ad status |
| `data[].type` | `string` | Ad type |
| `data[].updated_at` | `string` | Last update timestamp |

</details>

## Creatives

### Creatives List

Returns creatives belonging to an ad account

#### Python SDK

```python
await snapchat_marketing.creatives.list(
    ad_account_id="<str>"
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
        "ad_account_id": "<str>"
    }
}'
```


#### Parameters

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `ad_account_id` | `string` | Yes | Ad Account ID |


<details>
<summary><b>Response Schema</b></summary>

#### Records

| Field Name | Type | Description |
|------------|------|-------------|
| `id` | `string` |  |
| `name` | `string` |  |
| `type` | `string` |  |
| `ad_account_id` | `string` |  |
| `ad_product` | `string` |  |
| `brand_name` | `string` |  |
| `call_to_action` | `string` |  |
| `headline` | `string` |  |
| `render_type` | `string` |  |
| `review_status` | `string` |  |
| `review_status_details` | `string` |  |
| `shareable` | `boolean` |  |
| `forced_view_eligibility` | `string` |  |
| `packaging_status` | `string` |  |
| `top_snap_crop_position` | `string` |  |
| `top_snap_media_id` | `string` |  |
| `ad_to_place_properties` | `object` |  |
| `web_view_properties` | `object` |  |
| `created_at` | `string` |  |
| `updated_at` | `string` |  |


#### Meta

| Field Name | Type | Description |
|------------|------|-------------|
| `next_link` | `string` |  |

</details>

### Creatives Get

Get a single creative by ID

#### Python SDK

```python
await snapchat_marketing.creatives.get(
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
        "id": "<str>"
    }
}'
```


#### Parameters

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `id` | `string` | Yes | Creative ID |


### Creatives Search

Search and filter creatives records powered by Airbyte's data sync. This often provides additional fields and operators beyond what the API natively supports, making it easier to narrow down results before performing further operations. Only available in hosted mode.

#### Python SDK

```python
await snapchat_marketing.creatives.search(
    query={"filter": {"eq": {"ad_account_id": "<str>"}}}
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
| `ad_account_id` | `string` | Parent ad account ID |
| `ad_product` | `string` | Ad product type |
| `ad_to_place_properties` | `object` | Ad-to-place properties |
| `brand_name` | `string` | Brand name displayed in the creative |
| `call_to_action` | `string` | Call to action text |
| `created_at` | `string` | Creation timestamp |
| `forced_view_eligibility` | `string` | Forced view eligibility status |
| `headline` | `string` | Creative headline |
| `id` | `string` | Unique creative identifier |
| `name` | `string` | Creative name |
| `packaging_status` | `string` | Packaging status |
| `render_type` | `string` | Render type |
| `review_status` | `string` | Review status |
| `review_status_details` | `string` | Details about the review status |
| `shareable` | `boolean` | Whether the creative is shareable |
| `top_snap_crop_position` | `string` | Top snap crop position |
| `top_snap_media_id` | `string` | Top snap media ID |
| `type` | `string` | Creative type |
| `updated_at` | `string` | Last update timestamp |
| `web_view_properties` | `object` | Web view properties |

<details>
<summary><b>Response Schema</b></summary>

| Field Name | Type | Description |
|------------|------|-------------|
| `data` | `array` | List of matching records |
| `meta` | `object` | Pagination metadata |
| `meta.has_more` | `boolean` | Whether additional pages are available |
| `meta.cursor` | `string \| null` | Cursor for next page of results |
| `meta.took_ms` | `number \| null` | Query execution time in milliseconds |
| `data[].ad_account_id` | `string` | Parent ad account ID |
| `data[].ad_product` | `string` | Ad product type |
| `data[].ad_to_place_properties` | `object` | Ad-to-place properties |
| `data[].brand_name` | `string` | Brand name displayed in the creative |
| `data[].call_to_action` | `string` | Call to action text |
| `data[].created_at` | `string` | Creation timestamp |
| `data[].forced_view_eligibility` | `string` | Forced view eligibility status |
| `data[].headline` | `string` | Creative headline |
| `data[].id` | `string` | Unique creative identifier |
| `data[].name` | `string` | Creative name |
| `data[].packaging_status` | `string` | Packaging status |
| `data[].render_type` | `string` | Render type |
| `data[].review_status` | `string` | Review status |
| `data[].review_status_details` | `string` | Details about the review status |
| `data[].shareable` | `boolean` | Whether the creative is shareable |
| `data[].top_snap_crop_position` | `string` | Top snap crop position |
| `data[].top_snap_media_id` | `string` | Top snap media ID |
| `data[].type` | `string` | Creative type |
| `data[].updated_at` | `string` | Last update timestamp |
| `data[].web_view_properties` | `object` | Web view properties |

</details>

## Media

### Media List

Returns media belonging to an ad account

#### Python SDK

```python
await snapchat_marketing.media.list(
    ad_account_id="<str>"
)
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/integrations/connectors/{your_connector_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "media",
    "action": "list",
    "params": {
        "ad_account_id": "<str>"
    }
}'
```


#### Parameters

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `ad_account_id` | `string` | Yes | Ad Account ID |


<details>
<summary><b>Response Schema</b></summary>

#### Records

| Field Name | Type | Description |
|------------|------|-------------|
| `id` | `string` |  |
| `name` | `string` |  |
| `type` | `string` |  |
| `ad_account_id` | `string` |  |
| `media_status` | `string` |  |
| `file_name` | `string` |  |
| `file_size_in_bytes` | `integer` |  |
| `duration_in_seconds` | `number` |  |
| `hash` | `string` |  |
| `download_link` | `string` |  |
| `is_demo_media` | `boolean` |  |
| `visibility` | `string` |  |
| `media_usages` | `array<string>` |  |
| `image_metadata` | `object` |  |
| `video_metadata` | `object` |  |
| `created_at` | `string` |  |
| `updated_at` | `string` |  |


#### Meta

| Field Name | Type | Description |
|------------|------|-------------|
| `next_link` | `string` |  |

</details>

### Media Get

Get a single media item by ID

#### Python SDK

```python
await snapchat_marketing.media.get(
    id="<str>"
)
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/integrations/connectors/{your_connector_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "media",
    "action": "get",
    "params": {
        "id": "<str>"
    }
}'
```


#### Parameters

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `id` | `string` | Yes | Media ID |


### Media Search

Search and filter media records powered by Airbyte's data sync. This often provides additional fields and operators beyond what the API natively supports, making it easier to narrow down results before performing further operations. Only available in hosted mode.

#### Python SDK

```python
await snapchat_marketing.media.search(
    query={"filter": {"eq": {"ad_account_id": "<str>"}}}
)
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/integrations/connectors/{your_connector_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "media",
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
| `ad_account_id` | `string` | Parent ad account ID |
| `created_at` | `string` | Creation timestamp |
| `download_link` | `string` | Download URL for the media |
| `duration_in_seconds` | `number` | Duration in seconds for video media |
| `file_name` | `string` | Original file name |
| `file_size_in_bytes` | `integer` | File size in bytes |
| `hash` | `string` | Media file hash |
| `id` | `string` | Unique media identifier |
| `image_metadata` | `object` | Image-specific metadata |
| `is_demo_media` | `boolean` | Whether this is demo media |
| `media_status` | `string` | Media processing status |
| `media_usages` | `array` | Where the media is used |
| `name` | `string` | Media name |
| `type` | `string` | Media type |
| `updated_at` | `string` | Last update timestamp |
| `video_metadata` | `object` | Video-specific metadata |
| `visibility` | `string` | Media visibility setting |

<details>
<summary><b>Response Schema</b></summary>

| Field Name | Type | Description |
|------------|------|-------------|
| `data` | `array` | List of matching records |
| `meta` | `object` | Pagination metadata |
| `meta.has_more` | `boolean` | Whether additional pages are available |
| `meta.cursor` | `string \| null` | Cursor for next page of results |
| `meta.took_ms` | `number \| null` | Query execution time in milliseconds |
| `data[].ad_account_id` | `string` | Parent ad account ID |
| `data[].created_at` | `string` | Creation timestamp |
| `data[].download_link` | `string` | Download URL for the media |
| `data[].duration_in_seconds` | `number` | Duration in seconds for video media |
| `data[].file_name` | `string` | Original file name |
| `data[].file_size_in_bytes` | `integer` | File size in bytes |
| `data[].hash` | `string` | Media file hash |
| `data[].id` | `string` | Unique media identifier |
| `data[].image_metadata` | `object` | Image-specific metadata |
| `data[].is_demo_media` | `boolean` | Whether this is demo media |
| `data[].media_status` | `string` | Media processing status |
| `data[].media_usages` | `array` | Where the media is used |
| `data[].name` | `string` | Media name |
| `data[].type` | `string` | Media type |
| `data[].updated_at` | `string` | Last update timestamp |
| `data[].video_metadata` | `object` | Video-specific metadata |
| `data[].visibility` | `string` | Media visibility setting |

</details>

## Segments

### Segments List

Returns audience segments belonging to an ad account

#### Python SDK

```python
await snapchat_marketing.segments.list(
    ad_account_id="<str>"
)
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/integrations/connectors/{your_connector_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "segments",
    "action": "list",
    "params": {
        "ad_account_id": "<str>"
    }
}'
```


#### Parameters

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `ad_account_id` | `string` | Yes | Ad Account ID |


<details>
<summary><b>Response Schema</b></summary>

#### Records

| Field Name | Type | Description |
|------------|------|-------------|
| `id` | `string` |  |
| `name` | `string` |  |
| `description` | `string` |  |
| `ad_account_id` | `string` |  |
| `source_ad_account_id` | `string` |  |
| `organization_id` | `string` |  |
| `status` | `string` |  |
| `source_type` | `string` |  |
| `targetable_status` | `string` |  |
| `upload_status` | `string` |  |
| `retention_in_days` | `integer` |  |
| `approximate_number_users` | `integer` |  |
| `visible_to` | `array<string>` |  |
| `created_at` | `string` |  |
| `updated_at` | `string` |  |


#### Meta

| Field Name | Type | Description |
|------------|------|-------------|
| `next_link` | `string` |  |

</details>

### Segments Get

Get a single audience segment by ID

#### Python SDK

```python
await snapchat_marketing.segments.get(
    id="<str>"
)
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/integrations/connectors/{your_connector_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "segments",
    "action": "get",
    "params": {
        "id": "<str>"
    }
}'
```


#### Parameters

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `id` | `string` | Yes | Segment ID |


### Segments Search

Search and filter segments records powered by Airbyte's data sync. This often provides additional fields and operators beyond what the API natively supports, making it easier to narrow down results before performing further operations. Only available in hosted mode.

#### Python SDK

```python
await snapchat_marketing.segments.search(
    query={"filter": {"eq": {"ad_account_id": "<str>"}}}
)
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/integrations/connectors/{your_connector_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "segments",
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
| `ad_account_id` | `string` | Parent ad account ID |
| `approximate_number_users` | `integer` | Approximate number of users in the segment |
| `created_at` | `string` | Creation timestamp |
| `description` | `string` | Segment description |
| `id` | `string` | Unique segment identifier |
| `name` | `string` | Segment name |
| `organization_id` | `string` | Parent organization ID |
| `retention_in_days` | `integer` | Data retention period in days |
| `source_type` | `string` | Segment source type |
| `status` | `string` | Segment status |
| `targetable_status` | `string` | Whether the segment is targetable |
| `updated_at` | `string` | Last update timestamp |
| `upload_status` | `string` | Upload processing status |
| `visible_to` | `array` | Visibility settings |

<details>
<summary><b>Response Schema</b></summary>

| Field Name | Type | Description |
|------------|------|-------------|
| `data` | `array` | List of matching records |
| `meta` | `object` | Pagination metadata |
| `meta.has_more` | `boolean` | Whether additional pages are available |
| `meta.cursor` | `string \| null` | Cursor for next page of results |
| `meta.took_ms` | `number \| null` | Query execution time in milliseconds |
| `data[].ad_account_id` | `string` | Parent ad account ID |
| `data[].approximate_number_users` | `integer` | Approximate number of users in the segment |
| `data[].created_at` | `string` | Creation timestamp |
| `data[].description` | `string` | Segment description |
| `data[].id` | `string` | Unique segment identifier |
| `data[].name` | `string` | Segment name |
| `data[].organization_id` | `string` | Parent organization ID |
| `data[].retention_in_days` | `integer` | Data retention period in days |
| `data[].source_type` | `string` | Segment source type |
| `data[].status` | `string` | Segment status |
| `data[].targetable_status` | `string` | Whether the segment is targetable |
| `data[].updated_at` | `string` | Last update timestamp |
| `data[].upload_status` | `string` | Upload processing status |
| `data[].visible_to` | `array` | Visibility settings |

</details>

