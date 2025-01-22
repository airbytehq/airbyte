# PersistIq

## Sync overview

The PersistIq source supports Full Refresh syncs only.

This source syncs data for the [PersistIq API](https://apidocs.persistiq.com/#introduction).

### Output schema

This Source is capable of syncing the following streams:

- [Users](https://apidocs.persistiq.com/#users)
- [Leads](https://apidocs.persistiq.com/#leads)
- [Campaigns](https://apidocs.persistiq.com/#campaigns)

### Features

| Feature                   | Supported?\(Yes/No\) |
|:--------------------------|:---------------------|
| Full Refresh Sync         | Yes                  |
| Incremental - Append Sync | No                   |
| Namespaces                | No                   |

### Performance considerations

The PersistIq connector should not run into PersistIq API limitations under normal usage. Please [create an issue](https://github.com/airbytehq/airbyte/issues) if you see any rate limit issues that are not automatically retried successfully.

## Getting started

### Requirements

- PersistIq API Key

### Setup guide

Please read [How to find your API key](https://apidocs.persistiq.com/#introduction).

## Changelog

<details>
  <summary>Expand to review</summary>

| Version | Date       | Pull Request                                             | Subject                                |
|:--------|:-----------|:---------------------------------------------------------|:---------------------------------------|
| 0.3.10 | 2025-01-18 | [51867](https://github.com/airbytehq/airbyte/pull/51867) | Update dependencies |
| 0.3.9 | 2025-01-11 | [51320](https://github.com/airbytehq/airbyte/pull/51320) | Update dependencies |
| 0.3.8 | 2024-12-28 | [50729](https://github.com/airbytehq/airbyte/pull/50729) | Update dependencies |
| 0.3.7 | 2024-12-21 | [50247](https://github.com/airbytehq/airbyte/pull/50247) | Update dependencies |
| 0.3.6 | 2024-12-14 | [49676](https://github.com/airbytehq/airbyte/pull/49676) | Update dependencies |
| 0.3.5 | 2024-12-12 | [48266](https://github.com/airbytehq/airbyte/pull/48266) | Update dependencies |
| 0.3.4 | 2024-10-29 | [47851](https://github.com/airbytehq/airbyte/pull/47851) | Update dependencies |
| 0.3.3 | 2024-10-28 | [47579](https://github.com/airbytehq/airbyte/pull/47579) | Update dependencies |
| 0.3.2 | 2024-10-21 | [47193](https://github.com/airbytehq/airbyte/pull/47193) | Update dependencies |
| 0.3.1 | 2024-08-16 | [44196](https://github.com/airbytehq/airbyte/pull/44196) | Bump source-declarative-manifest version |
| 0.3.0 | 2024-08-15 | [44098](https://github.com/airbytehq/airbyte/pull/44098) | Refactor connector to manifest-only format |
| 0.2.14 | 2024-08-12 | [43737](https://github.com/airbytehq/airbyte/pull/43737) | Update dependencies |
| 0.2.13 | 2024-08-10 | [43656](https://github.com/airbytehq/airbyte/pull/43656) | Update dependencies |
| 0.2.12 | 2024-08-03 | [43104](https://github.com/airbytehq/airbyte/pull/43104) | Update dependencies |
| 0.2.11 | 2024-07-27 | [42661](https://github.com/airbytehq/airbyte/pull/42661) | Update dependencies |
| 0.2.10 | 2024-07-20 | [42374](https://github.com/airbytehq/airbyte/pull/42374) | Update dependencies |
| 0.2.9 | 2024-07-13 | [41715](https://github.com/airbytehq/airbyte/pull/41715) | Update dependencies |
| 0.2.8 | 2024-07-10 | [41419](https://github.com/airbytehq/airbyte/pull/41419) | Update dependencies |
| 0.2.7 | 2024-07-09 | [41196](https://github.com/airbytehq/airbyte/pull/41196) | Update dependencies |
| 0.2.6 | 2024-07-06 | [40787](https://github.com/airbytehq/airbyte/pull/40787) | Update dependencies |
| 0.2.5 | 2024-06-25 | [40377](https://github.com/airbytehq/airbyte/pull/40377) | Update dependencies |
| 0.2.4 | 2024-06-22 | [40039](https://github.com/airbytehq/airbyte/pull/40039) | Update dependencies |
| 0.2.3 | 2024-06-15 | [38789](https://github.com/airbytehq/airbyte/pull/38789) | Make connector compatible with builder |
| 0.2.2 | 2024-06-06 | [39288](https://github.com/airbytehq/airbyte/pull/39288) | [autopull] Upgrade base image to v1.2.2 |
| 0.2.1 | 2024-05-13 | [37596](https://github.com/airbytehq/airbyte/pull/37596) | Change `last_records` to `last_record` |
| 0.2.0 | 2023-10-10 | [31055](https://github.com/airbytehq/airbyte/pull/31055) | Migrate to low code |
| 0.1.0 | 2022-01-21 | [9515](https://github.com/airbytehq/airbyte/pull/9515) | 🎉 New Source: PersistIq |

</details>
