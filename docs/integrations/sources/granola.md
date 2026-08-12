# Granola

<HideInUI>

This page contains the setup guide and reference information for the [Granola](https://www.granola.ai/) source connector. Granola is an AI-powered meeting notes tool. This connector reads meeting notes from a Granola workspace using the [Granola API](https://docs.granola.ai/introduction).

</HideInUI>

## Prerequisites

You need a Granola API key, which is available on a **Business** or **Enterprise** plan. You can create either a personal API key or a workspace API key. The note access scopes selected when a key is created determine which data it returns:

- **Personal API key**: available to workspace members on a Business or Enterprise plan.
- **Workspace API key**: available to workspace administrators on a Business or Enterprise plan.

See [Data access by scope and key type](#data-access-by-scope-and-key-type) for details about the available scopes.

## Setup guide

### Generate an API key

Granola supports two API key types. Choose the one that matches your access needs.

#### Personal API key

1. Open the Granola desktop app.
2. Go to **Settings > Connectors > API keys**.
3. Click **Create new key**.
4. Select the note access scopes the key should include.
5. Click **Generate API Key**.
6. Copy the generated API key and store it securely.

:::note
Workspace administrators control which note access scopes members may use in **Settings > Workspace > General > API access for members**. Click **Manage** to review or update these controls.
:::

#### Workspace API key

1. Log in to the Granola desktop app as a workspace administrator.
2. Go to **Settings > Connectors > Workspace API keys**.
3. Click **Create new key**.
4. Select the note access scopes the key should include.
5. Copy the generated API key and store it securely.

### Set up the Granola connector in Airbyte

1. Enter a **Name** for the Granola source connector.
2. Enter your **API Key**.
3. (Optional) Enter a **Start Date** in `YYYY-MM-DD` format. The connector replicates notes created on or after this date. If you leave this field empty, the connector defaults to replicating notes from the last two years.
4. Click **Set up source** and wait for the connection test to complete.

## Supported sync modes

The Granola source connector supports the following sync modes:

| Feature                        | Supported? |
| :----------------------------- | :--------- |
| Full Refresh Sync              | Yes        |
| Full Refresh Sync - Overwrite  | Yes        |
| Incremental Sync               | Yes        |
| Incremental Sync - Append      | Yes        |

## Supported streams

The Granola source connector supports the following streams:

| Stream | Sync mode | Primary key |
| :--- | :--- | :--- |
| `notes` | Incremental | `id` |
| `detailed_notes` | Full refresh | `id` |

### Notes

The `notes` stream retrieves meeting notes from your Granola workspace using the [`GET /v1/notes`](https://docs.granola.ai/api-reference/list-notes) endpoint. Each record includes the note ID, title, object type, owner name and email, and creation timestamp. The API may return additional fields beyond those listed here, and the connector captures them automatically.

For incremental syncs, the connector uses `created_at` as the cursor field and fetches notes in 30-day time windows. The connector uses the `created_after` and `created_before` query parameters for these windows.

The API only returns notes that have a generated AI summary and transcript. Notes that are still being processed or were never summarized are excluded.

### Detailed notes

The `detailed_notes` stream retrieves each note from the `notes` stream with the [`GET /v1/notes/{note_id}`](https://docs.granola.ai/api-reference/get-note) endpoint. It includes the note metadata plus fields available only on the detail endpoint, including summaries, transcripts, attendees, calendar events, and folder membership.

The connector always requests transcript data for this stream. Syncing `detailed_notes` can increase sync time and data volume for workspaces with many notes.

The API returns a 404 for notes that don't have a generated AI summary and transcript. Because `detailed_notes` uses `notes` as its parent stream, it only requests detail records for notes returned by the list endpoint.

### Data access by scope and key type

The set of notes returned by the API depends on the access scopes selected when the key is created:

| Scope or key type | Data scope |
| :--- | :--- |
| **Personal notes** | Notes you own, notes shared directly with you, and notes in private folders shared with you. |
| **Public notes** | Notes visible to everyone in the workspace, such as notes in the Team space. |
| **Workspace API key** | Can read public notes unless the workspace has turned off **Allow public folders**, plus notes in spaces where **Allow Granola API access** is enabled. It cannot read private notes or private folders. Workspace API keys are not tied to a user and do not expire. |

For more information, refer to the [Granola API documentation](https://docs.granola.ai/help-center/sharing/integrations/granola-api).

## Performance considerations

The Granola API enforces rate limits of 25 requests in a burst and 5 requests per second sustained. Limits may apply per user or per workspace depending on the key's access scope.

| Metric | Value |
| :--- | :--- |
| Burst capacity | 25 requests |
| Time window | 5 seconds |
| Sustained rate | 5 requests per second (300/minute) |

The connector uses the API's burst limit to manage request volume and retries requests when a `429 Too Many Requests` response is received.

## IP allow list

If you use Airbyte Cloud and your organization restricts access to specific IPs, add the [Airbyte Cloud IP addresses](https://docs.airbyte.com/platform/operating-airbyte/ip-allowlist) to your allow list.

## Reference

This connector uses the [Granola API](https://docs.granola.ai/introduction). All API requests use the `https://public-api.granola.ai` endpoint.

For programmatic configuration, use these parameter names:

| Field | Required | Description |
| :--- | :---: | :--- |
| `api_key` | Yes | Granola API key starting with `grn_`. Create a personal or workspace API key in Granola and select the note access scopes it should include. |
| `start_date` | No | Earliest note creation date to replicate, in `YYYY-MM-DD` format. Defaults to two years before the sync runs. |

## Changelog

<details>
  <summary>Expand to review</summary>

| Version | Date | Pull Request | Subject |
| :------ | :--- | :----------- | :------ |
| 0.2.12 | 2026-08-12 | [84280](https://github.com/airbytehq/airbyte/pull/84280) | Clarify API key setup instructions and document the default two-year start date |
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
