# My Hours

## Features

| Feature           | Supported?\(Yes/No\) | Notes |
| :---------------- | :------------------- | :---- |
| Full Refresh Sync | Yes                  |       |
| Incremental Sync  | No                   |       |

This source syncs data from the [My Hours API](https://documenter.getpostman.com/view/8879268/TVmV4YYU).

## Supported Tables

This source allows you to synchronize the following data tables:

- Time logs
- Clients
- Projects
- Team members
- Tags

## Getting started

**Requirements**

- In order to use the My Hours API you need to provide the credentials to an admin My Hours account.

### Performance Considerations (Airbyte Open Source)

Depending on the amount of team members and time logs the source provides a property to change the pagination size for the time logs query. Typically a pagination of 30 days is a correct balance between reliability and speed. But if you have a big amount of monthly entries you might want to change this value to a lower value.

## Changelog

<details>
  <summary>Expand to review</summary>

| Version | Date       | Pull Request                                             | Subject                            |
| :------ | :--------- | :------------------------------------------------------- | :--------------------------------- |
| 0.3.43 | 2025-12-09 | [70576](https://github.com/airbytehq/airbyte/pull/70576) | Update dependencies |
| 0.3.42 | 2025-11-25 | [69863](https://github.com/airbytehq/airbyte/pull/69863) | Update dependencies |
| 0.3.41 | 2025-11-18 | [69380](https://github.com/airbytehq/airbyte/pull/69380) | Update dependencies |
| 0.3.40 | 2025-10-29 | [69070](https://github.com/airbytehq/airbyte/pull/69070) | Update dependencies |
| 0.3.39 | 2025-10-21 | [68389](https://github.com/airbytehq/airbyte/pull/68389) | Update dependencies |
| 0.3.38 | 2025-10-14 | [67816](https://github.com/airbytehq/airbyte/pull/67816) | Update dependencies |
| 0.3.37 | 2025-10-07 | [67383](https://github.com/airbytehq/airbyte/pull/67383) | Update dependencies |
| 0.3.36 | 2025-09-30 | [66929](https://github.com/airbytehq/airbyte/pull/66929) | Update dependencies |
| 0.3.35 | 2025-09-23 | [66614](https://github.com/airbytehq/airbyte/pull/66614) | Update dependencies |
| 0.3.34 | 2025-09-09 | [65850](https://github.com/airbytehq/airbyte/pull/65850) | Update dependencies |
| 0.3.33 | 2025-08-23 | [65203](https://github.com/airbytehq/airbyte/pull/65203) | Update dependencies |
| 0.3.32 | 2025-08-09 | [64748](https://github.com/airbytehq/airbyte/pull/64748) | Update dependencies |
| 0.3.31 | 2025-08-02 | [64249](https://github.com/airbytehq/airbyte/pull/64249) | Update dependencies |
| 0.3.30 | 2025-07-26 | [63871](https://github.com/airbytehq/airbyte/pull/63871) | Update dependencies |
| 0.3.29 | 2025-07-19 | [63385](https://github.com/airbytehq/airbyte/pull/63385) | Update dependencies |
| 0.3.28 | 2025-07-12 | [63254](https://github.com/airbytehq/airbyte/pull/63254) | Update dependencies |
| 0.3.27 | 2025-06-28 | [62406](https://github.com/airbytehq/airbyte/pull/62406) | Update dependencies |
| 0.3.26 | 2025-06-21 | [61913](https://github.com/airbytehq/airbyte/pull/61913) | Update dependencies |
| 0.3.25 | 2025-06-14 | [61056](https://github.com/airbytehq/airbyte/pull/61056) | Update dependencies |
| 0.3.24 | 2025-05-24 | [60452](https://github.com/airbytehq/airbyte/pull/60452) | Update dependencies |
| 0.3.23 | 2025-05-10 | [59509](https://github.com/airbytehq/airbyte/pull/59509) | Update dependencies |
| 0.3.22 | 2025-04-27 | [59092](https://github.com/airbytehq/airbyte/pull/59092) | Update dependencies |
| 0.3.21 | 2025-04-19 | [58513](https://github.com/airbytehq/airbyte/pull/58513) | Update dependencies |
| 0.3.20 | 2025-04-12 | [57890](https://github.com/airbytehq/airbyte/pull/57890) | Update dependencies |
| 0.3.19 | 2025-04-05 | [57288](https://github.com/airbytehq/airbyte/pull/57288) | Update dependencies |
| 0.3.18 | 2025-03-29 | [56714](https://github.com/airbytehq/airbyte/pull/56714) | Update dependencies |
| 0.3.17 | 2025-03-22 | [56046](https://github.com/airbytehq/airbyte/pull/56046) | Update dependencies |
| 0.3.16 | 2025-03-08 | [55432](https://github.com/airbytehq/airbyte/pull/55432) | Update dependencies |
| 0.3.15 | 2025-03-01 | [54752](https://github.com/airbytehq/airbyte/pull/54752) | Update dependencies |
| 0.3.14 | 2025-02-22 | [54323](https://github.com/airbytehq/airbyte/pull/54323) | Update dependencies |
| 0.3.13 | 2025-02-15 | [53807](https://github.com/airbytehq/airbyte/pull/53807) | Update dependencies |
| 0.3.12 | 2025-02-08 | [53278](https://github.com/airbytehq/airbyte/pull/53278) | Update dependencies |
| 0.3.11 | 2025-02-01 | [52734](https://github.com/airbytehq/airbyte/pull/52734) | Update dependencies |
| 0.3.10 | 2025-01-25 | [52242](https://github.com/airbytehq/airbyte/pull/52242) | Update dependencies |
| 0.3.9 | 2025-01-18 | [51791](https://github.com/airbytehq/airbyte/pull/51791) | Update dependencies |
| 0.3.8 | 2025-01-11 | [51220](https://github.com/airbytehq/airbyte/pull/51220) | Update dependencies |
| 0.3.7 | 2024-12-28 | [50599](https://github.com/airbytehq/airbyte/pull/50599) | Update dependencies |
| 0.3.6 | 2024-12-21 | [50120](https://github.com/airbytehq/airbyte/pull/50120) | Update dependencies |
| 0.3.5 | 2024-12-14 | [49611](https://github.com/airbytehq/airbyte/pull/49611) | Update dependencies |
| 0.3.4 | 2024-12-12 | [49253](https://github.com/airbytehq/airbyte/pull/49253) | Update dependencies |
| 0.3.3 | 2024-12-11 | [48285](https://github.com/airbytehq/airbyte/pull/48285) | Starting with this version, the Docker image is now rootless. Please note that this and future versions will not be compatible with Airbyte versions earlier than 0.64 |
| 0.3.2 | 2024-10-29 | [47787](https://github.com/airbytehq/airbyte/pull/47787) | Update dependencies |
| 0.3.1 | 2024-10-28 | [47095](https://github.com/airbytehq/airbyte/pull/47095) | Update dependencies |
| 0.3.0 | 2024-10-19 | [47012](https://github.com/airbytehq/airbyte/pull/47012) | Migrate to manifest only format |
| 0.2.20 | 2024-10-12 | [46852](https://github.com/airbytehq/airbyte/pull/46852) | Update dependencies |
| 0.2.19 | 2024-10-05 | [46469](https://github.com/airbytehq/airbyte/pull/46469) | Update dependencies |
| 0.2.18 | 2024-09-28 | [46167](https://github.com/airbytehq/airbyte/pull/46167) | Update dependencies |
| 0.2.17 | 2024-09-21 | [45781](https://github.com/airbytehq/airbyte/pull/45781) | Update dependencies |
| 0.2.16 | 2024-09-14 | [45582](https://github.com/airbytehq/airbyte/pull/45582) | Update dependencies |
| 0.2.15 | 2024-09-07 | [45235](https://github.com/airbytehq/airbyte/pull/45235) | Update dependencies |
| 0.2.14 | 2024-08-31 | [44948](https://github.com/airbytehq/airbyte/pull/44948) | Update dependencies |
| 0.2.13 | 2024-08-24 | [44729](https://github.com/airbytehq/airbyte/pull/44729) | Update dependencies |
| 0.2.12 | 2024-08-17 | [44280](https://github.com/airbytehq/airbyte/pull/44280) | Update dependencies |
| 0.2.11 | 2024-08-12 | [43833](https://github.com/airbytehq/airbyte/pull/43833) | Update dependencies |
| 0.2.10 | 2024-08-10 | [43518](https://github.com/airbytehq/airbyte/pull/43518) | Update dependencies |
| 0.2.9 | 2024-08-03 | [43127](https://github.com/airbytehq/airbyte/pull/43127) | Update dependencies |
| 0.2.8 | 2024-07-27 | [42809](https://github.com/airbytehq/airbyte/pull/42809) | Update dependencies |
| 0.2.7 | 2024-07-20 | [42350](https://github.com/airbytehq/airbyte/pull/42350) | Update dependencies |
| 0.2.6 | 2024-07-13 | [41905](https://github.com/airbytehq/airbyte/pull/41905) | Update dependencies |
| 0.2.5 | 2024-07-10 | [41297](https://github.com/airbytehq/airbyte/pull/41297) | Update dependencies |
| 0.2.4 | 2024-07-06 | [40993](https://github.com/airbytehq/airbyte/pull/40993) | Update dependencies |
| 0.2.3 | 2024-06-25 | [40286](https://github.com/airbytehq/airbyte/pull/40286) | Update dependencies |
| 0.2.2 | 2024-06-22 | [40020](https://github.com/airbytehq/airbyte/pull/40020) | Update dependencies |
| 0.2.1 | 2024-06-06 | [39308](https://github.com/airbytehq/airbyte/pull/39308) | [autopull] Upgrade base image to v1.2.2 |
| 0.2.0 | 2024-03-15 | [36063](https://github.com/airbytehq/airbyte/pull/36063) | Migrate to Low Code |
| 0.1.2 | 2023-11-20 | [32680](https://github.com/airbytehq/airbyte/pull/32680) | Schema and CDK updates |
| 0.1.1 | 2022-06-08 | [12964](https://github.com/airbytehq/airbyte/pull/12964) | Update schema for time_logs stream |
| 0.1.0 | 2021-11-26 | [8270](https://github.com/airbytehq/airbyte/pull/8270) | New Source: My Hours |

</details>
