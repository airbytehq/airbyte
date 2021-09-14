---
description: Keen is a fully managed event streaming and analytic platform.
---

# Keen

## Overview

The Airbyte Keen destination allows you to send/stream data into Keen. Keen is a flexible, fully managed event streaming and analytic platform.

### Sync overview

#### Output schema

Each stream will output an event in Keen. Each collection will inherit the name from the stream with all non-alphanumeric characters removed, except for `.-_ ` and whitespace characters. When possible, the connector will try to guess the timestamp value for the record and override the special field `keen.timestamp` with it.


#### Features

| Feature | Supported?\(Yes/No\) | Notes |
| :--- | :--- | :--- |
| Full Refresh Sync | Yes |  |
| Incremental - Append Sync | Yes |  |
| Namespaces | No |  |

## Getting started

### Requirements

To use the Keen destination, you'll need:

* A Keen Project ID
* A Keen Master API key associated with the project

See the setup guide for more information about how to acquire the required resources.

### Setup guide

#### Keen Project

If you already have the project set up, jump to the "Access" section.

Login to your [Keen](https://keen.io/) account, then click the Add New link next to the Projects label on the left-hand side tab. Then give project a name.


#### API Key and Project ID 

Keen connector uses Keen Kafka Inbound Cluster to stream the data. It requires `Project ID` and `Master Key` for the authentication. To get them, navigate to the `Access` tab from the left-hand side panel and check the `Project Details` section.
**Important**: This destination requires the Project's **Master** Key.

#### Timestamp Inference

`Infer Timestamp` field lets you specify if you want the connector to guess the special `keen.timestamp` field based on the streamed data. It might be useful for historical data synchronization to fully leverage Keen's analytics power. If not selected, `keen.timestamp` will be set to date when data was streamed. By default, set to `true`.

### Setup the Keen destination in Airbyte

Now you should have all the parameters needed to configure Keen destination.

* **Project ID**
* **Master API Key**
* **Infer Timestamp**

## CHANGELOG

| Version | Date       | Pull Request | Subject |
| :------ | :--------  | :-----       | :------ |
| 0.2.0   | 2021-09-10 | [#5973](https://github.com/airbytehq/airbyte/pull/5973) | Fix timestamp inference for complex schemas |
| 0.1.0   | 2021-08-18 | [#5339](https://github.com/airbytehq/airbyte/pull/5339) | Keen Destination Release! |

