# Opsgenie

## Overview

This page contains the setup guide and reference information for the Opsgenie source connector.

### Output Schema

This connector outputs the following streams:

* [Alerts](https://docs.opsgenie.com/docs/alert-api) \(Incremental\)
* [Alert Logs](https://docs.opsgenie.com/docs/alert-api-continued#list-alert-logs) \(Incremental\)
* [Alert Recipients](https://docs.opsgenie.com/docs/alert-api-continued#list-alert-recipients) \(Incremental\)
* [Services](https://docs.opsgenie.com/docs/service-api)
* [Incidents](https://docs.opsgenie.com/docs/incident-api) \(Incremental\)
* [Integrations](https://docs.opsgenie.com/docs/integration-api)
* [Users](https://docs.opsgenie.com/docs/user-api)
* [Teams](https://docs.opsgenie.com/docs/team-api)
* [Team Members](https://docs.opsgenie.com/docs/team-member-api)

### Features

| Feature                   | Supported? |
|:--------------------------| :--- |
| Full Refresh Sync         | Yes |
| Incremental - Append Sync | Partially \(not all streams\) |
| EU Instance               | Yes |

### Performance Considerations

Opsgenie has [rate limits](https://docs.opsgenie.com/docs/api-rate-limiting), but the Opsgenie connector should not run into API limitations under normal usage. Please [create an issue](https://github.com/airbytehq/airbyte/issues) if you see any rate limit issues that are not automatically retried successfully.

## Getting Started

### Requirements

* Opsgenie Account
* Opsgenie API Key wih the necessary permissions \(described below\)

### Setup Guide

Log into Opsgenie and then generate an [API Key](https://support.atlassian.com/opsgenie/docs/api-key-management/).

Your API Key needs to have `Read` and `Configuration Access` permissions to enable the connector to correctly load data.

## Additional Information

The Opsgenie connector uses the most recent API version for each source of data. Each stream endpoint operates on its own version.

## Changelog

| Version | Date       | Pull Request                                         | Subject |
|:--------|:-----------|:-----------------------------------------------------| :--- |
| 0.1.0   | 2022-09-14 | [16768](https://github.com/airbytehq/airbyte/pull/16768) | Initial Release |

