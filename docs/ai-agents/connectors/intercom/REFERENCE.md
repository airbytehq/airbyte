# Intercom full reference

This is the full reference documentation for the Intercom agent connector.

## Supported entities and actions

The Intercom connector supports the following entities and actions.

| Entity | Actions |
|--------|---------|
| Contacts | [List](#contacts-list), [Get](#contacts-get), [Search](#contacts-search) |
| Conversations | [List](#conversations-list), [Get](#conversations-get), [Search](#conversations-search) |
| Companies | [List](#companies-list), [Get](#companies-get), [Search](#companies-search) |
| Teams | [List](#teams-list), [Get](#teams-get), [Search](#teams-search) |
| Admins | [List](#admins-list), [Get](#admins-get) |
| Tags | [List](#tags-list), [Get](#tags-get) |
| Segments | [List](#segments-list), [Get](#segments-get) |

## Contacts

### Contacts List

Returns a paginated list of contacts in the workspace

#### Python SDK

```python
await intercom.contacts.list()
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


#### Parameters

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `per_page` | `integer` | No | Number of contacts to return per page |
| `starting_after` | `string` | No | Cursor for pagination - get contacts after this ID |


<details>
<summary><b>Response Schema</b></summary>

#### Records

| Field Name | Type | Description |
|------------|------|-------------|
| `type` | `string \| null` |  |
| `id` | `string` |  |
| `workspace_id` | `string \| null` |  |
| `external_id` | `string \| null` |  |
| `role` | `string \| null` |  |
| `email` | `string \| null` |  |
| `phone` | `string \| null` |  |
| `name` | `string \| null` |  |
| `avatar` | `string \| null` |  |
| `owner_id` | `integer \| null` |  |
| `social_profiles` | `object \| any` |  |
| `has_hard_bounced` | `boolean \| null` |  |
| `marked_email_as_spam` | `boolean \| null` |  |
| `unsubscribed_from_emails` | `boolean \| null` |  |
| `created_at` | `integer \| null` |  |
| `updated_at` | `integer \| null` |  |
| `signed_up_at` | `integer \| null` |  |
| `last_seen_at` | `integer \| null` |  |
| `last_replied_at` | `integer \| null` |  |
| `last_contacted_at` | `integer \| null` |  |
| `last_email_opened_at` | `integer \| null` |  |
| `last_email_clicked_at` | `integer \| null` |  |
| `language_override` | `string \| null` |  |
| `browser` | `string \| null` |  |
| `browser_version` | `string \| null` |  |
| `browser_language` | `string \| null` |  |
| `os` | `string \| null` |  |
| `location` | `object \| any` |  |
| `android_app_name` | `string \| null` |  |
| `android_app_version` | `string \| null` |  |
| `android_device` | `string \| null` |  |
| `android_os_version` | `string \| null` |  |
| `android_sdk_version` | `string \| null` |  |
| `android_last_seen_at` | `integer \| null` |  |
| `ios_app_name` | `string \| null` |  |
| `ios_app_version` | `string \| null` |  |
| `ios_device` | `string \| null` |  |
| `ios_os_version` | `string \| null` |  |
| `ios_sdk_version` | `string \| null` |  |
| `ios_last_seen_at` | `integer \| null` |  |
| `custom_attributes` | `object \| null` |  |
| `tags` | `object \| any` |  |
| `notes` | `object \| any` |  |
| `companies` | `object \| any` |  |


#### Meta

| Field Name | Type | Description |
|------------|------|-------------|
| `next_page` | `string \| null` |  |

</details>

### Contacts Get

Get a single contact by ID

#### Python SDK

```python
await intercom.contacts.get(
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
| `id` | `string` | Yes | Contact ID |


<details>
<summary><b>Response Schema</b></summary>

#### Records

| Field Name | Type | Description |
|------------|------|-------------|
| `type` | `string \| null` |  |
| `id` | `string` |  |
| `workspace_id` | `string \| null` |  |
| `external_id` | `string \| null` |  |
| `role` | `string \| null` |  |
| `email` | `string \| null` |  |
| `phone` | `string \| null` |  |
| `name` | `string \| null` |  |
| `avatar` | `string \| null` |  |
| `owner_id` | `integer \| null` |  |
| `social_profiles` | `object \| any` |  |
| `has_hard_bounced` | `boolean \| null` |  |
| `marked_email_as_spam` | `boolean \| null` |  |
| `unsubscribed_from_emails` | `boolean \| null` |  |
| `created_at` | `integer \| null` |  |
| `updated_at` | `integer \| null` |  |
| `signed_up_at` | `integer \| null` |  |
| `last_seen_at` | `integer \| null` |  |
| `last_replied_at` | `integer \| null` |  |
| `last_contacted_at` | `integer \| null` |  |
| `last_email_opened_at` | `integer \| null` |  |
| `last_email_clicked_at` | `integer \| null` |  |
| `language_override` | `string \| null` |  |
| `browser` | `string \| null` |  |
| `browser_version` | `string \| null` |  |
| `browser_language` | `string \| null` |  |
| `os` | `string \| null` |  |
| `location` | `object \| any` |  |
| `android_app_name` | `string \| null` |  |
| `android_app_version` | `string \| null` |  |
| `android_device` | `string \| null` |  |
| `android_os_version` | `string \| null` |  |
| `android_sdk_version` | `string \| null` |  |
| `android_last_seen_at` | `integer \| null` |  |
| `ios_app_name` | `string \| null` |  |
| `ios_app_version` | `string \| null` |  |
| `ios_device` | `string \| null` |  |
| `ios_os_version` | `string \| null` |  |
| `ios_sdk_version` | `string \| null` |  |
| `ios_last_seen_at` | `integer \| null` |  |
| `custom_attributes` | `object \| null` |  |
| `tags` | `object \| any` |  |
| `notes` | `object \| any` |  |
| `companies` | `object \| any` |  |


</details>

### Contacts Search

Search and filter contacts records powered by Airbyte's data sync. This often provides additional fields and operators beyond what the API natively supports, making it easier to narrow down results before performing further operations. Only available in hosted mode.

#### Python SDK

```python
await intercom.contacts.search(
    query={"filter": {"eq": {"android_app_name": "<str>"}}}
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
        "query": {"filter": {"eq": {"android_app_name": "<str>"}}}
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
| `android_app_name` | `string` | The name of the Android app associated with the contact. |
| `android_app_version` | `string` | The version of the Android app associated with the contact. |
| `android_device` | `string` | The device used by the contact for Android. |
| `android_last_seen_at` | `string` | The date and time when the contact was last seen on Android. |
| `android_os_version` | `string` | The operating system version of the Android device. |
| `android_sdk_version` | `string` | The SDK version of the Android device. |
| `avatar` | `string` | URL pointing to the contact's avatar image. |
| `browser` | `string` | The browser used by the contact. |
| `browser_language` | `string` | The language preference set in the contact's browser. |
| `browser_version` | `string` | The version of the browser used by the contact. |
| `companies` | `object` | Companies associated with the contact. |
| `created_at` | `integer` | The date and time when the contact was created. |
| `custom_attributes` | `object` | Custom attributes defined for the contact. |
| `email` | `string` | The email address of the contact. |
| `external_id` | `string` | External identifier for the contact. |
| `has_hard_bounced` | `boolean` | Flag indicating if the contact has hard bounced. |
| `id` | `string` | The unique identifier of the contact. |
| `ios_app_name` | `string` | The name of the iOS app associated with the contact. |
| `ios_app_version` | `string` | The version of the iOS app associated with the contact. |
| `ios_device` | `string` | The device used by the contact for iOS. |
| `ios_last_seen_at` | `integer` | The date and time when the contact was last seen on iOS. |
| `ios_os_version` | `string` | The operating system version of the iOS device. |
| `ios_sdk_version` | `string` | The SDK version of the iOS device. |
| `language_override` | `string` | Language override set for the contact. |
| `last_contacted_at` | `integer` | The date and time when the contact was last contacted. |
| `last_email_clicked_at` | `integer` | The date and time when the contact last clicked an email. |
| `last_email_opened_at` | `integer` | The date and time when the contact last opened an email. |
| `last_replied_at` | `integer` | The date and time when the contact last replied. |
| `last_seen_at` | `integer` | The date and time when the contact was last seen overall. |
| `location` | `object` | Location details of the contact. |
| `marked_email_as_spam` | `boolean` | Flag indicating if the contact's email was marked as spam. |
| `name` | `string` | The name of the contact. |
| `notes` | `object` | Notes associated with the contact. |
| `opted_in_subscription_types` | `object` | Subscription types the contact opted into. |
| `opted_out_subscription_types` | `object` | Subscription types the contact opted out from. |
| `os` | `string` | Operating system of the contact's device. |
| `owner_id` | `integer` | The unique identifier of the contact's owner. |
| `phone` | `string` | The phone number of the contact. |
| `referrer` | `string` | Referrer information related to the contact. |
| `role` | `string` | Role or position of the contact. |
| `signed_up_at` | `integer` | The date and time when the contact signed up. |
| `sms_consent` | `boolean` | Consent status for SMS communication. |
| `social_profiles` | `object` | Social profiles associated with the contact. |
| `tags` | `object` | Tags associated with the contact. |
| `type` | `string` | Type of contact. |
| `unsubscribed_from_emails` | `boolean` | Flag indicating if the contact unsubscribed from emails. |
| `unsubscribed_from_sms` | `boolean` | Flag indicating if the contact unsubscribed from SMS. |
| `updated_at` | `integer` | The date and time when the contact was last updated. |
| `utm_campaign` | `string` | Campaign data from UTM parameters. |
| `utm_content` | `string` | Content data from UTM parameters. |
| `utm_medium` | `string` | Medium data from UTM parameters. |
| `utm_source` | `string` | Source data from UTM parameters. |
| `utm_term` | `string` | Term data from UTM parameters. |
| `workspace_id` | `string` | The unique identifier of the workspace associated with the contact. |

<details>
<summary><b>Response Schema</b></summary>

| Field Name | Type | Description |
|------------|------|-------------|
| `data` | `array` | List of matching records |
| `meta` | `object` | Pagination metadata |
| `meta.has_more` | `boolean` | Whether additional pages are available |
| `meta.cursor` | `string \| null` | Cursor for next page of results |
| `meta.took_ms` | `number \| null` | Query execution time in milliseconds |
| `data[].android_app_name` | `string` | The name of the Android app associated with the contact. |
| `data[].android_app_version` | `string` | The version of the Android app associated with the contact. |
| `data[].android_device` | `string` | The device used by the contact for Android. |
| `data[].android_last_seen_at` | `string` | The date and time when the contact was last seen on Android. |
| `data[].android_os_version` | `string` | The operating system version of the Android device. |
| `data[].android_sdk_version` | `string` | The SDK version of the Android device. |
| `data[].avatar` | `string` | URL pointing to the contact's avatar image. |
| `data[].browser` | `string` | The browser used by the contact. |
| `data[].browser_language` | `string` | The language preference set in the contact's browser. |
| `data[].browser_version` | `string` | The version of the browser used by the contact. |
| `data[].companies` | `object` | Companies associated with the contact. |
| `data[].created_at` | `integer` | The date and time when the contact was created. |
| `data[].custom_attributes` | `object` | Custom attributes defined for the contact. |
| `data[].email` | `string` | The email address of the contact. |
| `data[].external_id` | `string` | External identifier for the contact. |
| `data[].has_hard_bounced` | `boolean` | Flag indicating if the contact has hard bounced. |
| `data[].id` | `string` | The unique identifier of the contact. |
| `data[].ios_app_name` | `string` | The name of the iOS app associated with the contact. |
| `data[].ios_app_version` | `string` | The version of the iOS app associated with the contact. |
| `data[].ios_device` | `string` | The device used by the contact for iOS. |
| `data[].ios_last_seen_at` | `integer` | The date and time when the contact was last seen on iOS. |
| `data[].ios_os_version` | `string` | The operating system version of the iOS device. |
| `data[].ios_sdk_version` | `string` | The SDK version of the iOS device. |
| `data[].language_override` | `string` | Language override set for the contact. |
| `data[].last_contacted_at` | `integer` | The date and time when the contact was last contacted. |
| `data[].last_email_clicked_at` | `integer` | The date and time when the contact last clicked an email. |
| `data[].last_email_opened_at` | `integer` | The date and time when the contact last opened an email. |
| `data[].last_replied_at` | `integer` | The date and time when the contact last replied. |
| `data[].last_seen_at` | `integer` | The date and time when the contact was last seen overall. |
| `data[].location` | `object` | Location details of the contact. |
| `data[].marked_email_as_spam` | `boolean` | Flag indicating if the contact's email was marked as spam. |
| `data[].name` | `string` | The name of the contact. |
| `data[].notes` | `object` | Notes associated with the contact. |
| `data[].opted_in_subscription_types` | `object` | Subscription types the contact opted into. |
| `data[].opted_out_subscription_types` | `object` | Subscription types the contact opted out from. |
| `data[].os` | `string` | Operating system of the contact's device. |
| `data[].owner_id` | `integer` | The unique identifier of the contact's owner. |
| `data[].phone` | `string` | The phone number of the contact. |
| `data[].referrer` | `string` | Referrer information related to the contact. |
| `data[].role` | `string` | Role or position of the contact. |
| `data[].signed_up_at` | `integer` | The date and time when the contact signed up. |
| `data[].sms_consent` | `boolean` | Consent status for SMS communication. |
| `data[].social_profiles` | `object` | Social profiles associated with the contact. |
| `data[].tags` | `object` | Tags associated with the contact. |
| `data[].type` | `string` | Type of contact. |
| `data[].unsubscribed_from_emails` | `boolean` | Flag indicating if the contact unsubscribed from emails. |
| `data[].unsubscribed_from_sms` | `boolean` | Flag indicating if the contact unsubscribed from SMS. |
| `data[].updated_at` | `integer` | The date and time when the contact was last updated. |
| `data[].utm_campaign` | `string` | Campaign data from UTM parameters. |
| `data[].utm_content` | `string` | Content data from UTM parameters. |
| `data[].utm_medium` | `string` | Medium data from UTM parameters. |
| `data[].utm_source` | `string` | Source data from UTM parameters. |
| `data[].utm_term` | `string` | Term data from UTM parameters. |
| `data[].workspace_id` | `string` | The unique identifier of the workspace associated with the contact. |

</details>

## Conversations

### Conversations List

Returns a paginated list of conversations

#### Python SDK

```python
await intercom.conversations.list()
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/integrations/connectors/{your_connector_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "conversations",
    "action": "list"
}'
```


#### Parameters

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `per_page` | `integer` | No | Number of conversations to return per page |
| `starting_after` | `string` | No | Cursor for pagination |


<details>
<summary><b>Response Schema</b></summary>

#### Records

| Field Name | Type | Description |
|------------|------|-------------|
| `type` | `string \| null` |  |
| `id` | `string` |  |
| `title` | `string \| null` |  |
| `created_at` | `integer \| null` |  |
| `updated_at` | `integer \| null` |  |
| `waiting_since` | `integer \| null` |  |
| `snoozed_until` | `integer \| null` |  |
| `open` | `boolean \| null` |  |
| `state` | `string \| null` |  |
| `read` | `boolean \| null` |  |
| `priority` | `string \| null` |  |
| `admin_assignee_id` | `integer \| null` |  |
| `team_assignee_id` | `string \| null` |  |
| `tags` | `object \| any` |  |
| `conversation_rating` | `object \| any` |  |
| `source` | `object \| any` |  |
| `contacts` | `object \| any` |  |
| `teammates` | `object \| any` |  |
| `first_contact_reply` | `object \| any` |  |
| `sla_applied` | `object \| any` |  |
| `statistics` | `object \| any` |  |
| `conversation_parts` | `object \| any` |  |
| `custom_attributes` | `object \| null` |  |


#### Meta

| Field Name | Type | Description |
|------------|------|-------------|
| `next_page` | `string \| null` |  |

</details>

### Conversations Get

Get a single conversation by ID

#### Python SDK

```python
await intercom.conversations.get(
    id="<str>"
)
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/integrations/connectors/{your_connector_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "conversations",
    "action": "get",
    "params": {
        "id": "<str>"
    }
}'
```


#### Parameters

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `id` | `string` | Yes | Conversation ID |


<details>
<summary><b>Response Schema</b></summary>

#### Records

| Field Name | Type | Description |
|------------|------|-------------|
| `type` | `string \| null` |  |
| `id` | `string` |  |
| `title` | `string \| null` |  |
| `created_at` | `integer \| null` |  |
| `updated_at` | `integer \| null` |  |
| `waiting_since` | `integer \| null` |  |
| `snoozed_until` | `integer \| null` |  |
| `open` | `boolean \| null` |  |
| `state` | `string \| null` |  |
| `read` | `boolean \| null` |  |
| `priority` | `string \| null` |  |
| `admin_assignee_id` | `integer \| null` |  |
| `team_assignee_id` | `string \| null` |  |
| `tags` | `object \| any` |  |
| `conversation_rating` | `object \| any` |  |
| `source` | `object \| any` |  |
| `contacts` | `object \| any` |  |
| `teammates` | `object \| any` |  |
| `first_contact_reply` | `object \| any` |  |
| `sla_applied` | `object \| any` |  |
| `statistics` | `object \| any` |  |
| `conversation_parts` | `object \| any` |  |
| `custom_attributes` | `object \| null` |  |


</details>

### Conversations Search

Search and filter conversations records powered by Airbyte's data sync. This often provides additional fields and operators beyond what the API natively supports, making it easier to narrow down results before performing further operations. Only available in hosted mode.

#### Python SDK

```python
await intercom.conversations.search(
    query={"filter": {"eq": {"admin_assignee_id": 0}}}
)
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/integrations/connectors/{your_connector_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "conversations",
    "action": "search",
    "params": {
        "query": {"filter": {"eq": {"admin_assignee_id": 0}}}
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
| `admin_assignee_id` | `integer` | The ID of the administrator assigned to the conversation |
| `ai_agent` | `object` | Data related to AI Agent involvement in the conversation |
| `ai_agent_participated` | `boolean` | Indicates whether AI Agent participated in the conversation |
| `assignee` | `object` | The assigned user responsible for the conversation. |
| `contacts` | `object` | List of contacts involved in the conversation. |
| `conversation_message` | `object` | The main message content of the conversation. |
| `conversation_rating` | `object` | Ratings given to the conversation by the customer and teammate. |
| `created_at` | `integer` | The timestamp when the conversation was created |
| `custom_attributes` | `object` | Custom attributes associated with the conversation |
| `customer_first_reply` | `object` | Timestamp indicating when the customer first replied. |
| `customers` | `array` | List of customers involved in the conversation |
| `first_contact_reply` | `object` | Timestamp indicating when the first contact replied. |
| `id` | `string` | The unique ID of the conversation |
| `linked_objects` | `object` | Linked objects associated with the conversation |
| `open` | `boolean` | Indicates if the conversation is open or closed |
| `priority` | `string` | The priority level of the conversation |
| `read` | `boolean` | Indicates if the conversation has been read |
| `redacted` | `boolean` | Indicates if the conversation is redacted |
| `sent_at` | `integer` | The timestamp when the conversation was sent |
| `sla_applied` | `object` | Service Level Agreement details applied to the conversation. |
| `snoozed_until` | `integer` | Timestamp until the conversation is snoozed |
| `source` | `object` | Source details of the conversation. |
| `state` | `string` | The state of the conversation (e.g., new, in progress) |
| `statistics` | `object` | Statistics related to the conversation. |
| `tags` | `object` | Tags applied to the conversation. |
| `team_assignee_id` | `integer` | The ID of the team assigned to the conversation |
| `teammates` | `object` | List of teammates involved in the conversation. |
| `title` | `string` | The title of the conversation |
| `topics` | `object` | Topics associated with the conversation. |
| `type` | `string` | The type of the conversation |
| `updated_at` | `integer` | The timestamp when the conversation was last updated |
| `user` | `object` | The user related to the conversation. |
| `waiting_since` | `integer` | Timestamp since waiting for a response |

<details>
<summary><b>Response Schema</b></summary>

| Field Name | Type | Description |
|------------|------|-------------|
| `data` | `array` | List of matching records |
| `meta` | `object` | Pagination metadata |
| `meta.has_more` | `boolean` | Whether additional pages are available |
| `meta.cursor` | `string \| null` | Cursor for next page of results |
| `meta.took_ms` | `number \| null` | Query execution time in milliseconds |
| `data[].admin_assignee_id` | `integer` | The ID of the administrator assigned to the conversation |
| `data[].ai_agent` | `object` | Data related to AI Agent involvement in the conversation |
| `data[].ai_agent_participated` | `boolean` | Indicates whether AI Agent participated in the conversation |
| `data[].assignee` | `object` | The assigned user responsible for the conversation. |
| `data[].contacts` | `object` | List of contacts involved in the conversation. |
| `data[].conversation_message` | `object` | The main message content of the conversation. |
| `data[].conversation_rating` | `object` | Ratings given to the conversation by the customer and teammate. |
| `data[].created_at` | `integer` | The timestamp when the conversation was created |
| `data[].custom_attributes` | `object` | Custom attributes associated with the conversation |
| `data[].customer_first_reply` | `object` | Timestamp indicating when the customer first replied. |
| `data[].customers` | `array` | List of customers involved in the conversation |
| `data[].first_contact_reply` | `object` | Timestamp indicating when the first contact replied. |
| `data[].id` | `string` | The unique ID of the conversation |
| `data[].linked_objects` | `object` | Linked objects associated with the conversation |
| `data[].open` | `boolean` | Indicates if the conversation is open or closed |
| `data[].priority` | `string` | The priority level of the conversation |
| `data[].read` | `boolean` | Indicates if the conversation has been read |
| `data[].redacted` | `boolean` | Indicates if the conversation is redacted |
| `data[].sent_at` | `integer` | The timestamp when the conversation was sent |
| `data[].sla_applied` | `object` | Service Level Agreement details applied to the conversation. |
| `data[].snoozed_until` | `integer` | Timestamp until the conversation is snoozed |
| `data[].source` | `object` | Source details of the conversation. |
| `data[].state` | `string` | The state of the conversation (e.g., new, in progress) |
| `data[].statistics` | `object` | Statistics related to the conversation. |
| `data[].tags` | `object` | Tags applied to the conversation. |
| `data[].team_assignee_id` | `integer` | The ID of the team assigned to the conversation |
| `data[].teammates` | `object` | List of teammates involved in the conversation. |
| `data[].title` | `string` | The title of the conversation |
| `data[].topics` | `object` | Topics associated with the conversation. |
| `data[].type` | `string` | The type of the conversation |
| `data[].updated_at` | `integer` | The timestamp when the conversation was last updated |
| `data[].user` | `object` | The user related to the conversation. |
| `data[].waiting_since` | `integer` | Timestamp since waiting for a response |

</details>

## Companies

### Companies List

Returns a paginated list of companies

#### Python SDK

```python
await intercom.companies.list()
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/integrations/connectors/{your_connector_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "companies",
    "action": "list"
}'
```


#### Parameters

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `per_page` | `integer` | No | Number of companies to return per page |
| `starting_after` | `string` | No | Cursor for pagination |


<details>
<summary><b>Response Schema</b></summary>

#### Records

| Field Name | Type | Description |
|------------|------|-------------|
| `type` | `string \| null` |  |
| `id` | `string` |  |
| `name` | `string \| null` |  |
| `company_id` | `string \| null` |  |
| `plan` | `object \| any` |  |
| `size` | `integer \| null` |  |
| `industry` | `string \| null` |  |
| `website` | `string \| null` |  |
| `remote_created_at` | `integer \| null` |  |
| `created_at` | `integer \| null` |  |
| `updated_at` | `integer \| null` |  |
| `last_request_at` | `integer \| null` |  |
| `session_count` | `integer \| null` |  |
| `monthly_spend` | `number \| null` |  |
| `user_count` | `integer \| null` |  |
| `tags` | `object \| any` |  |
| `segments` | `object \| any` |  |
| `custom_attributes` | `object \| null` |  |


#### Meta

| Field Name | Type | Description |
|------------|------|-------------|
| `next_page` | `string \| null` |  |

</details>

### Companies Get

Get a single company by ID

#### Python SDK

```python
await intercom.companies.get(
    id="<str>"
)
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/integrations/connectors/{your_connector_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "companies",
    "action": "get",
    "params": {
        "id": "<str>"
    }
}'
```


#### Parameters

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `id` | `string` | Yes | Company ID |


<details>
<summary><b>Response Schema</b></summary>

#### Records

| Field Name | Type | Description |
|------------|------|-------------|
| `type` | `string \| null` |  |
| `id` | `string` |  |
| `name` | `string \| null` |  |
| `company_id` | `string \| null` |  |
| `plan` | `object \| any` |  |
| `size` | `integer \| null` |  |
| `industry` | `string \| null` |  |
| `website` | `string \| null` |  |
| `remote_created_at` | `integer \| null` |  |
| `created_at` | `integer \| null` |  |
| `updated_at` | `integer \| null` |  |
| `last_request_at` | `integer \| null` |  |
| `session_count` | `integer \| null` |  |
| `monthly_spend` | `number \| null` |  |
| `user_count` | `integer \| null` |  |
| `tags` | `object \| any` |  |
| `segments` | `object \| any` |  |
| `custom_attributes` | `object \| null` |  |


</details>

### Companies Search

Search and filter companies records powered by Airbyte's data sync. This often provides additional fields and operators beyond what the API natively supports, making it easier to narrow down results before performing further operations. Only available in hosted mode.

#### Python SDK

```python
await intercom.companies.search(
    query={"filter": {"eq": {"app_id": "<str>"}}}
)
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/integrations/connectors/{your_connector_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "companies",
    "action": "search",
    "params": {
        "query": {"filter": {"eq": {"app_id": "<str>"}}}
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
| `app_id` | `string` | The ID of the application associated with the company |
| `company_id` | `string` | The unique identifier of the company |
| `created_at` | `integer` | The date and time when the company was created |
| `custom_attributes` | `object` | Custom attributes specific to the company |
| `id` | `string` | The ID of the company |
| `industry` | `string` | The industry in which the company operates |
| `monthly_spend` | `number` | The monthly spend of the company |
| `name` | `string` | The name of the company |
| `plan` | `object` | Details of the company's subscription plan |
| `remote_created_at` | `integer` | The remote date and time when the company was created |
| `segments` | `object` | Segments associated with the company |
| `session_count` | `integer` | The number of sessions related to the company |
| `size` | `integer` | The size of the company |
| `tags` | `object` | Tags associated with the company |
| `type` | `string` | The type of the company |
| `updated_at` | `integer` | The date and time when the company was last updated |
| `user_count` | `integer` | The number of users associated with the company |
| `website` | `string` | The website of the company |

<details>
<summary><b>Response Schema</b></summary>

| Field Name | Type | Description |
|------------|------|-------------|
| `data` | `array` | List of matching records |
| `meta` | `object` | Pagination metadata |
| `meta.has_more` | `boolean` | Whether additional pages are available |
| `meta.cursor` | `string \| null` | Cursor for next page of results |
| `meta.took_ms` | `number \| null` | Query execution time in milliseconds |
| `data[].app_id` | `string` | The ID of the application associated with the company |
| `data[].company_id` | `string` | The unique identifier of the company |
| `data[].created_at` | `integer` | The date and time when the company was created |
| `data[].custom_attributes` | `object` | Custom attributes specific to the company |
| `data[].id` | `string` | The ID of the company |
| `data[].industry` | `string` | The industry in which the company operates |
| `data[].monthly_spend` | `number` | The monthly spend of the company |
| `data[].name` | `string` | The name of the company |
| `data[].plan` | `object` | Details of the company's subscription plan |
| `data[].remote_created_at` | `integer` | The remote date and time when the company was created |
| `data[].segments` | `object` | Segments associated with the company |
| `data[].session_count` | `integer` | The number of sessions related to the company |
| `data[].size` | `integer` | The size of the company |
| `data[].tags` | `object` | Tags associated with the company |
| `data[].type` | `string` | The type of the company |
| `data[].updated_at` | `integer` | The date and time when the company was last updated |
| `data[].user_count` | `integer` | The number of users associated with the company |
| `data[].website` | `string` | The website of the company |

</details>

## Teams

### Teams List

Returns a list of all teams in the workspace

#### Python SDK

```python
await intercom.teams.list()
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/integrations/connectors/{your_connector_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "teams",
    "action": "list"
}'
```



<details>
<summary><b>Response Schema</b></summary>

#### Records

| Field Name | Type | Description |
|------------|------|-------------|
| `type` | `string \| null` |  |
| `id` | `string` |  |
| `name` | `string \| null` |  |
| `admin_ids` | `array<integer>` |  |
| `admin_priority_level` | `object \| any` |  |


</details>

### Teams Get

Get a single team by ID

#### Python SDK

```python
await intercom.teams.get(
    id="<str>"
)
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/integrations/connectors/{your_connector_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "teams",
    "action": "get",
    "params": {
        "id": "<str>"
    }
}'
```


#### Parameters

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `id` | `string` | Yes | Team ID |


<details>
<summary><b>Response Schema</b></summary>

#### Records

| Field Name | Type | Description |
|------------|------|-------------|
| `type` | `string \| null` |  |
| `id` | `string` |  |
| `name` | `string \| null` |  |
| `admin_ids` | `array<integer>` |  |
| `admin_priority_level` | `object \| any` |  |


</details>

### Teams Search

Search and filter teams records powered by Airbyte's data sync. This often provides additional fields and operators beyond what the API natively supports, making it easier to narrow down results before performing further operations. Only available in hosted mode.

#### Python SDK

```python
await intercom.teams.search(
    query={"filter": {"eq": {"admin_ids": []}}}
)
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/integrations/connectors/{your_connector_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "teams",
    "action": "search",
    "params": {
        "query": {"filter": {"eq": {"admin_ids": []}}}
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
| `admin_ids` | `array` | Array of user IDs representing the admins of the team. |
| `id` | `string` | Unique identifier for the team. |
| `name` | `string` | Name of the team. |
| `type` | `string` | Type of team (e.g., 'internal', 'external'). |

<details>
<summary><b>Response Schema</b></summary>

| Field Name | Type | Description |
|------------|------|-------------|
| `data` | `array` | List of matching records |
| `meta` | `object` | Pagination metadata |
| `meta.has_more` | `boolean` | Whether additional pages are available |
| `meta.cursor` | `string \| null` | Cursor for next page of results |
| `meta.took_ms` | `number \| null` | Query execution time in milliseconds |
| `data[].admin_ids` | `array` | Array of user IDs representing the admins of the team. |
| `data[].id` | `string` | Unique identifier for the team. |
| `data[].name` | `string` | Name of the team. |
| `data[].type` | `string` | Type of team (e.g., 'internal', 'external'). |

</details>

## Admins

### Admins List

Returns a list of all admins in the workspace

#### Python SDK

```python
await intercom.admins.list()
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/integrations/connectors/{your_connector_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "admins",
    "action": "list"
}'
```



<details>
<summary><b>Response Schema</b></summary>

#### Records

| Field Name | Type | Description |
|------------|------|-------------|
| `type` | `string \| null` |  |
| `id` | `string` |  |
| `name` | `string \| null` |  |
| `email` | `string \| null` |  |
| `email_verified` | `boolean \| null` |  |
| `job_title` | `string \| null` |  |
| `away_mode_enabled` | `boolean \| null` |  |
| `away_mode_reassign` | `boolean \| null` |  |
| `has_inbox_seat` | `boolean \| null` |  |
| `team_ids` | `array<integer>` |  |
| `avatar` | `object \| any` |  |


</details>

### Admins Get

Get a single admin by ID

#### Python SDK

```python
await intercom.admins.get(
    id="<str>"
)
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/integrations/connectors/{your_connector_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "admins",
    "action": "get",
    "params": {
        "id": "<str>"
    }
}'
```


#### Parameters

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `id` | `string` | Yes | Admin ID |


<details>
<summary><b>Response Schema</b></summary>

#### Records

| Field Name | Type | Description |
|------------|------|-------------|
| `type` | `string \| null` |  |
| `id` | `string` |  |
| `name` | `string \| null` |  |
| `email` | `string \| null` |  |
| `email_verified` | `boolean \| null` |  |
| `job_title` | `string \| null` |  |
| `away_mode_enabled` | `boolean \| null` |  |
| `away_mode_reassign` | `boolean \| null` |  |
| `has_inbox_seat` | `boolean \| null` |  |
| `team_ids` | `array<integer>` |  |
| `avatar` | `object \| any` |  |


</details>

## Tags

### Tags List

Returns a list of all tags in the workspace

#### Python SDK

```python
await intercom.tags.list()
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/integrations/connectors/{your_connector_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "tags",
    "action": "list"
}'
```



<details>
<summary><b>Response Schema</b></summary>

#### Records

| Field Name | Type | Description |
|------------|------|-------------|
| `type` | `string \| null` |  |
| `id` | `string` |  |
| `name` | `string \| null` |  |
| `applied_at` | `integer \| null` |  |
| `applied_by` | `object \| any` |  |


</details>

### Tags Get

Get a single tag by ID

#### Python SDK

```python
await intercom.tags.get(
    id="<str>"
)
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/integrations/connectors/{your_connector_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "tags",
    "action": "get",
    "params": {
        "id": "<str>"
    }
}'
```


#### Parameters

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `id` | `string` | Yes | Tag ID |


<details>
<summary><b>Response Schema</b></summary>

#### Records

| Field Name | Type | Description |
|------------|------|-------------|
| `type` | `string \| null` |  |
| `id` | `string` |  |
| `name` | `string \| null` |  |
| `applied_at` | `integer \| null` |  |
| `applied_by` | `object \| any` |  |


</details>

## Segments

### Segments List

Returns a list of all segments in the workspace

#### Python SDK

```python
await intercom.segments.list()
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


#### Parameters

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `include_count` | `boolean` | No | Include count of contacts in each segment |


<details>
<summary><b>Response Schema</b></summary>

#### Records

| Field Name | Type | Description |
|------------|------|-------------|
| `type` | `string \| null` |  |
| `id` | `string` |  |
| `name` | `string \| null` |  |
| `created_at` | `integer \| null` |  |
| `updated_at` | `integer \| null` |  |
| `person_type` | `string \| null` |  |
| `count` | `integer \| null` |  |


</details>

### Segments Get

Get a single segment by ID

#### Python SDK

```python
await intercom.segments.get(
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


<details>
<summary><b>Response Schema</b></summary>

#### Records

| Field Name | Type | Description |
|------------|------|-------------|
| `type` | `string \| null` |  |
| `id` | `string` |  |
| `name` | `string \| null` |  |
| `created_at` | `integer \| null` |  |
| `updated_at` | `integer \| null` |  |
| `person_type` | `string \| null` |  |
| `count` | `integer \| null` |  |


</details>

