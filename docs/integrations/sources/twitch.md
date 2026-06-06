# Twitch

This page contains the setup guide and reference information for the [Twitch](https://www.twitch.tv/) source connector.

## Documentation reference

Visit the [Twitch Helix API Reference](https://dev.twitch.tv/docs/api/reference/) for API documentation.

## Authentication setup

Source Twitch uses OAuth 2.0 for authentication. You need a Twitch application registered in the [Twitch Developer Console](https://dev.twitch.tv/console/apps).
The connector requests no Twitch authorization scopes; it uses OAuth only to obtain a valid token for read-only Helix endpoints.

1. Go to [Twitch Developer Console](https://dev.twitch.tv/console/apps) and register a new application.
2. Set the **OAuth Redirect URL** to `https://cloud.airbyte.com/auth_flow`.
3. Note your **Client ID** and **Client Secret**.
4. When configuring in Airbyte, the connector will handle the OAuth flow to obtain a refresh token.

See the [Twitch Authentication Guide](https://dev.twitch.tv/docs/authentication/) for more details.

## Configuration

| Input | Type | Description | Default Value |
|-------|------|-------------|---------------|
| `client_id` | `string` | Client ID. Your Twitch application client ID. |  |
| `client_secret` | `string` | Client Secret. Your Twitch application client secret. |  |
| `login` | `array` | Twitch Username(s). List of Twitch usernames to sync data for. |  |
| `start_date` | `string` | Start Date. The earliest date to sync data from (ISO 8601 format). | `2011-01-01T00:00:00Z` |
| `custom_reports` | `object` | Custom Reports. Configure custom clip and video streams filtered by Twitch game/category. |  |

### Custom reports

Custom reports let you create additional streams that pull clips or videos for a specific Twitch game/category. Each report resolves the game name to a Twitch category ID automatically.

#### Custom clip reports

| Input | Type | Description | Required |
|-------|------|-------------|----------|
| `name` | `string` | Report Name. Used to generate the stream name as `custom_clips_<snake_case(name)>`. | Yes |
| `game_name` | `string` | Game Name. Exact Twitch category name (e.g., `Fortnite`, `Minecraft`). | Yes |
| `is_featured` | `boolean` | Featured Clips Only. When set, filters to featured or non-featured clips. | No |

#### Custom video reports

| Input | Type | Description | Required |
|-------|------|-------------|----------|
| `name` | `string` | Report Name. Used to generate the stream name as `custom_videos_<snake_case(name)>`. | Yes |
| `game_name` | `string` | Game Name. Exact Twitch category name (e.g., `Fortnite`, `Minecraft`). | Yes |
| `sort` | `string` | Sort. One of `time`, `trending`, `views`. | No |
| `type` | `string` | Video Type. One of `all`, `archive`, `highlight`, `upload`. | No |
| `period` | `string` | Period. One of `all`, `day`, `month`, `week`. | No |
| `language` | `string` | Language. ISO 639-1 language code (e.g., `en`). | No |

## Streams

### Static streams

These streams sync data for the Twitch usernames configured in the `login` field.

| Stream Name | Primary Key | Pagination | Supports Full Sync | Supports Incremental |
|-------------|-------------|------------|---------------------|----------------------|
| users | `id` | No pagination | ✅ | ❌ |
| clips | `id` | DefaultPaginator | ✅ | ✅ |
| videos | `id` | DefaultPaginator | ✅ | ✅ |

### Dynamic streams (custom reports)

These streams are generated from the `custom_reports` configuration. Each resolves the configured game name to a Twitch category ID via the `/helix/games` endpoint, then fetches clips or videos for that category.

| Stream Name Pattern | Primary Key | Pagination | Supports Full Sync | Supports Incremental |
|---------------------|-------------|------------|---------------------|----------------------|
| `custom_clips_<name>` | `id` | DefaultPaginator | ✅ | ✅ |
| `custom_videos_<name>` | `id` | No pagination | ✅ | ❌ |

## Limitations and troubleshooting

- Twitch limits clip pagination to approximately 1,000 results per time window. The connector uses one-hour incremental slices for clip streams to reduce the chance of hitting this cap, but very active categories or broadcasters can still exceed it.
- Custom report `game_name` values must exactly match Twitch category names because the connector resolves them through the Twitch `/helix/games` endpoint before reading records.
- Custom video report streams are full-refresh-only and request the first 100 videos for the resolved game/category. Twitch does not support cursor pagination for `/helix/videos` requests filtered only by `game_id`.
- Twitch API rate limits are communicated through `Ratelimit-*` response headers. The connector treats HTTP 429 responses as retryable and backs off before retrying.

## Changelog

<details>
  <summary>Expand to review</summary>

| Version | Date | Pull Request | Subject |
|---------|------|--------------|---------|
| 0.1.0 | 2026-05-08 | [77904](https://github.com/airbytehq/airbyte/pull/77904) | Initial release |

</details>
