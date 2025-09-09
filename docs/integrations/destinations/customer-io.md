# Customer IO

This page contains the setup guide and reference information for the Customer IO destination connector.

:::info
Data activation is in **early access**. Try it today with the HubSpot and Customer.io destinations in Airbyte Cloud or Self-Managed version 1.8 and later. If you'd like to be an early adopter, chat with the team, and share feedback, [fill out this form](https://form.typeform.com/to/STc7a0jx).
:::

## Overview

The Customer IO destination connector allows you to sync data to Customer IO, a customer data management platform. This connector supports [data activation](/platform/next/move-data/elt-data-activation) and requires Airbyte version 1.8 or later.

## Prerequisites

- Customer IO Account
- Airbyte version 1.8 or later is required to use this connector


### Destination Objects + Operations

Here are the destination objects and their respective operations that are currently supported:
* [Person](https://docs.customer.io/journeys/create-update-person/): Identifies a person and assigns traits to them.
* [Person Events](https://docs.customer.io/journeys/events/): Track an event for a user that is known or not by Customer IO. Required fields: `person_email`, `event_name`. Optional fields: `event_id` (for event deduplication), `timestamp`.

### Features

| Feature                       | Supported? |
| :---------------------------- | :--------- |
| Full Refresh Sync            | Yes        |
| Incremental - Append Sync    | Yes        |
| Incremental - Dedupe Sync    | Yes        |
| Namespaces                   | Yes        |

### Restrictions

* Each entry sent to the API needs to be 32kb or smaller
* Customer IO allows you to send unstructured attributes. Those attributes are subject to the following restrictions:
    * Max number of attributes allowed per object is 300
    * Max size of all attributes is 100kb
    * The attributes name is 150 bytes or smaller
    * The value of attributes is 1000 bytes or smaller
* Event names are 100 bytes or smaller

## Getting started

### Setup guide

In order to configure this connector, you need to generate your Track API Key and obtain your Site ID from Customer IO (Workspace Settings → API and webhook credentials → Create Track API Key). Once this is done, provide both the Site ID and API Key in the connector's configuration and you are good to go.

**Object Storage for Rejected Records**: This connector supports data activation and can optionally store [rejected records](/platform/next/move-data/rejected-records) in object storage (such as S3). Configure object storage in the connector settings to capture records that couldn't be synced to Customer IO due to schema validation issues or other errors.

## Changelog

| Version | Date       | Pull Request                                             | Subject                                                  |
|:--------|:-----------|:---------------------------------------------------------|:---------------------------------------------------------|
| 0.0.5   | 2025-09-08 | [65157](https://github.com/airbytehq/airbyte/pull/65157)        | Update following breaking changes on spec |
| 0.0.4   | 2025-08-20 | [#65113](https://github.com/airbytehq/airbyte/pull/65113) | Update logo                                              |
| 0.0.3   | 2025-07-08 | [#62848](https://github.com/airbytehq/airbyte/pull/62848) | Improve UX on connector configuration                    |
| 0.0.2   | 2025-07-08 | [#62843](https://github.com/airbytehq/airbyte/pull/62843) | Checker should validate DLQ                              |
| 0.0.1   | 2025-07-07 | [#62083](https://github.com/airbytehq/airbyte/pull/62083) | Initial release of the Customer IO destination connector |
