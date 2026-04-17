# Twilio full reference

This is the full reference documentation for the Twilio agent connector.

## Supported entities and actions

The Twilio connector supports the following entities and actions.

| Entity | Actions |
|--------|---------|
| Accounts | [List](#accounts-list), [Get](#accounts-get), [Search](#accounts-search) |
| Calls | [List](#calls-list), [Get](#calls-get), [Search](#calls-search) |
| Messages | [List](#messages-list), [Get](#messages-get), [Search](#messages-search) |
| Incoming Phone Numbers | [List](#incoming-phone-numbers-list), [Get](#incoming-phone-numbers-get), [Search](#incoming-phone-numbers-search) |
| Recordings | [List](#recordings-list), [Get](#recordings-get), [Search](#recordings-search) |
| Conferences | [List](#conferences-list), [Get](#conferences-get), [Search](#conferences-search) |
| Usage Records | [List](#usage-records-list), [Search](#usage-records-search) |
| Addresses | [List](#addresses-list), [Get](#addresses-get), [Search](#addresses-search) |
| Queues | [List](#queues-list), [Get](#queues-get), [Search](#queues-search) |
| Transcriptions | [List](#transcriptions-list), [Get](#transcriptions-get), [Search](#transcriptions-search) |
| Outgoing Caller Ids | [List](#outgoing-caller-ids-list), [Get](#outgoing-caller-ids-get), [Search](#outgoing-caller-ids-search) |

## Accounts

### Accounts List

Returns a list of accounts associated with the authenticated account

#### Python SDK

```python
await twilio.accounts.list()
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/integrations/connectors/{your_connector_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "accounts",
    "action": "list"
}'
```


#### Parameters

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `PageSize` | `integer` | No | Number of items to return per page |


<details>
<summary><b>Response Schema</b></summary>

#### Records

| Field Name | Type | Description |
|------------|------|-------------|
| `auth_token` | `null \| string` |  |
| `date_created` | `null \| string` |  |
| `date_updated` | `null \| string` |  |
| `friendly_name` | `null \| string` |  |
| `owner_account_sid` | `null \| string` |  |
| `sid` | `null \| string` |  |
| `status` | `null \| string` |  |
| `subresource_uris` | `null \| object` |  |
| `type` | `null \| string` |  |
| `uri` | `null \| string` |  |


#### Meta

| Field Name | Type | Description |
|------------|------|-------------|
| `next_page_uri` | `null \| string` |  |
| `first_page_uri` | `null \| string` |  |
| `page` | `null \| integer` |  |
| `page_size` | `null \| integer` |  |

</details>

### Accounts Get

Get a single account by SID

#### Python SDK

```python
await twilio.accounts.get(
    sid="<str>"
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
        "sid": "<str>"
    }
}'
```


#### Parameters

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `sid` | `string` | Yes | Account SID |


<details>
<summary><b>Response Schema</b></summary>

#### Records

| Field Name | Type | Description |
|------------|------|-------------|
| `auth_token` | `null \| string` |  |
| `date_created` | `null \| string` |  |
| `date_updated` | `null \| string` |  |
| `friendly_name` | `null \| string` |  |
| `owner_account_sid` | `null \| string` |  |
| `sid` | `null \| string` |  |
| `status` | `null \| string` |  |
| `subresource_uris` | `null \| object` |  |
| `type` | `null \| string` |  |
| `uri` | `null \| string` |  |


</details>

### Accounts Search

Search and filter accounts records powered by Airbyte's data sync. This often provides additional fields and operators beyond what the API natively supports, making it easier to narrow down results before performing further operations. Only available in hosted mode.

#### Python SDK

```python
await twilio.accounts.search(
    query={"filter": {"eq": {"sid": "<str>"}}}
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
        "query": {"filter": {"eq": {"sid": "<str>"}}}
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
| `sid` | `string` | The unique identifier for the account |
| `friendly_name` | `string` | A user-defined friendly name for the account |
| `status` | `string` | The current status of the account |
| `type` | `string` | The type of the account |
| `owner_account_sid` | `string` | The SID of the owner account |
| `date_created` | `string` | The timestamp when the account was created |
| `date_updated` | `string` | The timestamp when the account was last updated |
| `uri` | `string` | The URI for accessing the account resource |

<details>
<summary><b>Response Schema</b></summary>

| Field Name | Type | Description |
|------------|------|-------------|
| `data` | `array` | List of matching records |
| `meta` | `object` | Pagination metadata |
| `meta.has_more` | `boolean` | Whether additional pages are available |
| `meta.cursor` | `string \| null` | Cursor for next page of results |
| `meta.took_ms` | `number \| null` | Query execution time in milliseconds |
| `data[].sid` | `string` | The unique identifier for the account |
| `data[].friendly_name` | `string` | A user-defined friendly name for the account |
| `data[].status` | `string` | The current status of the account |
| `data[].type` | `string` | The type of the account |
| `data[].owner_account_sid` | `string` | The SID of the owner account |
| `data[].date_created` | `string` | The timestamp when the account was created |
| `data[].date_updated` | `string` | The timestamp when the account was last updated |
| `data[].uri` | `string` | The URI for accessing the account resource |

</details>

## Calls

### Calls List

Returns a list of calls made to and from an account

#### Python SDK

```python
await twilio.calls.list(
    account_sid="<str>"
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
        "AccountSid": "<str>"
    }
}'
```


#### Parameters

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `AccountSid` | `string` | Yes | Account SID |
| `PageSize` | `integer` | No | Number of items to return per page |


<details>
<summary><b>Response Schema</b></summary>

#### Records

| Field Name | Type | Description |
|------------|------|-------------|
| `sid` | `null \| string` |  |
| `date_created` | `null \| string` |  |
| `date_updated` | `null \| string` |  |
| `parent_call_sid` | `null \| string` |  |
| `account_sid` | `null \| string` |  |
| `to` | `null \| string` |  |
| `to_formatted` | `null \| string` |  |
| `from` | `null \| string` |  |
| `from_formatted` | `null \| string` |  |
| `phone_number_sid` | `null \| string` |  |
| `status` | `null \| string` |  |
| `start_time` | `null \| string` |  |
| `end_time` | `null \| string` |  |
| `duration` | `null \| string` |  |
| `price` | `null \| string` |  |
| `price_unit` | `null \| string` |  |
| `direction` | `null \| string` |  |
| `answered_by` | `null \| string` |  |
| `annotation` | `null \| string` |  |
| `api_version` | `null \| string` |  |
| `forwarded_from` | `null \| string` |  |
| `group_sid` | `null \| string` |  |
| `caller_name` | `null \| string` |  |
| `queue_time` | `null \| string` |  |
| `trunk_sid` | `null \| string` |  |
| `uri` | `null \| string` |  |
| `subresource_uris` | `null \| object` |  |


#### Meta

| Field Name | Type | Description |
|------------|------|-------------|
| `next_page_uri` | `null \| string` |  |
| `first_page_uri` | `null \| string` |  |
| `page` | `null \| integer` |  |
| `page_size` | `null \| integer` |  |

</details>

### Calls Get

Get a single call by SID

#### Python SDK

```python
await twilio.calls.get(
    account_sid="<str>",
    sid="<str>"
)
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/integrations/connectors/{your_connector_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "calls",
    "action": "get",
    "params": {
        "AccountSid": "<str>",
        "sid": "<str>"
    }
}'
```


#### Parameters

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `AccountSid` | `string` | Yes | Account SID |
| `sid` | `string` | Yes | Call SID |


<details>
<summary><b>Response Schema</b></summary>

#### Records

| Field Name | Type | Description |
|------------|------|-------------|
| `sid` | `null \| string` |  |
| `date_created` | `null \| string` |  |
| `date_updated` | `null \| string` |  |
| `parent_call_sid` | `null \| string` |  |
| `account_sid` | `null \| string` |  |
| `to` | `null \| string` |  |
| `to_formatted` | `null \| string` |  |
| `from` | `null \| string` |  |
| `from_formatted` | `null \| string` |  |
| `phone_number_sid` | `null \| string` |  |
| `status` | `null \| string` |  |
| `start_time` | `null \| string` |  |
| `end_time` | `null \| string` |  |
| `duration` | `null \| string` |  |
| `price` | `null \| string` |  |
| `price_unit` | `null \| string` |  |
| `direction` | `null \| string` |  |
| `answered_by` | `null \| string` |  |
| `annotation` | `null \| string` |  |
| `api_version` | `null \| string` |  |
| `forwarded_from` | `null \| string` |  |
| `group_sid` | `null \| string` |  |
| `caller_name` | `null \| string` |  |
| `queue_time` | `null \| string` |  |
| `trunk_sid` | `null \| string` |  |
| `uri` | `null \| string` |  |
| `subresource_uris` | `null \| object` |  |


</details>

### Calls Search

Search and filter calls records powered by Airbyte's data sync. This often provides additional fields and operators beyond what the API natively supports, making it easier to narrow down results before performing further operations. Only available in hosted mode.

#### Python SDK

```python
await twilio.calls.search(
    query={"filter": {"eq": {"sid": "<str>"}}}
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
        "query": {"filter": {"eq": {"sid": "<str>"}}}
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
| `sid` | `string` | The unique identifier for the call |
| `account_sid` | `string` | The unique identifier for the account associated with the call |
| `to` | `string` | The phone number that received the call |
| `from` | `string` | The phone number that made the call |
| `status` | `string` | The current status of the call |
| `direction` | `string` | The direction of the call (inbound or outbound) |
| `duration` | `string` | The duration of the call in seconds |
| `price` | `string` | The cost of the call |
| `price_unit` | `string` | The currency unit of the call cost |
| `start_time` | `string` | The date and time when the call started |
| `end_time` | `string` | The date and time when the call ended |
| `date_created` | `string` | The date and time when the call record was created |
| `date_updated` | `string` | The date and time when the call record was last updated |

<details>
<summary><b>Response Schema</b></summary>

| Field Name | Type | Description |
|------------|------|-------------|
| `data` | `array` | List of matching records |
| `meta` | `object` | Pagination metadata |
| `meta.has_more` | `boolean` | Whether additional pages are available |
| `meta.cursor` | `string \| null` | Cursor for next page of results |
| `meta.took_ms` | `number \| null` | Query execution time in milliseconds |
| `data[].sid` | `string` | The unique identifier for the call |
| `data[].account_sid` | `string` | The unique identifier for the account associated with the call |
| `data[].to` | `string` | The phone number that received the call |
| `data[].from` | `string` | The phone number that made the call |
| `data[].status` | `string` | The current status of the call |
| `data[].direction` | `string` | The direction of the call (inbound or outbound) |
| `data[].duration` | `string` | The duration of the call in seconds |
| `data[].price` | `string` | The cost of the call |
| `data[].price_unit` | `string` | The currency unit of the call cost |
| `data[].start_time` | `string` | The date and time when the call started |
| `data[].end_time` | `string` | The date and time when the call ended |
| `data[].date_created` | `string` | The date and time when the call record was created |
| `data[].date_updated` | `string` | The date and time when the call record was last updated |

</details>

## Messages

### Messages List

Returns a list of messages associated with an account

#### Python SDK

```python
await twilio.messages.list(
    account_sid="<str>"
)
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/integrations/connectors/{your_connector_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "messages",
    "action": "list",
    "params": {
        "AccountSid": "<str>"
    }
}'
```


#### Parameters

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `AccountSid` | `string` | Yes | Account SID |
| `PageSize` | `integer` | No | Number of items to return per page |


<details>
<summary><b>Response Schema</b></summary>

#### Records

| Field Name | Type | Description |
|------------|------|-------------|
| `account_sid` | `null \| string` |  |
| `api_version` | `null \| string` |  |
| `body` | `null \| string` |  |
| `date_created` | `null \| string` |  |
| `date_sent` | `null \| string` |  |
| `date_updated` | `null \| string` |  |
| `direction` | `null \| string` |  |
| `error_code` | `null \| string` |  |
| `error_message` | `null \| string` |  |
| `from` | `null \| string` |  |
| `messaging_service_sid` | `null \| string` |  |
| `num_media` | `null \| string` |  |
| `num_segments` | `null \| string` |  |
| `price` | `null \| string` |  |
| `price_unit` | `null \| string` |  |
| `sid` | `null \| string` |  |
| `status` | `null \| string` |  |
| `subresource_uris` | `null \| object` |  |
| `to` | `null \| string` |  |
| `uri` | `null \| string` |  |


#### Meta

| Field Name | Type | Description |
|------------|------|-------------|
| `next_page_uri` | `null \| string` |  |
| `first_page_uri` | `null \| string` |  |
| `page` | `null \| integer` |  |
| `page_size` | `null \| integer` |  |

</details>

### Messages Get

Get a single message by SID

#### Python SDK

```python
await twilio.messages.get(
    account_sid="<str>",
    sid="<str>"
)
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/integrations/connectors/{your_connector_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "messages",
    "action": "get",
    "params": {
        "AccountSid": "<str>",
        "sid": "<str>"
    }
}'
```


#### Parameters

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `AccountSid` | `string` | Yes | Account SID |
| `sid` | `string` | Yes | Message SID |


<details>
<summary><b>Response Schema</b></summary>

#### Records

| Field Name | Type | Description |
|------------|------|-------------|
| `account_sid` | `null \| string` |  |
| `api_version` | `null \| string` |  |
| `body` | `null \| string` |  |
| `date_created` | `null \| string` |  |
| `date_sent` | `null \| string` |  |
| `date_updated` | `null \| string` |  |
| `direction` | `null \| string` |  |
| `error_code` | `null \| string` |  |
| `error_message` | `null \| string` |  |
| `from` | `null \| string` |  |
| `messaging_service_sid` | `null \| string` |  |
| `num_media` | `null \| string` |  |
| `num_segments` | `null \| string` |  |
| `price` | `null \| string` |  |
| `price_unit` | `null \| string` |  |
| `sid` | `null \| string` |  |
| `status` | `null \| string` |  |
| `subresource_uris` | `null \| object` |  |
| `to` | `null \| string` |  |
| `uri` | `null \| string` |  |


</details>

### Messages Search

Search and filter messages records powered by Airbyte's data sync. This often provides additional fields and operators beyond what the API natively supports, making it easier to narrow down results before performing further operations. Only available in hosted mode.

#### Python SDK

```python
await twilio.messages.search(
    query={"filter": {"eq": {"sid": "<str>"}}}
)
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/integrations/connectors/{your_connector_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "messages",
    "action": "search",
    "params": {
        "query": {"filter": {"eq": {"sid": "<str>"}}}
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
| `sid` | `string` | The unique identifier for this message |
| `account_sid` | `string` | The unique identifier for the account associated with this message |
| `to` | `string` | The phone number or recipient ID the message was sent to |
| `from` | `string` | The phone number or sender ID that sent the message |
| `body` | `string` | The text body of the message |
| `status` | `string` | The status of the message |
| `direction` | `string` | The direction of the message |
| `price` | `string` | The cost of the message |
| `price_unit` | `string` | The currency unit used for pricing |
| `date_created` | `string` | The date and time when the message was created |
| `date_sent` | `string` | The date and time when the message was sent |
| `error_code` | `string` | The error code associated with the message if any |
| `error_message` | `string` | The error message description if the message failed |
| `num_segments` | `string` | The number of message segments |
| `num_media` | `string` | The number of media files included in the message |

<details>
<summary><b>Response Schema</b></summary>

| Field Name | Type | Description |
|------------|------|-------------|
| `data` | `array` | List of matching records |
| `meta` | `object` | Pagination metadata |
| `meta.has_more` | `boolean` | Whether additional pages are available |
| `meta.cursor` | `string \| null` | Cursor for next page of results |
| `meta.took_ms` | `number \| null` | Query execution time in milliseconds |
| `data[].sid` | `string` | The unique identifier for this message |
| `data[].account_sid` | `string` | The unique identifier for the account associated with this message |
| `data[].to` | `string` | The phone number or recipient ID the message was sent to |
| `data[].from` | `string` | The phone number or sender ID that sent the message |
| `data[].body` | `string` | The text body of the message |
| `data[].status` | `string` | The status of the message |
| `data[].direction` | `string` | The direction of the message |
| `data[].price` | `string` | The cost of the message |
| `data[].price_unit` | `string` | The currency unit used for pricing |
| `data[].date_created` | `string` | The date and time when the message was created |
| `data[].date_sent` | `string` | The date and time when the message was sent |
| `data[].error_code` | `string` | The error code associated with the message if any |
| `data[].error_message` | `string` | The error message description if the message failed |
| `data[].num_segments` | `string` | The number of message segments |
| `data[].num_media` | `string` | The number of media files included in the message |

</details>

## Incoming Phone Numbers

### Incoming Phone Numbers List

Returns a list of incoming phone numbers for an account

#### Python SDK

```python
await twilio.incoming_phone_numbers.list(
    account_sid="<str>"
)
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/integrations/connectors/{your_connector_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "incoming_phone_numbers",
    "action": "list",
    "params": {
        "AccountSid": "<str>"
    }
}'
```


#### Parameters

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `AccountSid` | `string` | Yes | Account SID |
| `PageSize` | `integer` | No | Number of items to return per page |


<details>
<summary><b>Response Schema</b></summary>

#### Records

| Field Name | Type | Description |
|------------|------|-------------|
| `sid` | `null \| string` |  |
| `account_sid` | `null \| string` |  |
| `friendly_name` | `null \| string` |  |
| `phone_number` | `null \| string` |  |
| `voice_url` | `null \| string` |  |
| `voice_method` | `null \| string` |  |
| `voice_fallback_url` | `null \| string` |  |
| `voice_fallback_method` | `null \| string` |  |
| `voice_caller_id_lookup` | `null \| boolean` |  |
| `date_created` | `null \| string` |  |
| `date_updated` | `null \| string` |  |
| `sms_url` | `null \| string` |  |
| `sms_method` | `null \| string` |  |
| `sms_fallback_url` | `null \| string` |  |
| `sms_fallback_method` | `null \| string` |  |
| `address_requirements` | `null \| string` |  |
| `beta` | `null \| boolean` |  |
| `capabilities` | `null \| object` |  |
| `voice_receive_mode` | `null \| string` |  |
| `status_callback` | `null \| string` |  |
| `status_callback_method` | `null \| string` |  |
| `api_version` | `null \| string` |  |
| `voice_application_sid` | `null \| string` |  |
| `sms_application_sid` | `null \| string` |  |
| `origin` | `null \| string` |  |
| `trunk_sid` | `null \| string` |  |
| `emergency_status` | `null \| string` |  |
| `emergency_address_sid` | `null \| string` |  |
| `emergency_address_status` | `null \| string` |  |
| `address_sid` | `null \| string` |  |
| `identity_sid` | `null \| string` |  |
| `bundle_sid` | `null \| string` |  |
| `uri` | `null \| string` |  |
| `status` | `null \| string` |  |
| `type` | `null \| string` |  |
| `subresource_uris` | `null \| object` |  |


#### Meta

| Field Name | Type | Description |
|------------|------|-------------|
| `next_page_uri` | `null \| string` |  |
| `first_page_uri` | `null \| string` |  |
| `page` | `null \| integer` |  |
| `page_size` | `null \| integer` |  |

</details>

### Incoming Phone Numbers Get

Get a single incoming phone number by SID

#### Python SDK

```python
await twilio.incoming_phone_numbers.get(
    account_sid="<str>",
    sid="<str>"
)
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/integrations/connectors/{your_connector_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "incoming_phone_numbers",
    "action": "get",
    "params": {
        "AccountSid": "<str>",
        "sid": "<str>"
    }
}'
```


#### Parameters

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `AccountSid` | `string` | Yes | Account SID |
| `sid` | `string` | Yes | Incoming phone number SID |


<details>
<summary><b>Response Schema</b></summary>

#### Records

| Field Name | Type | Description |
|------------|------|-------------|
| `sid` | `null \| string` |  |
| `account_sid` | `null \| string` |  |
| `friendly_name` | `null \| string` |  |
| `phone_number` | `null \| string` |  |
| `voice_url` | `null \| string` |  |
| `voice_method` | `null \| string` |  |
| `voice_fallback_url` | `null \| string` |  |
| `voice_fallback_method` | `null \| string` |  |
| `voice_caller_id_lookup` | `null \| boolean` |  |
| `date_created` | `null \| string` |  |
| `date_updated` | `null \| string` |  |
| `sms_url` | `null \| string` |  |
| `sms_method` | `null \| string` |  |
| `sms_fallback_url` | `null \| string` |  |
| `sms_fallback_method` | `null \| string` |  |
| `address_requirements` | `null \| string` |  |
| `beta` | `null \| boolean` |  |
| `capabilities` | `null \| object` |  |
| `voice_receive_mode` | `null \| string` |  |
| `status_callback` | `null \| string` |  |
| `status_callback_method` | `null \| string` |  |
| `api_version` | `null \| string` |  |
| `voice_application_sid` | `null \| string` |  |
| `sms_application_sid` | `null \| string` |  |
| `origin` | `null \| string` |  |
| `trunk_sid` | `null \| string` |  |
| `emergency_status` | `null \| string` |  |
| `emergency_address_sid` | `null \| string` |  |
| `emergency_address_status` | `null \| string` |  |
| `address_sid` | `null \| string` |  |
| `identity_sid` | `null \| string` |  |
| `bundle_sid` | `null \| string` |  |
| `uri` | `null \| string` |  |
| `status` | `null \| string` |  |
| `type` | `null \| string` |  |
| `subresource_uris` | `null \| object` |  |


</details>

### Incoming Phone Numbers Search

Search and filter incoming phone numbers records powered by Airbyte's data sync. This often provides additional fields and operators beyond what the API natively supports, making it easier to narrow down results before performing further operations. Only available in hosted mode.

#### Python SDK

```python
await twilio.incoming_phone_numbers.search(
    query={"filter": {"eq": {"sid": "<str>"}}}
)
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/integrations/connectors/{your_connector_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "incoming_phone_numbers",
    "action": "search",
    "params": {
        "query": {"filter": {"eq": {"sid": "<str>"}}}
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
| `sid` | `string` | The SID of this phone number |
| `account_sid` | `string` | The SID of the account that owns this phone number |
| `phone_number` | `string` | The phone number in E.164 format |
| `friendly_name` | `string` | A user-assigned friendly name for this phone number |
| `status` | `string` | Status of the phone number |
| `capabilities` | `object` | Capabilities of this phone number |
| `date_created` | `string` | When the phone number was created |
| `date_updated` | `string` | When the phone number was last updated |

<details>
<summary><b>Response Schema</b></summary>

| Field Name | Type | Description |
|------------|------|-------------|
| `data` | `array` | List of matching records |
| `meta` | `object` | Pagination metadata |
| `meta.has_more` | `boolean` | Whether additional pages are available |
| `meta.cursor` | `string \| null` | Cursor for next page of results |
| `meta.took_ms` | `number \| null` | Query execution time in milliseconds |
| `data[].sid` | `string` | The SID of this phone number |
| `data[].account_sid` | `string` | The SID of the account that owns this phone number |
| `data[].phone_number` | `string` | The phone number in E.164 format |
| `data[].friendly_name` | `string` | A user-assigned friendly name for this phone number |
| `data[].status` | `string` | Status of the phone number |
| `data[].capabilities` | `object` | Capabilities of this phone number |
| `data[].date_created` | `string` | When the phone number was created |
| `data[].date_updated` | `string` | When the phone number was last updated |

</details>

## Recordings

### Recordings List

Returns a list of recordings for an account

#### Python SDK

```python
await twilio.recordings.list(
    account_sid="<str>"
)
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/integrations/connectors/{your_connector_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "recordings",
    "action": "list",
    "params": {
        "AccountSid": "<str>"
    }
}'
```


#### Parameters

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `AccountSid` | `string` | Yes | Account SID |
| `PageSize` | `integer` | No | Number of items to return per page |


<details>
<summary><b>Response Schema</b></summary>

#### Records

| Field Name | Type | Description |
|------------|------|-------------|
| `account_sid` | `null \| string` |  |
| `api_version` | `null \| string` |  |
| `call_sid` | `null \| string` |  |
| `conference_sid` | `null \| string` |  |
| `date_created` | `null \| string` |  |
| `date_updated` | `null \| string` |  |
| `start_time` | `null \| string` |  |
| `duration` | `null \| string` |  |
| `sid` | `null \| string` |  |
| `price` | `null \| string` |  |
| `price_unit` | `null \| string` |  |
| `status` | `null \| string` |  |
| `channels` | `null \| integer` |  |
| `source` | `null \| string` |  |
| `error_code` | `null \| string` |  |
| `media_url` | `null \| string` |  |
| `uri` | `null \| string` |  |
| `encryption_details` | `null \| object` |  |
| `subresource_uris` | `null \| object` |  |


#### Meta

| Field Name | Type | Description |
|------------|------|-------------|
| `next_page_uri` | `null \| string` |  |
| `first_page_uri` | `null \| string` |  |
| `page` | `null \| integer` |  |
| `page_size` | `null \| integer` |  |

</details>

### Recordings Get

Get a single recording by SID

#### Python SDK

```python
await twilio.recordings.get(
    account_sid="<str>",
    sid="<str>"
)
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/integrations/connectors/{your_connector_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "recordings",
    "action": "get",
    "params": {
        "AccountSid": "<str>",
        "sid": "<str>"
    }
}'
```


#### Parameters

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `AccountSid` | `string` | Yes | Account SID |
| `sid` | `string` | Yes | Recording SID |


<details>
<summary><b>Response Schema</b></summary>

#### Records

| Field Name | Type | Description |
|------------|------|-------------|
| `account_sid` | `null \| string` |  |
| `api_version` | `null \| string` |  |
| `call_sid` | `null \| string` |  |
| `conference_sid` | `null \| string` |  |
| `date_created` | `null \| string` |  |
| `date_updated` | `null \| string` |  |
| `start_time` | `null \| string` |  |
| `duration` | `null \| string` |  |
| `sid` | `null \| string` |  |
| `price` | `null \| string` |  |
| `price_unit` | `null \| string` |  |
| `status` | `null \| string` |  |
| `channels` | `null \| integer` |  |
| `source` | `null \| string` |  |
| `error_code` | `null \| string` |  |
| `media_url` | `null \| string` |  |
| `uri` | `null \| string` |  |
| `encryption_details` | `null \| object` |  |
| `subresource_uris` | `null \| object` |  |


</details>

### Recordings Search

Search and filter recordings records powered by Airbyte's data sync. This often provides additional fields and operators beyond what the API natively supports, making it easier to narrow down results before performing further operations. Only available in hosted mode.

#### Python SDK

```python
await twilio.recordings.search(
    query={"filter": {"eq": {"sid": "<str>"}}}
)
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/integrations/connectors/{your_connector_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "recordings",
    "action": "search",
    "params": {
        "query": {"filter": {"eq": {"sid": "<str>"}}}
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
| `sid` | `string` | The unique identifier of the recording |
| `account_sid` | `string` | The account SID that owns the recording |
| `call_sid` | `string` | The SID of the associated call |
| `duration` | `string` | Duration in seconds |
| `status` | `string` | The status of the recording |
| `channels` | `integer` | Number of audio channels |
| `price` | `string` | The cost of storing the recording |
| `price_unit` | `string` | The currency unit |
| `date_created` | `string` | When the recording was created |
| `start_time` | `string` | When the recording started |

<details>
<summary><b>Response Schema</b></summary>

| Field Name | Type | Description |
|------------|------|-------------|
| `data` | `array` | List of matching records |
| `meta` | `object` | Pagination metadata |
| `meta.has_more` | `boolean` | Whether additional pages are available |
| `meta.cursor` | `string \| null` | Cursor for next page of results |
| `meta.took_ms` | `number \| null` | Query execution time in milliseconds |
| `data[].sid` | `string` | The unique identifier of the recording |
| `data[].account_sid` | `string` | The account SID that owns the recording |
| `data[].call_sid` | `string` | The SID of the associated call |
| `data[].duration` | `string` | Duration in seconds |
| `data[].status` | `string` | The status of the recording |
| `data[].channels` | `integer` | Number of audio channels |
| `data[].price` | `string` | The cost of storing the recording |
| `data[].price_unit` | `string` | The currency unit |
| `data[].date_created` | `string` | When the recording was created |
| `data[].start_time` | `string` | When the recording started |

</details>

## Conferences

### Conferences List

Returns a list of conferences for an account

#### Python SDK

```python
await twilio.conferences.list(
    account_sid="<str>"
)
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/integrations/connectors/{your_connector_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "conferences",
    "action": "list",
    "params": {
        "AccountSid": "<str>"
    }
}'
```


#### Parameters

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `AccountSid` | `string` | Yes | Account SID |
| `PageSize` | `integer` | No | Number of items to return per page |


<details>
<summary><b>Response Schema</b></summary>

#### Records

| Field Name | Type | Description |
|------------|------|-------------|
| `account_sid` | `null \| string` |  |
| `date_created` | `null \| string` |  |
| `date_updated` | `null \| string` |  |
| `api_version` | `null \| string` |  |
| `friendly_name` | `null \| string` |  |
| `region` | `null \| string` |  |
| `sid` | `null \| string` |  |
| `status` | `null \| string` |  |
| `uri` | `null \| string` |  |
| `reason_conference_ended` | `null \| string` |  |
| `call_sid_ending_conference` | `null \| string` |  |
| `subresource_uris` | `null \| object` |  |


#### Meta

| Field Name | Type | Description |
|------------|------|-------------|
| `next_page_uri` | `null \| string` |  |
| `first_page_uri` | `null \| string` |  |
| `page` | `null \| integer` |  |
| `page_size` | `null \| integer` |  |

</details>

### Conferences Get

Get a single conference by SID

#### Python SDK

```python
await twilio.conferences.get(
    account_sid="<str>",
    sid="<str>"
)
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/integrations/connectors/{your_connector_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "conferences",
    "action": "get",
    "params": {
        "AccountSid": "<str>",
        "sid": "<str>"
    }
}'
```


#### Parameters

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `AccountSid` | `string` | Yes | Account SID |
| `sid` | `string` | Yes | Conference SID |


<details>
<summary><b>Response Schema</b></summary>

#### Records

| Field Name | Type | Description |
|------------|------|-------------|
| `account_sid` | `null \| string` |  |
| `date_created` | `null \| string` |  |
| `date_updated` | `null \| string` |  |
| `api_version` | `null \| string` |  |
| `friendly_name` | `null \| string` |  |
| `region` | `null \| string` |  |
| `sid` | `null \| string` |  |
| `status` | `null \| string` |  |
| `uri` | `null \| string` |  |
| `reason_conference_ended` | `null \| string` |  |
| `call_sid_ending_conference` | `null \| string` |  |
| `subresource_uris` | `null \| object` |  |


</details>

### Conferences Search

Search and filter conferences records powered by Airbyte's data sync. This often provides additional fields and operators beyond what the API natively supports, making it easier to narrow down results before performing further operations. Only available in hosted mode.

#### Python SDK

```python
await twilio.conferences.search(
    query={"filter": {"eq": {"sid": "<str>"}}}
)
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/integrations/connectors/{your_connector_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "conferences",
    "action": "search",
    "params": {
        "query": {"filter": {"eq": {"sid": "<str>"}}}
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
| `sid` | `string` | The unique identifier of the conference |
| `account_sid` | `string` | The account SID associated with the conference |
| `friendly_name` | `string` | A friendly name for the conference |
| `status` | `string` | The current status of the conference |
| `region` | `string` | The region where the conference is hosted |
| `date_created` | `string` | When the conference was created |
| `date_updated` | `string` | When the conference was last updated |

<details>
<summary><b>Response Schema</b></summary>

| Field Name | Type | Description |
|------------|------|-------------|
| `data` | `array` | List of matching records |
| `meta` | `object` | Pagination metadata |
| `meta.has_more` | `boolean` | Whether additional pages are available |
| `meta.cursor` | `string \| null` | Cursor for next page of results |
| `meta.took_ms` | `number \| null` | Query execution time in milliseconds |
| `data[].sid` | `string` | The unique identifier of the conference |
| `data[].account_sid` | `string` | The account SID associated with the conference |
| `data[].friendly_name` | `string` | A friendly name for the conference |
| `data[].status` | `string` | The current status of the conference |
| `data[].region` | `string` | The region where the conference is hosted |
| `data[].date_created` | `string` | When the conference was created |
| `data[].date_updated` | `string` | When the conference was last updated |

</details>

## Usage Records

### Usage Records List

Returns a list of usage records for an account

#### Python SDK

```python
await twilio.usage_records.list(
    account_sid="<str>"
)
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/integrations/connectors/{your_connector_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "usage_records",
    "action": "list",
    "params": {
        "AccountSid": "<str>"
    }
}'
```


#### Parameters

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `AccountSid` | `string` | Yes | Account SID |
| `PageSize` | `integer` | No | Number of items to return per page |


<details>
<summary><b>Response Schema</b></summary>

#### Records

| Field Name | Type | Description |
|------------|------|-------------|
| `account_sid` | `null \| string` |  |
| `api_version` | `null \| string` |  |
| `as_of` | `null \| string` |  |
| `category` | `null \| string` |  |
| `count` | `null \| string` |  |
| `count_unit` | `null \| string` |  |
| `description` | `null \| string` |  |
| `end_date` | `null \| string` |  |
| `price` | `null \| string` |  |
| `price_unit` | `null \| string` |  |
| `start_date` | `null \| string` |  |
| `subresource_uris` | `null \| object` |  |
| `usage` | `null \| string` |  |
| `usage_unit` | `null \| string` |  |
| `uri` | `null \| string` |  |


#### Meta

| Field Name | Type | Description |
|------------|------|-------------|
| `next_page_uri` | `null \| string` |  |
| `first_page_uri` | `null \| string` |  |
| `page` | `null \| integer` |  |
| `page_size` | `null \| integer` |  |

</details>

### Usage Records Search

Search and filter usage records records powered by Airbyte's data sync. This often provides additional fields and operators beyond what the API natively supports, making it easier to narrow down results before performing further operations. Only available in hosted mode.

#### Python SDK

```python
await twilio.usage_records.search(
    query={"filter": {"eq": {"account_sid": "<str>"}}}
)
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/integrations/connectors/{your_connector_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "usage_records",
    "action": "search",
    "params": {
        "query": {"filter": {"eq": {"account_sid": "<str>"}}}
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
| `account_sid` | `string` | The account SID associated with this usage record |
| `category` | `string` | The usage category (calls, SMS, recordings, etc.) |
| `description` | `string` | A description of the usage record |
| `usage` | `string` | The total usage value |
| `usage_unit` | `string` | The unit of measurement for usage |
| `count` | `string` | The number of units consumed |
| `count_unit` | `string` | The unit of measurement for count |
| `price` | `string` | The total price for consumed units |
| `price_unit` | `string` | The currency unit |
| `start_date` | `string` | The start date of the usage period |
| `end_date` | `string` | The end date of the usage period |

<details>
<summary><b>Response Schema</b></summary>

| Field Name | Type | Description |
|------------|------|-------------|
| `data` | `array` | List of matching records |
| `meta` | `object` | Pagination metadata |
| `meta.has_more` | `boolean` | Whether additional pages are available |
| `meta.cursor` | `string \| null` | Cursor for next page of results |
| `meta.took_ms` | `number \| null` | Query execution time in milliseconds |
| `data[].account_sid` | `string` | The account SID associated with this usage record |
| `data[].category` | `string` | The usage category (calls, SMS, recordings, etc.) |
| `data[].description` | `string` | A description of the usage record |
| `data[].usage` | `string` | The total usage value |
| `data[].usage_unit` | `string` | The unit of measurement for usage |
| `data[].count` | `string` | The number of units consumed |
| `data[].count_unit` | `string` | The unit of measurement for count |
| `data[].price` | `string` | The total price for consumed units |
| `data[].price_unit` | `string` | The currency unit |
| `data[].start_date` | `string` | The start date of the usage period |
| `data[].end_date` | `string` | The end date of the usage period |

</details>

## Addresses

### Addresses List

Returns a list of addresses for an account

#### Python SDK

```python
await twilio.addresses.list(
    account_sid="<str>"
)
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/integrations/connectors/{your_connector_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "addresses",
    "action": "list",
    "params": {
        "AccountSid": "<str>"
    }
}'
```


#### Parameters

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `AccountSid` | `string` | Yes | Account SID |
| `PageSize` | `integer` | No | Number of items to return per page |


<details>
<summary><b>Response Schema</b></summary>

#### Records

| Field Name | Type | Description |
|------------|------|-------------|
| `account_sid` | `null \| string` |  |
| `city` | `null \| string` |  |
| `customer_name` | `null \| string` |  |
| `date_created` | `null \| string` |  |
| `date_updated` | `null \| string` |  |
| `emergency_enabled` | `null \| boolean` |  |
| `friendly_name` | `null \| string` |  |
| `iso_country` | `null \| string` |  |
| `postal_code` | `null \| string` |  |
| `region` | `null \| string` |  |
| `sid` | `null \| string` |  |
| `street` | `null \| string` |  |
| `street_secondary` | `null \| string` |  |
| `validated` | `null \| boolean` |  |
| `verified` | `null \| boolean` |  |
| `uri` | `null \| string` |  |


#### Meta

| Field Name | Type | Description |
|------------|------|-------------|
| `next_page_uri` | `null \| string` |  |
| `first_page_uri` | `null \| string` |  |
| `page` | `null \| integer` |  |
| `page_size` | `null \| integer` |  |

</details>

### Addresses Get

Get a single address by SID

#### Python SDK

```python
await twilio.addresses.get(
    account_sid="<str>",
    sid="<str>"
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
        "AccountSid": "<str>",
        "sid": "<str>"
    }
}'
```


#### Parameters

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `AccountSid` | `string` | Yes | Account SID |
| `sid` | `string` | Yes | Address SID |


<details>
<summary><b>Response Schema</b></summary>

#### Records

| Field Name | Type | Description |
|------------|------|-------------|
| `account_sid` | `null \| string` |  |
| `city` | `null \| string` |  |
| `customer_name` | `null \| string` |  |
| `date_created` | `null \| string` |  |
| `date_updated` | `null \| string` |  |
| `emergency_enabled` | `null \| boolean` |  |
| `friendly_name` | `null \| string` |  |
| `iso_country` | `null \| string` |  |
| `postal_code` | `null \| string` |  |
| `region` | `null \| string` |  |
| `sid` | `null \| string` |  |
| `street` | `null \| string` |  |
| `street_secondary` | `null \| string` |  |
| `validated` | `null \| boolean` |  |
| `verified` | `null \| boolean` |  |
| `uri` | `null \| string` |  |


</details>

### Addresses Search

Search and filter addresses records powered by Airbyte's data sync. This often provides additional fields and operators beyond what the API natively supports, making it easier to narrow down results before performing further operations. Only available in hosted mode.

#### Python SDK

```python
await twilio.addresses.search(
    query={"filter": {"eq": {"sid": "<str>"}}}
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
        "query": {"filter": {"eq": {"sid": "<str>"}}}
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
| `sid` | `string` | The unique identifier of the address |
| `account_sid` | `string` | The account SID associated with this address |
| `customer_name` | `string` | The customer name associated with this address |
| `friendly_name` | `string` | A friendly name for the address |
| `street` | `string` | The street address |
| `city` | `string` | The city of the address |
| `region` | `string` | The region or state |
| `postal_code` | `string` | The postal code |
| `iso_country` | `string` | The ISO 3166-1 alpha-2 country code |
| `validated` | `boolean` | Whether the address has been validated |
| `verified` | `boolean` | Whether the address has been verified |

<details>
<summary><b>Response Schema</b></summary>

| Field Name | Type | Description |
|------------|------|-------------|
| `data` | `array` | List of matching records |
| `meta` | `object` | Pagination metadata |
| `meta.has_more` | `boolean` | Whether additional pages are available |
| `meta.cursor` | `string \| null` | Cursor for next page of results |
| `meta.took_ms` | `number \| null` | Query execution time in milliseconds |
| `data[].sid` | `string` | The unique identifier of the address |
| `data[].account_sid` | `string` | The account SID associated with this address |
| `data[].customer_name` | `string` | The customer name associated with this address |
| `data[].friendly_name` | `string` | A friendly name for the address |
| `data[].street` | `string` | The street address |
| `data[].city` | `string` | The city of the address |
| `data[].region` | `string` | The region or state |
| `data[].postal_code` | `string` | The postal code |
| `data[].iso_country` | `string` | The ISO 3166-1 alpha-2 country code |
| `data[].validated` | `boolean` | Whether the address has been validated |
| `data[].verified` | `boolean` | Whether the address has been verified |

</details>

## Queues

### Queues List

Returns a list of queues for an account

#### Python SDK

```python
await twilio.queues.list(
    account_sid="<str>"
)
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/integrations/connectors/{your_connector_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "queues",
    "action": "list",
    "params": {
        "AccountSid": "<str>"
    }
}'
```


#### Parameters

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `AccountSid` | `string` | Yes | Account SID |
| `PageSize` | `integer` | No | Number of items to return per page |


<details>
<summary><b>Response Schema</b></summary>

#### Records

| Field Name | Type | Description |
|------------|------|-------------|
| `account_sid` | `null \| string` |  |
| `average_wait_time` | `null \| integer` |  |
| `current_size` | `null \| integer` |  |
| `date_created` | `null \| string` |  |
| `date_updated` | `null \| string` |  |
| `friendly_name` | `null \| string` |  |
| `max_size` | `null \| integer` |  |
| `sid` | `null \| string` |  |
| `uri` | `null \| string` |  |
| `subresource_uris` | `null \| object` |  |


#### Meta

| Field Name | Type | Description |
|------------|------|-------------|
| `next_page_uri` | `null \| string` |  |
| `first_page_uri` | `null \| string` |  |
| `page` | `null \| integer` |  |
| `page_size` | `null \| integer` |  |

</details>

### Queues Get

Get a single queue by SID

#### Python SDK

```python
await twilio.queues.get(
    account_sid="<str>",
    sid="<str>"
)
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/integrations/connectors/{your_connector_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "queues",
    "action": "get",
    "params": {
        "AccountSid": "<str>",
        "sid": "<str>"
    }
}'
```


#### Parameters

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `AccountSid` | `string` | Yes | Account SID |
| `sid` | `string` | Yes | Queue SID |


<details>
<summary><b>Response Schema</b></summary>

#### Records

| Field Name | Type | Description |
|------------|------|-------------|
| `account_sid` | `null \| string` |  |
| `average_wait_time` | `null \| integer` |  |
| `current_size` | `null \| integer` |  |
| `date_created` | `null \| string` |  |
| `date_updated` | `null \| string` |  |
| `friendly_name` | `null \| string` |  |
| `max_size` | `null \| integer` |  |
| `sid` | `null \| string` |  |
| `uri` | `null \| string` |  |
| `subresource_uris` | `null \| object` |  |


</details>

### Queues Search

Search and filter queues records powered by Airbyte's data sync. This often provides additional fields and operators beyond what the API natively supports, making it easier to narrow down results before performing further operations. Only available in hosted mode.

#### Python SDK

```python
await twilio.queues.search(
    query={"filter": {"eq": {"sid": "<str>"}}}
)
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/integrations/connectors/{your_connector_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "queues",
    "action": "search",
    "params": {
        "query": {"filter": {"eq": {"sid": "<str>"}}}
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
| `sid` | `string` | The unique identifier for the queue |
| `account_sid` | `string` | The account SID that owns this queue |
| `friendly_name` | `string` | A friendly name for the queue |
| `current_size` | `integer` | Current number of callers waiting |
| `max_size` | `integer` | Maximum number of callers allowed |
| `average_wait_time` | `integer` | Average wait time in seconds |
| `date_created` | `string` | When the queue was created |
| `date_updated` | `string` | When the queue was last updated |

<details>
<summary><b>Response Schema</b></summary>

| Field Name | Type | Description |
|------------|------|-------------|
| `data` | `array` | List of matching records |
| `meta` | `object` | Pagination metadata |
| `meta.has_more` | `boolean` | Whether additional pages are available |
| `meta.cursor` | `string \| null` | Cursor for next page of results |
| `meta.took_ms` | `number \| null` | Query execution time in milliseconds |
| `data[].sid` | `string` | The unique identifier for the queue |
| `data[].account_sid` | `string` | The account SID that owns this queue |
| `data[].friendly_name` | `string` | A friendly name for the queue |
| `data[].current_size` | `integer` | Current number of callers waiting |
| `data[].max_size` | `integer` | Maximum number of callers allowed |
| `data[].average_wait_time` | `integer` | Average wait time in seconds |
| `data[].date_created` | `string` | When the queue was created |
| `data[].date_updated` | `string` | When the queue was last updated |

</details>

## Transcriptions

### Transcriptions List

Returns a list of transcriptions for an account

#### Python SDK

```python
await twilio.transcriptions.list(
    account_sid="<str>"
)
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/integrations/connectors/{your_connector_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "transcriptions",
    "action": "list",
    "params": {
        "AccountSid": "<str>"
    }
}'
```


#### Parameters

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `AccountSid` | `string` | Yes | Account SID |
| `PageSize` | `integer` | No | Number of items to return per page |


<details>
<summary><b>Response Schema</b></summary>

#### Records

| Field Name | Type | Description |
|------------|------|-------------|
| `account_sid` | `null \| string` |  |
| `api_version` | `null \| string` |  |
| `date_created` | `null \| string` |  |
| `date_updated` | `null \| string` |  |
| `duration` | `null \| string` |  |
| `price` | `null \| string` |  |
| `price_unit` | `null \| string` |  |
| `recording_sid` | `null \| string` |  |
| `sid` | `null \| string` |  |
| `status` | `null \| string` |  |
| `transcription_text` | `null \| string` |  |
| `type` | `null \| string` |  |
| `uri` | `null \| string` |  |


#### Meta

| Field Name | Type | Description |
|------------|------|-------------|
| `next_page_uri` | `null \| string` |  |
| `first_page_uri` | `null \| string` |  |
| `page` | `null \| integer` |  |
| `page_size` | `null \| integer` |  |

</details>

### Transcriptions Get

Get a single transcription by SID

#### Python SDK

```python
await twilio.transcriptions.get(
    account_sid="<str>",
    sid="<str>"
)
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/integrations/connectors/{your_connector_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "transcriptions",
    "action": "get",
    "params": {
        "AccountSid": "<str>",
        "sid": "<str>"
    }
}'
```


#### Parameters

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `AccountSid` | `string` | Yes | Account SID |
| `sid` | `string` | Yes | Transcription SID |


<details>
<summary><b>Response Schema</b></summary>

#### Records

| Field Name | Type | Description |
|------------|------|-------------|
| `account_sid` | `null \| string` |  |
| `api_version` | `null \| string` |  |
| `date_created` | `null \| string` |  |
| `date_updated` | `null \| string` |  |
| `duration` | `null \| string` |  |
| `price` | `null \| string` |  |
| `price_unit` | `null \| string` |  |
| `recording_sid` | `null \| string` |  |
| `sid` | `null \| string` |  |
| `status` | `null \| string` |  |
| `transcription_text` | `null \| string` |  |
| `type` | `null \| string` |  |
| `uri` | `null \| string` |  |


</details>

### Transcriptions Search

Search and filter transcriptions records powered by Airbyte's data sync. This often provides additional fields and operators beyond what the API natively supports, making it easier to narrow down results before performing further operations. Only available in hosted mode.

#### Python SDK

```python
await twilio.transcriptions.search(
    query={"filter": {"eq": {"sid": "<str>"}}}
)
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/integrations/connectors/{your_connector_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "transcriptions",
    "action": "search",
    "params": {
        "query": {"filter": {"eq": {"sid": "<str>"}}}
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
| `sid` | `string` | The unique identifier for the transcription |
| `account_sid` | `string` | The account SID |
| `recording_sid` | `string` | The SID of the associated recording |
| `status` | `string` | The status of the transcription |
| `duration` | `string` | Duration of the audio recording in seconds |
| `price` | `string` | The cost of the transcription |
| `price_unit` | `string` | The currency unit |
| `date_created` | `string` | When the transcription was created |
| `date_updated` | `string` | When the transcription was last updated |

<details>
<summary><b>Response Schema</b></summary>

| Field Name | Type | Description |
|------------|------|-------------|
| `data` | `array` | List of matching records |
| `meta` | `object` | Pagination metadata |
| `meta.has_more` | `boolean` | Whether additional pages are available |
| `meta.cursor` | `string \| null` | Cursor for next page of results |
| `meta.took_ms` | `number \| null` | Query execution time in milliseconds |
| `data[].sid` | `string` | The unique identifier for the transcription |
| `data[].account_sid` | `string` | The account SID |
| `data[].recording_sid` | `string` | The SID of the associated recording |
| `data[].status` | `string` | The status of the transcription |
| `data[].duration` | `string` | Duration of the audio recording in seconds |
| `data[].price` | `string` | The cost of the transcription |
| `data[].price_unit` | `string` | The currency unit |
| `data[].date_created` | `string` | When the transcription was created |
| `data[].date_updated` | `string` | When the transcription was last updated |

</details>

## Outgoing Caller Ids

### Outgoing Caller Ids List

Returns a list of outgoing caller IDs for an account

#### Python SDK

```python
await twilio.outgoing_caller_ids.list(
    account_sid="<str>"
)
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/integrations/connectors/{your_connector_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "outgoing_caller_ids",
    "action": "list",
    "params": {
        "AccountSid": "<str>"
    }
}'
```


#### Parameters

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `AccountSid` | `string` | Yes | Account SID |
| `PageSize` | `integer` | No | Number of items to return per page |


<details>
<summary><b>Response Schema</b></summary>

#### Records

| Field Name | Type | Description |
|------------|------|-------------|
| `account_sid` | `null \| string` |  |
| `date_created` | `null \| string` |  |
| `date_updated` | `null \| string` |  |
| `friendly_name` | `null \| string` |  |
| `phone_number` | `null \| string` |  |
| `sid` | `null \| string` |  |
| `uri` | `null \| string` |  |


#### Meta

| Field Name | Type | Description |
|------------|------|-------------|
| `next_page_uri` | `null \| string` |  |
| `first_page_uri` | `null \| string` |  |
| `page` | `null \| integer` |  |
| `page_size` | `null \| integer` |  |

</details>

### Outgoing Caller Ids Get

Get a single outgoing caller ID by SID

#### Python SDK

```python
await twilio.outgoing_caller_ids.get(
    account_sid="<str>",
    sid="<str>"
)
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/integrations/connectors/{your_connector_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "outgoing_caller_ids",
    "action": "get",
    "params": {
        "AccountSid": "<str>",
        "sid": "<str>"
    }
}'
```


#### Parameters

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `AccountSid` | `string` | Yes | Account SID |
| `sid` | `string` | Yes | Outgoing caller ID SID |


<details>
<summary><b>Response Schema</b></summary>

#### Records

| Field Name | Type | Description |
|------------|------|-------------|
| `account_sid` | `null \| string` |  |
| `date_created` | `null \| string` |  |
| `date_updated` | `null \| string` |  |
| `friendly_name` | `null \| string` |  |
| `phone_number` | `null \| string` |  |
| `sid` | `null \| string` |  |
| `uri` | `null \| string` |  |


</details>

### Outgoing Caller Ids Search

Search and filter outgoing caller ids records powered by Airbyte's data sync. This often provides additional fields and operators beyond what the API natively supports, making it easier to narrow down results before performing further operations. Only available in hosted mode.

#### Python SDK

```python
await twilio.outgoing_caller_ids.search(
    query={"filter": {"eq": {"sid": "<str>"}}}
)
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/integrations/connectors/{your_connector_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "outgoing_caller_ids",
    "action": "search",
    "params": {
        "query": {"filter": {"eq": {"sid": "<str>"}}}
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
| `sid` | `string` | The unique identifier |
| `account_sid` | `string` | The account SID |
| `phone_number` | `string` | The phone number |
| `friendly_name` | `string` | A friendly name |
| `date_created` | `string` | When the outgoing caller ID was created |
| `date_updated` | `string` | When the outgoing caller ID was last updated |

<details>
<summary><b>Response Schema</b></summary>

| Field Name | Type | Description |
|------------|------|-------------|
| `data` | `array` | List of matching records |
| `meta` | `object` | Pagination metadata |
| `meta.has_more` | `boolean` | Whether additional pages are available |
| `meta.cursor` | `string \| null` | Cursor for next page of results |
| `meta.took_ms` | `number \| null` | Query execution time in milliseconds |
| `data[].sid` | `string` | The unique identifier |
| `data[].account_sid` | `string` | The account SID |
| `data[].phone_number` | `string` | The phone number |
| `data[].friendly_name` | `string` | A friendly name |
| `data[].date_created` | `string` | When the outgoing caller ID was created |
| `data[].date_updated` | `string` | When the outgoing caller ID was last updated |

</details>

