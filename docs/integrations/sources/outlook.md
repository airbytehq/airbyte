# Outlook
Outlook is the email service provided by Microsoft. This connector enables you to sync emails, mailboxes, and conversations from Microsoft Outlook/Exchange Online using Microsoft Graph API with delegated permissions for multi-tenant support.

## Configuration

| Input | Type | Description | Default Value |
|-------|------|-------------|---------------|
| `client_id` | `string` | OAuth Client ID. The Client ID of your Microsoft Azure application |  |
| `tenant_id` | `string` | Tenant ID (Optional). Azure AD Tenant ID (optional for multi-tenant apps, defaults to &#39;common&#39;) | common |
| `client_secret` | `string` | OAuth Client Secret. The Client Secret of your Microsoft Azure application |  |
| `refresh_token` | `string` | Refresh Token. Refresh token obtained from Microsoft OAuth flow |  |

## Streams
| Stream Name | Primary Key | Pagination | Supports Full Sync | Supports Incremental |
|-------------|-------------|------------|---------------------|----------------------|
| profile |  | No pagination | ✅ |  ❌  |
| mailboxes | id | DefaultPaginator | ✅ |  ❌  |
| messages | id | DefaultPaginator | ✅ |  ❌  |
| messages_details | id | No pagination | ✅ |  ❌  |
| conversations | conversationId | DefaultPaginator | ✅ |  ❌  |

## Changelog

<details>
  <summary>Expand to review</summary>

| Version          | Date              | Pull Request | Subject        |
|------------------|-------------------|--------------|----------------|
| 0.0.10 | 2025-11-18 | [69707](https://github.com/airbytehq/airbyte/pull/69707) | Update dependencies |
| 0.0.9 | 2025-10-29 | [69010](https://github.com/airbytehq/airbyte/pull/69010) | Update dependencies |
| 0.0.8 | 2025-10-21 | [68311](https://github.com/airbytehq/airbyte/pull/68311) | Update dependencies |
| 0.0.7 | 2025-10-14 | [67772](https://github.com/airbytehq/airbyte/pull/67772) | Update dependencies |
| 0.0.6 | 2025-10-07 | [67343](https://github.com/airbytehq/airbyte/pull/67343) | Update dependencies |
| 0.0.5 | 2025-09-30 | [66389](https://github.com/airbytehq/airbyte/pull/66389) | Update dependencies |
| 0.0.4 | 2025-09-09 | [65826](https://github.com/airbytehq/airbyte/pull/65826) | Update dependencies |
| 0.0.3 | 2025-08-23 | [65161](https://github.com/airbytehq/airbyte/pull/65161) | Update dependencies |
| 0.0.2 | 2025-08-14 | [64942](https://github.com/airbytehq/airbyte/pull/64942) | Fix docker image entrypoint for platform syncs |
| 0.0.1 | 2025-08-14 | | Initial release by [@saif-qureshi-341](https://github.com/saif-qureshi-341) via Connector Builder |

</details>
