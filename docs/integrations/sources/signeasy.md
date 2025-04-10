# SignEasy
Website: https://app.signeasy.com/
API Reference: https://docs.signeasy.com/reference/introduction-to-signeasy-apis

## Configuration

| Input | Type | Description | Default Value |
|-------|------|-------------|---------------|
| `api_key` | `string` | API Key.  |  |
| `start_date` | `string` | Start date.  |  |

## Streams
| Stream Name | Primary Key | Pagination | Supports Full Sync | Supports Incremental |
|-------------|-------------|------------|---------------------|----------------------|
| user_me | id | No pagination | ✅ |  ✅  |
| originals | id | No pagination | ✅ |  ✅  |
| envelopes | id | No pagination | ✅ |  ✅  |
| signed_envelopes | uuid | No pagination | ✅ |  ❌  |
| self_signed_documents | id | No pagination | ✅ |  ✅  |
| templates | id | No pagination | ✅ |  ❌  |

## Changelog

<details>
  <summary>Expand to review</summary>

| Version          | Date              | Pull Request | Subject        |
|------------------|-------------------|--------------|----------------|
| 0.0.1 | 2025-04-10 | [57562](https://github.com/airbytehq/airbyte/pull/57562) | Initial release by [@btkcodedev](https://github.com/btkcodedev) via Connector Builder |

</details>
