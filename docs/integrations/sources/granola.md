# Granola

<HideInUI>

This page contains the setup guide and reference information for the [Granola](https://www.granola.ai/) source connector. Granola is an AI-powered meeting notes tool. This connector reads meeting notes from a Granola workspace using the [Granola API](https://docs.granola.ai/introduction).

</HideInUI>

## Prerequisites

You need one of the following:

- **Personal API key** (Beta) — available to any workspace member on a **Business** or **Enterprise** plan. On Enterprise plans, a workspace admin must enable Personal API key creation in **Settings > Workspace > General**.
- **Enterprise API key** — available to workspace admins on an **Enterprise** plan.

The API endpoints and connector behavior are the same for both key types. The difference is the scope of data each key can access. See [Data access by key type](#data-access-by-key-type) for details.

## Setup guide

### Generate an API key

Granola supports two API key types. Choose the one that matches your plan and access needs.

#### Personal API key (Beta)

1. Open the Granola desktop app.
2. Go to **Settings > Connectors > API keys > Create new key**.
3. Select **Personal API key** and click **Generate API Key**.
4. Copy the generated API key and store it securely.

:::note
On Enterprise plans, a workspace admin must enable Personal API key creation via the "Allow personal API keys" toggle in **Settings > Workspace > General** before members can create Personal API keys.
:::

#### Enterprise API key

1. Log in to your Granola workspace as an administrator.
2. Go to **Settings > API > Create new key**.
3. Select **Enterprise API key** and click **Generate API Key**.
4. Copy the generated API key and store it securely.

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

The Granola source connector supports the following stream:

| Stream  | Sync mode   | Primary key |
| :------ | :---------- | :---------- |
| `notes` | Incremental | `id`        |

### Notes

The `notes` stream retrieves meeting notes from your Granola workspace using the [`GET /v1/notes`](https://docs.granola.ai/api-reference/list-notes) endpoint. Each record includes the note ID, title, object type, owner name and email, and creation timestamp. The API may return additional fields beyond those listed here, and the connector captures them automatically.

For incremental syncs, the connector uses `created_at` as the cursor field and fetches notes in 30-day time windows.

The API only returns notes that have a generated AI summary and transcript. Notes that are still being processed or were never summarized are excluded.

This connector does not use the single-note detail endpoint (`GET /v1/notes/{note_id}`), so fields available only on that endpoint, such as summaries, transcripts, attendees, calendar events, and folder membership, are not included.

### Data access by key type

The set of notes returned by the API depends on the type of API key you use:

| Key type | Data scope |
| :--- | :--- |
| **Personal API key** | Notes you own, notes shared with you, and notes in private folders shared with you. For more information, refer to the [Granola Personal API documentation](https://docs.granola.ai/help-center/sharing/integrations/personal-api). |
| **Enterprise API key** | All notes in the Team space that workspace members can read. Private notes and private folders are excluded. For more information, refer to the [Granola Enterprise API documentation](https://docs.granola.ai/help-center/sharing/integrations/enterprise-api). |

## Performance considerations

The Granola API enforces rate limits. For Enterprise API keys, limits are applied per workspace. For Personal API keys, limits are applied per user.

| Metric         | Value                             |
| :------------- | :-------------------------------- |
| Burst capacity | 25 requests                       |
| Time window    | 5 seconds                         |
| Sustained rate | 5 requests per second (300/minute) |

The connector handles rate limiting automatically by retrying requests when a `429 Too Many Requests` response is received.

## Changelog

<details>
  <summary>Expand to review</summary>

| Version | Date       | Pull Request | Subject         |
| :------ | :--------- | :----------- | :-------------- |
| 0.2.0-rc.1 | 2026-04-27 | [*PR_NUMBER_PLACEHOLDER*](https://github.com/airbytehq/airbyte/pull/*PR_NUMBER_PLACEHOLDER*) | set default_concurrency=4 for concurrency tuning iteration 1 (Path A, max_rate_limit=5 req/s) |
| 0.1.3 | 2026-04-21 | [76632](https://github.com/airbytehq/airbyte/pull/76632) | Update dependencies |
| 0.1.2 | 2026-03-31 | [75737](https://github.com/airbytehq/airbyte/pull/75737) | Update dependencies |
| 0.1.1 | 2026-03-24 | [75353](https://github.com/airbytehq/airbyte/pull/75353) | Update dependencies |
| 0.1.0 | 2026-02-25 | [74033](https://github.com/airbytehq/airbyte/pull/74033) | Add detailed_notes substream with full note content via SubstreamPartitionRouter |
| 0.0.3 | 2026-02-24 | [73377](https://github.com/airbytehq/airbyte/pull/73377) | Update dependencies |
| 0.0.2 | 2026-02-12 | [73306](https://github.com/airbytehq/airbyte/pull/73306) | Fix pagination: set page_size to API maximum of 30 and improve stop condition |
| 0.0.1 | 2026-02-11 | [73238](https://github.com/airbytehq/airbyte/pull/73238) | Initial release |

</details>
