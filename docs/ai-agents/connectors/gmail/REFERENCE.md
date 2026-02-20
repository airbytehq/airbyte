# Gmail full reference

This is the full reference documentation for the Gmail agent connector.

## Supported entities and actions

The Gmail connector supports the following entities and actions.

| Entity | Actions |
|--------|---------|
| Profile | [Get](#profile-get) |
| Messages | [List](#messages-list), [Get](#messages-get), [Create](#messages-create), [Update](#messages-update) |
| Labels | [List](#labels-list), [Create](#labels-create), [Get](#labels-get), [Update](#labels-update), [Delete](#labels-delete) |
| Drafts | [List](#drafts-list), [Create](#drafts-create), [Get](#drafts-get), [Update](#drafts-update), [Delete](#drafts-delete) |
| Drafts Send | [Create](#drafts-send-create) |
| Threads | [List](#threads-list), [Get](#threads-get) |
| Messages Trash | [Create](#messages-trash-create) |
| Messages Untrash | [Create](#messages-untrash-create) |

## Profile

### Profile Get

Gets the current user's Gmail profile including email address and mailbox statistics

#### Python SDK

```python
await gmail.profile.get()
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/integrations/connectors/{your_connector_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "profile",
    "action": "get"
}'
```



<details>
<summary><b>Response Schema</b></summary>

#### Records

| Field Name | Type | Description |
|------------|------|-------------|
| `emailAddress` | `string \| null` |  |
| `messagesTotal` | `integer \| null` |  |
| `threadsTotal` | `integer \| null` |  |
| `historyId` | `string \| null` |  |


</details>

## Messages

### Messages List

Lists the messages in the user's mailbox. Returns message IDs and thread IDs.

#### Python SDK

```python
await gmail.messages.list()
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
| `maxResults` | `integer` | No | Maximum number of messages to return (1-500) |
| `pageToken` | `string` | No | Page token to retrieve a specific page of results |
| `q` | `string` | No | Gmail search query (same format as Gmail search box, e.g. "from:user@example.com", "is:unread", "subject:hello") |
| `labelIds` | `string` | No | Only return messages with labels matching all of the specified label IDs (comma-separated) |
| `includeSpamTrash` | `boolean` | No | Include messages from SPAM and TRASH in the results |


<details>
<summary><b>Response Schema</b></summary>

#### Records

| Field Name | Type | Description |
|------------|------|-------------|
| `id` | `string` |  |
| `threadId` | `string \| null` |  |


#### Meta

| Field Name | Type | Description |
|------------|------|-------------|
| `nextPageToken` | `string \| null` |  |
| `resultSizeEstimate` | `integer \| null` |  |

</details>

### Messages Get

Gets the full email message content including headers, body, and attachments metadata

#### Python SDK

```python
await gmail.messages.get(
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
        "messageId": "<str>"
    }
}'
```


#### Parameters

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `messageId` | `string` | Yes | The ID of the message to retrieve |
| `format` | `"full" \| "metadata" \| "minimal" \| "raw"` | No | The format to return the message in (full, metadata, minimal, raw) |
| `metadataHeaders` | `string` | No | When format is METADATA, only include headers specified (comma-separated) |


<details>
<summary><b>Response Schema</b></summary>

#### Records

| Field Name | Type | Description |
|------------|------|-------------|
| `id` | `string` |  |
| `threadId` | `string \| null` |  |
| `labelIds` | `array \| null` |  |
| `snippet` | `string \| null` |  |
| `historyId` | `string \| null` |  |
| `internalDate` | `string \| null` |  |
| `sizeEstimate` | `integer \| null` |  |
| `raw` | `string \| null` |  |
| `payload` | `object \| any` |  |


</details>

### Messages Create

Sends a new email message. The message should be provided as a base64url-encoded
RFC 2822 formatted string in the 'raw' field.


#### Python SDK

```python
await gmail.messages.create(
    raw="<str>",
    thread_id="<str>"
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
        "raw": "<str>",
        "threadId": "<str>"
    }
}'
```


#### Parameters

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `raw` | `string` | Yes | The entire email message in RFC 2822 format, base64url encoded |
| `threadId` | `string` | No | The thread ID to reply to (for threading replies in a conversation) |


<details>
<summary><b>Response Schema</b></summary>

#### Records

| Field Name | Type | Description |
|------------|------|-------------|
| `id` | `string` |  |
| `threadId` | `string \| null` |  |
| `labelIds` | `array \| null` |  |
| `snippet` | `string \| null` |  |
| `historyId` | `string \| null` |  |
| `internalDate` | `string \| null` |  |
| `sizeEstimate` | `integer \| null` |  |
| `raw` | `string \| null` |  |
| `payload` | `object \| any` |  |


</details>

### Messages Update

Modifies the labels on a message. Use this to archive (remove INBOX label),
mark as read (remove UNREAD label), mark as unread (add UNREAD label),
star (add STARRED label), or apply custom labels.


#### Python SDK

```python
await gmail.messages.update(
    add_label_ids=[],
    remove_label_ids=[],
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
    "action": "update",
    "params": {
        "addLabelIds": [],
        "removeLabelIds": [],
        "messageId": "<str>"
    }
}'
```


#### Parameters

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `addLabelIds` | `array<string>` | No | A list of label IDs to add to the message (e.g. STARRED, UNREAD, or custom label IDs) |
| `removeLabelIds` | `array<string>` | No | A list of label IDs to remove from the message (e.g. INBOX to archive, UNREAD to mark as read) |
| `messageId` | `string` | Yes | The ID of the message to modify |


<details>
<summary><b>Response Schema</b></summary>

#### Records

| Field Name | Type | Description |
|------------|------|-------------|
| `id` | `string` |  |
| `threadId` | `string \| null` |  |
| `labelIds` | `array \| null` |  |
| `snippet` | `string \| null` |  |
| `historyId` | `string \| null` |  |
| `internalDate` | `string \| null` |  |
| `sizeEstimate` | `integer \| null` |  |
| `raw` | `string \| null` |  |
| `payload` | `object \| any` |  |


</details>

## Labels

### Labels List

Lists all labels in the user's mailbox including system and user-created labels

#### Python SDK

```python
await gmail.labels.list()
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/integrations/connectors/{your_connector_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "labels",
    "action": "list"
}'
```



<details>
<summary><b>Response Schema</b></summary>

#### Records

| Field Name | Type | Description |
|------------|------|-------------|
| `id` | `string` |  |
| `name` | `string \| null` |  |
| `type` | `string \| null` |  |
| `messageListVisibility` | `string \| null` |  |
| `labelListVisibility` | `string \| null` |  |
| `messagesTotal` | `integer \| null` |  |
| `messagesUnread` | `integer \| null` |  |
| `threadsTotal` | `integer \| null` |  |
| `threadsUnread` | `integer \| null` |  |
| `color` | `object \| any` |  |


</details>

### Labels Create

Creates a new label in the user's mailbox

#### Python SDK

```python
await gmail.labels.create(
    name="<str>",
    message_list_visibility="<str>",
    label_list_visibility="<str>",
    color={}
)
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/integrations/connectors/{your_connector_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "labels",
    "action": "create",
    "params": {
        "name": "<str>",
        "messageListVisibility": "<str>",
        "labelListVisibility": "<str>",
        "color": {}
    }
}'
```


#### Parameters

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `name` | `string` | Yes | The display name of the label |
| `messageListVisibility` | `"show" \| "hide"` | No | The visibility of messages with this label in the message list (show or hide) |
| `labelListVisibility` | `"labelShow" \| "labelShowIfUnread" \| "labelHide"` | No | The visibility of the label in the label list |
| `color` | `object` | No | The color to assign to the label |
| `color.textColor` | `string` | No | The text color of the label as a hex string (#RRGGBB) |
| `color.backgroundColor` | `string` | No | The background color of the label as a hex string (#RRGGBB) |


<details>
<summary><b>Response Schema</b></summary>

#### Records

| Field Name | Type | Description |
|------------|------|-------------|
| `id` | `string` |  |
| `name` | `string \| null` |  |
| `type` | `string \| null` |  |
| `messageListVisibility` | `string \| null` |  |
| `labelListVisibility` | `string \| null` |  |
| `messagesTotal` | `integer \| null` |  |
| `messagesUnread` | `integer \| null` |  |
| `threadsTotal` | `integer \| null` |  |
| `threadsUnread` | `integer \| null` |  |
| `color` | `object \| any` |  |


</details>

### Labels Get

Gets a specific label by ID including message and thread counts

#### Python SDK

```python
await gmail.labels.get(
    label_id="<str>"
)
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/integrations/connectors/{your_connector_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "labels",
    "action": "get",
    "params": {
        "labelId": "<str>"
    }
}'
```


#### Parameters

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `labelId` | `string` | Yes | The ID of the label to retrieve |


<details>
<summary><b>Response Schema</b></summary>

#### Records

| Field Name | Type | Description |
|------------|------|-------------|
| `id` | `string` |  |
| `name` | `string \| null` |  |
| `type` | `string \| null` |  |
| `messageListVisibility` | `string \| null` |  |
| `labelListVisibility` | `string \| null` |  |
| `messagesTotal` | `integer \| null` |  |
| `messagesUnread` | `integer \| null` |  |
| `threadsTotal` | `integer \| null` |  |
| `threadsUnread` | `integer \| null` |  |
| `color` | `object \| any` |  |


</details>

### Labels Update

Updates the specified label

#### Python SDK

```python
await gmail.labels.update(
    id="<str>",
    name="<str>",
    message_list_visibility="<str>",
    label_list_visibility="<str>",
    color={},
    label_id="<str>"
)
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/integrations/connectors/{your_connector_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "labels",
    "action": "update",
    "params": {
        "id": "<str>",
        "name": "<str>",
        "messageListVisibility": "<str>",
        "labelListVisibility": "<str>",
        "color": {},
        "labelId": "<str>"
    }
}'
```


#### Parameters

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `id` | `string` | No | The ID of the label (must match the path parameter) |
| `name` | `string` | No | The new display name of the label |
| `messageListVisibility` | `"show" \| "hide"` | No | The visibility of messages with this label in the message list |
| `labelListVisibility` | `"labelShow" \| "labelShowIfUnread" \| "labelHide"` | No | The visibility of the label in the label list |
| `color` | `object` | No | The color to assign to the label |
| `color.textColor` | `string` | No | The text color of the label as a hex string (#RRGGBB) |
| `color.backgroundColor` | `string` | No | The background color of the label as a hex string (#RRGGBB) |
| `labelId` | `string` | Yes | The ID of the label to update |


<details>
<summary><b>Response Schema</b></summary>

#### Records

| Field Name | Type | Description |
|------------|------|-------------|
| `id` | `string` |  |
| `name` | `string \| null` |  |
| `type` | `string \| null` |  |
| `messageListVisibility` | `string \| null` |  |
| `labelListVisibility` | `string \| null` |  |
| `messagesTotal` | `integer \| null` |  |
| `messagesUnread` | `integer \| null` |  |
| `threadsTotal` | `integer \| null` |  |
| `threadsUnread` | `integer \| null` |  |
| `color` | `object \| any` |  |


</details>

### Labels Delete

Deletes the specified label and removes it from any messages and threads

#### Python SDK

```python
await gmail.labels.delete(
    label_id="<str>"
)
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/integrations/connectors/{your_connector_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "labels",
    "action": "delete",
    "params": {
        "labelId": "<str>"
    }
}'
```


#### Parameters

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `labelId` | `string` | Yes | The ID of the label to delete |


## Drafts

### Drafts List

Lists the drafts in the user's mailbox

#### Python SDK

```python
await gmail.drafts.list()
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/integrations/connectors/{your_connector_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "drafts",
    "action": "list"
}'
```


#### Parameters

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `maxResults` | `integer` | No | Maximum number of drafts to return (1-500) |
| `pageToken` | `string` | No | Page token to retrieve a specific page of results |
| `q` | `string` | No | Gmail search query to filter drafts |
| `includeSpamTrash` | `boolean` | No | Include drafts from SPAM and TRASH in the results |


<details>
<summary><b>Response Schema</b></summary>

#### Records

| Field Name | Type | Description |
|------------|------|-------------|
| `id` | `string` |  |
| `message` | `object \| any` |  |


#### Meta

| Field Name | Type | Description |
|------------|------|-------------|
| `nextPageToken` | `string \| null` |  |
| `resultSizeEstimate` | `integer \| null` |  |

</details>

### Drafts Create

Creates a new draft with the specified message content

#### Python SDK

```python
await gmail.drafts.create(
    message={
        "raw": "<str>"
    }
)
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/integrations/connectors/{your_connector_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "drafts",
    "action": "create",
    "params": {
        "message": {
            "raw": "<str>"
        }
    }
}'
```


#### Parameters

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `message` | `object` | Yes | The draft message content |
| `message.raw` | `string` | Yes | The draft message in RFC 2822 format, base64url encoded |
| `message.threadId` | `string` | No | The thread ID for the draft (for threading in a conversation) |


<details>
<summary><b>Response Schema</b></summary>

#### Records

| Field Name | Type | Description |
|------------|------|-------------|
| `id` | `string` |  |
| `message` | `object \| any` |  |


</details>

### Drafts Get

Gets the specified draft including its message content

#### Python SDK

```python
await gmail.drafts.get(
    draft_id="<str>"
)
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/integrations/connectors/{your_connector_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "drafts",
    "action": "get",
    "params": {
        "draftId": "<str>"
    }
}'
```


#### Parameters

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `draftId` | `string` | Yes | The ID of the draft to retrieve |
| `format` | `"full" \| "metadata" \| "minimal" \| "raw"` | No | The format to return the draft message in (full, metadata, minimal, raw) |


<details>
<summary><b>Response Schema</b></summary>

#### Records

| Field Name | Type | Description |
|------------|------|-------------|
| `id` | `string` |  |
| `message` | `object \| any` |  |


</details>

### Drafts Update

Replaces a draft's content with the specified message content

#### Python SDK

```python
await gmail.drafts.update(
    message={
        "raw": "<str>"
    },
    draft_id="<str>"
)
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/integrations/connectors/{your_connector_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "drafts",
    "action": "update",
    "params": {
        "message": {
            "raw": "<str>"
        },
        "draftId": "<str>"
    }
}'
```


#### Parameters

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `message` | `object` | Yes | The draft message content |
| `message.raw` | `string` | Yes | The draft message in RFC 2822 format, base64url encoded |
| `message.threadId` | `string` | No | The thread ID for the draft (for threading in a conversation) |
| `draftId` | `string` | Yes | The ID of the draft to update |


<details>
<summary><b>Response Schema</b></summary>

#### Records

| Field Name | Type | Description |
|------------|------|-------------|
| `id` | `string` |  |
| `message` | `object \| any` |  |


</details>

### Drafts Delete

Immediately and permanently deletes the specified draft (does not move to trash)

#### Python SDK

```python
await gmail.drafts.delete(
    draft_id="<str>"
)
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/integrations/connectors/{your_connector_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "drafts",
    "action": "delete",
    "params": {
        "draftId": "<str>"
    }
}'
```


#### Parameters

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `draftId` | `string` | Yes | The ID of the draft to delete |


## Drafts Send

### Drafts Send Create

Sends the specified existing draft to its recipients

#### Python SDK

```python
await gmail.drafts_send.create(
    id="<str>"
)
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/integrations/connectors/{your_connector_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "drafts_send",
    "action": "create",
    "params": {
        "id": "<str>"
    }
}'
```


#### Parameters

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `id` | `string` | Yes | The ID of the draft to send |


<details>
<summary><b>Response Schema</b></summary>

#### Records

| Field Name | Type | Description |
|------------|------|-------------|
| `id` | `string` |  |
| `threadId` | `string \| null` |  |
| `labelIds` | `array \| null` |  |
| `snippet` | `string \| null` |  |
| `historyId` | `string \| null` |  |
| `internalDate` | `string \| null` |  |
| `sizeEstimate` | `integer \| null` |  |
| `raw` | `string \| null` |  |
| `payload` | `object \| any` |  |


</details>

## Threads

### Threads List

Lists the threads in the user's mailbox

#### Python SDK

```python
await gmail.threads.list()
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/integrations/connectors/{your_connector_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "threads",
    "action": "list"
}'
```


#### Parameters

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `maxResults` | `integer` | No | Maximum number of threads to return (1-500) |
| `pageToken` | `string` | No | Page token to retrieve a specific page of results |
| `q` | `string` | No | Gmail search query to filter threads |
| `labelIds` | `string` | No | Only return threads with labels matching all of the specified label IDs (comma-separated) |
| `includeSpamTrash` | `boolean` | No | Include threads from SPAM and TRASH in the results |


<details>
<summary><b>Response Schema</b></summary>

#### Records

| Field Name | Type | Description |
|------------|------|-------------|
| `id` | `string` |  |
| `snippet` | `string \| null` |  |
| `historyId` | `string \| null` |  |


#### Meta

| Field Name | Type | Description |
|------------|------|-------------|
| `nextPageToken` | `string \| null` |  |
| `resultSizeEstimate` | `integer \| null` |  |

</details>

### Threads Get

Gets the specified thread including all messages in the conversation

#### Python SDK

```python
await gmail.threads.get(
    thread_id="<str>"
)
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/integrations/connectors/{your_connector_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "threads",
    "action": "get",
    "params": {
        "threadId": "<str>"
    }
}'
```


#### Parameters

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `threadId` | `string` | Yes | The ID of the thread to retrieve |
| `format` | `"full" \| "metadata" \| "minimal"` | No | The format to return the messages in (full, metadata, minimal) |
| `metadataHeaders` | `string` | No | When format is METADATA, only include headers specified (comma-separated) |


<details>
<summary><b>Response Schema</b></summary>

#### Records

| Field Name | Type | Description |
|------------|------|-------------|
| `id` | `string` |  |
| `snippet` | `string \| null` |  |
| `historyId` | `string \| null` |  |
| `messages` | `array \| null` |  |
| `messages[].id` | `string` |  |
| `messages[].threadId` | `string \| null` |  |
| `messages[].labelIds` | `array \| null` |  |
| `messages[].snippet` | `string \| null` |  |
| `messages[].historyId` | `string \| null` |  |
| `messages[].internalDate` | `string \| null` |  |
| `messages[].sizeEstimate` | `integer \| null` |  |
| `messages[].raw` | `string \| null` |  |
| `messages[].payload` | `object \| any` |  |


</details>

## Messages Trash

### Messages Trash Create

Moves the specified message to the trash

#### Python SDK

```python
await gmail.messages_trash.create(
    message_id="<str>"
)
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/integrations/connectors/{your_connector_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "messages_trash",
    "action": "create",
    "params": {
        "messageId": "<str>"
    }
}'
```


#### Parameters

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `messageId` | `string` | Yes | The ID of the message to trash |


<details>
<summary><b>Response Schema</b></summary>

#### Records

| Field Name | Type | Description |
|------------|------|-------------|
| `id` | `string` |  |
| `threadId` | `string \| null` |  |
| `labelIds` | `array \| null` |  |
| `snippet` | `string \| null` |  |
| `historyId` | `string \| null` |  |
| `internalDate` | `string \| null` |  |
| `sizeEstimate` | `integer \| null` |  |
| `raw` | `string \| null` |  |
| `payload` | `object \| any` |  |


</details>

## Messages Untrash

### Messages Untrash Create

Removes the specified message from the trash

#### Python SDK

```python
await gmail.messages_untrash.create(
    message_id="<str>"
)
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/integrations/connectors/{your_connector_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "messages_untrash",
    "action": "create",
    "params": {
        "messageId": "<str>"
    }
}'
```


#### Parameters

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `messageId` | `string` | Yes | The ID of the message to untrash |


<details>
<summary><b>Response Schema</b></summary>

#### Records

| Field Name | Type | Description |
|------------|------|-------------|
| `id` | `string` |  |
| `threadId` | `string \| null` |  |
| `labelIds` | `array \| null` |  |
| `snippet` | `string \| null` |  |
| `historyId` | `string \| null` |  |
| `internalDate` | `string \| null` |  |
| `sizeEstimate` | `integer \| null` |  |
| `raw` | `string \| null` |  |
| `payload` | `object \| any` |  |


</details>

