---
description: >-
  Delighted is a proprietary self-serve experience management platform that allows collecting feedback from customers and employees through surveys.
---

# Delighted

## Sync overview

The Delighted source supports both Full Refresh and Incremental syncs. You can choose if this connector will copy only the new or updated data, or all rows in the tables and columns you set up for replication, every time a sync is run.

This source can sync data for the [Delighted API](https://app.delighted.com/docs/api).

This Source Connector is based on a [Airbyte CDK](https://docs.airbyte.io/connector-development/cdk-python).


### Output schema

This Source is capable of syncing the following core Streams:

* [Survey Responses](https://app.delighted.com/docs/api/listing-survey-responses)
* [People](https://app.delighted.com/docs/api/listing-people)
* [Bounced People](https://app.delighted.com/docs/api/listing-bounced-people)
* [Unsubscribed People](https://app.delighted.com/docs/api/listing-unsubscribed-people)

## Getting started

This connector supports `API PASSWORD` as the authentication method.

### Connect using `API PASSWORD` option:
1. Go to `https://delighted.com/account/api`
2. Copy your Delighted API key.
6. You're ready to set up Delighted in Airbyte!


## Changelog

| Version | Date | Pull Request | Subject |
| :--- | :--- | :--- | :--- |
| 0.1.4 | 2022-06-10 | [13439](https://github.com/airbytehq/airbyte/pull/13439) | Change since parameter input to iso date |
| 0.1.3 | 2022-01-31 | [9550](https://github.com/airbytehq/airbyte/pull/9550) | Output only records in which cursor field is greater than the value in state for incremental streams |
| 0.1.2 | 2022-01-06 | [9333](https://github.com/airbytehq/airbyte/pull/9333) | Add incremental sync mode to streams in `integration_tests/configured_catalog.json` |
| 0.1.1 | 2022-01-04 | [9275](https://github.com/airbytehq/airbyte/pull/9275) | Fix pagination handling for `survey_responses`, `bounces` and `unsubscribes` streams |
| 0.1.0 | 2021-10-27 | [4551](https://github.com/airbytehq/airbyte/pull/4551) | Add Delighted source connector |
