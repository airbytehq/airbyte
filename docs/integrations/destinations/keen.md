---
description: >-
  Keen is a fully managed event streaming and analytics platform.
---

# Keen

## Overview

The Airbyte Keen destination allows you to stream data from any Airbyte Source into [Keen](https://keen.io?utm_campaign=Airbyte%20Destination%20Connector&utm_source=Airbyte%20Hosted%20Docs&utm_medium=Airbyte%20Hosted%20Docs&utm_term=Airbyte%20Hosted%20Docs&utm_content=Airbyte%20Hosted%20Docs) for storage, analysis, and visualization. Keen is a flexible, fully managed event streaming and analytics platform that empowers anyone to ship custom, embeddable dashboards in minutes, not months.

## Prerequisites

- For Airbyte Open Source users using the [Postgres](https://docs.airbyte.com/integrations/sources/postgres) source connector, [upgrade](https://docs.airbyte.com/operator-guides/upgrading-airbyte/) your Airbyte platform to version `v0.40.0-alpha` or newer and upgrade your Keen connector to version `0.2.4` or newer

### Sync overview

#### Output schema

Each replicated stream from Airbyte will output data into a corresponding event collection in Keen. Event collections store data in JSON format. Each collection will inherit the name from the stream with all non-alphanumeric characters removed, except for `.’, ‘-’, ‘_’,` and whitespace characters. When possible, the connector will try to infer the timestamp value for the record and override the special field `keen.timestamp` with it.

#### Features

| Feature                       | Supported?\(Yes/No\) | Notes                                                                                        |
| :---------------------------- | :------------------- | :------------------------------------------------------------------------------------------- |
| Full Refresh Sync             | Yes                  |                                                                                              |
| Incremental - Append Sync     | Yes                  |                                                                                              |
| Incremental - Deduped History | No                   | As this connector does not support dbt, we don't support this sync mode on this destination. |
| Namespaces                    | No                   |                                                                                              |

## Getting started

### Requirements

To use the Keen destination, you'll first need to create a [Keen account](https://keen.io/users/signup?utm_campaign=Airbyte%20Destination%20Connector&utm_source=Airbyte%20Hosted%20Docs&utm_medium=Airbyte%20Hosted%20Docs&utm_term=Airbyte%20Hosted%20Docs&utm_content=Airbyte%20Hosted%20Docs) (if you don’t already have one).

Once you have a Keen account, you can use the following credentials to set up the connector

- A Keen Project ID
- A Keen Master API key associated with the project

See the setup guide for more information about how to get started.

### Setup guide

#### Keen Project

If you haven’t set up a project to stream your data to:

Login to the [Keen application](https://keen.io/) and add a new project. To do this, click the ‘Add New’ link next to the Projects label on the left-hand, side ribbon. Then, give the project a name.

You can think of a project as a data silo. The data in a project is completely separate from data in other projects. We recommend that you create separate projects for each of your applications and separate projects for Dev and Prod environments.

Now, head to the ‘Access’ section and grab your Project ID and Master API Key.

If you already have a project set up:

Head to the ‘Access’ tab and grab your Project ID and Master API Key

#### API Key and Project ID

The Keen Connector uses the [Keen Kafka Inbound Cluster](https://keen.io/docs/streams/kafka-streaming/kafka-inbound-cluster/?utm_campaign=Airbyte%20Destination%20Connector&utm_source=Airbyte%20Hosted%20Docs&utm_medium=Airbyte%20Hosted%20Docs&utm_term=Airbyte%20Hosted%20Docs&utm_content=Airbyte%20Hosted%20Docs) to stream data. It requires your `Project ID` and `Master Key` for authentication. To get them, navigate to the `Access` tab from the left-hand, side panel and check the `Project Details` section.
**Important**: This destination requires the Project's **Master** Key.

#### Timestamp Inference

The `Infer Timestamp` field lets you specify if you want the connector to infer the [keen.timestamp](https://keen.io/docs/streams/overview/data-modeling-guide/#timestamp-data-type) field based on the data from the event that occurred in the source application. This feature allows for historical data synchronization enabling you to fully leverage the power of Keen's time series analytics. By default, this property is set to `true`. If toggled off, `keen.timestamp` will be set to the datetime when the data was recorded by Keen.

### Setup the Keen destination in Airbyte

Now, you should have all the parameters needed to configure Keen destination.

- **Project ID**
- **Master API Key**
- **Infer Timestamp**

Connect your first source and then head to the Keen application. You can seamlessly run [custom analysis](https://keen.io/docs/compute/data-explorer-guide/?utm_campaign=Airbyte%20Destination%20Connector&utm_source=Airbyte%20Hosted%20Docs&utm_medium=Airbyte%20Hosted%20Docs&utm_term=Airbyte%20Hosted%20Docs&utm_content=Airbyte%20Hosted%20Docs) on your data and [build interactive dashboards](https://keen.io/docs/visualize/dashboard-creator/dashboard-edition/?utm_campaign=Airbyte%20Destination%20Connector&utm_source=Airbyte%20Hosted%20Docs&utm_medium=Airbyte%20Hosted%20Docs&utm_term=Airbyte%20Hosted%20Docs&utm_content=Airbyte%20Hosted%20Docs) for key stakeholders.

If you have any questions, please reach out to us at team@keen.io and we’ll be happy to help!

## CHANGELOG

| Version | Date       | Pull Request                                             | Subject                                                                      |
| :------ | :--------- | :------------------------------------------------------- | :--------------------------------------------------------------------------- |
| 0.2.4   | 2022-08-04 | [15291](https://github.com/airbytehq/airbyte/pull/15291) | Update Keen destination to use outputRecordCollector to properly store state |
| 0.2.3   | 2022-06-17 | [13864](https://github.com/airbytehq/airbyte/pull/13864) | Updated stacktrace format for any trace message errors                       |
| 0.2.1   | 2021-12-30 | [8809](https://github.com/airbytehq/airbyte/pull/8809)   | Update connector fields title/description                                    |
| 0.2.0   | 2021-09-10 | [5973](https://github.com/airbytehq/airbyte/pull/5973)   | Fix timestamp inference for complex schemas                                  |
| 0.1.0   | 2021-08-18 | [5339](https://github.com/airbytehq/airbyte/pull/5339)   | Keen Destination Release!                                                    |
