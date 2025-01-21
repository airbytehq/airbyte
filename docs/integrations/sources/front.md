# Front
This page contains the setup guide and reference information for the [Front](https://app.frontapp.com) source connector.

## Documentation reference:
Visit `https://dev.frontapp.com/reference/introduction` for API documentation

## Authentication setup
`Source-front` uses bearer token authentication,
Visit `https://dev.frontapp.com/docs/create-and-revoke-api-tokens` for getting your API token.

## Configuration

| Input | Type | Description | Default Value |
|-------|------|-------------|---------------|
| `api_key` | `string` | API Key.  |  |
| `start_date` | `string` | Start date.  |  |
| `page_limit` | `string` | Page limit. Page limit for the responses | 50 |

## Streams
| Stream Name | Primary Key | Pagination | Supports Full Sync | Supports Incremental |
|-------------|-------------|------------|---------------------|----------------------|
| events | id | DefaultPaginator | ✅ |  ✅  |
| inboxes | id | DefaultPaginator | ✅ |  ❌  |
| inboxes_channels | id | DefaultPaginator | ✅ |  ❌  |
| inboxes_conversations | id | DefaultPaginator | ✅ |  ✅  |
| inboxes_teammates | id | DefaultPaginator | ✅ |  ❌  |
| conversations | id | DefaultPaginator | ✅ |  ✅  |
| conversations_events | id | DefaultPaginator | ✅ |  ✅  |
| conversations_followers | id | DefaultPaginator | ✅ |  ❌  |
| conversations_inboxes |  | DefaultPaginator | ✅ |  ❌  |
| conversations_messages | id | DefaultPaginator | ✅ |  ✅  |
| links | id | DefaultPaginator | ✅ |  ❌  |
| accounts | id | DefaultPaginator | ✅ |  ✅  |
| accounts_contacts | id | DefaultPaginator | ✅ |  ✅  |
| contacts | id | DefaultPaginator | ✅ |  ✅  |
| channels | id | DefaultPaginator | ✅ |  ❌  |
| company_tags | id | DefaultPaginator | ✅ |  ✅  |
| teammates | id | DefaultPaginator | ✅ |  ❌  |
| tags | id | DefaultPaginator | ✅ |  ✅  |
| tags_children | id | DefaultPaginator | ✅ |  ✅  |
| teammates_tags | id | DefaultPaginator | ✅ |  ✅  |
| teams | id | DefaultPaginator | ✅ |  ❌  |
| teams_tags | id | DefaultPaginator | ✅ |  ✅  |
| contact_groups | id | DefaultPaginator | ✅ |  ❌  |
| conversations_drafts | id | DefaultPaginator | ✅ |  ✅  |
| contacts_notes |  | DefaultPaginator | ✅ |  ✅  |
| teammates_contact_groups | id | DefaultPaginator | ✅ |  ❌  |
| teams_contact_groups |  | DefaultPaginator | ✅ |  ❌  |
| knowledge_bases | id | DefaultPaginator | ✅ |  ✅  |
| knowledge_bases_articles |  | DefaultPaginator | ✅ |  ✅  |
| knowledge_bases_categories |  | DefaultPaginator | ✅ |  ✅  |
| message_template_folders | id | DefaultPaginator | ✅ |  ✅  |
| teams_signatures | id | DefaultPaginator | ✅ |  ❌  |
| message_templates | id | DefaultPaginator | ✅ |  ✅  |
| teammates_message_templates | id | DefaultPaginator | ✅ |  ❌  |
| teams_message_templates | id | DefaultPaginator | ✅ |  ✅  |

## Changelog

<details>
  <summary>Expand to review</summary>

| Version | Date | Pull Request | Subject |
| ------------------ | ------------ | --- | ---------------- |
| 0.0.1 | 2024-09-11 | [45387](https://github.com/airbytehq/airbyte/pull/45387) | Initial release by [@btkcodedev](https://github.com/btkcodedev) via Connector Builder |

</details>