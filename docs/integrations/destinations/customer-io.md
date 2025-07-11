# Customer IO

This page contains the setup guide and reference information for the Customer IO destination connector.

## Overview

The Customer IO destination connector allows you to sync data to Customer IO, a customer data management platform. This destination relies on the Data Activation flow.

### Destination Objects + Operations

Here are the destination objects and their respective operations that are currently supported:
* [Person](https://docs.customer.io/journeys/create-update-person/): Identifies a person and assigns traits to them.
* [Person Events](https://docs.customer.io/journeys/events/): Track an event for a user that is known or not by Customer IO. Use `event_id` to leverage event deduplication.

### Features

| Feature                       | Supported? |
| :---------------------------- | :--------- |
| Full Refresh Sync            | Yes        |
| Incremental - Append Sync    | Yes        |
| Incremental - Dedupe Sync    | Yes        |
| Namespaces                   | Yes        |

### Restrictions

* Each entry sent to the API needs to be 32kb or smaller
* Customer IO allows to send unstructured attributes. Those attributes are subject to the following restrictions:
    * Max number of attributes allowed per object is 300
    * Max size of all attributes is 100kb
    * The attributes name is 150 bytes or smaller
    * The value of attributes is 1000 bytes or smaller
* Events name are 100 bytes or smaller

## Getting started

### Setup guide

In order to configure this connector, you only have to generate your API key (Workspace Settings → API and webhook credentials → Create Track API Key). Once this is done, provide this information in the connector's configuration and you are good to go.

## Changelog

| Version | Date       | Pull Request                                             | Subject                                                  |
|:--------|:-----------|:---------------------------------------------------------|:---------------------------------------------------------|
| 0.0.3   | 2025-07-08 | [#62848](https://github.com/airbytehq/airbyte/pull/62848) | Improve UX on connector configuration                    |
| 0.0.2   | 2025-07-08 | [#62843](https://github.com/airbytehq/airbyte/pull/62843) | Checker should validate DLQ                              |
| 0.0.1   | 2025-07-07 | [#62083](https://github.com/airbytehq/airbyte/pull/62083) | Initial release of the Customer IO destination connector |
