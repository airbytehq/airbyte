# Opsgenie

## Overview

This page contains the setup guide and reference information for the Opsgenie source connector.

### Output Schema

This connector outputs the following streams:

- [Alerts](https://docs.opsgenie.com/docs/alert-api) \(Incremental\)
- [Alert Logs](https://docs.opsgenie.com/docs/alert-api-continued#list-alert-logs) \(Incremental\)
- [Alert Recipients](https://docs.opsgenie.com/docs/alert-api-continued#list-alert-recipients) \(Incremental\)
- [Services](https://docs.opsgenie.com/docs/service-api)
- [Incidents](https://docs.opsgenie.com/docs/incident-api) \(Incremental\)
- [Integrations](https://docs.opsgenie.com/docs/integration-api)
- [Users](https://docs.opsgenie.com/docs/user-api)
- [Teams](https://docs.opsgenie.com/docs/team-api)
- [Team Members](https://docs.opsgenie.com/docs/team-member-api)

### Features

| Feature                   | Supported?                    |
| :------------------------ | :---------------------------- |
| Full Refresh Sync         | Yes                           |
| Incremental - Append Sync | Partially \(not all streams\) |
| EU Instance               | Yes                           |

### Performance Considerations

Opsgenie has [rate limits](https://docs.opsgenie.com/docs/api-rate-limiting), but the Opsgenie connector should not run into API limitations under normal usage. Please [create an issue](https://github.com/airbytehq/airbyte/issues) if you see any rate limit issues that are not automatically retried successfully.

## Getting Started

### Requirements

- Opsgenie Account
- Opsgenie API Key wih the necessary permissions \(described below\)

### Setup Guide

Log into Opsgenie and then generate an [API Key](https://support.atlassian.com/opsgenie/docs/api-key-management/).

Your API Key needs to have `Read` and `Configuration Access` permissions to enable the connector to correctly load data.

## Additional Information

The Opsgenie connector uses the most recent API version for each source of data. Each stream endpoint operates on its own version.

## Changelog

<details>
  <summary>Expand to review</summary>

| Version | Date       | Pull Request                                             | Subject                                                                         |
| :------ | :--------- | :------------------------------------------------------- | :------------------------------------------------------------------------------ |
| 0.4.6 | 2025-01-11 | [50293](https://github.com/airbytehq/airbyte/pull/50293) | Update dependencies |
| 0.4.5 | 2024-12-14 | [49661](https://github.com/airbytehq/airbyte/pull/49661) | Update dependencies |
| 0.4.4 | 2024-12-12 | [48253](https://github.com/airbytehq/airbyte/pull/48253) | Update dependencies |
| 0.4.3 | 2024-10-29 | [47920](https://github.com/airbytehq/airbyte/pull/47920) | Update dependencies |
| 0.4.2 | 2024-10-28 | [47653](https://github.com/airbytehq/airbyte/pull/47653) | Update dependencies |
| 0.4.1 | 2024-08-16 | [44196](https://github.com/airbytehq/airbyte/pull/44196) | Bump source-declarative-manifest version |
| 0.4.0 | 2024-08-15 | [44105](https://github.com/airbytehq/airbyte/pull/44105) | Refactor connector to manifest-only format |
| 0.3.16 | 2024-08-10 | [43579](https://github.com/airbytehq/airbyte/pull/43579) | Update dependencies |
| 0.3.15 | 2024-08-03 | [43248](https://github.com/airbytehq/airbyte/pull/43248) | Update dependencies |
| 0.3.14 | 2024-07-27 | [42650](https://github.com/airbytehq/airbyte/pull/42650) | Update dependencies |
| 0.3.13 | 2024-07-20 | [42193](https://github.com/airbytehq/airbyte/pull/42193) | Update dependencies |
| 0.3.12 | 2024-07-13 | [41895](https://github.com/airbytehq/airbyte/pull/41895) | Update dependencies |
| 0.3.11 | 2024-07-10 | [41493](https://github.com/airbytehq/airbyte/pull/41493) | Update dependencies |
| 0.3.10 | 2024-07-09 | [41132](https://github.com/airbytehq/airbyte/pull/41132) | Update dependencies |
| 0.3.9 | 2024-07-06 | [40988](https://github.com/airbytehq/airbyte/pull/40988) | Update dependencies |
| 0.3.8 | 2024-06-25 | [40434](https://github.com/airbytehq/airbyte/pull/40434) | Update dependencies |
| 0.3.7 | 2024-06-22 | [40093](https://github.com/airbytehq/airbyte/pull/40093) | Update dependencies |
| 0.3.6 | 2024-06-04 | [39035](https://github.com/airbytehq/airbyte/pull/39035) | [autopull] Upgrade base image to v1.2.1 |
| 0.3.5 | 2024-04-19 | [37210](https://github.com/airbytehq/airbyte/pull/37210) | Updating to 0.80.0 CDK |
| 0.3.4 | 2024-04-18 | [37210](https://github.com/airbytehq/airbyte/pull/37210) | Manage dependencies with Poetry. |
| 0.3.3 | 2024-04-15 | [37210](https://github.com/airbytehq/airbyte/pull/37210) | Base image migration: remove Dockerfile and use the python-connector-base image |
| 0.3.2 | 2024-04-12 | [37210](https://github.com/airbytehq/airbyte/pull/37210) | schema descriptions |
| 0.3.1 | 2024-02-14 | [35269](https://github.com/airbytehq/airbyte/pull/35269) | Fix parsing of updated_at timestamps in alerts |
| 0.3.0 | 2023-10-19 | [31552](https://github.com/airbytehq/airbyte/pull/31552) | Migrated to Low Code |
| 0.2.0 | 2023-10-24 | [31777](https://github.com/airbytehq/airbyte/pull/31777) | Fix schema |
| 0.1.0 | 2022-09-14 | [16768](https://github.com/airbytehq/airbyte/pull/16768) | Initial Release |

</details>
