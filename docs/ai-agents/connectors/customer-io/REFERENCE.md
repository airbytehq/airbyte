# Customer-Io full reference

This is the full reference documentation for the Customer-Io agent connector.

## Supported entities and actions

The Customer-Io connector supports the following entities and actions.

| Entity | Actions |
|--------|---------|
| Campaigns | [List](#campaigns-list), [Get](#campaigns-get), [Context Store Search](#campaigns-context-store-search) |
| Campaign Actions | [List](#campaign-actions-list), [Get](#campaign-actions-get), [Context Store Search](#campaign-actions-context-store-search) |
| Newsletters | [List](#newsletters-list), [Get](#newsletters-get), [Context Store Search](#newsletters-context-store-search) |
| Segments | [List](#segments-list), [Create](#segments-create), [Get](#segments-get) |
| Messages | [List](#messages-list), [Get](#messages-get) |
| Activities | [List](#activities-list) |
| Sender Identities | [List](#sender-identities-list), [Get](#sender-identities-get) |
| Snippets | [List](#snippets-list), [Create](#snippets-create), [Update](#snippets-update) |
| Collections | [List](#collections-list), [Create](#collections-create), [Get](#collections-get), [Update](#collections-update) |
| Reporting Webhooks | [List](#reporting-webhooks-list), [Create](#reporting-webhooks-create), [Get](#reporting-webhooks-get), [Update](#reporting-webhooks-update) |
| Exports | [List](#exports-list), [Create](#exports-create), [Get](#exports-get) |
| Transactional Email | [Create](#transactional-email-create) |
| Transactional Sms | [Create](#transactional-sms-create) |
| Transactional Push | [Create](#transactional-push-create) |
| Transactional Inbox Message | [Create](#transactional-inbox-message-create) |
| Broadcast Trigger | [Create](#broadcast-trigger-create) |

## Campaigns

### Campaigns List

Returns a list of all campaigns in the workspace.

#### Python SDK

```python
await customer_io.campaigns.list()
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



<details>
<summary><b>Response Schema</b></summary>

#### Records

| Field Name | Type | Description |
|------------|------|-------------|
| `id` | `null \| integer` |  |
| `name` | `null \| string` |  |
| `type` | `null \| string` |  |
| `state` | `null \| string` |  |
| `active` | `null \| boolean` |  |
| `created` | `null \| integer` |  |
| `updated` | `null \| integer` |  |
| `first_started` | `null \| integer` |  |
| `deduplicate_id` | `null \| string` |  |
| `tags` | `null \| array` |  |
| `actions` | `null \| array` |  |
| `msg_templates` | `null \| array` |  |
| `trigger_segment_ids` | `null \| array` |  |
| `filter_segment_ids` | `null \| array` |  |
| `frequency` | `null \| string` |  |
| `event_name` | `null \| string` |  |
| `date_attribute` | `null \| string` |  |
| `start_hour` | `null \| integer` |  |
| `start_minutes` | `null \| integer` |  |
| `timezone` | `null \| string` |  |
| `use_customer_timezone` | `null \| boolean` |  |
| `created_by` | `null \| string` |  |
| `scheduled_start` | `null \| integer` |  |
| `scheduled_start_should_backfill` | `null \| boolean` |  |
| `scheduled_stop` | `null \| integer` |  |
| `scheduled_stop_should_sunset` | `null \| boolean` |  |


</details>

### Campaigns Get

Returns a single campaign by ID.

#### Python SDK

```python
await customer_io.campaigns.get(
    campaign_id=0
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
        "campaign_id": 0
    }
}'
```


#### Parameters

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `campaign_id` | `integer` | Yes | The campaign identifier |


<details>
<summary><b>Response Schema</b></summary>

#### Records

| Field Name | Type | Description |
|------------|------|-------------|
| `id` | `null \| integer` |  |
| `name` | `null \| string` |  |
| `type` | `null \| string` |  |
| `state` | `null \| string` |  |
| `active` | `null \| boolean` |  |
| `created` | `null \| integer` |  |
| `updated` | `null \| integer` |  |
| `first_started` | `null \| integer` |  |
| `deduplicate_id` | `null \| string` |  |
| `tags` | `null \| array` |  |
| `actions` | `null \| array` |  |
| `msg_templates` | `null \| array` |  |
| `trigger_segment_ids` | `null \| array` |  |
| `filter_segment_ids` | `null \| array` |  |
| `frequency` | `null \| string` |  |
| `event_name` | `null \| string` |  |
| `date_attribute` | `null \| string` |  |
| `start_hour` | `null \| integer` |  |
| `start_minutes` | `null \| integer` |  |
| `timezone` | `null \| string` |  |
| `use_customer_timezone` | `null \| boolean` |  |
| `created_by` | `null \| string` |  |
| `scheduled_start` | `null \| integer` |  |
| `scheduled_start_should_backfill` | `null \| boolean` |  |
| `scheduled_stop` | `null \| integer` |  |
| `scheduled_stop_should_sunset` | `null \| boolean` |  |


</details>

### Campaigns Context Store Search

Search and filter campaigns records powered by Airbyte's data sync. This often provides additional fields and operators beyond what the API natively supports, making it easier to narrow down results before performing further operations. Only available in hosted mode.

#### Python SDK

```python
await customer_io.campaigns.context_store_search(
    query={"filter": {"eq": {"actions": []}}}
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
        "query": {"filter": {"eq": {"actions": []}}}
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
| `actions` | `array` | Actions defined in this campaign |
| `active` | `boolean` | Whether the campaign is active |
| `created` | `integer` | Creation timestamp (Unix) |
| `created_by` | `string` | Who created the campaign |
| `date_attribute` | `string` | Date attribute used for date-triggered campaigns |
| `deduplicate_id` | `string` | Deduplication identifier |
| `event_name` | `string` | Event name that triggers the campaign |
| `first_started` | `integer` | When the campaign was first started (Unix) |
| `frequency` | `string` | How frequently a person can receive this campaign |
| `id` | `integer` | Unique campaign identifier |
| `msg_templates` | `array` | Message templates used in the campaign |
| `name` | `string` | Campaign name |
| `start_hour` | `integer` | Hour of the day to trigger |
| `start_minutes` | `integer` | Minute of the hour to trigger |
| `state` | `string` | Campaign status (draft, active, stopped) |
| `tags` | `array` | Tags associated with the campaign |
| `timezone` | `string` | Timezone for trigger scheduling |
| `trigger_segment_ids` | `array` | Segment IDs that trigger this campaign |
| `type` | `string` | Campaign trigger type |
| `updated` | `integer` | Last update timestamp (Unix) |
| `use_customer_timezone` | `boolean` | Whether to use the customer's timezone |

<details>
<summary><b>Response Schema</b></summary>

| Field Name | Type | Description |
|------------|------|-------------|
| `data` | `array` | List of matching records |
| `meta` | `object` | Pagination metadata |
| `meta.has_more` | `boolean` | Whether additional pages are available |
| `meta.cursor` | `string \| null` | Cursor for next page of results |
| `meta.took_ms` | `number \| null` | Query execution time in milliseconds |
| `data[].actions` | `array` | Actions defined in this campaign |
| `data[].active` | `boolean` | Whether the campaign is active |
| `data[].created` | `integer` | Creation timestamp (Unix) |
| `data[].created_by` | `string` | Who created the campaign |
| `data[].date_attribute` | `string` | Date attribute used for date-triggered campaigns |
| `data[].deduplicate_id` | `string` | Deduplication identifier |
| `data[].event_name` | `string` | Event name that triggers the campaign |
| `data[].first_started` | `integer` | When the campaign was first started (Unix) |
| `data[].frequency` | `string` | How frequently a person can receive this campaign |
| `data[].id` | `integer` | Unique campaign identifier |
| `data[].msg_templates` | `array` | Message templates used in the campaign |
| `data[].name` | `string` | Campaign name |
| `data[].start_hour` | `integer` | Hour of the day to trigger |
| `data[].start_minutes` | `integer` | Minute of the hour to trigger |
| `data[].state` | `string` | Campaign status (draft, active, stopped) |
| `data[].tags` | `array` | Tags associated with the campaign |
| `data[].timezone` | `string` | Timezone for trigger scheduling |
| `data[].trigger_segment_ids` | `array` | Segment IDs that trigger this campaign |
| `data[].type` | `string` | Campaign trigger type |
| `data[].updated` | `integer` | Last update timestamp (Unix) |
| `data[].use_customer_timezone` | `boolean` | Whether to use the customer's timezone |

</details>

## Campaign Actions

### Campaign Actions List

Returns a paginated list of actions for a campaign.

#### Python SDK

```python
await customer_io.campaign_actions.list(
    campaign_id=0
)
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/integrations/connectors/{your_connector_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "campaign_actions",
    "action": "list",
    "params": {
        "campaign_id": 0
    }
}'
```


#### Parameters

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `campaign_id` | `integer` | Yes | The campaign identifier |
| `start` | `string` | No | Pagination cursor for the next page |


<details>
<summary><b>Response Schema</b></summary>

#### Records

| Field Name | Type | Description |
|------------|------|-------------|
| `id` | `null \| integer \| string` |  |
| `name` | `null \| string` |  |
| `type` | `null \| string` |  |
| `campaign_id` | `null \| integer` |  |
| `created` | `null \| integer` |  |
| `updated` | `null \| integer` |  |
| `deduplicate_id` | `null \| string` |  |
| `body` | `null \| string` |  |
| `layout` | `null \| string` |  |
| `from` | `null \| string` |  |
| `from_id` | `null \| integer` |  |
| `subject` | `null \| string` |  |
| `preheader_text` | `null \| string` |  |
| `recipient` | `null \| string` |  |
| `reply_to` | `null \| string` |  |
| `reply_to_id` | `null \| integer` |  |
| `bcc` | `null \| string` |  |
| `fake_bcc` | `null \| boolean` |  |
| `headers` | `null \| string` |  |
| `sending_state` | `null \| string` |  |
| `language` | `null \| string` |  |
| `parent_action_id` | `null \| integer` |  |
| `preprocessor` | `null \| string` |  |
| `body_amp` | `null \| string` |  |
| `broadcast_id` | `null \| integer` |  |
| `editor` | `null \| string` |  |
| `url` | `null \| string` |  |
| `body_plain` | `null \| string` |  |


#### Meta

| Field Name | Type | Description |
|------------|------|-------------|
| `next` | `string` |  |

</details>

### Campaign Actions Get

Returns a single campaign action by ID.

#### Python SDK

```python
await customer_io.campaign_actions.get(
    campaign_id=0,
    action_id=0
)
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/integrations/connectors/{your_connector_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "campaign_actions",
    "action": "get",
    "params": {
        "campaign_id": 0,
        "action_id": 0
    }
}'
```


#### Parameters

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `campaign_id` | `integer` | Yes | The campaign identifier |
| `action_id` | `integer` | Yes | The action identifier |


<details>
<summary><b>Response Schema</b></summary>

#### Records

| Field Name | Type | Description |
|------------|------|-------------|
| `id` | `null \| integer \| string` |  |
| `name` | `null \| string` |  |
| `type` | `null \| string` |  |
| `campaign_id` | `null \| integer` |  |
| `created` | `null \| integer` |  |
| `updated` | `null \| integer` |  |
| `deduplicate_id` | `null \| string` |  |
| `body` | `null \| string` |  |
| `layout` | `null \| string` |  |
| `from` | `null \| string` |  |
| `from_id` | `null \| integer` |  |
| `subject` | `null \| string` |  |
| `preheader_text` | `null \| string` |  |
| `recipient` | `null \| string` |  |
| `reply_to` | `null \| string` |  |
| `reply_to_id` | `null \| integer` |  |
| `bcc` | `null \| string` |  |
| `fake_bcc` | `null \| boolean` |  |
| `headers` | `null \| string` |  |
| `sending_state` | `null \| string` |  |
| `language` | `null \| string` |  |
| `parent_action_id` | `null \| integer` |  |
| `preprocessor` | `null \| string` |  |
| `body_amp` | `null \| string` |  |
| `broadcast_id` | `null \| integer` |  |
| `editor` | `null \| string` |  |
| `url` | `null \| string` |  |
| `body_plain` | `null \| string` |  |


</details>

### Campaign Actions Context Store Search

Search and filter campaign actions records powered by Airbyte's data sync. This often provides additional fields and operators beyond what the API natively supports, making it easier to narrow down results before performing further operations. Only available in hosted mode.

#### Python SDK

```python
await customer_io.campaign_actions.context_store_search(
    query={"filter": {"eq": {"bcc": "<str>"}}}
)
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/integrations/connectors/{your_connector_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "campaign_actions",
    "action": "context_store_search",
    "params": {
        "query": {"filter": {"eq": {"bcc": "<str>"}}}
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
| `bcc` | `string` | BCC addresses |
| `body` | `string` | Action body content (HTML for emails) |
| `campaign_id` | `integer` | Parent campaign ID |
| `created` | `integer` | Creation timestamp (Unix) |
| `deduplicate_id` | `string` | Deduplication identifier |
| `editor` | `string` | Editor used to create the action |
| `fake_bcc` | `boolean` | Whether to use fake BCC |
| `from` | `string` | From address |
| `from_id` | `string` | Sender identity ID |
| `headers` | `string` | Custom email headers as JSON |
| `id` | `string` | Unique action identifier |
| `language` | `string` | Language variant |
| `layout` | `string` | Layout template used |
| `name` | `string` | Action name |
| `parent_action_id` | `integer` | Parent action ID for language variants |
| `preheader_text` | `string` | Email preheader/preview text |
| `preprocessor` | `string` | CSS preprocessor setting |
| `recipient` | `string` | Recipient address |
| `recipient_environment_id` | `integer` | Recipient environment ID |
| `reply_to` | `string` | Reply-to address |
| `reply_to_id` | `string` | Reply-to sender identity ID |
| `request_method` | `string` | HTTP request method for webhook actions |
| `sending_state` | `string` | Sending behavior (automatic or draft) |
| `subject` | `string` | Email subject line |
| `type` | `string` | Action type (email, webhook, twilio, push, slack, in_app, whatsapp) |
| `updated` | `integer` | Last update timestamp (Unix) |
| `url` | `string` | Webhook URL (for webhook actions) |

<details>
<summary><b>Response Schema</b></summary>

| Field Name | Type | Description |
|------------|------|-------------|
| `data` | `array` | List of matching records |
| `meta` | `object` | Pagination metadata |
| `meta.has_more` | `boolean` | Whether additional pages are available |
| `meta.cursor` | `string \| null` | Cursor for next page of results |
| `meta.took_ms` | `number \| null` | Query execution time in milliseconds |
| `data[].bcc` | `string` | BCC addresses |
| `data[].body` | `string` | Action body content (HTML for emails) |
| `data[].campaign_id` | `integer` | Parent campaign ID |
| `data[].created` | `integer` | Creation timestamp (Unix) |
| `data[].deduplicate_id` | `string` | Deduplication identifier |
| `data[].editor` | `string` | Editor used to create the action |
| `data[].fake_bcc` | `boolean` | Whether to use fake BCC |
| `data[].from` | `string` | From address |
| `data[].from_id` | `string` | Sender identity ID |
| `data[].headers` | `string` | Custom email headers as JSON |
| `data[].id` | `string` | Unique action identifier |
| `data[].language` | `string` | Language variant |
| `data[].layout` | `string` | Layout template used |
| `data[].name` | `string` | Action name |
| `data[].parent_action_id` | `integer` | Parent action ID for language variants |
| `data[].preheader_text` | `string` | Email preheader/preview text |
| `data[].preprocessor` | `string` | CSS preprocessor setting |
| `data[].recipient` | `string` | Recipient address |
| `data[].recipient_environment_id` | `integer` | Recipient environment ID |
| `data[].reply_to` | `string` | Reply-to address |
| `data[].reply_to_id` | `string` | Reply-to sender identity ID |
| `data[].request_method` | `string` | HTTP request method for webhook actions |
| `data[].sending_state` | `string` | Sending behavior (automatic or draft) |
| `data[].subject` | `string` | Email subject line |
| `data[].type` | `string` | Action type (email, webhook, twilio, push, slack, in_app, whatsapp) |
| `data[].updated` | `integer` | Last update timestamp (Unix) |
| `data[].url` | `string` | Webhook URL (for webhook actions) |

</details>

## Newsletters

### Newsletters List

Returns a paginated list of newsletters.

#### Python SDK

```python
await customer_io.newsletters.list()
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/integrations/connectors/{your_connector_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "newsletters",
    "action": "list"
}'
```


#### Parameters

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `start` | `string` | No | Pagination cursor for the next page |
| `limit` | `integer` | No | Maximum number of newsletters to return |
| `sort` | `"asc" \| "desc"` | No | Sort order |


<details>
<summary><b>Response Schema</b></summary>

#### Records

| Field Name | Type | Description |
|------------|------|-------------|
| `id` | `null \| integer` |  |
| `name` | `null \| string` |  |
| `type` | `null \| string` |  |
| `created` | `null \| integer` |  |
| `updated` | `null \| integer` |  |
| `sent_at` | `null \| integer` |  |
| `deduplicate_id` | `null \| string` |  |
| `tags` | `null \| array` |  |
| `content_ids` | `null \| array` |  |
| `recipient_segment_ids` | `null \| array` |  |
| `subscription_topic_id` | `null \| integer` |  |


#### Meta

| Field Name | Type | Description |
|------------|------|-------------|
| `next` | `string` |  |

</details>

### Newsletters Get

Returns a single newsletter by ID.

#### Python SDK

```python
await customer_io.newsletters.get(
    newsletter_id=0
)
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/integrations/connectors/{your_connector_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "newsletters",
    "action": "get",
    "params": {
        "newsletter_id": 0
    }
}'
```


#### Parameters

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `newsletter_id` | `integer` | Yes | The newsletter identifier |


<details>
<summary><b>Response Schema</b></summary>

#### Records

| Field Name | Type | Description |
|------------|------|-------------|
| `id` | `null \| integer` |  |
| `name` | `null \| string` |  |
| `type` | `null \| string` |  |
| `created` | `null \| integer` |  |
| `updated` | `null \| integer` |  |
| `sent_at` | `null \| integer` |  |
| `deduplicate_id` | `null \| string` |  |
| `tags` | `null \| array` |  |
| `content_ids` | `null \| array` |  |
| `recipient_segment_ids` | `null \| array` |  |
| `subscription_topic_id` | `null \| integer` |  |


</details>

### Newsletters Context Store Search

Search and filter newsletters records powered by Airbyte's data sync. This often provides additional fields and operators beyond what the API natively supports, making it easier to narrow down results before performing further operations. Only available in hosted mode.

#### Python SDK

```python
await customer_io.newsletters.context_store_search(
    query={"filter": {"eq": {"content_ids": []}}}
)
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/integrations/connectors/{your_connector_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "newsletters",
    "action": "context_store_search",
    "params": {
        "query": {"filter": {"eq": {"content_ids": []}}}
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
| `content_ids` | `array` | Content variant IDs for this newsletter |
| `created` | `integer` | Creation timestamp (Unix) |
| `deduplicate_id` | `string` | Deduplication identifier |
| `id` | `integer` | Unique newsletter identifier |
| `name` | `string` | Newsletter name |
| `sent_at` | `integer` | When the newsletter was last sent (Unix) |
| `tags` | `array` | Tags associated with the newsletter |
| `type` | `string` | Channel type (email, webhook, twilio, push, in_app, inbox) |
| `updated` | `integer` | Last update timestamp (Unix) |

<details>
<summary><b>Response Schema</b></summary>

| Field Name | Type | Description |
|------------|------|-------------|
| `data` | `array` | List of matching records |
| `meta` | `object` | Pagination metadata |
| `meta.has_more` | `boolean` | Whether additional pages are available |
| `meta.cursor` | `string \| null` | Cursor for next page of results |
| `meta.took_ms` | `number \| null` | Query execution time in milliseconds |
| `data[].content_ids` | `array` | Content variant IDs for this newsletter |
| `data[].created` | `integer` | Creation timestamp (Unix) |
| `data[].deduplicate_id` | `string` | Deduplication identifier |
| `data[].id` | `integer` | Unique newsletter identifier |
| `data[].name` | `string` | Newsletter name |
| `data[].sent_at` | `integer` | When the newsletter was last sent (Unix) |
| `data[].tags` | `array` | Tags associated with the newsletter |
| `data[].type` | `string` | Channel type (email, webhook, twilio, push, in_app, inbox) |
| `data[].updated` | `integer` | Last update timestamp (Unix) |

</details>

## Segments

### Segments List

Returns all segments in the workspace.

#### Python SDK

```python
await customer_io.segments.list()
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
| `id` | `null \| integer` |  |
| `name` | `null \| string` |  |
| `description` | `null \| string` |  |
| `type` | `null \| string` |  |
| `state` | `null \| string` |  |
| `created_at` | `null \| integer` |  |
| `updated_at` | `null \| integer` |  |
| `deduplicate_id` | `null \| string` |  |
| `tags` | `null \| array` |  |
| `progress` | `null \| integer` |  |
| `conditions` | `null \| object` |  |


</details>

### Segments Create

Creates a new empty manual segment. People can be added to it separately.

#### Python SDK

```python
await customer_io.segments.create(
    segment={
        "name": "<str>"
    }
)
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/integrations/connectors/{your_connector_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "segments",
    "action": "create",
    "params": {
        "segment": {
            "name": "<str>"
        }
    }
}'
```


#### Parameters

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `segment` | `object` | Yes |  |
| `segment.name` | `string` | Yes | Name of the manual segment |
| `segment.description` | `string` | No | Optional description of the segment |


### Segments Get

Returns a single segment by ID.

#### Python SDK

```python
await customer_io.segments.get(
    segment_id=0
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
        "segment_id": 0
    }
}'
```


#### Parameters

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `segment_id` | `integer` | Yes | The segment identifier |


<details>
<summary><b>Response Schema</b></summary>

#### Records

| Field Name | Type | Description |
|------------|------|-------------|
| `id` | `null \| integer` |  |
| `name` | `null \| string` |  |
| `description` | `null \| string` |  |
| `type` | `null \| string` |  |
| `state` | `null \| string` |  |
| `created_at` | `null \| integer` |  |
| `updated_at` | `null \| integer` |  |
| `deduplicate_id` | `null \| string` |  |
| `tags` | `null \| array` |  |
| `progress` | `null \| integer` |  |
| `conditions` | `null \| object` |  |


</details>

## Messages

### Messages List

Returns a paginated list of message deliveries.

#### Python SDK

```python
await customer_io.messages.list()
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/integrations/connectors/{your_connector_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "messages",
    "action": "list"
}'
```


#### Parameters

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `start` | `string` | No | Pagination cursor for the next page |
| `limit` | `integer` | No | Maximum number of messages to return |
| `type` | `"email" \| "webhook" \| "twilio" \| "whatsapp" \| "slack" \| "push" \| "in_app"` | No | Filter messages by channel type |
| `metric` | `"attempted" \| "sent" \| "delivered" \| "opened" \| "clicked" \| "converted" \| "bounced" \| "spammed" \| "unsubscribed" \| "dropped" \| "failed" \| "undeliverable"` | No | Filter messages by delivery metric |
| `campaign_id` | `integer` | No | Filter by campaign ID |
| `newsletter_id` | `integer` | No | Filter by newsletter ID |


<details>
<summary><b>Response Schema</b></summary>

#### Records

| Field Name | Type | Description |
|------------|------|-------------|
| `id` | `null \| string` |  |
| `type` | `null \| string` |  |
| `created` | `null \| integer` |  |
| `deduplicate_id` | `null \| string` |  |
| `customer_id` | `null \| string` |  |
| `customer_identifiers` | `null \| object` |  |
| `campaign_id` | `null \| integer` |  |
| `newsletter_id` | `null \| integer` |  |
| `broadcast_id` | `null \| integer` |  |
| `content_id` | `null \| integer` |  |
| `action_id` | `null \| integer` |  |
| `parent_action_id` | `null \| integer` |  |
| `message_template_id` | `null \| integer` |  |
| `recipient` | `null \| string` |  |
| `subject` | `null \| string` |  |
| `forgotten` | `null \| boolean` |  |
| `failure_message` | `null \| string` |  |
| `trigger_event_id` | `null \| string` |  |
| `metrics` | `null \| object` |  |


#### Meta

| Field Name | Type | Description |
|------------|------|-------------|
| `next` | `string` |  |

</details>

### Messages Get

Returns a single message delivery by ID. Untested because the test workspace has no message deliveries to retrieve.


#### Python SDK

```python
await customer_io.messages.get(
    message_id="<str>"
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
        "message_id": "<str>"
    }
}'
```


#### Parameters

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `message_id` | `string` | Yes | The message delivery identifier |


<details>
<summary><b>Response Schema</b></summary>

#### Records

| Field Name | Type | Description |
|------------|------|-------------|
| `id` | `null \| string` |  |
| `type` | `null \| string` |  |
| `created` | `null \| integer` |  |
| `deduplicate_id` | `null \| string` |  |
| `customer_id` | `null \| string` |  |
| `customer_identifiers` | `null \| object` |  |
| `campaign_id` | `null \| integer` |  |
| `newsletter_id` | `null \| integer` |  |
| `broadcast_id` | `null \| integer` |  |
| `content_id` | `null \| integer` |  |
| `action_id` | `null \| integer` |  |
| `parent_action_id` | `null \| integer` |  |
| `message_template_id` | `null \| integer` |  |
| `recipient` | `null \| string` |  |
| `subject` | `null \| string` |  |
| `forgotten` | `null \| boolean` |  |
| `failure_message` | `null \| string` |  |
| `trigger_event_id` | `null \| string` |  |
| `metrics` | `null \| object` |  |


</details>

## Activities

### Activities List

Returns a paginated list of activities in the workspace.

#### Python SDK

```python
await customer_io.activities.list()
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/integrations/connectors/{your_connector_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "activities",
    "action": "list"
}'
```


#### Parameters

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `start` | `string` | No | Pagination cursor for the next page |
| `limit` | `integer` | No | Maximum number of activities to return |
| `type` | `string` | No | Filter by activity type |
| `name` | `string` | No | Filter by event name |


<details>
<summary><b>Response Schema</b></summary>

#### Records

| Field Name | Type | Description |
|------------|------|-------------|
| `id` | `null \| string` |  |
| `type` | `null \| string` |  |
| `timestamp` | `null \| integer` |  |
| `customer_id` | `null \| string` |  |
| `customer_identifiers` | `null \| object` |  |
| `delivery_id` | `null \| string` |  |
| `delivery_type` | `null \| string` |  |
| `data` | `null \| object` |  |


#### Meta

| Field Name | Type | Description |
|------------|------|-------------|
| `next` | `string` |  |

</details>

## Sender Identities

### Sender Identities List

Returns a paginated list of sender identities.

#### Python SDK

```python
await customer_io.sender_identities.list()
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/integrations/connectors/{your_connector_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "sender_identities",
    "action": "list"
}'
```


#### Parameters

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `start` | `string` | No | Pagination cursor for the next page |
| `limit` | `integer` | No | Maximum number of sender identities to return |
| `sort` | `"asc" \| "desc"` | No | Sort order |


<details>
<summary><b>Response Schema</b></summary>

#### Records

| Field Name | Type | Description |
|------------|------|-------------|
| `id` | `null \| integer` |  |
| `name` | `null \| string` |  |
| `email` | `null \| string` |  |
| `address` | `null \| string` |  |
| `template_type` | `null \| string` |  |
| `auto_generated` | `null \| boolean` |  |
| `deduplicate_id` | `null \| string` |  |
| `phone` | `null \| string` |  |


#### Meta

| Field Name | Type | Description |
|------------|------|-------------|
| `next` | `string` |  |

</details>

### Sender Identities Get

Returns a single sender identity by ID.

#### Python SDK

```python
await customer_io.sender_identities.get(
    sender_id=0
)
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/integrations/connectors/{your_connector_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "sender_identities",
    "action": "get",
    "params": {
        "sender_id": 0
    }
}'
```


#### Parameters

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `sender_id` | `integer` | Yes | The sender identity identifier |


<details>
<summary><b>Response Schema</b></summary>

#### Records

| Field Name | Type | Description |
|------------|------|-------------|
| `id` | `null \| integer` |  |
| `name` | `null \| string` |  |
| `email` | `null \| string` |  |
| `address` | `null \| string` |  |
| `template_type` | `null \| string` |  |
| `auto_generated` | `null \| boolean` |  |
| `deduplicate_id` | `null \| string` |  |
| `phone` | `null \| string` |  |


</details>

## Snippets

### Snippets List

Returns all snippets in the workspace.

#### Python SDK

```python
await customer_io.snippets.list()
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/integrations/connectors/{your_connector_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "snippets",
    "action": "list"
}'
```



<details>
<summary><b>Response Schema</b></summary>

#### Records

| Field Name | Type | Description |
|------------|------|-------------|
| `name` | `null \| string` |  |
| `value` | `null \| string` |  |
| `updated_at` | `null \| integer` |  |


</details>

### Snippets Create

Creates a new reusable content snippet. Returns 422 if a snippet with the same name already exists.

#### Python SDK

```python
await customer_io.snippets.create(
    name="<str>",
    value="<str>"
)
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/integrations/connectors/{your_connector_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "snippets",
    "action": "create",
    "params": {
        "name": "<str>",
        "value": "<str>"
    }
}'
```


#### Parameters

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `name` | `string` | Yes | Unique snippet name (used as the liquid tag identifier) |
| `value` | `string` | Yes | Snippet content (plain text, HTML, or Liquid) |


### Snippets Update

Updates an existing snippet by name, or creates it if it does not exist (upsert behavior).

#### Python SDK

```python
await customer_io.snippets.update(
    name="<str>",
    value="<str>"
)
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/integrations/connectors/{your_connector_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "snippets",
    "action": "update",
    "params": {
        "name": "<str>",
        "value": "<str>"
    }
}'
```


#### Parameters

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `name` | `string` | Yes | Snippet name to update (or create if it does not exist) |
| `value` | `string` | Yes | New snippet content (plain text, HTML, or Liquid) |


## Collections

### Collections List

Returns all collections in the workspace.

#### Python SDK

```python
await customer_io.collections.list()
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/integrations/connectors/{your_connector_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "collections",
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
| `bytes` | `null \| integer` |  |
| `rows` | `null \| integer` |  |
| `schema` | `null \| array` |  |
| `created_at` | `null \| integer` |  |
| `updated_at` | `null \| integer` |  |


</details>

### Collections Create

Creates a new data collection with inline data or a URL source.

#### Python SDK

```python
await customer_io.collections.create(
    name="<str>",
    data=[],
    url="<str>"
)
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/integrations/connectors/{your_connector_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "collections",
    "action": "create",
    "params": {
        "name": "<str>",
        "data": [],
        "url": "<str>"
    }
}'
```


#### Parameters

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `name` | `string` | Yes | Collection name, referenced in Liquid as collection_name.property |
| `data` | `array<object>` | No | Inline collection data (array of objects). Provide either data or url, not both. |
| `url` | `string` | No | URL to a CSV or JSON file containing collection data. Provide either data or url, not both. |


### Collections Get

Returns a single collection by ID.

#### Python SDK

```python
await customer_io.collections.get(
    collection_id=0
)
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/integrations/connectors/{your_connector_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "collections",
    "action": "get",
    "params": {
        "collection_id": 0
    }
}'
```


#### Parameters

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `collection_id` | `integer` | Yes | The collection identifier |


<details>
<summary><b>Response Schema</b></summary>

#### Records

| Field Name | Type | Description |
|------------|------|-------------|
| `id` | `null \| integer` |  |
| `name` | `null \| string` |  |
| `bytes` | `null \| integer` |  |
| `rows` | `null \| integer` |  |
| `schema` | `null \| array` |  |
| `created_at` | `null \| integer` |  |
| `updated_at` | `null \| integer` |  |


</details>

### Collections Update

Updates an existing collection's name, data, or URL source.

#### Python SDK

```python
await customer_io.collections.update(
    name="<str>",
    data=[],
    url="<str>",
    collection_id=0
)
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/integrations/connectors/{your_connector_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "collections",
    "action": "update",
    "params": {
        "name": "<str>",
        "data": [],
        "url": "<str>",
        "collection_id": 0
    }
}'
```


#### Parameters

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `name` | `string` | No | Rename the collection |
| `data` | `array<object>` | No | Replace collection data entirely (array of objects). Provide either data or url, not both. |
| `url` | `string` | No | Replace the URL source for collection data. Provide either data or url, not both. |
| `collection_id` | `integer` | Yes | The collection identifier |


## Reporting Webhooks

### Reporting Webhooks List

Returns all reporting webhooks in the workspace.

#### Python SDK

```python
await customer_io.reporting_webhooks.list()
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/integrations/connectors/{your_connector_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "reporting_webhooks",
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
| `endpoint` | `null \| string` |  |
| `disabled` | `null \| boolean` |  |
| `full_resolution` | `null \| boolean` |  |
| `with_content` | `null \| boolean` |  |
| `events` | `null \| array` |  |


</details>

### Reporting Webhooks Create

Creates a new reporting webhook to receive event notifications at the specified endpoint.

#### Python SDK

```python
await customer_io.reporting_webhooks.create(
    name="<str>",
    endpoint="<str>",
    events=[],
    disabled=True,
    full_resolution=True,
    with_content=True
)
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/integrations/connectors/{your_connector_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "reporting_webhooks",
    "action": "create",
    "params": {
        "name": "<str>",
        "endpoint": "<str>",
        "events": [],
        "disabled": True,
        "full_resolution": True,
        "with_content": True
    }
}'
```


#### Parameters

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `name` | `string` | Yes | Webhook display name |
| `endpoint` | `string` | Yes | The URL to receive webhook notifications |
| `events` | `array<string>` | Yes | Event types to report (e.g. customer_subscribed, email_sent, email_opened, email_clicked, email_bounced, email_converted, email_unsubscribed, sms_sent, sms_delivered, push_sent)
 |
| `disabled` | `boolean` | No | Whether the webhook should be disabled initially |
| `full_resolution` | `boolean` | No | Send all events instead of only unique events |
| `with_content` | `boolean` | No | Include the message body in sent events |


<details>
<summary><b>Response Schema</b></summary>

#### Records

| Field Name | Type | Description |
|------------|------|-------------|
| `id` | `null \| integer` |  |
| `name` | `null \| string` |  |
| `endpoint` | `null \| string` |  |
| `disabled` | `null \| boolean` |  |
| `full_resolution` | `null \| boolean` |  |
| `with_content` | `null \| boolean` |  |
| `events` | `null \| array` |  |


</details>

### Reporting Webhooks Get

Returns a single reporting webhook by ID.

#### Python SDK

```python
await customer_io.reporting_webhooks.get(
    webhook_id=0
)
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/integrations/connectors/{your_connector_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "reporting_webhooks",
    "action": "get",
    "params": {
        "webhook_id": 0
    }
}'
```


#### Parameters

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `webhook_id` | `integer` | Yes | The reporting webhook identifier |


<details>
<summary><b>Response Schema</b></summary>

#### Records

| Field Name | Type | Description |
|------------|------|-------------|
| `id` | `null \| integer` |  |
| `name` | `null \| string` |  |
| `endpoint` | `null \| string` |  |
| `disabled` | `null \| boolean` |  |
| `full_resolution` | `null \| boolean` |  |
| `with_content` | `null \| boolean` |  |
| `events` | `null \| array` |  |


</details>

### Reporting Webhooks Update

Updates an existing reporting webhook's configuration.

#### Python SDK

```python
await customer_io.reporting_webhooks.update(
    name="<str>",
    endpoint="<str>",
    events=[],
    disabled=True,
    full_resolution=True,
    with_content=True,
    webhook_id=0
)
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/integrations/connectors/{your_connector_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "reporting_webhooks",
    "action": "update",
    "params": {
        "name": "<str>",
        "endpoint": "<str>",
        "events": [],
        "disabled": True,
        "full_resolution": True,
        "with_content": True,
        "webhook_id": 0
    }
}'
```


#### Parameters

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `name` | `string` | Yes | Webhook display name |
| `endpoint` | `string` | Yes | The URL to receive webhook notifications |
| `events` | `array<string>` | Yes | Event types to report |
| `disabled` | `boolean` | No | Whether the webhook is disabled |
| `full_resolution` | `boolean` | No | Send all events instead of only unique events |
| `with_content` | `boolean` | No | Include the message body in sent events |
| `webhook_id` | `integer` | Yes | The reporting webhook identifier |


<details>
<summary><b>Response Schema</b></summary>

#### Records

| Field Name | Type | Description |
|------------|------|-------------|
| `id` | `null \| integer` |  |
| `name` | `null \| string` |  |
| `endpoint` | `null \| string` |  |
| `disabled` | `null \| boolean` |  |
| `full_resolution` | `null \| boolean` |  |
| `with_content` | `null \| boolean` |  |
| `events` | `null \| array` |  |


</details>

## Exports

### Exports List

Returns all exports in the workspace.

#### Python SDK

```python
await customer_io.exports.list()
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/integrations/connectors/{your_connector_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "exports",
    "action": "list"
}'
```



<details>
<summary><b>Response Schema</b></summary>

#### Records

| Field Name | Type | Description |
|------------|------|-------------|
| `id` | `null \| integer` |  |
| `type` | `null \| string` |  |
| `status` | `null \| string` |  |
| `description` | `null \| string` |  |
| `total` | `null \| integer` |  |
| `downloads` | `null \| integer` |  |
| `failed` | `null \| boolean` |  |
| `created_at` | `null \| integer` |  |
| `updated_at` | `null \| integer` |  |
| `deduplicate_id` | `null \| string` |  |
| `user_id` | `null \| integer` |  |
| `user_email` | `null \| string` |  |


</details>

### Exports Create

Triggers a new export of customer data. Use filters to select which customers to export.

#### Python SDK

```python
await customer_io.exports.create(
    filters={}
)
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/integrations/connectors/{your_connector_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "exports",
    "action": "create",
    "params": {
        "filters": {}
    }
}'
```


#### Parameters

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `filters` | `object` | Yes | Audience filter conditions to select which customers to export. Uses boolean logic with "and", "or", "not" arrays of conditions, "segment" objects with an "id" field, and "attribute" objects with "field", "operator", and "value" fields. Example: \{"and": [\{"segment": \{"id": 3\}\}, \{"attribute": \{"field": "plan", "operator": "eq", "value": "premium"\}\}]\}
 |


### Exports Get

Returns a single export by ID.

#### Python SDK

```python
await customer_io.exports.get(
    export_id=0
)
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/integrations/connectors/{your_connector_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "exports",
    "action": "get",
    "params": {
        "export_id": 0
    }
}'
```


#### Parameters

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `export_id` | `integer` | Yes | The export identifier |


<details>
<summary><b>Response Schema</b></summary>

#### Records

| Field Name | Type | Description |
|------------|------|-------------|
| `id` | `null \| integer` |  |
| `type` | `null \| string` |  |
| `status` | `null \| string` |  |
| `description` | `null \| string` |  |
| `total` | `null \| integer` |  |
| `downloads` | `null \| integer` |  |
| `failed` | `null \| boolean` |  |
| `created_at` | `null \| integer` |  |
| `updated_at` | `null \| integer` |  |
| `deduplicate_id` | `null \| string` |  |
| `user_id` | `null \| integer` |  |
| `user_email` | `null \| string` |  |


</details>

## Transactional Email

### Transactional Email Create

Sends a transactional email to a single recipient. Can use a pre-built template (via transactional_message_id) or provide inline content (subject, body, from). Creates the recipient profile if it does not already exist.


#### Python SDK

```python
await customer_io.transactional_email.create(
    transactional_message_id=0,
    to="<str>",
    identifiers={},
    message_data={},
    from_="<str>",
    subject="<str>",
    body="<str>",
    body_plain="<str>",
    reply_to="<str>",
    bcc="<str>",
    headers={},
    preheader_text="<str>",
    attachments={},
    disable_message_retention=True,
    send_to_unsubscribed=True,
    tracked=True,
    queue_draft=True,
    send_at=0
)
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/integrations/connectors/{your_connector_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "transactional_email",
    "action": "create",
    "params": {
        "transactional_message_id": 0,
        "to": "<str>",
        "identifiers": {},
        "message_data": {},
        "from": "<str>",
        "subject": "<str>",
        "body": "<str>",
        "body_plain": "<str>",
        "reply_to": "<str>",
        "bcc": "<str>",
        "headers": {},
        "preheader_text": "<str>",
        "attachments": {},
        "disable_message_retention": True,
        "send_to_unsubscribed": True,
        "tracked": True,
        "queue_draft": True,
        "send_at": 0
    }
}'
```


#### Parameters

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `transactional_message_id` | `integer \| string` | No | Template ID (number) or trigger name (string). Required if not providing inline body/subject/from. |
| `to` | `string` | Yes | Recipient email address. Supports display name format: "Name \<email\>" |
| `identifiers` | `object` | Yes | Recipient identity. One of: \{"id": "..."\}, \{"email": "..."\}, or \{"cio_id": "..."\} |
| `message_data` | `object` | No | Key-value pairs available as \{\{trigger.\<key\>\}\} in templates |
| `from` | `string` | No | Sender address (must be verified domain). Overrides template if provided. |
| `subject` | `string` | No | Email subject line. Overrides template if provided. |
| `body` | `string` | No | HTML email body. Overrides template if provided. |
| `body_plain` | `string` | No | Plaintext email body |
| `reply_to` | `string` | No | Reply-to email address |
| `bcc` | `string` | No | BCC address(es), comma-separated. Max 15 total recipients. |
| `headers` | `object` | No | Custom email headers (ASCII only) |
| `preheader_text` | `string` | No | Email preview text |
| `attachments` | `object` | No | Map of filename to base64 content: \{"file.pdf": "\<base64\>"\}. Max 2MB total. |
| `disable_message_retention` | `boolean` | No | Do not store message body (for sensitive data) |
| `send_to_unsubscribed` | `boolean` | No | Send even if person is unsubscribed |
| `tracked` | `boolean` | No | Enable open and click tracking |
| `queue_draft` | `boolean` | No | Queue as draft instead of sending immediately |
| `send_at` | `integer` | No | Unix timestamp for scheduled delivery (up to 90 days in the future) |


<details>
<summary><b>Response Schema</b></summary>

#### Records

| Field Name | Type | Description |
|------------|------|-------------|
| `delivery_id` | `null \| string` |  |
| `queued_at` | `null \| integer` |  |


</details>

## Transactional Sms

### Transactional Sms Create

Sends a transactional SMS to a single recipient. Always requires a pre-built template (transactional_message_id). Requires Twilio integration to be configured in the workspace.


#### Python SDK

```python
await customer_io.transactional_sms.create(
    transactional_message_id=0,
    to="<str>",
    identifiers={},
    message_data={},
    from_="<str>",
    send_to_unsubscribed=True,
    tracked=True,
    queue_draft=True,
    disable_message_retention=True
)
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/integrations/connectors/{your_connector_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "transactional_sms",
    "action": "create",
    "params": {
        "transactional_message_id": 0,
        "to": "<str>",
        "identifiers": {},
        "message_data": {},
        "from": "<str>",
        "send_to_unsubscribed": True,
        "tracked": True,
        "queue_draft": True,
        "disable_message_retention": True
    }
}'
```


#### Parameters

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `transactional_message_id` | `integer \| string` | Yes | Template ID (number) or trigger name (string). Always required for SMS. |
| `to` | `string` | Yes | Phone number in E.164 format (e.g. +15551234567) |
| `identifiers` | `object` | Yes | Recipient identity. One of: \{"id": "..."\}, \{"email": "..."\}, or \{"cio_id": "..."\} |
| `message_data` | `object` | No | Key-value pairs available as \{\{trigger.\<key\>\}\} in templates |
| `from` | `string` | No | Override sender phone number (must be verified in Twilio) |
| `send_to_unsubscribed` | `boolean` | No | Send even if person is unsubscribed |
| `tracked` | `boolean` | No | Enable link tracking |
| `queue_draft` | `boolean` | No | Queue as draft instead of sending immediately |
| `disable_message_retention` | `boolean` | No | Do not store message content |


<details>
<summary><b>Response Schema</b></summary>

#### Records

| Field Name | Type | Description |
|------------|------|-------------|
| `delivery_id` | `null \| string` |  |
| `queued_at` | `null \| integer` |  |


</details>

## Transactional Push

### Transactional Push Create

Sends a transactional push notification to a single recipient. Can use a template or provide inline title and message. Requires push notifications to be configured in the workspace.


#### Python SDK

```python
await customer_io.transactional_push.create(
    transactional_message_id=0,
    to="<str>",
    identifiers={},
    message_data={},
    title="<str>",
    message="<str>",
    link="<str>",
    image_url="<str>",
    custom_data={},
    custom_payload={},
    sound="<str>",
    send_to_unsubscribed=True,
    queue_draft=True,
    disable_message_retention=True,
    send_at=0
)
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/integrations/connectors/{your_connector_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "transactional_push",
    "action": "create",
    "params": {
        "transactional_message_id": 0,
        "to": "<str>",
        "identifiers": {},
        "message_data": {},
        "title": "<str>",
        "message": "<str>",
        "link": "<str>",
        "image_url": "<str>",
        "custom_data": {},
        "custom_payload": {},
        "sound": "<str>",
        "send_to_unsubscribed": True,
        "queue_draft": True,
        "disable_message_retention": True,
        "send_at": 0
    }
}'
```


#### Parameters

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `transactional_message_id` | `integer \| string` | No | Template ID or trigger name. Required if not providing inline title/message. |
| `to` | `string` | No | Device target: "last_used" for most recent device, or a specific device token. Defaults to all devices. |
| `identifiers` | `object` | Yes | Recipient identity. One of: \{"id": "..."\}, \{"email": "..."\}, or \{"cio_id": "..."\} |
| `message_data` | `object` | No | Key-value pairs available as \{\{trigger.\<key\>\}\} in templates |
| `title` | `string` | No | Push notification title (overrides template) |
| `message` | `string` | No | Push notification body (overrides template) |
| `link` | `string` | No | Deep link URL |
| `image_url` | `string` | No | Image URL to display in the notification |
| `custom_data` | `object` | No | Custom key-value data included in the push payload |
| `custom_payload` | `object` | No | Platform-specific payload overrides (iOS/Android) |
| `sound` | `string` | No | Notification sound name |
| `send_to_unsubscribed` | `boolean` | No | Send even if person is unsubscribed |
| `queue_draft` | `boolean` | No | Queue as draft instead of sending immediately |
| `disable_message_retention` | `boolean` | No | Do not store message content |
| `send_at` | `integer` | No | Unix timestamp for scheduled delivery |


<details>
<summary><b>Response Schema</b></summary>

#### Records

| Field Name | Type | Description |
|------------|------|-------------|
| `delivery_id` | `null \| string` |  |
| `queued_at` | `null \| integer` |  |


</details>

## Transactional Inbox Message

### Transactional Inbox Message Create

Sends a transactional in-app inbox message to a single recipient. Always requires a pre-built Inbox-type transactional message template (transactional_message_id). Messages appear in the recipient's notification inbox via the Customer.io SDK.


#### Python SDK

```python
await customer_io.transactional_inbox_message.create(
    transactional_message_id=0,
    identifiers={},
    message_data={}
)
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/integrations/connectors/{your_connector_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "transactional_inbox_message",
    "action": "create",
    "params": {
        "transactional_message_id": 0,
        "identifiers": {},
        "message_data": {}
    }
}'
```


#### Parameters

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `transactional_message_id` | `integer \| string` | Yes | Template ID or trigger name. Must reference an Inbox-type transactional message. |
| `identifiers` | `object` | Yes | Recipient identity. One of: \{"id": "..."\}, \{"email": "..."\}, or \{"cio_id": "..."\} |
| `message_data` | `object` | No | Key-value pairs available as \{\{trigger.\<key\>\}\} in the inbox message template |


<details>
<summary><b>Response Schema</b></summary>

#### Records

| Field Name | Type | Description |
|------------|------|-------------|
| `delivery_id` | `null \| string` |  |
| `queued_at` | `null \| integer` |  |


</details>

## Broadcast Trigger

### Broadcast Trigger Create

Triggers an API-triggered broadcast campaign. The broadcast must be configured as API-triggered in the Customer.io UI. Cannot be triggered more than once every 10 seconds, with a maximum of 5 queued broadcasts per campaign. Recipients must already exist in the workspace.


#### Python SDK

```python
await customer_io.broadcast_trigger.create(
    data={},
    recipients={},
    ids=[],
    emails=[],
    per_user_data=[],
    data_file_url="<str>",
    id_ignore_missing=True,
    email_ignore_missing=True,
    email_add_duplicates=True,
    campaign_id=0
)
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/integrations/connectors/{your_connector_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "broadcast_trigger",
    "action": "create",
    "params": {
        "data": {},
        "recipients": {},
        "ids": [],
        "emails": [],
        "per_user_data": [],
        "data_file_url": "<str>",
        "id_ignore_missing": True,
        "email_ignore_missing": True,
        "email_add_duplicates": True,
        "campaign_id": 0
    }
}'
```


#### Parameters

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `data` | `object` | No | Global data available as \{\{trigger.\<key\>\}\} in broadcast messages |
| `recipients` | `object` | No | Filter object to define audience (overrides UI-defined recipients). Supports and/or/not/segment/attribute conditions. |
| `ids` | `array<string>` | No | List of profile IDs to target (max 10,000) |
| `emails` | `array<string>` | No | List of email addresses to target (max 10,000) |
| `per_user_data` | `array<object>` | No | Per-recipient custom data: [\{"id": "user1", "data": \{...\}\}, ...] |
| `data_file_url` | `string` | No | URL to a JSON Lines file with per-user data |
| `id_ignore_missing` | `boolean` | No | Ignore IDs that do not match existing profiles (default false) |
| `email_ignore_missing` | `boolean` | No | Ignore emails that do not match existing profiles |
| `email_add_duplicates` | `boolean` | No | Send to all profiles sharing an email address |
| `campaign_id` | `integer` | Yes | The broadcast campaign identifier (found in Triggering Details) |


<details>
<summary><b>Response Schema</b></summary>

#### Records

| Field Name | Type | Description |
|------------|------|-------------|
| `id` | `null \| integer` |  |


</details>

