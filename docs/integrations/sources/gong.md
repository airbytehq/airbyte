# Gong

## Sync overview

The Gong source supports both Full Refresh only.

This source can sync data for the [Gong API](https://us-14321.app.gong.io/settings/api/documentation#overview).

### Output schema

This Source is capable of syncing the following core Streams:

- [answered scorecards](https://us-14321.app.gong.io/settings/api/documentation#post-/v2/stats/activity/scorecards)
- [calls](https://us-14321.app.gong.io/settings/api/documentation#get-/v2/calls)
- [scorecards](https://us-14321.app.gong.io/settings/api/documentation#get-/v2/settings/scorecards)
- [users](https://us-14321.app.gong.io/settings/api/documentation#get-/v2/users)

### Features

| Feature                   | Supported?\(Yes/No\) | Notes |
| :------------------------ | :------------------- | :---- |
| Full Refresh Sync         | Yes                  |       |
| Incremental - Append Sync | No                   |       |
| Namespaces                | No                   |       |

### Performance considerations

The Gong connector should not run into Gong API limitations under normal usage.
By default Gong limits your company's access to the service to 3 API calls per second, and 10,000 API calls per day.

## Requirements

- **Gong API keys**. See the [Gong docs](https://us-14321.app.gong.io/settings/api/documentation#overview) for information on how to obtain the API keys.

## Changelog

<details>
  <summary>Expand to review</summary>

| Version | Date       | Pull Request                                             | Subject                                                                         |
| :------ | :--------- | :------------------------------------------------------- | :------------------------------------------------------------------------------ |
| 0.1.6   | 2024-05-28 | [38596](https://github.com/airbytehq/airbyte/pull/38596) | Make connector compatible with builder                                          |
| 0.1.5   | 2024-04-19 | [37169](https://github.com/airbytehq/airbyte/pull/37169) | Updating to 0.80.0 CDK                                                          |
| 0.1.4   | 2024-04-18 | [37169](https://github.com/airbytehq/airbyte/pull/37169) | Manage dependencies with Poetry.                                                |
| 0.1.3   | 2024-04-15 | [37169](https://github.com/airbytehq/airbyte/pull/37169) | Base image migration: remove Dockerfile and use the python-connector-base image |
| 0.1.2   | 2024-04-12 | [37169](https://github.com/airbytehq/airbyte/pull/37169) | schema descriptions                                                             |
| 0.1.1   | 2024-02-05 | [34847](https://github.com/airbytehq/airbyte/pull/34847) | Adjust stream schemas and make ready for airbyte-lib                            |
| 0.1.0   | 2022-10-27 | [18819](https://github.com/airbytehq/airbyte/pull/18819) | Add Gong Source Connector                                                       |

</details>