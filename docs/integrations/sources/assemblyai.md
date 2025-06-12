# AssemblyAI
Website: https://www.assemblyai.com/
API Reference: https://www.assemblyai.com/docs/api-reference/overview

## Configuration

| Input | Type | Description | Default Value |
|-------|------|-------------|---------------|
| `api_key` | `string` | API Key. Your AssemblyAI API key. You can find it in the AssemblyAI dashboard at https://www.assemblyai.com/app/api-keys. |  |
| `start_date` | `string` | Start date.  |  |
| `subtitle_format` | `string` | Subtitle format. The subtitle format for transcript_subtitle stream | srt |

## Streams
| Stream Name | Primary Key | Pagination | Supports Full Sync | Supports Incremental |
|-------------|-------------|------------|---------------------|----------------------|
| transcripts | id | DefaultPaginator | ✅ |  ✅  |
| transcript_sentences | uuid | DefaultPaginator | ✅ |  ❌  |
| paragraphs | uuid | DefaultPaginator | ✅ |  ❌  |
| transcript_subtitle | uuid | DefaultPaginator | ✅ |  ❌  |

## Changelog

<details>
  <summary>Expand to review</summary>

| Version          | Date              | Pull Request | Subject        |
|------------------|-------------------|--------------|----------------|
| 0.0.6 | 2025-05-24 | [60630](https://github.com/airbytehq/airbyte/pull/60630) | Update dependencies |
| 0.0.5 | 2025-05-10 | [59784](https://github.com/airbytehq/airbyte/pull/59784) | Update dependencies |
| 0.0.4 | 2025-05-03 | [59329](https://github.com/airbytehq/airbyte/pull/59329) | Update dependencies |
| 0.0.3 | 2025-04-26 | [58705](https://github.com/airbytehq/airbyte/pull/58705) | Update dependencies |
| 0.0.2 | 2025-04-19 | [57655](https://github.com/airbytehq/airbyte/pull/57655) | Update dependencies |
| 0.0.1 | 2025-04-05 | [57210](http://github.com/airbytehq/airbyte/pull/57210) | Initial release by [@btkcodedev](https://github.com/btkcodedev) via Connector Builder |

</details>
