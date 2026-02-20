# Pylon

## Sync overview

The Pylon source supports Full Refresh and Incremental syncs.

This source can sync data for the [Pylon API](https://docs.usepylon.com/api-reference).

### Output schema

This Source is capable of syncing the following Streams:

- Accounts
- Contacts
- Issues (Incremental)
- Issue Messages
- Issue Threads
- Tags
- Teams
- Users
- Custom Fields
- Knowledge Bases
- Knowledge Base Articles
- Ticket Forms
- User Roles
- Activity Types
- Issue Statuses

### Features

| Feature                   | Supported?\(Yes/No\) | Notes                                      |
| :------------------------ | :------------------- | :----------------------------------------- |
| Full Refresh Sync         | Yes                  |                                             |
| Incremental - Append Sync | Yes                  | Issues stream only                          |
| Namespaces                | No                   |                                             |

### Performance considerations

The Pylon API enforces rate limits. The connector uses exponential backoff to handle rate-limited responses (HTTP 429). Under normal usage volumes, the connector should not encounter sustained rate limiting.

## Requirements

- **Pylon API token**. Generate one in the Pylon dashboard under Settings > API. See the [Pylon API docs](https://docs.usepylon.com/api-reference) for more details.

## Configuration

| Parameter    | Type   | Required | Description                                                                 |
| :----------- | :----- | :------- | :-------------------------------------------------------------------------- |
| `api_token`  | string | Yes      | Your Pylon API token.                                                       |
| `start_date` | string | Yes      | The date from which to start syncing data, in UTC. Format: YYYY-MM-DDTHH:MM:SSZ |

## Changelog

<details>
  <summary>Expand to review</summary>

| Version | Date       | Pull Request                                             | Subject                        |
| :------ | :--------- | :------------------------------------------------------- | :----------------------------- |
| 0.0.1   | 2026-02-18 | [73624](https://github.com/airbytehq/airbyte/pull/73624) | Initial release of Pylon source connector |

</details>
