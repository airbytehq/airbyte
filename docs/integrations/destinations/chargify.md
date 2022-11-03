---
description: >-
  Chargify is a SaaS billing and subscription management platform which specializes in complex billing, payment collections, and business analytics.
---

# Chargify

## Overview

The Airbyte Chargify destination allows you to stream data from any [Airbyte Source](https://airbyte.io/connectors?connector-type=Sources) into [Chargify](http://chargify.com) for [custom analysis](http://chargify.com/business-intelligence) and [multi-attribute, usage-based billing](http://chargify.com/events-based-billing). Chargify is the leading billing and subscription management software built for the evolving needs of fast-growth companies.

### Sync overview

#### Output schema

Each replicated stream from Airbyte will output data into a corresponding event collection in Chargify. Event collections store data in JSON format. Each collection will inherit the name from the stream with all non-alphanumeric characters removed, except for `.’, ‘-’, ‘_’,` and whitespace characters. When possible, the connector will try to infer the timestamp value for the record and override the special field `chargify.timestamp` with it.

#### Features

| Feature | Supported?\(Yes/No\) | Notes |
| :--- | :--- | :--- |
| Full Refresh Sync | Yes |  |
| Incremental - Append Sync | Yes |  |
| Incremental - Deduped History | No | As this connector does not support dbt, we don't support this sync mode on this destination. |
| Namespaces | No |  |

## Getting started

### Requirements

To use the Chargify destination, you'll first need to create a [Chargify account](https://go.chargify.com/free-trial/) (if you don’t already have one).

Once you have a Chargify account, you can use the following credentials to set up the connector

* A Project ID associated with the site
* A Master API key associated with the site

You can reach out to [support@chargify.com](mailto:support@chargify.com) to request your Project ID and Master API key for the Airbyte destination connector.

See the setup guide for more information about how to get started.

### Setup guide

#### Chargify

If [Business Intelligence](http://chargify.com/business-intelligence/) and [Events-Based Billing](http://chargify.com/events-based-billing) have not been enabled, please contact [support@chargify.com](mailto:support@chargify.com).

Login to the Chargify application and identify which sites you want to stream data to for Events-Based Billing and Chargify Business Intelligence.

Chargify sites are simply containers for your Products, Customers, and Subscriptions. You can use Chargify with just one Site, although most customers will want two sites at a minimum – one for testing and one for production.

Reach out to [support@chargify.com](mailto:support@chargify.com) to obtain your Site Project ID and Site Master API key. Note: You will need keys for each site you plan to stream data to.

#### API Key and Project ID

The Chargify Connector requires your `Project ID` and `Master Key` for authentication. To get them, please reach out to [support@chargify.com](mailto:support@chargify.com).

#### Timestamp Inference

The `Infer Timestamp` field lets you specify if you want the connector to infer the [chargify.timestamp](https://help.chargify.com/events/getting-data-in-guide.html#event-timestamps) field based on the data from the event that occurred in the source application. This feature allows for historical data synchronization enabling you to fully leverage the power of Chargify's time series analytics. By default, this property is set to true. If toggled off, chargify.timestamp will be set to the datetime when the data was recorded by Chargify.

### Setup the Chargify destination in Airbyte

Now, you should have all the parameters needed to configure Chargify destination.

* **Project ID**
* **Master API Key**
* **Infer Timestamp**

Connect your first source and then head to the Chargify application. You can seamlessly run [custom analysis](https://www.chargify.com/business-intelligence/) on your data and build [multi-attribute, usage-based pricing models](http://chargify.com/events-based-billing/).

If you have any questions or want to get started, [please reach out to a billing expert](https://go.chargify.com/contact/).

## CHANGELOG

| Version | Date | Pull Request | Subject |
| :--- | :--- | :--- | :--- |
| 0.2.2 | 2022-02-14 | [10256](https://github.com/airbytehq/airbyte/pull/10256) | Add `-XX:+ExitOnOutOfMemoryError` JVM option |
| 0.2.0 | 2021-09-10 | [\#5973](https://github.com/airbytehq/airbyte/pull/5973) | Fix timestamp inference for complex schemas |
| 0.1.0 | 2021-08-18 | [\#5339](https://github.com/airbytehq/airbyte/pull/5339) | Chargify Destination Release! |
