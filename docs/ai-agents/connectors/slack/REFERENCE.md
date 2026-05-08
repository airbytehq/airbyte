# Slack full reference

This is the full reference documentation for the Slack agent connector.

## Supported entities and actions

The Slack connector supports the following entities and actions.

| Entity | Actions |
|--------|---------|
| Users | [List](#users-list), [Get](#users-get), [Context Store Search](#users-context-store-search) |
| Channels | [List](#channels-list), [Get](#channels-get), [Create](#channels-create), [Update](#channels-update), [Context Store Search](#channels-context-store-search) |
| Channel Messages | [List](#channel-messages-list), [Context Store Search](#channel-messages-context-store-search) |
| Threads | [List](#threads-list), [Context Store Search](#threads-context-store-search) |
| Messages | [Create](#messages-create), [Update](#messages-update), [Delete](#messages-delete) |
| Channel Topics | [Create](#channel-topics-create) |
| Channel Purposes | [Create](#channel-purposes-create) |
| Channel Invites | [Create](#channel-invites-create) |
| Reactions | [Create](#reactions-create), [Delete](#reactions-delete) |
| Ephemeral Messages | [Create](#ephemeral-messages-create) |
| Scheduled Messages | [Create](#scheduled-messages-create) |
| Channel Archives | [Create](#channel-archives-create) |
| Channel Kicks | [Create](#channel-kicks-create) |
| Pins | [Create](#pins-create) |
| Bookmarks | [Create](#bookmarks-create) |

## Users

### Users List

Returns a list of all users in the Slack workspace

#### Python SDK

```python
await slack.users.list()
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/integrations/connectors/{your_connector_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "users",
    "action": "list"
}'
```


#### Parameters

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `cursor` | `string` | No | Pagination cursor for next page |
| `limit` | `integer` | No | Number of users to return per page |


<details>
<summary><b>Response Schema</b></summary>

#### Records

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


#### Meta

| Field Name | Type | Description |
|------------|------|-------------|
| `next_cursor` | `string \| null` |  |

</details>

### Users Get

Get information about a single user by ID

#### Python SDK

```python
await slack.users.get(
    user="<str>"
)
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/integrations/connectors/{your_connector_id}/execute' \
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


#### Parameters

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `user` | `string` | Yes | User ID |


<details>
<summary><b>Response Schema</b></summary>

#### Records

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

### Users Context Store Search

Search and filter users records powered by Airbyte's data sync. This often provides additional fields and operators beyond what the API natively supports, making it easier to narrow down results before performing further operations. Only available in hosted mode.

#### Python SDK

```python
await slack.users.context_store_search(
    query={"filter": {"eq": {"color": "<str>"}}}
)
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/integrations/connectors/{your_connector_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "users",
    "action": "context_store_search",
    "params": {
        "query": {"filter": {"eq": {"color": "<str>"}}}
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
| `color` | `string` | The color assigned to the user for visual purposes. |
| `deleted` | `boolean` | Indicates if the user is deleted or not. |
| `has_2fa` | `boolean` | Flag indicating if the user has two-factor authentication enabled. |
| `id` | `string` | Unique identifier for the user. |
| `is_admin` | `boolean` | Flag specifying if the user is an admin or not. |
| `is_app_user` | `boolean` | Specifies if the user is an app user. |
| `is_bot` | `boolean` | Indicates if the user is a bot account. |
| `is_email_confirmed` | `boolean` | Flag indicating if the user's email is confirmed. |
| `is_forgotten` | `boolean` | Specifies if the user is marked as forgotten. |
| `is_invited_user` | `boolean` | Indicates if the user is invited or not. |
| `is_owner` | `boolean` | Flag indicating if the user is an owner. |
| `is_primary_owner` | `boolean` | Specifies if the user is the primary owner. |
| `is_restricted` | `boolean` | Flag specifying if the user is restricted. |
| `is_ultra_restricted` | `boolean` | Indicates if the user has ultra-restricted access. |
| `name` | `string` | The username of the user. |
| `profile` | `object` | User's profile information containing detailed details. |
| `real_name` | `string` | The real name of the user. |
| `team_id` | `string` | Unique identifier for the team the user belongs to. |
| `tz` | `string` | Timezone of the user. |
| `tz_label` | `string` | Label representing the timezone of the user. |
| `tz_offset` | `integer` | Offset of the user's timezone. |
| `updated` | `integer` | Timestamp of when the user's information was last updated. |
| `who_can_share_contact_card` | `string` | Specifies who can share the user's contact card. |

<details>
<summary><b>Response Schema</b></summary>

| Field Name | Type | Description |
|------------|------|-------------|
| `data` | `array` | List of matching records |
| `meta` | `object` | Pagination metadata |
| `meta.has_more` | `boolean` | Whether additional pages are available |
| `meta.cursor` | `string \| null` | Cursor for next page of results |
| `meta.took_ms` | `number \| null` | Query execution time in milliseconds |
| `data[].color` | `string` | The color assigned to the user for visual purposes. |
| `data[].deleted` | `boolean` | Indicates if the user is deleted or not. |
| `data[].has_2fa` | `boolean` | Flag indicating if the user has two-factor authentication enabled. |
| `data[].id` | `string` | Unique identifier for the user. |
| `data[].is_admin` | `boolean` | Flag specifying if the user is an admin or not. |
| `data[].is_app_user` | `boolean` | Specifies if the user is an app user. |
| `data[].is_bot` | `boolean` | Indicates if the user is a bot account. |
| `data[].is_email_confirmed` | `boolean` | Flag indicating if the user's email is confirmed. |
| `data[].is_forgotten` | `boolean` | Specifies if the user is marked as forgotten. |
| `data[].is_invited_user` | `boolean` | Indicates if the user is invited or not. |
| `data[].is_owner` | `boolean` | Flag indicating if the user is an owner. |
| `data[].is_primary_owner` | `boolean` | Specifies if the user is the primary owner. |
| `data[].is_restricted` | `boolean` | Flag specifying if the user is restricted. |
| `data[].is_ultra_restricted` | `boolean` | Indicates if the user has ultra-restricted access. |
| `data[].name` | `string` | The username of the user. |
| `data[].profile` | `object` | User's profile information containing detailed details. |
| `data[].real_name` | `string` | The real name of the user. |
| `data[].team_id` | `string` | Unique identifier for the team the user belongs to. |
| `data[].tz` | `string` | Timezone of the user. |
| `data[].tz_label` | `string` | Label representing the timezone of the user. |
| `data[].tz_offset` | `integer` | Offset of the user's timezone. |
| `data[].updated` | `integer` | Timestamp of when the user's information was last updated. |
| `data[].who_can_share_contact_card` | `string` | Specifies who can share the user's contact card. |

</details>

## Channels

### Channels List

Returns a list of all channels in the Slack workspace

#### Python SDK

```python
await slack.channels.list()
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/integrations/connectors/{your_connector_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "channels",
    "action": "list"
}'
```


#### Parameters

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `cursor` | `string` | No | Pagination cursor for next page |
| `limit` | `integer` | No | Number of channels to return per page |
| `types` | `string` | No | Mix and match channel types (public_channel, private_channel, mpim, im) |
| `exclude_archived` | `boolean` | No | Exclude archived channels |


<details>
<summary><b>Response Schema</b></summary>

#### Records

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


#### Meta

| Field Name | Type | Description |
|------------|------|-------------|
| `next_cursor` | `string \| null` |  |

</details>

### Channels Get

Get information about a single channel by ID

#### Python SDK

```python
await slack.channels.get(
    channel="<str>"
)
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/integrations/connectors/{your_connector_id}/execute' \
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


#### Parameters

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `channel` | `string` | Yes | Channel ID |


<details>
<summary><b>Response Schema</b></summary>

#### Records

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

### Channels Create

Creates a new public or private channel

#### Python SDK

```python
await slack.channels.create(
    name="<str>",
    is_private=True
)
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/integrations/connectors/{your_connector_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "channels",
    "action": "create",
    "params": {
        "name": "<str>",
        "is_private": True
    }
}'
```


#### Parameters

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `name` | `string` | Yes | Channel name (lowercase, no spaces, max 80 chars) |
| `is_private` | `boolean` | No | Create a private channel instead of public |


<details>
<summary><b>Response Schema</b></summary>

#### Records

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

### Channels Update

Renames an existing channel

#### Python SDK

```python
await slack.channels.update(
    channel="<str>",
    name="<str>"
)
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/integrations/connectors/{your_connector_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "channels",
    "action": "update",
    "params": {
        "channel": "<str>",
        "name": "<str>"
    }
}'
```


#### Parameters

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `channel` | `string` | Yes | Channel ID to rename |
| `name` | `string` | Yes | New channel name (lowercase, no spaces, max 80 chars) |


<details>
<summary><b>Response Schema</b></summary>

#### Records

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

### Channels Context Store Search

Search and filter channels records powered by Airbyte's data sync. This often provides additional fields and operators beyond what the API natively supports, making it easier to narrow down results before performing further operations. Only available in hosted mode.

#### Python SDK

```python
await slack.channels.context_store_search(
    query={"filter": {"eq": {"context_team_id": "<str>"}}}
)
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/integrations/connectors/{your_connector_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "channels",
    "action": "context_store_search",
    "params": {
        "query": {"filter": {"eq": {"context_team_id": "<str>"}}}
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
| `context_team_id` | `string` | The unique identifier of the team context in which the channel exists. |
| `created` | `integer` | The timestamp when the channel was created. |
| `creator` | `string` | The ID of the user who created the channel. |
| `id` | `string` | The unique identifier of the channel. |
| `is_archived` | `boolean` | Indicates if the channel is archived. |
| `is_channel` | `boolean` | Indicates if the entity is a channel. |
| `is_ext_shared` | `boolean` | Indicates if the channel is externally shared. |
| `is_general` | `boolean` | Indicates if the channel is a general channel in the workspace. |
| `is_group` | `boolean` | Indicates if the channel is a group (private channel) rather than a regular channel. |
| `is_im` | `boolean` | Indicates if the entity is a direct message (IM) channel. |
| `is_member` | `boolean` | Indicates if the calling user is a member of the channel. |
| `is_mpim` | `boolean` | Indicates if the entity is a multiple person direct message (MPIM) channel. |
| `is_org_shared` | `boolean` | Indicates if the channel is organization-wide shared. |
| `is_pending_ext_shared` | `boolean` | Indicates if the channel is pending external shared. |
| `is_private` | `boolean` | Indicates if the channel is a private channel. |
| `is_read_only` | `boolean` | Indicates if the channel is read-only. |
| `is_shared` | `boolean` | Indicates if the channel is shared. |
| `last_read` | `string` | The timestamp of the user's last read message in the channel. |
| `locale` | `string` | The locale of the channel. |
| `name` | `string` | The name of the channel. |
| `name_normalized` | `string` | The normalized name of the channel. |
| `num_members` | `integer` | The number of members in the channel. |
| `parent_conversation` | `string` | The parent conversation of the channel. |
| `pending_connected_team_ids` | `array` | The IDs of teams that are pending to be connected to the channel. |
| `pending_shared` | `array` | The list of pending shared items of the channel. |
| `previous_names` | `array` | The previous names of the channel. |
| `purpose` | `object` | The purpose of the channel. |
| `shared_team_ids` | `array` | The IDs of teams with which the channel is shared. |
| `topic` | `object` | The topic of the channel. |
| `unlinked` | `integer` | Indicates if the channel is unlinked. |
| `updated` | `integer` | The timestamp when the channel was last updated. |

<details>
<summary><b>Response Schema</b></summary>

| Field Name | Type | Description |
|------------|------|-------------|
| `data` | `array` | List of matching records |
| `meta` | `object` | Pagination metadata |
| `meta.has_more` | `boolean` | Whether additional pages are available |
| `meta.cursor` | `string \| null` | Cursor for next page of results |
| `meta.took_ms` | `number \| null` | Query execution time in milliseconds |
| `data[].context_team_id` | `string` | The unique identifier of the team context in which the channel exists. |
| `data[].created` | `integer` | The timestamp when the channel was created. |
| `data[].creator` | `string` | The ID of the user who created the channel. |
| `data[].id` | `string` | The unique identifier of the channel. |
| `data[].is_archived` | `boolean` | Indicates if the channel is archived. |
| `data[].is_channel` | `boolean` | Indicates if the entity is a channel. |
| `data[].is_ext_shared` | `boolean` | Indicates if the channel is externally shared. |
| `data[].is_general` | `boolean` | Indicates if the channel is a general channel in the workspace. |
| `data[].is_group` | `boolean` | Indicates if the channel is a group (private channel) rather than a regular channel. |
| `data[].is_im` | `boolean` | Indicates if the entity is a direct message (IM) channel. |
| `data[].is_member` | `boolean` | Indicates if the calling user is a member of the channel. |
| `data[].is_mpim` | `boolean` | Indicates if the entity is a multiple person direct message (MPIM) channel. |
| `data[].is_org_shared` | `boolean` | Indicates if the channel is organization-wide shared. |
| `data[].is_pending_ext_shared` | `boolean` | Indicates if the channel is pending external shared. |
| `data[].is_private` | `boolean` | Indicates if the channel is a private channel. |
| `data[].is_read_only` | `boolean` | Indicates if the channel is read-only. |
| `data[].is_shared` | `boolean` | Indicates if the channel is shared. |
| `data[].last_read` | `string` | The timestamp of the user's last read message in the channel. |
| `data[].locale` | `string` | The locale of the channel. |
| `data[].name` | `string` | The name of the channel. |
| `data[].name_normalized` | `string` | The normalized name of the channel. |
| `data[].num_members` | `integer` | The number of members in the channel. |
| `data[].parent_conversation` | `string` | The parent conversation of the channel. |
| `data[].pending_connected_team_ids` | `array` | The IDs of teams that are pending to be connected to the channel. |
| `data[].pending_shared` | `array` | The list of pending shared items of the channel. |
| `data[].previous_names` | `array` | The previous names of the channel. |
| `data[].purpose` | `object` | The purpose of the channel. |
| `data[].shared_team_ids` | `array` | The IDs of teams with which the channel is shared. |
| `data[].topic` | `object` | The topic of the channel. |
| `data[].unlinked` | `integer` | Indicates if the channel is unlinked. |
| `data[].updated` | `integer` | The timestamp when the channel was last updated. |

</details>

## Channel Messages

### Channel Messages List

Returns messages from a channel

#### Python SDK

```python
await slack.channel_messages.list(
    channel="<str>"
)
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/integrations/connectors/{your_connector_id}/execute' \
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


#### Parameters

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

#### Records

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


#### Meta

| Field Name | Type | Description |
|------------|------|-------------|
| `next_cursor` | `string \| null` |  |
| `has_more` | `boolean \| null` |  |

</details>

### Channel Messages Context Store Search

Search and filter channel messages records powered by Airbyte's data sync. This often provides additional fields and operators beyond what the API natively supports, making it easier to narrow down results before performing further operations. Only available in hosted mode.

#### Python SDK

```python
await slack.channel_messages.context_store_search(
    query={"filter": {"eq": {"type": "<str>"}}}
)
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/integrations/connectors/{your_connector_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "channel_messages",
    "action": "context_store_search",
    "params": {
        "query": {"filter": {"eq": {"type": "<str>"}}}
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
| `type` | `string` | Message type. |
| `subtype` | `string` | Message subtype. |
| `ts` | `string` | Message timestamp (unique identifier). |
| `user` | `string` | User ID who sent the message. |
| `text` | `string` | Message text content. |
| `thread_ts` | `string` | Thread parent timestamp. |
| `reply_count` | `integer` | Number of replies in thread. |
| `reply_users_count` | `integer` | Number of unique users who replied. |
| `latest_reply` | `string` | Timestamp of latest reply. |
| `reply_users` | `array` | User IDs who replied to the thread. |
| `is_locked` | `boolean` | Whether the thread is locked. |
| `subscribed` | `boolean` | Whether the user is subscribed to the thread. |
| `reactions` | `array` | Reactions to the message. |
| `attachments` | `array` | Message attachments. |
| `blocks` | `array` | Block kit blocks. |
| `bot_id` | `string` | Bot ID if message was sent by a bot. |
| `bot_profile` | `object` | Bot profile information. |
| `team` | `string` | Team ID. |

<details>
<summary><b>Response Schema</b></summary>

| Field Name | Type | Description |
|------------|------|-------------|
| `data` | `array` | List of matching records |
| `meta` | `object` | Pagination metadata |
| `meta.has_more` | `boolean` | Whether additional pages are available |
| `meta.cursor` | `string \| null` | Cursor for next page of results |
| `meta.took_ms` | `number \| null` | Query execution time in milliseconds |
| `data[].type` | `string` | Message type. |
| `data[].subtype` | `string` | Message subtype. |
| `data[].ts` | `string` | Message timestamp (unique identifier). |
| `data[].user` | `string` | User ID who sent the message. |
| `data[].text` | `string` | Message text content. |
| `data[].thread_ts` | `string` | Thread parent timestamp. |
| `data[].reply_count` | `integer` | Number of replies in thread. |
| `data[].reply_users_count` | `integer` | Number of unique users who replied. |
| `data[].latest_reply` | `string` | Timestamp of latest reply. |
| `data[].reply_users` | `array` | User IDs who replied to the thread. |
| `data[].is_locked` | `boolean` | Whether the thread is locked. |
| `data[].subscribed` | `boolean` | Whether the user is subscribed to the thread. |
| `data[].reactions` | `array` | Reactions to the message. |
| `data[].attachments` | `array` | Message attachments. |
| `data[].blocks` | `array` | Block kit blocks. |
| `data[].bot_id` | `string` | Bot ID if message was sent by a bot. |
| `data[].bot_profile` | `object` | Bot profile information. |
| `data[].team` | `string` | Team ID. |

</details>

## Threads

### Threads List

Returns messages in a thread (thread replies from conversations.replies endpoint)

#### Python SDK

```python
await slack.threads.list(
    channel="<str>"
)
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/integrations/connectors/{your_connector_id}/execute' \
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


#### Parameters

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

#### Records

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


#### Meta

| Field Name | Type | Description |
|------------|------|-------------|
| `next_cursor` | `string \| null` |  |
| `has_more` | `boolean \| null` |  |

</details>

### Threads Context Store Search

Search and filter threads records powered by Airbyte's data sync. This often provides additional fields and operators beyond what the API natively supports, making it easier to narrow down results before performing further operations. Only available in hosted mode.

#### Python SDK

```python
await slack.threads.context_store_search(
    query={"filter": {"eq": {"type": "<str>"}}}
)
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/integrations/connectors/{your_connector_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "threads",
    "action": "context_store_search",
    "params": {
        "query": {"filter": {"eq": {"type": "<str>"}}}
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
| `type` | `string` | Message type. |
| `subtype` | `string` | Message subtype. |
| `ts` | `string` | Message timestamp (unique identifier). |
| `user` | `string` | User ID who sent the message. |
| `text` | `string` | Message text content. |
| `thread_ts` | `string` | Thread parent timestamp. |
| `parent_user_id` | `string` | User ID of the parent message author (present in thread replies). |
| `reply_count` | `integer` | Number of replies in thread. |
| `reply_users_count` | `integer` | Number of unique users who replied. |
| `latest_reply` | `string` | Timestamp of latest reply. |
| `reply_users` | `array` | User IDs who replied to the thread. |
| `is_locked` | `boolean` | Whether the thread is locked. |
| `subscribed` | `boolean` | Whether the user is subscribed to the thread. |
| `blocks` | `array` | Block kit blocks. |
| `bot_id` | `string` | Bot ID if message was sent by a bot. |
| `team` | `string` | Team ID. |

<details>
<summary><b>Response Schema</b></summary>

| Field Name | Type | Description |
|------------|------|-------------|
| `data` | `array` | List of matching records |
| `meta` | `object` | Pagination metadata |
| `meta.has_more` | `boolean` | Whether additional pages are available |
| `meta.cursor` | `string \| null` | Cursor for next page of results |
| `meta.took_ms` | `number \| null` | Query execution time in milliseconds |
| `data[].type` | `string` | Message type. |
| `data[].subtype` | `string` | Message subtype. |
| `data[].ts` | `string` | Message timestamp (unique identifier). |
| `data[].user` | `string` | User ID who sent the message. |
| `data[].text` | `string` | Message text content. |
| `data[].thread_ts` | `string` | Thread parent timestamp. |
| `data[].parent_user_id` | `string` | User ID of the parent message author (present in thread replies). |
| `data[].reply_count` | `integer` | Number of replies in thread. |
| `data[].reply_users_count` | `integer` | Number of unique users who replied. |
| `data[].latest_reply` | `string` | Timestamp of latest reply. |
| `data[].reply_users` | `array` | User IDs who replied to the thread. |
| `data[].is_locked` | `boolean` | Whether the thread is locked. |
| `data[].subscribed` | `boolean` | Whether the user is subscribed to the thread. |
| `data[].blocks` | `array` | Block kit blocks. |
| `data[].bot_id` | `string` | Bot ID if message was sent by a bot. |
| `data[].team` | `string` | Team ID. |

</details>

## Messages

### Messages Create

Posts a message to a public channel, private channel, or direct message conversation

#### Python SDK

```python
await slack.messages.create(
    channel="<str>",
    text="<str>",
    thread_ts="<str>",
    reply_broadcast=True,
    unfurl_links=True,
    unfurl_media=True
)
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/integrations/connectors/{your_connector_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "messages",
    "action": "create",
    "params": {
        "channel": "<str>",
        "text": "<str>",
        "thread_ts": "<str>",
        "reply_broadcast": True,
        "unfurl_links": True,
        "unfurl_media": True
    }
}'
```


#### Parameters

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `channel` | `string` | Yes | Channel ID, private group ID, or user ID to send message to |
| `text` | `string` | Yes | Message text content (supports mrkdwn formatting) |
| `thread_ts` | `string` | No | Thread timestamp to reply to (for threaded messages) |
| `reply_broadcast` | `boolean` | No | Also post reply to channel when replying to a thread |
| `unfurl_links` | `boolean` | No | Enable unfurling of primarily text-based content |
| `unfurl_media` | `boolean` | No | Enable unfurling of media content |


<details>
<summary><b>Response Schema</b></summary>

#### Records

| Field Name | Type | Description |
|------------|------|-------------|
| `type` | `string \| null` |  |
| `subtype` | `string \| null` |  |
| `text` | `string \| null` |  |
| `ts` | `string` |  |
| `user` | `string \| null` |  |
| `bot_id` | `string \| null` |  |
| `app_id` | `string \| null` |  |
| `team` | `string \| null` |  |
| `bot_profile` | `object \| any` |  |


</details>

### Messages Update

Updates an existing message in a channel

#### Python SDK

```python
await slack.messages.update(
    channel="<str>",
    ts="<str>",
    text="<str>"
)
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/integrations/connectors/{your_connector_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "messages",
    "action": "update",
    "params": {
        "channel": "<str>",
        "ts": "<str>",
        "text": "<str>"
    }
}'
```


#### Parameters

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `channel` | `string` | Yes | Channel ID containing the message |
| `ts` | `string` | Yes | Timestamp of the message to update |
| `text` | `string` | Yes | New message text content |


<details>
<summary><b>Response Schema</b></summary>

#### Records

| Field Name | Type | Description |
|------------|------|-------------|
| `type` | `string \| null` |  |
| `subtype` | `string \| null` |  |
| `text` | `string \| null` |  |
| `ts` | `string` |  |
| `user` | `string \| null` |  |
| `bot_id` | `string \| null` |  |
| `app_id` | `string \| null` |  |
| `team` | `string \| null` |  |
| `bot_profile` | `object \| any` |  |


</details>

### Messages Delete

Deletes a message from a channel. When used with a bot token, may only delete messages posted by that bot.

#### Python SDK

```python
await slack.messages.delete(
    channel="<str>",
    ts="<str>"
)
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/integrations/connectors/{your_connector_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "messages",
    "action": "delete",
    "params": {
        "channel": "<str>",
        "ts": "<str>"
    }
}'
```


#### Parameters

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `channel` | `string` | Yes | Channel ID containing the message to be deleted |
| `ts` | `string` | Yes | Timestamp of the message to be deleted |


<details>
<summary><b>Response Schema</b></summary>

#### Records

| Field Name | Type | Description |
|------------|------|-------------|
| `ok` | `boolean` |  |
| `channel` | `string \| null` |  |
| `ts` | `string \| null` |  |


</details>

## Channel Topics

### Channel Topics Create

Sets the topic for a channel

#### Python SDK

```python
await slack.channel_topics.create(
    channel="<str>",
    topic="<str>"
)
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/integrations/connectors/{your_connector_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "channel_topics",
    "action": "create",
    "params": {
        "channel": "<str>",
        "topic": "<str>"
    }
}'
```


#### Parameters

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `channel` | `string` | Yes | Channel ID to set topic for |
| `topic` | `string` | Yes | New topic text (max 250 characters) |


<details>
<summary><b>Response Schema</b></summary>

#### Records

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

## Channel Purposes

### Channel Purposes Create

Sets the purpose for a channel

#### Python SDK

```python
await slack.channel_purposes.create(
    channel="<str>",
    purpose="<str>"
)
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/integrations/connectors/{your_connector_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "channel_purposes",
    "action": "create",
    "params": {
        "channel": "<str>",
        "purpose": "<str>"
    }
}'
```


#### Parameters

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `channel` | `string` | Yes | Channel ID to set purpose for |
| `purpose` | `string` | Yes | New purpose text (max 250 characters) |


<details>
<summary><b>Response Schema</b></summary>

#### Records

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

## Channel Invites

### Channel Invites Create

Invites one or more users to a public or private channel

#### Python SDK

```python
await slack.channel_invites.create(
    channel="<str>",
    users="<str>",
    force=True
)
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/integrations/connectors/{your_connector_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "channel_invites",
    "action": "create",
    "params": {
        "channel": "<str>",
        "users": "<str>",
        "force": True
    }
}'
```


#### Parameters

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `channel` | `string` | Yes | The ID of the public or private channel to invite user(s) to |
| `users` | `string` | Yes | A comma separated list of user IDs. Up to 1000 users may be listed. |
| `force` | `boolean` | No | When set to true and multiple user IDs are provided, continue inviting the valid ones while disregarding invalid IDs. Defaults to false. |


<details>
<summary><b>Response Schema</b></summary>

#### Records

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

## Reactions

### Reactions Create

Adds a reaction (emoji) to a message

#### Python SDK

```python
await slack.reactions.create(
    channel="<str>",
    timestamp="<str>",
    name="<str>"
)
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/integrations/connectors/{your_connector_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "reactions",
    "action": "create",
    "params": {
        "channel": "<str>",
        "timestamp": "<str>",
        "name": "<str>"
    }
}'
```


#### Parameters

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `channel` | `string` | Yes | Channel ID containing the message |
| `timestamp` | `string` | Yes | Timestamp of the message to react to |
| `name` | `string` | Yes | Reaction emoji name (without colons, e.g., "thumbsup") |


<details>
<summary><b>Response Schema</b></summary>

#### Records

| Field Name | Type | Description |
|------------|------|-------------|
| `ok` | `boolean` |  |


</details>

### Reactions Delete

Removes a reaction (emoji) from a message

#### Python SDK

```python
await slack.reactions.delete(
    channel="<str>",
    timestamp="<str>",
    name="<str>"
)
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/integrations/connectors/{your_connector_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "reactions",
    "action": "delete",
    "params": {
        "channel": "<str>",
        "timestamp": "<str>",
        "name": "<str>"
    }
}'
```


#### Parameters

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `channel` | `string` | Yes | Channel ID containing the message |
| `timestamp` | `string` | Yes | Timestamp of the message to remove reaction from |
| `name` | `string` | Yes | Reaction emoji name to remove (without colons, e.g., "thumbsup") |


<details>
<summary><b>Response Schema</b></summary>

#### Records

| Field Name | Type | Description |
|------------|------|-------------|
| `ok` | `boolean` |  |


</details>

## Ephemeral Messages

### Ephemeral Messages Create

Sends an ephemeral message to a user in a channel. Ephemeral messages are visible only to the target user and do not persist across sessions.

#### Python SDK

```python
await slack.ephemeral_messages.create(
    channel="<str>",
    user="<str>",
    text="<str>",
    thread_ts="<str>",
    blocks="<str>"
)
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/integrations/connectors/{your_connector_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "ephemeral_messages",
    "action": "create",
    "params": {
        "channel": "<str>",
        "user": "<str>",
        "text": "<str>",
        "thread_ts": "<str>",
        "blocks": "<str>"
    }
}'
```


#### Parameters

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `channel` | `string` | Yes | Channel, private group, or IM channel to send the ephemeral message to. Can be an encoded ID or a name. |
| `user` | `string` | Yes | ID of the user who will receive the ephemeral message. The user should be in the channel specified by the channel argument. |
| `text` | `string` | Yes | Message text content (supports mrkdwn formatting). How this field works depends on whether blocks are also provided. |
| `thread_ts` | `string` | No | Provide another message's ts value to post this ephemeral message in a thread. The thread must already be active. |
| `blocks` | `string` | No | A JSON-based array of structured blocks, presented as a URL-encoded string. |


<details>
<summary><b>Response Schema</b></summary>

#### Records

| Field Name | Type | Description |
|------------|------|-------------|
| `ok` | `boolean` |  |
| `message_ts` | `string \| null` |  |


</details>

## Scheduled Messages

### Scheduled Messages Create

Schedules a message for delivery to a channel at a specified time in the future. Messages can be scheduled up to 120 days in advance.

#### Python SDK

```python
await slack.scheduled_messages.create(
    channel="<str>",
    text="<str>",
    post_at=0,
    thread_ts="<str>",
    reply_broadcast=True,
    unfurl_links=True,
    unfurl_media=True
)
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/integrations/connectors/{your_connector_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "scheduled_messages",
    "action": "create",
    "params": {
        "channel": "<str>",
        "text": "<str>",
        "post_at": 0,
        "thread_ts": "<str>",
        "reply_broadcast": True,
        "unfurl_links": True,
        "unfurl_media": True
    }
}'
```


#### Parameters

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `channel` | `string` | Yes | Channel, private group, or DM channel to send the scheduled message to. Can be an encoded ID or a name. |
| `text` | `string` | Yes | Message text content (supports mrkdwn formatting). How this field works depends on whether blocks are also provided. |
| `post_at` | `integer` | Yes | Unix timestamp representing the future time the message should post to Slack. Must be within 120 days. |
| `thread_ts` | `string` | No | Provide another message's ts value to make this message a reply. Avoid using a reply's ts value; use its parent instead. |
| `reply_broadcast` | `boolean` | No | Used in conjunction with thread_ts and indicates whether reply should be made visible to everyone in the channel. Defaults to false. |
| `unfurl_links` | `boolean` | No | Pass true to enable unfurling of primarily text-based content. |
| `unfurl_media` | `boolean` | No | Pass false to disable unfurling of media content. |


<details>
<summary><b>Response Schema</b></summary>

#### Records

| Field Name | Type | Description |
|------------|------|-------------|
| `ok` | `boolean` |  |
| `channel` | `string \| null` |  |
| `scheduled_message_id` | `string \| null` |  |
| `post_at` | `integer \| null` |  |
| `message` | `object \| any` |  |


</details>

## Channel Archives

### Channel Archives Create

Archives a conversation. Not all types of conversations can be archived.

#### Python SDK

```python
await slack.channel_archives.create(
    channel="<str>"
)
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/integrations/connectors/{your_connector_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "channel_archives",
    "action": "create",
    "params": {
        "channel": "<str>"
    }
}'
```


#### Parameters

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `channel` | `string` | Yes | ID of the channel to archive |


<details>
<summary><b>Response Schema</b></summary>

#### Records

| Field Name | Type | Description |
|------------|------|-------------|
| `ok` | `boolean` |  |


</details>

## Channel Kicks

### Channel Kicks Create

Removes a user from a public or private channel

#### Python SDK

```python
await slack.channel_kicks.create(
    channel="<str>",
    user="<str>"
)
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/integrations/connectors/{your_connector_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "channel_kicks",
    "action": "create",
    "params": {
        "channel": "<str>",
        "user": "<str>"
    }
}'
```


#### Parameters

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `channel` | `string` | Yes | ID of the channel to remove the user from |
| `user` | `string` | Yes | User ID to be removed from the channel |


<details>
<summary><b>Response Schema</b></summary>

#### Records

| Field Name | Type | Description |
|------------|------|-------------|
| `ok` | `boolean` |  |
| `errors` | `object \| null` |  |


</details>

## Pins

### Pins Create

Pins a message to a particular channel. Both channel and timestamp are required.

#### Python SDK

```python
await slack.pins.create(
    channel="<str>",
    timestamp="<str>"
)
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/integrations/connectors/{your_connector_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "pins",
    "action": "create",
    "params": {
        "channel": "<str>",
        "timestamp": "<str>"
    }
}'
```


#### Parameters

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `channel` | `string` | Yes | Channel ID to pin the message to |
| `timestamp` | `string` | Yes | Timestamp of the message to pin |


<details>
<summary><b>Response Schema</b></summary>

#### Records

| Field Name | Type | Description |
|------------|------|-------------|
| `ok` | `boolean` |  |


</details>

## Bookmarks

### Bookmarks Create

Adds a bookmark (link) to a channel. Bookmarks appear in the channel header for easy access.

#### Python SDK

```python
await slack.bookmarks.create(
    channel_id="<str>",
    title="<str>",
    type="<str>",
    link="<str>",
    emoji="<str>"
)
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/integrations/connectors/{your_connector_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "bookmarks",
    "action": "create",
    "params": {
        "channel_id": "<str>",
        "title": "<str>",
        "type": "<str>",
        "link": "<str>",
        "emoji": "<str>"
    }
}'
```


#### Parameters

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `channel_id` | `string` | Yes | Channel ID to add the bookmark to |
| `title` | `string` | Yes | Title for the bookmark |
| `type` | `string` | Yes | Type of the bookmark (e.g., "link") |
| `link` | `string` | No | URL to bookmark (required for link type). Must begin with http:// or https://. |
| `emoji` | `string` | No | Emoji tag to apply to the bookmark (e.g., ":rocket:") |


<details>
<summary><b>Response Schema</b></summary>

#### Records

| Field Name | Type | Description |
|------------|------|-------------|
| `id` | `string \| null` |  |
| `channel_id` | `string \| null` |  |
| `title` | `string \| null` |  |
| `link` | `string \| null` |  |
| `emoji` | `string \| null` |  |
| `icon_url` | `string \| null` |  |
| `type` | `string \| null` |  |
| `entity_id` | `string \| null` |  |
| `date_created` | `integer \| null` |  |
| `date_updated` | `integer \| null` |  |
| `rank` | `string \| null` |  |
| `last_updated_by_user_id` | `string \| null` |  |
| `last_updated_by_team_id` | `string \| null` |  |
| `shortcut_id` | `string \| null` |  |
| `app_id` | `string \| null` |  |


</details>

