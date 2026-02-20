# Pylon

<HideInUI>

This page contains the setup guide and reference information for the [Pylon](https://usepylon.com) source connector.

</HideInUI>

## Prerequisites

- A Pylon account with admin access
- A Pylon API token. Only admin users can create API tokens. Generate one in the Pylon dashboard under **Settings** > **API**. For details, see the [Pylon authentication documentation](https://docs.usepylon.com/pylon-docs/developer/api/authentication).

## Setup guide

<FieldAnchor field="api_token">

Enter your Pylon API token.

</FieldAnchor>

<FieldAnchor field="start_date">

For **Start Date**, enter the date from which you want to start syncing incremental data, in the format `YYYY-MM-DDTHH:MM:SSZ` (for example, `2024-01-01T00:00:00Z`). This applies to the Issues stream. Other streams always perform a full refresh.

</FieldAnchor>

<HideInUI>

## Supported sync modes

The Pylon source connector supports the following [sync modes](https://docs.airbyte.com/cloud/core-concepts/#connection-sync-modes):

- [Full Refresh - Overwrite](https://docs.airbyte.com/understanding-airbyte/connections/full-refresh-overwrite/)
- [Full Refresh - Append](https://docs.airbyte.com/understanding-airbyte/connections/full-refresh-append)
- [Incremental - Append](https://docs.airbyte.com/understanding-airbyte/connections/incremental-append)
- [Incremental - Append + Deduped](https://docs.airbyte.com/understanding-airbyte/connections/incremental-append-deduped)

## Supported streams

The Pylon source connector supports the following streams:

- [Accounts](https://docs.usepylon.com/pylon-docs/developer/api/api-reference/accounts)
- [Activity Types](https://docs.usepylon.com/pylon-docs/developer/api/api-reference)
- [Contacts](https://docs.usepylon.com/pylon-docs/developer/api/api-reference/contacts)
- [Custom Fields](https://docs.usepylon.com/pylon-docs/developer/api/api-reference/custom-fields) (fetches fields for account, issue, and contact object types)
- [Issue Messages](https://docs.usepylon.com/pylon-docs/developer/api/api-reference/messages) (child stream of Issues)
- Issue Threads (child stream of Issues)
- [Issues](https://docs.usepylon.com/pylon-docs/developer/api/api-reference/issues) \(Incremental\)
- Issue Statuses
- [Knowledge Base Articles](https://docs.usepylon.com/pylon-docs/developer/api/api-reference/knowledge-base) (child stream of Knowledge Bases)
- [Knowledge Bases](https://docs.usepylon.com/pylon-docs/developer/api/api-reference/knowledge-base)
- [Tags](https://docs.usepylon.com/pylon-docs/developer/api/api-reference/tags)
- [Teams](https://docs.usepylon.com/pylon-docs/developer/api/api-reference/teams)
- [Ticket Forms](https://docs.usepylon.com/pylon-docs/developer/api/api-reference/ticket-forms)
- [User Roles](https://docs.usepylon.com/pylon-docs/developer/api/api-reference/user-roles)
- [Users](https://docs.usepylon.com/pylon-docs/developer/api/api-reference/users)

### Stream notes

- **Issues** is the only incremental stream. It uses the `created_at` cursor field. The Pylon API requires `start_time` and `end_time` parameters with a maximum 30-day window, so the connector syncs Issues in 30-day intervals from the configured start date.
- **Issue Messages**, **Issue Threads**, and **Knowledge Base Articles** are child streams. Issue Messages and Issue Threads depend on the Issues stream, and Knowledge Base Articles depends on the Knowledge Bases stream. Syncing these child streams requires syncing their parent streams as well.
- **Custom Fields** queries three object types (account, issue, and contact) separately and combines the results.

## Limitations & Troubleshooting

<details>
<summary>
Expand to see details about Pylon connector limitations and troubleshooting.
</summary>

### Rate limiting

The Pylon API enforces rate limits that vary by endpoint. For example, the Issues endpoint allows 10 requests per minute, while other endpoints allow up to 60 requests per minute. The connector handles rate-limited responses (HTTP 429) with exponential backoff and up to 3 retries. Under normal usage, the connector should not encounter sustained rate limiting.

### Connector limitations

- The Issues stream syncs data in 30-day windows. If a single 30-day window contains more records than the API returns in one response, some records may not be synced.
- Schemas are defined with `additionalProperties: true`, so the connector accepts fields not explicitly defined in the schema. Field availability may vary depending on your Pylon plan and account configuration.

</details>

## Changelog

<details>
  <summary>Expand to review</summary>

| Version | Date       | Pull Request                                             | Subject                        |
| :------ | :--------- | :------------------------------------------------------- | :----------------------------- |
| 0.0.1   | 2026-02-20 | [73624](https://github.com/airbytehq/airbyte/pull/73624) | Initial release of Pylon source connector |

</details>

</HideInUI>
