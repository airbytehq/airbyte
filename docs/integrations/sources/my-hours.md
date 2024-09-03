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
