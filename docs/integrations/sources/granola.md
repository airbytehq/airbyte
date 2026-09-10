# Granola

<HideInUI>

This page contains the setup guide and reference information for the [Granola](https://www.granola.ai/) source connector. Granola is an AI-powered meeting notes tool. This connector reads meeting notes from a Granola workspace using the [Granola API](https://docs.granola.ai/introduction).

</HideInUI>

## Prerequisites

You need a Granola API key from a workspace on a **Business** or **Enterprise** plan. Granola offers two kinds of keys:

- **Personal API key**: any workspace member can create one. The key belongs to that member and inherits their access.
- **Workspace API key**: only workspace administrators can create one. The key belongs to the workspace, doesn't expire, and keeps working after the person who created it leaves.

The API endpoints and connector behavior are the same for both. The difference is which notes the key can read. See [Data access by key type](#data-access-by-key-type) for details.

## Setup guide

### Generate an API key

#### Personal API key

1. Open the Granola desktop app.
2. Go to **Settings > Connectors > API keys > Create new key**.
3. Select the note access scopes the key includes: **Personal notes**, **Public notes**, or both.
4. Click **Generate API Key**.
5. Copy the generated API key and store it securely.

:::note
On Enterprise plans, a workspace administrator controls which scopes members can use in **Settings > Workspace > General > API access for members**. If a scope is disabled there, members can't create keys with it, and the connector can't read the notes that scope covers.
:::

#### Workspace API key

1. Open the Granola desktop app as a workspace administrator.
2. Go to **Settings > Connectors > Workspace API keys > Create new key**.
3. Copy the generated API key and store it securely.

### Set up the Granola connector in Airbyte

1. Enter a **Name** for the Granola source connector.
2. Enter your **API Key**.
3. (Optional) Enter a **Start Date** in `YYYY-MM-DD` format. The connector replicates notes created on or after this date. If you leave this field empty, the connector defaults to replicating notes from the last two years.
4. Click **Set up source** and wait for the connection test to complete.

## Supported sync modes

The Granola source connector supports the following sync modes:

| Feature                             | Supported? |
| :---------------------------------- | :--------- |
| Full Refresh Sync                   | Yes        |
| Full Refresh Sync - Overwrite       | Yes        |
| Incremental Sync                    | Yes        |
| Incremental Sync - Append           | Yes        |
| Incremental Sync - Append + Deduped | Yes        |

## Supported streams

The Granola source connector supports the following streams:

| Stream | Sync mode | Primary key |
| :--- | :--- | :--- |
| `notes` | Incremental | `id` |
| `detailed_notes` | Full refresh | `id` |
| `note_transcripts` | Full refresh | None |

### Notes

The `notes` stream retrieves meeting notes from your Granola workspace using the [`GET /v1/notes`](https://docs.granola.ai/api-reference/list-notes) endpoint. Each record includes the note ID, title, object type, owner name and email, and creation timestamp. The API may return additional fields beyond those listed here, and the connector captures them automatically.

For incremental syncs, the connector uses `created_at` as the cursor field and fetches notes in 30-day time windows, passing each window's bounds as second-level timestamps in the `created_after` and `created_before` query parameters. Because the cursor is the creation date, edits to an existing note aren't picked up by later incremental syncs. Run a full refresh if you need to capture changes to notes you already synced.

The API only returns notes that have a generated AI summary and transcript. Notes that are still being processed or were never summarized are excluded.

### Detailed notes

The `detailed_notes` stream retrieves each note from the `notes` stream with the [`GET /v1/notes/{note_id}`](https://docs.granola.ai/api-reference/get-note) endpoint. It includes the note metadata plus fields available only on the detail endpoint, including summaries, transcripts, attendees, calendar events, and folder membership.

The connector always requests transcript data for this stream. Syncing `detailed_notes` can increase sync time and data volume for workspaces with many notes.

The API returns a 404 for notes that don't have a generated AI summary and transcript. Because `detailed_notes` uses `notes` as its parent stream, it only requests detail records for notes returned by the list endpoint.

Granola returns the transcript inline. If a transcript is too large to return that way, the API responds with `413` and the error code `TRANSCRIPT_TOO_LARGE` instead of the note. Long recordings, such as multi-hour meetings, are the most likely to hit this limit. Starting with version 0.3.0, the connector skips those notes in this stream instead of failing the sync, so a note with an oversized transcript produces no `detailed_notes` record at all. Sync the `note_transcripts` stream to replicate their transcripts, and see [Notes are missing from `detailed_notes`](#notes-are-missing-from-detailed_notes) for how to tell which notes were skipped.

### Note transcripts

The `note_transcripts` stream retrieves each note's transcript from the [`GET /v1/notes/{note_id}/transcript`](https://docs.granola.ai/api-reference/get-transcript) endpoint, one record per transcript segment. Each record carries the segment's speaker, text, and start and end times, plus the `note_id` of the note it belongs to. Because this endpoint is paged, it returns transcripts of any size, including those `detailed_notes` can't return inline.

The stream has no primary key, so records are appended rather than deduplicated. It isn't incremental: on every sync it re-reads the full list of notes created since your start date and requests each of those notes' transcripts again, so it adds at least one request for every note in that range rather than only for new notes. The connector requests the API's maximum of 100 transcript segments per page, so a transcript longer than 100 segments costs one more request for each additional page. On a workspace with thousands of historical notes this dominates sync time, so size your sync frequency against the total note count.

If Granola no longer returns a transcript for a note that the `notes` stream listed, such as a note deleted or unshared mid-sync, the API responds with `404` and the connector skips that note instead of failing the stream.

### Data access by key type

The set of notes the connector can read depends on the key you configure:

| Key type | Data scope |
| :--- | :--- |
| **Personal API key** | The scopes selected when the key was created. **Personal notes** covers notes you own, notes shared directly with you, and notes in private folders shared with you. **Public notes** covers notes visible to everyone in the workspace, such as notes in the Team space. |
| **Workspace API key** | Public notes in the workspace, plus notes in spaces where an administrator turned on **Allow Granola API access**. Private notes and folders that weren't shared this way are excluded. |

Notes in Granola are private by default, so a key with only **Public notes** access returns nothing until notes are placed in a folder that everyone in the workspace can see. If a sync returns no records, check the key's scopes first. For more information, refer to the [Granola API documentation](https://docs.granola.ai/help-center/sharing/integrations/granola-api).

## Performance considerations

The Granola API enforces rate limits. Depending on the key's access scope, limits apply per user or per workspace.

| Metric | Value |
| :--- | :--- |
| Burst capacity | 25 requests |
| Time window | 5 seconds |
| Sustained rate | 5 requests per second (300/minute) |

The connector throttles itself to the documented burst limit of 25 requests per 5 seconds. If Granola still returns `429 Too Many Requests`, or a `5xx` server error, the connector retries the request up to 5 times. It waits for the interval in the `Retry-After` response header when Granola sends one, up to 60 seconds, and otherwise backs off exponentially.

## Troubleshooting

### Notes are missing after syncing with version 0.2.13 or earlier

Versions up to 0.2.13 sent each 30-day window's bounds as dates rather than timestamps. The Granola API excludes the entire day named by `created_before`, so those syncs skipped every note created on a window boundary date, in both the `notes` and `detailed_notes` streams. Version 0.2.14 sends second-level timestamps, so new syncs cover the full range.

Existing connections don't backfill the skipped notes on their own. After upgrading to 0.2.14 or later, [refresh](/platform/operator-guides/refreshes) the `notes` stream once to recover them. You don't need to do anything for `detailed_notes`, which reads from `notes` and picks up the recovered notes with it.

### Notes are missing from `detailed_notes`

Starting with version 0.3.0, the connector skips a note in `detailed_notes` when Granola won't return its transcript inline. Earlier versions failed the whole sync in this situation. The connector logs each skip at INFO level rather than as a warning, so search the sync logs for `transcript is too large` to identify the affected notes.

A skipped note still appears in `notes`, with its ID, title, owner, and creation time, and its transcript still appears in `note_transcripts`. Only the fields that come from the detail endpoint are unavailable for those notes: summaries, attendees, calendar events, and folder membership.

## IP allow list

If you use Airbyte Cloud and your organization restricts access to specific IPs, add the [Airbyte Cloud IP addresses](https://docs.airbyte.com/platform/operating-airbyte/ip-allowlist) to your allow list.

## Reference

This connector uses the [Granola API](https://docs.granola.ai/introduction). All API requests use the `https://public-api.granola.ai` endpoint.

For programmatic configuration, use these parameter names:

| Field | Required | Description |
| :--- | :---: | :--- |
| `api_key` | Yes | Granola API key. Use a personal API key for notes your own account can read, or a workspace API key for the workspace's shared notes. |
| `start_date` | No | Earliest note creation date to replicate, in `YYYY-MM-DD` format. Defaults to two years before the sync runs. |

## Changelog

<details>
  <summary>Expand to review</summary>

| Version | Date | Pull Request | Subject |
| :------ | :--- | :----------- | :------ |
| 0.3.1 | 2026-09-08 | [85516](https://github.com/airbytehq/airbyte/pull/85516) | Update dependencies |
| 0.3.0 | 2026-08-21 | [84907](https://github.com/airbytehq/airbyte/pull/84907) | Add note_transcripts stream for transcripts of any size. Notes whose transcript is too large to return inline are now skipped in detailed_notes, producing no record for those notes, instead of failing the sync |
| 0.2.14 | 2026-08-21 | [84898](https://github.com/airbytehq/airbyte/pull/84898) | Stop dropping notes created on a 30-day incremental slice boundary date |
| 0.2.13 | 2026-08-18 | [84623](https://github.com/airbytehq/airbyte/pull/84623) | Update dependencies |
| 0.2.12 | 2026-08-12 | [84278](https://github.com/airbytehq/airbyte/pull/84278) | Retry rate-limited and server-error responses with backoff honoring Retry-After |
| 0.2.11 | 2026-08-11 | [83964](https://github.com/airbytehq/airbyte/pull/83964) | Update dependencies |
| 0.2.10 | 2026-08-04 | [83481](https://github.com/airbytehq/airbyte/pull/83481) | Update dependencies |
| 0.2.9 | 2026-07-28 | [82970](https://github.com/airbytehq/airbyte/pull/82970) | Update dependencies |
| 0.2.8 | 2026-07-21 | [82437](https://github.com/airbytehq/airbyte/pull/82437) | Update dependencies |
| 0.2.7 | 2026-07-14 | [81869](https://github.com/airbytehq/airbyte/pull/81869) | Update dependencies |
| 0.2.6 | 2026-06-30 | [81096](https://github.com/airbytehq/airbyte/pull/81096) | Update dependencies |
| 0.2.5 | 2026-06-23 | [80491](https://github.com/airbytehq/airbyte/pull/80491) | Update dependencies |
| 0.2.4 | 2026-06-16 | [79886](https://github.com/airbytehq/airbyte/pull/79886) | Update dependencies |
| 0.2.3 | 2026-06-09 | [79357](https://github.com/airbytehq/airbyte/pull/79357) | Update dependencies |
| 0.2.2 | 2026-06-02 | [77288](https://github.com/airbytehq/airbyte/pull/77288) | Update dependencies |
| 0.2.1 | 2026-05-15 | [78117](https://github.com/airbytehq/airbyte/pull/78117) | Update API key setup instructions |
| 0.2.0 | 2026-05-07 | [77861](https://github.com/airbytehq/airbyte/pull/77861) | Promoted release candidate to GA |
| 0.2.0-rc.4 | 2026-05-01 | [77698](https://github.com/airbytehq/airbyte/pull/77698) | Revert default_concurrency from 6 to 5 (optimal value from tuning) and add HTTP API budget matching Granola's documented rate limit (25 req/5s burst) |
| 0.2.0-rc.3 | 2026-04-30 | [77645](https://github.com/airbytehq/airbyte/pull/77645) | Increase default_concurrency from 5 to 6 for concurrency tuning iteration 3 (final) |
| 0.2.0-rc.2 | 2026-04-28 | [77551](https://github.com/airbytehq/airbyte/pull/77551) | Increase default_concurrency from 4 to 5 for concurrency tuning iteration 2 |
| 0.2.0-rc.1 | 2026-04-27 | [77067](https://github.com/airbytehq/airbyte/pull/77067) | set default_concurrency=4 for concurrency tuning iteration 1 (Path A, max_rate_limit=5 req/s) |
| 0.1.3 | 2026-04-21 | [76632](https://github.com/airbytehq/airbyte/pull/76632) | Update dependencies |
| 0.1.2 | 2026-03-31 | [75737](https://github.com/airbytehq/airbyte/pull/75737) | Update dependencies |
| 0.1.1 | 2026-03-24 | [75353](https://github.com/airbytehq/airbyte/pull/75353) | Update dependencies |
| 0.1.0 | 2026-02-25 | [74033](https://github.com/airbytehq/airbyte/pull/74033) | Add detailed_notes substream with full note content via SubstreamPartitionRouter |
| 0.0.3 | 2026-02-24 | [73377](https://github.com/airbytehq/airbyte/pull/73377) | Update dependencies |
| 0.0.2 | 2026-02-12 | [73306](https://github.com/airbytehq/airbyte/pull/73306) | Fix pagination: set page_size to API maximum of 30 and improve stop condition |
| 0.0.1 | 2026-02-11 | [73238](https://github.com/airbytehq/airbyte/pull/73238) | Initial release |

</details>
