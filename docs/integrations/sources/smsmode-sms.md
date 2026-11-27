# smsmode SMS

A source connector for the smsmode API dedicated to standard SMS services, supporting message logs and general consumption data synchronization.

## Set up the source

Create an API key using smsmode's [Credential API](https://dev.smsmode.com/commons/v1/#tag/Credential), with read access to the channels you want to sync. Enter this key when configuring the source in Airbyte. The connector sends it in the `X-Api-Key` header on both streams.

| Input | Type | Description | Default Value |
|-------|------|-------------|---------------|
| `api_key` | `string` | API Key. Your smsmode API key. You can generate and manage API keys in the smsmode dashboard under the &#39;Credentials&#39; section: https://dev.smsmode.com/commons/v1/#tag/Credential. Make sure the key is active and has the required permissions for your use case. |  |

## Supported streams

| Stream Name | Primary Key | Pagination | Supports Full Sync | Supports Incremental |
|-------------|-------------|------------|---------------------|----------------------|
| messages |  | DefaultPaginator | ✅ |  ❌  |
| consumptions | consumptionId | DefaultPaginator | ✅ |  ❌  |

- **messages** uses [`GET /sms/v1/messages`](https://dev.smsmode.com/sms/v1/#tag/Message/operation/messages-list). The API defaults to sent messages (`MT`).
- **consumptions** uses [`GET /commons/v1/consumptions`](https://dev.smsmode.com/commons/v1/#tag/Consumption/operation/consumptions-list). The API defaults to monthly SMS aggregates (`SMS_MONTH`).

Both streams request 100 records per page, the API's maximum page size, and increment the `page` parameter to fetch more records.

## Limitations

- **Rolling date windows.** The connector does not send `startDate` or `endDate`. The documented API defaults therefore apply: `messages` requests the last 10 days up to now, and `consumptions` requests the last 3 months up to today. These date filters are not configurable in this connector; this is not a statement about smsmode's data retention.
- **Full refresh only.** Neither stream has an incremental cursor, so each sync re-reads the current API window.
- **No primary key for messages.** The connector does not declare `messageId` as a primary key, even though it is present in the schema. The `consumptions` primary key is `consumptionId`.

## Changelog

<details>
  <summary>Expand to review</summary>

| Version          | Date              | Pull Request | Subject        |
|------------------|-------------------|--------------|----------------|
| 0.0.11 | 2026-11-10 | [91750](https://github.com/airbytehq/airbyte/pull/91750) | Update dependencies |
| 0.0.10 | 2026-11-03 | [90771](https://github.com/airbytehq/airbyte/pull/90771) | Update dependencies |
| 0.0.9 | 2026-10-27 | [90057](https://github.com/airbytehq/airbyte/pull/90057) | Update dependencies |
| 0.0.8 | 2026-10-20 | [89427](https://github.com/airbytehq/airbyte/pull/89427) | Update dependencies |
| 0.0.7 | 2026-10-13 | [88816](https://github.com/airbytehq/airbyte/pull/88816) | Update dependencies |
| 0.0.6 | 2026-10-06 | [88071](https://github.com/airbytehq/airbyte/pull/88071) | Update dependencies |
| 0.0.5 | 2026-09-29 | [87358](https://github.com/airbytehq/airbyte/pull/87358) | Update dependencies |
| 0.0.4 | 2026-09-22 | [86847](https://github.com/airbytehq/airbyte/pull/86847) | Update dependencies |
| 0.0.3 | 2026-09-15 | [86240](https://github.com/airbytehq/airbyte/pull/86240) | Update dependencies |
| 0.0.2 | 2026-09-08 | [85688](https://github.com/airbytehq/airbyte/pull/85688) | Update dependencies |
| 0.0.1 | 2026-08-28 | [79709](https://github.com/airbytehq/airbyte/pull/79709) | Initial release by [@CaladeTechnologies](https://github.com/CaladeTechnologies) via Connector Builder |

</details>
