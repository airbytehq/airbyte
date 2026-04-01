# Zendesk-Talk full reference

This is the full reference documentation for the Zendesk-Talk agent connector.

## Supported entities and actions

The Zendesk-Talk connector supports the following entities and actions.

| Entity | Actions |
|--------|---------|
| Phone Numbers | [List](#phone-numbers-list), [Get](#phone-numbers-get), [Search](#phone-numbers-search) |
| Addresses | [List](#addresses-list), [Get](#addresses-get), [Search](#addresses-search) |
| Greetings | [List](#greetings-list), [Get](#greetings-get), [Search](#greetings-search) |
| Greeting Categories | [List](#greeting-categories-list), [Get](#greeting-categories-get), [Search](#greeting-categories-search) |
| Ivrs | [List](#ivrs-list), [Get](#ivrs-get), [Search](#ivrs-search) |
| Agents Activity | [List](#agents-activity-list), [Search](#agents-activity-search) |
| Agents Overview | [List](#agents-overview-list), [Search](#agents-overview-search) |
| Account Overview | [List](#account-overview-list), [Search](#account-overview-search) |
| Current Queue Activity | [List](#current-queue-activity-list), [Search](#current-queue-activity-search) |
| Calls | [List](#calls-list), [Search](#calls-search) |
| Call Legs | [List](#call-legs-list), [Search](#call-legs-search) |

## Phone Numbers

### Phone Numbers List

Returns a list of all phone numbers in the Zendesk Talk account

#### Python SDK

```python
await zendesk_talk.phone_numbers.list()
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/integrations/connectors/{your_connector_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "phone_numbers",
    "action": "list"
}'
```



<details>
<summary><b>Response Schema</b></summary>

#### Records

| Field Name | Type | Description |
|------------|------|-------------|
| `id` | `null \| integer` |  |
| `brand_id` | `null \| integer` |  |
| `call_recording_consent` | `null \| string` |  |
| `capabilities` | `null \| object` |  |
| `categorised_greetings` | `null \| object` |  |
| `categorised_greetings_with_sub_settings` | `null \| object` |  |
| `country_code` | `null \| string` |  |
| `created_at` | `null \| string` |  |
| `default_greeting_ids` | `null \| array` |  |
| `default_group_id` | `null \| integer` |  |
| `display_number` | `null \| string` |  |
| `external` | `null \| boolean` |  |
| `failover_number` | `null \| string` |  |
| `greeting_ids` | `null \| array` |  |
| `group_ids` | `null \| array` |  |
| `ivr_id` | `null \| integer` |  |
| `line_type` | `null \| string` |  |
| `location` | `null \| string` |  |
| `name` | `null \| string` |  |
| `nickname` | `null \| string` |  |
| `number` | `null \| string` |  |
| `outbound_enabled` | `null \| boolean` |  |
| `priority` | `null \| integer` |  |
| `recorded` | `null \| boolean` |  |
| `schedule_id` | `null \| integer` |  |
| `sms_enabled` | `null \| boolean` |  |
| `sms_group_id` | `null \| integer` |  |
| `token` | `null \| string` |  |
| `toll_free` | `null \| boolean` |  |
| `transcription` | `null \| boolean` |  |
| `voice_enabled` | `null \| boolean` |  |


#### Meta

| Field Name | Type | Description |
|------------|------|-------------|
| `next_page` | `null \| string` |  |

</details>

### Phone Numbers Get

Retrieves a single phone number by ID

#### Python SDK

```python
await zendesk_talk.phone_numbers.get(
    phone_number_id=0
)
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/integrations/connectors/{your_connector_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "phone_numbers",
    "action": "get",
    "params": {
        "phone_number_id": 0
    }
}'
```


#### Parameters

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `phone_number_id` | `integer` | Yes | ID of the phone number |


<details>
<summary><b>Response Schema</b></summary>

#### Records

| Field Name | Type | Description |
|------------|------|-------------|
| `id` | `null \| integer` |  |
| `brand_id` | `null \| integer` |  |
| `call_recording_consent` | `null \| string` |  |
| `capabilities` | `null \| object` |  |
| `categorised_greetings` | `null \| object` |  |
| `categorised_greetings_with_sub_settings` | `null \| object` |  |
| `country_code` | `null \| string` |  |
| `created_at` | `null \| string` |  |
| `default_greeting_ids` | `null \| array` |  |
| `default_group_id` | `null \| integer` |  |
| `display_number` | `null \| string` |  |
| `external` | `null \| boolean` |  |
| `failover_number` | `null \| string` |  |
| `greeting_ids` | `null \| array` |  |
| `group_ids` | `null \| array` |  |
| `ivr_id` | `null \| integer` |  |
| `line_type` | `null \| string` |  |
| `location` | `null \| string` |  |
| `name` | `null \| string` |  |
| `nickname` | `null \| string` |  |
| `number` | `null \| string` |  |
| `outbound_enabled` | `null \| boolean` |  |
| `priority` | `null \| integer` |  |
| `recorded` | `null \| boolean` |  |
| `schedule_id` | `null \| integer` |  |
| `sms_enabled` | `null \| boolean` |  |
| `sms_group_id` | `null \| integer` |  |
| `token` | `null \| string` |  |
| `toll_free` | `null \| boolean` |  |
| `transcription` | `null \| boolean` |  |
| `voice_enabled` | `null \| boolean` |  |


</details>

### Phone Numbers Search

Search and filter phone numbers records powered by Airbyte's data sync. This often provides additional fields and operators beyond what the API natively supports, making it easier to narrow down results before performing further operations. Only available in hosted mode.

#### Python SDK

```python
await zendesk_talk.phone_numbers.search(
    query={"filter": {"eq": {"call_recording_consent": "<str>"}}}
)
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/integrations/connectors/{your_connector_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "phone_numbers",
    "action": "search",
    "params": {
        "query": {"filter": {"eq": {"call_recording_consent": "<str>"}}}
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
| `call_recording_consent` | `string` | What call recording consent is set to |
| `capabilities` | `object` | Phone number capabilities (sms, mms, voice) |
| `categorised_greetings` | `object` | Greeting category IDs and names |
| `categorised_greetings_with_sub_settings` | `object` | Greeting categories with associated settings |
| `country_code` | `string` | ISO country code for the number |
| `created_at` | `string` | Date and time the phone number was created |
| `default_greeting_ids` | `array` | Names of default system greetings |
| `default_group_id` | `integer` | Default group ID |
| `display_number` | `string` | Formatted phone number |
| `external` | `boolean` | Whether this is an external caller ID number |
| `failover_number` | `string` | Failover number associated with the phone number |
| `greeting_ids` | `array` | Custom greeting IDs associated with the phone number |
| `group_ids` | `array` | Array of associated group IDs |
| `id` | `integer` | Unique phone number identifier |
| `ivr_id` | `integer` | ID of IVR associated with the phone number |
| `line_type` | `string` | Type of line (phone or digital) |
| `location` | `string` | Geographical location of the number |
| `name` | `string` | Nickname if set, otherwise the display number |
| `nickname` | `string` | Nickname of the phone number |
| `number` | `string` | Phone number digits |
| `outbound_enabled` | `boolean` | Whether outbound calls are enabled |
| `priority` | `integer` | Priority level of the phone number |
| `recorded` | `boolean` | Whether calls are recorded |
| `schedule_id` | `integer` | ID of schedule associated with the phone number |
| `sms_enabled` | `boolean` | Whether SMS is enabled |
| `sms_group_id` | `integer` | Group associated with SMS |
| `token` | `string` | Generated token unique for the phone number |
| `toll_free` | `boolean` | Whether the number is toll-free |
| `transcription` | `boolean` | Whether voicemail transcription is enabled |
| `voice_enabled` | `boolean` | Whether voice is enabled |

<details>
<summary><b>Response Schema</b></summary>

| Field Name | Type | Description |
|------------|------|-------------|
| `data` | `array` | List of matching records |
| `meta` | `object` | Pagination metadata |
| `meta.has_more` | `boolean` | Whether additional pages are available |
| `meta.cursor` | `string \| null` | Cursor for next page of results |
| `meta.took_ms` | `number \| null` | Query execution time in milliseconds |
| `data[].call_recording_consent` | `string` | What call recording consent is set to |
| `data[].capabilities` | `object` | Phone number capabilities (sms, mms, voice) |
| `data[].categorised_greetings` | `object` | Greeting category IDs and names |
| `data[].categorised_greetings_with_sub_settings` | `object` | Greeting categories with associated settings |
| `data[].country_code` | `string` | ISO country code for the number |
| `data[].created_at` | `string` | Date and time the phone number was created |
| `data[].default_greeting_ids` | `array` | Names of default system greetings |
| `data[].default_group_id` | `integer` | Default group ID |
| `data[].display_number` | `string` | Formatted phone number |
| `data[].external` | `boolean` | Whether this is an external caller ID number |
| `data[].failover_number` | `string` | Failover number associated with the phone number |
| `data[].greeting_ids` | `array` | Custom greeting IDs associated with the phone number |
| `data[].group_ids` | `array` | Array of associated group IDs |
| `data[].id` | `integer` | Unique phone number identifier |
| `data[].ivr_id` | `integer` | ID of IVR associated with the phone number |
| `data[].line_type` | `string` | Type of line (phone or digital) |
| `data[].location` | `string` | Geographical location of the number |
| `data[].name` | `string` | Nickname if set, otherwise the display number |
| `data[].nickname` | `string` | Nickname of the phone number |
| `data[].number` | `string` | Phone number digits |
| `data[].outbound_enabled` | `boolean` | Whether outbound calls are enabled |
| `data[].priority` | `integer` | Priority level of the phone number |
| `data[].recorded` | `boolean` | Whether calls are recorded |
| `data[].schedule_id` | `integer` | ID of schedule associated with the phone number |
| `data[].sms_enabled` | `boolean` | Whether SMS is enabled |
| `data[].sms_group_id` | `integer` | Group associated with SMS |
| `data[].token` | `string` | Generated token unique for the phone number |
| `data[].toll_free` | `boolean` | Whether the number is toll-free |
| `data[].transcription` | `boolean` | Whether voicemail transcription is enabled |
| `data[].voice_enabled` | `boolean` | Whether voice is enabled |

</details>

## Addresses

### Addresses List

Returns a list of all addresses in the Zendesk Talk account

#### Python SDK

```python
await zendesk_talk.addresses.list()
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/integrations/connectors/{your_connector_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "addresses",
    "action": "list"
}'
```



<details>
<summary><b>Response Schema</b></summary>

#### Records

| Field Name | Type | Description |
|------------|------|-------------|
| `id` | `null \| integer` |  |
| `city` | `null \| string` |  |
| `country_code` | `null \| string` |  |
| `name` | `null \| string` |  |
| `provider_reference` | `null \| string` |  |
| `province` | `null \| string` |  |
| `state` | `null \| string` |  |
| `street` | `null \| string` |  |
| `zip` | `null \| string` |  |


#### Meta

| Field Name | Type | Description |
|------------|------|-------------|
| `next_page` | `null \| string` |  |

</details>

### Addresses Get

Retrieves a single address by ID

#### Python SDK

```python
await zendesk_talk.addresses.get(
    address_id=0
)
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/integrations/connectors/{your_connector_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "addresses",
    "action": "get",
    "params": {
        "address_id": 0
    }
}'
```


#### Parameters

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `address_id` | `integer` | Yes | ID of the address |


<details>
<summary><b>Response Schema</b></summary>

#### Records

| Field Name | Type | Description |
|------------|------|-------------|
| `id` | `null \| integer` |  |
| `city` | `null \| string` |  |
| `country_code` | `null \| string` |  |
| `name` | `null \| string` |  |
| `provider_reference` | `null \| string` |  |
| `province` | `null \| string` |  |
| `state` | `null \| string` |  |
| `street` | `null \| string` |  |
| `zip` | `null \| string` |  |


</details>

### Addresses Search

Search and filter addresses records powered by Airbyte's data sync. This often provides additional fields and operators beyond what the API natively supports, making it easier to narrow down results before performing further operations. Only available in hosted mode.

#### Python SDK

```python
await zendesk_talk.addresses.search(
    query={"filter": {"eq": {"city": "<str>"}}}
)
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/integrations/connectors/{your_connector_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "addresses",
    "action": "search",
    "params": {
        "query": {"filter": {"eq": {"city": "<str>"}}}
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
| `city` | `string` | City of the address |
| `country_code` | `string` | ISO country code |
| `id` | `integer` | Unique address identifier |
| `name` | `string` | Name of the address |
| `provider_reference` | `string` | Provider reference of the address |
| `province` | `string` | Province of the address |
| `state` | `string` | State of the address |
| `street` | `string` | Street of the address |
| `zip` | `string` | Zip code of the address |

<details>
<summary><b>Response Schema</b></summary>

| Field Name | Type | Description |
|------------|------|-------------|
| `data` | `array` | List of matching records |
| `meta` | `object` | Pagination metadata |
| `meta.has_more` | `boolean` | Whether additional pages are available |
| `meta.cursor` | `string \| null` | Cursor for next page of results |
| `meta.took_ms` | `number \| null` | Query execution time in milliseconds |
| `data[].city` | `string` | City of the address |
| `data[].country_code` | `string` | ISO country code |
| `data[].id` | `integer` | Unique address identifier |
| `data[].name` | `string` | Name of the address |
| `data[].provider_reference` | `string` | Provider reference of the address |
| `data[].province` | `string` | Province of the address |
| `data[].state` | `string` | State of the address |
| `data[].street` | `string` | Street of the address |
| `data[].zip` | `string` | Zip code of the address |

</details>

## Greetings

### Greetings List

Returns a list of all greetings in the Zendesk Talk account

#### Python SDK

```python
await zendesk_talk.greetings.list()
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/integrations/connectors/{your_connector_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "greetings",
    "action": "list"
}'
```



<details>
<summary><b>Response Schema</b></summary>

#### Records

| Field Name | Type | Description |
|------------|------|-------------|
| `id` | `null \| string` |  |
| `active` | `null \| boolean` |  |
| `audio_name` | `null \| string` |  |
| `audio_url` | `null \| string` |  |
| `category_id` | `null \| integer` |  |
| `default` | `null \| boolean` |  |
| `default_lang` | `null \| boolean` |  |
| `has_sub_settings` | `null \| boolean` |  |
| `ivr_ids` | `null \| array` |  |
| `name` | `null \| string` |  |
| `pending` | `null \| boolean` |  |
| `phone_number_ids` | `null \| array` |  |
| `upload_id` | `null \| integer` |  |


#### Meta

| Field Name | Type | Description |
|------------|------|-------------|
| `next_page` | `null \| string` |  |

</details>

### Greetings Get

Retrieves a single greeting by ID

#### Python SDK

```python
await zendesk_talk.greetings.get(
    greeting_id="<str>"
)
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/integrations/connectors/{your_connector_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "greetings",
    "action": "get",
    "params": {
        "greeting_id": "<str>"
    }
}'
```


#### Parameters

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `greeting_id` | `string` | Yes | ID of the greeting |


<details>
<summary><b>Response Schema</b></summary>

#### Records

| Field Name | Type | Description |
|------------|------|-------------|
| `id` | `null \| string` |  |
| `active` | `null \| boolean` |  |
| `audio_name` | `null \| string` |  |
| `audio_url` | `null \| string` |  |
| `category_id` | `null \| integer` |  |
| `default` | `null \| boolean` |  |
| `default_lang` | `null \| boolean` |  |
| `has_sub_settings` | `null \| boolean` |  |
| `ivr_ids` | `null \| array` |  |
| `name` | `null \| string` |  |
| `pending` | `null \| boolean` |  |
| `phone_number_ids` | `null \| array` |  |
| `upload_id` | `null \| integer` |  |


</details>

### Greetings Search

Search and filter greetings records powered by Airbyte's data sync. This often provides additional fields and operators beyond what the API natively supports, making it easier to narrow down results before performing further operations. Only available in hosted mode.

#### Python SDK

```python
await zendesk_talk.greetings.search(
    query={"filter": {"eq": {"active": True}}}
)
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/integrations/connectors/{your_connector_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "greetings",
    "action": "search",
    "params": {
        "query": {"filter": {"eq": {"active": True}}}
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
| `active` | `boolean` | Whether the greeting is associated with phone numbers |
| `audio_name` | `string` | Audio file name |
| `audio_url` | `string` | Path to the greeting sound file |
| `category_id` | `integer` | ID of the greeting category |
| `default` | `boolean` | Whether this is a system default greeting |
| `default_lang` | `boolean` | Whether the greeting has a default language |
| `has_sub_settings` | `boolean` | Sub-settings for categorized greetings |
| `id` | `string` | Greeting ID |
| `ivr_ids` | `array` | IDs of IVRs associated with the greeting |
| `name` | `string` | Name of the greeting |
| `pending` | `boolean` | Whether the greeting is pending |
| `phone_number_ids` | `array` | IDs of phone numbers associated with the greeting |
| `upload_id` | `integer` | Upload ID associated with the greeting |

<details>
<summary><b>Response Schema</b></summary>

| Field Name | Type | Description |
|------------|------|-------------|
| `data` | `array` | List of matching records |
| `meta` | `object` | Pagination metadata |
| `meta.has_more` | `boolean` | Whether additional pages are available |
| `meta.cursor` | `string \| null` | Cursor for next page of results |
| `meta.took_ms` | `number \| null` | Query execution time in milliseconds |
| `data[].active` | `boolean` | Whether the greeting is associated with phone numbers |
| `data[].audio_name` | `string` | Audio file name |
| `data[].audio_url` | `string` | Path to the greeting sound file |
| `data[].category_id` | `integer` | ID of the greeting category |
| `data[].default` | `boolean` | Whether this is a system default greeting |
| `data[].default_lang` | `boolean` | Whether the greeting has a default language |
| `data[].has_sub_settings` | `boolean` | Sub-settings for categorized greetings |
| `data[].id` | `string` | Greeting ID |
| `data[].ivr_ids` | `array` | IDs of IVRs associated with the greeting |
| `data[].name` | `string` | Name of the greeting |
| `data[].pending` | `boolean` | Whether the greeting is pending |
| `data[].phone_number_ids` | `array` | IDs of phone numbers associated with the greeting |
| `data[].upload_id` | `integer` | Upload ID associated with the greeting |

</details>

## Greeting Categories

### Greeting Categories List

Returns a list of all greeting categories

#### Python SDK

```python
await zendesk_talk.greeting_categories.list()
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/integrations/connectors/{your_connector_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "greeting_categories",
    "action": "list"
}'
```



<details>
<summary><b>Response Schema</b></summary>

#### Records

| Field Name | Type | Description |
|------------|------|-------------|
| `id` | `null \| integer` |  |
| `name` | `null \| string` |  |


#### Meta

| Field Name | Type | Description |
|------------|------|-------------|
| `next_page` | `null \| string` |  |

</details>

### Greeting Categories Get

Retrieves a single greeting category by ID

#### Python SDK

```python
await zendesk_talk.greeting_categories.get(
    greeting_category_id=0
)
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/integrations/connectors/{your_connector_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "greeting_categories",
    "action": "get",
    "params": {
        "greeting_category_id": 0
    }
}'
```


#### Parameters

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `greeting_category_id` | `integer` | Yes | ID of the greeting category |


<details>
<summary><b>Response Schema</b></summary>

#### Records

| Field Name | Type | Description |
|------------|------|-------------|
| `id` | `null \| integer` |  |
| `name` | `null \| string` |  |


</details>

### Greeting Categories Search

Search and filter greeting categories records powered by Airbyte's data sync. This often provides additional fields and operators beyond what the API natively supports, making it easier to narrow down results before performing further operations. Only available in hosted mode.

#### Python SDK

```python
await zendesk_talk.greeting_categories.search(
    query={"filter": {"eq": {"id": 0}}}
)
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/integrations/connectors/{your_connector_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "greeting_categories",
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
| `id` | `integer` | Greeting category ID |
| `name` | `string` | Name of the greeting category |

<details>
<summary><b>Response Schema</b></summary>

| Field Name | Type | Description |
|------------|------|-------------|
| `data` | `array` | List of matching records |
| `meta` | `object` | Pagination metadata |
| `meta.has_more` | `boolean` | Whether additional pages are available |
| `meta.cursor` | `string \| null` | Cursor for next page of results |
| `meta.took_ms` | `number \| null` | Query execution time in milliseconds |
| `data[].id` | `integer` | Greeting category ID |
| `data[].name` | `string` | Name of the greeting category |

</details>

## Ivrs

### Ivrs List

Returns a list of all IVR configurations

#### Python SDK

```python
await zendesk_talk.ivrs.list()
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/integrations/connectors/{your_connector_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "ivrs",
    "action": "list"
}'
```



<details>
<summary><b>Response Schema</b></summary>

#### Records

| Field Name | Type | Description |
|------------|------|-------------|
| `id` | `null \| integer` |  |
| `name` | `null \| string` |  |
| `phone_number_ids` | `null \| array` |  |
| `phone_number_names` | `null \| array` |  |
| `menus` | `null \| array` |  |


#### Meta

| Field Name | Type | Description |
|------------|------|-------------|
| `next_page` | `null \| string` |  |

</details>

### Ivrs Get

Retrieves a single IVR configuration by ID

#### Python SDK

```python
await zendesk_talk.ivrs.get(
    ivr_id=0
)
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/integrations/connectors/{your_connector_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "ivrs",
    "action": "get",
    "params": {
        "ivr_id": 0
    }
}'
```


#### Parameters

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `ivr_id` | `integer` | Yes | ID of the IVR |


<details>
<summary><b>Response Schema</b></summary>

#### Records

| Field Name | Type | Description |
|------------|------|-------------|
| `id` | `null \| integer` |  |
| `name` | `null \| string` |  |
| `phone_number_ids` | `null \| array` |  |
| `phone_number_names` | `null \| array` |  |
| `menus` | `null \| array` |  |


</details>

### Ivrs Search

Search and filter ivrs records powered by Airbyte's data sync. This often provides additional fields and operators beyond what the API natively supports, making it easier to narrow down results before performing further operations. Only available in hosted mode.

#### Python SDK

```python
await zendesk_talk.ivrs.search(
    query={"filter": {"eq": {"id": 0}}}
)
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/integrations/connectors/{your_connector_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "ivrs",
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
| `id` | `integer` | IVR ID |
| `menus` | `array` | List of IVR menus |
| `name` | `string` | Name of the IVR |
| `phone_number_ids` | `array` | IDs of phone numbers configured with this IVR |
| `phone_number_names` | `array` | Names of phone numbers configured with this IVR |

<details>
<summary><b>Response Schema</b></summary>

| Field Name | Type | Description |
|------------|------|-------------|
| `data` | `array` | List of matching records |
| `meta` | `object` | Pagination metadata |
| `meta.has_more` | `boolean` | Whether additional pages are available |
| `meta.cursor` | `string \| null` | Cursor for next page of results |
| `meta.took_ms` | `number \| null` | Query execution time in milliseconds |
| `data[].id` | `integer` | IVR ID |
| `data[].menus` | `array` | List of IVR menus |
| `data[].name` | `string` | Name of the IVR |
| `data[].phone_number_ids` | `array` | IDs of phone numbers configured with this IVR |
| `data[].phone_number_names` | `array` | Names of phone numbers configured with this IVR |

</details>

## Agents Activity

### Agents Activity List

Returns activity statistics for all agents for the current day

#### Python SDK

```python
await zendesk_talk.agents_activity.list()
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/integrations/connectors/{your_connector_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "agents_activity",
    "action": "list"
}'
```



<details>
<summary><b>Response Schema</b></summary>

#### Records

| Field Name | Type | Description |
|------------|------|-------------|
| `agent_id` | `null \| integer` |  |
| `agent_state` | `null \| string` |  |
| `available_time` | `null \| integer` |  |
| `avatar_url` | `null \| string` |  |
| `away_time` | `null \| integer` |  |
| `call_status` | `null \| string` |  |
| `calls_accepted` | `null \| integer` |  |
| `calls_denied` | `null \| integer` |  |
| `calls_missed` | `null \| integer` |  |
| `forwarding_number` | `null \| string` |  |
| `name` | `null \| string` |  |
| `online_time` | `null \| integer` |  |
| `total_call_duration` | `null \| integer` |  |
| `total_talk_time` | `null \| integer` |  |
| `total_wrap_up_time` | `null \| integer` |  |
| `transfers_only_time` | `null \| integer` |  |
| `via` | `null \| string` |  |
| `accepted_third_party_conferences` | `null \| integer` |  |
| `accepted_transfers` | `null \| integer` |  |
| `average_hold_time` | `null \| integer` |  |
| `average_talk_time` | `null \| integer` |  |
| `average_wrap_up_time` | `null \| integer` |  |
| `calls_put_on_hold` | `null \| integer` |  |
| `started_third_party_conferences` | `null \| integer` |  |
| `started_transfers` | `null \| integer` |  |
| `total_hold_time` | `null \| integer` |  |


#### Meta

| Field Name | Type | Description |
|------------|------|-------------|
| `next_page` | `null \| string` |  |

</details>

### Agents Activity Search

Search and filter agents activity records powered by Airbyte's data sync. This often provides additional fields and operators beyond what the API natively supports, making it easier to narrow down results before performing further operations. Only available in hosted mode.

#### Python SDK

```python
await zendesk_talk.agents_activity.search(
    query={"filter": {"eq": {"accepted_third_party_conferences": 0}}}
)
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/integrations/connectors/{your_connector_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "agents_activity",
    "action": "search",
    "params": {
        "query": {"filter": {"eq": {"accepted_third_party_conferences": 0}}}
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
| `accepted_third_party_conferences` | `integer` | Accepted third party conferences |
| `accepted_transfers` | `integer` | Total transfers accepted |
| `agent_id` | `integer` | Agent ID |
| `agent_state` | `string` | Agent state: online, offline, away, or transfers_only |
| `available_time` | `integer` | Total time agent was available to answer calls |
| `avatar_url` | `string` | URL to agent avatar |
| `average_hold_time` | `integer` | Average hold time per call |
| `average_talk_time` | `integer` | Average talk time per call |
| `average_wrap_up_time` | `integer` | Average wrap-up time per call |
| `away_time` | `integer` | Total time agent was set to away |
| `call_status` | `string` | Agent call status: on_call, wrap_up, or null |
| `calls_accepted` | `integer` | Total calls accepted |
| `calls_denied` | `integer` | Total calls denied |
| `calls_missed` | `integer` | Total calls missed |
| `calls_put_on_hold` | `integer` | Total calls placed on hold |
| `forwarding_number` | `string` | Forwarding number set by the agent |
| `name` | `string` | Agent name |
| `online_time` | `integer` | Total online time |
| `started_third_party_conferences` | `integer` | Started third party conferences |
| `started_transfers` | `integer` | Total transfers started |
| `total_call_duration` | `integer` | Total call duration |
| `total_hold_time` | `integer` | Total hold time across all calls |
| `total_talk_time` | `integer` | Total talk time (excludes hold) |
| `total_wrap_up_time` | `integer` | Total wrap-up time |
| `transfers_only_time` | `integer` | Total time in transfers-only mode |
| `via` | `string` | Channel the agent is registered on |

<details>
<summary><b>Response Schema</b></summary>

| Field Name | Type | Description |
|------------|------|-------------|
| `data` | `array` | List of matching records |
| `meta` | `object` | Pagination metadata |
| `meta.has_more` | `boolean` | Whether additional pages are available |
| `meta.cursor` | `string \| null` | Cursor for next page of results |
| `meta.took_ms` | `number \| null` | Query execution time in milliseconds |
| `data[].accepted_third_party_conferences` | `integer` | Accepted third party conferences |
| `data[].accepted_transfers` | `integer` | Total transfers accepted |
| `data[].agent_id` | `integer` | Agent ID |
| `data[].agent_state` | `string` | Agent state: online, offline, away, or transfers_only |
| `data[].available_time` | `integer` | Total time agent was available to answer calls |
| `data[].avatar_url` | `string` | URL to agent avatar |
| `data[].average_hold_time` | `integer` | Average hold time per call |
| `data[].average_talk_time` | `integer` | Average talk time per call |
| `data[].average_wrap_up_time` | `integer` | Average wrap-up time per call |
| `data[].away_time` | `integer` | Total time agent was set to away |
| `data[].call_status` | `string` | Agent call status: on_call, wrap_up, or null |
| `data[].calls_accepted` | `integer` | Total calls accepted |
| `data[].calls_denied` | `integer` | Total calls denied |
| `data[].calls_missed` | `integer` | Total calls missed |
| `data[].calls_put_on_hold` | `integer` | Total calls placed on hold |
| `data[].forwarding_number` | `string` | Forwarding number set by the agent |
| `data[].name` | `string` | Agent name |
| `data[].online_time` | `integer` | Total online time |
| `data[].started_third_party_conferences` | `integer` | Started third party conferences |
| `data[].started_transfers` | `integer` | Total transfers started |
| `data[].total_call_duration` | `integer` | Total call duration |
| `data[].total_hold_time` | `integer` | Total hold time across all calls |
| `data[].total_talk_time` | `integer` | Total talk time (excludes hold) |
| `data[].total_wrap_up_time` | `integer` | Total wrap-up time |
| `data[].transfers_only_time` | `integer` | Total time in transfers-only mode |
| `data[].via` | `string` | Channel the agent is registered on |

</details>

## Agents Overview

### Agents Overview List

Returns overview statistics for all agents for the current day

#### Python SDK

```python
await zendesk_talk.agents_overview.list()
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/integrations/connectors/{your_connector_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "agents_overview",
    "action": "list"
}'
```



<details>
<summary><b>Response Schema</b></summary>

#### Records

| Field Name | Type | Description |
|------------|------|-------------|
| `average_calls_accepted` | `null \| integer` |  |
| `average_calls_denied` | `null \| integer` |  |
| `average_calls_missed` | `null \| integer` |  |
| `average_wrap_up_time` | `null \| integer` |  |
| `total_calls_accepted` | `null \| integer` |  |
| `total_calls_denied` | `null \| integer` |  |
| `total_calls_missed` | `null \| integer` |  |
| `total_talk_time` | `null \| integer` |  |
| `total_wrap_up_time` | `null \| integer` |  |
| `average_accepted_transfers` | `null \| integer` |  |
| `average_available_time` | `null \| integer` |  |
| `average_away_time` | `null \| integer` |  |
| `average_calls_put_on_hold` | `null \| integer` |  |
| `average_hold_time` | `null \| integer` |  |
| `average_online_time` | `null \| integer` |  |
| `average_started_transfers` | `null \| integer` |  |
| `average_talk_time` | `null \| integer` |  |
| `average_transfers_only_time` | `null \| integer` |  |
| `current_timestamp` | `null \| integer` |  |
| `total_accepted_transfers` | `null \| integer` |  |
| `total_calls_put_on_hold` | `null \| integer` |  |
| `total_hold_time` | `null \| integer` |  |
| `total_started_transfers` | `null \| integer` |  |


</details>

### Agents Overview Search

Search and filter agents overview records powered by Airbyte's data sync. This often provides additional fields and operators beyond what the API natively supports, making it easier to narrow down results before performing further operations. Only available in hosted mode.

#### Python SDK

```python
await zendesk_talk.agents_overview.search(
    query={"filter": {"eq": {"average_accepted_transfers": 0}}}
)
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/integrations/connectors/{your_connector_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "agents_overview",
    "action": "search",
    "params": {
        "query": {"filter": {"eq": {"average_accepted_transfers": 0}}}
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
| `average_accepted_transfers` | `integer` | Average accepted transfers |
| `average_available_time` | `integer` | Average available time |
| `average_away_time` | `integer` | Average away time |
| `average_calls_accepted` | `integer` | Average calls accepted |
| `average_calls_denied` | `integer` | Average calls denied |
| `average_calls_missed` | `integer` | Average calls missed |
| `average_calls_put_on_hold` | `integer` | Average calls put on hold |
| `average_hold_time` | `integer` | Average hold time |
| `average_online_time` | `integer` | Average online time |
| `average_started_transfers` | `integer` | Average started transfers |
| `average_talk_time` | `integer` | Average talk time |
| `average_transfers_only_time` | `integer` | Average transfers-only time |
| `average_wrap_up_time` | `integer` | Average wrap-up time |
| `current_timestamp` | `integer` | Current timestamp |
| `total_accepted_transfers` | `integer` | Total accepted transfers |
| `total_calls_accepted` | `integer` | Total calls accepted |
| `total_calls_denied` | `integer` | Total calls denied |
| `total_calls_missed` | `integer` | Total calls missed |
| `total_calls_put_on_hold` | `integer` | Total calls put on hold |
| `total_hold_time` | `integer` | Total hold time |
| `total_started_transfers` | `integer` | Total started transfers |
| `total_talk_time` | `integer` | Total talk time |
| `total_wrap_up_time` | `integer` | Total wrap-up time |

<details>
<summary><b>Response Schema</b></summary>

| Field Name | Type | Description |
|------------|------|-------------|
| `data` | `array` | List of matching records |
| `meta` | `object` | Pagination metadata |
| `meta.has_more` | `boolean` | Whether additional pages are available |
| `meta.cursor` | `string \| null` | Cursor for next page of results |
| `meta.took_ms` | `number \| null` | Query execution time in milliseconds |
| `data[].average_accepted_transfers` | `integer` | Average accepted transfers |
| `data[].average_available_time` | `integer` | Average available time |
| `data[].average_away_time` | `integer` | Average away time |
| `data[].average_calls_accepted` | `integer` | Average calls accepted |
| `data[].average_calls_denied` | `integer` | Average calls denied |
| `data[].average_calls_missed` | `integer` | Average calls missed |
| `data[].average_calls_put_on_hold` | `integer` | Average calls put on hold |
| `data[].average_hold_time` | `integer` | Average hold time |
| `data[].average_online_time` | `integer` | Average online time |
| `data[].average_started_transfers` | `integer` | Average started transfers |
| `data[].average_talk_time` | `integer` | Average talk time |
| `data[].average_transfers_only_time` | `integer` | Average transfers-only time |
| `data[].average_wrap_up_time` | `integer` | Average wrap-up time |
| `data[].current_timestamp` | `integer` | Current timestamp |
| `data[].total_accepted_transfers` | `integer` | Total accepted transfers |
| `data[].total_calls_accepted` | `integer` | Total calls accepted |
| `data[].total_calls_denied` | `integer` | Total calls denied |
| `data[].total_calls_missed` | `integer` | Total calls missed |
| `data[].total_calls_put_on_hold` | `integer` | Total calls put on hold |
| `data[].total_hold_time` | `integer` | Total hold time |
| `data[].total_started_transfers` | `integer` | Total started transfers |
| `data[].total_talk_time` | `integer` | Total talk time |
| `data[].total_wrap_up_time` | `integer` | Total wrap-up time |

</details>

## Account Overview

### Account Overview List

Returns overview statistics for the account for the current day

#### Python SDK

```python
await zendesk_talk.account_overview.list()
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/integrations/connectors/{your_connector_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "account_overview",
    "action": "list"
}'
```



<details>
<summary><b>Response Schema</b></summary>

#### Records

| Field Name | Type | Description |
|------------|------|-------------|
| `average_call_duration` | `null \| integer` |  |
| `average_callback_wait_time` | `null \| integer` |  |
| `average_hold_time` | `null \| integer` |  |
| `average_queue_wait_time` | `null \| integer` |  |
| `average_time_to_answer` | `null \| integer` |  |
| `average_wrap_up_time` | `null \| integer` |  |
| `current_timestamp` | `null \| integer` |  |
| `max_calls_waiting` | `null \| integer` |  |
| `max_queue_wait_time` | `null \| integer` |  |
| `total_call_duration` | `null \| integer` |  |
| `total_callback_calls` | `null \| integer` |  |
| `total_calls` | `null \| integer` |  |
| `total_calls_abandoned_in_queue` | `null \| integer` |  |
| `total_calls_outside_business_hours` | `null \| integer` |  |
| `total_calls_with_exceeded_queue_wait_time` | `null \| integer` |  |
| `total_calls_with_requested_voicemail` | `null \| integer` |  |
| `total_embeddable_callback_calls` | `null \| integer` |  |
| `total_hold_time` | `null \| integer` |  |
| `total_inbound_calls` | `null \| integer` |  |
| `total_outbound_calls` | `null \| integer` |  |
| `total_textback_requests` | `null \| integer` |  |
| `total_voicemails` | `null \| integer` |  |
| `total_wrap_up_time` | `null \| integer` |  |


</details>

### Account Overview Search

Search and filter account overview records powered by Airbyte's data sync. This often provides additional fields and operators beyond what the API natively supports, making it easier to narrow down results before performing further operations. Only available in hosted mode.

#### Python SDK

```python
await zendesk_talk.account_overview.search(
    query={"filter": {"eq": {"average_call_duration": 0}}}
)
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/integrations/connectors/{your_connector_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "account_overview",
    "action": "search",
    "params": {
        "query": {"filter": {"eq": {"average_call_duration": 0}}}
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
| `average_call_duration` | `integer` | Average call duration |
| `average_callback_wait_time` | `integer` | Average callback wait time |
| `average_hold_time` | `integer` | Average hold time per call |
| `average_queue_wait_time` | `integer` | Average queue wait time |
| `average_time_to_answer` | `integer` | Average time to answer |
| `average_wrap_up_time` | `integer` | Average wrap-up time |
| `current_timestamp` | `integer` | Current timestamp |
| `max_calls_waiting` | `integer` | Max calls waiting in queue |
| `max_queue_wait_time` | `integer` | Max queue wait time |
| `total_call_duration` | `integer` | Total call duration |
| `total_callback_calls` | `integer` | Total callback calls |
| `total_calls` | `integer` | Total calls |
| `total_calls_abandoned_in_queue` | `integer` | Total calls abandoned in queue |
| `total_calls_outside_business_hours` | `integer` | Total calls outside business hours |
| `total_calls_with_exceeded_queue_wait_time` | `integer` | Total calls exceeding max queue wait time |
| `total_calls_with_requested_voicemail` | `integer` | Total calls requesting voicemail |
| `total_embeddable_callback_calls` | `integer` | Total embeddable callback calls |
| `total_hold_time` | `integer` | Total hold time |
| `total_inbound_calls` | `integer` | Total inbound calls |
| `total_outbound_calls` | `integer` | Total outbound calls |
| `total_textback_requests` | `integer` | Total textback requests |
| `total_voicemails` | `integer` | Total voicemails |
| `total_wrap_up_time` | `integer` | Total wrap-up time |

<details>
<summary><b>Response Schema</b></summary>

| Field Name | Type | Description |
|------------|------|-------------|
| `data` | `array` | List of matching records |
| `meta` | `object` | Pagination metadata |
| `meta.has_more` | `boolean` | Whether additional pages are available |
| `meta.cursor` | `string \| null` | Cursor for next page of results |
| `meta.took_ms` | `number \| null` | Query execution time in milliseconds |
| `data[].average_call_duration` | `integer` | Average call duration |
| `data[].average_callback_wait_time` | `integer` | Average callback wait time |
| `data[].average_hold_time` | `integer` | Average hold time per call |
| `data[].average_queue_wait_time` | `integer` | Average queue wait time |
| `data[].average_time_to_answer` | `integer` | Average time to answer |
| `data[].average_wrap_up_time` | `integer` | Average wrap-up time |
| `data[].current_timestamp` | `integer` | Current timestamp |
| `data[].max_calls_waiting` | `integer` | Max calls waiting in queue |
| `data[].max_queue_wait_time` | `integer` | Max queue wait time |
| `data[].total_call_duration` | `integer` | Total call duration |
| `data[].total_callback_calls` | `integer` | Total callback calls |
| `data[].total_calls` | `integer` | Total calls |
| `data[].total_calls_abandoned_in_queue` | `integer` | Total calls abandoned in queue |
| `data[].total_calls_outside_business_hours` | `integer` | Total calls outside business hours |
| `data[].total_calls_with_exceeded_queue_wait_time` | `integer` | Total calls exceeding max queue wait time |
| `data[].total_calls_with_requested_voicemail` | `integer` | Total calls requesting voicemail |
| `data[].total_embeddable_callback_calls` | `integer` | Total embeddable callback calls |
| `data[].total_hold_time` | `integer` | Total hold time |
| `data[].total_inbound_calls` | `integer` | Total inbound calls |
| `data[].total_outbound_calls` | `integer` | Total outbound calls |
| `data[].total_textback_requests` | `integer` | Total textback requests |
| `data[].total_voicemails` | `integer` | Total voicemails |
| `data[].total_wrap_up_time` | `integer` | Total wrap-up time |

</details>

## Current Queue Activity

### Current Queue Activity List

Returns current queue activity statistics

#### Python SDK

```python
await zendesk_talk.current_queue_activity.list()
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/integrations/connectors/{your_connector_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "current_queue_activity",
    "action": "list"
}'
```



<details>
<summary><b>Response Schema</b></summary>

#### Records

| Field Name | Type | Description |
|------------|------|-------------|
| `agents_online` | `null \| integer` |  |
| `average_wait_time` | `null \| integer` |  |
| `callbacks_waiting` | `null \| integer` |  |
| `calls_waiting` | `null \| integer` |  |
| `current_timestamp` | `null \| integer` |  |
| `embeddable_callbacks_waiting` | `null \| integer` |  |
| `longest_wait_time` | `null \| integer` |  |
| `ai_agent_calls` | `null \| integer` |  |


</details>

### Current Queue Activity Search

Search and filter current queue activity records powered by Airbyte's data sync. This often provides additional fields and operators beyond what the API natively supports, making it easier to narrow down results before performing further operations. Only available in hosted mode.

#### Python SDK

```python
await zendesk_talk.current_queue_activity.search(
    query={"filter": {"eq": {"agents_online": 0}}}
)
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/integrations/connectors/{your_connector_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "current_queue_activity",
    "action": "search",
    "params": {
        "query": {"filter": {"eq": {"agents_online": 0}}}
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
| `agents_online` | `integer` | Current number of agents online |
| `average_wait_time` | `integer` | Average wait time for callers in queue (seconds) |
| `callbacks_waiting` | `integer` | Number of callers in callback queue |
| `calls_waiting` | `integer` | Number of callers waiting in queue |
| `current_timestamp` | `integer` | Current timestamp |
| `embeddable_callbacks_waiting` | `integer` | Number of Web Widget callback requests waiting |
| `longest_wait_time` | `integer` | Longest wait time for any caller (seconds) |

<details>
<summary><b>Response Schema</b></summary>

| Field Name | Type | Description |
|------------|------|-------------|
| `data` | `array` | List of matching records |
| `meta` | `object` | Pagination metadata |
| `meta.has_more` | `boolean` | Whether additional pages are available |
| `meta.cursor` | `string \| null` | Cursor for next page of results |
| `meta.took_ms` | `number \| null` | Query execution time in milliseconds |
| `data[].agents_online` | `integer` | Current number of agents online |
| `data[].average_wait_time` | `integer` | Average wait time for callers in queue (seconds) |
| `data[].callbacks_waiting` | `integer` | Number of callers in callback queue |
| `data[].calls_waiting` | `integer` | Number of callers waiting in queue |
| `data[].current_timestamp` | `integer` | Current timestamp |
| `data[].embeddable_callbacks_waiting` | `integer` | Number of Web Widget callback requests waiting |
| `data[].longest_wait_time` | `integer` | Longest wait time for any caller (seconds) |

</details>

## Calls

### Calls List

Returns incremental call data. Requires a start_time parameter (Unix epoch timestamp).

#### Python SDK

```python
await zendesk_talk.calls.list(
    start_time=0
)
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/integrations/connectors/{your_connector_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "calls",
    "action": "list",
    "params": {
        "start_time": 0
    }
}'
```


#### Parameters

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `start_time` | `integer` | Yes | Unix epoch time to start from (e.g. 1704067200 for 2024-01-01) |


<details>
<summary><b>Response Schema</b></summary>

#### Records

| Field Name | Type | Description |
|------------|------|-------------|
| `id` | `null \| integer` |  |
| `agent_id` | `null \| integer` |  |
| `call_charge` | `null \| string` |  |
| `call_group_id` | `null \| integer` |  |
| `call_recording_consent` | `null \| string` |  |
| `call_recording_consent_action` | `null \| string` |  |
| `call_recording_consent_keypress` | `null \| string` |  |
| `callback` | `null \| boolean` |  |
| `callback_source` | `null \| string` |  |
| `completion_status` | `null \| string` |  |
| `consultation_time` | `null \| integer` |  |
| `created_at` | `null \| string` |  |
| `customer_requested_voicemail` | `null \| boolean` |  |
| `default_group` | `null \| boolean` |  |
| `direction` | `null \| string` |  |
| `duration` | `null \| integer` |  |
| `exceeded_queue_time` | `null \| boolean` |  |
| `exceeded_queue_wait_time` | `null \| boolean` |  |
| `hold_time` | `null \| integer` |  |
| `ivr_action` | `null \| string` |  |
| `ivr_destination_group_name` | `null \| string` |  |
| `ivr_hops` | `null \| integer` |  |
| `ivr_routed_to` | `null \| string` |  |
| `ivr_time_spent` | `null \| integer` |  |
| `minutes_billed` | `null \| integer` |  |
| `not_recording_time` | `null \| integer` |  |
| `outside_business_hours` | `null \| boolean` |  |
| `overflowed` | `null \| boolean` |  |
| `overflowed_to` | `null \| string` |  |
| `phone_number` | `null \| string` |  |
| `phone_number_id` | `null \| integer` |  |
| `quality_issues` | `null \| array` |  |
| `recording_control_interactions` | `null \| integer` |  |
| `recording_time` | `null \| integer` |  |
| `talk_time` | `null \| integer` |  |
| `ticket_id` | `null \| integer` |  |
| `time_to_answer` | `null \| integer` |  |
| `updated_at` | `null \| string` |  |
| `voicemail` | `null \| boolean` |  |
| `wait_time` | `null \| integer` |  |
| `wrap_up_time` | `null \| integer` |  |
| `customer_id` | `null \| integer` |  |
| `line` | `null \| string` |  |
| `line_id` | `null \| integer` |  |
| `line_type` | `null \| string` |  |
| `call_channel` | `null \| string` |  |
| `post_call_transcription_created` | `null \| boolean` |  |
| `post_call_summary_created` | `null \| boolean` |  |


#### Meta

| Field Name | Type | Description |
|------------|------|-------------|
| `next_page` | `null \| string` |  |
| `count` | `null \| integer` |  |

</details>

### Calls Search

Search and filter calls records powered by Airbyte's data sync. This often provides additional fields and operators beyond what the API natively supports, making it easier to narrow down results before performing further operations. Only available in hosted mode.

#### Python SDK

```python
await zendesk_talk.calls.search(
    query={"filter": {"eq": {"agent_id": 0}}}
)
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/integrations/connectors/{your_connector_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "calls",
    "action": "search",
    "params": {
        "query": {"filter": {"eq": {"agent_id": 0}}}
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
| `agent_id` | `integer` | Agent ID |
| `call_charge` | `string` | Call charge amount |
| `call_group_id` | `integer` | Call group ID |
| `call_recording_consent` | `string` | Call recording consent status |
| `call_recording_consent_action` | `string` | Recording consent action |
| `call_recording_consent_keypress` | `string` | Recording consent keypress |
| `callback` | `boolean` | Whether this was a callback |
| `callback_source` | `string` | Source of the callback |
| `completion_status` | `string` | Call completion status |
| `consultation_time` | `integer` | Consultation time |
| `created_at` | `string` | Creation timestamp |
| `customer_requested_voicemail` | `boolean` | Whether customer requested voicemail |
| `default_group` | `boolean` | Whether default group was used |
| `direction` | `string` | Call direction (inbound/outbound) |
| `duration` | `integer` | Call duration in seconds |
| `exceeded_queue_time` | `boolean` | Whether queue time was exceeded |
| `exceeded_queue_wait_time` | `boolean` | Whether max queue wait time was exceeded |
| `hold_time` | `integer` | Hold time in seconds |
| `id` | `integer` | Call ID |
| `ivr_action` | `string` | IVR action taken |
| `ivr_destination_group_name` | `string` | IVR destination group name |
| `ivr_hops` | `integer` | Number of IVR hops |
| `ivr_routed_to` | `string` | Where IVR routed the call |
| `ivr_time_spent` | `integer` | Time spent in IVR |
| `minutes_billed` | `integer` | Minutes billed |
| `not_recording_time` | `integer` | Time not recording |
| `outside_business_hours` | `boolean` | Whether call was outside business hours |
| `overflowed` | `boolean` | Whether call overflowed |
| `overflowed_to` | `string` | Where call overflowed to |
| `phone_number` | `string` | Phone number used |
| `phone_number_id` | `integer` | Phone number ID |
| `quality_issues` | `array` | Quality issues detected |
| `recording_control_interactions` | `integer` | Recording control interactions count |
| `recording_time` | `integer` | Recording time |
| `talk_time` | `integer` | Talk time in seconds |
| `ticket_id` | `integer` | Associated ticket ID |
| `time_to_answer` | `integer` | Time to answer in seconds |
| `updated_at` | `string` | Last update timestamp |
| `voicemail` | `boolean` | Whether it was a voicemail |
| `wait_time` | `integer` | Wait time in seconds |
| `wrap_up_time` | `integer` | Wrap-up time in seconds |

<details>
<summary><b>Response Schema</b></summary>

| Field Name | Type | Description |
|------------|------|-------------|
| `data` | `array` | List of matching records |
| `meta` | `object` | Pagination metadata |
| `meta.has_more` | `boolean` | Whether additional pages are available |
| `meta.cursor` | `string \| null` | Cursor for next page of results |
| `meta.took_ms` | `number \| null` | Query execution time in milliseconds |
| `data[].agent_id` | `integer` | Agent ID |
| `data[].call_charge` | `string` | Call charge amount |
| `data[].call_group_id` | `integer` | Call group ID |
| `data[].call_recording_consent` | `string` | Call recording consent status |
| `data[].call_recording_consent_action` | `string` | Recording consent action |
| `data[].call_recording_consent_keypress` | `string` | Recording consent keypress |
| `data[].callback` | `boolean` | Whether this was a callback |
| `data[].callback_source` | `string` | Source of the callback |
| `data[].completion_status` | `string` | Call completion status |
| `data[].consultation_time` | `integer` | Consultation time |
| `data[].created_at` | `string` | Creation timestamp |
| `data[].customer_requested_voicemail` | `boolean` | Whether customer requested voicemail |
| `data[].default_group` | `boolean` | Whether default group was used |
| `data[].direction` | `string` | Call direction (inbound/outbound) |
| `data[].duration` | `integer` | Call duration in seconds |
| `data[].exceeded_queue_time` | `boolean` | Whether queue time was exceeded |
| `data[].exceeded_queue_wait_time` | `boolean` | Whether max queue wait time was exceeded |
| `data[].hold_time` | `integer` | Hold time in seconds |
| `data[].id` | `integer` | Call ID |
| `data[].ivr_action` | `string` | IVR action taken |
| `data[].ivr_destination_group_name` | `string` | IVR destination group name |
| `data[].ivr_hops` | `integer` | Number of IVR hops |
| `data[].ivr_routed_to` | `string` | Where IVR routed the call |
| `data[].ivr_time_spent` | `integer` | Time spent in IVR |
| `data[].minutes_billed` | `integer` | Minutes billed |
| `data[].not_recording_time` | `integer` | Time not recording |
| `data[].outside_business_hours` | `boolean` | Whether call was outside business hours |
| `data[].overflowed` | `boolean` | Whether call overflowed |
| `data[].overflowed_to` | `string` | Where call overflowed to |
| `data[].phone_number` | `string` | Phone number used |
| `data[].phone_number_id` | `integer` | Phone number ID |
| `data[].quality_issues` | `array` | Quality issues detected |
| `data[].recording_control_interactions` | `integer` | Recording control interactions count |
| `data[].recording_time` | `integer` | Recording time |
| `data[].talk_time` | `integer` | Talk time in seconds |
| `data[].ticket_id` | `integer` | Associated ticket ID |
| `data[].time_to_answer` | `integer` | Time to answer in seconds |
| `data[].updated_at` | `string` | Last update timestamp |
| `data[].voicemail` | `boolean` | Whether it was a voicemail |
| `data[].wait_time` | `integer` | Wait time in seconds |
| `data[].wrap_up_time` | `integer` | Wrap-up time in seconds |

</details>

## Call Legs

### Call Legs List

Returns incremental call leg data. Requires a start_time parameter (Unix epoch timestamp).

#### Python SDK

```python
await zendesk_talk.call_legs.list(
    start_time=0
)
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/integrations/connectors/{your_connector_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "call_legs",
    "action": "list",
    "params": {
        "start_time": 0
    }
}'
```


#### Parameters

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `start_time` | `integer` | Yes | Unix epoch time to start from (e.g. 1704067200 for 2024-01-01) |


<details>
<summary><b>Response Schema</b></summary>

#### Records

| Field Name | Type | Description |
|------------|------|-------------|
| `id` | `null \| integer` |  |
| `type` | `null \| string` |  |
| `agent_id` | `null \| integer` |  |
| `available_via` | `null \| string` |  |
| `call_charge` | `null \| string` |  |
| `call_id` | `null \| integer` |  |
| `completion_status` | `null \| string` |  |
| `conference_from` | `null \| integer` |  |
| `conference_time` | `null \| integer` |  |
| `conference_to` | `null \| integer` |  |
| `consultation_from` | `null \| integer` |  |
| `consultation_time` | `null \| integer` |  |
| `consultation_to` | `null \| integer` |  |
| `created_at` | `null \| string` |  |
| `duration` | `null \| integer` |  |
| `forwarded_to` | `null \| string` |  |
| `hold_time` | `null \| integer` |  |
| `minutes_billed` | `null \| integer` |  |
| `quality_issues` | `null \| array` |  |
| `talk_time` | `null \| integer` |  |
| `transferred_from` | `null \| integer` |  |
| `transferred_to` | `null \| integer` |  |
| `updated_at` | `null \| string` |  |
| `user_id` | `null \| integer` |  |
| `wrap_up_time` | `null \| integer` |  |


#### Meta

| Field Name | Type | Description |
|------------|------|-------------|
| `next_page` | `null \| string` |  |
| `count` | `null \| integer` |  |

</details>

### Call Legs Search

Search and filter call legs records powered by Airbyte's data sync. This often provides additional fields and operators beyond what the API natively supports, making it easier to narrow down results before performing further operations. Only available in hosted mode.

#### Python SDK

```python
await zendesk_talk.call_legs.search(
    query={"filter": {"eq": {"agent_id": 0}}}
)
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/integrations/connectors/{your_connector_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "call_legs",
    "action": "search",
    "params": {
        "query": {"filter": {"eq": {"agent_id": 0}}}
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
| `agent_id` | `integer` | Agent ID |
| `available_via` | `string` | Channel agent was available through |
| `call_charge` | `string` | Call charge amount |
| `call_id` | `integer` | Associated call ID |
| `completion_status` | `string` | Completion status |
| `conference_from` | `integer` | Conference from time |
| `conference_time` | `integer` | Conference duration |
| `conference_to` | `integer` | Conference to time |
| `consultation_from` | `integer` | Consultation from time |
| `consultation_time` | `integer` | Consultation duration |
| `consultation_to` | `integer` | Consultation to time |
| `created_at` | `string` | Creation timestamp |
| `duration` | `integer` | Duration in seconds |
| `forwarded_to` | `string` | Number forwarded to |
| `hold_time` | `integer` | Hold time in seconds |
| `id` | `integer` | Call leg ID |
| `minutes_billed` | `integer` | Minutes billed |
| `quality_issues` | `array` | Quality issues detected |
| `talk_time` | `integer` | Talk time in seconds |
| `transferred_from` | `integer` | Transferred from agent ID |
| `transferred_to` | `integer` | Transferred to agent ID |
| `type` | `string` | Type of call leg |
| `updated_at` | `string` | Last update timestamp |
| `user_id` | `integer` | User ID |
| `wrap_up_time` | `integer` | Wrap-up time in seconds |

<details>
<summary><b>Response Schema</b></summary>

| Field Name | Type | Description |
|------------|------|-------------|
| `data` | `array` | List of matching records |
| `meta` | `object` | Pagination metadata |
| `meta.has_more` | `boolean` | Whether additional pages are available |
| `meta.cursor` | `string \| null` | Cursor for next page of results |
| `meta.took_ms` | `number \| null` | Query execution time in milliseconds |
| `data[].agent_id` | `integer` | Agent ID |
| `data[].available_via` | `string` | Channel agent was available through |
| `data[].call_charge` | `string` | Call charge amount |
| `data[].call_id` | `integer` | Associated call ID |
| `data[].completion_status` | `string` | Completion status |
| `data[].conference_from` | `integer` | Conference from time |
| `data[].conference_time` | `integer` | Conference duration |
| `data[].conference_to` | `integer` | Conference to time |
| `data[].consultation_from` | `integer` | Consultation from time |
| `data[].consultation_time` | `integer` | Consultation duration |
| `data[].consultation_to` | `integer` | Consultation to time |
| `data[].created_at` | `string` | Creation timestamp |
| `data[].duration` | `integer` | Duration in seconds |
| `data[].forwarded_to` | `string` | Number forwarded to |
| `data[].hold_time` | `integer` | Hold time in seconds |
| `data[].id` | `integer` | Call leg ID |
| `data[].minutes_billed` | `integer` | Minutes billed |
| `data[].quality_issues` | `array` | Quality issues detected |
| `data[].talk_time` | `integer` | Talk time in seconds |
| `data[].transferred_from` | `integer` | Transferred from agent ID |
| `data[].transferred_to` | `integer` | Transferred to agent ID |
| `data[].type` | `string` | Type of call leg |
| `data[].updated_at` | `string` | Last update timestamp |
| `data[].user_id` | `integer` | User ID |
| `data[].wrap_up_time` | `integer` | Wrap-up time in seconds |

</details>

