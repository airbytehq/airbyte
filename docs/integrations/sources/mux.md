# Mux
Website: https://www.mux.com/
API Docs: https://docs.mux.com/api-reference
Auth Docs: https://docs.mux.com/core/make-api-requests#http-basic-auth

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

| Version          | Date       | Subject        |
|------------------|------------|----------------|
| 0.0.1 | 2024-09-27 | Initial release by [@btkcodedev](https://github.com/btkcodedev) via Connector Builder|

</details>