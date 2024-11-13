# Oncehub
This is the Oncehub source that ingests data from the Oncehub API.

Oncehub is a no-code conversational journeys builder, integrating AI, chatbots, live chat, instant calls, and scheduled meetings https://oncehub.com/.

To use this source you must first create an account. Once logged in head over to Settings -&gt; API &amp; Webhooks and copy your API Key.
You can learn more about the API here https://developers.oncehub.com/reference/introduction

## Configuration

| Input | Type | Description | Default Value |
|-------|------|-------------|---------------|
| `api_key` | `string` | API Key. API key to use. Find it in your OnceHub account under the API &amp; Webhooks Integration page. |  |
| `start_date` | `string` | Start date.  |  |

## Streams
| Stream Name | Primary Key | Pagination | Supports Full Sync | Supports Incremental |
|-------------|-------------|------------|---------------------|----------------------|
| bookings | id | CursorPagination | ✅ |  ✅  |
| booking_pages | id | CursorPagination | ✅ |  ❌  |
| event_types | id | CursorPagination | ✅ |  ❌  |
| master_pages | id | CursorPagination | ✅ |  ❌  |
| users | id | CursorPagination | ✅ |  ❌  |
| teams | id | CursorPagination | ✅ |  ❌  |
| contacts | id | CursorPagination | ✅ |  ❌  |

## Changelog

<details>
  <summary>Expand to review</summary>

| Version          | Date              | Pull Request | Subject        |
|------------------|-------------------|--------------|----------------|
| 0.0.1 | 2024-10-30 | | Initial release by [@aazam-gh](https://github.com/aazam-gh) via Connector Builder |

</details>
