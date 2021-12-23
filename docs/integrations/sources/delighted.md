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
| 0.1.0 | 2021-10-27 | [4551](https://github.com/airbytehq/airbyte/pull/4551) | Add Delighted source connector |