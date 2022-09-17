# Outreach

## Overview

The Outreach source supports both `Full Refresh` and `Incremental` syncs. You can choose if this connector will copy only the new or updated data, or all rows in the tables and columns you set up for replication, every time a sync is run.

### Output schema

Some output streams are available from this source. A list of these streams can be found below in the [Streams](outreach.md#streams) section.

### Features

| Feature | Supported? |
| :--- | :--- |
| Full Refresh Sync | Yes |
| Incremental Sync | Yes |
| SSL connection | Yes |
| Namespaces | No |

## Getting started

### Requirements

* Outreach Account
* Outreach OAuth credentials

### Setup guide

Getting oauth credentials require contacting Outreach to request an account. Check out [here](https://www.outreach.io/lp/watch-demo#request-demo).

## Streams

List of available streams:

* Prospects
* Sequences
* SequenceStates

## Changelog

| Version | Date       | Pull Request | Subject |

| :------ | :--------  | :-----       | :------ |
| 0.1.2   | 2022-07-04 | [14386](https://github.com/airbytehq/airbyte/pull/14386) | Fix stream schema and cursor field |
| 0.1.1   | 2021-12-07 | [8582](https://github.com/airbytehq/airbyte/pull/8582) | Update connector fields title/description |
| 0.1.0   | 2021-11-03 | [7507](https://github.com/airbytehq/airbyte/pull/7507) | Outreach Connector |
