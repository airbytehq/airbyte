# Infobip
This is the Infobip source that ingests data from the infobip API.

Infobip drives deeper customer engagement with secure, personalized communications across SMS, RCS, Email, Voice, WhatsApp, and more https://www.infobip.com/

In order to use this source, you must first create an Infobip account. Once logged in, you can head over to Developer Tools in the sidebar and click on API Keys. Here you can generate a new API key for authenticating.

You can learn more about the API here https://www.infobip.com/docs/api

## Configuration

| Input | Type | Description | Default Value |
|-------|------|-------------|---------------|
| `api_key` | `string` | API Key. The API key associated with your account. |  |

## Streams
| Stream Name | Primary Key | Pagination | Supports Full Sync | Supports Incremental |
|-------------|-------------|------------|---------------------|----------------------|
| people | id | DefaultPaginator | ✅ |  ❌  |
| companies | id | DefaultPaginator | ✅ |  ❌  |
| custom_attributes | name | DefaultPaginator | ✅ |  ❌  |
| forms | id | DefaultPaginator | ✅ |  ❌  |
| conversations | id | DefaultPaginator | ✅ |  ❌  |

## Changelog

<details>
  <summary>Expand to review</summary>

| Version          | Date              | Pull Request | Subject        |
|------------------|-------------------|--------------|----------------|
| 0.0.1 | 2024-10-29 | | Initial release by [@aazam-gh](https://github.com/aazam-gh) via Connector Builder |

</details>
