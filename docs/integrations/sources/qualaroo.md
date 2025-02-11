# Qualaroo

## Overview

The Qualaroo source supports Full Refresh syncs. You can choose if this connector will copy only the new or updated data, or all rows in the tables and columns you set up for replication, every time a sync is run.

### Output schema

Several output streams are available from this source:

- [Surveys](https://help.qualaroo.com/hc/en-us/articles/201969438-The-REST-Reporting-API) \(Full table\)
  - [Responses](https://help.qualaroo.com/hc/en-us/articles/201969438-The-REST-Reporting-API) \(Full table\)

If there are more endpoints you'd like Airbyte to support, please [create an issue.](https://github.com/airbytehq/airbyte/issues/new/choose)

### Features

| Feature                   | Supported? |
| :------------------------ | :--------- |
| Full Refresh Sync         | Yes        |
| Incremental - Append Sync | NO         |
| SSL connection            | Yes        |
| Namespaces                | No         |

### Performance considerations

The connector is **not** yet restricted by normal requests limitation. As a result, the Qualaroo connector might run into API limitations under normal usage. Please [create an issue](https://github.com/airbytehq/airbyte/issues) if you see any rate limit issues that are not automatically retried successfully.

## Getting started

### Requirements

- Qualaroo API Key
- Qualaroo API Token

### Setup guide

<!-- markdown-link-check-disable-next-line -->

Please read [How to get your APIs Token and Key](https://help.qualaroo.com/hc/en-us/articles/201969438-The-REST-Reporting-API) or you can log in to Qualaroo and visit [Reporting API](https://app.qualaroo.com/account).

## Changelog

<details>
  <summary>Expand to review</summary>

| Version | Date       | Pull Request                                             | Subject                                                                                                  |
| :------ | :--------- | :------------------------------------------------------- | :------------------------------------------------------------------------------------------------------- |
| 0.4.9 | 2025-02-08 | [53447](https://github.com/airbytehq/airbyte/pull/53447) | Update dependencies |
| 0.4.8 | 2025-02-01 | [52992](https://github.com/airbytehq/airbyte/pull/52992) | Update dependencies |
| 0.4.7 | 2025-01-25 | [52497](https://github.com/airbytehq/airbyte/pull/52497) | Update dependencies |
| 0.4.6 | 2025-01-18 | [51371](https://github.com/airbytehq/airbyte/pull/51371) | Update dependencies |
| 0.4.5 | 2024-12-28 | [50701](https://github.com/airbytehq/airbyte/pull/50701) | Update dependencies |
| 0.4.4 | 2024-12-21 | [50224](https://github.com/airbytehq/airbyte/pull/50224) | Update dependencies |
| 0.4.3 | 2024-12-14 | [49680](https://github.com/airbytehq/airbyte/pull/49680) | Update dependencies |
| 0.4.2 | 2024-12-12 | [49344](https://github.com/airbytehq/airbyte/pull/49344) | Update dependencies |
| 0.4.1 | 2024-12-11 | [49098](https://github.com/airbytehq/airbyte/pull/49098) | Starting with this version, the Docker image is now rootless. Please note that this and future versions will not be compatible with Airbyte versions earlier than 0.64 |
| 0.4.0 | 2024-10-31 | [47017](https://github.com/airbytehq/airbyte/pull/47017) | Migrate to manifest only format |
| 0.3.24 | 2024-10-28 | [47111](https://github.com/airbytehq/airbyte/pull/47111) | Update dependencies |
| 0.3.23 | 2024-10-12 | [46767](https://github.com/airbytehq/airbyte/pull/46767) | Update dependencies |
| 0.3.22 | 2024-10-05 | [46439](https://github.com/airbytehq/airbyte/pull/46439) | Update dependencies |
| 0.3.21 | 2024-09-28 | [46168](https://github.com/airbytehq/airbyte/pull/46168) | Update dependencies |
| 0.3.20 | 2024-09-21 | [45825](https://github.com/airbytehq/airbyte/pull/45825) | Update dependencies |
| 0.3.19 | 2024-09-14 | [45527](https://github.com/airbytehq/airbyte/pull/45527) | Update dependencies |
| 0.3.18 | 2024-09-07 | [45260](https://github.com/airbytehq/airbyte/pull/45260) | Update dependencies |
| 0.3.17 | 2024-08-31 | [44958](https://github.com/airbytehq/airbyte/pull/44958) | Update dependencies |
| 0.3.16 | 2024-08-24 | [44646](https://github.com/airbytehq/airbyte/pull/44646) | Update dependencies |
| 0.3.15 | 2024-08-17 | [44267](https://github.com/airbytehq/airbyte/pull/44267) | Update dependencies |
| 0.3.14 | 2024-08-12 | [43773](https://github.com/airbytehq/airbyte/pull/43773) | Update dependencies |
| 0.3.13 | 2024-08-10 | [43683](https://github.com/airbytehq/airbyte/pull/43683) | Update dependencies |
| 0.3.12 | 2024-08-03 | [43199](https://github.com/airbytehq/airbyte/pull/43199) | Update dependencies |
| 0.3.11 | 2024-07-27 | [42730](https://github.com/airbytehq/airbyte/pull/42730) | Update dependencies |
| 0.3.10 | 2024-07-25 | [42539](https://github.com/airbytehq/airbyte/pull/42539) | Update manifest with proper param structure |
| 0.3.9 | 2024-07-20 | [42321](https://github.com/airbytehq/airbyte/pull/42321) | Update dependencies |
| 0.3.8 | 2024-07-13 | [41830](https://github.com/airbytehq/airbyte/pull/41830) | Update dependencies |
| 0.3.7 | 2024-07-10 | [41380](https://github.com/airbytehq/airbyte/pull/41380) | Update dependencies |
| 0.3.6 | 2024-07-10 | [41331](https://github.com/airbytehq/airbyte/pull/41331) | Update dependencies |
| 0.3.5 | 2024-07-06 | [40822](https://github.com/airbytehq/airbyte/pull/40822) | Update dependencies |
| 0.3.4 | 2024-06-25 | [40365](https://github.com/airbytehq/airbyte/pull/40365) | Update dependencies |
| 0.3.3 | 2024-06-22 | [40139](https://github.com/airbytehq/airbyte/pull/40139) | Update dependencies |
| 0.3.2 | 2024-06-06 | [39259](https://github.com/airbytehq/airbyte/pull/39259) | [autopull] Upgrade base image to v1.2.2 |
| 0.3.1 | 2024-05-20 | [38381](https://github.com/airbytehq/airbyte/pull/38381) | [autopull] base image + poetry + up_to_date |
| 0.3.0 | 2023-10-25 | [31070](https://github.com/airbytehq/airbyte/pull/31070) | Migrate to low-code framework |
| 0.2.0 | 2023-05-24 | [26491](https://github.com/airbytehq/airbyte/pull/26491) | Remove authSpecification from spec.json as OAuth is not supported by Qualaroo + update stream schema |
| 0.1.2 | 2022-05-24 | [13121](https://github.com/airbytehq/airbyte/pull/13121) | Fix `start_date` and `survey_ids` schema formatting. Separate source and stream files. Add stream_slices |
| 0.1.1 | 2022-05-20 | [13042](https://github.com/airbytehq/airbyte/pull/13042) | Update stream specs |
| 0.1.0 | 2021-08-18 | [8623](https://github.com/airbytehq/airbyte/pull/8623) | New source: Qualaroo |

</details>
