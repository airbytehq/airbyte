# Google Tasks
This page contains the setup guide and reference information for the [Google Tasks](https://tasksboard.com/app) source connector.

## Documentation reference:
Visit `https://developers.google.com/tasks/reference/rest` for API documentation

## Authentication setup
`Source-productive` uses bearer token authentication,
Visit `https://support.google.com/googleapi/answer/6158849?hl=en&amp;ref_topic=7013279` for getting bearer token via OAuth2.0

## Setting postman for getting bearer token
Currently Code granted OAuth 2.0 is not directly supported by airbyte, thus you could setup postman for getting the bearer token which could be used as `api_key`,
Steps:
- Visit google cloud `https://console.cloud.google.com/apis/api/tasks.googleapis.com/metrics` and enable the tasks api service
- Go to the consent screen `https://console.cloud.google.com/apis/credentials/consent` and add your email for enabling postman testing access
- Visit `https://console.cloud.google.com/apis/credentials` and create new credentails for OAuth 2.0 and copy client id and client secret 
- Add callback url `https://oauth.pstmn.io/v1/callback` while credential creation
- Goto postman client and select new tab for setting authorization to OAuth 2.0
  - Set scope as `https://www.googleapis.com/auth/tasks https://www.googleapis.com/auth/tasks.readonly`
  - Set access token URL as `https://accounts.google.com/o/oauth2/token`
  - Set auth URL as `https://accounts.google.com/o/oauth2/v2/auth`
  - Click `Get New Access Token` and authorize via your google account
  - Copy the resulted bearer token and use it as credential for the connector

## Configuration

| Input | Type | Description | Default Value |
|-------|------|-------------|---------------|
| `api_key` | `string` | API Key.  |  |
| `start_date` | `string` | Start date.  |  |
| `records_limit` | `string` | Records Limit. The maximum number of records to be returned per request | 50 |

## Streams
| Stream Name | Primary Key | Pagination | Supports Full Sync | Supports Incremental |
|-------------|-------------|------------|---------------------|----------------------|
| tasks | id | DefaultPaginator | ✅ |  ✅  |
| lists_tasks | id | DefaultPaginator | ✅ |  ✅  |

## Changelog

<details>
  <summary>Expand to review</summary>

| Version | Date | Pull Request | Subject |
| ------------------ | ------------ | --- | ---------------- |
| 0.0.1 | 2024-09-12 | [45427](https://github.com/airbytehq/airbyte/pull/45427) | Initial release by [@btkcodedev](https://github.com/btkcodedev) via Connector Builder |

</details>