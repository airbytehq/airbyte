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

- **Workramp API key**. See the [Workramp docs](https://developers.workramp.com/reference/basic-auth) for information on how to obtain an API key.

## Changelog

<details>
  <summary>Expand to review</summary>

| Version | Date       | Pull Request                                             | Subject                       |
|:--------|:-----------| :------------------------------------------------------- | :---------------------------- |
| 0.2.9 | 2025-01-25 | [52392](https://github.com/airbytehq/airbyte/pull/52392) | Update dependencies |
| 0.2.8 | 2025-01-18 | [52024](https://github.com/airbytehq/airbyte/pull/52024) | Update dependencies |
| 0.2.7 | 2025-01-11 | [51388](https://github.com/airbytehq/airbyte/pull/51388) | Update dependencies |
| 0.2.6 | 2024-12-28 | [50762](https://github.com/airbytehq/airbyte/pull/50762) | Update dependencies |
| 0.2.5 | 2024-12-21 | [50379](https://github.com/airbytehq/airbyte/pull/50379) | Update dependencies |
| 0.2.4 | 2024-12-14 | [49785](https://github.com/airbytehq/airbyte/pull/49785) | Update dependencies |
| 0.2.3 | 2024-12-12 | [49416](https://github.com/airbytehq/airbyte/pull/49416) | Update dependencies |
| 0.2.2 | 2024-11-04 | [48287](https://github.com/airbytehq/airbyte/pull/48287) | Update dependencies |
| 0.2.1 | 2024-08-16 | [44196](https://github.com/airbytehq/airbyte/pull/44196) | Bump source-declarative-manifest version |
| 0.2.0 | 2024-08-09 | [43451](https://github.com/airbytehq/airbyte/pull/43451) | Refactor connector to manifest-only format |
| 0.1.10 | 2024-08-03 | [43207](https://github.com/airbytehq/airbyte/pull/43207) | Update dependencies |
| 0.1.9 | 2024-07-20 | [42202](https://github.com/airbytehq/airbyte/pull/42202) | Update dependencies |
| 0.1.8 | 2024-07-13 | [41473](https://github.com/airbytehq/airbyte/pull/41473) | Update dependencies |
| 0.1.7 | 2024-07-09 | [41116](https://github.com/airbytehq/airbyte/pull/41116) | Update dependencies |
| 0.1.6 | 2024-07-06 | [40845](https://github.com/airbytehq/airbyte/pull/40845) | Update dependencies |
| 0.1.5 | 2024-06-25 | [40388](https://github.com/airbytehq/airbyte/pull/40388) | Update dependencies |
| 0.1.4 | 2024-06-22 | [39967](https://github.com/airbytehq/airbyte/pull/39967) | Update dependencies |
| 0.1.3 | 2024-06-12 | [38741](https://github.com/airbytehq/airbyte/pull/38741) | Make connector compatible with Builder |
| 0.1.2 | 2024-06-04 | [38941](https://github.com/airbytehq/airbyte/pull/38941) | [autopull] Upgrade base image to v1.2.1 |
| 0.1.1 | 2024-05-20 | [38419](https://github.com/airbytehq/airbyte/pull/38419) | [autopull] base image + poetry + up_to_date |
| 0.1.0 | 2022-01-02 | [18843](https://github.com/airbytehq/airbyte/pull/18843) | Add Workramp Source Connector |

</details>
