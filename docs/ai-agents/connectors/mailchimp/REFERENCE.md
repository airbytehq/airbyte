# Mailchimp full reference

This is the full reference documentation for the Mailchimp agent connector.

## Supported entities and actions

The Mailchimp connector supports the following entities and actions.

| Entity | Actions |
|--------|---------|
| Campaigns | [List](#campaigns-list), [Get](#campaigns-get), [Search](#campaigns-search) |
| Lists | [List](#lists-list), [Get](#lists-get), [Search](#lists-search) |
| List Members | [List](#list-members-list), [Get](#list-members-get) |
| Reports | [List](#reports-list), [Get](#reports-get), [Search](#reports-search) |
| Email Activity | [List](#email-activity-list), [Search](#email-activity-search) |
| Automations | [List](#automations-list) |
| Tags | [List](#tags-list) |
| Interest Categories | [List](#interest-categories-list), [Get](#interest-categories-get) |
| Interests | [List](#interests-list), [Get](#interests-get) |
| Segments | [List](#segments-list), [Get](#segments-get) |
| Segment Members | [List](#segment-members-list) |
| Unsubscribes | [List](#unsubscribes-list) |

## Campaigns

### Campaigns List

Get all campaigns in an account

#### Python SDK

```python
await mailchimp.campaigns.list()
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/connectors/sources/{your_source_id}/execute' \
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

#### Records

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


#### Meta

| Field Name | Type | Description |
|------------|------|-------------|
| `total_items` | `integer` |  |

</details>

### Campaigns Get

Get information about a specific campaign

#### Python SDK

```python
await mailchimp.campaigns.get(
    campaign_id="<str>"
)
```

#### API

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


#### Parameters

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `campaign_id` | `string` | Yes | The unique id for the campaign |


<details>
<summary><b>Response Schema</b></summary>

#### Records

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

### Campaigns Search

Search and filter campaigns records powered by Airbyte's data sync. This often provides additional fields and operators beyond what the API natively supports, making it easier to narrow down results before performing further operations. Only available in hosted mode.

#### Python SDK

```python
await mailchimp.campaigns.search(
    query={"filter": {"eq": {"ab_split_opts": {}}}}
)
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/connectors/sources/{your_source_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "campaigns",
    "action": "search",
    "params": {
        "query": {"filter": {"eq": {"ab_split_opts": {}}}}
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
| `ab_split_opts` | `object` | [A/B Testing](https://mailchimp.com/help/about-ab-testing-campaigns/) options for a campaign. |
| `archive_url` | `string` | The link to the campaign's archive version in ISO 8601 format. |
| `content_type` | `string` | How the campaign's content is put together. |
| `create_time` | `string` | The date and time the campaign was created in ISO 8601 format. |
| `delivery_status` | `object` | Updates on campaigns in the process of sending. |
| `emails_sent` | `integer` | The total number of emails sent for this campaign. |
| `id` | `string` | A string that uniquely identifies this campaign. |
| `long_archive_url` | `string` | The original link to the campaign's archive version. |
| `needs_block_refresh` | `boolean` | Determines if the campaign needs its blocks refreshed by opening the web-based campaign editor. D... |
| `parent_campaign_id` | `string` | If this campaign is the child of another campaign, this identifies the parent campaign. For Examp... |
| `recipients` | `object` | List settings for the campaign. |
| `report_summary` | `object` | For sent campaigns, a summary of opens, clicks, and e-commerce data. |
| `resendable` | `boolean` | Determines if the campaign qualifies to be resent to non-openers. |
| `rss_opts` | `object` | [RSS](https://mailchimp.com/help/share-your-blog-posts-with-mailchimp/) options for a campaign. |
| `send_time` | `string` | The date and time a campaign was sent. |
| `settings` | `object` | The settings for your campaign, including subject, from name, reply-to address, and more. |
| `social_card` | `object` | The preview for the campaign, rendered by social networks like Facebook and Twitter. [Learn more]... |
| `status` | `string` | The current status of the campaign. |
| `tracking` | `object` | The tracking options for a campaign. |
| `type` | `string` | There are four types of [campaigns](https://mailchimp.com/help/getting-started-with-campaigns/) y... |
| `variate_settings` | `object` | The settings specific to A/B test campaigns. |
| `web_id` | `integer` | The ID used in the Mailchimp web application. View this campaign in your Mailchimp account at `ht... |

<details>
<summary><b>Response Schema</b></summary>

| Field Name | Type | Description |
|------------|------|-------------|
| `hits` | `array` | List of matching records |
| `hits[].id` | `string` | Record identifier |
| `hits[].score` | `number` | Relevance score |
| `hits[].data` | `object` | Record data containing the searchable fields listed above |
| `hits[].data.ab_split_opts` | `object` | [A/B Testing](https://mailchimp.com/help/about-ab-testing-campaigns/) options for a campaign. |
| `hits[].data.archive_url` | `string` | The link to the campaign's archive version in ISO 8601 format. |
| `hits[].data.content_type` | `string` | How the campaign's content is put together. |
| `hits[].data.create_time` | `string` | The date and time the campaign was created in ISO 8601 format. |
| `hits[].data.delivery_status` | `object` | Updates on campaigns in the process of sending. |
| `hits[].data.emails_sent` | `integer` | The total number of emails sent for this campaign. |
| `hits[].data.id` | `string` | A string that uniquely identifies this campaign. |
| `hits[].data.long_archive_url` | `string` | The original link to the campaign's archive version. |
| `hits[].data.needs_block_refresh` | `boolean` | Determines if the campaign needs its blocks refreshed by opening the web-based campaign editor. D... |
| `hits[].data.parent_campaign_id` | `string` | If this campaign is the child of another campaign, this identifies the parent campaign. For Examp... |
| `hits[].data.recipients` | `object` | List settings for the campaign. |
| `hits[].data.report_summary` | `object` | For sent campaigns, a summary of opens, clicks, and e-commerce data. |
| `hits[].data.resendable` | `boolean` | Determines if the campaign qualifies to be resent to non-openers. |
| `hits[].data.rss_opts` | `object` | [RSS](https://mailchimp.com/help/share-your-blog-posts-with-mailchimp/) options for a campaign. |
| `hits[].data.send_time` | `string` | The date and time a campaign was sent. |
| `hits[].data.settings` | `object` | The settings for your campaign, including subject, from name, reply-to address, and more. |
| `hits[].data.social_card` | `object` | The preview for the campaign, rendered by social networks like Facebook and Twitter. [Learn more]... |
| `hits[].data.status` | `string` | The current status of the campaign. |
| `hits[].data.tracking` | `object` | The tracking options for a campaign. |
| `hits[].data.type` | `string` | There are four types of [campaigns](https://mailchimp.com/help/getting-started-with-campaigns/) y... |
| `hits[].data.variate_settings` | `object` | The settings specific to A/B test campaigns. |
| `hits[].data.web_id` | `integer` | The ID used in the Mailchimp web application. View this campaign in your Mailchimp account at `ht... |
| `next_cursor` | `string \| null` | Cursor for next page of results |
| `took_ms` | `number` | Query execution time in milliseconds |

</details>

## Lists

### Lists List

Get information about all lists in the account

#### Python SDK

```python
await mailchimp.lists.list()
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/connectors/sources/{your_source_id}/execute' \
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

#### Records

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


#### Meta

| Field Name | Type | Description |
|------------|------|-------------|
| `total_items` | `integer` |  |

</details>

### Lists Get

Get information about a specific list in your Mailchimp account

#### Python SDK

```python
await mailchimp.lists.get(
    list_id="<str>"
)
```

#### API

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


#### Parameters

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `list_id` | `string` | Yes | The unique ID for the list |


<details>
<summary><b>Response Schema</b></summary>

#### Records

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

### Lists Search

Search and filter lists records powered by Airbyte's data sync. This often provides additional fields and operators beyond what the API natively supports, making it easier to narrow down results before performing further operations. Only available in hosted mode.

#### Python SDK

```python
await mailchimp.lists.search(
    query={"filter": {"eq": {"beamer_address": "<str>"}}}
)
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/connectors/sources/{your_source_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "lists",
    "action": "search",
    "params": {
        "query": {"filter": {"eq": {"beamer_address": "<str>"}}}
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
| `beamer_address` | `string` | The list's Email Beamer address. |
| `campaign_defaults` | `object` | Default values for campaigns created for this list. |
| `contact` | `object` | Contact information displayed in campaign footers to comply with international spam laws. |
| `date_created` | `string` | The date and time that this list was created in ISO 8601 format. |
| `double_optin` | `boolean` | Whether or not to require the subscriber to confirm subscription via email. |
| `email_type_option` | `boolean` | Whether the list supports multiple formats for emails. When set to `true`, subscribers can choose... |
| `has_welcome` | `boolean` | Whether or not this list has a welcome automation connected. |
| `id` | `string` | A string that uniquely identifies this list. |
| `list_rating` | `integer` | An auto-generated activity score for the list (0-5). |
| `marketing_permissions` | `boolean` | Whether or not the list has marketing permissions (eg. GDPR) enabled. |
| `modules` | `array` | Any list-specific modules installed for this list. |
| `name` | `string` | The name of the list. |
| `notify_on_subscribe` | `string` | The email address to send subscribe notifications to. |
| `notify_on_unsubscribe` | `string` | The email address to send unsubscribe notifications to. |
| `permission_reminder` | `string` | The permission reminder for the list. |
| `stats` | `object` | Stats for the list. Many of these are cached for at least five minutes. |
| `subscribe_url_long` | `string` | The full version of this list's subscribe form (host will vary). |
| `subscribe_url_short` | `string` | Our EepURL shortened version of this list's subscribe form. |
| `use_archive_bar` | `boolean` | Whether campaigns for this list use the Archive Bar in archives by default. |
| `visibility` | `string` | Whether this list is public or private. |
| `web_id` | `integer` | The ID used in the Mailchimp web application. View this list in your Mailchimp account at `https:... |

<details>
<summary><b>Response Schema</b></summary>

| Field Name | Type | Description |
|------------|------|-------------|
| `hits` | `array` | List of matching records |
| `hits[].id` | `string` | Record identifier |
| `hits[].score` | `number` | Relevance score |
| `hits[].data` | `object` | Record data containing the searchable fields listed above |
| `hits[].data.beamer_address` | `string` | The list's Email Beamer address. |
| `hits[].data.campaign_defaults` | `object` | Default values for campaigns created for this list. |
| `hits[].data.contact` | `object` | Contact information displayed in campaign footers to comply with international spam laws. |
| `hits[].data.date_created` | `string` | The date and time that this list was created in ISO 8601 format. |
| `hits[].data.double_optin` | `boolean` | Whether or not to require the subscriber to confirm subscription via email. |
| `hits[].data.email_type_option` | `boolean` | Whether the list supports multiple formats for emails. When set to `true`, subscribers can choose... |
| `hits[].data.has_welcome` | `boolean` | Whether or not this list has a welcome automation connected. |
| `hits[].data.id` | `string` | A string that uniquely identifies this list. |
| `hits[].data.list_rating` | `integer` | An auto-generated activity score for the list (0-5). |
| `hits[].data.marketing_permissions` | `boolean` | Whether or not the list has marketing permissions (eg. GDPR) enabled. |
| `hits[].data.modules` | `array` | Any list-specific modules installed for this list. |
| `hits[].data.name` | `string` | The name of the list. |
| `hits[].data.notify_on_subscribe` | `string` | The email address to send subscribe notifications to. |
| `hits[].data.notify_on_unsubscribe` | `string` | The email address to send unsubscribe notifications to. |
| `hits[].data.permission_reminder` | `string` | The permission reminder for the list. |
| `hits[].data.stats` | `object` | Stats for the list. Many of these are cached for at least five minutes. |
| `hits[].data.subscribe_url_long` | `string` | The full version of this list's subscribe form (host will vary). |
| `hits[].data.subscribe_url_short` | `string` | Our EepURL shortened version of this list's subscribe form. |
| `hits[].data.use_archive_bar` | `boolean` | Whether campaigns for this list use the Archive Bar in archives by default. |
| `hits[].data.visibility` | `string` | Whether this list is public or private. |
| `hits[].data.web_id` | `integer` | The ID used in the Mailchimp web application. View this list in your Mailchimp account at `https:... |
| `next_cursor` | `string \| null` | Cursor for next page of results |
| `took_ms` | `number` | Query execution time in milliseconds |

</details>

## List Members

### List Members List

Get information about members in a specific Mailchimp list

#### Python SDK

```python
await mailchimp.list_members.list(
    list_id="<str>"
)
```

#### API

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


#### Parameters

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

#### Records

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


#### Meta

| Field Name | Type | Description |
|------------|------|-------------|
| `total_items` | `integer` |  |

</details>

### List Members Get

Get information about a specific list member

#### Python SDK

```python
await mailchimp.list_members.get(
    list_id="<str>",
    subscriber_hash="<str>"
)
```

#### API

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


#### Parameters

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `list_id` | `string` | Yes | The unique ID for the list |
| `subscriber_hash` | `string` | Yes | The MD5 hash of the lowercase version of the list member's email address |


<details>
<summary><b>Response Schema</b></summary>

#### Records

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

## Reports

### Reports List

Get campaign reports

#### Python SDK

```python
await mailchimp.reports.list()
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/connectors/sources/{your_source_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "reports",
    "action": "list"
}'
```


#### Parameters

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `count` | `integer` | No | The number of records to return |
| `offset` | `integer` | No | Used for pagination |
| `type` | `"regular" \| "plaintext" \| "absplit" \| "rss" \| "variate"` | No | The campaign type |
| `before_send_time` | `string` | No | Restrict the response to campaigns sent before the set time |
| `since_send_time` | `string` | No | Restrict the response to campaigns sent after the set time |


<details>
<summary><b>Response Schema</b></summary>

#### Records

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


#### Meta

| Field Name | Type | Description |
|------------|------|-------------|
| `total_items` | `integer` |  |

</details>

### Reports Get

Get report details for a specific sent campaign

#### Python SDK

```python
await mailchimp.reports.get(
    campaign_id="<str>"
)
```

#### API

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


#### Parameters

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `campaign_id` | `string` | Yes | The unique id for the campaign |


<details>
<summary><b>Response Schema</b></summary>

#### Records

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

### Reports Search

Search and filter reports records powered by Airbyte's data sync. This often provides additional fields and operators beyond what the API natively supports, making it easier to narrow down results before performing further operations. Only available in hosted mode.

#### Python SDK

```python
await mailchimp.reports.search(
    query={"filter": {"eq": {"ab_split": {}}}}
)
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/connectors/sources/{your_source_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "reports",
    "action": "search",
    "params": {
        "query": {"filter": {"eq": {"ab_split": {}}}}
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
| `ab_split` | `object` | General stats about different groups of an A/B Split campaign. Does not return information about ... |
| `abuse_reports` | `integer` | The number of abuse reports generated for this campaign. |
| `bounces` | `object` | An object describing the bounce summary for the campaign. |
| `campaign_title` | `string` | The title of the campaign. |
| `clicks` | `object` | An object describing the click activity for the campaign. |
| `delivery_status` | `object` | Updates on campaigns in the process of sending. |
| `ecommerce` | `object` | E-Commerce stats for a campaign. |
| `emails_sent` | `integer` | The total number of emails sent for this campaign. |
| `facebook_likes` | `object` | An object describing campaign engagement on Facebook. |
| `forwards` | `object` | An object describing the forwards and forward activity for the campaign. |
| `id` | `string` | A string that uniquely identifies this campaign. |
| `industry_stats` | `object` | The average campaign statistics for your industry. |
| `list_id` | `string` | The unique list id. |
| `list_is_active` | `boolean` | The status of the list used, namely if it's deleted or disabled. |
| `list_name` | `string` | The name of the list. |
| `list_stats` | `object` | The average campaign statistics for your list. This won't be present if we haven't calculated i... |
| `opens` | `object` | An object describing the open activity for the campaign. |
| `preview_text` | `string` | The preview text for the campaign. |
| `rss_last_send` | `string` | For RSS campaigns, the date and time of the last send in ISO 8601 format. |
| `send_time` | `string` | The date and time a campaign was sent in ISO 8601 format. |
| `share_report` | `object` | The url and password for the VIP report. |
| `subject_line` | `string` | The subject line for the campaign. |
| `timeseries` | `array` | An hourly breakdown of the performance of the campaign over the first 24 hours. |
| `timewarp` | `array` | An hourly breakdown of sends, opens, and clicks if a campaign is sent using timewarp. |
| `type` | `string` | The type of campaign (regular, plain-text, ab_split, rss, automation, variate, or auto). |
| `unsubscribed` | `integer` | The total number of unsubscribed members for this campaign. |

<details>
<summary><b>Response Schema</b></summary>

| Field Name | Type | Description |
|------------|------|-------------|
| `hits` | `array` | List of matching records |
| `hits[].id` | `string` | Record identifier |
| `hits[].score` | `number` | Relevance score |
| `hits[].data` | `object` | Record data containing the searchable fields listed above |
| `hits[].data.ab_split` | `object` | General stats about different groups of an A/B Split campaign. Does not return information about ... |
| `hits[].data.abuse_reports` | `integer` | The number of abuse reports generated for this campaign. |
| `hits[].data.bounces` | `object` | An object describing the bounce summary for the campaign. |
| `hits[].data.campaign_title` | `string` | The title of the campaign. |
| `hits[].data.clicks` | `object` | An object describing the click activity for the campaign. |
| `hits[].data.delivery_status` | `object` | Updates on campaigns in the process of sending. |
| `hits[].data.ecommerce` | `object` | E-Commerce stats for a campaign. |
| `hits[].data.emails_sent` | `integer` | The total number of emails sent for this campaign. |
| `hits[].data.facebook_likes` | `object` | An object describing campaign engagement on Facebook. |
| `hits[].data.forwards` | `object` | An object describing the forwards and forward activity for the campaign. |
| `hits[].data.id` | `string` | A string that uniquely identifies this campaign. |
| `hits[].data.industry_stats` | `object` | The average campaign statistics for your industry. |
| `hits[].data.list_id` | `string` | The unique list id. |
| `hits[].data.list_is_active` | `boolean` | The status of the list used, namely if it's deleted or disabled. |
| `hits[].data.list_name` | `string` | The name of the list. |
| `hits[].data.list_stats` | `object` | The average campaign statistics for your list. This won't be present if we haven't calculated i... |
| `hits[].data.opens` | `object` | An object describing the open activity for the campaign. |
| `hits[].data.preview_text` | `string` | The preview text for the campaign. |
| `hits[].data.rss_last_send` | `string` | For RSS campaigns, the date and time of the last send in ISO 8601 format. |
| `hits[].data.send_time` | `string` | The date and time a campaign was sent in ISO 8601 format. |
| `hits[].data.share_report` | `object` | The url and password for the VIP report. |
| `hits[].data.subject_line` | `string` | The subject line for the campaign. |
| `hits[].data.timeseries` | `array` | An hourly breakdown of the performance of the campaign over the first 24 hours. |
| `hits[].data.timewarp` | `array` | An hourly breakdown of sends, opens, and clicks if a campaign is sent using timewarp. |
| `hits[].data.type` | `string` | The type of campaign (regular, plain-text, ab_split, rss, automation, variate, or auto). |
| `hits[].data.unsubscribed` | `integer` | The total number of unsubscribed members for this campaign. |
| `next_cursor` | `string \| null` | Cursor for next page of results |
| `took_ms` | `number` | Query execution time in milliseconds |

</details>

## Email Activity

### Email Activity List

Get a list of member's subscriber activity in a specific campaign

#### Python SDK

```python
await mailchimp.email_activity.list(
    campaign_id="<str>"
)
```

#### API

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


#### Parameters

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `campaign_id` | `string` | Yes | The unique id for the campaign |
| `count` | `integer` | No | The number of records to return |
| `offset` | `integer` | No | Used for pagination |
| `since` | `string` | No | Restrict results to email activity events that occur after a specific time |


<details>
<summary><b>Response Schema</b></summary>

#### Records

| Field Name | Type | Description |
|------------|------|-------------|
| `campaign_id` | `string \| null` |  |
| `list_id` | `string \| null` |  |
| `list_is_active` | `boolean \| null` |  |
| `email_id` | `string \| null` |  |
| `email_address` | `string \| null` |  |
| `activity` | `array \| null` |  |


#### Meta

| Field Name | Type | Description |
|------------|------|-------------|
| `total_items` | `integer` |  |

</details>

### Email Activity Search

Search and filter email activity records powered by Airbyte's data sync. This often provides additional fields and operators beyond what the API natively supports, making it easier to narrow down results before performing further operations. Only available in hosted mode.

#### Python SDK

```python
await mailchimp.email_activity.search(
    query={"filter": {"eq": {"action": "<str>"}}}
)
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/connectors/sources/{your_source_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "email_activity",
    "action": "search",
    "params": {
        "query": {"filter": {"eq": {"action": "<str>"}}}
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
| `action` | `string` | One of the following actions: 'open', 'click', or 'bounce' |
| `campaign_id` | `string` | The unique id for the campaign. |
| `email_address` | `string` | Email address for a subscriber. |
| `email_id` | `string` | The MD5 hash of the lowercase version of the list member's email address. |
| `ip` | `string` | The IP address recorded for the action. |
| `list_id` | `string` | The unique id for the list. |
| `list_is_active` | `boolean` | The status of the list used, namely if it's deleted or disabled. |
| `timestamp` | `string` | The date and time recorded for the action in ISO 8601 format. |
| `type` | `string` | If the action is a 'bounce', the type of bounce received: 'hard', 'soft'. |
| `url` | `string` | If the action is a 'click', the URL on which the member clicked. |

<details>
<summary><b>Response Schema</b></summary>

| Field Name | Type | Description |
|------------|------|-------------|
| `hits` | `array` | List of matching records |
| `hits[].id` | `string` | Record identifier |
| `hits[].score` | `number` | Relevance score |
| `hits[].data` | `object` | Record data containing the searchable fields listed above |
| `hits[].data.action` | `string` | One of the following actions: 'open', 'click', or 'bounce' |
| `hits[].data.campaign_id` | `string` | The unique id for the campaign. |
| `hits[].data.email_address` | `string` | Email address for a subscriber. |
| `hits[].data.email_id` | `string` | The MD5 hash of the lowercase version of the list member's email address. |
| `hits[].data.ip` | `string` | The IP address recorded for the action. |
| `hits[].data.list_id` | `string` | The unique id for the list. |
| `hits[].data.list_is_active` | `boolean` | The status of the list used, namely if it's deleted or disabled. |
| `hits[].data.timestamp` | `string` | The date and time recorded for the action in ISO 8601 format. |
| `hits[].data.type` | `string` | If the action is a 'bounce', the type of bounce received: 'hard', 'soft'. |
| `hits[].data.url` | `string` | If the action is a 'click', the URL on which the member clicked. |
| `next_cursor` | `string \| null` | Cursor for next page of results |
| `took_ms` | `number` | Query execution time in milliseconds |

</details>

## Automations

### Automations List

Get a summary of an account's classic automations

#### Python SDK

```python
await mailchimp.automations.list()
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/connectors/sources/{your_source_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "automations",
    "action": "list"
}'
```


#### Parameters

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

#### Records

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


#### Meta

| Field Name | Type | Description |
|------------|------|-------------|
| `total_items` | `integer` |  |

</details>

## Tags

### Tags List

Search for tags on a list by name

#### Python SDK

```python
await mailchimp.tags.list(
    list_id="<str>"
)
```

#### API

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


#### Parameters

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `list_id` | `string` | Yes | The unique ID for the list |
| `name` | `string` | No | The search query used to filter tags |


<details>
<summary><b>Response Schema</b></summary>

#### Records

| Field Name | Type | Description |
|------------|------|-------------|
| `id` | `integer` |  |
| `name` | `string \| null` |  |


#### Meta

| Field Name | Type | Description |
|------------|------|-------------|
| `total_items` | `integer` |  |

</details>

## Interest Categories

### Interest Categories List

Get information about a list's interest categories

#### Python SDK

```python
await mailchimp.interest_categories.list(
    list_id="<str>"
)
```

#### API

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


#### Parameters

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `list_id` | `string` | Yes | The unique ID for the list |
| `count` | `integer` | No | The number of records to return |
| `offset` | `integer` | No | Used for pagination |


<details>
<summary><b>Response Schema</b></summary>

#### Records

| Field Name | Type | Description |
|------------|------|-------------|
| `list_id` | `string \| null` |  |
| `id` | `string` |  |
| `title` | `string \| null` |  |
| `display_order` | `integer \| null` |  |
| `type` | `string \| null` |  |


#### Meta

| Field Name | Type | Description |
|------------|------|-------------|
| `total_items` | `integer` |  |

</details>

### Interest Categories Get

Get information about a specific interest category

#### Python SDK

```python
await mailchimp.interest_categories.get(
    list_id="<str>",
    interest_category_id="<str>"
)
```

#### API

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


#### Parameters

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `list_id` | `string` | Yes | The unique ID for the list |
| `interest_category_id` | `string` | Yes | The unique ID for the interest category |


<details>
<summary><b>Response Schema</b></summary>

#### Records

| Field Name | Type | Description |
|------------|------|-------------|
| `list_id` | `string \| null` |  |
| `id` | `string` |  |
| `title` | `string \| null` |  |
| `display_order` | `integer \| null` |  |
| `type` | `string \| null` |  |


</details>

## Interests

### Interests List

Get a list of this category's interests

#### Python SDK

```python
await mailchimp.interests.list(
    list_id="<str>",
    interest_category_id="<str>"
)
```

#### API

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


#### Parameters

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `list_id` | `string` | Yes | The unique ID for the list |
| `interest_category_id` | `string` | Yes | The unique ID for the interest category |
| `count` | `integer` | No | The number of records to return |
| `offset` | `integer` | No | Used for pagination |


<details>
<summary><b>Response Schema</b></summary>

#### Records

| Field Name | Type | Description |
|------------|------|-------------|
| `category_id` | `string \| null` |  |
| `list_id` | `string \| null` |  |
| `id` | `string` |  |
| `name` | `string \| null` |  |
| `subscriber_count` | `string \| null` |  |
| `display_order` | `integer \| null` |  |


#### Meta

| Field Name | Type | Description |
|------------|------|-------------|
| `total_items` | `integer` |  |

</details>

### Interests Get

Get interests or group names for a specific category

#### Python SDK

```python
await mailchimp.interests.get(
    list_id="<str>",
    interest_category_id="<str>",
    interest_id="<str>"
)
```

#### API

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


#### Parameters

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `list_id` | `string` | Yes | The unique ID for the list |
| `interest_category_id` | `string` | Yes | The unique ID for the interest category |
| `interest_id` | `string` | Yes | The specific interest or group name |


<details>
<summary><b>Response Schema</b></summary>

#### Records

| Field Name | Type | Description |
|------------|------|-------------|
| `category_id` | `string \| null` |  |
| `list_id` | `string \| null` |  |
| `id` | `string` |  |
| `name` | `string \| null` |  |
| `subscriber_count` | `string \| null` |  |
| `display_order` | `integer \| null` |  |


</details>

## Segments

### Segments List

Get information about all available segments for a specific list

#### Python SDK

```python
await mailchimp.segments.list(
    list_id="<str>"
)
```

#### API

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


#### Parameters

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

#### Records

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


#### Meta

| Field Name | Type | Description |
|------------|------|-------------|
| `total_items` | `integer` |  |

</details>

### Segments Get

Get information about a specific segment

#### Python SDK

```python
await mailchimp.segments.get(
    list_id="<str>",
    segment_id="<str>"
)
```

#### API

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


#### Parameters

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `list_id` | `string` | Yes | The unique ID for the list |
| `segment_id` | `string` | Yes | The unique id for the segment |


<details>
<summary><b>Response Schema</b></summary>

#### Records

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

## Segment Members

### Segment Members List

Get information about members in a saved segment

#### Python SDK

```python
await mailchimp.segment_members.list(
    list_id="<str>",
    segment_id="<str>"
)
```

#### API

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


#### Parameters

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `list_id` | `string` | Yes | The unique ID for the list |
| `segment_id` | `string` | Yes | The unique id for the segment |
| `count` | `integer` | No | The number of records to return |
| `offset` | `integer` | No | Used for pagination |


<details>
<summary><b>Response Schema</b></summary>

#### Records

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


#### Meta

| Field Name | Type | Description |
|------------|------|-------------|
| `total_items` | `integer` |  |

</details>

## Unsubscribes

### Unsubscribes List

Get information about members who have unsubscribed from a specific campaign

#### Python SDK

```python
await mailchimp.unsubscribes.list(
    campaign_id="<str>"
)
```

#### API

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


#### Parameters

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `campaign_id` | `string` | Yes | The unique id for the campaign |
| `count` | `integer` | No | The number of records to return |
| `offset` | `integer` | No | Used for pagination |


<details>
<summary><b>Response Schema</b></summary>

#### Records

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


#### Meta

| Field Name | Type | Description |
|------------|------|-------------|
| `total_items` | `integer` |  |

</details>

