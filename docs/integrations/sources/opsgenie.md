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

| Version | Date       | Pull Request                                             | Subject                                                                         |
| :------ | :--------- | :------------------------------------------------------- | :------------------------------------------------------------------------------ |
| 0.3.5   | 2024-04-19 | [37210](https://github.com/airbytehq/airbyte/pull/37210) | Updating to 0.80.0 CDK                                                          |
| 0.3.4   | 2024-04-18 | [37210](https://github.com/airbytehq/airbyte/pull/37210) | Manage dependencies with Poetry.                                                |
| 0.3.3   | 2024-04-15 | [37210](https://github.com/airbytehq/airbyte/pull/37210) | Base image migration: remove Dockerfile and use the python-connector-base image |
| 0.3.2   | 2024-04-12 | [37210](https://github.com/airbytehq/airbyte/pull/37210) | schema descriptions                                                             |
| 0.3.1   | 2024-02-14 | [35269](https://github.com/airbytehq/airbyte/pull/35269) | Fix parsing of updated_at timestamps in alerts                                  |
| 0.3.0   | 2023-10-19 | [31552](https://github.com/airbytehq/airbyte/pull/31552) | Migrated to Low Code                                                            |
| 0.2.0   | 2023-10-24 | [31777](https://github.com/airbytehq/airbyte/pull/31777) | Fix schema                                                                      |
| 0.1.0   | 2022-09-14 | [16768](https://github.com/airbytehq/airbyte/pull/16768) | Initial Release                                                                 |
