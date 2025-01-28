# Mux
This directory contains the manifest-only connector for [`source-mux`](https://www.mux.com/).

## Documentation reference:
Visit `https://docs.mux.com/api-reference` for API documentation

## Authentication setup
`Mux` uses Http basic authentication, Visit `https://docs.mux.com/core/make-api-requests#http-basic-auth` for getting your API keys.
## Configuration

| Input | Type | Description | Default Value |
|-------|------|-------------|---------------|
| `username` | `string` | Username.  |  |
| `password` | `string` | Password.  |  |
| `start_date` | `string` | Start date.  |  |
| `playback_id` | `string` | Playback ID. The playback id for your video asset shown in website details |  |

## Streams
| Stream Name | Primary Key | Pagination | Supports Full Sync | Supports Incremental |
|-------------|-------------|------------|---------------------|----------------------|
| video_assets | id | DefaultPaginator | ✅ |  ✅  |
| video_live-streams | id | DefaultPaginator | ✅ |  ✅  |
| video_playbacks | id | DefaultPaginator | ✅ |  ❌  |
| system_signin-keys | id | DefaultPaginator | ✅ |  ✅  |
| video_playback-restrictions | id | DefaultPaginator | ✅ |  ✅  |
| video_transcription-vocabularies | id | DefaultPaginator | ✅ |  ✅  |
| video_uploads | id | DefaultPaginator | ✅ |  ❌  |
| video_signing-keys | id | DefaultPaginator | ✅ |  ✅  |

## Changelog

<details>
  <summary>Expand to review</summary>

| Version | Date | Pull Request | Subject |
| ------------------ | ------------ | --- | ---------------- |
| 0.0.12 | 2025-01-25 | [52280](https://github.com/airbytehq/airbyte/pull/52280) | Update dependencies |
| 0.0.11 | 2025-01-18 | [51818](https://github.com/airbytehq/airbyte/pull/51818) | Update dependencies |
| 0.0.10 | 2025-01-11 | [51175](https://github.com/airbytehq/airbyte/pull/51175) | Update dependencies |
| 0.0.9 | 2024-12-28 | [50651](https://github.com/airbytehq/airbyte/pull/50651) | Update dependencies |
| 0.0.8 | 2024-12-21 | [50127](https://github.com/airbytehq/airbyte/pull/50127) | Update dependencies |
| 0.0.7 | 2024-12-14 | [49632](https://github.com/airbytehq/airbyte/pull/49632) | Update dependencies |
| 0.0.6 | 2024-12-12 | [49241](https://github.com/airbytehq/airbyte/pull/49241) | Update dependencies |
| 0.0.5 | 2024-12-11 | [48912](https://github.com/airbytehq/airbyte/pull/48912) | Starting with this version, the Docker image is now rootless. Please note that this and future versions will not be compatible with Airbyte versions earlier than 0.64 |
| 0.0.4 | 2024-11-04 | [48231](https://github.com/airbytehq/airbyte/pull/48231) | Update dependencies |
| 0.0.3 | 2024-10-29 | [47880](https://github.com/airbytehq/airbyte/pull/47880) | Update dependencies |
| 0.0.2 | 2024-10-28 | [47492](https://github.com/airbytehq/airbyte/pull/47492) | Update dependencies |
| 0.0.1 | 2024-09-27 | [45921](https://github.com/airbytehq/airbyte/pull/45921) | Initial release by [@btkcodedev](https://github.com/btkcodedev) via Connector Builder |

</details>
