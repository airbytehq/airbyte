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
| 0.0.19 | 2025-12-09 | [70809](https://github.com/airbytehq/airbyte/pull/70809) | Update dependencies |
| 0.0.18 | 2025-11-25 | [69899](https://github.com/airbytehq/airbyte/pull/69899) | Update dependencies |
| 0.0.17 | 2025-11-18 | [69552](https://github.com/airbytehq/airbyte/pull/69552) | Update dependencies |
| 0.0.16 | 2025-10-29 | [68907](https://github.com/airbytehq/airbyte/pull/68907) | Update dependencies |
| 0.0.15 | 2025-10-21 | [68395](https://github.com/airbytehq/airbyte/pull/68395) | Update dependencies |
| 0.0.14 | 2025-10-14 | [67990](https://github.com/airbytehq/airbyte/pull/67990) | Update dependencies |
| 0.0.13 | 2025-10-07 | [67172](https://github.com/airbytehq/airbyte/pull/67172) | Update dependencies |
| 0.0.12 | 2025-09-30 | [66277](https://github.com/airbytehq/airbyte/pull/66277) | Update dependencies |
| 0.0.11 | 2025-09-09 | [65040](https://github.com/airbytehq/airbyte/pull/65040) | Update dependencies |
| 0.0.10 | 2025-07-26 | [63808](https://github.com/airbytehq/airbyte/pull/63808) | Update dependencies |
| 0.0.9 | 2025-07-19 | [63452](https://github.com/airbytehq/airbyte/pull/63452) | Update dependencies |
| 0.0.8 | 2025-07-05 | [62533](https://github.com/airbytehq/airbyte/pull/62533) | Update dependencies |
| 0.0.7 | 2025-06-21 | [61881](https://github.com/airbytehq/airbyte/pull/61881) | Update dependencies |
| 0.0.6 | 2025-05-24 | [60630](https://github.com/airbytehq/airbyte/pull/60630) | Update dependencies |
| 0.0.5 | 2025-05-10 | [59784](https://github.com/airbytehq/airbyte/pull/59784) | Update dependencies |
| 0.0.4 | 2025-05-03 | [59329](https://github.com/airbytehq/airbyte/pull/59329) | Update dependencies |
| 0.0.3 | 2025-04-26 | [58705](https://github.com/airbytehq/airbyte/pull/58705) | Update dependencies |
| 0.0.2 | 2025-04-19 | [57655](https://github.com/airbytehq/airbyte/pull/57655) | Update dependencies |
| 0.0.1 | 2025-04-05 | [57210](http://github.com/airbytehq/airbyte/pull/57210) | Initial release by [@btkcodedev](https://github.com/btkcodedev) via Connector Builder |

</details>
