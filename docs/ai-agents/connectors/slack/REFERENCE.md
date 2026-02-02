# Slack full reference

This is the full reference documentation for the Slack agent connector.

## Supported entities and actions

The Slack connector supports the following entities and actions.

| Entity | Actions |
|--------|---------|
| Users | [List](#users-list), [Get](#users-get), [Search](#users-search) |
| Channels | [List](#channels-list), [Get](#channels-get), [Create](#channels-create), [Update](#channels-update), [Search](#channels-search) |
| Channel Messages | [List](#channel-messages-list) |
| Threads | [List](#threads-list) |
| Messages | [Create](#messages-create), [Update](#messages-update) |
| Channel Topics | [Create](#channel-topics-create) |
| Channel Purposes | [Create](#channel-purposes-create) |
| Reactions | [Create](#reactions-create) |

## Users

### Users List

Returns a list of all users in the Slack workspace

#### Python SDK

```python
await slack.users.list()
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/connectors/sources/{your_source_id}/execute' \
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

### Users Search

Search and filter users records powered by Airbyte's data sync. This often provides additional fields and operators beyond what the API natively supports, making it easier to narrow down results before performing further operations. Only available in hosted mode.

#### Python SDK

```python
await slack.users.search(
    query={"filter": {"eq": {"color": "<str>"}}}
)
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/connectors/sources/{your_source_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "users",
    "action": "search",
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
| `cursor` | `string` | No | Pagination cursor from previous response's next_cursor |
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
| `hits` | `array` | List of matching records |
| `hits[].id` | `string` | Record identifier |
| `hits[].score` | `number` | Relevance score |
| `hits[].data` | `object` | Record data containing the searchable fields listed above |
| `hits[].data.color` | `string` | The color assigned to the user for visual purposes. |
| `hits[].data.deleted` | `boolean` | Indicates if the user is deleted or not. |
| `hits[].data.has_2fa` | `boolean` | Flag indicating if the user has two-factor authentication enabled. |
| `hits[].data.id` | `string` | Unique identifier for the user. |
| `hits[].data.is_admin` | `boolean` | Flag specifying if the user is an admin or not. |
| `hits[].data.is_app_user` | `boolean` | Specifies if the user is an app user. |
| `hits[].data.is_bot` | `boolean` | Indicates if the user is a bot account. |
| `hits[].data.is_email_confirmed` | `boolean` | Flag indicating if the user's email is confirmed. |
| `hits[].data.is_forgotten` | `boolean` | Specifies if the user is marked as forgotten. |
| `hits[].data.is_invited_user` | `boolean` | Indicates if the user is invited or not. |
| `hits[].data.is_owner` | `boolean` | Flag indicating if the user is an owner. |
| `hits[].data.is_primary_owner` | `boolean` | Specifies if the user is the primary owner. |
| `hits[].data.is_restricted` | `boolean` | Flag specifying if the user is restricted. |
| `hits[].data.is_ultra_restricted` | `boolean` | Indicates if the user has ultra-restricted access. |
| `hits[].data.name` | `string` | The username of the user. |
| `hits[].data.profile` | `object` | User's profile information containing detailed details. |
| `hits[].data.real_name` | `string` | The real name of the user. |
| `hits[].data.team_id` | `string` | Unique identifier for the team the user belongs to. |
| `hits[].data.tz` | `string` | Timezone of the user. |
| `hits[].data.tz_label` | `string` | Label representing the timezone of the user. |
| `hits[].data.tz_offset` | `integer` | Offset of the user's timezone. |
| `hits[].data.updated` | `integer` | Timestamp of when the user's information was last updated. |
| `hits[].data.who_can_share_contact_card` | `string` | Specifies who can share the user's contact card. |
| `next_cursor` | `string \| null` | Cursor for next page of results |
| `took_ms` | `number` | Query execution time in milliseconds |

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
curl --location 'https://api.airbyte.ai/api/v1/connectors/sources/{your_source_id}/execute' \
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
curl --location 'https://api.airbyte.ai/api/v1/connectors/sources/{your_source_id}/execute' \
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
curl --location 'https://api.airbyte.ai/api/v1/connectors/sources/{your_source_id}/execute' \
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

### Channels Search

Search and filter channels records powered by Airbyte's data sync. This often provides additional fields and operators beyond what the API natively supports, making it easier to narrow down results before performing further operations. Only available in hosted mode.

#### Python SDK

```python
await slack.channels.search(
    query={"filter": {"eq": {"context_team_id": "<str>"}}}
)
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/connectors/sources/{your_source_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "channels",
    "action": "search",
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
| `cursor` | `string` | No | Pagination cursor from previous response's next_cursor |
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
| `hits` | `array` | List of matching records |
| `hits[].id` | `string` | Record identifier |
| `hits[].score` | `number` | Relevance score |
| `hits[].data` | `object` | Record data containing the searchable fields listed above |
| `hits[].data.context_team_id` | `string` | The unique identifier of the team context in which the channel exists. |
| `hits[].data.created` | `integer` | The timestamp when the channel was created. |
| `hits[].data.creator` | `string` | The ID of the user who created the channel. |
| `hits[].data.id` | `string` | The unique identifier of the channel. |
| `hits[].data.is_archived` | `boolean` | Indicates if the channel is archived. |
| `hits[].data.is_channel` | `boolean` | Indicates if the entity is a channel. |
| `hits[].data.is_ext_shared` | `boolean` | Indicates if the channel is externally shared. |
| `hits[].data.is_general` | `boolean` | Indicates if the channel is a general channel in the workspace. |
| `hits[].data.is_group` | `boolean` | Indicates if the channel is a group (private channel) rather than a regular channel. |
| `hits[].data.is_im` | `boolean` | Indicates if the entity is a direct message (IM) channel. |
| `hits[].data.is_member` | `boolean` | Indicates if the calling user is a member of the channel. |
| `hits[].data.is_mpim` | `boolean` | Indicates if the entity is a multiple person direct message (MPIM) channel. |
| `hits[].data.is_org_shared` | `boolean` | Indicates if the channel is organization-wide shared. |
| `hits[].data.is_pending_ext_shared` | `boolean` | Indicates if the channel is pending external shared. |
| `hits[].data.is_private` | `boolean` | Indicates if the channel is a private channel. |
| `hits[].data.is_read_only` | `boolean` | Indicates if the channel is read-only. |
| `hits[].data.is_shared` | `boolean` | Indicates if the channel is shared. |
| `hits[].data.last_read` | `string` | The timestamp of the user's last read message in the channel. |
| `hits[].data.locale` | `string` | The locale of the channel. |
| `hits[].data.name` | `string` | The name of the channel. |
| `hits[].data.name_normalized` | `string` | The normalized name of the channel. |
| `hits[].data.num_members` | `integer` | The number of members in the channel. |
| `hits[].data.parent_conversation` | `string` | The parent conversation of the channel. |
| `hits[].data.pending_connected_team_ids` | `array` | The IDs of teams that are pending to be connected to the channel. |
| `hits[].data.pending_shared` | `array` | The list of pending shared items of the channel. |
| `hits[].data.previous_names` | `array` | The previous names of the channel. |
| `hits[].data.purpose` | `object` | The purpose of the channel. |
| `hits[].data.shared_team_ids` | `array` | The IDs of teams with which the channel is shared. |
| `hits[].data.topic` | `object` | The topic of the channel. |
| `hits[].data.unlinked` | `integer` | Indicates if the channel is unlinked. |
| `hits[].data.updated` | `integer` | The timestamp when the channel was last updated. |
| `next_cursor` | `string \| null` | Cursor for next page of results |
| `took_ms` | `number` | Query execution time in milliseconds |

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
curl --location 'https://api.airbyte.ai/api/v1/connectors/sources/{your_source_id}/execute' \
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
curl --location 'https://api.airbyte.ai/api/v1/connectors/sources/{your_source_id}/execute' \
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
curl --location 'https://api.airbyte.ai/api/v1/connectors/sources/{your_source_id}/execute' \
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
curl --location 'https://api.airbyte.ai/api/v1/connectors/sources/{your_source_id}/execute' \
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
curl --location 'https://api.airbyte.ai/api/v1/connectors/sources/{your_source_id}/execute' \
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

