# Workramp

## Sync overview

The Workramp source supports both Full Refresh only.

This source can sync data for the [Workramp API](https://developers.workramp.com/reference/getting-started).

### Output schema

This Source is capable of syncing the following core Streams:

- [awarded_certifications](https://developers.workramp.com/reference/get-all-awarded-certifications)
- [certifications](https://developers.workramp.com/reference/get-all-certifications-2)
- [paths_users](https://developers.workramp.com/reference/get-all-paths-1)
- [registrations](https://developers.workramp.com/reference/get-all-registrations)
- [users](https://developers.workramp.com/reference/get-1)
- [trainings](https://developers.workramp.com/reference/get-all-trainings)

### Features

| Feature                   | Supported?\(Yes/No\) | Notes |
| :------------------------ | :------------------- | :---- |
| Full Refresh Sync         | Yes                  |       |
| Incremental - Append Sync | No                   |       |
| Namespaces                | No                   |       |

### Performance considerations

The Workramp connector should not run into Workramp API limitations under normal usage.

## Requirements

- **Workramp API ke**. See the [Workramp docs](https://developers.workramp.com/reference/basic-auth) for information on how to obtain an API key.

## Changelog

| Version | Date       | Pull Request                                             | Subject                       |
| :------ | :--------- | :------------------------------------------------------- | :---------------------------- |
| 0.1.0   | 2022-01-02 | [18843](https://github.com/airbytehq/airbyte/pull/18843) | Add Workramp Source Connector |
