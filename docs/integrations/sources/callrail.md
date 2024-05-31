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
| 0.1.1 | 2024-05-21 | [38531](https://github.com/airbytehq/airbyte/pull/38531) | [autopull] base image + poetry + up_to_date |
| 0.1.0 | 2022-10-31 | [18739](https://github.com/airbytehq/airbyte/pull/18739) | 🎉 New Source: CallRail |

</details>