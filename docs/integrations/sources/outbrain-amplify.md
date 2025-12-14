# Outbrain Amplify

## Sync overview

This source can sync data for the [Outbrain Amplify API](https://amplifyv01.docs.apiary.io/#reference/authentications). It supports Full Refresh syncs only. The connector will copy all rows in the tables and columns you set up for replication every time a sync is run.

### Output schema

This Source is capable of syncing the following streams:

- **marketers** - List of marketers
- **campaigns** - Campaigns by marketers
- **campaigns_geo_location** - Campaign geo-location targeting
- **promoted_links** - Promoted links for campaigns
- **promoted_links_sequences** - Promoted links sequences for campaigns
- **budgets** - Budgets for marketers
- **performance_campaigns** - Performance statistics for campaigns by marketers
- **performance_periodic** - Periodic performance statistics by marketers
- **performance_periodic_campaigns** - Periodic performance statistics by campaigns
- **performance_promoted_links** - Periodic performance statistics by promoted links
- **performance_publishers** - Performance statistics by publisher
- **performance_publishers_campaigns** - Performance statistics by publishers and campaigns
- **performance_platforms** - Performance statistics by platform
- **performance_platforms_campaigns** - Performance statistics by platforms and campaigns
- **performance_geo** - Performance statistics by geo location
- **performance_geo_campaigns** - Performance statistics by geo location and campaigns
- **performance_interests** - Performance statistics by interest

### Data type mapping

| Integration Type | Airbyte Type | Notes |
| :--------------- | :----------- | :---- |
| `string`         | `string`     |       |
| `integer`        | `integer`    |       |
| `number`         | `number`     |       |
| `array`          | `array`      |       |
| `object`         | `object`     |       |

### Features

| Feature           | Supported?\(Yes/No\) | Notes |
| :---------------- | :------------------- | :---- |
| Full Refresh Sync | Yes                  |       |
| Incremental Sync  | No                   |       |
| Namespaces        | No                   |       |

### Performance considerations

The Outbrain Amplify connector should not run into Outbrain Amplify API limitations under normal usage. Please [create an issue](https://github.com/airbytehq/airbyte/issues) if you see any rate limit issues that are not automatically retried successfully.

## Getting started

### Requirements

- Outbrain Amplify account credentials (either username/password or access token)
- Start date for data replication

### Setup guide

1. **Authentication**: You can authenticate using either:
   - **Access Token**: Provide your Outbrain Amplify API access token
   - **Username and Password**: Provide your Outbrain Amplify username and password

2. **Start Date** (required): Specify the date from which you want to start syncing data in YYYY-MM-DD format (e.g., 2017-01-25). Any data before this date will not be replicated.

3. **End Date** (optional): Optionally specify an end date in YYYY-MM-DD format to limit data replication to a specific time range.

4. **Report Granularity** (optional): Choose the granularity for periodic reports:
   - daily (default)
   - weekly
   - monthly

5. **Geo Location Breakdown** (optional): Choose the granularity for geo-location data:
   - country
   - region (default)
   - subregion

6. **Conversion Count** (optional): Define how conversions are counted in reports:
   - conversion_time (default) - Count conversions by the time they occurred
   - click/view_time - Count conversions by the time of the click or view that led to them

## Changelog

<details>
  <summary>Expand to review</summary>

| Version | Date       | Pull Request                                             | Subject                            |
| :------ | :--------- | :------------------------------------------------------- | :--------------------------------- |
| 0.2.22 | 2025-12-09 | [68984](https://github.com/airbytehq/airbyte/pull/68984) | Update dependencies |
| 0.2.21 | 2025-10-14 | [67754](https://github.com/airbytehq/airbyte/pull/67754) | Update dependencies |
| 0.2.20 | 2025-10-07 | [67079](https://github.com/airbytehq/airbyte/pull/67079/) | Fix broken pagination. |
| 0.2.19 | 2025-10-07 | [67354](https://github.com/airbytehq/airbyte/pull/67354) | Update dependencies |
| 0.2.18 | 2025-09-30 | [66383](https://github.com/airbytehq/airbyte/pull/66383) | Update dependencies |
| 0.2.17 | 2025-09-09 | [65847](https://github.com/airbytehq/airbyte/pull/65847) | Update dependencies |
| 0.2.16 | 2025-08-23 | [65178](https://github.com/airbytehq/airbyte/pull/65178) | Update dependencies |
| 0.2.15 | 2025-08-16 | [64979](https://github.com/airbytehq/airbyte/pull/64979) | Update dependencies |
| 0.2.14 | 2025-08-09 | [64678](https://github.com/airbytehq/airbyte/pull/64678) | Update dependencies |
| 0.2.13 | 2025-08-02 | [64286](https://github.com/airbytehq/airbyte/pull/64286) | Update dependencies |
| 0.2.12 | 2025-07-19 | [63413](https://github.com/airbytehq/airbyte/pull/63413) | Update dependencies |
| 0.2.11 | 2025-07-12 | [63186](https://github.com/airbytehq/airbyte/pull/63186) | Update dependencies |
| 0.2.10 | 2025-07-05 | [62630](https://github.com/airbytehq/airbyte/pull/62630) | Update dependencies |
| 0.2.9 | 2025-06-28 | [62353](https://github.com/airbytehq/airbyte/pull/62353) | Update dependencies |
| 0.2.8 | 2025-06-21 | [60489](https://github.com/airbytehq/airbyte/pull/60489) | Update dependencies |
| 0.2.7 | 2025-05-10 | [60191](https://github.com/airbytehq/airbyte/pull/60191) | Update dependencies |
| 0.2.6 | 2025-05-04 | [59511](https://github.com/airbytehq/airbyte/pull/59511) | Update dependencies |
| 0.2.5 | 2025-04-27 | [59100](https://github.com/airbytehq/airbyte/pull/59100) | Update dependencies |
| 0.2.4 | 2025-04-19 | [58502](https://github.com/airbytehq/airbyte/pull/58502) | Update dependencies |
| 0.2.3 | 2025-04-12 | [57901](https://github.com/airbytehq/airbyte/pull/57901) | Update dependencies |
| 0.2.2 | 2025-04-05 | [57318](https://github.com/airbytehq/airbyte/pull/57318) | Update dependencies |
| 0.2.1 | 2025-03-29 | [56805](https://github.com/airbytehq/airbyte/pull/56805) | Update dependencies |
| 0.2.0 | 2025-03-13 | [55746](https://github.com/airbytehq/airbyte/pull/55746) | Add optional parameter to set conversion_count metric by 'Time of Click/View' or 'Time of Conversion' |
| 0.1.33 | 2025-03-22 | [56217](https://github.com/airbytehq/airbyte/pull/56217) | Update dependencies |
| 0.1.32 | 2025-03-08 | [55067](https://github.com/airbytehq/airbyte/pull/55067) | Update dependencies |
| 0.1.31 | 2025-02-23 | [54557](https://github.com/airbytehq/airbyte/pull/54557) | Update dependencies |
| 0.1.30 | 2025-02-15 | [53963](https://github.com/airbytehq/airbyte/pull/53963) | Update dependencies |
| 0.1.29 | 2025-02-01 | [53010](https://github.com/airbytehq/airbyte/pull/53010) | Update dependencies |
| 0.1.28 | 2025-01-25 | [52461](https://github.com/airbytehq/airbyte/pull/52461) | Update dependencies |
| 0.1.27 | 2025-01-18 | [51889](https://github.com/airbytehq/airbyte/pull/51889) | Update dependencies |
| 0.1.26 | 2025-01-11 | [51319](https://github.com/airbytehq/airbyte/pull/51319) | Update dependencies |
| 0.1.25 | 2024-12-28 | [50746](https://github.com/airbytehq/airbyte/pull/50746) | Update dependencies |
| 0.1.24 | 2024-12-21 | [50236](https://github.com/airbytehq/airbyte/pull/50236) | Update dependencies |
| 0.1.23 | 2024-12-14 | [49715](https://github.com/airbytehq/airbyte/pull/49715) | Update dependencies |
| 0.1.22 | 2024-12-12 | [49065](https://github.com/airbytehq/airbyte/pull/49065) | Update dependencies |
| 0.1.21 | 2024-11-25 | [48634](https://github.com/airbytehq/airbyte/pull/48634) | Starting with this version, the Docker image is now rootless. Please note that this and future versions will not be compatible with Airbyte versions earlier than 0.64 |
| 0.1.20 | 2024-10-29 | [47849](https://github.com/airbytehq/airbyte/pull/47849) | Update dependencies |
| 0.1.19 | 2024-10-28 | [47040](https://github.com/airbytehq/airbyte/pull/47040) | Update dependencies |
| 0.1.18 | 2024-10-12 | [46775](https://github.com/airbytehq/airbyte/pull/46775) | Update dependencies |
| 0.1.17 | 2024-10-05 | [46403](https://github.com/airbytehq/airbyte/pull/46403) | Update dependencies |
| 0.1.16 | 2024-09-28 | [46195](https://github.com/airbytehq/airbyte/pull/46195) | Update dependencies |
| 0.1.15 | 2024-09-21 | [45832](https://github.com/airbytehq/airbyte/pull/45832) | Update dependencies |
| 0.1.14 | 2024-09-14 | [45502](https://github.com/airbytehq/airbyte/pull/45502) | Update dependencies |
| 0.1.13 | 2024-09-07 | [45240](https://github.com/airbytehq/airbyte/pull/45240) | Update dependencies |
| 0.1.12 | 2024-08-31 | [45024](https://github.com/airbytehq/airbyte/pull/45024) | Update dependencies |
| 0.1.11 | 2024-08-24 | [44737](https://github.com/airbytehq/airbyte/pull/44737) | Update dependencies |
| 0.1.10 | 2024-08-17 | [44351](https://github.com/airbytehq/airbyte/pull/44351) | Update dependencies |
| 0.1.9 | 2024-08-10 | [43605](https://github.com/airbytehq/airbyte/pull/43605) | Update dependencies |
| 0.1.8 | 2024-08-03 | [43068](https://github.com/airbytehq/airbyte/pull/43068) | Update dependencies |
| 0.1.7 | 2024-07-27 | [42754](https://github.com/airbytehq/airbyte/pull/42754) | Update dependencies |
| 0.1.6 | 2024-07-20 | [42334](https://github.com/airbytehq/airbyte/pull/42334) | Update dependencies |
| 0.1.5 | 2024-07-13 | [41869](https://github.com/airbytehq/airbyte/pull/41869) | Update dependencies |
| 0.1.4 | 2024-07-10 | [41574](https://github.com/airbytehq/airbyte/pull/41574) | Update dependencies |
| 0.1.3 | 2024-07-08 | [41035](https://github.com/airbytehq/airbyte/pull/41035) | Migrate to poetry |
| 0.1.2 | 2022-08-25 | [15667](https://github.com/airbytehq/airbyte/pull/15667) | Add message when no data available |
| 0.1.1 | 2022-05-30 | [11732](https://github.com/airbytehq/airbyte/pull/11732) | Fix docs |
| 0.1.0 | 2022-05-30 | [11732](https://github.com/airbytehq/airbyte/pull/11732) | Initial Release |

</details>
