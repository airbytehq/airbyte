# Firebolt

## Overview

The Firebolt source allows you to sync your data from [Firebolt](https://www.firebolt.io/). Only Full refresh is supported at the moment.

The connector is built on top of a pure Python [firebolt-sdk](https://pypi.org/project/firebolt-sdk/) and does not require additonal dependencies.

#### Resulting schema

The Firebolt source does not alter schema present in your database. Depending on the destination connected to this source, however, the result schema may be altered. See the destination's documentation for more details.

#### Features

| Feature                   | Supported?\(Yes/No\) | Notes |
| :------------------------ | :------------------- | :---- |
| Full Refresh Sync         | Yes                  |       |
| Incremental - Append Sync | No                   |       |

## Getting started

### Requirements

1. An existing AWS account

### Setup guide

1. Sign up to Firebolt following the [guide](https://docs.firebolt.io/godocs/Guides/managing-your-organization/creating-an-organization.html)

1. Follow the getting started [tutorial](https://docs.firebolt.io/godocs/Guides/getting-started.html) to setup a database.

1. Create a [service account](https://docs.firebolt.io/godocs/Guides/managing-your-organization/service-accounts.html).

1. [Load data](https://docs.firebolt.io/godocs/Guides/loading-data/loading-data.html).

#### You should now have the following

1. An existing Firebolt account
1. Connection parameters handy
   1. Service account id
   1. Service account password
   1. [Account name](https://docs.firebolt.io/godocs/Guides/managing-your-organization/managing-accounts.html)
   1. Host (Optional)
   1. Engine (Optional)
1. A running engine (if an engine is stopped or booting up you won't be able to connect to it)
1. Your data in either [Fact or Dimension](https://docs.firebolt.io/godocs/Overview/working-with-tables/working-with-tables.html#fact-and-dimension-tables) tables.

You can now use the Airbyte Firebolt source.

## Changelog

<details>
  <summary>Expand to review</summary>

| Version | Date       | Pull Request                                             | Subject                                                      |
| :------ | :--------- | :------------------------------------------------------- | :----------------------------------------------------------- |
| 2.0.40 | 2025-12-09 | [68764](https://github.com/airbytehq/airbyte/pull/68764) | Update dependencies |
| 2.0.39 | 2025-10-14 | [68068](https://github.com/airbytehq/airbyte/pull/68068) | Update dependencies |
| 2.0.38 | 2025-10-07 | [67315](https://github.com/airbytehq/airbyte/pull/67315) | Update dependencies |
| 2.0.37 | 2025-09-30 | [66779](https://github.com/airbytehq/airbyte/pull/66779) | Update dependencies |
| 2.0.36 | 2025-09-24 | [66165](https://github.com/airbytehq/airbyte/pull/66165) | Update dependencies |
| 2.0.35 | 2025-09-09 | [65804](https://github.com/airbytehq/airbyte/pull/65804) | Update dependencies |
| 2.0.34 | 2025-08-23 | [65289](https://github.com/airbytehq/airbyte/pull/65289) | Update dependencies |
| 2.0.33 | 2025-08-16 | [65019](https://github.com/airbytehq/airbyte/pull/65019) | Update dependencies |
| 2.0.32 | 2025-08-09 | [64742](https://github.com/airbytehq/airbyte/pull/64742) | Update dependencies |
| 2.0.31 | 2025-08-02 | [64374](https://github.com/airbytehq/airbyte/pull/64374) | Update dependencies |
| 2.0.30 | 2025-07-26 | [63969](https://github.com/airbytehq/airbyte/pull/63969) | Update dependencies |
| 2.0.29 | 2025-07-19 | [63563](https://github.com/airbytehq/airbyte/pull/63563) | Update dependencies |
| 2.0.28 | 2025-07-12 | [62984](https://github.com/airbytehq/airbyte/pull/62984) | Update dependencies |
| 2.0.27 | 2025-07-05 | [62754](https://github.com/airbytehq/airbyte/pull/62754) | Update dependencies |
| 2.0.26 | 2025-06-28 | [62434](https://github.com/airbytehq/airbyte/pull/62434) | Update dependencies |
| 2.0.25 | 2025-06-22 | [48657](https://github.com/airbytehq/airbyte/pull/48657) | Update dependencies |
| 2.0.24 | 2024-11-04 | [48154](https://github.com/airbytehq/airbyte/pull/48154) | Update dependencies |
| 2.0.23 | 2024-10-28 | [47109](https://github.com/airbytehq/airbyte/pull/47109) | Update dependencies |
| 2.0.22 | 2024-10-12 | [46826](https://github.com/airbytehq/airbyte/pull/46826) | Update dependencies |
| 2.0.21 | 2024-10-05 | [46471](https://github.com/airbytehq/airbyte/pull/46471) | Update dependencies |
| 2.0.20 | 2024-09-28 | [46210](https://github.com/airbytehq/airbyte/pull/46210) | Update dependencies |
| 2.0.19 | 2024-09-21 | [45765](https://github.com/airbytehq/airbyte/pull/45765) | Update dependencies |
| 2.0.18 | 2024-09-14 | [45572](https://github.com/airbytehq/airbyte/pull/45572) | Update dependencies |
| 2.0.17 | 2024-09-07 | [45211](https://github.com/airbytehq/airbyte/pull/45211) | Update dependencies |
| 2.0.16 | 2024-08-31 | [45030](https://github.com/airbytehq/airbyte/pull/45030) | Update dependencies |
| 2.0.15 | 2024-08-24 | [44715](https://github.com/airbytehq/airbyte/pull/44715) | Update dependencies |
| 2.0.14 | 2024-08-17 | [44212](https://github.com/airbytehq/airbyte/pull/44212) | Update dependencies |
| 2.0.13 | 2024-08-12 | [43774](https://github.com/airbytehq/airbyte/pull/43774) | Update dependencies |
| 2.0.12 | 2024-08-10 | [43535](https://github.com/airbytehq/airbyte/pull/43535) | Update dependencies |
| 2.0.11 | 2024-08-03 | [43268](https://github.com/airbytehq/airbyte/pull/43268) | Update dependencies |
| 2.0.10 | 2024-07-20 | [42159](https://github.com/airbytehq/airbyte/pull/42159) | Update dependencies |
| 2.0.9 | 2024-07-13 | [41744](https://github.com/airbytehq/airbyte/pull/41744) | Update dependencies |
| 2.0.8 | 2024-07-10 | [41575](https://github.com/airbytehq/airbyte/pull/41575) | Update dependencies |
| 2.0.7 | 2024-07-09 | [41151](https://github.com/airbytehq/airbyte/pull/41151) | Update dependencies |
| 2.0.6 | 2024-07-06 | [40979](https://github.com/airbytehq/airbyte/pull/40979) | Update dependencies |
| 2.0.5 | 2024-06-25 | [40438](https://github.com/airbytehq/airbyte/pull/40438) | Update dependencies |
| 2.0.4 | 2024-06-22 | [40199](https://github.com/airbytehq/airbyte/pull/40199) | Update dependencies |
| 2.0.3 | 2024-06-06 | [39183](https://github.com/airbytehq/airbyte/pull/39183) | [autopull] Upgrade base image to v1.2.2 |
| 2.0.2 | 2024-06-03 | [38892](https://github.com/airbytehq/airbyte/pull/38892) | Replace AirbyteLogger with logging.Logger |
| 2.0.1 | 2024-06-03 | [38892](https://github.com/airbytehq/airbyte/pull/38892) | Replace AirbyteLogger with logging.Logger |
| 2.0.0 | 2024-06-01 | [36349](https://github.com/airbytehq/airbyte/pull/36349) | Service account authentication support |
| 1.0.0 | 2023-07-20 | [21842](https://github.com/airbytehq/airbyte/pull/21842) | PGDate, TimestampTZ, TimestampNTZ and Boolean column support |
| 0.2.1 | 2022-05-10 | [25965](https://github.com/airbytehq/airbyte/pull/25965) | Fix DATETIME conversion to Airbyte date-time type |
| 0.2.0 | 2022-09-09 | [16583](https://github.com/airbytehq/airbyte/pull/16583) | Reading from views |
| 0.1.0 | 2022-04-28 | [13874](https://github.com/airbytehq/airbyte/pull/13874) | Create Firebolt source |

</details>
