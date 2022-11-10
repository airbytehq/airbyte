# InfluxDB
InfluxDB API Documentation is available [here](https://docs.influxdata.com/influxdb/v1.7/tools/api/#ping-http-endpoint)

## Overview

The InfluxDB source supports full refresh syncs

### Output schema

Several output streams are available from this source:

query: https://docs.influxdata.com/influxdb/cloud/reference/api/influxdb-1x/query/

If there are more endpoints you'd like Airbyte to support, please [create an issue.](https://github.com/airbytehq/airbyte/issues/new/choose)

### Features

| Feature           | Supported? |
|:------------------|:-----------|
| Full Refresh Sync | Yes        |
| Incremental Sync  | No         |

### Performance considerations

The influxdb connector should not run into limitations under normal usage. Please [create an issue](https://github.com/airbytehq/airbyte/issues) if you see any rate limit issues that are not automatically retried successfully.

## Getting started

### Requirements

* InfluxDB API Token
* InfluxDB username
* InfluxDB Database Name
* InfluxDB Database query

### Connect using `API Key`:

1. Create a new App [here](https://developer.nytimes.com/my-apps/new-app) (You need to have an account to create a new App).
2. Enable API access for the supported endpoints (see Output schema section for supported streams).
3. Write the key into `secrets/config.json` file.

## Changelog

| Version | Date       | Pull Request                                             | Subject                                         |
|:--------|:-----------|:---------------------------------------------------------|:------------------------------------------------|
| 0.1.0   | 2022-11-01 | [18801](https://github.com/airbytehq/airbyte/pull/18801) | 🎉 New Source: InfluxDB                         |
