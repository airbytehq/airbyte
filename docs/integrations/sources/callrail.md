# CallRail

## Overview

The CailRail source supports Full Refresh and Incremental syncs.

### Output schema

This Source is capable of syncing the following core Streams:

- [Calls](https://apidocs.callrail.com/#calls)
- [Companies](https://apidocs.callrail.com/#companies)
- [Text Messages](https://apidocs.callrail.com/#text-messages)
- [Users](https://apidocs.callrail.com/#users)

### Features

| Feature                   | Supported? |
| :------------------------ | :--------- |
| Full Refresh Sync         | Yes        |
| Incremental - Append Sync | Yes        |
| Incremental - Dedupe Sync | Yes        |
| SSL connection            | No         |
| Namespaces                | No         |

## Getting started

### Requirements

- CallRail Account
- CallRail API Token

## Changelog

<details>
  <summary>Expand to review</summary>

| Version | Date       | Pull Request                                             | Subject                 |
| :------ | :--------- | :------------------------------------------------------- | :---------------------- |
| 0.1.9 | 2024-07-20 | [42229](https://github.com/airbytehq/airbyte/pull/42229) | Update dependencies |
| 0.1.8 | 2024-07-13 | [41788](https://github.com/airbytehq/airbyte/pull/41788) | Update dependencies |
| 0.1.7 | 2024-07-10 | [41551](https://github.com/airbytehq/airbyte/pull/41551) | Update dependencies |
| 0.1.6 | 2024-07-09 | [41129](https://github.com/airbytehq/airbyte/pull/41129) | Update dependencies |
| 0.1.5 | 2024-07-06 | [40833](https://github.com/airbytehq/airbyte/pull/40833) | Update dependencies |
| 0.1.4 | 2024-06-25 | [40335](https://github.com/airbytehq/airbyte/pull/40335) | Update dependencies |
| 0.1.3 | 2024-06-22 | [39949](https://github.com/airbytehq/airbyte/pull/39949) | Update dependencies |
| 0.1.2 | 2024-06-06 | [39281](https://github.com/airbytehq/airbyte/pull/39281) | [autopull] Upgrade base image to v1.2.2 |
| 0.1.1 | 2024-05-21 | [38531](https://github.com/airbytehq/airbyte/pull/38531) | [autopull] base image + poetry + up_to_date |
| 0.1.0 | 2022-10-31 | [18739](https://github.com/airbytehq/airbyte/pull/18739) | 🎉 New Source: CallRail |

</details>
