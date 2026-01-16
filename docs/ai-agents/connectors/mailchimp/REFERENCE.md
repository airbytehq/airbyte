# Mailchimp full reference

This is the full reference documentation for the Mailchimp agent connector.

## Supported entities and actions

The Mailchimp connector supports the following entities and actions.

| Entity | Actions |
|--------|---------|
| Campaigns | [List](#campaigns-list), [Get](#campaigns-get) |
| Lists | [List](#lists-list), [Get](#lists-get) |
| List Members | [List](#list-members-list), [Get](#list-members-get) |
| Reports | [List](#reports-list), [Get](#reports-get) |
| Email Activity | [List](#email-activity-list) |
| Automations | [List](#automations-list) |
| Tags | [List](#tags-list) |
| Interest Categories | [List](#interest-categories-list), [Get](#interest-categories-get) |
| Interests | [List](#interests-list), [Get](#interests-get) |
| Segments | [List](#segments-list), [Get](#segments-get) |
| Segment Members | [List](#segment-members-list) |
| Unsubscribes | [List](#unsubscribes-list) |

### Campaigns

#### Campaigns List

Get all campaigns in an account

**Python SDK**

```python
await mailchimp.campaigns.list()
```

**API**

```bash
curl --location 'https://api.airbyte.ai/api/v1/connectors/sources/{your_source_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "campaigns",
    "action": "list"
}'
```


**Parameters**

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `count` | `integer` | No | The number of records to return. Default is 10. Maximum is 1000. |
| `offset` | `integer` | No | Used for pagination, this is the number of records from a collection to skip. |
| `type` | `"regular" \| "plaintext" \| "absplit" \| "rss" \| "variate"` | No | The campaign type |
| `status` | `"save" \| "paused" \| "schedule" \| "sending" \| "sent"` | No | The status of the campaign |
| `before_send_time` | `string` | No | Restrict the response to campaigns sent before the set time |
| `since_send_time` | `string` | No | Restrict the response to campaigns sent after the set time |
| `before_create_time` | `string` | No | Restrict the response to campaigns created before the set time |
| `since_create_time` | `string` | No | Restrict the response to campaigns created after the set time |
| `list_id` | `string` | No | The unique id for the list |
| `folder_id` | `string` | No | The unique folder id |
| `sort_field` | `"create_time" \| "send_time"` | No | Returns files sorted by the specified field |
| `sort_dir` | `"ASC" \| "DESC"` | No | Determines the order direction for sorted results |


<details>
<summary><b>Response Schema</b></summary>

**Records**

| Field Name | Type | Description |
|------------|------|-------------|
| `id` | `string` |  |
| `web_id` | `integer \| null` |  |
| `parent_campaign_id` | `string \| null` |  |
| `type` | `string \| null` |  |
| `create_time` | `string \| null` |  |
| `archive_url` | `string \| null` |  |
| `long_archive_url` | `string \| null` |  |
| `status` | `string \| null` |  |
| `emails_sent` | `integer \| null` |  |
| `send_time` | `string \| null` |  |
| `content_type` | `string \| null` |  |
| `needs_block_refresh` | `boolean \| null` |  |
| `resendable` | `boolean \| null` |  |
| `recipients` | `object \| null` |  |
| `settings` | `object \| null` |  |
| `tracking` | `object \| null` |  |
| `report_summary` | `object \| null` |  |
| `delivery_status` | `object \| null` |  |


**Meta**

| Field Name | Type | Description |
|------------|------|-------------|
| `total_items` | `integer` |  |

</details>

#### Campaigns Get

Get information about a specific campaign

**Python SDK**

```python
await mailchimp.campaigns.get(
    campaign_id="<str>"
)
```

**API**

```bash
curl --location 'https://api.airbyte.ai/api/v1/connectors/sources/{your_source_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "campaigns",
    "action": "get",
    "params": {
        "campaign_id": "<str>"
    }
}'
```


**Parameters**

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `campaign_id` | `string` | Yes | The unique id for the campaign |


<details>
<summary><b>Response Schema</b></summary>

**Records**

| Field Name | Type | Description |
|------------|------|-------------|
| `id` | `string` |  |
| `web_id` | `integer \| null` |  |
| `parent_campaign_id` | `string \| null` |  |
| `type` | `string \| null` |  |
| `create_time` | `string \| null` |  |
| `archive_url` | `string \| null` |  |
| `long_archive_url` | `string \| null` |  |
| `status` | `string \| null` |  |
| `emails_sent` | `integer \| null` |  |
| `send_time` | `string \| null` |  |
| `content_type` | `string \| null` |  |
| `needs_block_refresh` | `boolean \| null` |  |
| `resendable` | `boolean \| null` |  |
| `recipients` | `object \| null` |  |
| `settings` | `object \| null` |  |
| `tracking` | `object \| null` |  |
| `report_summary` | `object \| null` |  |
| `delivery_status` | `object \| null` |  |


</details>

### Lists

#### Lists List

Get information about all lists in the account

**Python SDK**

```python
await mailchimp.lists.list()
```

**API**

```bash
curl --location 'https://api.airbyte.ai/api/v1/connectors/sources/{your_source_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "lists",
    "action": "list"
}'
```


**Parameters**

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `count` | `integer` | No | The number of records to return |
| `offset` | `integer` | No | Used for pagination |
| `before_date_created` | `string` | No | Restrict response to lists created before the set date |
| `since_date_created` | `string` | No | Restrict response to lists created after the set date |
| `before_campaign_last_sent` | `string` | No | Restrict results to lists created before the last campaign send date |
| `since_campaign_last_sent` | `string` | No | Restrict results to lists created after the last campaign send date |
| `email` | `string` | No | Restrict results to lists that include a specific subscriber's email address |
| `sort_field` | `"date_created"` | No | Returns files sorted by the specified field |
| `sort_dir` | `"ASC" \| "DESC"` | No | Determines the order direction for sorted results |


<details>
<summary><b>Response Schema</b></summary>

**Records**

| Field Name | Type | Description |
|------------|------|-------------|
| `id` | `string` |  |
| `web_id` | `integer \| null` |  |
| `name` | `string \| null` |  |
| `contact` | `object \| null` |  |
| `permission_reminder` | `string \| null` |  |
| `use_archive_bar` | `boolean \| null` |  |
| `campaign_defaults` | `object \| null` |  |
| `notify_on_subscribe` | `string \| null` |  |
| `notify_on_unsubscribe` | `string \| null` |  |
| `date_created` | `string \| null` |  |
| `list_rating` | `integer \| null` |  |
| `email_type_option` | `boolean \| null` |  |
| `subscribe_url_short` | `string \| null` |  |
| `subscribe_url_long` | `string \| null` |  |
| `beamer_address` | `string \| null` |  |
| `visibility` | `string \| null` |  |
| `double_optin` | `boolean \| null` |  |
| `has_welcome` | `boolean \| null` |  |
| `marketing_permissions` | `boolean \| null` |  |
| `stats` | `object \| null` |  |


**Meta**

| Field Name | Type | Description |
|------------|------|-------------|
| `total_items` | `integer` |  |

</details>

#### Lists Get

Get information about a specific list in your Mailchimp account

**Python SDK**

```python
await mailchimp.lists.get(
    list_id="<str>"
)
```

**API**

```bash
curl --location 'https://api.airbyte.ai/api/v1/connectors/sources/{your_source_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "lists",
    "action": "get",
    "params": {
        "list_id": "<str>"
    }
}'
```


**Parameters**

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `list_id` | `string` | Yes | The unique ID for the list |


<details>
<summary><b>Response Schema</b></summary>

**Records**

| Field Name | Type | Description |
|------------|------|-------------|
| `id` | `string` |  |
| `web_id` | `integer \| null` |  |
| `name` | `string \| null` |  |
| `contact` | `object \| null` |  |
| `permission_reminder` | `string \| null` |  |
| `use_archive_bar` | `boolean \| null` |  |
| `campaign_defaults` | `object \| null` |  |
| `notify_on_subscribe` | `string \| null` |  |
| `notify_on_unsubscribe` | `string \| null` |  |
| `date_created` | `string \| null` |  |
| `list_rating` | `integer \| null` |  |
| `email_type_option` | `boolean \| null` |  |
| `subscribe_url_short` | `string \| null` |  |
| `subscribe_url_long` | `string \| null` |  |
| `beamer_address` | `string \| null` |  |
| `visibility` | `string \| null` |  |
| `double_optin` | `boolean \| null` |  |
| `has_welcome` | `boolean \| null` |  |
| `marketing_permissions` | `boolean \| null` |  |
| `stats` | `object \| null` |  |


</details>

### List Members

#### List Members List

Get information about members in a specific Mailchimp list

**Python SDK**

```python
await mailchimp.list_members.list(
    list_id="<str>"
)
```

**API**

```bash
curl --location 'https://api.airbyte.ai/api/v1/connectors/sources/{your_source_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "list_members",
    "action": "list",
    "params": {
        "list_id": "<str>"
    }
}'
```


**Parameters**

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `list_id` | `string` | Yes | The unique ID for the list |
| `count` | `integer` | No | The number of records to return |
| `offset` | `integer` | No | Used for pagination |
| `email_type` | `string` | No | The email type |
| `status` | `"subscribed" \| "unsubscribed" \| "cleaned" \| "pending" \| "transactional" \| "archived"` | No | The subscriber's status |
| `since_timestamp_opt` | `string` | No | Restrict results to subscribers who opted-in after the set timeframe |
| `before_timestamp_opt` | `string` | No | Restrict results to subscribers who opted-in before the set timeframe |
| `since_last_changed` | `string` | No | Restrict results to subscribers whose information changed after the set timeframe |
| `before_last_changed` | `string` | No | Restrict results to subscribers whose information changed before the set timeframe |
| `unique_email_id` | `string` | No | A unique identifier for the email address across all Mailchimp lists |
| `vip_only` | `boolean` | No | A filter to return only the list's VIP members |
| `interest_category_id` | `string` | No | The unique id for the interest category |
| `interest_ids` | `string` | No | Used to filter list members by interests |
| `interest_match` | `"any" \| "all" \| "none"` | No | Used to filter list members by interests |
| `sort_field` | `"timestamp_opt" \| "timestamp_signup" \| "last_changed"` | No | Returns files sorted by the specified field |
| `sort_dir` | `"ASC" \| "DESC"` | No | Determines the order direction for sorted results |


<details>
<summary><b>Response Schema</b></summary>

**Records**

| Field Name | Type | Description |
|------------|------|-------------|
| `id` | `string` |  |
| `email_address` | `string \| null` |  |
| `unique_email_id` | `string \| null` |  |
| `contact_id` | `string \| null` |  |
| `full_name` | `string \| null` |  |
| `web_id` | `integer \| null` |  |
| `email_type` | `string \| null` |  |
| `status` | `string \| null` |  |
| `unsubscribe_reason` | `string \| null` |  |
| `consents_to_one_to_one_messaging` | `boolean \| null` |  |
| `merge_fields` | `object \| null` |  |
| `interests` | `object \| null` |  |
| `stats` | `object \| null` |  |
| `ip_signup` | `string \| null` |  |
| `timestamp_signup` | `string \| null` |  |
| `ip_opt` | `string \| null` |  |
| `timestamp_opt` | `string \| null` |  |
| `member_rating` | `integer \| null` |  |
| `last_changed` | `string \| null` |  |
| `language` | `string \| null` |  |
| `vip` | `boolean \| null` |  |
| `email_client` | `string \| null` |  |
| `location` | `object \| null` |  |
| `source` | `string \| null` |  |
| `tags_count` | `integer \| null` |  |
| `tags` | `array \| null` |  |
| `list_id` | `string \| null` |  |


**Meta**

| Field Name | Type | Description |
|------------|------|-------------|
| `total_items` | `integer` |  |

</details>

#### List Members Get

Get information about a specific list member

**Python SDK**

```python
await mailchimp.list_members.get(
    list_id="<str>",
    subscriber_hash="<str>"
)
```

**API**

```bash
curl --location 'https://api.airbyte.ai/api/v1/connectors/sources/{your_source_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "list_members",
    "action": "get",
    "params": {
        "list_id": "<str>",
        "subscriber_hash": "<str>"
    }
}'
```


**Parameters**

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `list_id` | `string` | Yes | The unique ID for the list |
| `subscriber_hash` | `string` | Yes | The MD5 hash of the lowercase version of the list member's email address |


<details>
<summary><b>Response Schema</b></summary>

**Records**

| Field Name | Type | Description |
|------------|------|-------------|
| `id` | `string` |  |
| `email_address` | `string \| null` |  |
| `unique_email_id` | `string \| null` |  |
| `contact_id` | `string \| null` |  |
| `full_name` | `string \| null` |  |
| `web_id` | `integer \| null` |  |
| `email_type` | `string \| null` |  |
| `status` | `string \| null` |  |
| `unsubscribe_reason` | `string \| null` |  |
| `consents_to_one_to_one_messaging` | `boolean \| null` |  |
| `merge_fields` | `object \| null` |  |
| `interests` | `object \| null` |  |
| `stats` | `object \| null` |  |
| `ip_signup` | `string \| null` |  |
| `timestamp_signup` | `string \| null` |  |
| `ip_opt` | `string \| null` |  |
| `timestamp_opt` | `string \| null` |  |
| `member_rating` | `integer \| null` |  |
| `last_changed` | `string \| null` |  |
| `language` | `string \| null` |  |
| `vip` | `boolean \| null` |  |
| `email_client` | `string \| null` |  |
| `location` | `object \| null` |  |
| `source` | `string \| null` |  |
| `tags_count` | `integer \| null` |  |
| `tags` | `array \| null` |  |
| `list_id` | `string \| null` |  |


</details>

### Reports

#### Reports List

Get campaign reports

**Python SDK**

```python
await mailchimp.reports.list()
```

**API**

```bash
curl --location 'https://api.airbyte.ai/api/v1/connectors/sources/{your_source_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "reports",
    "action": "list"
}'
```


**Parameters**

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `count` | `integer` | No | The number of records to return |
| `offset` | `integer` | No | Used for pagination |
| `type` | `"regular" \| "plaintext" \| "absplit" \| "rss" \| "variate"` | No | The campaign type |
| `before_send_time` | `string` | No | Restrict the response to campaigns sent before the set time |
| `since_send_time` | `string` | No | Restrict the response to campaigns sent after the set time |


<details>
<summary><b>Response Schema</b></summary>

**Records**

| Field Name | Type | Description |
|------------|------|-------------|
| `id` | `string` |  |
| `campaign_title` | `string \| null` |  |
| `type` | `string \| null` |  |
| `list_id` | `string \| null` |  |
| `list_is_active` | `boolean \| null` |  |
| `list_name` | `string \| null` |  |
| `subject_line` | `string \| null` |  |
| `preview_text` | `string \| null` |  |
| `emails_sent` | `integer \| null` |  |
| `abuse_reports` | `integer \| null` |  |
| `unsubscribed` | `integer \| null` |  |
| `send_time` | `string \| null` |  |
| `rss_last_send` | `string \| null` |  |
| `bounces` | `object \| null` |  |
| `forwards` | `object \| null` |  |
| `opens` | `object \| null` |  |
| `clicks` | `object \| null` |  |
| `facebook_likes` | `object \| null` |  |
| `industry_stats` | `object \| null` |  |
| `list_stats` | `object \| null` |  |
| `ecommerce` | `object \| null` |  |
| `delivery_status` | `object \| null` |  |


**Meta**

| Field Name | Type | Description |
|------------|------|-------------|
| `total_items` | `integer` |  |

</details>

#### Reports Get

Get report details for a specific sent campaign

**Python SDK**

```python
await mailchimp.reports.get(
    campaign_id="<str>"
)
```

**API**

```bash
curl --location 'https://api.airbyte.ai/api/v1/connectors/sources/{your_source_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "reports",
    "action": "get",
    "params": {
        "campaign_id": "<str>"
    }
}'
```


**Parameters**

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `campaign_id` | `string` | Yes | The unique id for the campaign |


<details>
<summary><b>Response Schema</b></summary>

**Records**

| Field Name | Type | Description |
|------------|------|-------------|
| `id` | `string` |  |
| `campaign_title` | `string \| null` |  |
| `type` | `string \| null` |  |
| `list_id` | `string \| null` |  |
| `list_is_active` | `boolean \| null` |  |
| `list_name` | `string \| null` |  |
| `subject_line` | `string \| null` |  |
| `preview_text` | `string \| null` |  |
| `emails_sent` | `integer \| null` |  |
| `abuse_reports` | `integer \| null` |  |
| `unsubscribed` | `integer \| null` |  |
| `send_time` | `string \| null` |  |
| `rss_last_send` | `string \| null` |  |
| `bounces` | `object \| null` |  |
| `forwards` | `object \| null` |  |
| `opens` | `object \| null` |  |
| `clicks` | `object \| null` |  |
| `facebook_likes` | `object \| null` |  |
| `industry_stats` | `object \| null` |  |
| `list_stats` | `object \| null` |  |
| `ecommerce` | `object \| null` |  |
| `delivery_status` | `object \| null` |  |


</details>

### Email Activity

#### Email Activity List

Get a list of member's subscriber activity in a specific campaign

**Python SDK**

```python
await mailchimp.email_activity.list(
    campaign_id="<str>"
)
```

**API**

```bash
curl --location 'https://api.airbyte.ai/api/v1/connectors/sources/{your_source_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "email_activity",
    "action": "list",
    "params": {
        "campaign_id": "<str>"
    }
}'
```


**Parameters**

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `campaign_id` | `string` | Yes | The unique id for the campaign |
| `count` | `integer` | No | The number of records to return |
| `offset` | `integer` | No | Used for pagination |
| `since` | `string` | No | Restrict results to email activity events that occur after a specific time |


<details>
<summary><b>Response Schema</b></summary>

**Records**

| Field Name | Type | Description |
|------------|------|-------------|
| `campaign_id` | `string \| null` |  |
| `list_id` | `string \| null` |  |
| `list_is_active` | `boolean \| null` |  |
| `email_id` | `string \| null` |  |
| `email_address` | `string \| null` |  |
| `activity` | `array \| null` |  |


**Meta**

| Field Name | Type | Description |
|------------|------|-------------|
| `total_items` | `integer` |  |

</details>

### Automations

#### Automations List

Get a summary of an account's classic automations

**Python SDK**

```python
await mailchimp.automations.list()
```

**API**

```bash
curl --location 'https://api.airbyte.ai/api/v1/connectors/sources/{your_source_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "automations",
    "action": "list"
}'
```


**Parameters**

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `count` | `integer` | No | The number of records to return |
| `offset` | `integer` | No | Used for pagination |
| `before_create_time` | `string` | No | Restrict the response to automations created before this time |
| `since_create_time` | `string` | No | Restrict the response to automations created after this time |
| `before_start_time` | `string` | No | Restrict the response to automations started before this time |
| `since_start_time` | `string` | No | Restrict the response to automations started after this time |
| `status` | `"save" \| "paused" \| "sending"` | No | Restrict the results to automations with the specified status |


<details>
<summary><b>Response Schema</b></summary>

**Records**

| Field Name | Type | Description |
|------------|------|-------------|
| `id` | `string` |  |
| `create_time` | `string \| null` |  |
| `start_time` | `string \| null` |  |
| `status` | `string \| null` |  |
| `emails_sent` | `integer \| null` |  |
| `recipients` | `object \| null` |  |
| `settings` | `object \| null` |  |
| `tracking` | `object \| null` |  |
| `report_summary` | `object \| null` |  |


**Meta**

| Field Name | Type | Description |
|------------|------|-------------|
| `total_items` | `integer` |  |

</details>

### Tags

#### Tags List

Search for tags on a list by name

**Python SDK**

```python
await mailchimp.tags.list(
    list_id="<str>"
)
```

**API**

```bash
curl --location 'https://api.airbyte.ai/api/v1/connectors/sources/{your_source_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "tags",
    "action": "list",
    "params": {
        "list_id": "<str>"
    }
}'
```


**Parameters**

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `list_id` | `string` | Yes | The unique ID for the list |
| `name` | `string` | No | The search query used to filter tags |


<details>
<summary><b>Response Schema</b></summary>

**Records**

| Field Name | Type | Description |
|------------|------|-------------|
| `id` | `integer` |  |
| `name` | `string \| null` |  |


**Meta**

| Field Name | Type | Description |
|------------|------|-------------|
| `total_items` | `integer` |  |

</details>

### Interest Categories

#### Interest Categories List

Get information about a list's interest categories

**Python SDK**

```python
await mailchimp.interest_categories.list(
    list_id="<str>"
)
```

**API**

```bash
curl --location 'https://api.airbyte.ai/api/v1/connectors/sources/{your_source_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "interest_categories",
    "action": "list",
    "params": {
        "list_id": "<str>"
    }
}'
```


**Parameters**

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `list_id` | `string` | Yes | The unique ID for the list |
| `count` | `integer` | No | The number of records to return |
| `offset` | `integer` | No | Used for pagination |


<details>
<summary><b>Response Schema</b></summary>

**Records**

| Field Name | Type | Description |
|------------|------|-------------|
| `list_id` | `string \| null` |  |
| `id` | `string` |  |
| `title` | `string \| null` |  |
| `display_order` | `integer \| null` |  |
| `type` | `string \| null` |  |


**Meta**

| Field Name | Type | Description |
|------------|------|-------------|
| `total_items` | `integer` |  |

</details>

#### Interest Categories Get

Get information about a specific interest category

**Python SDK**

```python
await mailchimp.interest_categories.get(
    list_id="<str>",
    interest_category_id="<str>"
)
```

**API**

```bash
curl --location 'https://api.airbyte.ai/api/v1/connectors/sources/{your_source_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "interest_categories",
    "action": "get",
    "params": {
        "list_id": "<str>",
        "interest_category_id": "<str>"
    }
}'
```


**Parameters**

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `list_id` | `string` | Yes | The unique ID for the list |
| `interest_category_id` | `string` | Yes | The unique ID for the interest category |


<details>
<summary><b>Response Schema</b></summary>

**Records**

| Field Name | Type | Description |
|------------|------|-------------|
| `list_id` | `string \| null` |  |
| `id` | `string` |  |
| `title` | `string \| null` |  |
| `display_order` | `integer \| null` |  |
| `type` | `string \| null` |  |


</details>

### Interests

#### Interests List

Get a list of this category's interests

**Python SDK**

```python
await mailchimp.interests.list(
    list_id="<str>",
    interest_category_id="<str>"
)
```

**API**

```bash
curl --location 'https://api.airbyte.ai/api/v1/connectors/sources/{your_source_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "interests",
    "action": "list",
    "params": {
        "list_id": "<str>",
        "interest_category_id": "<str>"
    }
}'
```


**Parameters**

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `list_id` | `string` | Yes | The unique ID for the list |
| `interest_category_id` | `string` | Yes | The unique ID for the interest category |
| `count` | `integer` | No | The number of records to return |
| `offset` | `integer` | No | Used for pagination |


<details>
<summary><b>Response Schema</b></summary>

**Records**

| Field Name | Type | Description |
|------------|------|-------------|
| `category_id` | `string \| null` |  |
| `list_id` | `string \| null` |  |
| `id` | `string` |  |
| `name` | `string \| null` |  |
| `subscriber_count` | `string \| null` |  |
| `display_order` | `integer \| null` |  |


**Meta**

| Field Name | Type | Description |
|------------|------|-------------|
| `total_items` | `integer` |  |

</details>

#### Interests Get

Get interests or group names for a specific category

**Python SDK**

```python
await mailchimp.interests.get(
    list_id="<str>",
    interest_category_id="<str>",
    interest_id="<str>"
)
```

**API**

```bash
curl --location 'https://api.airbyte.ai/api/v1/connectors/sources/{your_source_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "interests",
    "action": "get",
    "params": {
        "list_id": "<str>",
        "interest_category_id": "<str>",
        "interest_id": "<str>"
    }
}'
```


**Parameters**

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `list_id` | `string` | Yes | The unique ID for the list |
| `interest_category_id` | `string` | Yes | The unique ID for the interest category |
| `interest_id` | `string` | Yes | The specific interest or group name |


<details>
<summary><b>Response Schema</b></summary>

**Records**

| Field Name | Type | Description |
|------------|------|-------------|
| `category_id` | `string \| null` |  |
| `list_id` | `string \| null` |  |
| `id` | `string` |  |
| `name` | `string \| null` |  |
| `subscriber_count` | `string \| null` |  |
| `display_order` | `integer \| null` |  |


</details>

### Segments

#### Segments List

Get information about all available segments for a specific list

**Python SDK**

```python
await mailchimp.segments.list(
    list_id="<str>"
)
```

**API**

```bash
curl --location 'https://api.airbyte.ai/api/v1/connectors/sources/{your_source_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "segments",
    "action": "list",
    "params": {
        "list_id": "<str>"
    }
}'
```


**Parameters**

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `list_id` | `string` | Yes | The unique ID for the list |
| `count` | `integer` | No | The number of records to return |
| `offset` | `integer` | No | Used for pagination |
| `type` | `string` | No | Limit results based on segment type |
| `since_created_at` | `string` | No | Restrict results to segments created after the set time |
| `before_created_at` | `string` | No | Restrict results to segments created before the set time |
| `since_updated_at` | `string` | No | Restrict results to segments updated after the set time |
| `before_updated_at` | `string` | No | Restrict results to segments updated before the set time |


<details>
<summary><b>Response Schema</b></summary>

**Records**

| Field Name | Type | Description |
|------------|------|-------------|
| `id` | `integer` |  |
| `name` | `string \| null` |  |
| `member_count` | `integer \| null` |  |
| `type` | `string \| null` |  |
| `created_at` | `string \| null` |  |
| `updated_at` | `string \| null` |  |
| `options` | `object \| null` |  |
| `list_id` | `string \| null` |  |


**Meta**

| Field Name | Type | Description |
|------------|------|-------------|
| `total_items` | `integer` |  |

</details>

#### Segments Get

Get information about a specific segment

**Python SDK**

```python
await mailchimp.segments.get(
    list_id="<str>",
    segment_id="<str>"
)
```

**API**

```bash
curl --location 'https://api.airbyte.ai/api/v1/connectors/sources/{your_source_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "segments",
    "action": "get",
    "params": {
        "list_id": "<str>",
        "segment_id": "<str>"
    }
}'
```


**Parameters**

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `list_id` | `string` | Yes | The unique ID for the list |
| `segment_id` | `string` | Yes | The unique id for the segment |


<details>
<summary><b>Response Schema</b></summary>

**Records**

| Field Name | Type | Description |
|------------|------|-------------|
| `id` | `integer` |  |
| `name` | `string \| null` |  |
| `member_count` | `integer \| null` |  |
| `type` | `string \| null` |  |
| `created_at` | `string \| null` |  |
| `updated_at` | `string \| null` |  |
| `options` | `object \| null` |  |
| `list_id` | `string \| null` |  |


</details>

### Segment Members

#### Segment Members List

Get information about members in a saved segment

**Python SDK**

```python
await mailchimp.segment_members.list(
    list_id="<str>",
    segment_id="<str>"
)
```

**API**

```bash
curl --location 'https://api.airbyte.ai/api/v1/connectors/sources/{your_source_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "segment_members",
    "action": "list",
    "params": {
        "list_id": "<str>",
        "segment_id": "<str>"
    }
}'
```


**Parameters**

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `list_id` | `string` | Yes | The unique ID for the list |
| `segment_id` | `string` | Yes | The unique id for the segment |
| `count` | `integer` | No | The number of records to return |
| `offset` | `integer` | No | Used for pagination |


<details>
<summary><b>Response Schema</b></summary>

**Records**

| Field Name | Type | Description |
|------------|------|-------------|
| `id` | `string` |  |
| `email_address` | `string \| null` |  |
| `unique_email_id` | `string \| null` |  |
| `email_type` | `string \| null` |  |
| `status` | `string \| null` |  |
| `merge_fields` | `object \| null` |  |
| `interests` | `object \| null` |  |
| `stats` | `object \| null` |  |
| `ip_signup` | `string \| null` |  |
| `timestamp_signup` | `string \| null` |  |
| `ip_opt` | `string \| null` |  |
| `timestamp_opt` | `string \| null` |  |
| `member_rating` | `integer \| null` |  |
| `last_changed` | `string \| null` |  |
| `language` | `string \| null` |  |
| `vip` | `boolean \| null` |  |
| `email_client` | `string \| null` |  |
| `location` | `object \| null` |  |
| `list_id` | `string \| null` |  |


**Meta**

| Field Name | Type | Description |
|------------|------|-------------|
| `total_items` | `integer` |  |

</details>

### Unsubscribes

#### Unsubscribes List

Get information about members who have unsubscribed from a specific campaign

**Python SDK**

```python
await mailchimp.unsubscribes.list(
    campaign_id="<str>"
)
```

**API**

```bash
curl --location 'https://api.airbyte.ai/api/v1/connectors/sources/{your_source_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "unsubscribes",
    "action": "list",
    "params": {
        "campaign_id": "<str>"
    }
}'
```


**Parameters**

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `campaign_id` | `string` | Yes | The unique id for the campaign |
| `count` | `integer` | No | The number of records to return |
| `offset` | `integer` | No | Used for pagination |


<details>
<summary><b>Response Schema</b></summary>

**Records**

| Field Name | Type | Description |
|------------|------|-------------|
| `email_id` | `string \| null` |  |
| `email_address` | `string \| null` |  |
| `merge_fields` | `object \| null` |  |
| `vip` | `boolean \| null` |  |
| `timestamp` | `string \| null` |  |
| `reason` | `string \| null` |  |
| `campaign_id` | `string \| null` |  |
| `list_id` | `string \| null` |  |
| `list_is_active` | `boolean \| null` |  |


**Meta**

| Field Name | Type | Description |
|------------|------|-------------|
| `total_items` | `integer` |  |

</details>



## Configuration

The Mailchimp connector requires the following configuration variables. These variables are used to construct the base API URL. Pass them via the `config` parameter when initializing the connector.

| Variable | Type | Required | Default | Description |
|----------|------|----------|---------|-------------|
| `data_center` | `string` | Yes | us1 | The data center for your Mailchimp account (e.g., us1, us2, us6) |


## Authentication

The Mailchimp connector supports the following authentication methods.


### API Key Authentication

| Field Name | Type | Required | Description |
|------------|------|----------|-------------|
| `api_key` | `str` | Yes | Your Mailchimp API key. You can find this in your Mailchimp account under Account > Extras > API keys. |
| `data_center` | `str` | No | The data center for your Mailchimp account. This is the suffix of your API key (e.g., 'us6' if your API key ends with '-us6'). |

#### Example

**Python SDK**

```python
MailchimpConnector(
  auth_config=MailchimpAuthConfig(
    api_key="<Your Mailchimp API key. You can find this in your Mailchimp account under Account > Extras > API keys.>",
    data_center="<The data center for your Mailchimp account. This is the suffix of your API key (e.g., 'us6' if your API key ends with '-us6').>"
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
    "api_key": "<Your Mailchimp API key. You can find this in your Mailchimp account under Account > Extras > API keys.>",
    "data_center": "<The data center for your Mailchimp account. This is the suffix of your API key (e.g., 'us6' if your API key ends with '-us6').>"
  },
  "name": "My Mailchimp Connector"
}'
```

