# ClickUp API

## Sync overview

This source can sync data from [ClickUp API](https://clickup.com/api/). Currently, this connector only supports full refresh syncs. That is, every time a sync is run, all the records are fetched from the source.

### Output schema

This source is capable of syncing the following streams:

- [`user`](https://clickup.com/api/clickupreference/operation/GetAuthorizedUser/)
- [`teams`](https://clickup.com/api/clickupreference/operation/GetAuthorizedTeams/)
- [`spaces`](https://clickup.com/api/clickupreference/operation/GetSpaces/)
- [`folders`](https://clickup.com/api/clickupreference/operation/GetFolders/)
- [`lists`](https://clickup.com/api/clickupreference/operation/GetLists/)
- [`tasks`](https://clickup.com/api/clickupreference/operation/GetTasks)

### Features

| Feature           | Supported? \(Yes/No\) | Notes |
| :---------------- | :-------------------- | :---- |
| Full Refresh Sync | Yes                   |       |
| Incremental Sync  | No                    |       |

### Performance considerations

The ClickUp API enforces request rate limits per token. The rate limits are depending on your workplace plan. See [here](https://clickup.com/api/developer-portal/rate-limits/).

## Getting started

### Requirements

1. Generate an API key from [ClickUp](https://clickup.com/). See [here](https://clickup.com/api/developer-portal/authentication/#generate-your-personal-api-token).

### Setup guide

The following fields are required fields for the connector to work:

- `api_token`: Your ClickUp API Token.

Here are some optional fields for different streams:

- `team_id`: Your team ID in your ClickUp workspace. It is required for `space` stream.

- `space_id`: Your space ID in your ClickUp workspace. It is required for `folder` stream.

- `folder_id`: Your folder ID in your ClickUp space. It is required for `list` stream.

- `list_id`: Your list ID in your folder of space. It is required for `task` stream.

- `Include Closed Tasks`: Toggle to include or exclude closed tasks. By default, they are excluded.

## Changelog

<details>
  <summary>Expand to review</summary>

| Version | Date       | Pull Request                                             | Subject                           |
| :------ | :--------- | :------------------------------------------------------- | :-------------------------------- |
| 0.1.2 | 2024-05-21 | [38501](https://github.com/airbytehq/airbyte/pull/38501) | [autopull] base image + poetry + up_to_date |
| 0.1.1   | 2023-02-10 | [23951](https://github.com/airbytehq/airbyte/pull/23951) | Add optional include Closed Tasks |
| 0.1.0   | 2022-11-07 | [17770](https://github.com/airbytehq/airbyte/pull/17770) | New source                        |

</details>
