# Smaily

## Sync overview

This source can sync data from the [Smaily API](https://smaily.com/help/api/). At present this connector only supports full refresh syncs meaning that each time you use the connector it will sync all available records from scratch. Please use cautiously if you expect your API to have a lot of records.

## This Source Supports the Following Streams

- users
- segments
- campaigns
- templates
- automations
- A/B tests

### Features

| Feature           | Supported?\(Yes/No\) | Notes |
| :---------------- | :------------------- | :---- |
| Full Refresh Sync | Yes                  |       |
| Incremental Sync  | No                   |       |

### Performance considerations

The connector has a rate limit of 5 API requests per second per IP-address.

## Getting started

### Requirements

- Smaily API user username
- Smaily API user password
- Smaily API subdomain

## Changelog

<details>
  <summary>Expand to review</summary>

| Version | Date       | Pull Request                                             | Subject        |
| :------ | :--------- | :------------------------------------------------------- | :------------- |
| 0.2.42 | 2025-12-09 | [70690](https://github.com/airbytehq/airbyte/pull/70690) | Update dependencies |
| 0.2.41 | 2025-11-25 | [70106](https://github.com/airbytehq/airbyte/pull/70106) | Update dependencies |
| 0.2.40 | 2025-11-18 | [69488](https://github.com/airbytehq/airbyte/pull/69488) | Update dependencies |
| 0.2.39 | 2025-10-29 | [68825](https://github.com/airbytehq/airbyte/pull/68825) | Update dependencies |
| 0.2.38 | 2025-10-21 | [68281](https://github.com/airbytehq/airbyte/pull/68281) | Update dependencies |
| 0.2.37 | 2025-10-14 | [67731](https://github.com/airbytehq/airbyte/pull/67731) | Update dependencies |
| 0.2.36 | 2025-10-07 | [67453](https://github.com/airbytehq/airbyte/pull/67453) | Update dependencies |
| 0.2.35 | 2025-09-30 | [66912](https://github.com/airbytehq/airbyte/pull/66912) | Update dependencies |
| 0.2.34 | 2025-09-24 | [66261](https://github.com/airbytehq/airbyte/pull/66261) | Update dependencies |
| 0.2.33 | 2025-09-09 | [66110](https://github.com/airbytehq/airbyte/pull/66110) | Update dependencies |
| 0.2.32 | 2025-08-23 | [65419](https://github.com/airbytehq/airbyte/pull/65419) | Update dependencies |
| 0.2.31 | 2025-08-16 | [65025](https://github.com/airbytehq/airbyte/pull/65025) | Update dependencies |
| 0.2.30 | 2025-08-02 | [64425](https://github.com/airbytehq/airbyte/pull/64425) | Update dependencies |
| 0.2.29 | 2025-07-26 | [64006](https://github.com/airbytehq/airbyte/pull/64006) | Update dependencies |
| 0.2.28 | 2025-07-19 | [63624](https://github.com/airbytehq/airbyte/pull/63624) | Update dependencies |
| 0.2.27 | 2025-07-12 | [63078](https://github.com/airbytehq/airbyte/pull/63078) | Update dependencies |
| 0.2.26 | 2025-07-05 | [62732](https://github.com/airbytehq/airbyte/pull/62732) | Update dependencies |
| 0.2.25 | 2025-06-28 | [62265](https://github.com/airbytehq/airbyte/pull/62265) | Update dependencies |
| 0.2.24 | 2025-06-21 | [61299](https://github.com/airbytehq/airbyte/pull/61299) | Update dependencies |
| 0.2.23 | 2025-05-24 | [60503](https://github.com/airbytehq/airbyte/pull/60503) | Update dependencies |
| 0.2.22 | 2025-05-10 | [60196](https://github.com/airbytehq/airbyte/pull/60196) | Update dependencies |
| 0.2.21 | 2025-05-04 | [59621](https://github.com/airbytehq/airbyte/pull/59621) | Update dependencies |
| 0.2.20 | 2025-04-27 | [58973](https://github.com/airbytehq/airbyte/pull/58973) | Update dependencies |
| 0.2.19 | 2025-04-19 | [58442](https://github.com/airbytehq/airbyte/pull/58442) | Update dependencies |
| 0.2.18 | 2025-04-12 | [57978](https://github.com/airbytehq/airbyte/pull/57978) | Update dependencies |
| 0.2.17 | 2025-04-05 | [57452](https://github.com/airbytehq/airbyte/pull/57452) | Update dependencies |
| 0.2.16 | 2025-03-29 | [56826](https://github.com/airbytehq/airbyte/pull/56826) | Update dependencies |
| 0.2.15 | 2025-03-22 | [56259](https://github.com/airbytehq/airbyte/pull/56259) | Update dependencies |
| 0.2.14 | 2025-03-08 | [55148](https://github.com/airbytehq/airbyte/pull/55148) | Update dependencies |
| 0.2.13 | 2025-02-22 | [54506](https://github.com/airbytehq/airbyte/pull/54506) | Update dependencies |
| 0.2.12 | 2025-02-15 | [54039](https://github.com/airbytehq/airbyte/pull/54039) | Update dependencies |
| 0.2.11 | 2025-02-08 | [53547](https://github.com/airbytehq/airbyte/pull/53547) | Update dependencies |
| 0.2.10 | 2025-02-01 | [53078](https://github.com/airbytehq/airbyte/pull/53078) | Update dependencies |
| 0.2.9 | 2025-01-25 | [52388](https://github.com/airbytehq/airbyte/pull/52388) | Update dependencies |
| 0.2.8 | 2025-01-18 | [51944](https://github.com/airbytehq/airbyte/pull/51944) | Update dependencies |
| 0.2.7 | 2025-01-11 | [51443](https://github.com/airbytehq/airbyte/pull/51443) | Update dependencies |
| 0.2.6 | 2024-12-28 | [50774](https://github.com/airbytehq/airbyte/pull/50774) | Update dependencies |
| 0.2.5 | 2024-12-21 | [50330](https://github.com/airbytehq/airbyte/pull/50330) | Update dependencies |
| 0.2.4 | 2024-12-14 | [49791](https://github.com/airbytehq/airbyte/pull/49791) | Update dependencies |
| 0.2.3 | 2024-12-12 | [49394](https://github.com/airbytehq/airbyte/pull/49394) | Update dependencies |
| 0.2.2 | 2024-12-11 | [47809](https://github.com/airbytehq/airbyte/pull/47809) | Starting with this version, the Docker image is now rootless. Please note that this and future versions will not be compatible with Airbyte versions earlier than 0.64 |
| 0.2.1 | 2024-08-16 | [44196](https://github.com/airbytehq/airbyte/pull/44196) | Bump source-declarative-manifest version |
| 0.2.0 | 2024-08-14 | [44065](https://github.com/airbytehq/airbyte/pull/44065) | Refactor connector to manifest-only format |
| 0.1.14 | 2024-08-12 | [43872](https://github.com/airbytehq/airbyte/pull/43872) | Update dependencies |
| 0.1.13 | 2024-08-10 | [43664](https://github.com/airbytehq/airbyte/pull/43664) | Update dependencies |
| 0.1.12 | 2024-08-03 | [43175](https://github.com/airbytehq/airbyte/pull/43175) | Update dependencies |
| 0.1.11 | 2024-07-27 | [42777](https://github.com/airbytehq/airbyte/pull/42777) | Update dependencies |
| 0.1.10 | 2024-07-20 | [42227](https://github.com/airbytehq/airbyte/pull/42227) | Update dependencies |
| 0.1.9 | 2024-07-13 | [41838](https://github.com/airbytehq/airbyte/pull/41838) | Update dependencies |
| 0.1.8 | 2024-07-10 | [41579](https://github.com/airbytehq/airbyte/pull/41579) | Update dependencies |
| 0.1.7 | 2024-07-09 | [41093](https://github.com/airbytehq/airbyte/pull/41093) | Update dependencies |
| 0.1.6 | 2024-07-06 | [41010](https://github.com/airbytehq/airbyte/pull/41010) | Update dependencies |
| 0.1.5 | 2024-06-25 | [40460](https://github.com/airbytehq/airbyte/pull/40460) | Update dependencies |
| 0.1.4 | 2024-06-22 | [39959](https://github.com/airbytehq/airbyte/pull/39959) | Update dependencies |
| 0.1.3 | 2024-06-06 | [39176](https://github.com/airbytehq/airbyte/pull/39176) | [autopull] Upgrade base image to v1.2.2 |
| 0.1.2 | 2024-06-06 | [38931](https://github.com/airbytehq/airbyte/pull/38931) | Make compatible with builder |
| 0.1.1 | 2024-05-20 | [38412](https://github.com/airbytehq/airbyte/pull/38412) | [autopull] base image + poetry + up_to_date |
| 0.1.0 | 2022-10-25 | [18674](https://github.com/airbytehq/airbyte/pull/18674) | Initial commit |

</details>
