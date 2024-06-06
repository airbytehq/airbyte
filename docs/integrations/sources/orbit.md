# Orbit

## Sync overview

This source can sync data for the [Orbit API](https://docs.orbit.love/reference/about-the-orbit-api). It currently only supports Full Refresh syncs.

### Output schema

This Source is capable of syncing the following core Streams:

- [Members](https://api.orbit.love/reference/get_workspace-slug-members)
- [Workspaces](https://docs.orbit.love/reference/get_workspaces-workspace-slug)

### Features

| Feature           | Supported?\(Yes/No\) | Notes |
| :---------------- | :------------------- | :---- |
| Full Refresh Sync | Yes                  |       |
| Incremental Sync  | No                   |       |
| Namespaces        | No                   |       |
| Pagination        | Yes                  |       |

### Performance considerations / Rate Limiting

The Orbit API is rate limited at 120 requests per IP per minute as stated [here](https://docs.orbit.love/reference/rate-limiting).

Please [create an issue](https://github.com/airbytehq/airbyte/issues) if you see any rate limit issues that are not automatically retried successfully.

## Getting started

### Requirements

- Orbit API key - This can either be a workspace-tied key or a general personal key.

### Setup guide

The Orbit API Key should be available to you immediately as an Orbit user.

1. Head to app.orbit.love and login to your account.
2. Go to the **Settings** tab on the right sidebar.
3. Navigate to **API Tokens**.
4. Click **New API Token** in the top right if one doesn't already exist.

## Changelog

<details>
  <summary>Expand to review</summary>

| Version | Date       | Pull Request                                             | Subject                                                                         |
| :------ | :--------- | :------------------------------------------------------- | :------------------------------------------------------------------------------ |
| 0.3.6 | 2024-06-06 | [39179](https://github.com/airbytehq/airbyte/pull/39179) | [autopull] Upgrade base image to v1.2.2 |
| 0.3.5 | 2024-05-28 | [38700](https://github.com/airbytehq/airbyte/pull/38700) | Make compatible with builder |
| 0.3.4 | 2024-04-19 | [37212](https://github.com/airbytehq/airbyte/pull/37212) | Updating to 0.80.0 CDK |
| 0.3.3 | 2024-04-18 | [37212](https://github.com/airbytehq/airbyte/pull/37212) | Manage dependencies with Poetry. |
| 0.3.2 | 2024-04-15 | [37212](https://github.com/airbytehq/airbyte/pull/37212) | Base image migration: remove Dockerfile and use the python-connector-base image |
| 0.3.1 | 2024-04-12 | [37212](https://github.com/airbytehq/airbyte/pull/37212) | schema descriptions |
| 0.3.0 | 2023-10-25 | [30976](https://github.com/airbytehq/airbyte/pull/30976) | Migrate to low-code framework |
| 0.2.0 | 2023-10-23 | [31747](https://github.com/airbytehq/airbyte/pull/31747) | Update schema |
| 0.1.1 | 2022-06-28 | [14208](https://github.com/airbytehq/airbyte/pull/14208) | Remove unused schema |
| 0.1.0 | 2022-06-27 | [13390](https://github.com/airbytehq/airbyte/pull/13390) | Initial Release |

</details>
