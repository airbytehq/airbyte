# Slack full reference

This is the full reference documentation for the Slack agent connector.

## Supported entities and actions

The Slack connector supports the following entities and actions.

| Entity | Actions |
|--------|---------|
| Users | [List](#users-list), [Get](#users-get) |
| Channels | [List](#channels-list), [Get](#channels-get) |
| Channel Messages | [List](#channel-messages-list) |
| Threads | [List](#threads-list) |

### Users

#### Users List

Returns a list of all users in the Slack workspace

**Python SDK**

```python
await slack.users.list()
```

**API**

```bash
curl --location 'https://api.airbyte.ai/api/v1/connectors/sources/{your_source_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "users",
    "action": "list"
}'
```


**Parameters**

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `cursor` | `string` | No | Pagination cursor for next page |
| `limit` | `integer` | No | Number of users to return per page |


<details>
<summary><b>Response Schema</b></summary>

**Records**

| Field Name | Type | Description |
|------------|------|-------------|
| `id` | `string` |  |
| `team_id` | `string \| null` |  |
| `name` | `string \| null` |  |
| `deleted` | `boolean \| null` |  |
| `color` | `string \| null` |  |
| `real_name` | `string \| null` |  |
| `tz` | `string \| null` |  |
| `tz_label` | `string \| null` |  |
| `tz_offset` | `integer \| null` |  |
| `profile` | `object \| any` |  |
| `is_admin` | `boolean \| null` |  |
| `is_owner` | `boolean \| null` |  |
| `is_primary_owner` | `boolean \| null` |  |
| `is_restricted` | `boolean \| null` |  |
| `is_ultra_restricted` | `boolean \| null` |  |
| `is_bot` | `boolean \| null` |  |
| `is_app_user` | `boolean \| null` |  |
| `updated` | `integer \| null` |  |
| `is_email_confirmed` | `boolean \| null` |  |
| `who_can_share_contact_card` | `string \| null` |  |


**Meta**

| Field Name | Type | Description |
|------------|------|-------------|
| `next_cursor` | `string \| null` |  |

</details>

#### Users Get

Get information about a single user by ID

**Python SDK**

```python
await slack.users.get(
    user="<str>"
)
```

**API**

```bash
curl --location 'https://api.airbyte.ai/api/v1/connectors/sources/{your_source_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "users",
    "action": "get",
    "params": {
        "user": "<str>"
    }
}'
```


**Parameters**

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `user` | `string` | Yes | User ID |


<details>
<summary><b>Response Schema</b></summary>

**Records**

| Field Name | Type | Description |
|------------|------|-------------|
| `id` | `string` |  |
| `team_id` | `string \| null` |  |
| `name` | `string \| null` |  |
| `deleted` | `boolean \| null` |  |
| `color` | `string \| null` |  |
| `real_name` | `string \| null` |  |
| `tz` | `string \| null` |  |
| `tz_label` | `string \| null` |  |
| `tz_offset` | `integer \| null` |  |
| `profile` | `object \| any` |  |
| `is_admin` | `boolean \| null` |  |
| `is_owner` | `boolean \| null` |  |
| `is_primary_owner` | `boolean \| null` |  |
| `is_restricted` | `boolean \| null` |  |
| `is_ultra_restricted` | `boolean \| null` |  |
| `is_bot` | `boolean \| null` |  |
| `is_app_user` | `boolean \| null` |  |
| `updated` | `integer \| null` |  |
| `is_email_confirmed` | `boolean \| null` |  |
| `who_can_share_contact_card` | `string \| null` |  |


</details>

### Channels

#### Channels List

Returns a list of all channels in the Slack workspace

**Python SDK**

```python
await slack.channels.list()
```

**API**

```bash
curl --location 'https://api.airbyte.ai/api/v1/connectors/sources/{your_source_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "channels",
    "action": "list"
}'
```


**Parameters**

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `cursor` | `string` | No | Pagination cursor for next page |
| `limit` | `integer` | No | Number of channels to return per page |
| `types` | `string` | No | Mix and match channel types (public_channel, private_channel, mpim, im) |
| `exclude_archived` | `boolean` | No | Exclude archived channels |


<details>
<summary><b>Response Schema</b></summary>

**Records**

| Field Name | Type | Description |
|------------|------|-------------|
| `id` | `string` |  |
| `name` | `string \| null` |  |
| `is_channel` | `boolean \| null` |  |
| `is_group` | `boolean \| null` |  |
| `is_im` | `boolean \| null` |  |
| `is_mpim` | `boolean \| null` |  |
| `is_private` | `boolean \| null` |  |
| `created` | `integer \| null` |  |
| `is_archived` | `boolean \| null` |  |
| `is_general` | `boolean \| null` |  |
| `unlinked` | `integer \| null` |  |
| `name_normalized` | `string \| null` |  |
| `is_shared` | `boolean \| null` |  |
| `is_org_shared` | `boolean \| null` |  |
| `is_pending_ext_shared` | `boolean \| null` |  |
| `pending_shared` | `array \| null` |  |
| `context_team_id` | `string \| null` |  |
| `updated` | `integer \| null` |  |
| `creator` | `string \| null` |  |
| `is_ext_shared` | `boolean \| null` |  |
| `shared_team_ids` | `array \| null` |  |
| `pending_connected_team_ids` | `array \| null` |  |
| `is_member` | `boolean \| null` |  |
| `topic` | `object \| any` |  |
| `purpose` | `object \| any` |  |
| `previous_names` | `array \| null` |  |
| `num_members` | `integer \| null` |  |
| `parent_conversation` | `string \| null` |  |
| `properties` | `object \| null` |  |
| `is_thread_only` | `boolean \| null` |  |
| `is_read_only` | `boolean \| null` |  |


**Meta**

| Field Name | Type | Description |
|------------|------|-------------|
| `next_cursor` | `string \| null` |  |

</details>

#### Channels Get

Get information about a single channel by ID

**Python SDK**

```python
await slack.channels.get(
    channel="<str>"
)
```

**API**

```bash
curl --location 'https://api.airbyte.ai/api/v1/connectors/sources/{your_source_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "channels",
    "action": "get",
    "params": {
        "channel": "<str>"
    }
}'
```


**Parameters**

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `channel` | `string` | Yes | Channel ID |


<details>
<summary><b>Response Schema</b></summary>

**Records**

| Field Name | Type | Description |
|------------|------|-------------|
| `id` | `string` |  |
| `name` | `string \| null` |  |
| `is_channel` | `boolean \| null` |  |
| `is_group` | `boolean \| null` |  |
| `is_im` | `boolean \| null` |  |
| `is_mpim` | `boolean \| null` |  |
| `is_private` | `boolean \| null` |  |
| `created` | `integer \| null` |  |
| `is_archived` | `boolean \| null` |  |
| `is_general` | `boolean \| null` |  |
| `unlinked` | `integer \| null` |  |
| `name_normalized` | `string \| null` |  |
| `is_shared` | `boolean \| null` |  |
| `is_org_shared` | `boolean \| null` |  |
| `is_pending_ext_shared` | `boolean \| null` |  |
| `pending_shared` | `array \| null` |  |
| `context_team_id` | `string \| null` |  |
| `updated` | `integer \| null` |  |
| `creator` | `string \| null` |  |
| `is_ext_shared` | `boolean \| null` |  |
| `shared_team_ids` | `array \| null` |  |
| `pending_connected_team_ids` | `array \| null` |  |
| `is_member` | `boolean \| null` |  |
| `topic` | `object \| any` |  |
| `purpose` | `object \| any` |  |
| `previous_names` | `array \| null` |  |
| `num_members` | `integer \| null` |  |
| `parent_conversation` | `string \| null` |  |
| `properties` | `object \| null` |  |
| `is_thread_only` | `boolean \| null` |  |
| `is_read_only` | `boolean \| null` |  |


</details>

### Channel Messages

#### Channel Messages List

Returns messages from a channel

**Python SDK**

```python
await slack.channel_messages.list(
    channel="<str>"
)
```

**API**

```bash
curl --location 'https://api.airbyte.ai/api/v1/connectors/sources/{your_source_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "channel_messages",
    "action": "list",
    "params": {
        "channel": "<str>"
    }
}'
```


**Parameters**

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `channel` | `string` | Yes | Channel ID to get messages from |
| `cursor` | `string` | No | Pagination cursor for next page |
| `limit` | `integer` | No | Number of messages to return per page |
| `oldest` | `string` | No | Start of time range (Unix timestamp) |
| `latest` | `string` | No | End of time range (Unix timestamp) |
| `inclusive` | `boolean` | No | Include messages with oldest or latest timestamps |


<details>
<summary><b>Response Schema</b></summary>

**Records**

| Field Name | Type | Description |
|------------|------|-------------|
| `type` | `string \| null` |  |
| `subtype` | `string \| null` |  |
| `ts` | `string` |  |
| `user` | `string \| null` |  |
| `text` | `string \| null` |  |
| `thread_ts` | `string \| null` |  |
| `reply_count` | `integer \| null` |  |
| `reply_users_count` | `integer \| null` |  |
| `latest_reply` | `string \| null` |  |
| `reply_users` | `array \| null` |  |
| `is_locked` | `boolean \| null` |  |
| `subscribed` | `boolean \| null` |  |
| `reactions` | `array \| null` |  |
| `reactions[].name` | `string \| null` |  |
| `reactions[].users` | `array \| null` |  |
| `reactions[].count` | `integer \| null` |  |
| `attachments` | `array \| null` |  |
| `attachments[].id` | `integer \| null` |  |
| `attachments[].fallback` | `string \| null` |  |
| `attachments[].color` | `string \| null` |  |
| `attachments[].pretext` | `string \| null` |  |
| `attachments[].author_name` | `string \| null` |  |
| `attachments[].author_link` | `string \| null` |  |
| `attachments[].author_icon` | `string \| null` |  |
| `attachments[].title` | `string \| null` |  |
| `attachments[].title_link` | `string \| null` |  |
| `attachments[].text` | `string \| null` |  |
| `attachments[].fields` | `array \| null` |  |
| `attachments[].image_url` | `string \| null` |  |
| `attachments[].thumb_url` | `string \| null` |  |
| `attachments[].footer` | `string \| null` |  |
| `attachments[].footer_icon` | `string \| null` |  |
| `attachments[].ts` | `string \| integer \| null` |  |
| `blocks` | `array \| null` |  |
| `files` | `array \| null` |  |
| `files[].id` | `string \| null` |  |
| `files[].name` | `string \| null` |  |
| `files[].title` | `string \| null` |  |
| `files[].mimetype` | `string \| null` |  |
| `files[].filetype` | `string \| null` |  |
| `files[].pretty_type` | `string \| null` |  |
| `files[].user` | `string \| null` |  |
| `files[].size` | `integer \| null` |  |
| `files[].mode` | `string \| null` |  |
| `files[].is_external` | `boolean \| null` |  |
| `files[].external_type` | `string \| null` |  |
| `files[].is_public` | `boolean \| null` |  |
| `files[].public_url_shared` | `boolean \| null` |  |
| `files[].url_private` | `string \| null` |  |
| `files[].url_private_download` | `string \| null` |  |
| `files[].permalink` | `string \| null` |  |
| `files[].permalink_public` | `string \| null` |  |
| `files[].created` | `integer \| null` |  |
| `files[].timestamp` | `integer \| null` |  |
| `edited` | `object \| any` |  |
| `bot_id` | `string \| null` |  |
| `bot_profile` | `object \| any` |  |
| `app_id` | `string \| null` |  |
| `team` | `string \| null` |  |


**Meta**

| Field Name | Type | Description |
|------------|------|-------------|
| `next_cursor` | `string \| null` |  |
| `has_more` | `boolean \| null` |  |

</details>

### Threads

#### Threads List

Returns messages in a thread (thread replies from conversations.replies endpoint)

**Python SDK**

```python
await slack.threads.list(
    channel="<str>"
)
```

**API**

```bash
curl --location 'https://api.airbyte.ai/api/v1/connectors/sources/{your_source_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "threads",
    "action": "list",
    "params": {
        "channel": "<str>"
    }
}'
```


**Parameters**

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `channel` | `string` | Yes | Channel ID containing the thread |
| `ts` | `string` | No | Timestamp of the parent message (required for thread replies) |
| `cursor` | `string` | No | Pagination cursor for next page |
| `limit` | `integer` | No | Number of replies to return per page |
| `oldest` | `string` | No | Start of time range (Unix timestamp) |
| `latest` | `string` | No | End of time range (Unix timestamp) |
| `inclusive` | `boolean` | No | Include messages with oldest or latest timestamps |


<details>
<summary><b>Response Schema</b></summary>

**Records**

| Field Name | Type | Description |
|------------|------|-------------|
| `type` | `string \| null` |  |
| `subtype` | `string \| null` |  |
| `ts` | `string` |  |
| `user` | `string \| null` |  |
| `text` | `string \| null` |  |
| `thread_ts` | `string \| null` |  |
| `parent_user_id` | `string \| null` |  |
| `reply_count` | `integer \| null` |  |
| `reply_users_count` | `integer \| null` |  |
| `latest_reply` | `string \| null` |  |
| `reply_users` | `array \| null` |  |
| `is_locked` | `boolean \| null` |  |
| `subscribed` | `boolean \| null` |  |
| `reactions` | `array \| null` |  |
| `reactions[].name` | `string \| null` |  |
| `reactions[].users` | `array \| null` |  |
| `reactions[].count` | `integer \| null` |  |
| `attachments` | `array \| null` |  |
| `attachments[].id` | `integer \| null` |  |
| `attachments[].fallback` | `string \| null` |  |
| `attachments[].color` | `string \| null` |  |
| `attachments[].pretext` | `string \| null` |  |
| `attachments[].author_name` | `string \| null` |  |
| `attachments[].author_link` | `string \| null` |  |
| `attachments[].author_icon` | `string \| null` |  |
| `attachments[].title` | `string \| null` |  |
| `attachments[].title_link` | `string \| null` |  |
| `attachments[].text` | `string \| null` |  |
| `attachments[].fields` | `array \| null` |  |
| `attachments[].image_url` | `string \| null` |  |
| `attachments[].thumb_url` | `string \| null` |  |
| `attachments[].footer` | `string \| null` |  |
| `attachments[].footer_icon` | `string \| null` |  |
| `attachments[].ts` | `string \| integer \| null` |  |
| `blocks` | `array \| null` |  |
| `files` | `array \| null` |  |
| `files[].id` | `string \| null` |  |
| `files[].name` | `string \| null` |  |
| `files[].title` | `string \| null` |  |
| `files[].mimetype` | `string \| null` |  |
| `files[].filetype` | `string \| null` |  |
| `files[].pretty_type` | `string \| null` |  |
| `files[].user` | `string \| null` |  |
| `files[].size` | `integer \| null` |  |
| `files[].mode` | `string \| null` |  |
| `files[].is_external` | `boolean \| null` |  |
| `files[].external_type` | `string \| null` |  |
| `files[].is_public` | `boolean \| null` |  |
| `files[].public_url_shared` | `boolean \| null` |  |
| `files[].url_private` | `string \| null` |  |
| `files[].url_private_download` | `string \| null` |  |
| `files[].permalink` | `string \| null` |  |
| `files[].permalink_public` | `string \| null` |  |
| `files[].created` | `integer \| null` |  |
| `files[].timestamp` | `integer \| null` |  |
| `edited` | `object \| any` |  |
| `bot_id` | `string \| null` |  |
| `bot_profile` | `object \| any` |  |
| `app_id` | `string \| null` |  |
| `team` | `string \| null` |  |


**Meta**

| Field Name | Type | Description |
|------------|------|-------------|
| `next_cursor` | `string \| null` |  |
| `has_more` | `boolean \| null` |  |

</details>



## Authentication

The Slack connector supports the following authentication methods.


### Token Authentication

| Field Name | Type | Required | Description |
|------------|------|----------|-------------|
| `access_token` | `str` | Yes | Your Slack Bot Token (xoxb-) or User Token (xoxp-) |

#### Example

**Python SDK**

```python
SlackConnector(
  auth_config=SlackTokenAuthenticationAuthConfig(
    access_token="<Your Slack Bot Token (xoxb-) or User Token (xoxp-)>"
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
    "access_token": "<Your Slack Bot Token (xoxb-) or User Token (xoxp-)>"
  },
  "name": "My Slack Connector"
}'
```


### OAuth 2.0 Authentication

| Field Name | Type | Required | Description |
|------------|------|----------|-------------|
| `client_id` | `str` | Yes | Your Slack App's Client ID |
| `client_secret` | `str` | Yes | Your Slack App's Client Secret |
| `access_token` | `str` | Yes | OAuth access token (bot token from oauth.v2.access response) |

#### Example

**Python SDK**

```python
SlackConnector(
  auth_config=SlackOauth20AuthenticationAuthConfig(
    client_id="<Your Slack App's Client ID>",
    client_secret="<Your Slack App's Client Secret>",
    access_token="<OAuth access token (bot token from oauth.v2.access response)>"
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
    "client_id": "<Your Slack App's Client ID>",
    "client_secret": "<Your Slack App's Client Secret>",
    "access_token": "<OAuth access token (bot token from oauth.v2.access response)>"
  },
  "name": "My Slack Connector"
}'
```

