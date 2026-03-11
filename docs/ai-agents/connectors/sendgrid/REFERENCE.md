# Sendgrid full reference

This is the full reference documentation for the Sendgrid agent connector.

## Supported entities and actions

The Sendgrid connector supports the following entities and actions.

| Entity | Actions |
|--------|---------|
| Contacts | [List](#contacts-list), [Get](#contacts-get), [Search](#contacts-search) |
| Lists | [List](#lists-list), [Get](#lists-get), [Search](#lists-search) |
| Segments | [List](#segments-list), [Get](#segments-get), [Search](#segments-search) |
| Campaigns | [List](#campaigns-list), [Search](#campaigns-search) |
| Singlesends | [List](#singlesends-list), [Get](#singlesends-get), [Search](#singlesends-search) |
| Templates | [List](#templates-list), [Get](#templates-get), [Search](#templates-search) |
| Singlesend Stats | [List](#singlesend-stats-list), [Search](#singlesend-stats-search) |
| Bounces | [List](#bounces-list), [Search](#bounces-search) |
| Blocks | [List](#blocks-list), [Search](#blocks-search) |
| Spam Reports | [List](#spam-reports-list) |
| Invalid Emails | [List](#invalid-emails-list), [Search](#invalid-emails-search) |
| Global Suppressions | [List](#global-suppressions-list), [Search](#global-suppressions-search) |
| Suppression Groups | [List](#suppression-groups-list), [Get](#suppression-groups-get), [Search](#suppression-groups-search) |
| Suppression Group Members | [List](#suppression-group-members-list), [Search](#suppression-group-members-search) |

## Contacts

### Contacts List

Returns a sample of contacts. Use the export endpoint for full lists.

#### Python SDK

```python
await sendgrid.contacts.list()
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/integrations/connectors/{your_connector_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "contacts",
    "action": "list"
}'
```



<details>
<summary><b>Response Schema</b></summary>

#### Records

| Field Name | Type | Description |
|------------|------|-------------|
| `id` | `string` |  |
| `email` | `null \| string` |  |
| `first_name` | `null \| string` |  |
| `last_name` | `null \| string` |  |
| `unique_name` | `null \| string` |  |
| `alternate_emails` | `null \| array` |  |
| `address_line_1` | `null \| string` |  |
| `address_line_2` | `null \| string` |  |
| `city` | `null \| string` |  |
| `state_province_region` | `null \| string` |  |
| `country` | `null \| string` |  |
| `postal_code` | `null \| string` |  |
| `phone_number` | `null \| string` |  |
| `whatsapp` | `null \| string` |  |
| `line` | `null \| string` |  |
| `facebook` | `null \| string` |  |
| `list_ids` | `null \| array` |  |
| `segment_ids` | `null \| array` |  |
| `custom_fields` | `null \| object` |  |
| `created_at` | `null \| string` |  |
| `updated_at` | `null \| string` |  |


</details>

### Contacts Get

Returns the full details and all fields for the specified contact.

#### Python SDK

```python
await sendgrid.contacts.get(
    id="<str>"
)
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/integrations/connectors/{your_connector_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "contacts",
    "action": "get",
    "params": {
        "id": "<str>"
    }
}'
```


#### Parameters

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `id` | `string` | Yes | The ID of the contact |


<details>
<summary><b>Response Schema</b></summary>

#### Records

| Field Name | Type | Description |
|------------|------|-------------|
| `id` | `string` |  |
| `email` | `null \| string` |  |
| `first_name` | `null \| string` |  |
| `last_name` | `null \| string` |  |
| `unique_name` | `null \| string` |  |
| `alternate_emails` | `null \| array` |  |
| `address_line_1` | `null \| string` |  |
| `address_line_2` | `null \| string` |  |
| `city` | `null \| string` |  |
| `state_province_region` | `null \| string` |  |
| `country` | `null \| string` |  |
| `postal_code` | `null \| string` |  |
| `phone_number` | `null \| string` |  |
| `whatsapp` | `null \| string` |  |
| `line` | `null \| string` |  |
| `facebook` | `null \| string` |  |
| `list_ids` | `null \| array` |  |
| `segment_ids` | `null \| array` |  |
| `custom_fields` | `null \| object` |  |
| `created_at` | `null \| string` |  |
| `updated_at` | `null \| string` |  |


</details>

### Contacts Search

Search and filter contacts records powered by Airbyte's data sync. This often provides additional fields and operators beyond what the API natively supports, making it easier to narrow down results before performing further operations. Only available in hosted mode.

#### Python SDK

```python
await sendgrid.contacts.search(
    query={"filter": {"eq": {"address_line_1": "<str>"}}}
)
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/integrations/connectors/{your_connector_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "contacts",
    "action": "search",
    "params": {
        "query": {"filter": {"eq": {"address_line_1": "<str>"}}}
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
| `address_line_1` | `string` | Address line 1 |
| `address_line_2` | `string` | Address line 2 |
| `alternate_emails` | `array` | Alternate email addresses |
| `city` | `string` | City |
| `contact_id` | `string` | Unique contact identifier used by Airbyte |
| `country` | `string` | Country |
| `created_at` | `string` | When the contact was created |
| `custom_fields` | `object` | Custom field values |
| `email` | `string` | Contact email address |
| `facebook` | `string` | Facebook ID |
| `first_name` | `string` | Contact first name |
| `last_name` | `string` | Contact last name |
| `line` | `string` | LINE ID |
| `list_ids` | `array` | IDs of lists the contact belongs to |
| `phone_number` | `string` | Phone number |
| `postal_code` | `string` | Postal code |
| `state_province_region` | `string` | State, province, or region |
| `unique_name` | `string` | Unique name for the contact |
| `updated_at` | `string` | When the contact was last updated |
| `whatsapp` | `string` | WhatsApp number |

<details>
<summary><b>Response Schema</b></summary>

| Field Name | Type | Description |
|------------|------|-------------|
| `data` | `array` | List of matching records |
| `meta` | `object` | Pagination metadata |
| `meta.has_more` | `boolean` | Whether additional pages are available |
| `meta.cursor` | `string \| null` | Cursor for next page of results |
| `meta.took_ms` | `number \| null` | Query execution time in milliseconds |
| `data[].address_line_1` | `string` | Address line 1 |
| `data[].address_line_2` | `string` | Address line 2 |
| `data[].alternate_emails` | `array` | Alternate email addresses |
| `data[].city` | `string` | City |
| `data[].contact_id` | `string` | Unique contact identifier used by Airbyte |
| `data[].country` | `string` | Country |
| `data[].created_at` | `string` | When the contact was created |
| `data[].custom_fields` | `object` | Custom field values |
| `data[].email` | `string` | Contact email address |
| `data[].facebook` | `string` | Facebook ID |
| `data[].first_name` | `string` | Contact first name |
| `data[].last_name` | `string` | Contact last name |
| `data[].line` | `string` | LINE ID |
| `data[].list_ids` | `array` | IDs of lists the contact belongs to |
| `data[].phone_number` | `string` | Phone number |
| `data[].postal_code` | `string` | Postal code |
| `data[].state_province_region` | `string` | State, province, or region |
| `data[].unique_name` | `string` | Unique name for the contact |
| `data[].updated_at` | `string` | When the contact was last updated |
| `data[].whatsapp` | `string` | WhatsApp number |

</details>

## Lists

### Lists List

Returns all marketing contact lists.

#### Python SDK

```python
await sendgrid.lists.list()
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/integrations/connectors/{your_connector_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "lists",
    "action": "list"
}'
```


#### Parameters

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `page_size` | `integer` | No | Maximum number of lists to return |


<details>
<summary><b>Response Schema</b></summary>

#### Records

| Field Name | Type | Description |
|------------|------|-------------|
| `id` | `string` |  |
| `name` | `string` |  |
| `contact_count` | `integer` |  |
| `_metadata` | `null \| object` |  |


#### Meta

| Field Name | Type | Description |
|------------|------|-------------|
| `next` | `null \| string` |  |

</details>

### Lists Get

Returns a specific marketing list by ID.

#### Python SDK

```python
await sendgrid.lists.get(
    id="<str>"
)
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/integrations/connectors/{your_connector_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "lists",
    "action": "get",
    "params": {
        "id": "<str>"
    }
}'
```


#### Parameters

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `id` | `string` | Yes | The ID of the list |


<details>
<summary><b>Response Schema</b></summary>

#### Records

| Field Name | Type | Description |
|------------|------|-------------|
| `id` | `string` |  |
| `name` | `string` |  |
| `contact_count` | `integer` |  |
| `_metadata` | `null \| object` |  |


</details>

### Lists Search

Search and filter lists records powered by Airbyte's data sync. This often provides additional fields and operators beyond what the API natively supports, making it easier to narrow down results before performing further operations. Only available in hosted mode.

#### Python SDK

```python
await sendgrid.lists.search(
    query={"filter": {"eq": {"_metadata": {}}}}
)
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/integrations/connectors/{your_connector_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "lists",
    "action": "search",
    "params": {
        "query": {"filter": {"eq": {"_metadata": {}}}}
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
| `_metadata` | `object` | Metadata about the list resource |
| `contact_count` | `integer` | Number of contacts in the list |
| `id` | `string` | Unique list identifier |
| `name` | `string` | Name of the list |

<details>
<summary><b>Response Schema</b></summary>

| Field Name | Type | Description |
|------------|------|-------------|
| `data` | `array` | List of matching records |
| `meta` | `object` | Pagination metadata |
| `meta.has_more` | `boolean` | Whether additional pages are available |
| `meta.cursor` | `string \| null` | Cursor for next page of results |
| `meta.took_ms` | `number \| null` | Query execution time in milliseconds |
| `data[]._metadata` | `object` | Metadata about the list resource |
| `data[].contact_count` | `integer` | Number of contacts in the list |
| `data[].id` | `string` | Unique list identifier |
| `data[].name` | `string` | Name of the list |

</details>

## Segments

### Segments List

Returns all segments (v2).

#### Python SDK

```python
await sendgrid.segments.list()
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/integrations/connectors/{your_connector_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "segments",
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
| `contacts_count` | `integer` |  |
| `created_at` | `null \| string` |  |
| `updated_at` | `null \| string` |  |
| `sample_updated_at` | `null \| string` |  |
| `next_sample_update` | `null \| string` |  |
| `parent_list_ids` | `null \| array` |  |
| `query_version` | `string` |  |
| `status` | `null \| object` |  |


</details>

### Segments Get

Returns a specific segment by ID.

#### Python SDK

```python
await sendgrid.segments.get(
    segment_id="<str>"
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
        "segment_id": "<str>"
    }
}'
```


#### Parameters

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `segment_id` | `string` | Yes | The ID of the segment |


<details>
<summary><b>Response Schema</b></summary>

#### Records

| Field Name | Type | Description |
|------------|------|-------------|
| `id` | `string` |  |
| `name` | `string` |  |
| `contacts_count` | `integer` |  |
| `created_at` | `null \| string` |  |
| `updated_at` | `null \| string` |  |
| `sample_updated_at` | `null \| string` |  |
| `next_sample_update` | `null \| string` |  |
| `parent_list_ids` | `null \| array` |  |
| `query_version` | `string` |  |
| `status` | `null \| object` |  |


</details>

### Segments Search

Search and filter segments records powered by Airbyte's data sync. This often provides additional fields and operators beyond what the API natively supports, making it easier to narrow down results before performing further operations. Only available in hosted mode.

#### Python SDK

```python
await sendgrid.segments.search(
    query={"filter": {"eq": {"contacts_count": 0}}}
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
        "query": {"filter": {"eq": {"contacts_count": 0}}}
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
| `contacts_count` | `integer` | Number of contacts in the segment |
| `created_at` | `string` | When the segment was created |
| `id` | `string` | Unique segment identifier |
| `name` | `string` | Segment name |
| `next_sample_update` | `string` | When the next sample update will occur |
| `parent_list_ids` | `array` | IDs of parent lists |
| `query_version` | `string` | Query version used |
| `sample_updated_at` | `string` | When the sample was last updated |
| `status` | `object` | Segment status details |
| `updated_at` | `string` | When the segment was last updated |

<details>
<summary><b>Response Schema</b></summary>

| Field Name | Type | Description |
|------------|------|-------------|
| `data` | `array` | List of matching records |
| `meta` | `object` | Pagination metadata |
| `meta.has_more` | `boolean` | Whether additional pages are available |
| `meta.cursor` | `string \| null` | Cursor for next page of results |
| `meta.took_ms` | `number \| null` | Query execution time in milliseconds |
| `data[].contacts_count` | `integer` | Number of contacts in the segment |
| `data[].created_at` | `string` | When the segment was created |
| `data[].id` | `string` | Unique segment identifier |
| `data[].name` | `string` | Segment name |
| `data[].next_sample_update` | `string` | When the next sample update will occur |
| `data[].parent_list_ids` | `array` | IDs of parent lists |
| `data[].query_version` | `string` | Query version used |
| `data[].sample_updated_at` | `string` | When the sample was last updated |
| `data[].status` | `object` | Segment status details |
| `data[].updated_at` | `string` | When the segment was last updated |

</details>

## Campaigns

### Campaigns List

Returns all marketing campaigns.

#### Python SDK

```python
await sendgrid.campaigns.list()
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/integrations/connectors/{your_connector_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "campaigns",
    "action": "list"
}'
```


#### Parameters

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `page_size` | `integer` | No | Maximum number of campaigns to return per page |


<details>
<summary><b>Response Schema</b></summary>

#### Records

| Field Name | Type | Description |
|------------|------|-------------|
| `id` | `string` |  |
| `name` | `string` |  |
| `status` | `string` |  |
| `channels` | `null \| array` |  |
| `is_abtest` | `boolean` |  |
| `created_at` | `null \| string` |  |
| `updated_at` | `null \| string` |  |


#### Meta

| Field Name | Type | Description |
|------------|------|-------------|
| `next` | `null \| string` |  |

</details>

### Campaigns Search

Search and filter campaigns records powered by Airbyte's data sync. This often provides additional fields and operators beyond what the API natively supports, making it easier to narrow down results before performing further operations. Only available in hosted mode.

#### Python SDK

```python
await sendgrid.campaigns.search(
    query={"filter": {"eq": {"channels": []}}}
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
        "query": {"filter": {"eq": {"channels": []}}}
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
| `channels` | `array` | Channels for this campaign |
| `created_at` | `string` | When the campaign was created |
| `id` | `string` | Unique campaign identifier |
| `is_abtest` | `boolean` | Whether this campaign is an A/B test |
| `name` | `string` | Campaign name |
| `status` | `string` | Campaign status |
| `updated_at` | `string` | When the campaign was last updated |

<details>
<summary><b>Response Schema</b></summary>

| Field Name | Type | Description |
|------------|------|-------------|
| `data` | `array` | List of matching records |
| `meta` | `object` | Pagination metadata |
| `meta.has_more` | `boolean` | Whether additional pages are available |
| `meta.cursor` | `string \| null` | Cursor for next page of results |
| `meta.took_ms` | `number \| null` | Query execution time in milliseconds |
| `data[].channels` | `array` | Channels for this campaign |
| `data[].created_at` | `string` | When the campaign was created |
| `data[].id` | `string` | Unique campaign identifier |
| `data[].is_abtest` | `boolean` | Whether this campaign is an A/B test |
| `data[].name` | `string` | Campaign name |
| `data[].status` | `string` | Campaign status |
| `data[].updated_at` | `string` | When the campaign was last updated |

</details>

## Singlesends

### Singlesends List

Returns all single sends.

#### Python SDK

```python
await sendgrid.singlesends.list()
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/integrations/connectors/{your_connector_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "singlesends",
    "action": "list"
}'
```


#### Parameters

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `page_size` | `integer` | No | Maximum number of single sends to return per page |


<details>
<summary><b>Response Schema</b></summary>

#### Records

| Field Name | Type | Description |
|------------|------|-------------|
| `id` | `string` |  |
| `name` | `string` |  |
| `status` | `string` |  |
| `categories` | `null \| array` |  |
| `send_at` | `null \| string` |  |
| `send_to` | `null \| object` |  |
| `email_config` | `null \| object` |  |
| `is_abtest` | `boolean` |  |
| `created_at` | `string` |  |
| `updated_at` | `string` |  |


#### Meta

| Field Name | Type | Description |
|------------|------|-------------|
| `next` | `null \| string` |  |

</details>

### Singlesends Get

Returns details about one single send.

#### Python SDK

```python
await sendgrid.singlesends.get(
    id="<str>"
)
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/integrations/connectors/{your_connector_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "singlesends",
    "action": "get",
    "params": {
        "id": "<str>"
    }
}'
```


#### Parameters

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `id` | `string` | Yes | The ID of the single send |


<details>
<summary><b>Response Schema</b></summary>

#### Records

| Field Name | Type | Description |
|------------|------|-------------|
| `id` | `string` |  |
| `name` | `string` |  |
| `status` | `string` |  |
| `categories` | `null \| array` |  |
| `send_at` | `null \| string` |  |
| `send_to` | `null \| object` |  |
| `email_config` | `null \| object` |  |
| `is_abtest` | `boolean` |  |
| `created_at` | `string` |  |
| `updated_at` | `string` |  |


</details>

### Singlesends Search

Search and filter singlesends records powered by Airbyte's data sync. This often provides additional fields and operators beyond what the API natively supports, making it easier to narrow down results before performing further operations. Only available in hosted mode.

#### Python SDK

```python
await sendgrid.singlesends.search(
    query={"filter": {"eq": {"categories": []}}}
)
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/integrations/connectors/{your_connector_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "singlesends",
    "action": "search",
    "params": {
        "query": {"filter": {"eq": {"categories": []}}}
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
| `categories` | `array` | Categories associated with this single send |
| `created_at` | `string` | When the single send was created |
| `id` | `string` | Unique single send identifier |
| `is_abtest` | `boolean` | Whether this is an A/B test |
| `name` | `string` | Single send name |
| `send_at` | `string` | Scheduled send time |
| `status` | `string` | Current status: draft, scheduled, or triggered |
| `updated_at` | `string` | When the single send was last updated |

<details>
<summary><b>Response Schema</b></summary>

| Field Name | Type | Description |
|------------|------|-------------|
| `data` | `array` | List of matching records |
| `meta` | `object` | Pagination metadata |
| `meta.has_more` | `boolean` | Whether additional pages are available |
| `meta.cursor` | `string \| null` | Cursor for next page of results |
| `meta.took_ms` | `number \| null` | Query execution time in milliseconds |
| `data[].categories` | `array` | Categories associated with this single send |
| `data[].created_at` | `string` | When the single send was created |
| `data[].id` | `string` | Unique single send identifier |
| `data[].is_abtest` | `boolean` | Whether this is an A/B test |
| `data[].name` | `string` | Single send name |
| `data[].send_at` | `string` | Scheduled send time |
| `data[].status` | `string` | Current status: draft, scheduled, or triggered |
| `data[].updated_at` | `string` | When the single send was last updated |

</details>

## Templates

### Templates List

Returns paged transactional templates (legacy and dynamic).

#### Python SDK

```python
await sendgrid.templates.list()
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/integrations/connectors/{your_connector_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "templates",
    "action": "list"
}'
```


#### Parameters

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `generations` | `string` | No | Template generations to return |
| `page_size` | `integer` | No | Number of templates per page |


<details>
<summary><b>Response Schema</b></summary>

#### Records

| Field Name | Type | Description |
|------------|------|-------------|
| `id` | `string` |  |
| `name` | `string` |  |
| `generation` | `string` |  |
| `updated_at` | `null \| string` |  |
| `versions` | `null \| array` |  |


</details>

### Templates Get

Returns a single transactional template.

#### Python SDK

```python
await sendgrid.templates.get(
    template_id="<str>"
)
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/integrations/connectors/{your_connector_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "templates",
    "action": "get",
    "params": {
        "template_id": "<str>"
    }
}'
```


#### Parameters

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `template_id` | `string` | Yes | The ID of the template |


<details>
<summary><b>Response Schema</b></summary>

#### Records

| Field Name | Type | Description |
|------------|------|-------------|
| `id` | `string` |  |
| `name` | `string` |  |
| `generation` | `string` |  |
| `updated_at` | `null \| string` |  |
| `versions` | `null \| array` |  |


</details>

### Templates Search

Search and filter templates records powered by Airbyte's data sync. This often provides additional fields and operators beyond what the API natively supports, making it easier to narrow down results before performing further operations. Only available in hosted mode.

#### Python SDK

```python
await sendgrid.templates.search(
    query={"filter": {"eq": {"generation": "<str>"}}}
)
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/integrations/connectors/{your_connector_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "templates",
    "action": "search",
    "params": {
        "query": {"filter": {"eq": {"generation": "<str>"}}}
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
| `generation` | `string` | Template generation (legacy or dynamic) |
| `id` | `string` | Unique template identifier |
| `name` | `string` | Template name |
| `updated_at` | `string` | When the template was last updated |
| `versions` | `array` | Template versions |

<details>
<summary><b>Response Schema</b></summary>

| Field Name | Type | Description |
|------------|------|-------------|
| `data` | `array` | List of matching records |
| `meta` | `object` | Pagination metadata |
| `meta.has_more` | `boolean` | Whether additional pages are available |
| `meta.cursor` | `string \| null` | Cursor for next page of results |
| `meta.took_ms` | `number \| null` | Query execution time in milliseconds |
| `data[].generation` | `string` | Template generation (legacy or dynamic) |
| `data[].id` | `string` | Unique template identifier |
| `data[].name` | `string` | Template name |
| `data[].updated_at` | `string` | When the template was last updated |
| `data[].versions` | `array` | Template versions |

</details>

## Singlesend Stats

### Singlesend Stats List

Returns stats for all single sends.

#### Python SDK

```python
await sendgrid.singlesend_stats.list()
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/integrations/connectors/{your_connector_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "singlesend_stats",
    "action": "list"
}'
```


#### Parameters

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `page_size` | `integer` | No | Maximum number of stats to return per page |


<details>
<summary><b>Response Schema</b></summary>

#### Records

| Field Name | Type | Description |
|------------|------|-------------|
| `id` | `string` |  |
| `ab_phase` | `null \| string` |  |
| `ab_variation` | `null \| string` |  |
| `aggregation` | `null \| string` |  |
| `stats` | `null \| object` |  |


#### Meta

| Field Name | Type | Description |
|------------|------|-------------|
| `next` | `null \| string` |  |

</details>

### Singlesend Stats Search

Search and filter singlesend stats records powered by Airbyte's data sync. This often provides additional fields and operators beyond what the API natively supports, making it easier to narrow down results before performing further operations. Only available in hosted mode.

#### Python SDK

```python
await sendgrid.singlesend_stats.search(
    query={"filter": {"eq": {"ab_phase": "<str>"}}}
)
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/integrations/connectors/{your_connector_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "singlesend_stats",
    "action": "search",
    "params": {
        "query": {"filter": {"eq": {"ab_phase": "<str>"}}}
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
| `ab_phase` | `string` | The A/B test phase |
| `ab_variation` | `string` | The A/B test variation |
| `aggregation` | `string` | The aggregation type |
| `id` | `string` | The single send ID |
| `stats` | `object` | Email statistics for the single send |

<details>
<summary><b>Response Schema</b></summary>

| Field Name | Type | Description |
|------------|------|-------------|
| `data` | `array` | List of matching records |
| `meta` | `object` | Pagination metadata |
| `meta.has_more` | `boolean` | Whether additional pages are available |
| `meta.cursor` | `string \| null` | Cursor for next page of results |
| `meta.took_ms` | `number \| null` | Query execution time in milliseconds |
| `data[].ab_phase` | `string` | The A/B test phase |
| `data[].ab_variation` | `string` | The A/B test variation |
| `data[].aggregation` | `string` | The aggregation type |
| `data[].id` | `string` | The single send ID |
| `data[].stats` | `object` | Email statistics for the single send |

</details>

## Bounces

### Bounces List

Returns all bounced email records.

#### Python SDK

```python
await sendgrid.bounces.list()
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/integrations/connectors/{your_connector_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "bounces",
    "action": "list"
}'
```


#### Parameters

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `limit` | `integer` | No | Number of records to return |
| `offset` | `integer` | No | Number of records to skip for pagination |


<details>
<summary><b>Response Schema</b></summary>

#### Records

| Field Name | Type | Description |
|------------|------|-------------|
| `created` | `integer` |  |
| `email` | `string` |  |
| `reason` | `string` |  |
| `status` | `string` |  |


</details>

### Bounces Search

Search and filter bounces records powered by Airbyte's data sync. This often provides additional fields and operators beyond what the API natively supports, making it easier to narrow down results before performing further operations. Only available in hosted mode.

#### Python SDK

```python
await sendgrid.bounces.search(
    query={"filter": {"eq": {"created": 0}}}
)
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/integrations/connectors/{your_connector_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "bounces",
    "action": "search",
    "params": {
        "query": {"filter": {"eq": {"created": 0}}}
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
| `created` | `integer` | Unix timestamp when the bounce occurred |
| `email` | `string` | The email address that bounced |
| `reason` | `string` | The reason for the bounce |
| `status` | `string` | The enhanced status code for the bounce |

<details>
<summary><b>Response Schema</b></summary>

| Field Name | Type | Description |
|------------|------|-------------|
| `data` | `array` | List of matching records |
| `meta` | `object` | Pagination metadata |
| `meta.has_more` | `boolean` | Whether additional pages are available |
| `meta.cursor` | `string \| null` | Cursor for next page of results |
| `meta.took_ms` | `number \| null` | Query execution time in milliseconds |
| `data[].created` | `integer` | Unix timestamp when the bounce occurred |
| `data[].email` | `string` | The email address that bounced |
| `data[].reason` | `string` | The reason for the bounce |
| `data[].status` | `string` | The enhanced status code for the bounce |

</details>

## Blocks

### Blocks List

Returns all blocked email records.

#### Python SDK

```python
await sendgrid.blocks.list()
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/integrations/connectors/{your_connector_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "blocks",
    "action": "list"
}'
```


#### Parameters

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `limit` | `integer` | No | Number of records to return |
| `offset` | `integer` | No | Number of records to skip for pagination |


<details>
<summary><b>Response Schema</b></summary>

#### Records

| Field Name | Type | Description |
|------------|------|-------------|
| `created` | `integer` |  |
| `email` | `string` |  |
| `reason` | `string` |  |
| `status` | `string` |  |


</details>

### Blocks Search

Search and filter blocks records powered by Airbyte's data sync. This often provides additional fields and operators beyond what the API natively supports, making it easier to narrow down results before performing further operations. Only available in hosted mode.

#### Python SDK

```python
await sendgrid.blocks.search(
    query={"filter": {"eq": {"created": 0}}}
)
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/integrations/connectors/{your_connector_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "blocks",
    "action": "search",
    "params": {
        "query": {"filter": {"eq": {"created": 0}}}
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
| `created` | `integer` | Unix timestamp when the block occurred |
| `email` | `string` | The blocked email address |
| `reason` | `string` | The reason for the block |
| `status` | `string` | The status code for the block |

<details>
<summary><b>Response Schema</b></summary>

| Field Name | Type | Description |
|------------|------|-------------|
| `data` | `array` | List of matching records |
| `meta` | `object` | Pagination metadata |
| `meta.has_more` | `boolean` | Whether additional pages are available |
| `meta.cursor` | `string \| null` | Cursor for next page of results |
| `meta.took_ms` | `number \| null` | Query execution time in milliseconds |
| `data[].created` | `integer` | Unix timestamp when the block occurred |
| `data[].email` | `string` | The blocked email address |
| `data[].reason` | `string` | The reason for the block |
| `data[].status` | `string` | The status code for the block |

</details>

## Spam Reports

### Spam Reports List

Returns all spam report records.

#### Python SDK

```python
await sendgrid.spam_reports.list()
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/integrations/connectors/{your_connector_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "spam_reports",
    "action": "list"
}'
```


#### Parameters

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `limit` | `integer` | No | Number of records to return |
| `offset` | `integer` | No | Number of records to skip for pagination |


<details>
<summary><b>Response Schema</b></summary>

#### Records

| Field Name | Type | Description |
|------------|------|-------------|
| `created` | `integer` |  |
| `email` | `string` |  |
| `ip` | `string` |  |


</details>

## Invalid Emails

### Invalid Emails List

Returns all invalid email records.

#### Python SDK

```python
await sendgrid.invalid_emails.list()
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/integrations/connectors/{your_connector_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "invalid_emails",
    "action": "list"
}'
```


#### Parameters

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `limit` | `integer` | No | Number of records to return |
| `offset` | `integer` | No | Number of records to skip for pagination |


<details>
<summary><b>Response Schema</b></summary>

#### Records

| Field Name | Type | Description |
|------------|------|-------------|
| `created` | `integer` |  |
| `email` | `string` |  |
| `reason` | `string` |  |


</details>

### Invalid Emails Search

Search and filter invalid emails records powered by Airbyte's data sync. This often provides additional fields and operators beyond what the API natively supports, making it easier to narrow down results before performing further operations. Only available in hosted mode.

#### Python SDK

```python
await sendgrid.invalid_emails.search(
    query={"filter": {"eq": {"created": 0}}}
)
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/integrations/connectors/{your_connector_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "invalid_emails",
    "action": "search",
    "params": {
        "query": {"filter": {"eq": {"created": 0}}}
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
| `created` | `integer` | Unix timestamp when the invalid email was recorded |
| `email` | `string` | The invalid email address |
| `reason` | `string` | The reason the email is invalid |

<details>
<summary><b>Response Schema</b></summary>

| Field Name | Type | Description |
|------------|------|-------------|
| `data` | `array` | List of matching records |
| `meta` | `object` | Pagination metadata |
| `meta.has_more` | `boolean` | Whether additional pages are available |
| `meta.cursor` | `string \| null` | Cursor for next page of results |
| `meta.took_ms` | `number \| null` | Query execution time in milliseconds |
| `data[].created` | `integer` | Unix timestamp when the invalid email was recorded |
| `data[].email` | `string` | The invalid email address |
| `data[].reason` | `string` | The reason the email is invalid |

</details>

## Global Suppressions

### Global Suppressions List

Returns all globally unsubscribed email addresses.

#### Python SDK

```python
await sendgrid.global_suppressions.list()
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/integrations/connectors/{your_connector_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "global_suppressions",
    "action": "list"
}'
```


#### Parameters

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `limit` | `integer` | No | Number of records to return |
| `offset` | `integer` | No | Number of records to skip for pagination |


<details>
<summary><b>Response Schema</b></summary>

#### Records

| Field Name | Type | Description |
|------------|------|-------------|
| `created` | `integer` |  |
| `email` | `string` |  |


</details>

### Global Suppressions Search

Search and filter global suppressions records powered by Airbyte's data sync. This often provides additional fields and operators beyond what the API natively supports, making it easier to narrow down results before performing further operations. Only available in hosted mode.

#### Python SDK

```python
await sendgrid.global_suppressions.search(
    query={"filter": {"eq": {"created": 0}}}
)
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/integrations/connectors/{your_connector_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "global_suppressions",
    "action": "search",
    "params": {
        "query": {"filter": {"eq": {"created": 0}}}
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
| `created` | `integer` | Unix timestamp when the global suppression was created |
| `email` | `string` | The globally suppressed email address |

<details>
<summary><b>Response Schema</b></summary>

| Field Name | Type | Description |
|------------|------|-------------|
| `data` | `array` | List of matching records |
| `meta` | `object` | Pagination metadata |
| `meta.has_more` | `boolean` | Whether additional pages are available |
| `meta.cursor` | `string \| null` | Cursor for next page of results |
| `meta.took_ms` | `number \| null` | Query execution time in milliseconds |
| `data[].created` | `integer` | Unix timestamp when the global suppression was created |
| `data[].email` | `string` | The globally suppressed email address |

</details>

## Suppression Groups

### Suppression Groups List

Returns all suppression (unsubscribe) groups.

#### Python SDK

```python
await sendgrid.suppression_groups.list()
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/integrations/connectors/{your_connector_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "suppression_groups",
    "action": "list"
}'
```



<details>
<summary><b>Response Schema</b></summary>

#### Records

| Field Name | Type | Description |
|------------|------|-------------|
| `id` | `integer` |  |
| `name` | `string` |  |
| `description` | `string` |  |
| `is_default` | `boolean` |  |
| `unsubscribes` | `integer` |  |


</details>

### Suppression Groups Get

Returns information about a single suppression group.

#### Python SDK

```python
await sendgrid.suppression_groups.get(
    group_id=0
)
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/integrations/connectors/{your_connector_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "suppression_groups",
    "action": "get",
    "params": {
        "group_id": 0
    }
}'
```


#### Parameters

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `group_id` | `integer` | Yes | The ID of the suppression group |


<details>
<summary><b>Response Schema</b></summary>

#### Records

| Field Name | Type | Description |
|------------|------|-------------|
| `id` | `integer` |  |
| `name` | `string` |  |
| `description` | `string` |  |
| `is_default` | `boolean` |  |
| `unsubscribes` | `integer` |  |


</details>

### Suppression Groups Search

Search and filter suppression groups records powered by Airbyte's data sync. This often provides additional fields and operators beyond what the API natively supports, making it easier to narrow down results before performing further operations. Only available in hosted mode.

#### Python SDK

```python
await sendgrid.suppression_groups.search(
    query={"filter": {"eq": {"description": "<str>"}}}
)
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/integrations/connectors/{your_connector_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "suppression_groups",
    "action": "search",
    "params": {
        "query": {"filter": {"eq": {"description": "<str>"}}}
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
| `description` | `string` | Description of the suppression group |
| `id` | `integer` | Unique suppression group identifier |
| `is_default` | `boolean` | Whether this is the default suppression group |
| `name` | `string` | Suppression group name |
| `unsubscribes` | `integer` | Number of unsubscribes in this group |

<details>
<summary><b>Response Schema</b></summary>

| Field Name | Type | Description |
|------------|------|-------------|
| `data` | `array` | List of matching records |
| `meta` | `object` | Pagination metadata |
| `meta.has_more` | `boolean` | Whether additional pages are available |
| `meta.cursor` | `string \| null` | Cursor for next page of results |
| `meta.took_ms` | `number \| null` | Query execution time in milliseconds |
| `data[].description` | `string` | Description of the suppression group |
| `data[].id` | `integer` | Unique suppression group identifier |
| `data[].is_default` | `boolean` | Whether this is the default suppression group |
| `data[].name` | `string` | Suppression group name |
| `data[].unsubscribes` | `integer` | Number of unsubscribes in this group |

</details>

## Suppression Group Members

### Suppression Group Members List

Returns all suppressions across all groups.

#### Python SDK

```python
await sendgrid.suppression_group_members.list()
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/integrations/connectors/{your_connector_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "suppression_group_members",
    "action": "list"
}'
```


#### Parameters

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `limit` | `integer` | No | Number of records to return |
| `offset` | `integer` | No | Number of records to skip for pagination |


<details>
<summary><b>Response Schema</b></summary>

#### Records

| Field Name | Type | Description |
|------------|------|-------------|
| `email` | `string` |  |
| `group_id` | `integer` |  |
| `group_name` | `string` |  |
| `created_at` | `integer` |  |


</details>

### Suppression Group Members Search

Search and filter suppression group members records powered by Airbyte's data sync. This often provides additional fields and operators beyond what the API natively supports, making it easier to narrow down results before performing further operations. Only available in hosted mode.

#### Python SDK

```python
await sendgrid.suppression_group_members.search(
    query={"filter": {"eq": {"created_at": 0}}}
)
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/integrations/connectors/{your_connector_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "suppression_group_members",
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
| `created_at` | `integer` | Unix timestamp when the suppression was created |
| `email` | `string` | The suppressed email address |
| `group_id` | `integer` | ID of the suppression group |
| `group_name` | `string` | Name of the suppression group |

<details>
<summary><b>Response Schema</b></summary>

| Field Name | Type | Description |
|------------|------|-------------|
| `data` | `array` | List of matching records |
| `meta` | `object` | Pagination metadata |
| `meta.has_more` | `boolean` | Whether additional pages are available |
| `meta.cursor` | `string \| null` | Cursor for next page of results |
| `meta.took_ms` | `number \| null` | Query execution time in milliseconds |
| `data[].created_at` | `integer` | Unix timestamp when the suppression was created |
| `data[].email` | `string` | The suppressed email address |
| `data[].group_id` | `integer` | ID of the suppression group |
| `data[].group_name` | `string` | Name of the suppression group |

</details>

