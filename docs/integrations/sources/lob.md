# Lob
This page contains the setup guide and reference information for the [Lob](https://dashboard.lob.com/) source connector.

## Documentation reference:
Visit `https://docs.lob.com/` for API documentation

## Authentication setup
`Lob` uses Basic Http authentication via api key, Visit `https://dashboard.lob.com/settings/api-keys` for getting your api keys. Refer `https://docs.lob.com/#tag/Authentication` for more details.

## Configuration

| Input | Type | Description | Default Value |
|-------|------|-------------|---------------|
| `api_key` | `string` | API Key. API key to use for authentication. You can find your account&#39;s API keys in your Dashboard Settings at https://dashboard.lob.com/settings/api-keys. |  |
| `start_date` | `string` | Start date.  |  |
| `limit` | `string` | Limit. Max records per page limit | 50 |

## Streams
| Stream Name | Primary Key | Pagination | Supports Full Sync | Supports Incremental |
|-------------|-------------|------------|---------------------|----------------------|
| addresses | id | DefaultPaginator | ✅ |  ✅  |
| banks | id | DefaultPaginator | ✅ |  ✅  |
| postcards | id | DefaultPaginator | ✅ |  ✅  |
| templates | id | DefaultPaginator | ✅ |  ✅  |
| templates_versions | id | DefaultPaginator | ✅ |  ✅  |
| campaigns | id | DefaultPaginator | ✅ |  ✅  |
| uploads | id | DefaultPaginator | ✅ |  ✅  |
| qr_code_analytics | resource_id | DefaultPaginator | ✅ |  ✅  |

## Changelog

<details>
  <summary>Expand to review</summary>

| Version | Date | Pull Request | Subject |
| ------------------ | ------------ | --- | ---------------- |
| 0.0.1 | 2024-09-22 | [45843](https://github.com/airbytehq/airbyte/pull/45843) | Initial release by [@btkcodedev](https://github.com/btkcodedev) via Connector Builder |

</details>