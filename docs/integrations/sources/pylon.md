# Pylon

<HideInUI>

This page contains the setup guide and reference information for the [Pylon](https://usepylon.com) source connector.

</HideInUI>

## Prerequisites

- A Pylon account with an Admin role.
- A Pylon API token. Only Admin users can create API tokens. Generate one in your Pylon dashboard under **Settings > API**. For details, see [Pylon's authentication guide](https://docs.usepylon.com/pylon-docs/developer/api/authentication).

## Setup guide

<FieldAnchor field="api_token">

Enter your **API Token**. This is the Bearer token used to authenticate all requests to the Pylon API.

</FieldAnchor>

<FieldAnchor field="start_date">

Optionally, enter a **Start Date** in UTC format (`YYYY-MM-DDTHH:MM:SSZ`). This controls how far back the connector syncs data for the Issues stream and its child streams (Issue Messages and Issue Threads). If not provided, defaults to 30 days ago.

</FieldAnchor>

## Supported sync modes

The Pylon source connector supports the following [sync modes](https://docs.airbyte.com/cloud/core-concepts/#connection-sync-modes):

- Full Refresh | Overwrite
- Full Refresh | Append
- Incremental Sync | Append (Issues stream only)

## Supported streams

The Pylon source connector supports the following streams:

- [Accounts](https://docs.usepylon.com/pylon-docs/developer/api/api-reference/accounts)
- [Activity Types](https://docs.usepylon.com/pylon-docs/developer/api/api-reference)
- [Contacts](https://docs.usepylon.com/pylon-docs/developer/api/api-reference/contacts)
- [Custom Fields](https://docs.usepylon.com/pylon-docs/developer/api/api-reference/custom-fields)
- [Issues](https://docs.usepylon.com/pylon-docs/developer/api/api-reference/issues) (Incremental)
  - [Issue Messages](https://docs.usepylon.com/pylon-docs/developer/api/api-reference/messages)
  - [Issue Threads](https://docs.usepylon.com/pylon-docs/developer/api/api-reference)
- [Issue Statuses](https://docs.usepylon.com/pylon-docs/developer/api/api-reference)
- [Knowledge Bases](https://docs.usepylon.com/pylon-docs/developer/api/api-reference/knowledge-base)
  - [Knowledge Base Articles](https://docs.usepylon.com/pylon-docs/developer/api/api-reference/knowledge-base)
- [Tags](https://docs.usepylon.com/pylon-docs/developer/api/api-reference/tags)
- [Teams](https://docs.usepylon.com/pylon-docs/developer/api/api-reference/teams)
- [Ticket Forms](https://docs.usepylon.com/pylon-docs/developer/api/api-reference/ticket-forms)
- [User Roles](https://docs.usepylon.com/pylon-docs/developer/api/api-reference/user-roles)
- [Users](https://docs.usepylon.com/pylon-docs/developer/api/api-reference/users)

### Stream notes

- **Issues** is the only incremental stream. It uses `created_at` as its cursor field and syncs data in 30-day windows, as required by the Pylon API.
- **Issue Messages** and **Issue Threads** are child streams of Issues. They retrieve data for each issue returned by the Issues stream, so the Start Date configuration indirectly affects these streams.
- **Knowledge Base Articles** is a child stream of Knowledge Bases.
- **Custom Fields** queries the Pylon API once for each of the three supported object types: account, issue, and contact.

## Limitations & Troubleshooting

### Rate limiting

The Pylon API enforces per-endpoint rate limits. The Issues endpoint allows 10 requests per minute, while most other endpoints allow 60 requests per minute. The connector handles rate-limited responses (HTTP 429) with exponential backoff and retries up to 3 times.

## Changelog

<details>
  <summary>Expand to review</summary>

| Version | Date       | Pull Request                                             | Subject                        |
| :------ | :--------- | :------------------------------------------------------- | :----------------------------- |
| 0.0.3 | 2026-02-24 | [73850](https://github.com/airbytehq/airbyte/pull/73850) | Update dependencies |
| 0.0.2 | 2026-02-20 | [73693](https://github.com/airbytehq/airbyte/pull/73693) | Make start_date optional, default to 1 month ago |
| 0.0.1 | 2026-02-20 | [73624](https://github.com/airbytehq/airbyte/pull/73624) | Initial release of Pylon source connector |

</details>
